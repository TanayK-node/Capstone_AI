"""Math stage (M10): equations (LaTeX source when available, else the PDF) and a glossary.

1. Equations: from the arXiv source when the paper came with one (math/latex.py), matched
   to the PDF's equation blocks by their printed number, so clicking an equation highlights
   it; otherwise the PDF's equation blocks as text.
2. Glossary: one LLM call over the method / background sections and the equations. Each
   symbol's defining quote is grounded like extraction evidence; a symbol whose quote is not
   in the paper stays, marked "unlocated" (CLAUDE.md rule 5).
3. Python links every symbol to the equations whose LaTeX contains it.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.pipeline.extract.groups import render_block
from app.pipeline.math.latex import equations as latex_equations
from app.pipeline.math.latex import flatten, macros, read_sources
from app.pipeline.verify.grounding import attach_location
from app.schemas.document import ParsedDocument
from app.schemas.extraction import Evidence
from app.schemas.math import Equation, GlossaryOut, MathReport, Symbol

log = logging.getLogger("paperlens.math")
TEXT_ROLES = {"method", "background", "introduction", "experiments", "appendix"}
MAX_TEXT_CHARS = 30_000
MAX_EQUATIONS = 80
MIN_PDF_CHARS = 8


@dataclass
class MathRun:
    report: MathReport
    llm_calls: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    warnings: list[str] = field(default_factory=list)


def _number(label: str | None) -> str | None:
    m = re.search(r"\(?\s*([\w.]+)\s*\)?", label or "")
    return m.group(1) if m else None


def build_equations(
    doc: ParsedDocument, latex_blob: bytes | None
) -> tuple[list[Equation], dict[str, str]]:
    blocks = [b for b in doc.blocks if b.type == "equation"]
    by_number = {n: b for b in blocks if (n := _number(b.label))}
    if latex_blob:
        text = flatten(read_sources(latex_blob))
        found = latex_equations(text) if text else []
        if found:
            eqs: list[Equation] = []
            for i, eq in enumerate(found[:MAX_EQUATIONS], 1):
                first = (eq.number or "").split(",")[0].strip()
                block = by_number.get(first) if first else None
                eqs.append(
                    Equation(
                        id=f"eq{i}",
                        number=f"({eq.number})" if eq.number else None,
                        latex=eq.latex,
                        text=block.text if block else "",
                        block_id=block.id if block else None,
                        page=block.page if block else None,
                        boxes=[b.model_dump() for b in block.boxes] if block else [],
                        source="latex",
                    )
                )
            return eqs, macros(text)
    # GROBID also marks inline fragments ("√ d k") as formulas: an unnumbered block with
    # almost no letters or digits is one of those, not a display equation.
    kept = [b for b in blocks if b.label or len(re.findall(r"\w", b.text)) >= MIN_PDF_CHARS]
    return [
        Equation(
            id=f"eq{i}",
            number=b.label,
            text=_strip_label(b.text, b.label),
            block_id=b.id,
            page=b.page,
            boxes=[x.model_dump() for x in b.boxes],
        )
        for i, b in enumerate(kept[:MAX_EQUATIONS], 1)
    ], {}


def _strip_label(text: str, label: str | None) -> str:
    """GROBID keeps the printed number in the formula text ("...V(1)"); it is shown apart."""
    if label and text.rstrip().endswith(label.strip()):
        return text.rstrip()[: -len(label.strip())].rstrip()
    return text


def glossary_text(doc: ParsedDocument) -> str:
    parts: list[str] = []
    used = 0
    for block in doc.blocks:
        if block.type not in ("paragraph", "equation") or (block.role or "") not in TEXT_ROLES:
            continue
        piece = render_block(block)
        if used + len(piece) > MAX_TEXT_CHARS:
            break
        parts.append(piece)
        used += len(piece) + 2
    return "\n\n".join(parts)


def _symbol_key(symbol: str) -> str:
    return re.sub(r"\s+|[{}]", "", symbol)


def build_report(
    doc: ParsedDocument,
    client: LLMClient | None,
    *,
    latex_blob: bytes | None,
    pdf_path: Path | None,
) -> MathRun:
    eqs, user_macros = build_equations(doc, latex_blob)
    run = MathRun(MathReport(latex_available=bool(latex_blob) and any(e.latex for e in eqs),
                             equations=eqs, macros=user_macros))  # fmt: skip
    if latex_blob and not run.report.latex_available:
        run.warnings.append("the LaTeX source had no readable equations; using the PDF")
    text = glossary_text(doc)
    if client is None:
        run.warnings.append("no LLM available: no glossary")
    elif not text and not eqs:
        run.warnings.append("no method text or equations found")
    else:
        prompt = prompts.render(
            "glossary",
            equations=[{"number": e.number, "body": e.latex or e.text} for e in eqs],
            text=text,
        )
        run.prompt_version = prompt.id
        try:
            result = client.generate_json(prompt, GlossaryOut, role="extraction")
        except LLMError as exc:
            run.warnings.append(f"glossary call failed: {type(exc).__name__}: {exc}")
        else:
            run.llm_calls += 0 if result.meta.cached else 1
            run.provider, run.model = result.meta.provider, result.meta.model
            run.report.symbols = _symbols(result.value, doc, eqs, pdf_path)
    run.report.warnings = run.warnings
    return run


def _symbols(
    out: GlossaryOut, doc: ParsedDocument, eqs: list[Equation], pdf_path: Path | None
) -> list[Symbol]:
    blocks = {b.id: b for b in doc.blocks}
    pages = {b.id: b.page for b in doc.blocks}
    pdf = pymupdf.open(pdf_path) if pdf_path and pdf_path.exists() else None
    symbols: list[Symbol] = []
    seen: set[str] = set()
    try:
        for s in out.symbols:
            key = _symbol_key(s.symbol)
            if not key or key in seen or not s.meaning.strip():
                continue
            seen.add(key)
            evidence: list[Evidence] = []
            if s.quote.strip():
                chunk = s.chunk_id.strip().strip("[]")
                ev = Evidence(chunk_id=chunk, page=pages.get(chunk, 1), quote=s.quote.strip())
                if attach_location(ev, blocks, pdf):
                    ev.grounding_status = "verified"  # the defining sentence is in the paper
                evidence.append(ev)
            used_in = [e.id for e in eqs if key in _symbol_key(e.latex or e.text)]
            symbols.append(Symbol(symbol=s.symbol.strip(), meaning=s.meaning.strip(),
                                  evidence=evidence, equations=used_in))  # fmt: skip
    finally:
        if pdf is not None:
            pdf.close()
    return symbols
