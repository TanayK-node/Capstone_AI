"""Gemini provider (google-genai SDK, free tier)."""

from __future__ import annotations

import re
from typing import Any

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.llm.errors import (
    LLMError,
    ProviderUnavailableError,
    RateLimitedError,
    TransientError,
)
from app.llm.types import ProviderRequest, ProviderResponse

_RETRY_DELAY_RE = re.compile(r"^(\d+(?:\.\d+)?)s$")


def _retry_after(response_json: Any) -> float | None:
    """Pull RetryInfo.retryDelay ("37s") out of a 429 body, if present."""
    try:
        details = response_json["error"]["details"]
    except (KeyError, TypeError):
        return None
    for detail in details if isinstance(details, list) else []:
        delay = detail.get("retryDelay") if isinstance(detail, dict) else None
        if isinstance(delay, str) and (m := _RETRY_DELAY_RE.match(delay)):
            return float(m.group(1))
    return None


def map_api_error(exc: genai_errors.APIError) -> LLMError:
    code = exc.code
    msg = f"gemini HTTP {code}: {exc.message or exc}"
    if code == 429:
        return RateLimitedError(msg, retry_after_s=_retry_after(exc.details))
    if code in (401, 403):
        return ProviderUnavailableError(msg)
    if code >= 500 or code == 408:
        return TransientError(msg)
    return LLMError(msg)


class GeminiProvider:
    name = "gemini"

    def __init__(
        self, api_key: str, timeout_s: float = 120.0, client: genai.Client | None = None
    ) -> None:
        self._client = client or genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
        )

    def _config(self, request: ProviderRequest) -> types.GenerateContentConfig:
        config = types.GenerateContentConfig(
            temperature=request.temperature,
            system_instruction=request.system,
        )
        if request.json_schema is not None:
            config.response_mime_type = "application/json"
            config.response_json_schema = request.json_schema
        if not request.thinking:
            # Budget 0 turns thinking off on Flash / Flash-Lite (CLAUDE.md: off by default).
            config.thinking_config = types.ThinkingConfig(thinking_budget=0)
        return config

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        try:
            response = self._client.models.generate_content(
                model=request.model, contents=request.prompt, config=self._config(request)
            )
        except genai_errors.APIError as exc:
            raise map_api_error(exc) from exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise TransientError(f"gemini transport error: {exc}") from exc

        text = response.text
        if not text:
            reason = response.candidates[0].finish_reason if response.candidates else None
            raise LLMError(f"gemini returned no text (finish_reason={reason})")
        usage = response.usage_metadata
        return ProviderResponse(
            text=text,
            input_tokens=usage.prompt_token_count if usage else None,
            output_tokens=usage.candidates_token_count if usage else None,
        )

    def list_models(self) -> list[str]:
        try:
            return sorted(
                (m.name or "").removeprefix("models/")
                for m in self._client.models.list()
                if "generateContent" in (m.supported_actions or [])
            )
        except genai_errors.APIError as exc:
            raise map_api_error(exc) from exc
