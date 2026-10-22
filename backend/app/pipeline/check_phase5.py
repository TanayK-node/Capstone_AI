"""Phase 5 exit check: chat answers cite pages; a glossary is built for 5 math-heavy papers;
the citation graph has data to render.

    uv run python -m app.pipeline.check_phase5                       # the 5 default papers
    uv run python -m app.pipeline.check_phase5 --pdf-dir ./pdfs      # local PDFs (arXiv ids)
    uv run python -m app.pipeline.check_phase5 --only 2006.11239

Per paper: GROBID parse, section roles, then
- math: equations from the arXiv LaTeX source (downloaded when the name is an arXiv id),
  one Gemini call for the glossary;
- chat: the questions below, hybrid search (keyword search if the embedding model is off),
  one Gemini call each; the off-topic question must be refused without a citation;
- context: Semantic Scholar references / citations, one Gemini call for novelty.
About 6 Gemini calls per paper (no extraction run). Needs GROBID and GEMINI_API_KEY.
Writes report.md to <data_dir>/phase5_check/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.llm.cache import MemoryCache
from app.llm.client import build_client
from app.pipeline.chat.service import answer
from app.pipeline.context.graph import build_report as build_context
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import SourceFetcher
from app.pipeline.math.glossary import build_report as build_math
from app.pipeline.parse import get_parser
from app.pipeline.parse.grobid import GrobidParser
from app.pipeline.retrieval.embedder import get_embedder
from app.pipeline.retrieval.search import PaperIndex, Passage
from app.pipeline.retrieval.store import SKIP_ROLES
from app.pipeline.runner import make_s2
from app.pipeline.structure.sections import structure_document
from app.schemas.chat import ChatAnswer, ChatRequest
from app.schemas.document import ParsedDocument

MATH_HEAVY = [
    "1312.6114",  # VAE
    "1412.6980",  # Adam
    "2006.11239",  # DDPM
    "1706.03762",  # Transformer
    "2106.09685",  # LoRA
]
QUESTIONS = [
    "What problem does the paper address?",
    "What is the main equation or objective the method optimizes?",
    "Which datasets are used in the experiments?",
]
OFF_TOPIC = "What is the capital of France?"
MIN_SYMBOLS = 3
MIN_GROUNDED = 0.5  # share of glossary symbols whose defining sentence was found
MIN_ANSWERED = 2  # of the questions above, per paper
MIN_NODES = 5
_ARXIV = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


def passages(doc: ParsedDocument) -> list[Passage]:
    """The chat passages, straight from the parse (the app reads them from the database)."""
    return [
        Passage(chunk_id=b.id, text=b.text, page=b.page, section=" > ".join(b.section_path[-2:]),
                boxes=[x.model_dump() for x in b.boxes])
        for b in doc.blocks
        if b.type == "paragraph" and (b.role or "") not in SKIP_ROLES and b.text.strip()
    ]  # fmt: skip


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("ids", nargs="*", help="arXiv ids (default: 5 math-heavy papers)")
    ap.add_argument("--pdf-dir", type=Path, help="use local PDFs instead of downloading")
    ap.add_argument("--only", help="only the paper whose id / file name contains this")
    ap.add_argument("--pause", type=float, default=10.0, help="seconds between papers")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    settings = get_settings()
    out_dir = Path(settings.app.data_dir) / "phase5_check"
    pdf_dir = out_dir / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    parser = get_parser(settings, "grobid")
    if isinstance(parser, GrobidParser) and not parser.is_alive():
        print(f"GROBID is not reachable at {settings.grobid_url}; run `docker compose up grobid`")
        return 2
    llm = build_client(settings, MemoryCache())
    if not llm.providers:
        print("No GEMINI_API_KEY in .env: the glossary, chat and novelty need Gemini")
        return 2
    embedder = get_embedder(settings)
    print(f"chat search: {'keyword + embeddings' if embedder else 'keyword only'}")
    fetcher = SourceFetcher(settings)

    if args.pdf_dir:
        papers = [(p.stem, p) for p in sorted(args.pdf_dir.glob("*.pdf"))]
    else:
        papers = [(i, None) for i in (args.ids or MATH_HEAVY)]
    if args.only:
        papers = [p for p in papers if args.only in p[0]]

    rows: list[dict[str, Any]] = []
    md = ["# Phase 5 check: chat, math, context\n"]
    for n, (name, local) in enumerate(papers):
        if n and args.pause:
            time.sleep(args.pause)
        row: dict[str, Any] = {"id": name}
        started = time.monotonic()
        try:
            path = local or pdf_dir / f"{name.replace('/', '_')}.pdf"
            if not path.exists():
                path.write_bytes(fetcher.fetch(resolve(name)).pdf)
            arxiv_id = name if _ARXIV.match(name) else None
            src = pdf_dir / f"{name.replace('/', '_')}.src"
            if arxiv_id and not src.exists():
                src.write_bytes(fetcher.arxiv_source(arxiv_id) or b"")
            latex = src.read_bytes() if src.exists() and src.stat().st_size else None

            doc = parser.parse(path)
            roles = structure_document(doc, llm).block_roles
            for block in doc.blocks:
                block.role = roles.get(block.id)
            title = doc.metadata.title or name

            math = build_math(doc, llm, latex_blob=latex, pdf_path=path).report
            grounded = sum(
                1 for s in math.symbols if any(e.grounding_status == "verified" for e in s.evidence)
            )
            row["math"] = {
                "latex": math.latex_available,
                "equations": len(math.equations),
                "symbols": len(math.symbols),
                "grounded": grounded,
                "ok": len(math.symbols) >= MIN_SYMBOLS
                and grounded >= MIN_GROUNDED * len(math.symbols),
            }

            index = PaperIndex(passages(doc), None)
            if embedder is not None and index.passages:
                index = PaperIndex(
                    index.passages, embedder.embed([p.text[:2000] for p in index.passages])
                )
            replies: list[tuple[str, ChatAnswer]] = [
                (q, answer(ChatRequest(question=q), index, embedder, llm, settings))
                for q in [*QUESTIONS, OFF_TOPIC]
            ]
            answered = [r for q, r in replies[:-1] if r.answered]
            cite_pages = all(r.citations and all(c.page for c in r.citations) for r in answered)
            refused = not replies[-1][1].answered
            row["chat"] = {
                "answered": len(answered),
                "all_cite_pages": cite_pages,
                "off_topic_refused": refused,
                "ok": len(answered) >= MIN_ANSWERED and cite_pages and refused,
            }

            s2 = make_s2(settings)
            try:
                ctx = build_context(doc, {"title": title, "arxiv_id": arxiv_id}, s2=s2,
                                    client=llm, extraction=None, pdf_path=path).report  # fmt: skip
            finally:
                if s2 is not None:
                    s2.close()
            nodes = len(ctx.references) + len(ctx.citations)
            row["context"] = {
                "source": ctx.source,
                "references": len(ctx.references),
                "cited_in_text": sum(1 for r in ctx.references if r.mentions),
                "citations": len(ctx.citations),
                "novelty": bool(ctx.novelty),
                "ok": nodes >= MIN_NODES,
            }
            row["seconds"] = round(time.monotonic() - started, 1)
            md += _markdown(name, title, math, replies, ctx)
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["trace"] = traceback.format_exc(limit=3)
        rows.append(row)
        print(_line(row), flush=True)

    (out_dir / "report.json").write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    (out_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    ok = {k: sum(1 for r in rows if r.get(k, {}).get("ok")) for k in ("math", "chat", "context")}
    total = len(rows)
    print(f"\nglossary built: {ok['math']}/{total}   chat cites pages: {ok['chat']}/{total}   "
          f"graph data: {ok['context']}/{total}   (details: {out_dir / 'report.md'})")  # fmt: skip
    passed = total >= 5 and all(v == total for v in ok.values())
    if total < 5:
        print("(the exit criterion needs 5 papers)")
    print("PHASE 5 EXIT CRITERION:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


def _flag(ok: bool) -> str:
    return "OK  " if ok else "FAIL"


def _line(row: dict[str, Any]) -> str:
    if "error" in row:
        return f"{row['id']:<14} ERROR {row['error']}"
    m, c, x = row["math"], row["chat"], row["context"]
    return (
        f"{row['id']:<14} math {_flag(m['ok'])} {m['symbols']} symbols ({m['grounded']} grounded), "
        f"{m['equations']} eq. {'LaTeX' if m['latex'] else 'PDF'} | chat {_flag(c['ok'])} "
        f"{c['answered']}/{len(QUESTIONS)} answered, off-topic "
        f"{'refused' if c['off_topic_refused'] else 'ANSWERED'} | graph {_flag(x['ok'])} "
        f"{x['references']} refs, {x['citations']} citing ({x['source']}) | {row['seconds']} s"
    )


def _markdown(name: str, title: str, math: Any, replies: Any, ctx: Any) -> list[str]:
    md = [f"## {name}: {title}\n", "### Glossary\n", "| symbol | meaning | grounded | equations |",
          "|---|---|---|---|"]  # fmt: skip
    for s in math.symbols:
        status = s.evidence[0].grounding_status if s.evidence else "no quote"
        md.append(f"| `{s.symbol}` | {s.meaning} | {status} | {len(s.equations)} |")
    md += ["", f"{len(math.equations)} equations ({'LaTeX' if math.latex_available else 'PDF'}). "
           + " ".join(f"⚠ {w}" for w in math.warnings), "", "### Chat\n"]  # fmt: skip
    for q, r in replies:
        pages = ", ".join(f"p. {c.page}" for c in r.citations) or "no citation"
        md += [f"**Q: {q}**", "", f"{r.answer}", "", f"_{pages}_", ""]
    warnings = " ".join(f"⚠ {w}" for w in ctx.warnings)
    md += ["### Citation graph\n", f"Source: {ctx.source}. {warnings}", "", "Key references:"]
    md += [f"- {r.title} ({r.year or '?'}): cited {r.mentions}x in the text"
           for r in ctx.references[:8]]  # fmt: skip
    if ctx.citations:
        md += ["", "Cited by:"] + [f"- {c.title} ({c.year or '?'})" for c in ctx.citations[:5]]
    if ctx.novelty:
        md += ["", f"Novelty: {ctx.novelty.summary}", ""]
        for p in ctx.novelty.positions:
            status = p.evidence[0].grounding_status if p.evidence else "no quote"
            md.append(f"- {p.relation} **{p.title}**: {p.statement} ({status})")
    return [*md, ""]


if __name__ == "__main__":
    raise SystemExit(main())
