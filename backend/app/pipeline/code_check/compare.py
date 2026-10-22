"""Paper vs code hyperparameters (M7 comparison). Names through a synonym table, values in
Python (CLAUDE.md rule 4).

Rows:
  match          a code value equals a value the paper states (any file, any setting)
  mismatch       the code sets this hyperparameter, and none of its values is the paper's
  only_in_paper  the paper states it; the scan found no value in the code
  only_in_code   a well-known hyperparameter the code sets but the paper does not state

A repository often holds several settings (defaults, per-task configs, README commands), so
"match" means the paper's value appears somewhere; values that differ elsewhere are listed in
the row's note, because a default that disagrees with the paper is worth knowing about.
"""

from __future__ import annotations

import math
import re

from app.pipeline.extract.normalize import normalize_value
from app.schemas.code import CodeParam, Comparison
from app.schemas.extraction import Hyperparameter

# canonical -> names seen in papers and code (lower case, "_" for separators)
SYNONYMS: dict[str, list[str]] = {
    "learning_rate": ["lr", "learning_rate", "learningrate", "base_lr", "init_lr",
                      "initial_learning_rate", "max_lr", "peak_lr", "peak_learning_rate"],
    "batch_size": ["batch_size", "bs", "train_batch_size", "per_device_train_batch_size",
                   "mini_batch_size", "minibatch_size", "global_batch_size", "total_batch_size",
                   "batch"],
    "epochs": ["epochs", "num_epochs", "num_train_epochs", "max_epochs", "n_epochs",
               "train_epochs", "epoch", "training_epochs"],
    "train_steps": ["steps", "num_train_steps", "max_steps", "train_steps", "total_steps",
                    "num_steps", "training_steps", "max_update", "max_updates",
                    "num_iterations", "iterations", "max_iter", "train_iters"],
    "warmup_steps": ["warmup", "warmup_steps", "num_warmup_steps", "warmup_updates",
                     "warmup_iters", "learning_rate_warmup_steps"],
    "warmup_epochs": ["warmup_epochs", "warmup_epoch"],  # not steps: different units
    "warmup_ratio": ["warmup_ratio", "warmup_proportion", "warmup_fraction"],
    "weight_decay": ["weight_decay", "wd", "l2", "l2_reg", "weight_decay_rate"],
    "dropout": ["dropout", "dropout_rate", "hidden_dropout_prob", "dropout_prob", "drop_rate",
                "residual_dropout", "layer_prepostprocess_dropout", "p_dropout",
                "hidden_dropout"],
    "attention_dropout": ["attention_dropout", "attention_probs_dropout_prob", "attn_dropout"],
    "label_smoothing": ["label_smoothing", "label_smoothing_factor"],
    "seed": ["seed", "random_seed"],
    "momentum": ["momentum"],
    "adam_beta1": ["beta1", "adam_beta1", "optimizer_adam_beta1"],
    "adam_beta2": ["beta2", "adam_beta2", "optimizer_adam_beta2"],
    "adam_epsilon": ["eps", "epsilon", "adam_epsilon", "adam_eps", "optimizer_adam_epsilon"],
    "max_seq_length": ["max_seq_length", "max_seq_len", "max_length", "seq_len",
                       "sequence_length", "max_source_positions"],
    "hidden_size": ["hidden_size", "d_model", "hidden_dim", "model_dim", "embed_dim",
                    "encoder_embed_dim"],
    "num_layers": ["num_layers", "n_layers", "num_hidden_layers", "num_encoder_layers",
                   "encoder_layers"],
    "num_heads": ["num_heads", "n_heads", "num_attention_heads", "encoder_attention_heads"],
    "ffn_size": ["filter_size", "ffn_dim", "intermediate_size", "d_ff", "encoder_ffn_embed_dim"],
    "lora_rank": ["lora_r", "lora_rank", "lora_dim"],
    "lora_alpha": ["lora_alpha"],
    "temperature": ["temperature", "tau", "temp"],
    "max_grad_norm": ["max_grad_norm", "clip_norm", "grad_clip", "clip_grad",
                      "gradient_clip_val", "clip_grad_norm"],
    "grad_accumulation": ["gradient_accumulation_steps", "grad_accum", "update_freq",
                          "accumulate_grad_batches"],
}  # fmt: skip
_LOOKUP = {name: canon for canon, names in SYNONYMS.items() for name in names}
# Words in a paper's hyperparameter name -> canonical, when the name is not in the table.
_WORDS: list[tuple[str, str]] = [
    (r"attention.*dropout|dropout.*attention", "attention_dropout"),
    (r"warm-?up.*(ratio|proportion|fraction|%)", "warmup_ratio"),
    (r"warm-?up.*epoch", "warmup_epochs"),
    (r"warm-?up", "warmup_steps"),
    (r"learning[ _-]?rate|\blr\b", "learning_rate"),
    (r"batch", "batch_size"),
    (r"epoch", "epochs"),
    (r"\b(steps?|iterations?|updates?)\b", "train_steps"),
    (r"weight[ _-]?decay|\bl2\b", "weight_decay"),
    (r"label[ _-]?smoothing", "label_smoothing"),
    (r"dropout", "dropout"),
    (r"\bseeds?\b", "seed"),
    (r"momentum", "momentum"),
    (r"β ?1|beta ?1", "adam_beta1"),
    (r"β ?2|beta ?2", "adam_beta2"),
    (r"ε|epsilon", "adam_epsilon"),
    (r"(max(imum)?|sequence)[ _-]?(seq(uence)?)?[ _-]?length", "max_seq_length"),
    (r"temperature|\bτ\b", "temperature"),
    (r"\brank\b|\br\b", "lora_rank"),
    (r"\balpha\b|α", "lora_alpha"),
    (r"grad(ient)?[ _-]?(clip|norm)", "max_grad_norm"),
    (r"hidden (size|dim)|d_?model", "hidden_size"),
    (r"(number of )?layers", "num_layers"),
    (r"(attention )?heads", "num_heads"),
]
_NUMBERS = re.compile(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?(?:\s*[kKmM]\b)?")


def canonical_code(name: str) -> str | None:
    """'--learning_rate' / 'optimizer.lr' / 'hparams.LR' -> 'learning_rate'."""
    key = re.sub(r"[^a-z0-9]+", "_", name.lower().split(".")[-1].split("/")[-1]).strip("_")
    return _LOOKUP.get(key)


def canonical_paper(name: str) -> str | None:
    key = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if key in _LOOKUP:
        return _LOOKUP[key]
    low = name.lower()
    return next((canon for pattern, canon in _WORDS if re.search(pattern, low)), None)


def code_number(value: str) -> float | None:
    v = value.strip().strip("'\"")
    if v.lower() in ("true", "false", "none", ""):
        return None
    return normalize_value(v)


def paper_numbers(hp: Hyperparameter) -> list[float]:
    """The single normalised value, or every number in a range / set as written
    ("{5e-5, 3e-5, 2e-5}", "4.8 (= 0.3 x BatchSize/256)"); a percent also as a fraction."""
    if hp.value_norm is not None:
        values = [hp.value_norm]
    else:
        values = [
            v for m in _NUMBERS.findall(hp.value_raw) if (v := normalize_value(m)) is not None
        ]
    if "%" in hp.value_raw:
        values += [v / 100 for v in values]
    return values


def equal(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-12)


def compare(hyperparameters: list[Hyperparameter], params: list[CodeParam]) -> list[Comparison]:
    by_canon: dict[str, list[CodeParam]] = {}
    for p in params:
        p.canonical = p.canonical or canonical_code(p.name)
        if p.canonical:
            p.value_norm = code_number(p.value)
            by_canon.setdefault(p.canonical, []).append(p)

    rows: list[Comparison] = []
    seen: set[str] = set()
    for hp in hyperparameters:
        canon = canonical_paper(hp.name or hp.value)
        if canon is None:
            continue
        seen.add(canon)
        code = by_canon.get(canon, [])
        wanted = paper_numbers(hp)
        row = Comparison(canonical=canon, status="only_in_paper", paper_name=hp.name,
                         paper_value=hp.value_raw or hp.value, paper_scope=hp.scope,
                         paper_evidence=hp.evidence)  # fmt: skip
        numeric = [p for p in code if p.value_norm is not None]
        if not code:
            row.note = "No value for this hyperparameter was found in the code."
        elif not wanted or not numeric:
            row.status = "match" if _same_text(hp.value_raw, code) else "mismatch"
            row.code_values = code[:6]
            row.note = "Compared as text."
        else:
            hits = [p for p in numeric if any(equal(p.value_norm, w) for w in wanted)]  # type: ignore[arg-type]
            others = [p for p in numeric if p not in hits]
            if hits:
                row.status = "match"
                row.code_values = (hits + others)[:6]
                if others:
                    row.note = "Other values in the code: " + ", ".join(
                        sorted({f"{p.value} ({p.file})" for p in others})[:4]
                    )
            else:
                row.status = "mismatch"
                row.code_values = numeric[:6]
                row.note = (
                    "No value in the code equals the paper's " + (hp.value_raw or "value") + "."
                )
        rows.append(row)

    for canon, code in sorted(by_canon.items()):
        if canon in seen:
            continue
        rows.append(
            Comparison(
                canonical=canon,
                status="only_in_code",
                code_values=code[:6],
                note="Set in the code, not stated in the paper.",
            )
        )
    return rows


def _same_text(raw: str, code: list[CodeParam]) -> bool:
    want = re.sub(r"\W+", "", raw.lower())
    return bool(want) and any(re.sub(r"\W+", "", p.value.lower()) == want for p in code)
