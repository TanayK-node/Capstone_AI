"""Equations and macros from an arXiv LaTeX source (M10).

The e-print is untrusted input: it is read in memory (never extracted to disk), only regular
.tex members are read, with size caps. Nothing is compiled or executed; this is text parsing.

Numbering follows LaTeX: equation / gather / multline / eqnarray / align number each
equation or row unless starred or marked \\nonumber / \\notag; \\tag{x} sets the number.
Appendix numbering schemes (A.1) and custom counters are not followed: such equations keep
their LaTeX but may not be matched to the PDF.
"""

from __future__ import annotations

import gzip
import io
import re
import tarfile
from dataclasses import dataclass

MAX_MEMBER = 2_000_000
MAX_TOTAL = 20_000_000
NUMBERED = {"equation", "gather", "multline", "eqnarray", "align", "alignat", "flalign"}
UNNUMBERED = {"displaymath"}
MULTI_ROW = {"gather", "eqnarray", "align", "alignat", "flalign"}
_ENV = re.compile(
    r"\\begin\{(equation|gather|multline|eqnarray|align|alignat|flalign|displaymath)(\*?)\}"
    r"(?:\{\d+\})?(.*?)\\end\{\1\2\}",
    re.S,
)
_DISPLAY = re.compile(r"\\\[(.*?)\\\]|\$\$(.*?)\$\$", re.S)
_INPUT = re.compile(r"\\(?:input|include)\{([^}]+)\}")
_LABEL = re.compile(r"\\label\{[^}]*\}")
_TAG = re.compile(r"\\tag\*?\{([^}]*)\}")


@dataclass
class LatexEquation:
    latex: str
    number: str | None  # "3" or the \tag text


def read_sources(blob: bytes) -> dict[str, str]:
    """name -> text of every .tex file in an arXiv e-print (tar.gz, or a single gzipped .tex)."""
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:*") as tar:
            out: dict[str, str] = {}
            total = 0
            for member in tar.getmembers():
                if not member.isfile() or not member.name.endswith(".tex"):
                    continue
                if member.size > MAX_MEMBER or total + member.size > MAX_TOTAL:
                    continue
                f = tar.extractfile(member)
                if f is None:
                    continue
                total += member.size
                out[member.name] = f.read().decode("utf-8", errors="replace")
            return out
    except tarfile.TarError:
        pass
    try:  # a single-file submission is just a gzipped .tex
        text = gzip.decompress(blob)[:MAX_MEMBER].decode("utf-8", errors="replace")
    except (OSError, EOFError):
        return {}
    return {"main.tex": text} if "\\begin{document}" in text else {}


def strip_comments(text: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", text)


def flatten(files: dict[str, str]) -> str:
    """The main file with \\input / \\include replaced by the files they name.
    Submissions often carry a template or sample paper too (iclr2015.tex next to the paper):
    of the files with \\documentclass, the longest after expansion is the paper."""
    mains = [n for n, t in files.items() if "\\documentclass" in strip_comments(t)]
    with_body = [n for n in mains if "\\begin{document}" in files[n]]
    return max((_expand(files, n) for n in with_body or mains), key=len, default="")


def _expand(files: dict[str, str], main: str) -> str:
    by_stem = {n.removesuffix(".tex"): n for n in files}
    seen: set[str] = set()

    def expand(name: str, depth: int) -> str:
        if depth > 8 or name in seen:
            return ""
        seen.add(name)
        text = strip_comments(files[name])

        def sub(m: re.Match[str]) -> str:
            ref = m.group(1).strip().removesuffix(".tex").lstrip("./")
            target = by_stem.get(ref) or next(
                (n for s, n in by_stem.items() if s.endswith("/" + ref)), None
            )
            return expand(target, depth + 1) if target else ""

        return _INPUT.sub(sub, text)

    return expand(main, 0)


def _braced(text: str, start: int) -> tuple[str, int] | None:
    """The {...} group starting at text[start] == "{", and the index after it."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{" and text[i - 1 : i] != "\\":
            depth += 1
        elif text[i] == "}" and text[i - 1 : i] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
    return None


def macros(text: str) -> dict[str, str]:
    """\\newcommand / \\renewcommand / \\def / \\DeclareMathOperator -> KaTeX macros.
    Macros with arguments keep their #1 placeholders, which KaTeX understands."""
    out: dict[str, str] = {}
    for m in re.finditer(
        r"\\(?:re)?newcommand\*?\s*\{?\s*(\\[A-Za-z]+)\s*\}?\s*(?:\[\d\])?\s*", text
    ):
        body = _braced(text, m.end())
        if body:
            out[m.group(1)] = body[0]
    for m in re.finditer(r"\\def\s*(\\[A-Za-z]+)\s*(?:#\d)*\s*", text):
        body = _braced(text, m.end())
        if body:
            out.setdefault(m.group(1), body[0])
    for m in re.finditer(r"\\DeclareMathOperator\*?\s*\{\s*(\\[A-Za-z]+)\s*\}\s*", text):
        body = _braced(text, m.end())
        if body:
            out[m.group(1)] = f"\\operatorname{{{body[0]}}}"
    return {k: v for k, v in out.items() if len(v) < 500}


_ENV_ALIAS = re.compile(r"\s*\\(?:begin|end)\{[A-Za-z]+\*?\}\s*")


def expand_env_aliases(text: str) -> str:
    """Shorthands like \\newcommand{\\beq}{\\begin{equation}} replaced by what they stand for,
    so the equations written with them are found."""
    for name, body in macros(text).items():
        if _ENV_ALIAS.fullmatch(body):
            env = body.strip()
            text = re.sub(re.escape(name) + r"(?![A-Za-z])", lambda _m: env, text)  # noqa: B023
    return text


def equations(text: str) -> list[LatexEquation]:
    """Display equations in document order, with the numbers LaTeX would print."""
    body = expand_env_aliases(text).split("\\begin{document}", 1)[-1]
    found: list[tuple[int, LatexEquation]] = []
    counter = 0
    covered: list[tuple[int, int]] = []
    for m in _ENV.finditer(body):
        env, star, inner = m.group(1), m.group(2), m.group(3)
        covered.append((m.start(), m.end()))
        inner = _LABEL.sub("", inner).strip()
        numbered = env in NUMBERED and not star
        if env in MULTI_ROW:
            rows = [r for r in re.split(r"\\\\(?:\[[^\]]*\])?", inner) if r.strip()]
            numbers: list[str] = []
            for row in rows:
                tag = _TAG.search(row)
                if tag:
                    numbers.append(tag.group(1))
                elif numbered and not re.search(r"\\no(number|tag)\b", row):
                    counter += 1
                    numbers.append(str(counter))
            clean = re.sub(r"\\no(number|tag)\b|\\tag\*?\{[^}]*\}", "", inner)
            env_name = (
                "aligned" if env in ("align", "alignat", "flalign", "eqnarray") else "gathered"
            )
            latex = f"\\begin{{{env_name}}}{clean}\\end{{{env_name}}}"
            found.append((m.start(), LatexEquation(latex, ", ".join(numbers) or None)))
        else:
            tag = _TAG.search(inner)
            number: str | None = None
            if tag:
                number = tag.group(1)
            elif numbered and not re.search(r"\\no(number|tag)\b", inner):
                counter += 1
                number = str(counter)
            clean = re.sub(r"\\no(number|tag)\b|\\tag\*?\{[^}]*\}", "", inner).strip()
            if env == "multline":
                clean = clean.replace("\\\\", "\\\\ ")
            found.append((m.start(), LatexEquation(clean, number)))
    for m in _DISPLAY.finditer(body):
        if any(a <= m.start() < b for a, b in covered):
            continue
        inner = (m.group(1) or m.group(2) or "").strip()
        if inner:
            found.append((m.start(), LatexEquation(_LABEL.sub("", inner), None)))
    found.sort(key=lambda x: x[0])
    return [eq for _, eq in found]
