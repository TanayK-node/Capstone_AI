from app.pipeline.compare import PaperData, build_comparison
from app.schemas.extraction import (
    Dataset,
    Evidence,
    Hyperparameter,
    Item,
    Metadata,
    PaperExtraction,
)
from app.schemas.results import ResultCell, ResultColumn, ResultRow, ResultsTable


def ev(page: int) -> list[Evidence]:
    return [Evidence(chunk_id="b1", page=page, quote="q", grounding_status="verified")]


def table(header: str, rows: list[tuple[str, float, bool]]) -> ResultsTable:
    return ResultsTable(
        table_id="t", label="Table 2", caption="Results.", page=6,
        columns=[ResultColumn(index=0, header="Model"),
                 ResultColumn(index=1, header=header, numeric=True, higher_is_better=True)],
        rows=[ResultRow(index=i, label=name, is_proposed=own,
                        cells=[ResultCell(col=1, text=str(v), value=v)])
              for i, (name, v, own) in enumerate(rows)],
    )  # fmt: skip


def paper(pid: str, datasets: list[str], lr: str, tables: list[ResultsTable]) -> PaperData:
    ex = PaperExtraction(
        metadata=Metadata(title=f"Paper {pid}", year="2020"),
        datasets=[Dataset(id=f"d{i}", value=d, name=d, evidence=ev(i + 3))
                  for i, d in enumerate(datasets)],
        metrics=[Item(id="m0", value="BLEU", evidence=ev(5))],
        hyperparameters=[Hyperparameter(id="h0", value=lr, name="learning rate", value_raw=lr,
                                        evidence=ev(4))],
    )  # fmt: skip
    return PaperData(id=pid, title="", extraction=ex, tables=tables, method=["Ours"])


def test_matrix_rows_and_shared_results() -> None:
    a = paper("a", ["WMT 2014 English-German", "CIFAR-10"], "3e-4",
              [table("BLEU EN-DE", [("Baseline", 25.0, False), ("Ours", 28.4, True),
                                    ("Ours-small", 27.0, True)])])  # fmt: skip
    b = paper("b", ["WMT 2014 English-German", "CIFAR-100"], "1e-3",
              [table("EN-DE BLEU", [("Ours", 29.1, True)])])  # fmt: skip
    comp = build_comparison([a, b])

    assert [p.title for p in comp.papers] == ["Paper a", "Paper b"]
    datasets = [r for r in comp.rows if r.group == "Datasets"]
    # Shared first; CIFAR-10 and CIFAR-100 never merge (different numbers).
    assert datasets[0].label == "WMT 2014 English-German" and datasets[0].shared
    assert datasets[0].cells[0].pages == [3] and datasets[0].cells[1].pages == [3]
    labels = {r.label: r for r in datasets}
    assert "CIFAR-10" in labels and "CIFAR-100" in labels
    assert not labels["CIFAR-10"].shared and labels["CIFAR-100"].cells[0].values == []

    lr = next(r for r in comp.rows if r.label == "learning rate")
    assert [c.values for c in lr.cells] == [["3e-4"], ["1e-3"]] and lr.shared
    assert next(r for r in comp.rows if r.group == "Metrics").shared

    # Same header words in a different order match; each paper's own best value is shown.
    [res] = comp.results
    assert [c.text for c in res.cells] == ["28.4", "29.1"]
    assert res.cells[0].method == "Ours" and res.cells[0].page == 6
    assert comp.warnings == []


def test_no_shared_results_is_a_warning() -> None:
    comp = build_comparison([paper("a", ["SQuAD"], "1e-4", []), paper("b", ["MNLI"], "1e-4", [])])
    assert comp.results == [] and comp.warnings
    assert all(not r.shared for r in comp.rows if r.group == "Datasets")
