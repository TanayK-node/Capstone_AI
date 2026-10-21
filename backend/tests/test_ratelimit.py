import pytest

from app.config import RateLimit
from app.llm.errors import QuotaExhaustedError
from app.llm.ratelimit import RateLimiter, TokenBucket
from tests.conftest import FakeClock


def test_bucket_allows_burst_then_waits(clock: FakeClock) -> None:
    bucket = TokenBucket(per_minute=6, clock=clock)
    assert all(bucket.try_take() == 0.0 for _ in range(6))
    wait = bucket.try_take()
    assert wait == pytest.approx(10.0)  # 6/min = one token per 10 s
    clock.now += 10.0
    assert bucket.try_take() == 0.0


def test_limiter_sleeps_for_rpm(clock: FakeClock) -> None:
    limiter = RateLimiter(lambda p, m: RateLimit(rpm=2), clock=clock, sleep=clock.sleep)
    for _ in range(3):
        limiter.acquire("gemini", "flash")
    assert clock.sleeps == [pytest.approx(30.0)]


def test_limiter_raises_when_daily_quota_spent(clock: FakeClock) -> None:
    day = ["2026-10-21"]
    limiter = RateLimiter(
        lambda p, m: RateLimit(rpm=None, rpd=2), clock=clock, sleep=clock.sleep, day=lambda: day[0]
    )
    limiter.acquire("gemini", "flash")
    limiter.acquire("gemini", "flash")
    with pytest.raises(QuotaExhaustedError):
        limiter.acquire("gemini", "flash")
    # Other models have their own budget.
    limiter.acquire("gemini", "flash-lite")
    # Budget resets on the next UTC day.
    day[0] = "2026-10-22"
    limiter.acquire("gemini", "flash")
    usage = {u["model"]: u for u in limiter.usage()}
    assert usage["flash"]["used_today"] == 1
    assert usage["flash"]["remaining_today"] == 1


def test_penalize_delays_next_request(clock: FakeClock) -> None:
    limiter = RateLimiter(lambda p, m: RateLimit(rpm=60), clock=clock, sleep=clock.sleep)
    limiter.acquire("gemini", "flash")
    limiter.penalize("gemini", "flash", 5.0)
    limiter.acquire("gemini", "flash")
    assert sum(clock.sleeps) == pytest.approx(5.0)
