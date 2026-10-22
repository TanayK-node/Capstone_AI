"""Claim verifier (M8): verdicts are computed in Python from table cells."""

from app.pipeline.claims.service import check_claims
from app.pipeline.claims.verifier import name_score, number, verify
from app.pipeline.results.builder import build_table
from app.schemas.claims import ClaimCheck
from app.schemas.extraction import Claim, PaperExtraction
from app.schemas.results import ResultsTable
from tests.test_results import table_block

TOL = 0.15


def transformer_table() -> ResultsTable:
    t = build_table(
        table_block(
            [
                ["", "BLEU", "", "", "Training Cost (FLOPs)"],
                ["Model", "EN-DE", "EN-FR", "EN-DE", "EN-FR"],
                ["GNMT + RL [38]", "24.6", "39.92", "2.3e19", "1.4e20"],
                ["ConvS2S Ensemble [9]", "26.36", "41.29", "7.7e19", "1.2e21"],
                ["Transformer (big)", "28.4", "41.8", "2.3e19", "2.3e19"],
            ],
            caption="Table 2: The Transformer achieves better BLEU scores.",
        ),
        names=["Transformer"],
    )
    assert t is not None
    return t


def claim(**kw) -> ClaimCheck:  # type: ignore[no-untyped-def]
    return ClaimCheck(id="claims.0", text="", **kw)


def test_score_supported_from_the_papers_row() -> None:
    c = claim(kind="score", metric="BLEU", dataset="WMT 2014 English-to-German",
              claimed_value=28.4)  # fmt: skip
    verify(c, [transformer_table()], TOL)
    assert c.verdict == "supported"
    assert c.checked_cells[0].row_label == "Transformer (big)"
    assert c.checked_cells[0].column.endswith("EN-DE")


def test_score_contradicted_by_the_one_matching_cell() -> None:
    c = claim(kind="score", metric="BLEU", dataset="English-to-French", claimed_value=42.5)
    verify(c, [transformer_table()], TOL)
    assert c.verdict == "contradicted" and c.table_value == 41.8
    assert "41.8" in c.explanation


def test_improvement_over_previous_best_at_least() -> None:
    """ "improving over the existing best results ... by over 2 BLEU" """
    c = claim(kind="improvement", metric="BLEU", dataset="English-German", claimed_delta=2.0,
              baseline="the existing best results", comparator="at_least")  # fmt: skip
    verify(c, [transformer_table()], TOL)
    assert c.verdict == "supported"
    assert c.recomputed_delta == round(28.4 - 26.36, 4)  # Python, not the LLM
    assert [x.role for x in c.checked_cells] == ["method", "baseline"]


def test_wrong_amount_is_not_supported() -> None:
    c = claim(kind="improvement", metric="BLEU", dataset="English-German",
              baseline="GNMT + RL", claimed_delta=5.0)  # fmt: skip
    verify(c, [transformer_table()], TOL)
    assert c.verdict in ("contradicted", "unsupported")
    assert c.recomputed_delta == round(28.4 - 24.6, 4)


def test_lower_is_better_and_relative_percent() -> None:
    t = build_table(
        table_block([["Method", "Top-1 error (%)"], ["ResNet-34", "25.0"], ["Ours", "20.0"]]),
        names=[],
    )
    assert t is not None
    points = claim(kind="improvement", metric="top-1 error", baseline="ResNet-34",
                   claimed_delta=5.0, delta_unit="points", direction="lower")  # fmt: skip
    verify(points, [t], TOL)
    assert points.verdict == "supported"
    relative = claim(kind="improvement", metric="top-1 error", baseline="ResNet-34",
                     claimed_delta=20.0, delta_unit="percent", direction="lower")  # fmt: skip
    verify(relative, [t], TOL)
    assert relative.verdict == "supported" and relative.recomputed_relative == 20.0


def test_factor_claim() -> None:
    t = build_table(
        table_block([["Method", "# Trainable Parameters", "Acc"],
                     ["GPT-3 (FT)", "175255.8M", "73.8"], ["GPT-3 (LoRA)", "4.7M", "74.0"]]),
        names=["LoRA"],
    )  # fmt: skip
    assert t is not None
    c = claim(kind="factor", metric="trainable parameters", baseline="GPT-3 175B fine-tuned",
              claimed_delta=10000, comparator="at_least", direction="lower")  # fmt: skip
    verify(c, [t], TOL)
    assert c.verdict == "supported" and c.recomputed_factor and c.recomputed_factor > 37000


def test_qualitative_and_unverifiable() -> None:
    q = claim(kind="qualitative")
    verify(q, [transformer_table()], TOL)
    assert q.verdict == "weakly_supported"
    missing = claim(kind="score", metric="ROUGE-L", claimed_value=40.0)
    verify(missing, [transformer_table()], TOL)
    assert missing.verdict == "unverifiable" and "ROUGE-L" in missing.explanation


def test_unparsed_claims_are_unverifiable_never_guessed() -> None:
    ex = PaperExtraction(claims=[Claim(id="claims.0", value="We are state of the art.")])
    report = check_claims(ex, [transformer_table()], client=None, tolerance=TOL).report
    assert report.claims[0].verdict == "unverifiable"
    assert report.counts == {"unverifiable": 1}


def test_helpers() -> None:
    assert number("over 2 BLEU") == 2.0 and number("10,000") == 10000.0
    assert number("4.2%") == 4.2 and number("") is None
    assert name_score("English-to-German", "BLEU EN-DE") >= 90
    assert name_score("ResNet", "Transformer (big)") < 80
