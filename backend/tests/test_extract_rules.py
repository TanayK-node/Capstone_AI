import pytest

from app.pipeline.extract.groups import build_groups
from app.pipeline.extract.hints import find_code_urls, find_hints
from app.pipeline.extract.normalize import normalize_value, same_item
from app.schemas.document import Block, PageInfo, ParsedDocument, Sentence


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        ("3e-4", 3e-4),
        ("0.0003", 3e-4),
        ("50k", 50000.0),
        ("1M", 1e6),
        ("2 × 10^-4", 2e-4),  # noqa: RUF001
        ("256", 256.0),
        ("1,024", 1024.0),
        ("−0.5", -0.5),  # noqa: RUF001 - unicode minus on purpose
        ("{0.01, 0.03}", None),
        ("cosine", None),
    ],
)
def test_normalize_value(raw: str, value: float | None) -> None:
    got = normalize_value(raw)
    assert got == pytest.approx(value) if value is not None else got is None


@pytest.mark.parametrize(
    ("a", "b", "same"),
    [
        ("ImageNet-1k", "ImageNet 1K", True),
        ("ImageNet-1k", "ImageNet", True),
        ("Adam optimiser", "Adam optimizer", True),
        ("WMT 2014 English-German", "WMT 2014 English-French", False),
        ("CIFAR-10", "CIFAR-100", False),
        ("BLEU", "", False),
    ],
)
def test_same_item(a: str, b: str, same: bool) -> None:
    assert same_item(a, b) is same


def _block(text: str, type_: str = "paragraph", id_: str = "b0001") -> Block:
    return Block(
        id=id_,
        type=type_,
        order=0,
        page=1,
        bbox=None,
        text=text,
        sentences=[Sentence(text=text)],
    )


def test_hints_find_training_details() -> None:
    block = _block("We train with Adam using a learning rate of 3e-4 on 8 NVIDIA A100 GPUs.")
    kinds = {h.kind for h in find_hints([block])}
    assert {"learning_rate", "optimizer", "hardware"} <= kinds


def test_code_urls_skip_bibliography_and_join_broken_links() -> None:
    blocks = [
        _block("Code is at https://github.com/ example/sparseroute.", id_="b1"),
        _block("Smith. 2020. https://github.com/other/repo", type_="reference", id_="b2"),
    ]
    urls = [u for u, _, _ in find_code_urls(blocks)]
    assert urls == ["https://github.com/example/sparseroute"]


def test_groups_route_tables_and_training_details_to_experiments() -> None:
    """GROBID can drop a "Results" heading, leaving tables and setup text under "method"."""
    blocks = [
        _block("We propose a sparse router.", id_="b1"),
        _block("We train with Adam and a learning rate of 3e-4.", id_="b2"),
        _block("Table 2: BLEU on WMT.", type_="table", id_="b3"),
        _block("Smith et al. 2020. Adam, learning rate 1e-3.", id_="b4"),
    ]
    for block, role in zip(blocks, ["method", "method", "method", "references"], strict=True):
        block.role = role
    doc = ParsedDocument(
        parser="test", parser_version="0", pages=[PageInfo(number=1, width=1, height=1)],
        blocks=blocks,
    )  # fmt: skip
    groups = build_groups(doc, 10_000)
    assert [b.id for b in groups["method"].blocks] == ["b1", "b2"]
    assert [b.id for b in groups["experiments"].blocks] == ["b2", "b3"]
