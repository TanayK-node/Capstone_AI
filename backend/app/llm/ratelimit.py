"""Per-model rate limiting: a token bucket for RPM and a counter for RPD.

Limits are enforced in-process. Run the Celery worker with one process that owns LLM
calls (the compose file does) or the per-project free-tier limits will be overshot.
A Redis-backed limiter can replace this behind the same interface if that changes.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.config import RateLimit
from app.llm.errors import QuotaExhaustedError

Clock = Callable[[], float]
Sleep = Callable[[float], None]


class TokenBucket:
    """Classic token bucket. capacity = rate per minute, refilled continuously."""

    def __init__(self, per_minute: int, clock: Clock = time.monotonic) -> None:
        if per_minute <= 0:
            raise ValueError("per_minute must be positive")
        self.capacity = float(per_minute)
        self.refill_per_s = per_minute / 60.0
        self._tokens = self.capacity
        self._clock = clock
        self._last = clock()

    def _refill(self) -> None:
        now = self._clock()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.refill_per_s)
        self._last = now

    def try_take(self) -> float:
        """Take a token if one is available. Returns 0.0 on success, else seconds to wait."""
        self._refill()
        # Tolerance: after sleeping exactly the computed wait, float error can leave 0.9999999.
        if self._tokens >= 1.0 - 1e-9:
            self._tokens -= 1.0
            return 0.0
        return (1.0 - self._tokens) / self.refill_per_s

    def drain_for(self, seconds: float) -> None:
        """Empty the bucket so the next token only appears after `seconds`."""
        self._refill()
        self._tokens = min(self._tokens, 1.0 - seconds * self.refill_per_s)

    @property
    def available(self) -> float:
        self._refill()
        return self._tokens


def _utc_day() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


@dataclass
class _ModelState:
    limit: RateLimit
    bucket: TokenBucket | None
    day: str
    used_today: int = 0


class RateLimiter:
    """Holds a bucket and a daily counter per (provider, model)."""

    def __init__(
        self,
        limits: Callable[[str, str], RateLimit],
        clock: Clock = time.monotonic,
        sleep: Sleep = time.sleep,
        day: Callable[[], str] = _utc_day,
    ) -> None:
        self._limits = limits
        self._clock = clock
        self._sleep = sleep
        self._day = day
        self._state: dict[tuple[str, str], _ModelState] = {}
        self._lock = threading.Lock()

    def _get(self, provider: str, model: str) -> _ModelState:
        key = (provider, model)
        state = self._state.get(key)
        if state is None:
            limit = self._limits(provider, model)
            bucket = TokenBucket(limit.rpm, self._clock) if limit.rpm else None
            state = _ModelState(limit=limit, bucket=bucket, day=self._day())
            self._state[key] = state
        today = self._day()
        if state.day != today:
            state.day, state.used_today = today, 0
        return state

    def acquire(self, provider: str, model: str) -> None:
        """Block until a request may be sent. Raises QuotaExhaustedError if RPD is spent."""
        while True:
            with self._lock:
                state = self._get(provider, model)
                rpd = state.limit.rpd
                if rpd is not None and state.used_today >= rpd:
                    raise QuotaExhaustedError(
                        f"{provider}/{model}: daily limit of {rpd} requests reached"
                    )
                wait = state.bucket.try_take() if state.bucket else 0.0
                if wait == 0.0:
                    state.used_today += 1
                    return
            self._sleep(max(wait, 0.01))

    def penalize(self, provider: str, model: str, seconds: float) -> None:
        """After a 429, drain the bucket so other threads also back off."""
        with self._lock:
            state = self._get(provider, model)
            if state.bucket is not None:
                state.bucket.drain_for(seconds)

    def usage(self) -> list[dict[str, object]]:
        """Snapshot for the settings / health endpoint and the UI quota badge."""
        with self._lock:
            out: list[dict[str, object]] = []
            for (provider, model), state in sorted(self._state.items()):
                self._get(provider, model)  # roll the day over if needed
                rpd = state.limit.rpd
                out.append(
                    {
                        "provider": provider,
                        "model": model,
                        "rpm": state.limit.rpm,
                        "rpd": rpd,
                        "used_today": state.used_today,
                        "remaining_today": None if rpd is None else max(0, rpd - state.used_today),
                    }
                )
            return out
