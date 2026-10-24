"""Paper charts from eval/results (run collect_flash_lite and phase2_flash_lite).

From the repo root: python docs/paper/make_figs.py (needs matplotlib and numpy).
"""
import csv
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

ROOT = str(Path(__file__).resolve().parents[2])
R = f"{ROOT}/eval/results"
OUT = f"{ROOT}/docs/paper/figs"
RUN, REF = "collect_flash_lite", "phase2_flash_lite"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "legend.frameon": False, "pdf.fonttype": 42})
W = 3.45
NAMES = {"task": "Task", "datasets": "Datasets", "baselines": "Baselines", "metrics": "Metrics",
         "hyperparameters": "Hyperparams", "compute": "Compute", "code_urls": "Code URLs"}
FIELDS = list(NAMES)


def bars(ax, x, vals, w, color, label):
    return ax.bar(x, vals, w, color=color, label=label, edgecolor="white", linewidth=0.8)


# 1. per-field P / R / F1 (50 papers)
rows = [r for r in csv.DictReader(open(f"{R}/by_field.csv")) if r["run"] == RUN]
x = np.arange(len(rows)); w = 0.27
fig, ax = plt.subplots(figsize=(W, 2.1))
for k, (key, c, lab) in enumerate([("precision", C1, "Precision"), ("recall", C2, "Recall"),
                                   ("f1", C3, "F1")]):
    bars(ax, x + (k - 1) * w, [float(r[key]) for r in rows], w, c, lab)
for i, r in enumerate(rows):
    ax.text(i + w, float(r["f1"]) + 0.02, f"{float(r['f1']):.2f}", ha="center", va="bottom",
            fontsize=6, color=INK)
ax.set_xticks(x, [NAMES[r["field"]] for r in rows], fontsize=6.5, rotation=25, ha="right")
ax.set_ylim(0, 1.12); ax.set_ylabel("Score"); ax.grid(axis="x", visible=False)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.16), fontsize=7)
fig.tight_layout(pad=0.3); fig.savefig(f"{OUT}/fig_fields.pdf"); plt.close(fig)

# 2. per-paper F1 heatmap, papers grouped by area (full width)
papers = {r["arxiv_id"]: r for r in csv.DictReader(open(f"{ROOT}/eval/papers.csv"))}
order = ["NLP", "CV", "Generative", "Multimodal", "ML", "Graph", "RL", "Speech", "Time series"]
pr = {r["paper_id"]: r for r in csv.DictReader(open(f"{R}/by_paper.csv")) if r["run"] == RUN}
ids = sorted(pr, key=lambda i: (order.index(papers[i]["area"]), papers[i]["set"] != "reference",
                                papers[i]["year"]))
M = np.array([[np.nan if pr[i][c] in ("-", "") else float(pr[i][c]) for i in ids] for c in FIELDS])
cmap = LinearSegmentedColormap.from_list("b", ["#eef4fc", "#9cc1ee", "#2a78d6", "#123f7a"])
cmap.set_bad("#f3f2ef")
fig, ax = plt.subplots(figsize=(7.1, 2.35))
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect="auto")
ax.set_yticks(range(len(FIELDS)), [NAMES[c] for c in FIELDS], fontsize=6.5)
labels = [papers[i]["name"].split(",")[0] + ("*" if papers[i]["set"] == "reference" else "")
          for i in ids]
ax.set_xticks(range(len(ids)), labels, fontsize=5.4, rotation=60, ha="right")
ax.grid(False); [s.set_visible(False) for s in ax.spines.values()]
start = 0
for area in order:
    n = sum(papers[i]["area"] == area for i in ids)
    if not n:
        continue
    if start:
        ax.axvline(start - 0.5, color="white", lw=2.2)
    short = {"Generative": "Gen.", "Multimodal": "MM", "Speech": "Sp.", "Time series": "TS"}
    ax.text(start + (n - 1) / 2, -0.85, short.get(area, area), ha="center", va="bottom",
            fontsize=6.3, color=INK)
    start += n
cb = fig.colorbar(im, ax=ax, fraction=0.015, pad=0.01); cb.ax.tick_params(labelsize=6)
cb.outline.set_visible(False); cb.set_label("F1", fontsize=7)
fig.tight_layout(pad=0.3); fig.savefig(f"{OUT}/fig_papers.pdf"); plt.close(fig)

# 3. A3 evidence policies: both runs
text = open(f"{R}/ablations.md", encoding="utf-8").read()


def a3(run):
    block = text.split(f"### {run}")[1].split("###")[0].split("A1")[0]
    out = []
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 6 and cells[1].isdigit():
            out.append((int(cells[1]), *map(float, cells[2:5]), int(cells[5].rstrip("%"))))
    return out


pol = ["Keep\nall", "Quote\nfound", "+ supp.\nor part.", "+ sup-\nports"]
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 1.75))
x = np.arange(4); w = 0.38
for k, (run, lab, c) in enumerate([(REF, "development set (earlier pipeline)", C2),
                                   (RUN, "all 50 papers", C1)]):
    rs = a3(run)
    bars(a, x + (k - 0.5) * w, [r[3] for r in rs], w, c, lab)
    bars(b, x + (k - 0.5) * w, [r[4] for r in rs], w, c, lab)
    for i, r in enumerate(rs):
        a.text(i + (k - 0.5) * w, r[3] + 0.01, f"{r[3]:.2f}", ha="center", fontsize=4.8,
               color=INK)
        b.text(i + (k - 0.5) * w, r[4] + 0.2, f"{r[4]}", ha="center", fontsize=5.5, color=INK)
for ax, title in ((a, "Core-field F1"), (b, "Hallucination rate (%)")):
    ax.set_xticks(x, pol, fontsize=5.8); ax.grid(axis="x", visible=False)
    ax.set_title(title, fontsize=7, color=INK); ax.tick_params(axis="y", labelsize=6)
a.set_ylim(0.4, 0.75); b.set_ylim(0, 11.5)
h, l = a.get_legend_handles_labels()
fig.legend(h, l, ncol=2, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, 1.02))
fig.tight_layout(pad=0.3, rect=(0, 0, 1, 0.9)); fig.savefig(f"{OUT}/fig_a3.pdf"); plt.close(fig)

# 4. errors: missed gold items by field + audit of the not-in-gold items (new 40 papers)
missed, f = Counter(), None
for line in open(f"{R}/errors_{RUN}.md", encoding="utf-8"):
    m = re.match(r"### (\S+)", line)
    if m:
        f = m.group(1)
    if line.startswith("- missed"):
        missed[f] += 1
audit = list(csv.DictReader(open(f"{ROOT}/eval/gold/audit_v2.csv", encoding="utf-8")))
cats = [("correct, matcher missed", "Correct, matcher missed", C3),
        ("gold omission (added)", "Gold omission (added)", C1),
        ("out of scope", "Out of scope", "#b7b5ae"), ("wrong", "Wrong", "#dc2626")]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.1, 2.25), gridspec_kw={"wspace": 0.45})
ks = sorted(missed, key=missed.get)
a.barh([NAMES[k] for k in ks], [missed[k] for k in ks], color=C1, height=0.6, edgecolor="white")
for i, k in enumerate(ks):
    a.text(missed[k] + 8, i, missed[k], va="center", fontsize=6.5, color=INK)
a.set_xlim(0, max(missed.values()) * 1.15)
a.set_title(f"Missed gold items ({sum(missed.values())} of 2796)", fontsize=7.5, color=INK)
a.grid(axis="y", visible=False); a.tick_params(axis="y", labelsize=7)
ks2 = [k for k in FIELDS][::-1]
left = np.zeros(len(ks2))
for key, lab, c in cats:
    vals = np.array([sum(r["field"] == k and r["category"] == key for r in audit) for k in ks2])
    tot = sum(r["category"] == key for r in audit)
    b.barh([NAMES[k] for k in ks2], vals, left=left, color=c, height=0.6, edgecolor="white",
           label=f"{lab} ({tot})")
    left += vals
b.set_title(f"Not-in-gold items, read one by one ({len(audit)})", fontsize=7.5, color=INK)
b.grid(axis="y", visible=False); b.tick_params(axis="y", labelsize=7)
b.legend(fontsize=6, ncol=2, loc="upper center", bbox_to_anchor=(0.45, -0.13), handlelength=1)
fig.subplots_adjust(left=0.11, right=0.99, top=0.9, bottom=0.3)
fig.savefig(f"{OUT}/fig_errors.pdf"); plt.close(fig)
print("ok")

# 5. A1 parser: gold values still in the parsed text, by field (from ablations.md)
a1 = text.split("## A1:")[1].split("## A6:")[0]
head_row = next(line for line in a1.splitlines() if line.startswith("| parser | baselines"))
fl = [c.strip() for c in head_row.strip("|").split("|")][1:]
overall, by = {}, {}
for line in a1.splitlines():
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) == 10 and cells[1].isdigit():
        overall[cells[0]] = cells[9]
    elif len(cells) == len(fl) + 1 and cells[0] in overall:
        by[cells[0]] = [int(c.rstrip("%")) for c in cells[1:]]
gro, pym = by["GROBID (cached TEI)"], by["PyMuPDF only"]
n = re.search(r"\| GROBID \(cached TEI\) \| (\d+) \|", a1).group(1)
fig, ax = plt.subplots(figsize=(W, 1.95)); x = np.arange(len(fl)); w = 0.38
bars(ax, x - w / 2, gro, w, C1, f"GROBID ({overall['GROBID (cached TEI)']} overall)")
bars(ax, x + w / 2, pym, w, C2, f"PyMuPDF only ({overall['PyMuPDF only']} overall)")
for i in range(len(fl)):
    for dx, v in ((-w / 2, gro[i]), (w / 2, pym[i])):
        if v < 100:
            ax.text(i + dx, v + 1, v, ha="center", fontsize=6, color=INK)
ax.set_xticks(x, [NAMES[f] for f in fl], fontsize=6.5, rotation=25, ha="right")
ax.set_ylim(55, 106); ax.set_ylabel(f"Gold values in text (%, {n} papers)", fontsize=7)
ax.grid(axis="x", visible=False)
ax.legend(ncol=2, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, 1.18))
fig.tight_layout(pad=0.3); fig.savefig(f"{OUT}/fig_a1.pdf"); plt.close(fig)
print("a1 ok")
