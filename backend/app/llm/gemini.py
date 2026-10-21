"""Gemini provider (google-genai SDK, free tier)."""

from __future__ import annotations

import re
from typing import Any, Literal

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
from app.llm.schema import inline_refs
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


def _detail_text(response_json: Any) -> str:
    """Field violations etc. from the error body; a bare "invalid argument" says nothing."""
    try:
        details = response_json["error"]["details"]
    except (KeyError, TypeError):
        return ""
    parts: list[str] = []
    for detail in details if isinstance(details, list) else []:
        if not isinstance(detail, dict):
            continue
        for v in detail.get("fieldViolations", []) or []:
            parts.append(f"{v.get('field', '?')}: {v.get('description', '')}")
        if "reason" in detail:
            parts.append(str(detail["reason"]))
    return f" [{'; '.join(parts)}]" if parts else ""


def map_api_error(exc: genai_errors.APIError) -> LLMError:
    code = exc.code
    msg = f"gemini HTTP {code}: {exc.message or exc}{_detail_text(exc.details)}"
    if code == 429:
        return RateLimitedError(msg, retry_after_s=_retry_after(exc.details))
    if code in (401, 403):
        return ProviderUnavailableError(msg)
    if code >= 500 or code == 408:
        return TransientError(msg)
    return LLMError(msg)


# Ways to switch thinking off, tried in order. Gemini 2.5 takes thinking_budget=0; Gemini 3.x
# uses thinking_level instead and can reject a budget of 0; "default" sends no thinking config.
ThinkingOffMode = Literal["budget", "level", "default"]
_THINKING_OFF_MODES: tuple[ThinkingOffMode, ...] = ("budget", "level", "default")


class GeminiProvider:
    name = "gemini"

    def __init__(
        self, api_key: str, timeout_s: float = 120.0, client: genai.Client | None = None
    ) -> None:
        self._client = client or genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
        )
        # Per model: the first thinking-off mode it accepted (or the one to try next).
        self._off_mode: dict[str, int] = {}

    def _config(
        self, request: ProviderRequest, off_mode: ThinkingOffMode = "budget"
    ) -> types.GenerateContentConfig:
        config = types.GenerateContentConfig(
            temperature=request.temperature,
            system_instruction=request.system,
        )
        if request.json_schema is not None:
            config.response_mime_type = "application/json"
            config.response_json_schema = inline_refs(request.json_schema)
        if not request.thinking:
            # Thinking off by default (CLAUDE.md); how depends on the model generation.
            if off_mode == "budget":
                config.thinking_config = types.ThinkingConfig(thinking_budget=0)
            elif off_mode == "level":
                config.thinking_config = types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                )
        return config

    def _send(self, request: ProviderRequest, off_mode: ThinkingOffMode) -> Any:
        try:
            return self._client.models.generate_content(
                model=request.model,
                contents=request.prompt,
                config=self._config(request, off_mode),
            )
        except genai_errors.APIError as exc:
            raise map_api_error(exc) from exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise TransientError(f"gemini transport error: {exc}") from exc

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        if request.thinking:
            response = self._send(request, "default")
        else:
            idx = self._off_mode.get(request.model, 0)
            while True:
                try:
                    response = self._send(request, _THINKING_OFF_MODES[idx])
                    break
                except LLMError as exc:
                    # A 400 here is usually the thinking config; try the next way to turn it off.
                    is_400 = isinstance(exc.__cause__, genai_errors.APIError) and (
                        exc.__cause__.code == 400
                    )
                    if not is_400 or idx == len(_THINKING_OFF_MODES) - 1:
                        raise
                    idx += 1
            self._off_mode[request.model] = idx

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
