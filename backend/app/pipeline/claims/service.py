"""Claims stage (M8): parse the extracted claims with one LLM call, then verify in Python."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app import prompts
from app.llm.client import LLMClient
from app.llm.errors import LLMError
from app.pipeline.claims.verifier import number, verify
from app.schemas.claims import ClaimCheck, ClaimReport, ClaimsParseOut
from app.schemas.extraction import PaperExtraction
from app.schemas.results import ResultsTable

log = logging.getLogger("paperlens.claims")


@dataclass
class ClaimsRun:
    report: ClaimReport
    llm_calls: int = 0
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    warnings: list[str] = field(default_factory=list)


def check_claims(
    extraction: PaperExtraction,
    tables: list[ResultsTable],
    client: LLMClient | None,
    tolerance: float,
) -> ClaimsRun:
    claims = [
        ClaimCheck(id=c.id, text=(c.evidence[0].quote if c.evidence else c.value),
                   evidence=c.evidence)
        for c in extraction.claims
    ]  # fmt: skip
    run = ClaimsRun(ClaimReport(tolerance=tolerance, claims=claims))
    if not claims:
        return run
    parsed: set[int] = set()
    if client is None:
        run.warnings.append("no LLM available: claims were not parsed or checked")
    else:
        parsed = _parse(claims, client, run)
    for i, claim in enumerate(claims):
        if i in parsed:
            verify(claim, tables, tolerance)
        else:  # never guess a verdict for a claim nobody read
            claim.verdict, claim.explanation = "unverifiable", "The claim could not be parsed."
    counts: dict[str, int] = {}
    for c in claims:
        counts[c.verdict] = counts.get(c.verdict, 0) + 1
    run.report.counts = counts
    run.report.warnings = run.warnings
    return run


def _parse(claims: list[ClaimCheck], client: LLMClient, run: ClaimsRun) -> set[int]:
    """Fill the claim fields from the LLM; returns the indices it answered for."""
    prompt = prompts.render(
        "claims_parse", claims=[{"id": i, "text": c.text} for i, c in enumerate(claims)]
    )
    run.prompt_version = prompt.id
    try:
        result = client.generate_json(prompt, ClaimsParseOut, role="extraction")
    except LLMError as exc:
        run.warnings.append(f"claim parsing failed: {type(exc).__name__}: {exc}")
        return set()
    run.llm_calls += 0 if result.meta.cached else 1
    run.provider, run.model = result.meta.provider, result.meta.model
    answered: set[int] = set()
    for out in result.value.claims:
        if not 0 <= out.id < len(claims):
            continue
        answered.add(out.id)
        c = claims[out.id]
        c.kind, c.method, c.baseline = out.kind, out.method.strip(), out.baseline.strip()
        c.dataset, c.metric = out.dataset.strip(), out.metric.strip()
        c.comparator, c.direction, c.delta_unit = out.comparator, out.direction, out.delta_unit
        # Numbers are parsed in Python from the text the LLM copied (CLAUDE.md rule 4).
        c.claimed_value = number(out.value) if out.kind == "score" else None
        c.claimed_delta = number(out.delta) if out.kind in ("improvement", "factor") else None
    return answered
