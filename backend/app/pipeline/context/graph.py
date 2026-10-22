"""Citation graph and novelty positioning (M12).

1. References: the PDF's own list (GROBID), with how often the text cites each one and the
   citing sentences as evidence. Semantic Scholar, when reachable, adds citation counts,
   "influential" flags, abstracts and references GROBID missed; matched by arXiv id, DOI or
   title.
2. Citing papers: from Semantic Scholar only; influential first, then by citation count.
3. Novelty: one LLM call over the abstracts of the references the paper cites most, with the
   paper's own paragraphs that cite them. Each position's quote must come from the paper and
   is grounded like extraction evidence; unfound quotes stay, marked "unlocated".
Without Semantic Scholar there are no citing papers and no novelty summary (no abstracts),
but the reference graph still renders.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pymupdf
from rapidfuzz import fuzz

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.pipeline.context.s2 import S2Client, S2Error
from app.pipeline.extract.groups import render_block
from app.pipeline.verify.grounding import attach_location
from app.schemas.context import ContextReport, GraphNode, Novelty, NoveltyOut, NoveltyPosition
from app.schemas.document import Block, ParsedDocument, Reference, union_box
from app.schemas.extraction import Evidence, PaperExtraction

log = logging.getLogger("paperlens.context")
TITLE_MATCH = 90  # rapidfuzz ratio of normalised titles
MAX_EVIDENCE = 3  # citing sentences kept per reference
MAX_TEXT_CHARS = 20_000
MAX_ABSTRACT_CHARS = 1_200


@dataclass
class ContextRun:
    report: ContextReport
    llm_calls: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class _Ref:
    """A reference while it is being merged: the PDF's entry and / or the S2 record."""

    local: Reference | None = None
    s2: dict[str, Any] | None = None
    influential: bool = False
    citing: list[tuple[Block, int]] = field(default_factory=list)  # (block, sentence index)

    @property
    def mentions(self) -> int:
        return len(self.citing)

    @property
    def citation_count(self) -> int:
        return int((self.s2 or {}).get("citationCount") or 0)


def norm_title(title: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def _authors(data: dict[str, Any]) -> list[str]:
    return [a.get("name", "") for a in (data.get("authors") or [])[:3] if a.get("name")]


def _year(value: Any) -> int | None:
    try:
        return int(str(value)[:4])
    except (TypeError, ValueError):
        return None


def _local_url(ref: Reference) -> str | None:
    if ref.arxiv_id:
        return f"https://arxiv.org/abs/{ref.arxiv_id}"
    if ref.doi:
        return f"https://doi.org/{ref.doi}"
    return None


def _citing_sentences(doc: ParsedDocument) -> dict[str, list[tuple[Block, int]]]:
    out: dict[str, list[tuple[Block, int]]] = {}
    for block in doc.blocks:
        for i, sent in enumerate(block.sentences):
            for rid in sent.cites:
                out.setdefault(rid, []).append((block, i))
    return out


def _evidence(block: Block, index: int) -> Evidence:
    sent = block.sentences[index]
    return Evidence(chunk_id=block.id, page=sent.boxes[0].page if sent.boxes else block.page,
                    bbox=union_box(sent.boxes), boxes=sent.boxes, quote=sent.text,
                    grounding_status="verified", match_score=100.0)  # fmt: skip


def merge_references(doc: ParsedDocument, s2_refs: list[dict[str, Any]]) -> list[_Ref]:
    """The PDF's references, each matched to at most one S2 reference; then the S2 ones
    GROBID did not list."""
    citing = _citing_sentences(doc)
    refs = [_Ref(local=r, citing=citing.get(r.id, [])) for r in doc.references]
    by_arxiv = {r.local.arxiv_id.split("v")[0]: r for r in refs if r.local and r.local.arxiv_id}
    by_doi = {r.local.doi.lower(): r for r in refs if r.local and r.local.doi}
    titles = [(norm_title(r.local.title), r) for r in refs if r.local and r.local.title]
    extra: list[_Ref] = []
    for entry in s2_refs:
        paper = entry["citedPaper"]
        ext = paper.get("externalIds") or {}
        match = by_arxiv.get(str(ext.get("ArXiv") or "")) or by_doi.get(
            str(ext.get("DOI") or "").lower()
        )
        if match is None:
            title = norm_title(paper.get("title"))
            best = max(titles, key=lambda t: fuzz.ratio(t[0], title), default=None)
            if best and fuzz.ratio(best[0], title) >= TITLE_MATCH:
                match = best[1]
        if match is not None and match.s2 is None:
            match.s2, match.influential = paper, bool(entry.get("isInfluential"))
        elif match is None:
            extra.append(_Ref(s2=paper, influential=bool(entry.get("isInfluential"))))
    return refs + extra


def _ref_node(ref: _Ref) -> GraphNode:
    s2, local = ref.s2 or {}, ref.local
    title = s2.get("title") or (local.title if local else None) or (local.text if local else "")
    return GraphNode(
        id=f"ref:{local.id}" if local else f"s2:{s2.get('paperId')}",
        kind="reference",
        title=title[:300],
        year=_year(s2.get("year") or (local.year if local else None)),
        venue=s2.get("venue") or None,
        authors=_authors(s2),
        citation_count=s2.get("citationCount") if s2 else None,
        influential=ref.influential,
        mentions=ref.mentions,
        ref_id=local.id if local else None,
        url=s2.get("url") or (_local_url(local) if local else None),
        evidence=[_evidence(b, i) for b, i in ref.citing[:MAX_EVIDENCE]],
    )


def _citation_node(entry: dict[str, Any]) -> GraphNode:
    p = entry["citingPaper"]
    return GraphNode(id=f"s2:{p.get('paperId')}", kind="citation", title=p["title"][:300],
                     year=_year(p.get("year")), venue=p.get("venue") or None,
                     authors=_authors(p), citation_count=p.get("citationCount"),
                     influential=bool(entry.get("isInfluential")), url=p.get("url"))  # fmt: skip


def build_report(
    doc: ParsedDocument,
    meta: dict[str, Any],
    *,
    s2: S2Client | None,
    client: LLMClient | None,
    extraction: PaperExtraction | None,
    pdf_path: Path | None,
    top_references: int = 20,
    top_citations: int = 20,
    novelty_references: int = 10,
    citations_fetched: int = 1000,
) -> ContextRun:
    warnings: list[str] = []
    title = meta.get("title") or doc.metadata.title or "This paper"
    found: dict[str, Any] | None = None
    s2_refs: list[dict[str, Any]] = []
    s2_cites: list[dict[str, Any]] = []
    if s2 is None:
        warnings.append("Semantic Scholar is off: references from the PDF only, no citing papers")
    else:
        try:
            found = s2.find(arxiv_id=meta.get("arxiv_id"), doi=meta.get("doi"),
                            s2_id=meta.get("s2_id"), title=title)  # fmt: skip
            if found is None:
                warnings.append("paper not found on Semantic Scholar: references from the PDF only")
            else:
                s2_refs = s2.references(found["paperId"])
                s2_cites = s2.citations(found["paperId"], citations_fetched)
        except S2Error as exc:
            warnings.append(f"{exc}: references from the PDF only")

    refs = merge_references(doc, s2_refs)
    if not any(r.mentions for r in refs) and doc.references:
        warnings.append("no in-text citations in this parse (re-run the parse to count them)")
    ranked = sorted(refs, key=lambda r: (r.mentions, r.influential, r.citation_count),
                    reverse=True)  # fmt: skip
    cites = sorted(s2_cites, key=lambda c: (bool(c.get("isInfluential")),
                                            c["citingPaper"].get("citationCount") or 0),
                   reverse=True)  # fmt: skip
    paper = GraphNode(
        id="paper",
        kind="paper",
        title=(found or {}).get("title") or title,
        year=_year((found or {}).get("year") or meta.get("year")),
        venue=(found or {}).get("venue") or meta.get("venue"),
        authors=_authors(found) if found else [a.name for a in doc.metadata.authors[:3]],
        citation_count=(found or {}).get("citationCount"),
        url=(found or {}).get("url"),
    )
    report = ContextReport(
        source="semantic_scholar" if found else "pdf",
        paper=paper,
        references=[_ref_node(r) for r in ranked[:top_references]],
        citations=[_citation_node(c) for c in cites[:top_citations]],
        reference_count=max(len(refs), int((found or {}).get("referenceCount") or 0)),
        citation_count=(found or {}).get("citationCount"),
        influential_citation_count=(found or {}).get("influentialCitationCount"),
    )
    run = ContextRun(report, warnings=warnings)

    # Novelty: the references this paper cites most that have an abstract (S2).
    chosen = [r for r in ranked if r.s2 and r.s2.get("abstract")][:novelty_references]
    if not chosen:
        warnings.append("no reference abstracts (Semantic Scholar): no novelty summary")
    elif client is None:
        warnings.append("no LLM available: no novelty summary")
    else:
        _novelty(run, doc, meta, chosen, client, extraction, pdf_path)
    report.warnings = warnings
    return run


def _novelty(
    run: ContextRun,
    doc: ParsedDocument,
    meta: dict[str, Any],
    chosen: list[_Ref],
    client: LLMClient,
    extraction: PaperExtraction | None,
    pdf_path: Path | None,
) -> None:
    markers = {f"R{i}": r for i, r in enumerate(chosen, 1)}
    parts: list[str] = []
    used = 0
    seen: set[str] = set()
    for ref in chosen:
        for block, _ in ref.citing:
            if block.id in seen:
                continue
            piece = render_block(block)
            if used + len(piece) > MAX_TEXT_CHARS:
                break
            seen.add(block.id)
            parts.append(piece)
            used += len(piece) + 2
    contributions = [i.value for i in (extraction.contributions if extraction else [])]
    contributions += [i.value for i in (extraction.novelty if extraction else [])]
    abstract = (
        meta.get("abstract")
        or doc.metadata.abstract
        or " ".join(b.text for b in doc.blocks if b.role == "abstract" and b.type == "paragraph")
    )
    prompt = prompts.render(
        "novelty",
        title=run.report.paper.title,
        abstract=abstract[:3000],
        contributions=contributions[:12],
        references=[
            {
                "marker": m,
                "title": (r.s2 or {}).get("title"),
                "year": (r.s2 or {}).get("year"),
                "abstract": str((r.s2 or {}).get("abstract"))[:MAX_ABSTRACT_CHARS],
            }
            for m, r in markers.items()
        ],
        text="\n\n".join(parts) or "(the paper's text cites none of them directly)",
    )
    run.prompt_version = prompt.id
    try:
        result = client.generate_json(prompt, NoveltyOut, role="extraction")
    except LLMError as exc:
        run.warnings.append(f"novelty call failed: {type(exc).__name__}: {exc}")
        return
    run.llm_calls += 0 if result.meta.cached else 1
    run.provider, run.model = result.meta.provider, result.meta.model
    out = result.value

    blocks = {b.id: b for b in doc.blocks}
    pages = {b.id: b.page for b in doc.blocks}
    nodes = {n.ref_id: n for n in run.report.references if n.ref_id}
    positions: list[NoveltyPosition] = []
    invented = 0
    pdf = pymupdf.open(pdf_path) if pdf_path and pdf_path.exists() else None
    try:
        for pos in out.positions:
            target = markers.get(pos.ref.strip().strip("[]"))
            if target is None:
                invented += 1  # a marker that names no reference: nothing to check it against
                continue
            node = _ref_node(target)
            node = nodes.get(node.ref_id or "", node)
            evidence: list[Evidence] = []
            if pos.quote.strip():
                chunk = pos.chunk_id.strip().strip("[]")
                ev = Evidence(chunk_id=chunk, page=pages.get(chunk, 1), quote=pos.quote.strip())
                if attach_location(ev, blocks, pdf):
                    ev.grounding_status = "verified"  # the sentence is in the paper
                evidence.append(ev)
            positions.append(NoveltyPosition(node=node.id, title=node.title,
                                             relation=pos.relation,
                                             statement=pos.statement.strip(),
                                             evidence=evidence))  # fmt: skip
    finally:
        if pdf is not None:
            pdf.close()
    if invented:
        run.warnings.append(f"{invented} position(s) named an unknown reference and were dropped")
    run.report.novelty = Novelty(summary=out.summary.strip(), positions=positions)
