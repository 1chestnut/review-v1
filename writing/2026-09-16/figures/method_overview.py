#!/usr/bin/env python3
"""Publication workflow schematic for SAKI; generated with matplotlib only."""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent
NAVY, TEAL, GOLD = "#24476A", "#168A83", "#B47616"
INK, MUTED = "#17212B", "#526273"
PALE_BLUE, PALE_TEAL, PALE_GOLD = "#F2F6FA", "#EDF7F5", "#FBF4E9"
WHITE = "#FFFFFF"

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7.3,
    "axes.unicode_minus": False,
})

fig, ax = plt.subplots(figsize=(7.2, 5.9))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)
ax.set_xlim(0, 7.2)
ax.set_ylim(0, 5.9)
ax.axis("off")


def box(x, y, w, h, fc, ec="#BAC6D1", lw=0.8, radius=0.07):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.025,rounding_size={radius}",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=1,
    ))


def arrow(x1, y1, x2, y2, color=NAVY, lw=1.05, ms=9):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>",
        mutation_scale=ms, linewidth=lw, color=color,
        shrinkA=0, shrinkB=1, zorder=4,
        connectionstyle="arc3,rad=0",
    ))


def label(x, y, text, size=7.3, color=INK, weight="normal",
          ha="center", va="center"):
    ax.text(x, y, text, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, linespacing=1.10, zorder=5)


# Preparation and inference have distinct boundaries.
box(0.12, 5.06, 6.96, 0.73, "#F8FAFC", ec="#D0D9E2", radius=0.08)
label(0.25, 5.66, "OFFLINE KNOWLEDGE PREPARATION",
      7.8, NAVY, "bold", ha="left")
box(0.12, 0.15, 6.96, 4.79, WHITE, ec="#9BAAB9", lw=0.95, radius=0.09)
label(0.25, 4.81, "ONLINE SAMPLE-LEVEL INFERENCE",
      7.8, NAVY, "bold", ha="left")

# Offline left-to-right sequence.
offline = [
    (0.32, "Class labels\n× 47 relations"),
    (1.98, "RotatE\nTop-M tails"),
    (3.64, "AAKV\ntriple descriptions"),
    (5.30, "CLAP text\ncache"),
]
for x, txt in offline:
    box(x, 5.15, 1.47, 0.32, WHITE, ec="#C2CED8", lw=0.78, radius=0.045)
    label(x + 0.735, 5.31, txt, 6.65, INK, "semibold")
for i in range(3):
    arrow(offline[i][0] + 1.48, 5.31, offline[i+1][0] - 0.025,
          5.31, color=MUTED, lw=0.9, ms=7)

# Online inputs: audio and class text jointly produce CLAP scores.
box(0.39, 4.02, 3.04, 0.62, PALE_BLUE, ec="#A7BAC9", lw=0.85)
label(1.91, 4.51, "CLAP INITIAL RANKING", 7.8, NAVY, "bold")
label(1.91, 4.31, "Input audio + candidate class text", 7.25, INK)
label(1.91, 4.11, r"Base scores $s_{\mathrm{base}}$  →  Top-$K$ classes",
      7.2, NAVY, "semibold")

# Audio embedding and cached AAKV texts produce sample-specific evidence scores.
box(3.77, 4.02, 3.04, 0.62, PALE_TEAL, ec="#8ABAB5", lw=0.85)
label(5.29, 4.51, "AUDIO–EVIDENCE MATCHING", 7.8, TEAL, "bold")
label(5.29, 4.31, "Audio + cached AAKV text embeddings", 7.15, INK)
label(5.29, 4.11, r"Evidence scores $u_{irt}$", 7.25, TEAL, "semibold")
arrow(3.45, 4.33, 3.75, 4.33, color=NAVY, lw=1.0, ms=8)
arrow(6.04, 5.14, 6.04, 4.66, color=TEAL, lw=1.05, ms=8)

# Both score streams feed the per-relation experts.
box(0.39, 2.45, 6.42, 1.37, PALE_TEAL, ec="#8ABAB5", lw=0.9)
label(3.60, 3.67, "RELATION EXPERT RESULTS", 8.0, TEAL, "bold")
label(1.25, 3.47, "Relation", 7.15, MUTED, "bold")
label(3.58, 3.47, "Top-1 class", 7.15, MUTED, "bold")
label(5.68, 3.47, r"Top-two score gap $\Delta_r$", 7.15, MUTED, "bold")
ax.plot([0.57, 6.63], [3.36, 3.36], color="#A7CBC7", lw=0.72, zorder=2)
rows = [
    (r"$r_1$", "A", r"$\Delta_1$"),
    (r"$r_2$", "A", r"$\Delta_2$"),
    (r"$r_3$", "B", r"$\Delta_3$"),
    (r"$\vdots$", r"$\vdots$", r"$\vdots$"),
    (r"$r_{47}$", "A", r"$\Delta_{47}$"),
]
for y, row in zip([3.23, 3.06, 2.89, 2.72, 2.55], rows):
    label(1.25, y, row[0], 7.3, INK)
    label(3.58, y, row[1], 7.35,
          TEAL if row[1] == "A" else GOLD if row[1] == "B" else MUTED,
          "bold" if row[1] in ("A", "B") else "normal")
    label(5.68, y, row[2], 7.3, INK)
arrow(1.91, 4.01, 1.91, 3.84, color=NAVY, lw=1.05, ms=8)
arrow(5.29, 4.01, 5.29, 3.84, color=TEAL, lw=1.05, ms=8)

# Vote once, then rank the relation experts using the same score-gap definition.
box(0.39, 1.42, 6.42, 0.81, PALE_GOLD, ec="#D6B579", lw=0.87)
label(3.60, 2.09, "Top-1 votes  →  Consensus class: A",
      8.1, GOLD, "bold")
label(3.60, 1.82,
      r"Relations voting for A first; sort each group by $\Delta_r$ (descending)",
      7.05, INK)
label(3.60, 1.57, "Select the first 5 relations", 7.45, GOLD, "semibold")
arrow(3.60, 2.44, 3.60, 2.25, color=GOLD, lw=1.1, ms=8)

# Evidence pooling and final prediction use the selected relations.
box(0.39, 0.29, 6.42, 0.94, PALE_BLUE, ec="#A7BAC9", lw=0.88)
ax.plot([3.35, 3.35], [0.36, 1.15], color="#C9D4DE", lw=0.8, zorder=2)
label(1.87, 1.07, "SELECTED EVIDENCE PER CLASS", 7.5, NAVY, "bold")
label(1.87, 0.81, "Pool tails from the 5 relations", 7.05, INK)
label(1.87, 0.56, r"Exact-string dedup  →  $A_\kappa(\mathcal{U}_i^*)$",
      7.1, TEAL, "semibold")
label(5.08, 1.07, "FINAL SCORES AND RANKING", 7.5, NAVY, "bold")
label(5.08, 0.85,
      r"$s_{\mathrm{final}}(c_i)=\alpha s_{\mathrm{base}}(c_i)$",
      7.05, NAVY, "semibold")
label(5.08, 0.67,
      r"$\qquad+(1-\alpha)A_\kappa(\mathcal{U}_i^*)$",
      7.05, NAVY, "semibold")
label(5.08, 0.46, "Rank all classes  →  predicted label",
      7.05, INK, "semibold")
arrow(3.60, 1.41, 3.60, 1.25, color=GOLD, lw=1.1, ms=8)

# Values in the miniature expert table are illustrative, not measurements.
fig.savefig(OUT / "method_overview.svg", bbox_inches="tight", pad_inches=0.025)
fig.savefig(OUT / "method_overview.pdf", bbox_inches="tight", pad_inches=0.025)
fig.savefig(OUT / "method_overview.png", dpi=600, bbox_inches="tight", pad_inches=0.025)
fig.savefig(OUT / "method_overview_preview.jpg", dpi=80,
            bbox_inches="tight", pad_inches=0.025, pil_kwargs={"quality": 55})
plt.close(fig)
