"""
Notebook 06 — Turnout surge
============================

Output
------
- outputs/charts/turnout_top20.png

Shows the top 20 constituencies by turnout increase (delta = 2026 - 2021),
coloured by region with inline annotations.
"""

# %%
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT     = Path(__file__).resolve().parents[1]
OUTPUTS  = ROOT / "outputs"
CHARTS   = ROOT / "outputs" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# ── Data ─────────────────────────────────────────────────────────────────────
df = pd.read_csv(OUTPUTS / "turnout_delta.csv")
top20 = df.head(20).copy()                     # already sorted delta desc
top20 = top20.sort_values("delta")             # ascending so largest is at top

REGION_COLORS = {
    "Chennai Metro": "#1F3A93",
    "North":         "#6C3483",
    "Central":       "#1A5276",
    "Kongu":         "#7D6608",
    "Delta":         "#145A32",
    "South":         "#784212",
}

bar_colors = top20["region"].map(REGION_COLORS)

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 9), dpi=150)

bars = ax.barh(
    y=top20["constituency"],
    width=top20["delta"],
    color=bar_colors,
    height=0.65,
    edgecolor="white",
    linewidth=0.5,
)

# ── Bar annotations: "turnout_2021% → turnout_2026%" ─────────────────────────
for bar, (_, row) in zip(bars, top20.iterrows()):
    label = f"  {row['turnout_2021']:.1f}% → {row['turnout_2026']:.1f}%"
    ax.text(
        bar.get_width() + 0.15,
        bar.get_y() + bar.get_height() / 2,
        label,
        va="center", ha="left",
        fontsize=8.5, color="#333333",
    )

# ── Axes formatting ───────────────────────────────────────────────────────────
ax.set_xlabel("Turnout change (percentage points)", fontsize=11, color="#444444", labelpad=8)
ax.set_xlim(0, top20["delta"].max() + 8)
ax.tick_params(axis="y", labelsize=10, length=0)
ax.tick_params(axis="x", labelsize=10, colors="#555555")
ax.set_axisbelow(True)
ax.grid(axis="x", color="#dddddd", linewidth=0.7, linestyle=":")
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#cccccc")

# ── Region color legend ───────────────────────────────────────────────────────
regions_in_chart = top20["region"].unique()
legend_patches = [
    mpatches.Patch(color=REGION_COLORS[r], label=r)
    for r in sorted(regions_in_chart, key=list(REGION_COLORS).index)
]
ax.legend(
    handles=legend_patches,
    title="Region",
    title_fontsize=9,
    fontsize=9,
    loc="lower right",
    framealpha=0.9,
    edgecolor="#cccccc",
)

# ── Titles & source note ──────────────────────────────────────────────────────
fig.text(
    0.10, 0.97,
    "Top 20 Turnout Surge Constituencies — 2021 vs 2026",
    ha="left", va="top",
    fontsize=17, fontweight="bold", color="#1a1a1a",
)
fig.text(
    0.10, 0.935,
    "Turnout change in percentage points. Chennai Metro dominated the top 20.",
    ha="left", va="top",
    fontsize=11, color="#666666",
)
fig.text(
    0.10, 0.018,
    "Source: Election Commission of India.",
    ha="left", va="bottom",
    fontsize=9, color="#888888",
)

plt.tight_layout(rect=[0.0, 0.03, 1.0, 0.91])

out_path = CHARTS / "turnout_top20.png"
plt.savefig(out_path, dpi=150, facecolor="white", bbox_inches="tight")
print(f"[ok] {out_path.relative_to(ROOT)} written")
