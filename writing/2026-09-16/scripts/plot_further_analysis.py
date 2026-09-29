from pathlib import Path
import csv
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "further_analysis"
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    "font.family": "Times New Roman",
    "font.serif": ["Times New Roman", "Times", "STIXGeneral"],
    "mathtext.fontset": "stix",
    "font.size": 7,
    "axes.labelsize": 7,
    "axes.titlesize": 8,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

BLUE = "#3A78B4"
ORANGE = "#D98C3F"
TEAL = "#3C9D8F"
GRAY = "#727A84"
LIGHT = "#E8EDF2"

# Restrained publication palette adapted from the supplied examples.
NATURE_BLUE = "#79A1C2"
NATURE_OLIVE = "#BFC557"
BLUE_CMAP = LinearSegmentedColormap.from_list(
    "paper_blue", ["#DDEAF3", "#8AAECD", "#315F86"]
)
BROWN_CMAP = LinearSegmentedColormap.from_list(
    "paper_brown", ["#F1C7A6", "#C6683D", "#8F351F"]
)


def save_all(fig, stem):
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.png", dpi=600, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.tiff", dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


datasets = ["ESC-50", "UrbanSound8K", "FSD50K", "AudioSet", "TUT2017"]
n = [2000, 8732, 10231, 17233, 6300]
dh1 = np.array([2.50, 2.2904260192, 4.6232039879, 2.0774096211, 12.7301587302])
h1lo = np.array([1.60, 1.7521759047, 3.8703450298, 1.5589972727, 11.4920634921])
h1hi = np.array([3.45, 2.8172240037, 5.3562701593, 2.5822549759, 13.9523809524])
dmrr = np.array([1.1825, 1.1396778134, 2.3259568902, 1.0239047445, 6.6821371310])
mrrlo = np.array([0.675833, 0.8459259047, 1.8795754065, 0.7212232109, 5.9452560612])
mrrhi = np.array([1.700833, 1.4347658039, 2.7618717179, 1.3372892192, 7.4112421551])

with (OUT / "source_statistics.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["dataset", "n", "delta_Hit1_pp", "Hit1_CI_low", "Hit1_CI_high",
                "delta_MRR_pp", "MRR_CI_low", "MRR_CI_high"])
    w.writerows(zip(datasets, n, dh1, h1lo, h1hi, dmrr, mrrlo, mrrhi))

# Figure 1: paired bootstrap forest plot
y = np.arange(len(datasets))
fig, axes = plt.subplots(1, 2, figsize=(7.20, 2.35), sharey=True)
for ax, val, lo, hi, title, color in [
    (axes[0], dh1, h1lo, h1hi, r"Hit@1 difference (percentage points)", BLUE),
    (axes[1], dmrr, mrrlo, mrrhi, r"MRR difference (percentage points)", TEAL),
]:
    ax.axvline(0, color="#9AA1A8", lw=0.8, ls="--", zorder=0)
    ax.errorbar(val, y, xerr=np.vstack([val-lo, hi-val]), fmt="o", ms=4.2,
                color=color, ecolor=color, capsize=2.5, lw=1.1)
    ax.set_title(title, pad=6)
    ax.set_xlabel(r"SAKI − iKnow$^{\dagger}$")
    ax.grid(axis="x", color=LIGHT, lw=0.6)
    ax.set_ylim(-0.6, len(datasets)-0.4)
axes[0].set_yticks(y, [f"{d}  ($n$={nn:,})" for d, nn in zip(datasets, n)])
axes[0].invert_yaxis()
axes[0].text(-0.16, 1.05, "a", transform=axes[0].transAxes, fontweight="bold", fontsize=9)
axes[1].text(-0.13, 1.05, "b", transform=axes[1].transAxes, fontweight="bold", fontsize=9)
fig.subplots_adjust(wspace=0.28)
save_all(fig, "fig_statistical_significance")

# Figure 2: DCASE development sensitivity heatmaps
alphas = [0.3, 0.5, 0.7]
nrs = [1, 3, 5, 10]
hit1 = np.array([[64.43914081]*4, [63.00715990]*4, [63.00715990]*4])
mrr = np.array([
    [75.55015986, 75.71154184, 75.83882903, 75.68767549],
    [74.77450354, 75.14272720, 75.30979164, 74.96372959],
    [75.12454332, 75.30183619, 75.23023715, 75.42912338],
])
with (OUT / "source_parameter_sensitivity.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["alpha", "N_r", "Hit@1", "MRR", "selected"])
    for i, a in enumerate(alphas):
        for j, nr in enumerate(nrs):
            w.writerow([a, nr, hit1[i, j], mrr[i, j], a == 0.3 and nr == 5])

fig, axes = plt.subplots(2, 1, figsize=(3.35, 4.25))
for k, (ax, arr, title, cmap) in enumerate([
    (axes[0], hit1, "Hit@1 (%)", BLUE_CMAP),
    (axes[1], mrr, "MRR (%)", BROWN_CMAP),
]):
    # The measured grid is 3 x 4 (three alpha values and four N_r values).
    # Keep square cells instead of inventing a fourth alpha level for appearance.
    im = ax.imshow(arr, cmap=cmap, aspect="equal", vmin=arr.min()-0.08, vmax=arr.max()+0.08)
    ax.set_xticks(range(4), nrs); ax.set_yticks(range(3), alphas)
    ax.set_xlabel(r"Number of selected relations, $N_r$")
    ax.set_ylabel(r"Fusion weight, $\alpha$")
    ax.set_title(title, pad=5)
    for i in range(3):
        for j in range(4):
            ax.text(j, i, f"{arr[i,j]:.2f}", ha="center", va="center",
                    color="black", fontsize=6.6)
    ax.add_patch(plt.Rectangle((1.5, -0.5), 1, 1, fill=False,
                               edgecolor="#6A0624", lw=2.0))
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.035)
    cb.ax.tick_params(labelsize=6)
    ax.text(-0.16, 1.05, chr(ord('a')+k), transform=ax.transAxes, fontweight="bold", fontsize=9)
fig.subplots_adjust(hspace=0.58)
save_all(fig, "fig_parameter_sensitivity")

# Figure 3: sample-level prediction transitions
rescued = np.array([72, 382, 991, 1131, 1218])
harmed = np.array([22, 182, 518, 773, 416])
with (OUT / "source_prediction_transitions.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["dataset", "wrong_to_correct", "correct_to_wrong", "net_rescued"])
    w.writerows(zip(datasets, rescued, harmed, rescued-harmed))

fig, ax = plt.subplots(figsize=(3.35, 3.30))
y = np.arange(len(datasets)); height = 0.30
b1 = ax.barh(y-height/2, rescued, height, color=NATURE_BLUE,
             label=r"Wrong $\rightarrow$ correct")
b2 = ax.barh(y+height/2, harmed, height, color=NATURE_OLIVE,
             label=r"Correct $\rightarrow$ wrong")
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_width()+18, b.get_y()+b.get_height()/2, f"{int(b.get_width()):,}",
                ha="left", va="center", fontsize=6.0)
ax.set_yticks(y, datasets)
ax.invert_yaxis()
ax.set_xlabel("Number of test samples")
ax.set_xlim(0, 1340)
ax.grid(False)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2,
          fontsize=5.8, frameon=False, columnspacing=0.9, handlelength=1.8)
fig.subplots_adjust(top=0.86)
save_all(fig, "fig_prediction_transitions")

print(OUT)
