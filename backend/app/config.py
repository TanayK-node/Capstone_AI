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
    # model -> backup model of the same provider, tried when the model stays overloaded
    # (Gemini 503 "high demand") or its daily quota is spent.
    overload_fallback: dict[str, str] = Field(default_factory=dict)

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


class IngestSection(BaseModel):
    max_mb: int = 50
    max_pages: int = 100
    allow_scanned: bool = False
    fetch_latex_source: bool = True
    download_timeout_s: float = 60.0
    contact_email: str | None = None


class ParsingSection(BaseModel):
    parser: Literal["auto", "grobid", "pymupdf"] = "auto"
    grobid_timeout_s: float = 180.0


class PipelineSection(BaseModel):
    eager: bool = False


class ExtractionSection(BaseModel):
    max_group_chars: int = 48_000
    parallel_calls: int = 2  # section-group calls in flight at once
    retry_failed_after_s: float = 20.0  # pause before re-trying groups whose call failed


class ReproSection(BaseModel):
    github_check: bool = True  # read repo metadata / README via the GitHub API (no clone)
    github_timeout_s: float = 15.0
    max_context_chars: int = 48_000  # paper text sent with the checklist LLM call


class ClaimsSection(BaseModel):
    tolerance: float = 0.15  # absolute, for recomputed values and deltas (SCOPE.md F8)


class CodeCheckSection(BaseModel):
    sandbox: Literal["auto", "docker", "process"] = "auto"
    clone_timeout_s: float = 60.0
    max_repo_mb: float = 200.0
    search_github: bool = True


class EmbeddingsSection(BaseModel):
    enabled: bool = True  # False = BM25 only (no model download)
    model: str = "BAAI/bge-small-en-v1.5"
    device: str = "cpu"
    threads: int | None = None  # ONNX Runtime threads; None = all cores


class ChatSection(BaseModel):
    top_k: int = 5  # passages given to the LLM
    candidates: int = 20  # per retriever, before fusion
    min_cosine: float = 0.45  # below this (and no shared word) the question is off-topic
    history_turns: int = 4  # earlier question/answer pairs sent with a follow-up


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
    ingest: IngestSection = Field(default_factory=IngestSection)
    parsing: ParsingSection = Field(default_factory=ParsingSection)
    pipeline: PipelineSection = Field(default_factory=PipelineSection)
    extraction: ExtractionSection = Field(default_factory=ExtractionSection)
    repro: ReproSection = Field(default_factory=ReproSection)
    claims: ClaimsSection = Field(default_factory=ClaimsSection)
    code_check: CodeCheckSection = Field(default_factory=CodeCheckSection)
    chat: ChatSection = Field(default_factory=ChatSection)
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
