from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any

import requests

from .generation import GenerationResult


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    api_key: str
    base_url: str
    model_id: str
    temperature: float
    top_p: float
    max_retries: int
    timeout_seconds: int
    retry_base_delay_seconds: float
    retry_max_delay_seconds: float
    min_request_interval_seconds: float
    omit_seed: bool
    extra_body: dict[str, Any] = field(default_factory=dict)


class OpenAICompatibleGenerator:
    def __init__(self, config: OpenAICompatibleConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self._last_request_started_at = 0.0
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        )

    def load(self) -> None:
        return None

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        seed: int,
        max_new_tokens: int,
    ) -> GenerationResult:
        payload: dict[str, Any] = {
            "model": self.config.model_id,
            "messages": messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": max_new_tokens,
            "stream": False,
        }
        if not self.config.omit_seed:
            payload["seed"] = seed
        payload.update(self.config.extra_body)

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            try:
                self._throttle_if_needed()
                started_at = time.perf_counter()
                response = self.session.post(
                    f"{self.config.base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    timeout=self.config.timeout_seconds,
                )
                response.raise_for_status()
                body = response.json()
                usage = body.get("usage", {}) if isinstance(body, dict) else {}
                return GenerationResult(
                    content=body["choices"][0]["message"]["content"].strip(),
                    latency_seconds=time.perf_counter() - started_at,
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                    raw_response=body if isinstance(body, dict) else None,
                )
            except Exception as exc:
                last_error = exc
                should_sleep = False
                if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
                    if exc.response.status_code in {429, 500, 502, 503, 504}:
                        should_sleep = True
                        retry_after_header = exc.response.headers.get("Retry-After")
                        if retry_after_header:
                            try:
                                retry_after_seconds = float(retry_after_header)
                            except ValueError:
                                retry_after_seconds = None
                        else:
                            retry_after_seconds = None
                elif isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
                    should_sleep = True
                    retry_after_seconds = None
                else:
                    retry_after_seconds = None

                if should_sleep and attempt + 1 < self.config.max_retries:
                    computed_delay = min(
                        self.config.retry_max_delay_seconds,
                        self.config.retry_base_delay_seconds * (2 ** attempt),
                    )
                    sleep_seconds = retry_after_seconds if retry_after_seconds is not None else computed_delay
                    time.sleep(max(0.0, sleep_seconds))
        assert last_error is not None
        raise last_error

    def _throttle_if_needed(self) -> None:
        min_interval = max(0.0, self.config.min_request_interval_seconds)
        if min_interval <= 0:
            self._last_request_started_at = time.monotonic()
            return

        now = time.monotonic()
        elapsed = now - self._last_request_started_at
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request_started_at = time.monotonic()
