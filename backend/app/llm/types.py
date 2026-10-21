"""Request/response types shared by the LLM client and providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class ProviderRequest:
    model: str
    prompt: str
    system: str | None = None
    # JSON schema the output must follow; None means free text.
    json_schema: dict[str, Any] | None = None
    thinking: bool = False
    temperature: float = 0.0


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class Provider(Protocol):
    """One LLM backend (Gemini, Ollama). Implementations map their errors to llm.errors."""

    name: str

    def generate(self, request: ProviderRequest) -> ProviderResponse: ...

    def list_models(self) -> list[str]: ...


@dataclass(frozen=True)
class CallMeta:
    """What actually served a call. Stored with every result so experiments stay comparable."""

    provider: str
    model: str
    prompt_version: str
    cached: bool
    latency_s: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    repaired: bool = False  # True if the first output failed validation and the re-ask fixed it
    fell_back: bool = False  # True if the primary provider was skipped or failed for this call


@dataclass(frozen=True)
class TextResult:
    text: str
    meta: CallMeta


@dataclass(frozen=True)
class JSONResult(Generic[T]):
    value: T
    raw: str
    meta: CallMeta = field(compare=False)
