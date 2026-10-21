"""Structured extraction (M4): one LLM call per section group, merged into PaperExtraction.

Evidence returned here is only what the LLM claims (quote + chunk_id); the verify stage
(verify/grounding.py) locates each quote in the parsed text and checks it supports the value.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.pipeline.extract.groups import GroupText, build_groups
from app.pipeline.extract.hints import find_code_urls, find_hints
from app.pipeline.extract.normalize import normalize_value, same_item
from app.schemas.document import ParsedDocument
from app.schemas.extraction import (
    Claim,
    ClosingOut,
    Dataset,
    Evidence,
    ExperimentsOut,
    FrontOut,
    Hyperparameter,
    Item,
    ItemOut,
    Metadata,
    MethodOut,
    PaperExtraction,
)

log = logging.getLogger("paperlens.extract")

# group name -> (prompt template, output schema)
GROUP_SPECS: dict[str, tuple[str, type[BaseModel]]] = {
    "front": ("extract_front", FrontOut),
    "method": ("extract_method", MethodOut),
    "experiments": ("extract_experiments", ExperimentsOut),
    "closing": ("extract_closing", ClosingOut),
}


@dataclass
class GroupRun:
    name: str
    status: str  # done | failed | skipped
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    cached: bool = False
    items: int = 0
    truncated: bool = False
    error: str | None = None


@dataclass
class ExtractionRun:
    extraction: PaperExtraction
    groups: list[GroupRun] = field(default_factory=list)

    @property
    def calls(self) -> int:
        return sum(1 for g in self.groups if g.status == "done" and not g.cached)

    @property
    def all_failed(self) -> bool:
        ran = [g for g in self.groups if g.status != "skipped"]
        return bool(ran) and all(g.status == "failed" for g in ran)


def extract_document(
    doc: ParsedDocument,
    client: LLMClient,
    *,
    metadata: dict[str, Any] | None = None,
    max_group_chars: int = 48_000,
) -> ExtractionRun:
    extraction = PaperExtraction(metadata=_metadata(doc, metadata or {}))
    pages = {b.id: b.page for b in doc.blocks}
    groups = build_groups(doc, max_group_chars)
    runs: list[GroupRun] = []

    for name, (template, schema) in GROUP_SPECS.items():
        group = groups[name]
        if not group.text:
            runs.append(GroupRun(name, "skipped"))
            continue
        variables: dict[str, Any] = {"text": group.text}
        if name == "experiments":
            variables["hints"] = find_hints(group.blocks)
        prompt = prompts.render(template, **variables)
        try:
            result = client.generate_json(prompt, schema, role="extraction")
        except LLMError as exc:
            log.warning("extraction group %s failed: %s", name, exc)
            runs.append(GroupRun(name, "failed", prompt.id, error=f"{type(exc).__name__}: {exc}"))
            continue
        added = _absorb(extraction, result.value, group, pages)
        runs.append(
            GroupRun(
                name,
                "done",
                prompt.id,
                result.meta.provider,
                result.meta.model,
                result.meta.cached,
                added,
                group.truncated,
            )
        )

    _add_code_urls(extraction, doc)
    _dedupe(extraction)
    _number_items(extraction)
    return ExtractionRun(extraction, runs)


# ------------------------------------------------------------------ conversion


def _evidence(out: ItemOut, group: GroupText, pages: dict[str, int]) -> list[Evidence]:
    quote = out.quote.strip()
    if not quote:
        return []
    chunk = out.chunk_id.strip().strip("[]")
    if chunk not in pages:  # the model mis-cited; grounding will search the whole paper
        chunk = next(iter(group.block_ids), "")
    return [Evidence(chunk_id=chunk, page=pages.get(chunk, 1), quote=quote)]


def _base(out: ItemOut, group: GroupText, pages: dict[str, int]) -> dict[str, Any]:
    return {
        "id": "",
        "value": out.value.strip(),
        "evidence": _evidence(out, group, pages),
        "confidence": min(1.0, max(0.0, out.confidence)),
    }


def _absorb(
    extraction: PaperExtraction, out: BaseModel, group: GroupText, pages: dict[str, int]
) -> int:
    added = 0
    for name in type(out).model_fields:
        items: list[Any] = getattr(out, name)
        target: list[Any] = getattr(extraction, name)
        for raw in items:
            if not raw.value.strip() and not raw.quote.strip():
                continue
            base = _base(raw, group, pages)
            if name == "datasets":
                item: Item = Dataset(
                    **base, name=raw.name.strip() or raw.value.strip(), split=raw.split,
                    size=raw.size, public=raw.public or "unknown",
                )  # fmt: skip
            elif name == "hyperparameters":
                item = Hyperparameter(
                    **base, name=raw.name.strip(), value_raw=raw.value_raw.strip(),
                    value_norm=normalize_value(raw.value_raw), scope=raw.scope,
                )  # fmt: skip
            elif name == "claims":
                item = Claim(**base, kind=raw.kind or "qualitative")
            else:
                item = Item(**base)
            target.append(item)
            added += 1
    return added


def _metadata(doc: ParsedDocument, meta: dict[str, Any]) -> Metadata:
    """Source metadata (arXiv/Crossref) wins over what the parser read from the PDF."""
    authors = meta.get("authors") or [a.name for a in doc.metadata.authors]
    urls = [u for u in (meta.get("source_url"), meta.get("pdf_url")) if u]
    if meta.get("arxiv_id"):
        urls.insert(0, f"https://arxiv.org/abs/{meta['arxiv_id']}")
    return Metadata(
        title=meta.get("title") or doc.metadata.title,
        authors=[str(a) for a in authors],
        venue=meta.get("venue") or doc.metadata.venue,
        year=meta.get("year") or doc.metadata.year,
        arxiv_id=meta.get("arxiv_id") or doc.metadata.arxiv_id,
        doi=meta.get("doi") or doc.metadata.doi,
        urls=list(dict.fromkeys(urls)),
    )


def _add_code_urls(extraction: PaperExtraction, doc: ParsedDocument) -> None:
    """Repository links come from regex over the paper text, not from the LLM."""
    for url, block, sentence in find_code_urls(doc.blocks):
        extraction.code_urls.append(
            Item(
                id="",
                value=url,
                evidence=[Evidence(chunk_id=block.id, page=block.page, quote=sentence)],
                confidence=1.0,
                source="rule",
            )
        )


def _dedupe(extraction: PaperExtraction) -> None:
    """Merge items naming the same thing; keep the most confident, pool their evidence."""
    for name in PaperExtraction.model_fields:
        if name in ("metadata", "results"):
            continue
        items: list[Item] = getattr(extraction, name)
        merged: list[Item] = []
        for item in items:
            key = _dedupe_key(item)
            twin = next((m for m in merged if same_item(_dedupe_key(m), key)), None)
            if twin is None:
                merged.append(item)
                continue
            if item.confidence > twin.confidence:
                twin.value, twin.confidence = item.value, item.confidence
            quotes = {e.quote for e in twin.evidence}
            twin.evidence += [e for e in item.evidence if e.quote not in quotes]
        setattr(extraction, name, merged)


def _dedupe_key(item: Item) -> str:
    if isinstance(item, Hyperparameter):
        return f"{item.name} {item.scope} {item.value_raw}"
    if isinstance(item, Dataset):
        return item.name
    return item.value


def _number_items(extraction: PaperExtraction) -> None:
    for name in PaperExtraction.model_fields:
        if name in ("metadata", "results"):
            continue
        for i, item in enumerate(getattr(extraction, name)):
            item.id = f"{name}.{i}"
