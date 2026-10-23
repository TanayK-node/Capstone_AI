"""Extraction quality against the gold set (SCOPE.md section 8, "Metrics").

Per field: precision = extracted items that match a gold item / extracted items; recall =
gold items matched by some extracted item / gold items. Several extracted items may match
the same gold item (paraphrases); an extracted item that matches nothing is a false positive.

Hyperparameters, in addition:
- coverage: share of the gold (paper, hyperparameter name) pairs for which a correct value
  was extracted (the gold lists every stated setting; coverage asks "did we get the lr?");
- numeric accuracy: of the extracted hyperparameters whose name is in the gold for that paper,
  the share whose value is right (SCOPE.md: "exact after normalization").

Grounding over every extracted item, all fields: share verified / partial / unlocated /
unsupported / without evidence. Hallucination rate = unlocated + unsupported + no evidence.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from app.eval.data import SCORED_FIELDS, GoldItem, PredItem
from app.eval.match import any_match, hp_name, hp_names, numbers, url_key, value_match

CORE_FIELDS = ("task", "datasets", "baselines", "metrics", "hyperparameters", "code_urls")
UNGROUNDED = ("unlocated", "unsupported", "no evidence", "unchecked")


@dataclass
class FieldScore:
    gold: int = 0
    pred: int = 0
    pred_correct: int = 0
    gold_found: int = 0

    @property
    def precision(self) -> float | None:
        return self.pred_correct / self.pred if self.pred else None

    @property
    def recall(self) -> float | None:
        return self.gold_found / self.gold if self.gold else None

    @property
    def f1(self) -> float | None:
        p, r = self.precision, self.recall
        if p is None or r is None:
            return None
        return 2 * p * r / (p + r) if p + r else 0.0

    def add(self, other: FieldScore) -> None:
        self.gold += other.gold
        self.pred += other.pred
        self.pred_correct += other.pred_correct
        self.gold_found += other.gold_found


@dataclass
class PaperResult:
    paper_id: str
    fields: dict[str, FieldScore] = field(default_factory=dict)
    missed: dict[str, list[GoldItem]] = field(default_factory=dict)
    wrong: dict[str, list[PredItem]] = field(default_factory=dict)
    hp_names_gold: set[str] = field(default_factory=set)
    hp_names_found: set[str] = field(default_factory=set)
    hp_named: int = 0  # extracted hyperparameters whose name is in the gold
    hp_named_right: int = 0


@dataclass
class ExtractionReport:
    papers: list[PaperResult]
    status_counts: Counter[str]
    status_by_field: dict[str, Counter[str]]

    def total(self, name: str) -> FieldScore:
        out = FieldScore()
        for p in self.papers:
            if name in p.fields:
                out.add(p.fields[name])
        return out

    def macro_f1(self, name: str) -> float | None:
        vals = [
            f1 for p in self.papers if name in p.fields and (f1 := p.fields[name].f1) is not None
        ]
        return sum(vals) / len(vals) if vals else None

    @property
    def hp_coverage(self) -> float | None:
        gold = sum(len(p.hp_names_gold) for p in self.papers)
        return sum(len(p.hp_names_found) for p in self.papers) / gold if gold else None

    @property
    def numeric_accuracy(self) -> float | None:
        named = sum(p.hp_named for p in self.papers)
        return sum(p.hp_named_right for p in self.papers) / named if named else None

    @property
    def hallucination_rate(self) -> float | None:
        total = sum(self.status_counts.values())
        bad = sum(self.status_counts[s] for s in UNGROUNDED)
        return bad / total if total else None


def _gold_hp_names(g: GoldItem) -> list[str]:
    return [g.name.replace("_", " "), *g.aliases]


def _hp_name_match(p: PredItem, g: GoldItem) -> bool:
    return bool(hp_names(p.name) & hp_names(g.name)) or any_match(p.name, _gold_hp_names(g))


def _gold_values(g: GoldItem) -> list[str]:
    """A numeric gold value is complete as written; its aliases are other names for the
    hyperparameter ("β1"), which must not be read as values."""
    return [g.value] if numbers(g.value) else g.names


def _matches(field_name: str, p: PredItem, g: GoldItem) -> bool:
    if field_name == "hyperparameters":
        return _hp_name_match(p, g) and value_match(p.value, _gold_values(g))
    if field_name == "code_urls":
        pu = url_key(p.value)
        return any(u and (u in pu or pu in u) for u in map(url_key, g.names))
    return any_match(p.value, g.names, field=field_name)


def score_paper(paper_id: str, gold: list[GoldItem], preds: list[PredItem]) -> PaperResult:
    res = PaperResult(paper_id)
    for f in SCORED_FIELDS:
        gs = [g for g in gold if g.field == f]
        ps = [p for p in preds if p.field == f]
        if not gs and not ps:
            continue
        found = [any(_matches(f, p, g) for p in ps) for g in gs]
        correct = [any(_matches(f, p, g) for g in gs) for p in ps]
        res.fields[f] = FieldScore(gold=len(gs), pred=len(ps), pred_correct=sum(correct),
                                   gold_found=sum(found))  # fmt: skip
        res.missed[f] = [g for g, ok in zip(gs, found, strict=True) if not ok]
        res.wrong[f] = [p for p, ok in zip(ps, correct, strict=True) if not ok]
        if f == "hyperparameters":
            res.hp_names_gold = {hp_name(g.name) for g in gs}
            res.hp_names_found = {hp_name(g.name) for g, ok in zip(gs, found, strict=True) if ok}
            named = [p for p in ps if any(_hp_name_match(p, g) for g in gs)]
            res.hp_named = len(named)
            res.hp_named_right = sum(1 for p in named if any(_matches(f, p, g) for g in gs))
    return res


def evaluate(gold: list[GoldItem], preds: list[PredItem]) -> ExtractionReport:
    """Scores every paper that has both gold items and predictions."""
    gold_by: dict[str, list[GoldItem]] = defaultdict(list)
    for g in gold:
        gold_by[g.paper_id].append(g)
    pred_by: dict[str, list[PredItem]] = defaultdict(list)
    for p in preds:
        pred_by[p.paper_id].append(p)
    papers = sorted(set(gold_by) & set(pred_by))
    statuses: Counter[str] = Counter()
    by_field: dict[str, Counter[str]] = defaultdict(Counter)
    for pid in papers:
        for p in pred_by[pid]:
            statuses[p.status] += 1
            by_field[p.field][p.status] += 1
    return ExtractionReport(
        papers=[score_paper(pid, gold_by[pid], pred_by[pid]) for pid in papers],
        status_counts=statuses,
        status_by_field=dict(by_field),
    )
