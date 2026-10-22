"""Paper-code consistency (M7): scanner, comparison, discovery, locked-down clone."""

import os
from pathlib import Path

import pytest

from app.pipeline.code_check.clone import CloneError, RepoTooLargeError, clone, split_url
from app.pipeline.code_check.compare import canonical_code, canonical_paper, compare
from app.pipeline.code_check.discovery import candidates_from_paper, candidates_from_search
from app.pipeline.code_check.sandbox import run_scanner
from app.pipeline.code_check.scanner import scan
from app.schemas.code import CodeParam, RepoCandidate
from app.schemas.extraction import Evidence, Hyperparameter, Item, PaperExtraction
from tests.code_fixture import make_repo

PY = """
import argparse, click
from absl import flags
from dataclasses import dataclass, field
p = argparse.ArgumentParser()
p.add_argument("--learning_rate", "-lr", type=float, default=3e-4, help="peak lr")
p.add_argument("--data", default="/tmp/x")
flags.DEFINE_integer("train_batch_size", 4096, "batch")
@click.option("--warmup-steps", default=4000)
def main(): pass
@dataclass
class Config:
    dropout: float = 0.1
    weight_decay: float = field(default=1e-6)
hparams.label_smoothing = 0.1
hparams.add_hparam("num_heads", 8)
LEARNING_RATE = compute_lr()  # not a literal: never evaluated
open("/tmp/PAPERLENS_SCANNER_RAN", "w").write("x")
class BertConfig:
    def __init__(self, vocab_size, hidden_dropout_prob=0.1, *, seed=42): pass
def model(config, is_training):
    if not is_training:
        config.hidden_dropout_prob = 0.0  # inference only: not a hyperparameter
opt = AdamWeightDecayOptimizer(learning_rate=lr, weight_decay_rate=0.01)
"""


def test_scanner_reads_every_kind_without_executing(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    (repo / "conf").mkdir(parents=True)
    (repo / "train.py").write_text(PY)
    (repo / "old.py").write_text("print 'python 2'\n")
    (repo / "conf" / "exp.yaml").write_text("optim:\n  lr: 0.001\n  betas: [0.9, 0.98]\n")
    (repo / "README.md").write_text("```\npython train.py --epochs 90 --lr=0.1\n```\n")
    os.symlink("/etc/passwd", repo / "passwd.yaml")  # must not be followed
    out = scan(str(repo))
    found = {(p["name"], p["kind"]): p["value"] for p in out["params"]}  # type: ignore[union-attr]
    assert found[("learning_rate", "argparse")] == "0.0003"
    assert found[("train_batch_size", "flags")] == "4096"
    assert found[("warmup-steps", "click")] == "4000"
    assert found[("dropout", "constant")] == "0.1"
    assert found[("weight_decay", "constant")] == "1e-06"
    assert found[("label_smoothing", "attr")] == "0.1"
    assert found[("num_heads", "hparams")] == "8"
    assert found[("optim.lr", "config")] == "0.001"
    assert found[("epochs", "readme")] == "90" and found[("lr", "readme")] == "0.1"
    assert not any(n == "LEARNING_RATE" for n, _ in found)  # a call, not a literal
    assert found[("hidden_dropout_prob", "default")] == "0.1"  # function signature
    assert found[("seed", "default")] == "42"
    assert found[("weight_decay_rate", "kwarg")] == "0.01"  # any call's keyword
    assert ("hidden_dropout_prob", "attr") not in found  # the eval-only override is skipped
    assert not any("passwd" in str(p["file"]) for p in out["params"])  # type: ignore[union-attr]
    assert any("old.py" in e for e in out["errors"])  # type: ignore[union-attr]
    assert not Path("/tmp/PAPERLENS_SCANNER_RAN").exists()


def test_scanner_runs_in_a_separate_process(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    output, mode = run_scanner(repo, "process")
    assert mode == "process" and output["files_scanned"] >= 3
    assert not Path("/tmp/PAPERLENS_EXECUTED").exists()


# ------------------------------------------------------------------ comparison


@pytest.mark.parametrize(
    ("paper", "canon"),
    [
        ("Learning rate (peak)", "learning_rate"),
        ("batch size", "batch_size"),
        ("Adam β2", "adam_beta2"),
        ("warmup steps", "warmup_steps"),
        ("warm-up epochs", "warmup_epochs"),
        ("attention dropout", "attention_dropout"),
        ("LoRA rank r", "lora_rank"),
        ("training steps", "train_steps"),
    ],
)
def test_paper_names(paper: str, canon: str) -> None:
    assert canonical_paper(paper) == canon


def test_code_names() -> None:
    assert canonical_code("--learning_rate") == "learning_rate"
    assert canonical_code("optimizer.lr") == "learning_rate"
    assert canonical_code("per_device_train_batch_size") == "batch_size"
    assert canonical_code("data_dir") is None


def hp(name: str, raw: str, norm: float | None) -> Hyperparameter:
    ev = Evidence(chunk_id="b1", page=1, quote=f"{name} {raw}")
    return Hyperparameter(id="h", value=raw, name=name, value_raw=raw, value_norm=norm,
                          evidence=[ev])  # fmt: skip


def param(name: str, value: str, file: str = "train.py") -> CodeParam:
    return CodeParam(name=name, value=value, file=file, kind="argparse")


def test_compare_rows() -> None:
    rows = compare(
        [
            hp("learning rate", "3e-4", 3e-4),
            hp("batch size", "4096", 4096),
            hp("fine-tuning learning rates", "{5e-5, 3e-5, 2e-5}", None),
            hp("warmup ratio", "6%", None),
            hp("label smoothing", "0.1", 0.1),
        ],
        [
            param("lr", "0.0003"),
            param("lr", "0.001", "configs/old.yaml"),
            param("train_batch_size", "512"),
            param("warmup_proportion", "0.06"),
            param("weight_decay", "0.01"),
        ],
    )
    by = {(r.canonical, r.paper_value): r for r in rows}
    lr = by[("learning_rate", "3e-4")]
    assert lr.status == "match" and "configs/old.yaml" in lr.note  # other values reported
    assert by[("batch_size", "4096")].status == "mismatch"  # 512 in the code
    assert by[("learning_rate", "{5e-5, 3e-5, 2e-5}")].status == "mismatch"  # none of the set
    assert by[("warmup_ratio", "6%")].status == "match"  # 6% == 0.06
    assert by[("label_smoothing", "0.1")].status == "only_in_paper"
    assert by[("weight_decay", "")].status == "only_in_code"


# ------------------------------------------------------------------ discovery


def url_item(url: str, sentence: str) -> Item:
    return Item(id="c", value=url, source="rule",
                evidence=[Evidence(chunk_id="b1", page=1, quote=sentence)])  # fmt: skip


def test_discovery_prefers_the_authors_repo() -> None:
    ex = PaperExtraction(
        code_urls=[
            url_item("https://github.com/tensorflow/tensor2tensor",
                     "Our implementation is based on the tensor2tensor library."),
            url_item("https://github.com/google-research/bert",
                     "The code and pre-trained models are available at https://github.com/google-research/bert."),
        ]
    )  # fmt: skip
    ex.metadata.title = "BERT: Pre-training of Deep Bidirectional Transformers"
    found = candidates_from_paper(ex, ["BERT"])
    assert found[0].url.endswith("google-research/bert") and found[0].confidence == 1.0
    assert found[1].confidence < 0.6


def test_search_candidates_always_need_confirmation() -> None:
    title = "Sparse Routing Improves Low-Resource Translation"
    results = [{"full_name": "a/sparseroute", "description": title,
                "html_url": "https://github.com/a/sparseroute", "stargazers_count": 3}]  # fmt: skip
    found = candidates_from_search(results, title)
    assert found[0].confidence <= 0.5


# ------------------------------------------------------------------ clone


def test_split_url() -> None:
    hf = "https://github.com/huggingface/transformers"
    assert split_url(f"{hf}/tree/main/examples/distillation") == (hf, "examples/distillation")
    assert split_url("https://github.com/o/r.git") == ("https://github.com/o/r", None)


def test_clone_is_locked_down(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, {"a.py": "x = 1\n", "big.bin": "0" * 2_000_000})
    os.symlink("/etc/passwd", repo / "link")
    import subprocess

    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(repo),
                    "commit", "-qm", "link"], check=True)  # fmt: skip
    cand = RepoCandidate(url=f"file://{repo}", source="user", confidence=1, reason="")
    with pytest.raises(CloneError):  # local protocols are refused outside tests
        clone(cand, tmp_path / "c1")
    cloned = clone(cand, tmp_path / "c2", allow_file_protocol=True)
    assert cloned.commit and (cloned.path / "a.py").exists()
    assert not (cloned.path / "link").is_symlink()  # checked out as a plain file
    with pytest.raises(RepoTooLargeError):
        clone(cand, tmp_path / "c3", allow_file_protocol=True, max_mb=1)
    assert not (tmp_path / "c3").exists()  # too large: deleted
