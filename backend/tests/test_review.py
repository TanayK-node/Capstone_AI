"""Reviewer mode (F15): facts come from the analyses, in Python."""

from __future__ import annotations

from app.pipeline.review.service import findings
from app.schemas.claims import ClaimCheck, ClaimReport
from app.schemas.code import CodeParam, CodeReport, Comparison
from app.schemas.repro import ItemResult, Scorecard


def test_findings_come_from_the_analyses() -> None:
    card = Scorecard(checklist_version=4, score=50.0, groups=[], items=[
        ItemResult(id="seeds", group="stats", description="Number of seeds", weight=2.0,
                   status="missing"),
        ItemResult(id="lr", group="setup", description="Learning rate", weight=1.0,
                   status="present"),
    ])  # fmt: skip
    claims = ClaimReport(tolerance=0.15, claims=[
        ClaimCheck(id="claims.0", text="We improve BLEU by 5.", verdict="contradicted",
                   explanation="the tables give +2.1"),
        ClaimCheck(id="claims.1", text="Fast.", verdict="supported"),
    ])  # fmt: skip
    code = CodeReport(status="ok", comparisons=[
        Comparison(canonical="learning_rate", status="mismatch", paper_name="learning rate",
                   paper_value="1e-4", code_values=[CodeParam(name="lr", value="5e-05",
                                                              file="run.py", kind="flags")]),
        Comparison(canonical="batch_size", status="match"),
    ])  # fmt: skip
    facts = findings(card, claims, code)
    assert [f.source for f in facts] == ["reproducibility", "claims", "code"]
    assert facts[0].text == "Not stated: Number of seeds"
    assert "contradicted" in facts[1].text and "+2.1" in facts[1].text
    assert facts[2].text == "learning rate: paper 1e-4, code 5e-05"
