"""Phase 6 evaluation: matching rules, report parsing, field scores."""

from __future__ import annotations

from pathlib import Path

from app.eval.data import GoldItem, PredItem, from_extraction, from_markdown
from app.eval.extraction import evaluate
from app.eval.match import numbers, parts, text_match, value_match
from app.eval.run_eval import audit_md, breakdown_md, gemini_arms_md, previous_a1_a6
from app.schemas.extraction import Evidence, Hyperparameter, Item, PaperExtraction


def test_text_match_is_lenient_on_wording_strict_on_identity() -> None:
    assert text_match("BLEU score", "BLEU")
    assert text_match("WMT 2014 English-to-German", "WMT 2014 English-German")
    assert text_match("the standard WMT 2014 English-German dataset", "WMT 2014 English-German")
    assert text_match("Four NVIDIA Titan Black GPUs", "4 NVIDIA Titan Black GPUs")
    assert text_match("NVIDIA Tesla V100 used for all experiments", "V100")
    assert not text_match("ImageNet-21k", "ImageNet")
    assert not text_match("CIFAR-100", "CIFAR-10")
    assert not text_match("visual recognition tasks", "object detection")
    # Metrics: qualifiers around the gold name are fine, not the other way round.
    assert text_match("logical form validation accuracy", "accuracy", qualifiers=True)
    assert not text_match("top-5 error", "top-5 localisation error", qualifiers=True)


def test_packed_items_are_split() -> None:
    assert "F1" in parts("Exact Match (EM) and F1")
    assert {"CIFAR-10", "CIFAR-100"} <= set(parts("CIFAR-10/100"))
    assert "GLUE" in parts("General Language Understanding Evaluation (GLUE)")
    assert "BitFit" in parts("Bias-only or BitFit")


def test_values_are_compared_as_numbers() -> None:
    assert numbers("5 • 10 -4") == [5e-4]
    assert 0.06 in numbers("6%")
    assert numbers("none") == [0.0]
    assert value_match("80 sentences", ["80"])
    assert value_match("10 -9", ["1e-9"])
    assert value_match("5e-5, 4e-5, 3e-5, and 2e-5", ["3e-5"])  # one of a listed grid
    assert value_match("Adam", ["Adam"]) and not value_match("Adam", ["SGD"])
    assert not value_match("3e-4", ["3e-5"])


REPORT = """# Phase 2 extraction check

## 1234.5678

# A Paper

## Datasets

- WMT'14 (348M words) _[verified]_
  > p. 4: “We use WMT'14.”
- MadeUpSet _[unlocated]_

## Hyperparameters

- learning rate (fine-tuning): 3e-5 _[verified]_
  > p. 5: “lr 3e-5.”
- batch size: 32 _[partial]_
"""


def test_report_markdown_is_parsed() -> None:
    preds = from_markdown(REPORT)
    assert [(p.field, p.value, p.status) for p in preds][:2] == [
        ("datasets", "WMT'14", "verified"), ("datasets", "MadeUpSet", "unlocated")]  # fmt: skip
    hp = preds[2]
    assert (hp.name, hp.scope, hp.value, hp.page) == ("learning rate", "fine-tuning", "3e-5", 5)


def test_scores_per_field() -> None:
    gold = [
        GoldItem("p", "datasets", "WMT'14 English-French", aliases=["WMT'14"]),
        GoldItem("p", "datasets", "newstest2013"),
        GoldItem("p", "hyperparameters", "3e-5", name="learning_rate"),
        GoldItem("p", "hyperparameters", "32", name="batch_size"),
        GoldItem("p", "hyperparameters", "0.1", name="dropout"),
    ]
    preds = [
        PredItem("p", "datasets", "WMT'14", status="verified"),
        PredItem("p", "datasets", "MadeUpSet", status="unlocated"),
        PredItem("p", "hyperparameters", "3e-5", name="learning rate", status="verified"),
        PredItem("p", "hyperparameters", "64", name="batch size", status="partial"),
    ]
    rep = evaluate(gold, preds)
    ds = rep.total("datasets")
    assert (ds.precision, ds.recall) == (0.5, 0.5)
    hp = rep.total("hyperparameters")
    assert (hp.pred_correct, hp.gold_found) == (1, 1)
    assert rep.hp_coverage == 1 / 3  # lr found; batch size wrong; dropout missing
    assert rep.numeric_accuracy == 0.5  # 2 named in gold, 1 right
    assert rep.hallucination_rate == 0.25  # MadeUpSet: no locatable evidence
    assert [g.value for g in rep.papers[0].missed["datasets"]] == ["newstest2013"]


def test_predictions_from_extraction_json() -> None:
    ex = PaperExtraction(
        task=[Item(id="task.0", value="machine translation",
                   evidence=[Evidence(chunk_id="b1", page=1, quote="q",
                                      grounding_status="verified")])],
        hyperparameters=[Hyperparameter(id="hyperparameters.0", value="lr: 1e-4",
                                        name="learning rate", value_raw="1e-4")],
    )  # fmt: skip
    preds = from_extraction("p", ex)
    assert (preds[0].field, preds[0].status, preds[0].page) == ("task", "verified", 1)
    assert (preds[1].name, preds[1].value, preds[1].status) == (
        "learning rate",
        "1e-4",
        "no evidence",
    )


def test_a3_policies_filter_by_evidence() -> None:
    from app.eval.ablations import a3, core_scores

    gold = [GoldItem("p", "datasets", "SQuAD"), GoldItem("p", "datasets", "GLUE")]
    preds = [PredItem("p", "datasets", "SQuAD", status="verified"),
             PredItem("p", "datasets", "GLUE", status="unlocated"),
             PredItem("p", "datasets", "MadeUp", status="unsupported")]  # fmt: skip
    reps = a3(gold, preds)
    keep_all, located, *_, verified = reps.values()
    assert core_scores(keep_all)[1] == 1.0 and core_scores(verified)[1] == 0.5
    assert located.hallucination_rate == 0.5  # SQuAD verified, MadeUp unsupported
    assert verified.hallucination_rate == 0.0


def test_gold_found_in_parsed_text() -> None:
    from app.eval.ablations import _found_in

    texts = ["We train with a learning rate of 3e-4 for 50k steps.",
             "Results on WMT 2014 English-German."]  # fmt: skip
    assert _found_in(texts, GoldItem("p", "hyperparameters", "0.0003", name="learning_rate"))
    assert not _found_in(texts, GoldItem("p", "hyperparameters", "1e-4", name="learning_rate"))
    assert _found_in(texts, GoldItem("p", "datasets", "WMT 2014 English-German"))


def test_breakdown_by_group_and_shared_papers(tmp_path: Path) -> None:
    gold = [GoldItem(pid, "datasets", "SQuAD") for pid in ("a", "b", "c")]
    preds = {
        "big": [PredItem(pid, "datasets", "SQuAD", status="verified") for pid in ("a", "b", "c")],
        "small": [PredItem("a", "datasets", "MNIST", status="verified")],
    }
    groups = {"a": ("reference", "NLP"), "b": ("new", "NLP"), "c": ("new", "CV")}
    md = breakdown_md(gold, preds, groups)
    assert "| set: new | 2 | 1.00 |" in md and "| area: NLP | 2 | 1.00 |" in md
    assert "### small" not in md  # one paper: nothing to break down
    assert "Every run on the 1 papers they share" in md
    assert "| small | 1 | 0.00 |" in md  # like-for-like on paper a only

    audit = tmp_path / "audit_x.csv"
    rows = ["run,paper_id,field,extracted,evidence,category",
            "big,a,datasets,SQuAD v1,verified,matcher missed",
            "big,a,code_urls,https://x,verified,out of scope"]  # fmt: skip
    audit.write_text("\n".join(rows) + "\n", encoding="utf-8")
    md = audit_md([audit])
    assert "| datasets | 1 | 0 |" in md and "| all | 1 | 1 |" in md


def test_a1_a6_sections_survive_a_run_without_pdfs() -> None:
    md = (
        "# Ablations\n\n## A3: x\n\n## A1: parser\n\n| a |\n\n"
        "## A6: retrieval\n\n| b |\n\n## A2 / A3 / A5: Gemini arms\n\n| c |\n\n## Pending\n"
    )
    kept = previous_a1_a6(md)
    assert kept[0].startswith("_A1 and A6 kept") and "## A1: parser" in kept
    assert "## A6: retrieval" in kept and not any("Pending" in x for x in kept)
    assert "| b |" in kept and not any("Gemini arms" in x or "| c |" in x for x in kept)
    assert previous_a1_a6("# Ablations\n\nA1 and A6 not run\n\n## Pending\n") == []


def test_gemini_arms_table_on_shared_papers(tmp_path: Path) -> None:
    gold = [GoldItem(pid, "datasets", "SQuAD") for pid in ("a", "b")]
    preds = {
        "collect_flash_lite": [PredItem(p, "datasets", "SQuAD", status="verified") for p in "ab"],
        "a3_noquote": [PredItem("a", "datasets", "SQuAD", status="unchecked")],
    }
    (tmp_path / "a3_noquote").mkdir()
    (tmp_path / "a3_noquote" / "calls.json").write_text('{"a": {"calls": 2, "model": "m"}}')
    md = "\n".join(gemini_arms_md(gold, preds, tmp_path))
    assert "Same 1 papers" in md  # only paper a is in both runs
    assert "| `a3_noquote` | 2.0 |" in md and "n/a (no quotes)" in md
    assert gemini_arms_md(gold, {"collect_flash_lite": preds["collect_flash_lite"]}, tmp_path) == []
