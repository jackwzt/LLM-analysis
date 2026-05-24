from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoProcessor,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)


def load_processor_and_tokenizer(model_id: str, model_family: str):
    if model_family == "gemma4":
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        tokenizer = processor.tokenizer
        return processor, tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    return None, tokenizer


def apply_chat_template(processor, tokenizer, messages: list[dict[str, str]], model_family: str) -> str:
    template_owner = processor if processor is not None else tokenizer
    kwargs = {"tokenize": False, "add_generation_prompt": True}
    if model_family in {"qwen", "gemma4"}:
        kwargs["enable_thinking"] = False
    try:
        return template_owner.apply_chat_template(messages, **kwargs)
    except TypeError:
        kwargs.pop("enable_thinking", None)
        return template_owner.apply_chat_template(messages, **kwargs)


def format_example(example, processor, tokenizer, model_family: str) -> dict[str, str]:
    prompt_text = apply_chat_template(processor, tokenizer, example["messages"], model_family)
    target_text = example["target_text"]
    if tokenizer.eos_token and not target_text.endswith(tokenizer.eos_token):
        target_text = f"{target_text}{tokenizer.eos_token}"
    return {"prompt_text": prompt_text, "target_text": target_text, "text": f"{prompt_text}{target_text}"}


def tokenize_example(example, tokenizer, max_seq_length: int) -> dict[str, list[int]]:
    prompt_ids = tokenizer(example["prompt_text"], add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(example["text"], add_special_tokens=False)["input_ids"]
    input_ids = full_ids[:max_seq_length]
    attention_mask = [1] * len(input_ids)
    labels = [-100] * min(len(prompt_ids), len(input_ids))
    labels.extend(input_ids[len(labels) :])
    labels = labels[:max_seq_length]
    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


def data_collator(features, tokenizer):
    max_length = max(len(feature["input_ids"]) for feature in features)
    input_ids = []
    attention_mask = []
    labels = []
    for feature in features:
        pad_length = max_length - len(feature["input_ids"])
        input_ids.append(feature["input_ids"] + [tokenizer.pad_token_id] * pad_length)
        attention_mask.append(feature["attention_mask"] + [0] * pad_length)
        labels.append(feature["labels"] + [-100] * pad_length)
    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }


def lora_target_modules(model, model_family: str) -> list[str]:
    suffixes = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
    if model_family == "gemma4":
        return [
            name
            for name, module in model.named_modules()
            if name.startswith("model.language_model.layers.")
            and name.endswith(suffixes)
            and module.__class__.__name__ != "Gemma4ClippableLinear"
        ]
    return list(suffixes)


def main() -> None:
    parser = argparse.ArgumentParser(description="QLoRA SFT distillation for critique_revise teacher outputs.")
    parser.add_argument("--model-id", default="Qwen/Qwen3-4B")
    parser.add_argument("--model-family", choices=["qwen", "gemma4"], default="qwen")
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument("--val-jsonl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--per-device-train-batch-size", type=int, default=1)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--lora-r", type=int, default=32)
    parser.add_argument("--lora-alpha", type=int, default=64)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    args = parser.parse_args()

    processor, tokenizer = load_processor_and_tokenizer(args.model_id, args.model_family)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    compute_dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    model_cls = AutoModelForImageTextToText if args.model_family == "gemma4" else AutoModelForCausalLM
    model = model_cls.from_pretrained(
        args.model_id,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
        dtype=compute_dtype,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=lora_target_modules(model, args.model_family),
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset(
        "json",
        data_files={"train": str(args.train_jsonl), "validation": str(args.val_jsonl)},
    )
    dataset = dataset.map(
        lambda ex: format_example(ex, processor, tokenizer, args.model_family),
        remove_columns=dataset["train"].column_names,
    )
    dataset = dataset.map(
        lambda ex: tokenize_example(ex, tokenizer, args.max_seq_length),
        remove_columns=["prompt_text", "target_text", "text"],
    )

    training_args = TrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        eval_strategy="steps",
        eval_steps=25,
        save_strategy="steps",
        save_steps=25,
        save_total_limit=2,
        bf16=compute_dtype == torch.bfloat16,
        fp16=compute_dtype == torch.float16,
        report_to=[],
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        data_collator=lambda features: data_collator(features, tokenizer),
    )
    trainer.train()
    trainer.save_model(str(args.output_dir / "final_adapter"))
    if processor is not None:
        processor.save_pretrained(str(args.output_dir / "final_adapter"))
    else:
        tokenizer.save_pretrained(str(args.output_dir / "final_adapter"))
    (args.output_dir / "training_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
