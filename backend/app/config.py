"""Typed settings loaded from config/config.yaml, overridden by env vars / .env.

Precedence (highest first): explicit kwargs > environment > .env file > config.yaml.
Nested keys use "__" in env vars: PAPERLENS_LLM__GEMINI__MODELS__EXTRACTION=...
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "config.yaml"

ProviderName = Literal["gemini", "ollama"]
ModelRole = Literal["extraction", "small", "vision"]


def config_path() -> Path:
    return Path(os.environ.get("PAPERLENS_CONFIG", DEFAULT_CONFIG_PATH))


class AppSection(BaseModel):
    env: str = "dev"
    log_level: str = "INFO"
    data_dir: Path = Path("./data")


class RateLimit(BaseModel):
    rpm: int | None = None  # requests per minute; None = unlimited
    rpd: int | None = None  # requests per day; None = unlimited


class RetrySection(BaseModel):
    max_attempts: int = 4
    base_delay_s: float = 2.0
    max_delay_s: float = 30.0
    jitter: float = 0.5


class ModelRoles(BaseModel):
    extraction: str
    small: str
    vision: str

    def for_role(self, role: ModelRole) -> str:
        model: str = getattr(self, role)
        return model


class ProviderSection(BaseModel):
    models: ModelRoles
    rate_limits: dict[str, RateLimit] = Field(default_factory=dict)
    default_rate_limit: RateLimit = Field(default_factory=RateLimit)

    def rate_limit_for(self, model: str) -> RateLimit:
        return self.rate_limits.get(model, self.default_rate_limit)


class OllamaSection(ProviderSection):
    base_url: str = "http://localhost:11434"
    num_ctx: int = 8192


class LLMSection(BaseModel):
    primary: ProviderName = "gemini"
    fallback: ProviderName | None = "ollama"
    fallback_after_failures: int = 3
    fallback_cooldown_s: float = 300.0
    request_timeout_s: float = 120.0
    cache_version: int = 1
    retry: RetrySection = Field(default_factory=RetrySection)
    gemini: ProviderSection
    ollama: OllamaSection
    thinking_default: bool = False


class EmbeddingsSection(BaseModel):
    model: str = "BAAI/bge-small-en-v1.5"
    device: str = "cpu"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PAPERLENS_",
        env_nested_delimiter="__",
        env_file=(REPO_ROOT / ".env", ".env"),
        extra="ignore",
    )

    app: AppSection = Field(default_factory=AppSection)
    database_url: str = "sqlite:///./paperlens.db"
    redis_url: str = "redis://localhost:6379/0"
    grobid_url: str = "http://localhost:8070"
    llm: LLMSection
    embeddings: EmbeddingsSection = Field(default_factory=EmbeddingsSection)
    features: dict[str, bool] = Field(default_factory=dict)

    # Secrets: read from the conventional unprefixed names as well.
    gemini_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "GEMINI_API_KEY", "GOOGLE_API_KEY", "PAPERLENS_GEMINI_API_KEY"
        ),
    )
    github_token: SecretStr | None = Field(
        default=None, validation_alias=AliasChoices("GITHUB_TOKEN", "PAPERLENS_GITHUB_TOKEN")
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_source = YamlConfigSettingsSource(settings_cls, yaml_file=config_path())
        return (init_settings, env_settings, dotenv_settings, yaml_source, file_secret_settings)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # required fields (llm) come from config.yaml
