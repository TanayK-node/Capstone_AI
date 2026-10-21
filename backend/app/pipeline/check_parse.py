"""Phase 1 exit check: 10 arXiv papers parse without errors; tables detected on >= 8.

    uv run python -m app.pipeline.check_parse                 # default 10 papers, GROBID
    uv run python -m app.pipeline.check_parse 1706.03762 ...  # your own arXiv ids
    uv run python -m app.pipeline.check_parse --parser pymupdf  # ablation A1 arm
    uv run python -m app.pipeline.check_parse --pdf-dir ./pdfs  # local PDFs, no download

Needs GROBID (`docker compose up grobid`) unless --parser pymupdf. Writes report.json and
report.md (every reconstructed table, for eyeballing) to <data_dir>/phase1_check/.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.pipeline.ingest.resolver import resolve
from app.pipeline.ingest.sources import SourceFetcher
from app.pipeline.ingest.validate import validate_pdf
from app.pipeline.parse import get_parser
from app.pipeline.parse.grobid import GrobidParser
from app.pipeline.structure.sections import structure_document
from app.schemas.document import ParsedDocument

# Mixed NLP / CV / ML papers, all with results tables.
DEFAULT_IDS = [
    "1706.03762",  # Transformer
    "1810.04805",  # BERT
    "1512.03385",  # ResNet
    "2010.11929",  # ViT
    "1907.11692",  # RoBERTa
    "2106.09685",  # LoRA
    "1409.0473",  # Bahdanau attention
    "1409.1556",  # VGG
    "2002.05709",  # SimCLR
    "1910.01108",  # DistilBERT
]


def summarize(doc: ParsedDocument, seconds: float) -> dict[str, Any]:
    structure = structure_document(doc, client=None)
    grids = [t for t in doc.tables if t.table and t.table.n_cols >= 2 and t.table.n_rows >= 2]
    return {
        "parser": doc.parser,
        "pages": len(doc.pages),
        "blocks": len(doc.blocks),
        "headings": sum(1 for b in doc.blocks if b.type == "heading"),
        "sections": len(structure.sections),
        "unknown_roles": sum(1 for s in structure.sections if s.role == "other"),
        "tables": len(doc.tables),
        "tables_with_grid": len(grids),
        "references": len(doc.references),
        "title": doc.metadata.title,
        "seconds": round(seconds, 1),
        "warnings": doc.warnings,
    }


def table_markdown(doc: ParsedDocument) -> list[str]:
    out: list[str] = []
    for t in doc.tables:
        out.append(f"#### {t.label or t.id} (page {t.page})\n\n{t.text[:200]}\n")
        if not t.table or not t.table.n_rows:
            out.append("_no grid_\n")
            continue
        grid = t.table.grid()
        out.append("| " + " | ".join(c.replace("|", "/") or " " for c in grid[0]) + " |")
        out.append("|" + "---|" * len(grid[0]))
        for row in grid[1:]:
            out.append("| " + " | ".join(c.replace("|", "/") or " " for c in row) + " |")
        out.append("")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("ids", nargs="*", help="arXiv ids (default: 10 well-known papers)")
    ap.add_argument("--parser", choices=["grobid", "pymupdf", "auto"], default="grobid")
    ap.add_argument("--pdf-dir", type=Path, help="parse local PDFs instead of downloading")
    args = ap.parse_args()
    # A cp1252 Windows console must not crash on a non-Latin character in an error message.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    settings = get_settings()
    out_dir = Path(settings.app.data_dir) / "phase1_check"
    pdf_dir = out_dir / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    parser = get_parser(settings, args.parser)
    if isinstance(parser, GrobidParser) and not parser.is_alive():
        print(f"GROBID is not reachable at {settings.grobid_url}; run `docker compose up grobid`")
        return 2

    if args.pdf_dir:
        items = [(p.stem, p) for p in sorted(args.pdf_dir.glob("*.pdf"))]
    else:
        items = [(i, None) for i in (args.ids or DEFAULT_IDS)]
    fetcher = SourceFetcher(settings)
    results: list[dict[str, Any]] = []
    md: list[str] = [f"# Phase 1 parse check ({args.parser})\n"]

    for n, (name, local) in enumerate(items):
        row: dict[str, Any] = {"id": name}
        try:
            if local is None:
                path = pdf_dir / f"{name.replace('/', '_')}.pdf"
                if not path.exists():
                    if n:
                        time.sleep(3)  # arXiv asks for at most one request every 3 s
                    fetched = fetcher.fetch(resolve(name))
                    path.write_bytes(fetched.pdf)
            else:
                path = local
            validate_pdf(path.read_bytes(), settings.ingest)
            started = time.monotonic()
            doc = parser.parse(path)
            row |= {"ok": True, **summarize(doc, time.monotonic() - started)}
            md += [f"## {name}: {doc.metadata.title}\n", *table_markdown(doc)]
        except Exception as exc:
            row |= {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            row["trace"] = traceback.format_exc(limit=3)
        results.append(row)
        status = (
            f"{row['pages']:>3}p {row['blocks']:>4} blocks {row['headings']:>3} heads "
            f"{row['tables']:>2} tables ({row['tables_with_grid']} grids) "
            f"{row['references']:>3} refs {row['seconds']:>5}s"
            if row["ok"]
            else f"ERROR {row['error']}"
        )
        print(f"{name:<14} {status}", flush=True)

    ok = [r for r in results if r["ok"]]
    with_tables = [r for r in ok if r["tables_with_grid"] > 0]
    total = len(results)
    print(
        f"\nparsed without errors: {len(ok)}/{total}   "
        f"tables detected (with a grid): {len(with_tables)}/{total}"
    )
    # Explicit UTF-8: Windows defaults to cp1252, which can't encode symbols in table cells.
    (out_dir / "report.json").write_text(
        json.dumps(results, indent=2, default=str, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"report: {out_dir / 'report.md'}")
    passed = len(ok) == total and len(with_tables) >= 0.8 * total
    print("PHASE 1 EXIT CRITERION:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
