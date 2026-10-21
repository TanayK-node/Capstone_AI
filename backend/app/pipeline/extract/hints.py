"""Rule-based pre-extractors (M4): regex hits handed to the LLM as hints, and code URLs
extracted without the LLM at all. Also the A4 ablation arm ("regex hints + LLM")."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.document import Block

_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")

PATTERNS: dict[str, re.Pattern[str]] = {
    "learning_rate": re.compile(r"learning[\s-]rate|\blr\b", re.I),
    "batch_size": re.compile(r"batch[\s-]size|mini-?batch(es)? of \d", re.I),
    "epochs_steps": re.compile(r"\b\d[\d,.]*\s*[kKM]?\s*(epochs?|steps|iterations|updates)\b"),
    "optimizer": re.compile(r"\b(Adam(W)?|SGD|Adafactor|LAMB|RMSProp|momentum)\b"),
    "hardware": re.compile(
        r"\b(A100|H100|V100|P100|K80|T4|A6000|RTX\s?\d{4}|TPU\s?v?\d|TPUv\d|GPUs?|TPUs?)\b"
    ),
    "compute_time": re.compile(r"\b\d[\d.,]*\s*(GPU[- ]hours?|hours?|days?|core[- ]days)\b", re.I),
    "seeds_runs": re.compile(
        r"random seeds?|\bseeds?\b|averaged over \d+|\d+ (independent )?runs|mean (and|±)", re.I
    ),
    "dropout": re.compile(r"\bdropout\b", re.I),
    "warmup": re.compile(r"\bwarm-?up\b", re.I),
}

URL_RE = re.compile(
    r"https?://(?:www\.)?(github\.com|gitlab\.com|huggingface\.co|bitbucket\.org)/[\w.\-/]+",
    re.I,
)


@dataclass(frozen=True)
class Hint:
    kind: str
    block_id: str
    sentence: str


def sentences_of(block: Block) -> list[str]:
    if block.sentences:
        return [s.text for s in block.sentences if s.text]
    return [s for s in _SENT.split(block.text) if s]


def find_hints(blocks: list[Block], limit_per_kind: int = 6) -> list[Hint]:
    hints: list[Hint] = []
    counts: dict[str, int] = {}
    for block in blocks:
        if block.type not in ("paragraph", "footnote", "table", "caption"):
            continue
        for sentence in sentences_of(block):
            for kind, pattern in PATTERNS.items():
                if counts.get(kind, 0) < limit_per_kind and pattern.search(sentence):
                    hints.append(Hint(kind, block.id, sentence[:300]))
                    counts[kind] = counts.get(kind, 0) + 1
    return hints


def find_code_urls(blocks: list[Block]) -> list[tuple[str, Block, str]]:
    """(normalised url, block, sentence) for repository links anywhere in the paper text."""
    seen: set[str] = set()
    out: list[tuple[str, Block, str]] = []
    for block in blocks:
        if block.type == "reference":
            continue  # links in the bibliography point at other people's code
        # GROBID can split URLs at line breaks: "github.com/ example"
        text = re.sub(r"(https?://\S+)\s+(?=[\w\-]+/)", r"\1", block.text)
        for match in URL_RE.finditer(text):
            url = match.group(0).rstrip(".,;)")
            key = url.lower().removesuffix("/")
            if key in seen:
                continue
            seen.add(key)
            sentence = next(
                (s for s in sentences_of(block) if match.group(1).lower() in s.lower()), block.text
            )
            out.append((url, block, sentence))
    return out
