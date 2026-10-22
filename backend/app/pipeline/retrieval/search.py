"""Hybrid search (M11): BM25 and embedding similarity, fused by reciprocal rank.

BM25 catches exact terms (names, numbers, "learning rate"); embeddings catch paraphrases
("how long did they train" ~ "training took 3.5 days"). Reciprocal rank fusion needs no score
calibration between the two. A question that matches nothing (no BM25 term overlap and low
cosine similarity) returns no passages, so chat can refuse instead of guessing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]

from app.pipeline.retrieval.embedder import Embedder

RRF_K = 60
_TOKEN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*")
_STOP = {
    "the", "a", "an", "of", "in", "on", "for", "to", "and", "or", "is", "are", "was", "were",
    "what", "which", "how", "do", "does", "did", "they", "their", "this", "that", "with",
    "by", "be", "it", "as", "at", "from", "paper", "authors", "use", "used",
}  # fmt: skip


def _stem(t: str) -> str:
    """Light suffix stripping (like Porter's first step), so "problem" finds "problems" and
    "optimizes" / "optimized" / "optimizing" meet. Numbers and short tokens are left alone."""
    if len(t) <= 4 or not t.isalpha():
        return t
    if t.endswith("sses"):
        t = t[:-2]
    elif t.endswith("ies"):
        t = t[:-3] + "y"
    elif t.endswith("s") and not t.endswith(("ss", "us", "is")):
        t = t[:-1]
    elif t.endswith("ing") and len(t) >= 6:
        t = t[:-3]
    elif t.endswith("ed") and len(t) >= 5:
        t = t[:-2]
    return t[:-1] if t.endswith("e") and len(t) > 4 else t


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in _TOKEN.findall(text.lower()) if t not in _STOP]


@dataclass
class Passage:
    chunk_id: str
    text: str
    page: int
    section: str
    boxes: list[dict[str, float]] = field(default_factory=list)


@dataclass
class Hit:
    passage: Passage
    score: float  # fused RRF score
    bm25: float
    cosine: float | None


class PaperIndex:
    """Search structures for one paper. Built per request (a paper has ~100-1000 passages)."""

    def __init__(self, passages: list[Passage], vectors: np.ndarray | None) -> None:
        self.passages = passages
        self.vectors = vectors if vectors is not None and len(vectors) == len(passages) else None
        corpus = [tokenize(p.text) or ["_"] for p in passages]
        self.bm25 = BM25Okapi(corpus) if passages else None

    def search(
        self,
        question: str,
        embedder: Embedder | None,
        *,
        k: int = 5,
        candidates: int = 20,
        min_cosine: float = 0.45,
    ) -> list[Hit]:
        if not self.passages or self.bm25 is None:
            return []
        terms = tokenize(question)
        n = len(self.passages)
        bm25 = (
            np.asarray(self.bm25.get_scores(terms), dtype=np.float32)
            if terms
            else np.zeros(n, dtype=np.float32)
        )
        cos: np.ndarray | None = None
        if embedder is not None and self.vectors is not None:
            cos = self.vectors @ embedder.embed([question], query=True)[0]
        # Nothing relevant: no shared term and no passage close in meaning.
        if float(bm25.max(initial=0.0)) <= 0.0 and (cos is None or float(cos.max()) < min_cosine):
            return []

        rankings: list[list[int]] = [
            [int(i) for i in np.argsort(-bm25)[:candidates] if bm25[i] > 0]
        ]
        if cos is not None:
            rankings.append([int(i) for i in np.argsort(-cos)[:candidates]])
        fused: dict[int, float] = {}
        for ranking in rankings:
            for rank, idx in enumerate(ranking):
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (RRF_K + rank + 1)
        best = sorted(fused, key=lambda i: fused[i], reverse=True)[:k]
        return [
            Hit(
                self.passages[i],
                fused[i],
                float(bm25[i]),
                float(cos[i]) if cos is not None else None,
            )
            for i in best
        ]
