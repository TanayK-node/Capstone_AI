"""Smoke-check both providers with the toy schema.

uv run python -m app.llm.check               # call each configured provider once
uv run python -m app.llm.check --list-models # show models each provider offers
"""

from __future__ import annotations

import argparse
import sys

from app import prompts
from app.config import get_settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient, build_client
from app.schemas.toy import TOY_TEXT, ToyExtraction


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-models", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    base = build_client(settings, MemoryCache())
    if not base.providers:
        print("no providers configured")
        return 1

    failed = False
    for name, provider in base.providers.items():
        if args.list_models:
            try:
                print(f"{name}: {', '.join(provider.list_models()) or '(none)'}")
            except Exception as exc:
                print(f"{name}: ERROR {exc}")
                failed = True
            continue
        # One client per provider with fallback disabled, so each is tested on its own.
        solo_settings = settings.model_copy(
            update={"llm": settings.llm.model_copy(update={"primary": name, "fallback": None})}
        )
        client = LLMClient(solo_settings, {name: provider}, MemoryCache())
        try:
            result = client.generate_json(
                prompts.render("toy_extract", text=TOY_TEXT), ToyExtraction, role="small"
            )
        except Exception as exc:
            print(f"{name}: FAIL {type(exc).__name__}: {exc}")
            failed = True
            continue
        m = result.meta
        print(f"{name}: OK model={m.model} latency={m.latency_s}s -> {result.value}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
