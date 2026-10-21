import pytest

from app.config import Settings


def test_loads_model_names_from_yaml(settings: Settings) -> None:
    assert settings.llm.primary == "gemini"
    assert settings.llm.gemini.models.for_role("extraction")
    assert settings.llm.ollama.models.for_role("small")


def test_env_overrides_nested_yaml_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPERLENS_LLM__PRIMARY", "ollama")
    monkeypatch.setenv("PAPERLENS_LLM__GEMINI__MODELS__EXTRACTION", "gemini-test-model")
    monkeypatch.setenv("GEMINI_API_KEY", "secret")
    s = Settings(_env_file=None)
    assert s.llm.primary == "ollama"
    assert s.llm.gemini.models.extraction == "gemini-test-model"
    # Untouched siblings still come from YAML.
    assert s.llm.gemini.models.small
    assert s.gemini_api_key is not None and s.gemini_api_key.get_secret_value() == "secret"


def test_rate_limit_falls_back_to_default(settings: Settings) -> None:
    unknown = settings.llm.gemini.rate_limit_for("some-new-model")
    assert unknown == settings.llm.gemini.default_rate_limit
