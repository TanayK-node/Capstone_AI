"""Deterministic checklist rules (M6 rule layer, SCOPE.md F5).

A rule either decides an item, with the sentence(s) that show it, or returns "inconclusive"
and the item goes to the LLM. Rules prefer "inconclusive" over "missing" when the absence of
a regex hit proves little (a paper can describe its hardware without naming a GPU model).
Rules named in config/checklist.yaml must exist in RULES (checked by a test).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Literal

from app.pipeline.extract.hints import Hint, find_hints
from app.schemas.document import Block, ParsedDocument
from app.schemas.extraction import Evidence, Item, PaperExtraction
from app.schemas.repro import ItemSource, RepoInfo

RuleStatus = Literal["present", "partial", "missing", "unknown", "inconclusive"]


@dataclass
class RuleContext:
    doc: ParsedDocument
    extraction: PaperExtraction
    repo: RepoInfo | None
    hints: list[Hint] = field(default_factory=list)  # over the whole paper, references excluded

    @classmethod
    def build(
        cls, doc: ParsedDocument, extraction: PaperExtraction, repo: RepoInfo | None
    ) -> RuleContext:
        body = [b for b in doc.blocks if (b.role or "") not in ("references",)]
        return cls(doc, extraction, repo, find_hints(body, limit_per_kind=50))

    def page_of(self, block_id: str) -> int:
        return next((b.page for b in self.doc.blocks if b.id == block_id), 1)

    def role_of(self, block_id: str) -> str:
        return next((b.role or "" for b in self.doc.blocks if b.id == block_id), "")


@dataclass
class RuleResult:
    status: RuleStatus
    note: str = ""
    evidence: list[Evidence] = field(default_factory=list)
    source: ItemSource = "rule"


INCONCLUSIVE = RuleResult("inconclusive")

# ------------------------------------------------------------------ helpers


def _hint_evidence(ctx: RuleContext, hints: list[Hint], limit: int = 2) -> list[Evidence]:
    out: list[Evidence] = []
    for h in hints:
        if any(e.quote == h.sentence for e in out):
            continue
        out.append(Evidence(chunk_id=h.block_id, page=ctx.page_of(h.block_id), quote=h.sentence))
        if len(out) == limit:
            break
    return out


def _item_evidence(items: Sequence[Item], limit: int = 2) -> list[Evidence]:
    """Copies of evidence the verify stage already confirmed (verified / partial)."""
    good = [
        e.model_copy(deep=True)
        for i in items
        for e in i.evidence
        if e.grounding_status in ("verified", "partial")
    ]
    return good[:limit]


# Evidence from the setup sections reads better than a passing mention in the abstract
# ("Compared to GPT-3 fine-tuned with Adam, ..."); sentences about training come first.
_ROLE_RANK = {"experiments": 0, "appendix": 0, "results": 1, "ablation": 1, "method": 2}
_TRAINING_WORDS = re.compile(r"\b(train|trained|training|experiments?)\b", re.I)


def _kind(ctx: RuleContext, kind: str) -> list[Hint]:
    hits = [h for h in ctx.hints if h.kind == kind]
    return sorted(
        hits,
        key=lambda h: (
            not _TRAINING_WORDS.search(h.sentence),
            _ROLE_RANK.get(ctx.role_of(h.block_id), 3),
        ),
    )


# ------------------------------------------------------------------ code


def code_url_present(ctx: RuleContext) -> RuleResult:
    urls = ctx.extraction.code_urls
    if not urls:
        return RuleResult(
            "missing", "No repository link (GitHub, GitLab, Hugging Face) in the text."
        )
    return RuleResult("present", urls[0].value, _item_evidence(urls) or list(urls[0].evidence))


def _repo_state(ctx: RuleContext) -> RuleResult | None:
    """Shared outcome for repo_* rules when there is no repository to look at."""
    repo = ctx.repo
    if repo is None:
        return RuleResult("missing", "No repository is linked from the paper.", source="repo")
    if repo.reachable is None:
        # The reason (e.g. GitHub API rate limit) is shown once with the repository.
        return RuleResult(
            "unknown", "Repository not checked (see the repository line).", source="repo"
        )
    if repo.reachable is False:
        return RuleResult("missing", repo.error or "Repository not reachable.", source="repo")
    return None


def repo_reachable(ctx: RuleContext) -> RuleResult:
    if (state := _repo_state(ctx)) is not None:
        return state
    assert ctx.repo is not None
    r = ctx.repo
    facts = [f"github.com/{r.owner}/{r.name}"]
    if r.stars is not None:
        facts.append(f"{r.stars} stars")
    if r.pushed_at:
        facts.append(f"last push {r.pushed_at[:10]}")
    if r.archived:
        facts.append("archived")
    return RuleResult("present", " · ".join(facts), source="repo")


def repo_license(ctx: RuleContext) -> RuleResult:
    if (state := _repo_state(ctx)) is not None:
        return state
    assert ctx.repo is not None
    if ctx.repo.license:
        return RuleResult("present", f"License: {ctx.repo.license}", source="repo")
    return RuleResult("missing", "GitHub reports no license for the repository.", source="repo")


DEPENDENCY_FILES = re.compile(
    r"^(requirements.*\.txt|environment\.ya?ml|conda.*\.ya?ml|pyproject\.toml|setup\.py|"
    r"setup\.cfg|Pipfile(\.lock)?|poetry\.lock|Dockerfile|docker-compose\.ya?ml|"
    r"package\.json|Cargo\.toml|DESCRIPTION)$",
    re.I,
)


def repo_dependency_file(ctx: RuleContext) -> RuleResult:
    if (state := _repo_state(ctx)) is not None:
        return state
    assert ctx.repo is not None
    found = [f for f in ctx.repo.root_files if DEPENDENCY_FILES.match(f)]
    if found:
        return RuleResult("present", "Found: " + ", ".join(found), source="repo")
    if re.search(r"pip install|conda (env )?create|conda install", ctx.repo.readme_excerpt):
        return RuleResult(
            "partial", "README lists install commands, no dependency file.", source="repo"
        )
    return RuleResult("missing", "No dependency file in the repository root.", source="repo")


_TRAIN_CMD = re.compile(
    r"(python3?|bash|sh|torchrun|accelerate launch|deepspeed|fairseq-train|make)\s+[^\n]*"
    r"(train|finetun|fine-tun|pretrain|run_|main)",
    re.I,
)
_EVAL_CMD = re.compile(
    r"(python3?|bash|sh|torchrun|accelerate launch|fairseq-generate|make)\s+[^\n]*"
    r"(eval|test|infer|predict|generate|validat)",
    re.I,
)
_HEADING = re.compile(r"^#+\s*(.+)$", re.M)


def repo_run_instructions(ctx: RuleContext) -> RuleResult:
    if (state := _repo_state(ctx)) is not None:
        return state
    assert ctx.repo is not None
    readme = ctx.repo.readme_excerpt
    if not readme.strip():
        return RuleResult("missing", "The repository has no README.", source="repo")
    headings = " ".join(_HEADING.findall(readme)).lower()
    train = bool(_TRAIN_CMD.search(readme)) or "train" in headings
    evaluate = bool(_EVAL_CMD.search(readme)) or bool(re.search(r"eval|test|infer", headings))
    if train and evaluate:
        return RuleResult(
            "present", "README shows training and evaluation commands.", source="repo"
        )
    if train or evaluate:
        which = "training" if train else "evaluation"
        return RuleResult("partial", f"README covers {which} only.", source="repo")
    return RuleResult("missing", "README has no training or evaluation commands.", source="repo")


_WEIGHTS = re.compile(
    r"checkpoints?|pre-?trained (models?|weights)|model weights|download (the )?(models?|weights)|"
    r"huggingface\.co/|model zoo|\.pth\b|\.ckpt\b|\.safetensors\b|release[ds]? .{0,30}weights",
    re.I,
)


def repo_weights(ctx: RuleContext) -> RuleResult:
    """Weights mentioned in the README decide it; otherwise the paper text may say
    "we release our models", which the LLM checks."""
    if ctx.repo and ctx.repo.reachable and (m := _WEIGHTS.search(ctx.repo.readme_excerpt)):
        return RuleResult("present", f"README mentions “{m.group(0)}”.", source="repo")
    return INCONCLUSIVE


# ------------------------------------------------------------------ data

KNOWN_PUBLIC = re.compile(
    r"ImageNet|CIFAR|MNIST|COCO|Pascal VOC|VOC ?20\d\d|WMT|GLUE|SuperGLUE|SQuAD|RACE|"
    r"Wikipedia|BooksCorpus|BookCorpus|Common ?Crawl|C4|OpenWebText|Penn Treebank|PTB|"
    r"WikiText|LibriSpeech|IWSLT|MultiNLI|MNLI|SNLI|SST|CoLA|QQP|MRPC|STS-B|QNLI|RTE|WNLI|"
    r"Oxford|Flowers|Food-?101|SVHN|STL-?10|Places|Kinetics|FLORES|WikiSQL|SAMSum|E2E|DART|"
    r"WebNLG|CNN/?Daily ?Mail|XSum|JFT",
    re.I,
)


def dataset_links(ctx: RuleContext) -> RuleResult:
    datasets = ctx.extraction.datasets
    public = [d for d in datasets if d.public == "yes" or KNOWN_PUBLIC.search(d.name or d.value)]
    if datasets and len(public) == len(datasets):
        names = ", ".join(d.name or d.value for d in public[:6])
        return RuleResult(
            "present", f"Public datasets: {names}", _item_evidence(public), "extraction"
        )
    return INCONCLUSIVE  # private data may still be described; the LLM reads the text


# ------------------------------------------------------------------ setup / compute / stats


def training_terms(ctx: RuleContext) -> RuleResult:
    opt, lr, steps = (_kind(ctx, k) for k in ("optimizer", "learning_rate", "epochs_steps"))
    if opt and lr and steps:
        ev = _hint_evidence(ctx, [opt[0], lr[0], steps[0]], limit=3)
        return RuleResult("present", "Optimizer, learning rate and epochs/steps are stated.", ev)
    return INCONCLUSIVE


_DEVICE_MODEL = re.compile(
    r"\b(A100|H100|V100|P100|K80|T4|A6000|A40|L4|RTX\s?\d{4}|GTX\s?\d{3,4}|Titan\s?\w+|"
    r"TPU\s?v?\d|TPUv\d|Cloud TPU)\b",
    re.I,
)


def gpu_models(ctx: RuleContext) -> RuleResult:
    hits = [h for h in _kind(ctx, "hardware") if _DEVICE_MODEL.search(h.sentence)]
    if hits:
        return RuleResult("present", "A GPU/TPU model is named.", _hint_evidence(ctx, hits))
    return INCONCLUSIVE  # "trained on 8 GPUs" names no model; the LLM judges partial/missing


_TRAINING_CONTEXT = re.compile(r"train|GPU|TPU|pre-?train|fine-?tun|took|takes", re.I)


def compute_hours(ctx: RuleContext) -> RuleResult:
    hits = [h for h in _kind(ctx, "compute_time") if _TRAINING_CONTEXT.search(h.sentence)]
    if hits:
        return RuleResult("present", "Training time is reported.", _hint_evidence(ctx, hits))
    return INCONCLUSIVE


_SEEDS = re.compile(
    r"random seeds?|\b\d+ (different |random |independent )?(seeds|runs|trials)\b|"
    r"averaged? over \d+|(mean|median) (of|over) \d+|\bseeds?\b",
    re.I,
)


def seed_terms(ctx: RuleContext) -> RuleResult:
    hits = [h for h in _kind(ctx, "seeds_runs") if _SEEDS.search(h.sentence)]
    # A sentence about seeds beats "latency averaged over 100 trials" (LoRA, Table 1).
    hits.sort(key=lambda h: "seed" not in h.sentence.lower())
    if hits:
        return RuleResult(
            "present", "Number of runs or seeds is mentioned.", _hint_evidence(ctx, hits)
        )
    return INCONCLUSIVE


_SPREAD_TEXT = re.compile(
    r"standard deviation|std\.?\b|confidence interval|error bars?|standard error|"
    r"±\s?\d|\+/-",  # not "variance over": "BN mean and variance over all devices" (SimCLR)
    re.I,
)


def error_bars(ctx: RuleContext) -> RuleResult:
    for block in ctx.doc.tables:
        cells = block.table.cells if block.table else []
        if any(c.std is not None for c in cells) or "±" in block.text:
            quote = block.text.split(". ")[0][:300] or block.label or block.id
            ev = Evidence(chunk_id=block.id, page=block.page, quote=quote)
            return RuleResult("present", f"{block.label or 'A table'} reports ± spreads.", [ev])
    body = [b for b in ctx.doc.blocks if b.type in ("paragraph", "caption", "footnote")]
    for block in body:
        if (block.role or "") == "references":
            continue
        if m := _SPREAD_TEXT.search(block.text):
            sentence = _sentence_around(block, m.start())
            ev = Evidence(chunk_id=block.id, page=block.page, quote=sentence)
            return RuleResult("present", "Spread (std / CI / error bars) is reported.", [ev])
    return INCONCLUSIVE


def _sentence_around(block: Block, pos: int) -> str:
    dot = block.text.rfind(". ", 0, pos)
    start = dot + 2 if dot != -1 else 0
    end = block.text.find(". ", pos)
    return block.text[start : end + 1 if end != -1 else len(block.text)].strip()[:400]


RULES: dict[str, Callable[[RuleContext], RuleResult]] = {
    "code_url_present": code_url_present,
    "repo_reachable": repo_reachable,
    "repo_license": repo_license,
    "repo_dependency_file": repo_dependency_file,
    "repo_run_instructions": repo_run_instructions,
    "repo_weights": repo_weights,
    "dataset_links": dataset_links,
    "training_terms": training_terms,
    "gpu_models": gpu_models,
    "compute_hours": compute_hours,
    "seed_terms": seed_terms,
    "error_bars": error_bars,
}
