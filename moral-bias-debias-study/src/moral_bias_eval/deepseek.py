from __future__ import annotations

from dataclasses import dataclass

from .openai_compatible import OpenAICompatibleConfig, OpenAICompatibleGenerator


@dataclass(frozen=True)
class DeepSeekModelConfig(OpenAICompatibleConfig):
    pass


class DeepSeekGenerator(OpenAICompatibleGenerator):
    pass
