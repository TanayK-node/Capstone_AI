"""Reproducibility analyzer (M6): rules -> repository check -> LLM for the rest -> score.

1. Each checklist item with a rule is decided by it, unless the rule is inconclusive or only
   found candidate mentions (rules.py "candidate": a mention is not full coverage).
2. Inconclusive, candidate and rule-less items go to the LLM in ONE call over the experiment
   sections, tables and appendix, with the candidate sentences listed; it returns a status
   plus a verbatim quote per item. Without an answer, a candidate counts as "partial".
3. Every quote is grounded like Phase 2 extraction (verify/grounding.py). An LLM "present"
   whose quote is not found in the paper, or does not support the item, is capped at
   "partial" with a note: a hallucinated quote must not earn full marks.
4. Python computes group scores and the 0-100 total (CLAUDE.md rule 4).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.pipeline.extract.groups import build_groups, render_block
from app.pipeline.repro.github import GitHubClient, parse_repo_url
from app.pipeline.repro.rules import RULES, RuleContext, RuleResult
from app.pipeline.verify.grounding import VerifyRun, attach_location, check_support
from app.schemas.document import Block, ParsedDocument
from app.schemas.extraction import Evidence, PaperExtraction
from app.schemas.repro import (
    POINTS,
    Checklist,
    GroupScore,
    ItemResult,
    RepoInfo,
    ReproOut,
    Scorecard,
)

log = logging.getLogger("paperlens.repro")


@dataclass
class ReproRun:
    scorecard: Scorecard
    llm_items: int = 0
    llm_calls: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    warnings: list[str] = field(default_factory=list)


def analyze(
    doc: ParsedDocument,
    extraction: PaperExtraction,
    checklist: Checklist,
    *,
    client: LLMClient | None,
    github: GitHubClient | None,
    pdf_path: Path | None = None,
    max_chars: int = 48_000,
) -> ReproRun:
    repo = _inspect_repo(extraction, github)
    ctx = RuleContext.build(doc, extraction, repo)
    items: dict[str, ItemResult] = {}
    candidates: dict[str, RuleResult] = {}
    for ci in checklist.items:
        result = RULES[ci.rule](ctx) if ci.rule else RuleResult("inconclusive")
        item = ItemResult(id=ci.id, group=ci.group, description=ci.description, weight=ci.weight)
        if result.status == "candidate":
            candidates[ci.id] = result  # stays open for the LLM
        elif result.status != "inconclusive":
            item.status, item.note, item.source = result.status, result.note, result.source
            item.evidence = result.evidence
        items[ci.id] = item

    run = ReproRun(Scorecard(checklist_version=checklist.version, score=None, groups=[], items=[]))
    open_items = [items[ci.id] for ci in checklist.items if items[ci.id].source == "none"]
    if open_items and client is not None:
        guidance = {ci.id: ci.guidance for ci in checklist.items}
        _ask_llm(open_items, candidates, guidance, doc, extraction, client, max_chars, run)
    elif open_items:
        run.warnings.append("no LLM available: items without a decisive rule are unknown")
        _fallback_to_candidates(open_items, candidates)

    _ground(list(items.values()), doc, client, pdf_path, run)
    card = run.scorecard
    card.items = [items[ci.id] for ci in checklist.items]
    card.repo = repo
    if repo and repo.error:
        run.warnings.append(f"repository check: {repo.error}")
    score_card(card, checklist)
    card.warnings = run.warnings
    return run


# ------------------------------------------------------------------ steps


def _inspect_repo(extraction: PaperExtraction, github: GitHubClient | None) -> RepoInfo | None:
    if not extraction.code_urls:
        return None
    url = extraction.code_urls[0].value
    if github is None:
        info = parse_repo_url(url)
        info.error = "repository check switched off"
        return info
    return github.inspect(url)


def context_text(doc: ParsedDocument, max_chars: int) -> str:
    """Experiment sections, every table, training-detail paragraphs and the whole appendix:
    where reproducibility details live. Tagged with block ids like extraction prompts."""
    chosen: list[Block] = list(build_groups(doc, max_chars)["experiments"].blocks)
    seen = {b.id for b in chosen}
    for block in doc.blocks:
        if block.id in seen or (block.role or "") != "appendix":
            continue
        if block.type in ("paragraph", "table", "caption", "footnote"):
            chosen.append(block)
            seen.add(block.id)
    chosen.sort(key=lambda b: b.order)
    parts: list[str] = []
    used = 0
    for block in chosen:
        piece = render_block(block)
        if used + len(piece) > max_chars:
            break
        parts.append(piece)
        used += len(piece) + 2
    return "\n\n".join(parts)


def _extracted_summary(extraction: PaperExtraction) -> list[str]:
    lines: list[str] = []
    if extraction.datasets:
        lines.append("datasets: " + "; ".join(d.name or d.value for d in extraction.datasets[:12]))
    if extraction.baselines:
        lines.append("baselines: " + "; ".join(b.value for b in extraction.baselines[:12]))
    if extraction.hyperparameters:
        hps = [f"{h.name}={h.value_raw}" for h in extraction.hyperparameters[:15]]
        lines.append("hyperparameters: " + "; ".join(hps))
    if extraction.compute:
        lines.append("compute: " + "; ".join(c.value for c in extraction.compute[:5]))
    return lines


def _fallback_to_candidates(
    open_items: list[ItemResult], candidates: dict[str, RuleResult]
) -> None:
    """No LLM verdict: a rule's mention counts as "partial" (mentioned, coverage unjudged)."""
    for item in open_items:
        cand = candidates.get(item.id)
        if cand is None or item.status != "unknown":
            continue
        item.status, item.source = "partial", "rule"
        item.note = f"{cand.note} Coverage not judged (no LLM answer)."
        item.evidence = cand.evidence


def _ask_llm(
    open_items: list[ItemResult],
    candidates: dict[str, RuleResult],
    guidance: dict[str, str],
    doc: ParsedDocument,
    extraction: PaperExtraction,
    client: LLMClient,
    max_chars: int,
    run: ReproRun,
) -> None:
    prompt = prompts.render(
        "repro_checklist",
        items=[
            {
                "id": i.id,
                "description": i.description,
                "guidance": guidance.get(i.id, ""),
                "matches": [f"[{e.chunk_id}] {e.quote}" for e in candidates[i.id].evidence]
                if i.id in candidates
                else [],
            }
            for i in open_items
        ],
        extracted=_extracted_summary(extraction),
        text=context_text(doc, max_chars),
    )
    run.prompt_version = prompt.id
    run.llm_items = len(open_items)
    try:
        result = client.generate_json(prompt, ReproOut, role="extraction")
    except LLMError as exc:
        run.warnings.append(f"checklist LLM call failed: {type(exc).__name__}: {exc}")
        for item in open_items:
            item.note = "LLM call failed; not decided"
        _fallback_to_candidates(open_items, candidates)
        return
    run.llm_calls += 0 if result.meta.cached else 1
    run.provider, run.model = result.meta.provider, result.meta.model
    pages = {b.id: b.page for b in doc.blocks}
    answers = {a.id.strip(): a for a in result.value.items}
    # A rule's pattern match proves the item is mentioned: never "missing" (the sentence may
    # sit outside the text the LLM was given, e.g. DistilBERT's "8 16GB V100 GPUs").
    for item_id, out in answers.items():
        if item_id in candidates and out.status in ("missing", "not_applicable"):
            out.status = "partial"
            out.quote, out.chunk_id = "", ""
            out.note = f"{candidates[item_id].note} (the LLM missed it; pattern match)"
    for item in open_items:
        answer = answers.get(item.id)
        if answer is None:
            item.note = "The LLM gave no answer for this item."
            _fallback_to_candidates([item], candidates)
            continue
        item.source = "llm"
        item.status = answer.status
        item.note = answer.note.strip()
        quote = answer.quote.strip()
        if quote and answer.status in ("present", "partial"):
            chunk = answer.chunk_id.strip().strip("[]")
            item.evidence = [Evidence(chunk_id=chunk, page=pages.get(chunk, 1), quote=quote)]
        elif answer.status in ("present", "partial") and item.id in candidates:
            item.evidence = candidates[item.id].evidence  # the rule's sentences back it


def _ground(
    items: list[ItemResult],
    doc: ParsedDocument,
    client: LLMClient | None,
    pdf_path: Path | None,
    run: ReproRun,
) -> None:
    blocks = {b.id: b for b in doc.blocks}
    pdf = pymupdf.open(pdf_path) if pdf_path and pdf_path.exists() else None
    to_check: list[tuple[str, str, Evidence]] = []
    try:
        for item in items:
            for ev in item.evidence:
                if ev.grounding_status in ("verified", "partial") and ev.boxes:
                    continue  # copied from the verified extraction
                if not attach_location(ev, blocks, pdf):
                    continue
                if item.source == "llm":
                    ev.grounding_status = "unchecked"
                    to_check.append((f"checklist: {item.id}", item.description, ev))
                else:
                    ev.grounding_status = "verified"  # a rule hit is its own evidence
    finally:
        if pdf is not None:
            pdf.close()
    if to_check and client is not None:
        verify = VerifyRun()
        check_support(client, to_check, verify)
        run.llm_calls += verify.support_calls
        run.warnings += verify.warnings
    # Cap LLM claims whose quote is not in the paper or does not support the item.
    for item in items:
        if item.source != "llm" or item.status != "present" or not item.evidence:
            continue
        if not any(e.grounding_status in ("verified", "partial") for e in item.evidence):
            item.status = "partial"
            item.note = (item.note + " (quote not confirmed in the paper)").strip()


def score_card(card: Scorecard, checklist: Checklist) -> None:
    """Weighted mean of item points per group, then of groups; unknown / not applicable
    items and groups with nothing scorable are left out of the denominator."""
    questions = {ci.id: ci.question for ci in checklist.items}
    groups: list[GroupScore] = []
    for g in checklist.groups:
        members = [i for i in card.items if i.group == g.id]
        scored = [i for i in members if i.status in POINTS]
        total_w = sum(i.weight for i in scored)
        score = sum(i.weight * POINTS[i.status] for i in scored) / total_w if total_w else None
        counts: dict[str, int] = {}
        for i in members:
            counts[i.status] = counts.get(i.status, 0) + 1
        groups.append(
            GroupScore(
                id=g.id,
                label=g.label,
                weight=g.weight,
                score=None if score is None else round(score, 3),
                counts=counts,
            )
        )
    card.groups = groups
    weighted = [(g.weight, g.score) for g in groups if g.score is not None]
    total_w = sum(w for w, _ in weighted)
    card.score = round(100 * sum(w * s for w, s in weighted) / total_w, 1) if total_w else None

    group_w = {g.id: g.weight for g in checklist.groups}
    gaps = [i for i in card.items if i.status in ("missing", "partial")]
    gaps.sort(key=lambda i: (i.status != "missing", -i.weight * group_w.get(i.group, 0)))
    card.missing = [i.id for i in gaps]
    for item in card.items:
        item.question = questions.get(item.id, "") if item.id in card.missing else ""
    card.questions = [questions[i.id] for i in gaps if questions.get(i.id)]
