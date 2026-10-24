"""Ablations that need no LLM calls (SCOPE.md section 8, "Ablations").

A3 grounding: the same extraction scored under stricter evidence policies, keeping only items
   whose quote was found in the paper, then only items the verifier also accepted. (The full
   A3, extracting without asking for quotes at all, needs new LLM runs: pending.)
A1 parser: GROBID vs PyMuPDF-only on the gold papers: what each parse keeps (sections,
   tables with a grid, references, equations) and the share of gold items whose value can
   still be found in the parsed text, an upper bound on what extraction can recall.
A6 retrieval for chat: keyword (BM25) vs dense vs hybrid, scored on questions built from the
   gold set: does the top-k contain the passage with the answer? Dense and hybrid need the
   local embedding model (downloaded once); without it only BM25 is reported.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from app.eval.data import GoldItem, PredItem
from app.eval.extraction import CORE_FIELDS, ExtractionReport, evaluate
from app.eval.match import norm, numbers
from app.pipeline.retrieval.embedder import Embedder
from app.pipeline.retrieval.search import PaperIndex, Passage
from app.pipeline.retrieval.store import SKIP_ROLES
from app.pipeline.structure.sections import structure_document
from app.schemas.document import Block, ParsedDocument

# ------------------------------------------------------------------ A3 grounding policies

LOCATED = {"verified", "partial", "unsupported"}
POLICIES: dict[str, Callable[[PredItem], bool]] = {
    "no evidence requirement (keep all)": lambda p: True,
    "quote found in the paper": lambda p: p.status in LOCATED,
    "quote found + verifier: supports or partly": lambda p: p.status in {"verified", "partial"},
    "quote found + verifier: supports": lambda p: p.status == "verified",
}


def a3(gold: list[GoldItem], preds: list[PredItem]) -> dict[str, ExtractionReport]:
    return {name: evaluate(gold, [p for p in preds if keep(p)]) for name, keep in POLICIES.items()}


def core_scores(rep: ExtractionReport) -> tuple[float | None, float | None, float | None]:
    """Micro precision / recall / F1 over the core fields together."""
    pred = sum(rep.total(f).pred for f in CORE_FIELDS)
    right = sum(rep.total(f).pred_correct for f in CORE_FIELDS)
    gold = sum(rep.total(f).gold for f in CORE_FIELDS)
    found = sum(rep.total(f).gold_found for f in CORE_FIELDS)
    p = right / pred if pred else None
    r = found / gold if gold else None
    f1 = 2 * p * r / (p + r) if p is not None and r is not None and p + r else None
    return p, r, f1


# ------------------------------------------------------------------ A1 parser


@dataclass
class ParseStats:
    parser: str
    papers: int = 0
    seconds: float = 0.0
    sections: int = 0
    paragraphs: int = 0
    tables: int = 0
    tables_with_grid: int = 0
    references: int = 0
    equations: int = 0
    gold: int = 0
    gold_in_text: int = 0
    by_field: dict[str, list[int]] = field(default_factory=dict)  # field -> [found, total]


def _found_in(doc_blocks: list[str], g: GoldItem) -> bool:
    """Is a gold item's value still in the parsed text (blocks as parsed, not normalised)?
    Hyperparameters: a block that names the hyperparameter and contains the value."""
    normed = [f" {norm(t)} " for t in doc_blocks]
    if g.field == "hyperparameters":
        want = numbers(g.value)
        names = [norm(n) for n in [g.name.replace("_", " "), *g.aliases] if norm(n)]
        for raw, text in zip(doc_blocks, normed, strict=True):
            if want and not set(want) & set(numbers(raw)):
                continue
            if not want and f" {norm(g.value)} " not in text:
                continue
            if any(f" {n} " in text for n in names):
                return True
        return False
    variants = [norm(v) for v in g.names if len(norm(v)) >= 2]
    return any(f" {v} " in text for text in normed for v in variants)


def _block_text(b: Block) -> str:
    """A block's text plus its table cells (a grid may hold values its caption does not)."""
    rows = b.table.grid() if b.table else []
    return " ".join([b.text, *(" ".join(r) for r in rows)])


def parse_stats(name: str, docs: dict[str, tuple[ParsedDocument, float]],
                gold: list[GoldItem]) -> ParseStats:  # fmt: skip
    st = ParseStats(name)
    for pid, (doc, secs) in docs.items():
        st.papers += 1
        st.seconds += secs
        blocks = doc.blocks
        st.sections += sum(1 for b in blocks if b.type == "heading")
        st.paragraphs += sum(1 for b in blocks if b.type == "paragraph")
        st.tables += sum(1 for b in blocks if b.type == "table")
        st.tables_with_grid += sum(1 for b in blocks if b.type == "table" and b.table
                                   and b.table.n_rows > 1)  # fmt: skip
        st.references += len(doc.references)
        st.equations += sum(1 for b in blocks if b.type == "equation")
        texts = [_block_text(b) for b in blocks]
        for g in (g for g in gold if g.paper_id == pid and g.field != "code_urls"):
            found = _found_in(texts, g)
            st.gold += 1
            st.gold_in_text += found
            cell = st.by_field.setdefault(g.field, [0, 0])
            cell[0] += found
            cell[1] += 1
    return st


def parse_all(parse: Callable[[Path], ParsedDocument], pdfs: dict[str, Path],
              log: Callable[[str], None] | None = None,
              ) -> dict[str, tuple[ParsedDocument, float]]:  # fmt: skip
    """Parses every PDF; one that fails is left out (and logged) instead of ending the run."""
    out: dict[str, tuple[ParsedDocument, float]] = {}
    for n, (pid, path) in enumerate(pdfs.items(), 1):
        t = time.perf_counter()
        try:
            doc = parse(path)
        except Exception as e:  # one bad PDF must not lose a long run
            if log:
                log(f"  [{n}/{len(pdfs)}] {pid}: failed ({type(e).__name__}: {e}), skipped")
            continue
        out[pid] = (doc, time.perf_counter() - t)
        if log:
            log(f"  [{n}/{len(pdfs)}] {pid}: {out[pid][1]:.1f} s")
    return out


# ------------------------------------------------------------------ A6 retrieval

QUESTIONS = {
    "task": "What task or problem does the paper address?",
    "datasets": "Which datasets are used in the experiments?",
    "baselines": "Which baselines or prior methods are compared against?",
    "metrics": "Which evaluation metrics are reported?",
}
K = 5


def passages(doc: ParsedDocument) -> list[Passage]:
    roles = structure_document(doc, None).block_roles
    return [
        Passage(chunk_id=b.id, text=b.text, page=b.page, section=" > ".join(b.section_path[-2:]),
                role=roles.get(b.id))
        for b in doc.blocks
        if b.type in ("paragraph", "table") and (roles.get(b.id) or "") not in SKIP_ROLES
        and b.text.strip()
    ]  # fmt: skip


def _rank(index: PaperIndex, q: str, mode: str, embedder: Embedder | None) -> list[Passage]:
    if mode == "bm25":
        return [h.passage for h in index.search(q, None, k=K)]
    if mode == "hybrid":
        return [h.passage for h in index.search(q, embedder, k=K, min_cosine=-1.0)]
    assert embedder is not None and index.vectors is not None
    cos = index.vectors @ embedder.embed([q], query=True)[0]
    return [index.passages[int(i)] for i in np.argsort(-cos)[:K]]


@dataclass
class RetrievalScore:
    mode: str
    items: int = 0
    hits: int = 0
    by_field: dict[str, list[int]] = field(default_factory=dict)

    @property
    def recall(self) -> float | None:
        return self.hits / self.items if self.items else None


def retrieval(docs: dict[str, ParsedDocument], gold: list[GoldItem],
              embedder: Embedder | None,
              log: Callable[[str], None] | None = None) -> list[RetrievalScore]:  # fmt: skip
    """Recall@5 of gold items: field questions ("Which datasets...") for entity fields, one
    question per hyperparameter ("What learning rate is used?")."""
    modes = ["bm25"] + (["dense", "hybrid"] if embedder is not None else [])
    scores = {m: RetrievalScore(m) for m in modes}
    for n, (pid, doc) in enumerate(docs.items(), 1):
        if log:
            log(f"  [{n}/{len(docs)}] {pid}")
        ps = passages(doc)
        vectors = (
            embedder.embed([p.text[:2000] for p in ps]) if embedder is not None and ps else None
        )
        index = PaperIndex(ps, vectors)
        golds = [g for g in gold if g.paper_id == pid]
        asks: list[tuple[str, list[GoldItem]]] = [
            (q, [g for g in golds if g.field == f]) for f, q in QUESTIONS.items()
        ]
        seen: set[str] = set()
        for g in (g for g in golds if g.field == "hyperparameters"):
            if g.name not in seen:  # one question per hyperparameter name
                seen.add(g.name)
                same = [x for x in golds if x.field == "hyperparameters" and x.name == g.name]
                asks.append((f"What {g.name.replace('_', ' ')} is used?", same))
        for mode in modes:
            for q, items in asks:
                if not items:
                    continue
                texts = [p.text for p in _rank(index, q, mode, embedder)]
                if items[0].field == "hyperparameters":
                    hit = [any(_found_in(texts, x) for x in items)]  # any stated value counts
                else:
                    hit = [_found_in(texts, x) for x in items]
                s = scores[mode]
                s.items += len(hit)
                s.hits += sum(hit)
                cell = s.by_field.setdefault(items[0].field, [0, 0])
                cell[0] += sum(hit)
                cell[1] += len(hit)
    return list(scores.values())
