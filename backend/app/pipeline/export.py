"""Exports of a paper's extraction (SCOPE.md §7): JSON, Markdown, BibTeX and CSV.

Pure functions over PaperExtraction, so the API and scripts render the same output.
Every exported item keeps its evidence (page + quote + grounding status): CLAUDE.md rule 5.
"""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata

from app.schemas.extraction import Dataset, Hyperparameter, Item, PaperExtraction

FORMATS = {
    "json": ("application/json", "json"),
    "md": ("text/markdown; charset=utf-8", "md"),
    "bib": ("application/x-bibtex; charset=utf-8", "bib"),
    "csv": ("text/csv; charset=utf-8", "csv"),
}

# Field order and headings shared by the Markdown export and the Overview tab.
SECTIONS: list[tuple[str, str]] = [
    ("problem", "Problem"),
    ("task", "Task"),
    ("contributions", "Contributions"),
    ("method_summary", "Method"),
    ("novelty", "Novelty"),
    ("datasets", "Datasets"),
    ("baselines", "Baselines"),
    ("metrics", "Metrics"),
    ("hyperparameters", "Hyperparameters"),
    ("compute", "Compute"),
    ("seeds_and_runs", "Seeds and runs"),
    ("ablations", "Ablations"),
    ("claims", "Claims"),
    ("limitations", "Limitations"),
    ("future_work", "Future work"),
    ("ethics", "Ethics"),
    ("code_urls", "Code"),
]


def render(extraction: PaperExtraction, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(extraction.model_dump(mode="json"), indent=2, ensure_ascii=False)
    if fmt == "md":
        return to_markdown(extraction)
    if fmt == "bib":
        return to_bibtex(extraction)
    if fmt == "csv":
        return to_csv(extraction)
    raise ValueError(f"unknown export format {fmt!r}")


def item_label(item: Item) -> str:
    if isinstance(item, Hyperparameter):
        scope = f" ({item.scope})" if item.scope else ""
        return f"{item.name}{scope}: {item.value_raw or item.value}"
    if isinstance(item, Dataset):
        extra = ", ".join(x for x in (item.split, item.size) if x)
        return f"{item.name} ({extra})" if extra else item.name
    return item.value


def _status(item: Item) -> str:
    statuses = [e.grounding_status for e in item.evidence]
    for s in ("verified", "partial", "unsupported", "unlocated", "unchecked"):
        if s in statuses:
            return s
    return "no evidence"


def to_markdown(extraction: PaperExtraction) -> str:
    meta = extraction.metadata
    out = [f"# {meta.title or 'Untitled paper'}", ""]
    if meta.authors:
        out.append(", ".join(meta.authors))
    facts = [x for x in (meta.venue, meta.year) if x]
    facts += [f"arXiv:{meta.arxiv_id}"] if meta.arxiv_id else []
    facts += [f"doi:{meta.doi}"] if meta.doi else []
    if facts:
        out.append(" · ".join(facts))
    out.append("")
    for name, heading in SECTIONS:
        items: list[Item] = getattr(extraction, name)
        if not items:
            continue
        out += [f"## {heading}", ""]
        for item in items:
            out.append(f"- {item_label(item)} _[{_status(item)}]_")
            for ev in item.evidence:
                out.append(f"  > p. {ev.page}: “{ev.quote}”")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def to_csv(extraction: PaperExtraction) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(
        ["field", "id", "value", "confidence", "grounding_status", "page", "chunk_id", "quote"]
    )
    for name, item in extraction.all_items():
        ev = item.evidence[0] if item.evidence else None
        writer.writerow(
            [
                name,
                item.id,
                item_label(item),
                f"{item.confidence:.2f}",
                _status(item),
                ev.page if ev else "",
                ev.chunk_id if ev else "",
                ev.quote if ev else "",
            ]
        )
    return buf.getvalue()


def to_bibtex(extraction: PaperExtraction) -> str:
    meta = extraction.metadata
    fields: list[tuple[str, str]] = [
        ("title", meta.title or ""),
        ("author", " and ".join(meta.authors)),
        ("year", meta.year or ""),
        (
            "journal",
            meta.venue or (f"arXiv preprint arXiv:{meta.arxiv_id}" if meta.arxiv_id else ""),
        ),
        ("doi", meta.doi or ""),
        ("eprint", meta.arxiv_id or ""),
        ("url", meta.urls[0] if meta.urls else ""),
    ]
    if meta.arxiv_id:
        fields.append(("archivePrefix", "arXiv"))
    body = ",\n".join(f"  {k} = {{{_bib_escape(v)}}}" for k, v in fields if v)
    return f"@article{{{_bib_key(extraction)},\n{body}\n}}\n"


def _bib_key(extraction: PaperExtraction) -> str:
    meta = extraction.metadata
    surname = meta.authors[0].split()[-1] if meta.authors else "anon"
    words = [w for w in re.findall(r"[A-Za-z]+", meta.title or "") if len(w) > 3]
    raw = f"{surname}{meta.year or ''}{words[0] if words else ''}".lower()
    return unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode() or "paper"


def _bib_escape(text: str) -> str:
    return re.sub(r"([&%$#_])", r"\\\1", text)
