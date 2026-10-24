"""Gemini ablation arms (A2 granularity, A3 quotes) on the fixture paper with a fake LLM."""

import pytest

from app.config import Settings
from app.eval.ablate import EXPERIMENT_FIELDS, SCORED, extract_arm, output_schema, plan
from app.pipeline.verify.grounding import ground
from tests.fake_llm import FakePaperProvider
from tests.test_extraction import client, fixture_doc


def test_plans_differ_only_in_granularity() -> None:
    doc = fixture_doc()
    groups = plan("groups", doc, 48_000)
    assert [(c.label, c.fields) for c in groups] == [
        ("front", ["task"]),
        ("experiments", EXPERIMENT_FIELDS),
    ]
    assert [c.fields for c in plan("whole", doc, 48_000)] == [SCORED]
    per_field = plan("per_field", doc, 48_000)
    assert [c.fields for c in per_field] == [[f] for f in SCORED]
    # The whole text is every block the groups see, once: the experiments group is in it.
    whole = per_field[0].group
    assert groups[1].group.block_ids <= whole.block_ids
    assert len({b.id for b in whole.blocks}) == len(whole.blocks)
    with pytest.raises(ValueError):
        plan("everything", doc, 48_000)


def test_bare_schema_has_no_quote_fields() -> None:
    bare = output_schema(["hyperparameters"], quotes=False).model_json_schema()
    item = next(iter(bare["$defs"].values()))
    assert "quote" not in item["properties"] and "value_raw" in item["properties"]
    quoted = output_schema(["task"], quotes=True).model_json_schema()
    assert "quote" in next(iter(quoted["$defs"].values()))["properties"]


@pytest.mark.parametrize(("arm", "calls"), [("groups", 2), ("noquote", 2), ("whole", 1),
                                            ("per_field", 6)])  # fmt: skip
def test_arms_call_counts_and_evidence(settings: Settings, arm: str, calls: int) -> None:
    provider = FakePaperProvider()
    doc = fixture_doc()
    ex, made = extract_arm(arm, doc, client(settings, provider), 48_000)
    assert made == calls == len(provider.calls)
    assert all("ablation" not in c.prompt for c in provider.calls)  # the template comment
    assert ex.task and ex.datasets and ex.hyperparameters
    assert not ex.problem and not ex.limitations  # only the scored fields are asked for
    assert ex.hyperparameters[0].value_norm == 3e-4  # normalised in Python as in production
    assert [u.value for u in ex.code_urls] == ["https://github.com/example/sparseroute"]
    items = [i for name, i in ex.all_items() if name != "code_urls"]
    if arm == "noquote":
        assert all(not i.evidence for i in items)
        assert "quote" not in provider.calls[0].prompt.split("Fields:")[0]
    else:
        assert all(i.evidence for i in items)
        ground(ex, doc, client(settings, provider))
        assert all(e.grounding_status != "unlocated" for i in items for e in i.evidence)
