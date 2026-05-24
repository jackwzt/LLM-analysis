from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

import torch
from datasets import load_dataset
from peft import PeftModel, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import DPOConfig, DPOTrainer


def ensure_eos(text: str, tokenizer) -> str:
    text = str(text or "").strip()
    if tokenizer.eos_token and not text.endswith(tokenizer.eos_token):
        text = f"{text}{tokenizer.eos_token}"
    return text


def format_example(example, tokenizer) -> dict[str, str]:
    prompt_text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    return {
        "prompt": prompt_text,
        "chosen": ensure_eos(example["chosen"], tokenizer),
        "rejected": ensure_eos(example["rejected"], tokenizer),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="DPO training for Qwen3-4B debiasing adapter.")
    parser.add_argument("--model-id", default="Qwen/Qwen3-4B")
    parser.add_argument("--sft-adapter-path", type=Path, required=True)
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument("--val-jsonl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-length", type=int, default=1536)
    parser.add_argument("--max-prompt-length", type=int, default=1152)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--per-device-train-batch-size", type=int, default=1)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=5e-6)
    parser.add_argument("--beta", type=float, default=0.05)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    compute_dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
        dtype=compute_dtype,
    )
    base_model.config.use_cache = False
    base_model = prepare_model_for_kbit_training(base_model)
    model = PeftModel.from_pretrained(base_model, str(args.sft_adapter_path), is_trainable=True)
    model.print_trainable_parameters()

    dataset = load_dataset(
        "json",
        data_files={"train": str(args.train_jsonl), "validation": str(args.val_jsonl)},
    )
    dataset = dataset.map(lambda ex: format_example(ex, tokenizer), remove_columns=dataset["train"].column_names)

    dpo_config_kwargs = {
        "output_dir": str(args.output_dir),
        "num_train_epochs": args.epochs,
        "max_steps": args.max_steps,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": args.per_device_eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "learning_rate": args.learning_rate,
        "lr_scheduler_type": "cosine",
        "warmup_ratio": 0.03,
        "logging_steps": 5,
        "eval_strategy": "steps",
        "eval_steps": 25,
        "save_strategy": "steps",
        "save_steps": 25,
        "save_total_limit": 2,
        "bf16": compute_dtype == torch.bfloat16,
        "fp16": compute_dtype == torch.float16,
        "report_to": [],
        "optim": "paged_adamw_8bit",
        "gradient_checkpointing": True,
        "beta": args.beta,
        "max_length": args.max_length,
        "max_prompt_length": args.max_prompt_length,
        "precompute_ref_log_probs": False,
    }
    supported_config_args = set(inspect.signature(DPOConfig.__init__).parameters)
    dpo_args = DPOConfig(**{key: value for key, value in dpo_config_kwargs.items() if key in supported_config_args})
    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=dpo_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        processing_class=tokenizer,
    )
    trainer.train()
    trainer.save_model(str(args.output_dir / "final_adapter"))
    tokenizer.save_pretrained(str(args.output_dir / "final_adapter"))
    (args.output_dir / "training_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
