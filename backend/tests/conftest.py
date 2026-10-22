from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

import pytest

from app.config import Settings
from app.llm.errors import LLMError
from app.llm.types import ProviderRequest, ProviderResponse


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Settings from the real config.yaml, isolated from the developer's env/.env."""
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "PAPERLENS_LLM__PRIMARY"):
        monkeypatch.delenv(var, raising=False)
    # Never download the embedding model in tests; tests that need vectors use FakeEmbedder.
    monkeypatch.setenv("PAPERLENS_EMBEDDINGS__ENABLED", "false")
    return Settings(_env_file=None)


class FakeEmbedder:
    """Deterministic bag-of-words hashing into 256 dims: shared words -> similar vectors."""

    model_name = "fake-embedder"

    def embed(self, texts: list[str], *, query: bool = False):  # type: ignore[no-untyped-def]
        import re
        import zlib

        import numpy as np

        out = np.zeros((len(texts), 256), dtype=np.float32)
        for i, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                out[i, zlib.crc32(word.encode()) % 256] += 1.0
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.maximum(norms, 1e-12)


class FakeClock:
    """Monotonic clock that only moves when sleep() is called."""

    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


Step = str | LLMError | Callable[[ProviderRequest], str]


@dataclass
class FakeProvider:
    """Replays a script of responses/errors; the last step repeats once the script runs out."""

    name: str
    script: list[Step] = field(default_factory=list)
    calls: list[ProviderRequest] = field(default_factory=list)

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self.calls.append(request)
        step = self.script[min(len(self.calls), len(self.script)) - 1]
        if isinstance(step, LLMError):
            raise step
        text = step(request) if callable(step) else step
        return ProviderResponse(text=text, input_tokens=10, output_tokens=5)

    def list_models(self) -> list[str]:
        return ["fake-model"]


@pytest.fixture
def no_log_noise(caplog: pytest.LogCaptureFixture) -> Iterator[None]:
    caplog.set_level("ERROR")
    yield
