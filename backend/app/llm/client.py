"""The single LLM gateway (CLAUDE.md rule 2).

Every call goes through LLMClient, which handles, in order:
  1. cache lookup (any provider in the chain, so a cached Gemini answer beats a fresh Qwen call)
  2. per-model rate limiting (RPM bucket, RPD counter)
  3. retries with exponential backoff + jitter on 429 / transient errors, then the model's
     overload fallback (another model of the same provider, e.g. Flash -> Flash-Lite)
  4. fallback from the primary provider to the fallback (sticky after N failed calls)
  5. Pydantic validation with one repair re-ask
  6. logging of provider / model / prompt_version / tokens / latency
"""

from __future__ import annotations

import logging
import random
import re
import threading
import time
from collections.abc import Callable
from dataclasses import replace
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app import prompts
from app.config import ModelRole, ProviderName, RateLimit, Settings
from app.llm.cache import CachedResponse, LLMCache, make_cache_key
from app.llm.errors import (
    AllProvidersFailedError,
    LLMError,
    LLMValidationError,
    ProviderUnavailableError,
    QuotaExhaustedError,
    RateLimitedError,
    TransientError,
)
from app.llm.ratelimit import Clock, RateLimiter, Sleep
from app.llm.types import (
    CallMeta,
    JSONResult,
    Provider,
    ProviderRequest,
    ProviderResponse,
    TextResult,
)

log = logging.getLogger("paperlens.llm")

T = TypeVar("T", bound=BaseModel)
PromptInput = str | prompts.RenderedPrompt

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


def strip_json_fences(text: str) -> str:
    """Local models sometimes wrap JSON in ```json fences despite format=schema."""
    match = _FENCE_RE.match(text)
    return match.group(1) if match else text.strip()


class LLMClient:
    def __init__(
        self,
        settings: Settings,
        providers: dict[str, Provider],
        cache: LLMCache | None,
        limiter: RateLimiter | None = None,
        *,
        clock: Clock = time.monotonic,
        sleep: Sleep = time.sleep,
        rng: random.Random | None = None,
    ) -> None:
        self.settings = settings
        self.cfg = settings.llm
        self.providers = providers
        self.cache = cache
        self.limiter = limiter or RateLimiter(self._rate_limit_for, clock=clock, sleep=sleep)
        self._clock = clock
        self._sleep = sleep
        self._rng = rng or random.Random()
        self._lock = threading.Lock()
        self._consecutive_failures = 0
        self._fallback_until: float | None = None

    # ---------------------------------------------------------------- public API

    def generate_json(
        self,
        prompt: PromptInput,
        schema: type[T],
        *,
        role: ModelRole = "extraction",
        system: str | None = None,
        thinking: bool | None = None,
        temperature: float = 0.0,
        use_cache: bool = True,
    ) -> JSONResult[T]:
        """Schema-constrained call. Returns a validated `schema` instance plus call metadata."""
        text, version = self._unpack(prompt)
        json_schema = schema.model_json_schema()
        resp, meta = self._complete(
            text, version, role, system, json_schema, thinking, temperature, use_cache
        )
        think = self.cfg.thinking_default if thinking is None else thinking
        try:
            value = self._validate(resp.text, schema)
        except ValidationError as first_error:
            log.warning("llm.validation_failed", extra={"llm": _meta_dict(meta)})
            repair = prompts.render(
                "repair_json",
                errors=_short_errors(first_error),
                previous=resp.text[:4000],
                original=text,
            )
            # Re-ask once on the provider that produced the bad output; never cached.
            repaired, rmeta = self._complete(
                repair.text,
                f"{version}+{repair.id}",
                role,
                system,
                json_schema,
                thinking,
                temperature,
                use_cache=False,
                only_provider=meta.provider,
            )
            try:
                value = self._validate(repaired.text, schema)
            except ValidationError as second_error:
                raise LLMValidationError(
                    f"output failed {schema.__name__} validation after repair: "
                    f"{_short_errors(second_error)}",
                    raw_output=repaired.text,
                ) from second_error
            final_meta = replace(
                rmeta, prompt_version=version, repaired=True, fell_back=meta.fell_back
            )
            if use_cache:
                # Cache the repaired answer under the original request's key.
                self._store(final_meta, text, system, json_schema, think, temperature, repaired)
            return JSONResult(value=value, raw=repaired.text, meta=final_meta)
        if use_cache and not meta.cached:
            self._store(meta, text, system, json_schema, think, temperature, resp)
        return JSONResult(value=value, raw=resp.text, meta=meta)

    def generate_text(
        self,
        prompt: PromptInput,
        *,
        role: ModelRole = "extraction",
        system: str | None = None,
        thinking: bool | None = None,
        temperature: float = 0.2,
        use_cache: bool = True,
    ) -> TextResult:
        text, version = self._unpack(prompt)
        resp, meta = self._complete(
            text, version, role, system, None, thinking, temperature, use_cache
        )
        return TextResult(text=resp.text, meta=meta)

    def status(self) -> dict[str, Any]:
        """Provider state for /api/health and the UI badge ("running on local model")."""
        active = self._provider_chain()
        return {
            "primary": self.cfg.primary,
            "fallback": self.cfg.fallback,
            "active": active[0] if active else None,
            "degraded": bool(active) and active[0] != self.cfg.primary,
            "configured": sorted(self.providers),
            "consecutive_failures": self._consecutive_failures,
            "usage": self.limiter.usage(),
        }

    # ---------------------------------------------------------------- internals

    @staticmethod
    def _unpack(prompt: PromptInput) -> tuple[str, str]:
        if isinstance(prompt, prompts.RenderedPrompt):
            return prompt.text, prompt.id
        return prompt, "adhoc"

    @staticmethod
    def _validate(text: str, schema: type[T]) -> T:
        return schema.model_validate_json(strip_json_fences(text))

    def _rate_limit_for(self, provider: str, model: str) -> RateLimit:
        section = self.cfg.gemini if provider == "gemini" else self.cfg.ollama
        return section.rate_limit_for(model)

    def _model_for(self, provider: str, role: ModelRole) -> str:
        section = self.cfg.gemini if provider == "gemini" else self.cfg.ollama
        return section.models.for_role(role)

    def _configured_chain(self) -> list[str]:
        primary: ProviderName = self.cfg.primary
        chain = [primary]
        if self.cfg.fallback and self.cfg.fallback != primary:
            chain.append(self.cfg.fallback)
        return [p for p in chain if p in self.providers]

    def _provider_chain(self) -> list[str]:
        """Providers to try, in order. Sticky fallback skips the primary during cooldown."""
        chain = self._configured_chain()
        with self._lock:
            if self._fallback_until is not None:
                if self._clock() < self._fallback_until:
                    chain = [p for p in chain if p != self.cfg.primary]
                else:
                    self._fallback_until = None  # cooldown over; try the primary again
        return chain

    def _record(self, provider: str, ok: bool, *, sticky: bool = False) -> None:
        if provider != self.cfg.primary:
            return
        with self._lock:
            if ok:
                self._consecutive_failures = 0
                return
            self._consecutive_failures += 1
            if sticky or self._consecutive_failures >= self.cfg.fallback_after_failures:
                if self._fallback_until is None:
                    log.warning(
                        "llm.fallback_engaged primary=%s failures=%d cooldown_s=%s",
                        provider,
                        self._consecutive_failures,
                        self.cfg.fallback_cooldown_s,
                    )
                self._fallback_until = self._clock() + self.cfg.fallback_cooldown_s

    def _key(
        self,
        provider: str,
        model: str,
        text: str,
        version: str,
        system: str | None,
        json_schema: dict[str, Any] | None,
        thinking: bool,
        temperature: float,
    ) -> str:
        return make_cache_key(
            provider=provider,
            model=model,
            prompt=text,
            system=system,
            json_schema=json_schema,
            prompt_version=version,
            thinking=thinking,
            temperature=temperature,
            cache_version=self.cfg.cache_version,
        )

    def _complete(
        self,
        text: str,
        version: str,
        role: ModelRole,
        system: str | None,
        json_schema: dict[str, Any] | None,
        thinking: bool | None,
        temperature: float,
        use_cache: bool,
        only_provider: str | None = None,
    ) -> tuple[ProviderResponse, CallMeta]:
        think = self.cfg.thinking_default if thinking is None else thinking
        if only_provider is not None:
            chain = [only_provider]
        else:
            chain = self._provider_chain()
            if not chain:
                raise ProviderUnavailableError(
                    "no LLM provider configured (set GEMINI_API_KEY or start Ollama)"
                )

        if use_cache and self.cache is not None:
            # Look in every provider's cache, primary first, even during sticky fallback.
            lookup = chain if only_provider is not None else self._configured_chain()
            for name in lookup:
                model = self._model_for(name, role)
                key = self._key(name, model, text, version, system, json_schema, think, temperature)
                hit = self.cache.get(key)
                if hit is not None:
                    meta = CallMeta(
                        provider=hit.provider,
                        model=hit.model,
                        prompt_version=version,
                        cached=True,
                        latency_s=0.0,
                        input_tokens=hit.input_tokens,
                        output_tokens=hit.output_tokens,
                    )
                    log.info("llm.cache_hit", extra={"llm": _meta_dict(meta)})
                    return ProviderResponse(hit.text, hit.input_tokens, hit.output_tokens), meta

        errors: dict[str, LLMError] = {}
        for name in chain:
            model = self._model_for(name, role)
            request = ProviderRequest(
                model=model,
                prompt=text,
                system=system,
                json_schema=json_schema,
                thinking=think,
                temperature=temperature,
            )
            started = self._clock()
            try:
                resp, model = self._call_model(name, request)
            except QuotaExhaustedError as exc:
                errors[name] = exc
                self._record(name, ok=False, sticky=True)
                continue
            except LLMError as exc:
                # Fall back on anything the provider throws; a demo must not stall.
                errors[name] = exc
                self._record(name, ok=False)
                log.warning("llm.provider_failed provider=%s model=%s error=%s", name, model, exc)
                continue

            self._record(name, ok=True)
            meta = CallMeta(
                provider=name,
                model=model,
                prompt_version=version,
                cached=False,
                latency_s=round(self._clock() - started, 3),
                input_tokens=resp.input_tokens,
                output_tokens=resp.output_tokens,
                fell_back=only_provider is None and name != self.cfg.primary,
            )
            log.info("llm.call", extra={"llm": _meta_dict(meta)})
            # JSON results are stored by generate_json, only once they validate.
            if use_cache and json_schema is None:
                self._store(meta, text, system, None, think, temperature, resp)
            return resp, meta

        raise AllProvidersFailedError(errors)

    def _store(
        self,
        meta: CallMeta,
        text: str,
        system: str | None,
        json_schema: dict[str, Any] | None,
        thinking: bool,
        temperature: float,
        resp: ProviderResponse,
    ) -> None:
        if self.cache is None:
            return
        key = self._key(
            meta.provider,
            meta.model,
            text,
            meta.prompt_version,
            system,
            json_schema,
            thinking,
            temperature,
        )
        try:
            self.cache.set(
                key,
                CachedResponse(
                    provider=meta.provider,
                    model=meta.model,
                    prompt_version=meta.prompt_version,
                    text=resp.text,
                    input_tokens=resp.input_tokens,
                    output_tokens=resp.output_tokens,
                ),
            )
        except Exception:  # a cache outage must never fail the call
            log.exception("llm.cache_write_failed")

    def _backoff(self, attempt: int, hint: float | None) -> float:
        retry = self.cfg.retry
        delay: float = min(retry.max_delay_s, retry.base_delay_s * 2.0 ** (attempt - 1))
        if hint is not None:
            delay = max(delay, min(hint, retry.max_delay_s))
        return max(0.0, delay * (1 + self._rng.uniform(-retry.jitter, retry.jitter)))

    def _call_model(self, name: str, request: ProviderRequest) -> tuple[ProviderResponse, str]:
        """Call the configured model; if it stays overloaded (5xx / 429 after every retry) or
        its daily quota is spent, try the provider's overload fallback model once.
        Returns the response and the model that actually answered (logged and cached)."""
        section = self.cfg.gemini if name == "gemini" else self.cfg.ollama
        backup = section.overload_fallback.get(request.model)
        try:
            return self._call_with_retry(name, request), request.model
        except (TransientError, QuotaExhaustedError) as exc:
            if not backup or backup == request.model:
                raise
            log.warning(
                "llm.model_overloaded provider=%s model=%s backup=%s error=%s",
                name,
                request.model,
                backup,
                exc,
            )
        return self._call_with_retry(name, replace(request, model=backup)), backup

    def _call_with_retry(self, name: str, request: ProviderRequest) -> ProviderResponse:
        provider = self.providers[name]
        attempts = self.cfg.retry.max_attempts
        for attempt in range(1, attempts + 1):
            self.limiter.acquire(name, request.model)  # may raise QuotaExhaustedError
            try:
                return provider.generate(request)
            except TransientError as exc:
                if attempt == attempts:
                    raise
                hint = exc.retry_after_s if isinstance(exc, RateLimitedError) else None
                delay = self._backoff(attempt, hint)
                if isinstance(exc, RateLimitedError):
                    self.limiter.penalize(name, request.model, delay)
                log.info(
                    "llm.retry provider=%s model=%s attempt=%d delay_s=%.1f error=%s",
                    name,
                    request.model,
                    attempt,
                    delay,
                    exc,
                )
                self._sleep(delay)
        raise AssertionError("unreachable")


def _short_errors(exc: ValidationError, limit: int = 10) -> str:
    lines = [
        f"- {'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['msg']}"
        for err in exc.errors()[:limit]
    ]
    return "\n".join(lines)


def _meta_dict(meta: CallMeta) -> dict[str, Any]:
    return dict(meta.__dict__)


def build_client(
    settings: Settings,
    cache: LLMCache | None,
    provider_factories: dict[str, Callable[[], Provider]] | None = None,
) -> LLMClient:
    """Wire providers from settings. Gemini is skipped when no API key is set."""
    from app.llm.gemini import GeminiProvider
    from app.llm.ollama import OllamaProvider

    providers: dict[str, Provider] = {}
    if provider_factories is not None:
        providers = {name: make() for name, make in provider_factories.items()}
    else:
        if settings.gemini_api_key is not None and settings.gemini_api_key.get_secret_value():
            providers["gemini"] = GeminiProvider(
                settings.gemini_api_key.get_secret_value(), settings.llm.request_timeout_s
            )
        # Only wire Ollama when config actually uses it (primary or fallback).
        if "ollama" in (settings.llm.primary, settings.llm.fallback):
            providers["ollama"] = OllamaProvider(
                settings.llm.ollama.base_url,
                num_ctx=settings.llm.ollama.num_ctx,
                timeout_s=settings.llm.request_timeout_s,
            )
    return LLMClient(settings, providers, cache)


__all__ = ["LLMClient", "build_client", "strip_json_fences"]
