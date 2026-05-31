"""
04_q4_margin_analysis.py
=========================
Q4 — Top 5 candidates by winning margin (largest & smallest) in 2021 and 2026

Run after: 00_data_loader.py
Output:    ./outputs/q4_margins_2021.csv
           ./outputs/q4_margins_2026.csv
           ./outputs/charts/q4_margins.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

PROC = "./data/processed"
OUT  = "./outputs"
os.makedirs(f"{OUT}/charts", exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
w21 = pd.read_csv(f"{PROC}/winners_2021.csv")
w26 = pd.read_csv(f"{PROC}/winners_2026.csv")

# ── Top 5 / Bottom 5 margins ─────────────────────────────────────────────────
top5_21  = w21.nlargest(5,  "margin")[["constituency", "candidate", "party", "votes", "runner_votes", "margin", "region"]]
bot5_21  = w21.nsmallest(5, "margin")[["constituency", "candidate", "party", "votes", "runner_votes", "margin", "region"]]
top5_26  = w26.nlargest(5,  "margin")[["constituency", "candidate", "party", "votes", "runner_votes", "margin", "region"]]
bot5_26  = w26.nsmallest(5, "margin")[["constituency", "candidate", "party", "votes", "runner_votes", "margin", "region"]]

# ── Print ─────────────────────────────────────────────────────────────────────
print("=" * 75)
print("Q4 — TOP 5 & BOTTOM 5 CANDIDATES BY WINNING MARGIN")
print("=" * 75)

for label, df in [
    ("TOP 5 LARGEST MARGINS — 2021",    top5_21),
    ("TOP 5 SMALLEST MARGINS — 2021",   bot5_21),
    ("TOP 5 LARGEST MARGINS — 2026",    top5_26),
    ("TOP 5 SMALLEST MARGINS — 2026",   bot5_26),
]:
    print(f"\n{label}")
    print("-" * 75)
    print(f"  {'Constituency':<25} {'Candidate':<28} {'Party':<8} {'Margin':>8}  Region")
    print("  " + "-" * 70)
    for _, r in df.iterrows():
        print(f"  {r['constituency']:<25} {r['candidate']:<28} {r['party']:<8} {r['margin']:>8,}  {r['region']}")

# ── Notable facts ─────────────────────────────────────────────────────────────
min26 = w26.nsmallest(1, "margin").iloc[0]
max26 = w26.nlargest(1, "margin").iloc[0]
print(f"\n\n📌 CLOSEST 2026:  {min26['constituency']} — {min26['candidate']} ({min26['party']}) won by {min26['margin']:,} vote(s)!")
print(f"📌 BIGGEST 2026:  {max26['constituency']} — {max26['candidate']} ({max26['party']}) won by {max26['margin']:,} votes")

# Appears in both top 5?
both = set(top5_21["constituency"]) & set(top5_26["constituency"])
if both:
    print(f"\n📌 Appears in BOTH years' top 5 margins: {', '.join(both)}")

# ── Save ──────────────────────────────────────────────────────────────────────
pd.concat([top5_21.assign(category="Top 5"),
           bot5_21.assign(category="Bottom 5")]).to_csv(f"{OUT}/q4_margins_2021.csv", index=False)
pd.concat([top5_26.assign(category="Top 5"),
           bot5_26.assign(category="Bottom 5")]).to_csv(f"{OUT}/q4_margins_2026.csv", index=False)

# ── Chart ─────────────────────────────────────────────────────────────────────
PARTY_COLORS = {
    "DMK": "#e53e3e", "AIADMK": "#38a169", "TVK": "#9f7aea",
    "INC": "#63b3ed", "BJP": "#f6ad55", "PMK": "#ecc94b",
    "VCK": "#81e6d9", "NTK": "#a0aec0", "CPI": "#fc8181",
}

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.patch.set_facecolor("#0d0f14")
fig.suptitle("Q4 — Winning Margins: Top 5 (Landslides) & Bottom 5 (Razor-Edge)",
             color="white", fontsize=14, fontweight="bold")

panels = [
    (axes[0, 0], top5_21,  "🏆 Top 5 Margins — 2021",    "party"),
    (axes[0, 1], bot5_21,  "⚔️ Bottom 5 Margins — 2021",  "party"),
    (axes[1, 0], top5_26,  "🏆 Top 5 Margins — 2026",    "party"),
    (axes[1, 1], bot5_26,  "⚔️ Bottom 5 Margins — 2026",  "party"),
]

for ax, df, title, _ in panels:
    ax.set_facecolor("#141720")
    colors = [PARTY_COLORS.get(p, "#718096") for p in df["party"]]
    bars = ax.barh(df["constituency"], df["margin"], color=colors, height=0.55, edgecolor="none")
    for bar, (_, row) in zip(bars, df.iterrows()):
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                f"{int(row['margin']):,}", va="center", fontsize=8, color="white")
    ax.set_title(title, color="#f0a500", fontsize=11, fontweight="bold", pad=8)
    ax.tick_params(colors="white", labelsize=9)
    ax.spines[:].set_color("#2a2f40")
    ax.set_xlabel("Margin (votes)", color="#6b7280", fontsize=9)
    ax.tick_params(axis="x", colors="#6b7280")
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="x", color="#2a2f40", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q4_margins.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q4_margins.png")
print(f"✅ CSVs saved:  {OUT}/q4_margins_2021.csv  |  q4_margins_2026.csv")
