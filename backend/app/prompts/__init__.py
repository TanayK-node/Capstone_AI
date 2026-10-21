"""Versioned Jinja prompt templates (CLAUDE.md rule 7).

Each template starts with a version comment, e.g. `{# version: 3 #}`. Bump it on any
change; the version is part of the LLM cache key and is logged with every call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

PROMPTS_DIR = Path(__file__).parent
_VERSION_RE = re.compile(r"\{#\s*version:\s*([\w.\-]+)\s*#\}")


@dataclass(frozen=True)
class RenderedPrompt:
    name: str
    version: str
    text: str

    @property
    def id(self) -> str:
        return f"{self.name}@{self.version}"


@lru_cache
def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(PROMPTS_DIR),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,  # plain-text prompts, not HTML
    )


def prompt_version(name: str) -> str:
    source = (PROMPTS_DIR / f"{name}.jinja").read_text()
    match = _VERSION_RE.search(source)
    if match is None:
        raise ValueError(f"prompt {name!r} has no '{{# version: N #}}' header")
    return match.group(1)


def render(name: str, **variables: Any) -> RenderedPrompt:
    text = _env().get_template(f"{name}.jinja").render(**variables).strip()
    return RenderedPrompt(name=name, version=prompt_version(name), text=text)
