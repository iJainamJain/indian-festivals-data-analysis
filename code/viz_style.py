"""Shared chart style: validated categorical palette (fixed slot order, never cycled), one-hue sequential ramp,
thin marks, recessive grid.  Traditions are mapped to slots ONCE so a colour always means the same tradition."""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
# 9 traditions -> 8 slots: Parsi (1 festival) folds with the multi-faith cultural group into "Other"
TRAD_ORDER = ["Hindu", "Muslim", "Christian", "Tribal/Indigenous", "Sikh", "Buddhist", "Jain", "Other (Parsi, multi-faith)"]
TRAD_COLOR = dict(zip(TRAD_ORDER, SLOTS))
def trad_group(t):
    return "Other (Parsi, multi-faith)" if t in ("Parsi", "Cultural (multi-faith)") else t

SEQ = LinearSegmentedColormap.from_list("seq_blue", ["#f4f8fd", "#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])
DIV = LinearSegmentedColormap.from_list("div", ["#184f95", "#6da7ec", "#f0efec", "#ee8c8b", "#b3261e"])

def apply():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.family": "Segoe UI", "font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
        "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
        "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "lines.linewidth": 2,
        "savefig.dpi": 200, "savefig.bbox": "tight"})

def source_note(fig, text):
    fig.text(0.01, -0.02, "Source: " + text, fontsize=7.5, color=INK2, ha="left", va="top", wrap=True)

def label_points(ax, xs, ys, texts, fontsize=9.5, dx=8, min_gap=15):
    """Direct labels to the right of points with a simple vertical repel (no overlaps, leader line when moved)."""
    import numpy as np
    fig = ax.figure; fig.canvas.draw()
    pts = ax.transData.transform(np.column_stack([xs, ys]))
    order = np.argsort(pts[:, 1]); placed = []
    for i in order:
        x, y = pts[i]; ty = y
        for (px, py) in placed:
            if abs(px - x) < 170 and abs(py - ty) < min_gap: ty = py + min_gap
        placed.append((x, ty))
        off = ty - y
        ax.annotate(texts[i], (xs[i], ys[i]), xytext=(dx, off * 72 / fig.dpi), textcoords="offset points", fontsize=fontsize,
                    color=INK2, va="center", arrowprops=dict(arrowstyle="-", color=GRID, lw=0.8) if abs(off) > 4 else None)
