"""Equations from LaTeX sources and the notation glossary (M10)."""

import gzip
import io
import random
import tarfile

from app.config import Settings
from app.llm.cache import MemoryCache
from app.llm.client import LLMClient
from app.pipeline.math.glossary import build_report
from app.pipeline.math.latex import equations, flatten, macros, read_sources
from tests.conftest import FakeClock
from tests.fake_llm import FakePaperProvider
from tests.test_extraction import PDF, fixture_doc

MAIN = r"""
\documentclass{article}
\newcommand{\R}{\mathbb{R}}
\newcommand{\norm}[1]{\lVert #1 \rVert}
\DeclareMathOperator{\softmax}{softmax}
\begin{document}
% \begin{equation} commented out \end{equation}
\input{method}
\begin{equation*} x = 1 \end{equation*}
$$ y = 2 $$
\end{document}
"""
METHOD = r"""
\begin{equation}\label{eq:att}
\mathrm{Attention}(Q, K, V) = \softmax(QK^T / \sqrt{d_k}) V
\end{equation}
\begin{align}
a &= b + c \\
d &= e \nonumber \\
f &= \norm{g} \tag{*}
\end{align}
\begin{equation} h = 4 \end{equation}
"""


def tarball(files: dict[str, str], extra: list[tarfile.TarInfo] | None = None) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        for info in extra or []:
            tar.addfile(info)
    return buf.getvalue()


def test_numbering_follows_latex() -> None:
    blob = tarball({"main.tex": MAIN, "sections/method.tex": METHOD})
    text = flatten(read_sources(blob))
    eqs = equations(text)
    assert [e.number for e in eqs] == ["1", "2, *", "3", None, None]
    assert eqs[0].latex.startswith(r"\mathrm{Attention}") and "\\label" not in eqs[0].latex
    assert eqs[1].latex.startswith(r"\begin{aligned}") and "\\nonumber" not in eqs[1].latex
    assert "commented out" not in text


def test_macros_for_katex() -> None:
    m = macros(MAIN)
    assert m[r"\R"] == r"\mathbb{R}"
    assert m[r"\norm"] == r"\lVert #1 \rVert"
    assert m[r"\softmax"] == r"\operatorname{softmax}"


def test_untrusted_tarball_only_regular_tex_files() -> None:
    link = tarfile.TarInfo("evil.tex")
    link.type = tarfile.SYMTYPE
    link.linkname = "/etc/passwd"
    blob = tarball({"main.tex": MAIN, "fig.png": "x"}, extra=[link])
    assert set(read_sources(blob)) == {"main.tex"}
    single = gzip.compress(MAIN.encode())  # a one-file submission
    assert set(read_sources(single)) == {"main.tex"}
    assert read_sources(b"%PDF-1.5 not a source") == {}


def test_glossary_is_grounded_and_linked(settings: Settings) -> None:
    clock = FakeClock()
    llm = LLMClient(settings, {"gemini": FakePaperProvider()}, MemoryCache(), clock=clock,  # type: ignore[dict-item]
                    sleep=clock.sleep, rng=random.Random(0))  # fmt: skip
    run = build_report(fixture_doc(), llm, latex_blob=None, pdf_path=PDF)
    report = run.report
    assert not report.latex_available and report.equations  # the PDF's equation block
    eq = report.equations[0]
    assert eq.source == "pdf" and eq.block_id and eq.boxes
    by = {s.symbol: s for s in report.symbols}
    assert by["x"].evidence[0].grounding_status == "verified" and by["x"].evidence[0].boxes
    assert by["\\zeta"].evidence[0].grounding_status == "unlocated"  # kept, flagged


def test_latex_equations_matched_to_pdf_blocks(settings: Settings) -> None:
    doc = fixture_doc()
    eq_block = next(b for b in doc.blocks if b.type == "equation")
    eq_block.label = "(1)"
    blob = tarball({"main.tex": MAIN, "method.tex": METHOD})
    report = build_report(doc, None, latex_blob=blob, pdf_path=PDF).report
    assert report.latex_available and report.equations[0].block_id == eq_block.id
    assert report.macros[r"\R"] == r"\mathbb{R}"


def test_pdf_equations_drop_inline_fragments() -> None:
    doc = fixture_doc()
    eq_block = next(b for b in doc.blocks if b.type == "equation")
    eq_block.text, eq_block.label = "y = softmax(x W + b) (1)", "(1)"
    fragment = eq_block.model_copy(update={"id": "frag", "text": "√ d k", "label": None})
    doc.blocks.append(fragment)
    report = build_report(doc, None, latex_blob=None, pdf_path=None).report
    assert [e.text for e in report.equations] == ["y = softmax(x W + b)"]
    assert report.equations[0].number == "(1)" and report.equations[0].source == "pdf"


def test_symbols_damaged_by_json_escapes_are_restored() -> None:
    from app.pipeline.math.glossary import fix_latex

    assert fix_latex("p_\theta \bar\\alpha \beta_t \nabla") == r"p_\theta \bar\alpha \beta_t \nabla"


def test_main_file_is_the_paper_not_the_template() -> None:
    template = "\\documentclass{article}\n\\begin{document}Sample.\\end{document}"
    paper = (
        "\\documentclass{article}\n\\newcommand{\\beq}{\\begin{equation}}\n"
        "\\newcommand{\\eeq}{\\end{equation}}\n\\begin{document}\n"
        "\\beq a = b \\eeq\n\\input{body}\n\\end{document}"
    )
    files = {"iclr2015.tex": template, "adam.tex": paper, "body.tex": "\\beq c = d \\eeq"}
    text = flatten(files)
    assert "Sample." not in text
    assert [(e.latex, e.number) for e in equations(text)] == [("a = b", "1"), ("c = d", "2")]
