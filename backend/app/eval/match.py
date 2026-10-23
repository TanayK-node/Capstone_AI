"""When does an extracted item count as a gold item? (eval/ANNOTATION_GUIDE.md, "Scoring")

Text fields: two strings match when, after normalising (case, punctuation, accents),
- they are equal, or nearly (rapidfuzz ratio >= 88: "ConvS2S" / "Conv S2S") with the same
  numbers ("CIFAR-10" never matches "CIFAR-100"), or
- the words of one are all in the other and what is left over is filler ("BLEU" / "BLEU
  score"), or the contained part is specific on its own: three or more words, two words
  with a number ("5 days", "8 GPUs"), or a model-like token ("V100", "TPUv3").
"ImageNet" does not match "ImageNet-21k": "21k" is not filler.
Metrics are names with qualifiers, so there any extra words are allowed ("accuracy" /
"logical form validation accuracy").

An extracted item that packs several ("EM and F1", "CIFAR-10/100", "GLUE (General Language
Understanding Evaluation)") is also tried part by part (task, datasets, baselines, metrics).

Hyperparameters: the names must mean the same (code_check's synonym table, else the text
rule) and the values must be equal after normalisation (3e-4 == 0.0003 == "3 x 10^-4"; "6%"
== 0.06), or match as text for non-numbers ("Adam"). A value listing several numbers
("5e-5, 4e-5, 3e-5") is right when one of them is a gold value.
"""

from __future__ import annotations

import re
import unicodedata

from rapidfuzz import fuzz

from app.pipeline.code_check.compare import canonical_paper
from app.pipeline.extract.normalize import normalize_value

FUZZY = 88.0
SPLIT_FIELDS = {"task", "datasets", "baselines", "metrics"}
# Words that may surround a name without changing what it names.
FILLER = {
    "the", "a", "an", "of", "on", "for", "and", "with", "using", "used", "standard", "in",
    "dataset", "datasets", "data", "set", "benchmark", "benchmarks", "corpus", "task", "tasks",
    "score", "scores", "metric", "metrics", "rate", "ratio", "challenge", "competition",
    "model", "models", "method", "baseline", "baselines", "system", "evaluation", "test",
    "validation", "dev", "development", "official", "full", "public", "large", "scale",
    "results", "result", "measured", "reported", "split", "splits", "classification",
    "approximately", "about", "around", "roughly", "total", "per", "all", "experiments",
    "ensemble", "single",
}  # fmt: skip
_WORD_NUMBERS = dict(
    zip(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve"], map(str, range(13)), strict=True)
)  # fmt: skip
_ZERO = {"none", "no", "zero", "not used", "disabled", "off"}
_DIGIT = re.compile(r"\d")


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"https?://(www\.)?", "", text)
    text = re.sub(r"(?<=\d)\.(?=\d)", "\x00", text)  # keep decimals: 1.1 stays one token
    text = re.sub(r"[^a-z0-9\x00%]+", " ", text).replace("\x00", ".")
    return " ".join(_WORD_NUMBERS.get(w, w) for w in text.split())


def _digits(text: str) -> list[str]:
    return re.findall(r"\d+", text)


def _specific(tokens: list[str]) -> bool:
    """Is a contained phrase specific enough to count on its own?"""
    if len(tokens) >= 3:
        return True
    if len(tokens) == 2 and any(_DIGIT.search(t) for t in tokens):
        return True
    return len(tokens) == 1 and bool(re.fullmatch(r"(?=.*[a-z])(?=.*\d)[a-z0-9.]{3,}", tokens[0]))


def text_match(a: str, b: str, *, qualifiers: bool = False) -> bool:
    """a = extracted, b = gold. `qualifiers`: extra words are allowed around the gold name
    in the extracted text ("validation accuracy" for "accuracy"), not the other way round."""
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return False
    ta, tb = na.split(), nb.split()
    if na == nb or (fuzz.ratio(na, nb) >= FUZZY and _digits(na) == _digits(nb)):
        return True
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if not set(short) <= set(long_):
        return False
    rest = [w for w in long_ if w not in set(short)]
    gold_inside = short is tb
    # A specific phrase counts when the gold is inside the extracted text; an extracted
    # phrase inside a longer gold name is less specific than it ("top-5 error" is not
    # "top-5 localisation error").
    return (gold_inside and (qualifiers or _specific(short))) or all(w in FILLER for w in rest)


def parts(value: str) -> list[str]:
    """'EM and F1' -> [..., 'EM', 'F1']; 'CIFAR-10/100' -> [..., 'CIFAR-10', 'CIFAR-100'];
    'General Language Understanding Evaluation (GLUE)' -> [..., 'General ...', 'GLUE']."""
    out = [value]
    if m := re.fullmatch(r"\s*(.+?)\s*\(([^()]+)\)\s*", value):
        out += [m.group(1), m.group(2)]
    out += [p for p in re.split(r",\s*|;\s*|\s+(?:and|or|plus)\s+", value) if p.strip()]
    if m := re.search(r"([A-Za-z][\w ]*?)[- ](\d+)/(\d+)\b", value):
        out += [f"{m.group(1)}-{m.group(2)}", f"{m.group(1)}-{m.group(3)}"]
    return list(dict.fromkeys(p.strip() for p in out if p.strip()))


def any_match(pred: str, names: list[str], *, field: str = "") -> bool:
    cands = parts(pred) if field in SPLIT_FIELDS else [pred]
    q = field == "metrics"
    return any(text_match(c, n, qualifiers=q) for c in cands for n in names if n)


def url_key(url: str) -> str:
    u = re.sub(r"^https?://(www\.)?", "", url.strip().lower()).rstrip("/")
    return u.removesuffix(".git")


def hp_name(name: str) -> str:
    """Canonical hyperparameter name: the synonym table's, else the normalised words."""
    return canonical_paper(name) or norm(name).replace(" ", "_")


def hp_names(name: str) -> set[str]:
    """Every canonical name a compound like 'epochs_steps' or 'warmup / decay' may mean."""
    words = [w for w in re.split(r"[_\s/,]+", name) if w]
    return {hp_name(name)} | {c for w in words if (c := canonical_paper(w))}


_TIMES10 = re.compile(r"(\d+(?:\.\d+)?)\s*[×x·•*]\s*10\s*\^?\s*([-−]?\d+)")
_NUM = re.compile(
    r"10\s*\^?\s*[-−]\d+|[-+−]?\d[\d,]*(?:\.\d+)?(?:[eE][-+−]?\d+)?(?:\s*[kKmMbB]\b)?%?"
)


def numbers(text: str) -> list[float]:
    """Every number in a value: '5 • 10 -4' -> [5e-4]; '5e-5, 4e-5' -> [5e-5, 4e-5];
    '6%' -> [6.0, 0.06]; '80 sentences' -> [80.0]."""
    if norm(text) in _ZERO:
        return [0.0]
    t = _TIMES10.sub(lambda m: f"{m.group(1)}e{m.group(2).replace('−', '-')}", text)
    whole = normalize_value(t)
    found = [t] if whole is not None else _NUM.findall(t)
    out: list[float] = []
    for raw in found:
        v = normalize_value(raw.replace(" ", "").rstrip("%"))
        if v is None:
            continue
        out.append(v)
        if raw.strip().endswith("%"):
            out.append(v / 100)
    return out


def value_match(pred: str, gold: list[str]) -> bool:
    pv = numbers(pred)
    for g in gold:
        gv = numbers(g)
        if pv and gv:
            if any(abs(p - x) <= 1e-9 * max(1.0, abs(x)) for p in pv for x in gv):
                return True
        elif not pv and not gv and text_match(pred, g):
            return True
    return False
