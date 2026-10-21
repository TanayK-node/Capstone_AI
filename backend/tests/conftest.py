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
    return Settings(_env_file=None)


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
