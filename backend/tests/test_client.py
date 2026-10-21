import random

import pytest

from app import prompts
from app.config import Settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient, strip_json_fences
from app.llm.errors import (
    AllProvidersFailedError,
    LLMValidationError,
    ProviderUnavailableError,
    QuotaExhaustedError,
    RateLimitedError,
    TransientError,
)
from app.schemas.toy import TOY_TEXT, ToyExtraction
from tests.conftest import FakeClock, FakeProvider

GOOD = '{"title": "Attention Is All You Need", "datasets": ["WMT 2014 English-German"]}'


def make_client(
    settings: Settings, clock: FakeClock, gemini: FakeProvider | None, ollama: FakeProvider | None
) -> LLMClient:
    providers = {p.name: p for p in (gemini, ollama) if p is not None}
    return LLMClient(
        settings,
        providers,  # type: ignore[arg-type]
        MemoryCache(),
        clock=clock,
        sleep=clock.sleep,
        rng=random.Random(0),
    )


def toy_prompt() -> prompts.RenderedPrompt:
    return prompts.render("toy_extract", text=TOY_TEXT)


def test_json_call_validates_and_records_meta(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", [GOOD])
    client = make_client(settings, clock, gemini, FakeProvider("ollama", [GOOD]))
    result = client.generate_json(toy_prompt(), ToyExtraction)
    assert result.value.title == "Attention Is All You Need"
    assert result.meta.provider == "gemini"
    assert result.meta.model == settings.llm.gemini.models.extraction
    assert result.meta.prompt_version == "toy_extract@1"
    assert not result.meta.cached
    # The Pydantic schema is passed to the provider, thinking off by default.
    assert gemini.calls[0].json_schema == ToyExtraction.model_json_schema()
    assert gemini.calls[0].thinking is False


def test_second_identical_call_is_served_from_cache(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", [GOOD])
    client = make_client(settings, clock, gemini, None)
    client.generate_json(toy_prompt(), ToyExtraction)
    again = client.generate_json(toy_prompt(), ToyExtraction)
    assert again.meta.cached
    assert len(gemini.calls) == 1


def test_role_selects_model(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", [GOOD])
    client = make_client(settings, clock, gemini, None)
    result = client.generate_json(toy_prompt(), ToyExtraction, role="small")
    assert result.meta.model == settings.llm.gemini.models.small


def test_invalid_output_is_repaired_once(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", ['{"title": 1}', GOOD])
    client = make_client(settings, clock, gemini, None)
    result = client.generate_json(toy_prompt(), ToyExtraction)
    assert result.meta.repaired
    assert len(gemini.calls) == 2
    assert "did not match the required JSON schema" in gemini.calls[1].prompt
    # The repaired answer is cached under the original request.
    assert client.generate_json(toy_prompt(), ToyExtraction).meta.cached


def test_still_invalid_after_repair_raises(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", ["not json"])
    client = make_client(settings, clock, gemini, FakeProvider("ollama", [GOOD]))
    with pytest.raises(LLMValidationError) as info:
        client.generate_json(toy_prompt(), ToyExtraction)
    assert info.value.raw_output == "not json"
    assert len(gemini.calls) == 2  # original + one repair, no fallback for bad output


def test_json_fences_are_stripped() -> None:
    assert strip_json_fences('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert strip_json_fences(' {"a": 1} ') == '{"a": 1}'


def test_429_backs_off_then_succeeds(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", [RateLimitedError("429", retry_after_s=7.0), GOOD])
    client = make_client(settings, clock, gemini, None)
    result = client.generate_json(toy_prompt(), ToyExtraction)
    assert result.meta.provider == "gemini"
    # Delay honours the server's retry hint (7 s) within the jitter band.
    jitter = settings.llm.retry.jitter
    assert any(7.0 * (1 - jitter) <= s <= 7.0 * (1 + jitter) for s in clock.sleeps)


def test_falls_back_to_ollama_when_gemini_keeps_failing(
    settings: Settings, clock: FakeClock
) -> None:
    gemini = FakeProvider("gemini", [RateLimitedError("429")])
    ollama = FakeProvider("ollama", [GOOD])
    client = make_client(settings, clock, gemini, ollama)
    result = client.generate_json(toy_prompt(), ToyExtraction)
    assert result.meta.provider == "ollama"
    assert result.meta.fell_back
    assert result.meta.model == settings.llm.ollama.models.extraction
    assert len(gemini.calls) == settings.llm.retry.max_attempts


def test_sticky_fallback_after_n_failed_calls_then_recovers(
    settings: Settings, clock: FakeClock
) -> None:
    gemini = FakeProvider("gemini", [TransientError("503")])
    ollama = FakeProvider("ollama", [GOOD])
    client = make_client(settings, clock, gemini, ollama)
    n = settings.llm.fallback_after_failures
    for i in range(n):
        client.generate_text(f"q{i}")
    assert client.status()["degraded"] is True
    calls_before = len(gemini.calls)
    client.generate_text("next")
    assert len(gemini.calls) == calls_before  # primary skipped during cooldown

    clock.now += settings.llm.fallback_cooldown_s + 1
    gemini.script = ["back"]
    gemini.calls.clear()
    assert client.generate_text("later").meta.provider == "gemini"
    assert client.status()["degraded"] is False


def test_quota_exhaustion_switches_immediately(settings: Settings, clock: FakeClock) -> None:
    gemini = FakeProvider("gemini", [QuotaExhaustedError("rpd")])
    ollama = FakeProvider("ollama", ["ok"])
    client = make_client(settings, clock, gemini, ollama)
    client.generate_text("q")
    assert client.status()["active"] == "ollama"
    assert len(gemini.calls) == 1  # quota errors are not retried


def test_all_providers_failing_raises_with_both_errors(
    settings: Settings, clock: FakeClock
) -> None:
    gemini = FakeProvider("gemini", [ProviderUnavailableError("bad key")])
    ollama = FakeProvider("ollama", [ProviderUnavailableError("not running")])
    client = make_client(settings, clock, gemini, ollama)
    with pytest.raises(AllProvidersFailedError) as info:
        client.generate_text("q")
    assert set(info.value.errors) == {"gemini", "ollama"}


def test_offline_mode_uses_only_ollama(settings: Settings, clock: FakeClock) -> None:
    offline = settings.model_copy(
        update={"llm": settings.llm.model_copy(update={"primary": "ollama", "fallback": None})}
    )
    ollama = FakeProvider("ollama", [GOOD])
    client = make_client(offline, clock, None, ollama)
    assert client.generate_json(toy_prompt(), ToyExtraction).meta.provider == "ollama"
    assert client.status()["degraded"] is False


def test_missing_gemini_key_goes_straight_to_ollama(settings: Settings, clock: FakeClock) -> None:
    client = make_client(settings, clock, None, FakeProvider("ollama", [GOOD]))
    result = client.generate_json(toy_prompt(), ToyExtraction)
    assert result.meta.provider == "ollama"
    assert client.status()["degraded"] is True  # UI shows "running on local model"


def test_cached_primary_answer_is_used_even_in_fallback(
    settings: Settings, clock: FakeClock
) -> None:
    gemini = FakeProvider("gemini", [GOOD])
    ollama = FakeProvider("ollama", [GOOD])
    client = make_client(settings, clock, gemini, ollama)
    client.generate_json(toy_prompt(), ToyExtraction)
    client._fallback_until = clock.now + 100  # force fallback mode
    again = client.generate_json(toy_prompt(), ToyExtraction)
    assert again.meta.cached and again.meta.provider == "gemini"
    assert ollama.calls == []
