"""Generate the three fixture PDFs used by the parser tests.

    uv run python tests/fixtures/make_fixtures.py

The PDFs are committed; re-run only when changing their content. They are synthetic so the
repo carries no third-party papers, but they mimic real ones: numbered sections, an abstract,
a booktabs-style results table with ± and a bold best value, captions, an equation and a
reference list.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pymupdf

HERE = Path(__file__).parent

CSS = """
body { font-family: serif; font-size: 10pt; line-height: 1.25; }
h1 { font-size: 15pt; text-align: center; margin-bottom: 4pt; }
.authors { text-align: center; font-size: 10pt; margin-bottom: 10pt; }
h2 { font-size: 11.5pt; margin-top: 10pt; margin-bottom: 4pt; }
h3 { font-size: 10.5pt; margin-top: 8pt; margin-bottom: 3pt; }
p { text-align: justify; margin-bottom: 5pt; }
.abstract { font-size: 9.5pt; margin-left: 24pt; margin-right: 24pt; }
.eq { text-align: center; font-style: italic; margin: 6pt 0; }
table { border-collapse: collapse; margin: 6pt auto; font-size: 9pt; }
th, td { padding: 2pt 6pt; text-align: center; }
thead th { border-top: 1pt solid black; border-bottom: 0.6pt solid black; }
tbody tr:last-child td { border-bottom: 1pt solid black; }
.ruled td, .ruled th { border: 0.6pt solid black; }
.caption { font-size: 9pt; text-align: center; margin-bottom: 8pt; }
.refs p { font-size: 8.5pt; text-indent: -12pt; margin-left: 12pt; margin-bottom: 3pt; }
"""

FILLER = (
    "Recent work has shown that careful design of the training objective matters as much as "
    "model size. We study this question under a controlled compute budget and report results "
    "averaged over several random seeds so that differences can be attributed to the method "
    "rather than to noise. "
)

SINGLE_HTML = f"""
<h1>Sparse Routing Improves Low-Resource Translation</h1>
<div class="authors">Asha Rao<sup>1</sup>, Daniel Okafor<sup>2</sup><br/>
<sup>1</sup>Institute of Language Technology &nbsp; <sup>2</sup>City University</div>
<h2>Abstract</h2>
<p class="abstract">We introduce SparseRoute, a mixture-of-experts layer that routes each token
to a single expert. On the FLORES-200 benchmark SparseRoute improves BLEU by 2.1 points over a
dense Transformer baseline while using 30% fewer training FLOPs. Code is available at
https://github.com/example/sparseroute.</p>
<h2>1 Introduction</h2>
<p>{FILLER * 3}</p>
<p>Our contributions are threefold. First, we propose a routing rule that needs no auxiliary
load-balancing loss. Second, we evaluate it on FLORES-200 and WMT 2014 English-German. Third,
we release code and trained checkpoints.</p>
<h2>2 Related Work</h2>
<p>{FILLER * 4}</p>
<h2>3 Method</h2>
<p>Each token representation x is sent to the expert with the highest router score, and the
layer output is the expert output scaled by the router probability:</p>
<p class="eq">y = p<sub>k</sub>(x) E<sub>k</sub>(x), &nbsp; k = argmax<sub>i</sub> W<sub>r</sub> x &nbsp;&nbsp; (1)</p>
<p>{FILLER * 3}</p>
<h3>3.1 Training details</h3>
<p>We train with Adam using a learning rate of 3e-4, batch size 256 and 50k steps on 8 NVIDIA
A100 GPUs, which takes about 36 hours. Dropout is 0.1. We use 3 random seeds.</p>
<h2>4 Experiments</h2>
<p>{FILLER * 2}</p>
<table>
<thead><tr><th>Method</th><th>FLORES-200 BLEU</th><th>WMT14 En-De BLEU</th><th>FLOPs (%)</th></tr></thead>
<tbody>
<tr><td>Transformer</td><td>24.3 ± 0.2</td><td>27.1 ± 0.1</td><td>100</td></tr>
<tr><td>Switch</td><td>25.0 ± 0.3</td><td>27.4 ± 0.2</td><td>72</td></tr>
<tr><td>SparseRoute (ours)</td><td><b>26.4 ± 0.2</b></td><td><b>27.9 ± 0.1</b></td><td>70</td></tr>
</tbody></table>
<p class="caption">Table 1: Test BLEU averaged over 3 seeds (mean ± std).</p>
<h3>4.1 Ablation study</h3>
<p>{FILLER * 2}</p>
<h2>5 Limitations</h2>
<p>We only evaluate translation. Routing may behave differently on long documents.</p>
<h2>6 Conclusion</h2>
<p>{FILLER * 2}</p>
<h2>References</h2>
<div class="refs">
<p>Vaswani, A., Shazeer, N., Parmar, N., et al. 2017. Attention is all you need. In
Advances in Neural Information Processing Systems.</p>
<p>Fedus, W., Zoph, B., and Shazeer, N. 2022. Switch transformers: Scaling to trillion
parameter models with simple and efficient sparsity. Journal of Machine Learning Research.</p>
<p>NLLB Team. 2022. No language left behind: Scaling human-centered machine translation.
arXiv:2207.04672.</p>
</div>
"""

TWOCOL_HTML = f"""
<h2>Abstract</h2>
<p class="abstract">We pretrain a sentence encoder with a contrastive objective and fine-tune it
on MNLI, where it reaches 88.0% matched accuracy, 1.9 points above RoBERTa.</p>
<h2>1 Introduction</h2>
<p>{FILLER * 4}</p>
<h2>2 Approach</h2>
<p>{FILLER * 3}</p>
<h2>3 Results</h2>
<p>{FILLER * 2}</p>
<table class="ruled">
<tr><th>Model</th><th>Acc. (%)</th><th>F1</th></tr>
<tr><td>BERT-base</td><td>84.6</td><td>0.812</td></tr>
<tr><td>RoBERTa</td><td>86.1</td><td>0.829</td></tr>
<tr><td>Ours</td><td><b>88.0</b></td><td><b>0.851</b></td></tr>
</table>
<p class="caption">Table 2: Accuracy on the MNLI matched dev set.</p>
<p>{FILLER * 3}</p>
<h2>4 Conclusion</h2>
<p>{FILLER * 2}</p>
<h2>References</h2>
<div class="refs"><p>Devlin, J., Chang, M., Lee, K., and Toutanova, K. 2019. BERT: Pre-training
of deep bidirectional transformers for language understanding. In NAACL.</p></div>
"""

PAGE = pymupdf.paper_rect("letter")
MARGIN = 54


def render(html: str, out: Path, columns: int = 1, header: str | None = None) -> None:
    """Lay out `html` in `columns` columns; `header` is a full-width block atop page 1.

    The header is drawn first so it comes first in the content stream, as in real papers.
    """
    story = pymupdf.Story(html=html, user_css=CSS)
    head_story = pymupdf.Story(html=header, user_css=CSS) if header else None
    writer = pymupdf.DocumentWriter(str(out))
    gutter = 18
    width = (PAGE.width - 2 * MARGIN - (columns - 1) * gutter) / columns
    head_height = 0.0
    page_no, col = 0, 0
    device: Any = None
    more = True
    while more:
        if col == 0:
            if device is not None:
                writer.end_page()
            device = writer.begin_page(PAGE)
            page_no += 1
            if page_no == 1 and head_story is not None:
                head_rect = pymupdf.Rect(MARGIN, MARGIN, PAGE.width - MARGIN, MARGIN + 120)
                _, filled = head_story.place(head_rect)
                head_story.draw(device)
                head_height = pymupdf.Rect(filled).y1 - MARGIN + 8
        top = MARGIN + (head_height if page_no == 1 else 0)
        x0 = MARGIN + col * (width + gutter)
        more, _ = story.place(pymupdf.Rect(x0, top, x0 + width, PAGE.height - MARGIN))
        story.draw(device)
        col = (col + 1) % columns
    writer.end_page()
    writer.close()


def make_scanned(source: Path, out: Path) -> None:
    """Image-only copy of a page: no text layer, as a scanned paper would be."""
    src = pymupdf.open(source)
    pix = src[0].get_pixmap(dpi=100)
    doc = pymupdf.open()
    page = doc.new_page(width=PAGE.width, height=PAGE.height)
    page.insert_image(page.rect, pixmap=pix)
    doc.save(out, deflate=True)


def main() -> None:
    render(SINGLE_HTML, HERE / "paper_single.pdf")
    render(
        TWOCOL_HTML,
        HERE / "paper_twocol.pdf",
        columns=2,
        header=(
            "<h1>Contrastive Pretraining for Natural Language Inference</h1>"
            '<div class="authors">Mei Lin, Tomas Varga</div>'
        ),
    )
    make_scanned(HERE / "paper_single.pdf", HERE / "scanned.pdf")
    for name in ("paper_single.pdf", "paper_twocol.pdf", "scanned.pdf"):
        doc = pymupdf.open(HERE / name)
        print(f"{name}: {doc.page_count} pages, {(HERE / name).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
