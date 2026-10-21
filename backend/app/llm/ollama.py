"""Ollama provider for local Qwen models (offline mode and fallback)."""

from __future__ import annotations

from typing import Any

import httpx

from app.llm.errors import LLMError, ProviderUnavailableError, TransientError
from app.llm.types import ProviderRequest, ProviderResponse


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        num_ctx: int = 8192,
        timeout_s: float = 120.0,
        http: httpx.Client | None = None,
    ) -> None:
        self._num_ctx = num_ctx
        self._http = http or httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout_s)
        # Models that rejected the `think` flag; we stop sending it to them.
        self._no_think: set[str] = set()

    def _body(self, request: ProviderRequest) -> dict[str, Any]:
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.append({"role": "user", "content": request.prompt})
        body: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": request.temperature, "num_ctx": self._num_ctx},
        }
        if request.json_schema is not None:
            body["format"] = request.json_schema  # Ollama structured outputs
        if request.model not in self._no_think:
            body["think"] = request.thinking
        return body

    def _post(self, path: str, body: dict[str, Any]) -> httpx.Response:
        try:
            return self._http.post(path, json=body)
        except httpx.ConnectError as exc:
            raise ProviderUnavailableError(
                f"ollama not reachable at {self._http.base_url} (is `ollama serve` running?)"
            ) from exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise TransientError(f"ollama transport error: {exc}") from exc

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        resp = self._post("/api/chat", self._body(request))
        if resp.status_code == 400 and "think" in resp.text and request.model not in self._no_think:
            # Older or non-reasoning models reject `think`; retry once without it.
            self._no_think.add(request.model)
            resp = self._post("/api/chat", self._body(request))

        if resp.status_code == 404:
            raise LLMError(
                f"ollama model {request.model!r} not found; run `ollama pull {request.model}`"
            )
        if resp.status_code >= 500:
            raise TransientError(f"ollama HTTP {resp.status_code}: {resp.text[:200]}")
        if resp.status_code >= 400:
            raise LLMError(f"ollama HTTP {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        text = (data.get("message") or {}).get("content", "")
        if not text:
            raise LLMError(f"ollama returned no text (done_reason={data.get('done_reason')})")
        return ProviderResponse(
            text=text,
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
        )

    def list_models(self) -> list[str]:
        try:
            resp = self._http.get("/api/tags")
        except httpx.TransportError as exc:
            raise ProviderUnavailableError(f"ollama not reachable: {exc}") from exc
        resp.raise_for_status()
        return sorted(m["name"] for m in resp.json().get("models", []))
