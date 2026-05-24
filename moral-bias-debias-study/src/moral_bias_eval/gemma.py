from __future__ import annotations

from dataclasses import dataclass
import time

import torch
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

from .generation import GenerationResult


@dataclass(frozen=True)
class GemmaModelConfig:
    model_id: str
    quantization: str
    device_map: str
    temperature: float
    top_p: float
    top_k: int
    enable_thinking: bool
    adapter_path: str | None = None


class GemmaGenerator:
    def __init__(self, config: GemmaModelConfig) -> None:
        self.config = config
        self.processor = None
        self.model = None

    def load(self) -> None:
        self.processor = AutoProcessor.from_pretrained(self.config.model_id, trust_remote_code=True)
        self.model = self._load_model(self.config.model_id, self.config.quantization)
        if self.config.adapter_path:
            self.model = PeftModel.from_pretrained(self.model, self.config.adapter_path)

    def _load_model(self, model_id: str, quantization: str):
        hf_config = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
        model_cls = (
            AutoModelForImageTextToText
            if "ConditionalGeneration" in str(getattr(hf_config, "architectures", []))
            else AutoModelForCausalLM
        )
        common_kwargs = {
            "device_map": self.config.device_map,
            "trust_remote_code": True,
        }
        if quantization == "bnb4":
            compute_dtype = (
                torch.bfloat16
                if torch.cuda.is_available() and torch.cuda.is_bf16_supported()
                else torch.float16
            )
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=compute_dtype,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            return model_cls.from_pretrained(
                model_id,
                quantization_config=quant_config,
                torch_dtype=compute_dtype,
                **common_kwargs,
            )
        if quantization == "none":
            return model_cls.from_pretrained(
                model_id,
                torch_dtype="auto",
                **common_kwargs,
            )
        raise ValueError(f"Unsupported quantization mode: {quantization}")

    @property
    def input_device(self) -> torch.device:
        assert self.model is not None
        return next(self.model.parameters()).device

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        seed: int,
        max_new_tokens: int,
    ) -> GenerationResult:
        assert self.processor is not None
        assert self.model is not None

        prompt_text = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=self.config.enable_thinking,
        )
        inputs = self.processor(text=prompt_text, return_tensors="pt")
        inputs = {key: value.to(self.input_device) for key, value in inputs.items()}

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        started_at = time.perf_counter()
        output_ids = self.model.generate(
            **inputs,
            do_sample=True,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            max_new_tokens=max_new_tokens,
        )
        elapsed = time.perf_counter() - started_at
        generated = output_ids[0][len(inputs["input_ids"][0]) :]
        return GenerationResult(
            content=self.processor.decode(generated, skip_special_tokens=True).strip(),
            latency_seconds=elapsed,
            prompt_tokens=int(inputs["input_ids"].shape[-1]),
            completion_tokens=int(generated.shape[-1]),
            total_tokens=int(output_ids.shape[-1]),
        )
