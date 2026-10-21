"""Provider adapters, with the network mocked out."""

import json
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from google.genai import errors as genai_errors

from app.llm.errors import (
    LLMError,
    ProviderUnavailableError,
    RateLimitedError,
    TransientError,
)
from app.llm.gemini import GeminiProvider
from app.llm.ollama import OllamaProvider
from app.llm.types import ProviderRequest

REQ = ProviderRequest(model="m", prompt="hi", system="sys", json_schema={"type": "object"})


# ------------------------------------------------------------------ Gemini


class FakeModels:
    """outcome: a response, an exception, or a callable(config) returning/raising either."""

    def __init__(self, outcome: Any) -> None:
        self.outcome = outcome
        self.kwargs: dict[str, Any] = {}
        self.configs: list[Any] = []

    def generate_content(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        self.configs.append(kwargs["config"])
        outcome = self.outcome(kwargs["config"]) if callable(self.outcome) else self.outcome
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def gemini_with(outcome: Any) -> tuple[GeminiProvider, FakeModels]:
    models = FakeModels(outcome)
    client = SimpleNamespace(models=models)
    return GeminiProvider("key", client=client), models  # type: ignore[arg-type]


def test_gemini_builds_json_config_with_thinking_off() -> None:
    usage = SimpleNamespace(prompt_token_count=12, candidates_token_count=3)
    provider, models = gemini_with(
        SimpleNamespace(text='{"a": 1}', usage_metadata=usage, candidates=[])
    )
    resp = provider.generate(REQ)
    assert (resp.text, resp.input_tokens, resp.output_tokens) == ('{"a": 1}', 12, 3)
    config = models.kwargs["config"]
    assert models.kwargs["model"] == "m"
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == {"type": "object"}
    assert config.system_instruction == "sys"
    assert config.thinking_config.thinking_budget == 0


def test_gemini_thinking_on_leaves_budget_unset() -> None:
    provider, models = gemini_with(SimpleNamespace(text="x", usage_metadata=None, candidates=[]))
    provider.generate(ProviderRequest(model="m", prompt="p", thinking=True))
    assert models.kwargs["config"].thinking_config is None


def api_error(code: int, body: dict[str, Any] | None = None) -> genai_errors.APIError:
    return genai_errors.APIError(code, body or {"error": {"message": f"err {code}"}})


OK_RESPONSE = SimpleNamespace(text="ok", usage_metadata=None, candidates=[])


def test_gemini_switches_to_thinking_level_when_budget_is_rejected() -> None:
    """Gemini 3.x rejects thinking_budget=0 with a 400; retry with thinking_level=MINIMAL."""

    def outcome(config: Any) -> Any:
        if config.thinking_config is not None and config.thinking_config.thinking_budget == 0:
            return api_error(400, {"error": {"message": "Request contains an invalid argument."}})
        return OK_RESPONSE

    provider, models = gemini_with(outcome)
    assert provider.generate(REQ).text == "ok"
    assert models.configs[-1].thinking_config.thinking_level == "MINIMAL"
    # The working mode is remembered: the next call goes straight to thinking_level.
    models.configs.clear()
    provider.generate(REQ)
    assert len(models.configs) == 1


def test_gemini_drops_thinking_config_when_both_are_rejected() -> None:
    def outcome(config: Any) -> Any:
        if config.thinking_config is not None:
            return api_error(400)
        return OK_RESPONSE

    provider, models = gemini_with(outcome)
    assert provider.generate(REQ).text == "ok"
    assert len(models.configs) == 3


def test_gemini_400_unrelated_to_thinking_still_raises_with_details() -> None:
    body = {
        "error": {
            "message": "Request contains an invalid argument.",
            "details": [{"fieldViolations": [{"field": "contents", "description": "empty"}]}],
        }
    }
    provider, models = gemini_with(api_error(400, body))
    with pytest.raises(LLMError, match=r"contents: empty"):
        provider.generate(REQ)
    assert len(models.configs) == 3  # tried every thinking mode first


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (429, RateLimitedError),
        (503, TransientError),
        (403, ProviderUnavailableError),
        (400, LLMError),
    ],
)
def test_gemini_maps_http_errors(code: int, expected: type[Exception]) -> None:
    provider, _ = gemini_with(api_error(code))
    with pytest.raises(expected):
        provider.generate(REQ)


def test_gemini_429_reads_retry_delay() -> None:
    body = {
        "error": {
            "message": "quota",
            "details": [{"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "37s"}],
        }
    }
    provider, _ = gemini_with(api_error(429, body))
    with pytest.raises(RateLimitedError) as info:
        provider.generate(REQ)
    assert info.value.retry_after_s == 37.0


# ------------------------------------------------------------------ Ollama


def ollama_with(handler: Any) -> OllamaProvider:
    http = httpx.Client(base_url="http://ollama", transport=httpx.MockTransport(handler))
    return OllamaProvider("http://ollama", num_ctx=4096, http=http)


def test_ollama_sends_schema_and_think_flag() -> None:
    seen: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={"message": {"content": '{"a": 1}'}, "prompt_eval_count": 7, "eval_count": 2},
        )

    resp = ollama_with(handler).generate(REQ)
    assert (resp.text, resp.input_tokens, resp.output_tokens) == ('{"a": 1}', 7, 2)
    body = seen[0]
    assert body["format"] == {"type": "object"}
    assert body["think"] is False
    assert body["stream"] is False
    assert body["options"]["num_ctx"] == 4096
    assert body["messages"][0] == {"role": "system", "content": "sys"}


def test_ollama_retries_without_think_for_models_that_reject_it() -> None:
    bodies: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        bodies.append(body)
        if "think" in body:
            return httpx.Response(400, json={"error": '"m" does not support thinking'})
        return httpx.Response(200, json={"message": {"content": "ok"}})

    provider = ollama_with(handler)
    assert provider.generate(REQ).text == "ok"
    provider.generate(REQ)
    assert len(bodies) == 3  # one rejected call, then never sends `think` again


def test_ollama_connection_refused_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(ProviderUnavailableError, match="ollama serve"):
        ollama_with(handler).generate(REQ)


@pytest.mark.parametrize(
    ("status", "expected", "match"),
    [(404, LLMError, "ollama pull m"), (500, TransientError, "500")],
)
def test_ollama_http_errors(status: int, expected: type[Exception], match: str) -> None:
    provider = ollama_with(lambda r: httpx.Response(status, text="boom"))
    with pytest.raises(expected, match=match):
        provider.generate(REQ)
