"""Phase 0 exit criterion: both real providers return schema-valid JSON for a toy schema.

Run with `uv run pytest -m live`. Each test skips if its provider isn't set up.
"""

import httpx
import pytest

from app import prompts
from app.config import Settings, get_settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.llm.gemini import GeminiProvider
from app.llm.ollama import OllamaProvider
from app.llm.types import Provider
from app.schemas.toy import TOY_TEXT, ToyExtraction

pytestmark = pytest.mark.live


def solo_client(settings: Settings, provider: Provider) -> LLMClient:
    """Client with fallback disabled, so the test proves this provider on its own."""
    llm = settings.llm.model_copy(update={"primary": provider.name, "fallback": None})
    return LLMClient(settings.model_copy(update={"llm": llm}), {provider.name: provider}, None)


def check_toy(client: LLMClient) -> None:
    result = client.generate_json(prompts.render("toy_extract", text=TOY_TEXT), ToyExtraction)
    assert "attention" in result.value.title.lower()
    joined = " ".join(result.value.datasets).lower()
    assert "wmt" in joined
    assert not result.meta.cached


def test_gemini_returns_valid_json() -> None:
    settings = get_settings()
    if settings.gemini_api_key is None:
        pytest.skip("GEMINI_API_KEY not set")
    provider = GeminiProvider(settings.gemini_api_key.get_secret_value())
    check_toy(solo_client(settings, provider))


def test_ollama_returns_valid_json() -> None:
    settings = get_settings()
    base = settings.llm.ollama.base_url
    try:
        tags = httpx.get(f"{base}/api/tags", timeout=3).json()
    except httpx.HTTPError:
        pytest.skip(f"Ollama not reachable at {base}")
    model = settings.llm.ollama.models.extraction
    if not any(m["name"] == model for m in tags.get("models", [])):
        pytest.skip(f"model {model} not pulled; run `ollama pull {model}`")
    provider = OllamaProvider(base, num_ctx=settings.llm.ollama.num_ctx, timeout_s=300)
    check_toy(solo_client(settings, provider))


def test_cache_makes_second_call_free() -> None:
    settings = get_settings()
    if settings.gemini_api_key is None:
        pytest.skip("GEMINI_API_KEY not set")
    provider = GeminiProvider(settings.gemini_api_key.get_secret_value())
    client = solo_client(settings, provider)
    client.cache = MemoryCache()
    prompt = prompts.render("toy_extract", text=TOY_TEXT)
    client.generate_json(prompt, ToyExtraction, role="small")
    assert client.generate_json(prompt, ToyExtraction, role="small").meta.cached
