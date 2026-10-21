"""Error types raised by the LLM gateway and its providers.

The client uses these classes to decide what to do: retry with backoff, fall back to
the other provider, or fail the call.
"""

from __future__ import annotations


class LLMError(Exception):
    """Base class. Raised as-is for non-retryable provider errors (e.g. HTTP 400)."""


class TransientError(LLMError):
    """Timeouts, 5xx and similar; worth retrying on the same provider."""


class RateLimitedError(TransientError):
    """HTTP 429 from the provider. retry_after_s is the server's hint, if it sent one."""

    def __init__(self, message: str, retry_after_s: float | None = None) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s


class QuotaExhaustedError(LLMError):
    """Our own limiter says the daily budget for this model is spent. Fall back at once."""


class ProviderUnavailableError(LLMError):
    """Provider not configured, unreachable, or rejecting our credentials."""


class LLMValidationError(LLMError):
    """Output still failed schema validation after the repair retry."""

    def __init__(self, message: str, raw_output: str) -> None:
        super().__init__(message)
        self.raw_output = raw_output


class AllProvidersFailedError(LLMError):
    """Every provider in the chain failed for this call."""

    def __init__(self, errors: dict[str, LLMError]) -> None:
        detail = "; ".join(f"{name}: {type(e).__name__}: {e}" for name, e in errors.items())
        super().__init__(f"all LLM providers failed ({detail})")
        self.errors = errors
