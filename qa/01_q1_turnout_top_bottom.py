"""
01_q1_turnout_top_bottom.py
============================
Q1 — Top 5 / Bottom 5 Constituencies by Voter Turnout (2021 & 2026)

Note: 2014 and 2019 data refers to Lok Sabha elections; Assembly election
data is only available for 2021 and 2026 in this dataset.

Run after: 00_data_loader.py
Output:    ./outputs/q1_turnout_top_bottom.csv
           ./outputs/q1_turnout_delta_top10.csv
           ./outputs/charts/q1_turnout_bars.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

PROC = "./data/processed"
OUT  = "./outputs"
os.makedirs(f"{OUT}/charts", exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
turnout = pd.read_csv(f"{PROC}/turnout_master.csv")

# ── Top / Bottom 5 ───────────────────────────────────────────────────────────
top5_21  = turnout.nlargest(5,  "turnout_21")[["constituency", "turnout_21", "region", "reserved"]]
bot5_21  = turnout.nsmallest(5, "turnout_21")[["constituency", "turnout_21", "region", "reserved"]]
top5_26  = turnout.nlargest(5,  "turnout_26")[["constituency", "turnout_26", "region", "reserved"]]
bot5_26  = turnout.nsmallest(5, "turnout_26")[["constituency", "turnout_26", "region", "reserved"]]
delta10  = turnout.nlargest(10, "delta")[["constituency", "turnout_21", "turnout_26", "delta", "region"]]

# ── Print results ─────────────────────────────────────────────────────────────
print("=" * 60)
print("Q1 — VOTER TURNOUT TOP 5 / BOTTOM 5")
print("=" * 60)

for label, df, col in [
    ("TOP 5 — 2021",    top5_21,  "turnout_21"),
    ("BOTTOM 5 — 2021", bot5_21,  "turnout_21"),
    ("TOP 5 — 2026",    top5_26,  "turnout_26"),
    ("BOTTOM 5 — 2026", bot5_26,  "turnout_26"),
]:
    print(f"\n{label}")
    print("-" * 50)
    for _, r in df.iterrows():
        print(f"  {r['constituency']:<30} {r[col]:.2f}%  [{r['region']}]")

print("\nTOP 10 — BIGGEST TURNOUT JUMP (2021 → 2026)")
print("-" * 60)
for _, r in delta10.iterrows():
    print(f"  {r['constituency']:<30} {r['turnout_21']:.2f}% → {r['turnout_26']:.1f}%  (+{r['delta']:.2f}pp)  [{r['region']}]")

# ── Save CSVs ─────────────────────────────────────────────────────────────────
summary = pd.concat([
    top5_21.assign(category="Top 5 — 2021",    year=2021).rename(columns={"turnout_21": "turnout"}),
    bot5_21.assign(category="Bottom 5 — 2021", year=2021).rename(columns={"turnout_21": "turnout"}),
    top5_26.assign(category="Top 5 — 2026",    year=2026).rename(columns={"turnout_26": "turnout"}),
    bot5_26.assign(category="Bottom 5 — 2026", year=2026).rename(columns={"turnout_26": "turnout"}),
], ignore_index=True)
summary.to_csv(f"{OUT}/q1_turnout_top_bottom.csv", index=False)
delta10.to_csv(f"{OUT}/q1_turnout_delta_top10.csv", index=False)

# ── Chart ─────────────────────────────────────────────────────────────────────
REGION_COLORS = {
    "Chennai Metro": "#63b3ed",
    "North": "#6ee7b7",
    "Central": "#fcd34d",
    "Kongu": "#fca5a5",
    "Delta": "#c4b5fd",
    "South": "#fdba74",
}

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.patch.set_facecolor("#0d0f14")
fig.suptitle("Q1 — Voter Turnout: Top 5 & Bottom 5 (2021 vs 2026)",
             color="white", fontsize=14, fontweight="bold", y=1.01)

panels = [
    (axes[0, 0], top5_21,  "turnout_21", "Top 5 — 2021",    100),
    (axes[0, 1], bot5_21,  "turnout_21", "Bottom 5 — 2021", 100),
    (axes[1, 0], top5_26,  "turnout_26", "Top 5 — 2026",    100),
    (axes[1, 1], bot5_26,  "turnout_26", "Bottom 5 — 2026", 100),
]

for ax, df, col, title, xmax in panels:
    ax.set_facecolor("#141720")
    colors = [REGION_COLORS.get(r, "#718096") for r in df["region"]]
    bars = ax.barh(df["constituency"], df[col], color=colors, edgecolor="none", height=0.55)
    for bar, val in zip(bars, df[col]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9, color="white")
    ax.set_xlim(0, xmax + 5)
    ax.set_title(title, color="#f0a500", fontsize=11, fontweight="bold", pad=8)
    ax.tick_params(colors="white", labelsize=9)
    ax.spines[:].set_visible(False)
    ax.set_xlabel("Turnout %", color="#6b7280", fontsize=9)
    ax.xaxis.label.set_color("#6b7280")
    ax.tick_params(axis="x", colors="#6b7280")
    ax.tick_params(axis="y", colors="white")

# Legend
legend_patches = [mpatches.Patch(color=c, label=r) for r, c in REGION_COLORS.items()]
fig.legend(handles=legend_patches, loc="lower center", ncol=6,
           facecolor="#141720", edgecolor="#2a2f40",
           labelcolor="white", fontsize=9, bbox_to_anchor=(0.5, -0.05))

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q1_turnout_bars.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q1_turnout_bars.png")
print(f"✅ CSVs saved:  {OUT}/q1_turnout_top_bottom.csv  |  q1_turnout_delta_top10.csv")
