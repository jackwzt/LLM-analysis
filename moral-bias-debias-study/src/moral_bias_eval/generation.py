from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationResult:
    content: str
    latency_seconds: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    raw_response: dict[str, Any] | None = None

    def to_trace_dict(self, step_name: str) -> dict[str, Any]:
        payload = asdict(self)
        payload["step_name"] = step_name
        return payload
