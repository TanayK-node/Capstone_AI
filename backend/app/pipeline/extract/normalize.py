"""Python-side normalisation of extracted values (CLAUDE.md rule 4: the LLM never does it)."""

from __future__ import annotations

import re

from rapidfuzz import fuzz

from app.pipeline.parse.tables import parse_number

_SUFFIX = {"k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6, "b": 1e9, "B": 1e9}
_SCALED = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([kKmMbB])\s*$")
_TIMES_TEN = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*[×x*]\s*10\s*\^?\s*([-+−]?\d+)\s*$")
# A bare power of ten as PDFs flatten it: "10^-6", "10 -6", "10−6" (= 1e-6).
_POWER_TEN = re.compile(r"^\s*10\s*\^?\s*([-−]\d+)\s*$")


def normalize_value(raw: str) -> float | None:
    """'3e-4' -> 0.0003, '50k' -> 50000, '1M' -> 1e6, '2 × 10^-4' -> 0.0002, '256' -> 256.

    Returns None for anything that is not a single number ('{0.01, 0.03}', 'cosine')."""
    text = raw.strip().replace("−", "-").replace(",", "")
    if m := _SCALED.match(text):
        return float(m.group(1)) * float(_SUFFIX[m.group(2)])
    if m := _TIMES_TEN.match(text):
        return float(m.group(1)) * 10.0 ** int(m.group(2).replace("−", "-"))
    if m := _POWER_TEN.match(text):
        return 10.0 ** int(m.group(1).replace("−", "-"))
    num = parse_number(text)
    return float(num.value) if num else None


def same_item(a: str, b: str, threshold: float = 92.0) -> bool:
    """Do two extracted values name the same thing?

    Same: 'ImageNet-1k' / 'ImageNet 1K' / 'ImageNet', 'Adam optimiser' / 'Adam optimizer'.
    Different: 'WMT 2014 English-German' / 'WMT 2014 English-French'.
    """
    na, nb = _key(a), _key(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    # Different numbers mean different things: CIFAR-10 / CIFAR-100, GPT-2 / GPT-3.
    da, db = re.findall(r"\d+", na), re.findall(r"\d+", nb)
    if da and db and da != db:
        return False
    if fuzz.ratio(na, nb) >= threshold:
        return True
    ta, tb = set(na.split()), set(nb.split())
    small, big = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    # One name contains the other, and the rest is only short tags like "1k", "v2", "big".
    return small < big and all(len(t) <= 3 for t in big - small)


def _key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
