"""
03_q3_biggest_flips.py
=======================
Q3 — Constituencies that voted DIFFERENT parties in 2021 vs 2026
      Top 10 by absolute difference in winner vote % between elections

Run after: 00_data_loader.py
Output:    ./outputs/q3_biggest_flips.csv
           ./outputs/q3_all_flips.csv
           ./outputs/charts/q3_flips.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

PROC = "./data/processed"
OUT  = "./outputs"
os.makedirs(f"{OUT}/charts", exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
flip = pd.read_csv(f"{PROC}/flip_table.csv")

flipped = flip[flip["flipped"] == True].copy()
flipped = flipped.sort_values("vote_pct_diff", ascending=False).reset_index(drop=True)
flipped["rank"] = flipped.index + 1

top10 = flipped.head(10)

# ── Print ─────────────────────────────────────────────────────────────────────
total_flipped = flipped.shape[0]
total_retained = flip[flip["flipped"] == False].shape[0]

print("=" * 80)
print(f"Q3 — CONSTITUENCIES THAT FLIPPED PARTY  ({total_flipped} flipped, {total_retained} retained)")
print("     Top 10 by |winner vote % 2026 − winner vote % 2021|")
print("=" * 80)
print(f"\n{'#':<3} {'Constituency':<28} {'2021 Party':>10} {'2021 %':>7} {'2026 Party':>10} {'2026 %':>7} {'Swing':>8} {'Region':<14}")
print("-" * 80)
for _, r in top10.iterrows():
    diff_str = f"-{r['vote_pct_diff']:.2f}pp"
    print(f"{r['rank']:<3} {r['constituency']:<28} {r['party_21']:>10} {r['vote_pct_21']:>7.2f}% "
          f"{r['party_26']:>10} {r['vote_pct_26']:>7.2f}% {diff_str:>8} {r['region']:<14}")

# ── Flip summary by region ────────────────────────────────────────────────────
print("\n\nFLIP SUMMARY BY REGION:")
print("-" * 50)
region_summary = flipped.groupby("region").agg(
    flipped_seats=("ac_number", "count"),
    avg_swing=("vote_pct_diff", "mean")
).reset_index().sort_values("flipped_seats", ascending=False)

for _, r in region_summary.iterrows():
    print(f"  {r['region']:<18} {r['flipped_seats']:>3} seats flipped  |  avg swing {r['avg_swing']:.1f}pp")

# ── Flip summary by party transition ─────────────────────────────────────────
print("\n\nTOP PARTY TRANSITIONS:")
print("-" * 50)
transitions = flipped.groupby(["party_21", "party_26"]).size().reset_index(name="seats")
transitions = transitions.sort_values("seats", ascending=False).head(10)
for _, r in transitions.iterrows():
    print(f"  {r['party_21']:>8} → {r['party_26']:<8}  {r['seats']:>3} seats")

# ── Save ──────────────────────────────────────────────────────────────────────
top10.to_csv(f"{OUT}/q3_biggest_flips.csv", index=False)
flipped.to_csv(f"{OUT}/q3_all_flips.csv", index=False)

# ── Chart ─────────────────────────────────────────────────────────────────────
PARTY_COLORS = {
    "DMK": "#e53e3e", "AIADMK": "#38a169", "TVK": "#9f7aea",
    "INC": "#63b3ed", "BJP": "#f6ad55", "PMK": "#ecc94b",
    "VCK": "#81e6d9", "NTK": "#a0aec0", "CPI": "#fc8181",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={"width_ratios": [3, 1]})
fig.patch.set_facecolor("#0d0f14")

# Left: top 10 flips
ax1.set_facecolor("#141720")
labels = [r["constituency"] for _, r in top10.iterrows()]
pct21  = [r["vote_pct_21"] for _, r in top10.iterrows()]
pct26  = [r["vote_pct_26"] for _, r in top10.iterrows()]
col21  = [PARTY_COLORS.get(r["party_21"], "#718096") for _, r in top10.iterrows()]
col26  = [PARTY_COLORS.get(r["party_26"], "#718096") for _, r in top10.iterrows()]

y = list(range(len(labels)))[::-1]
ax1.barh([i + 0.2 for i in y], pct21, height=0.35, color=col21, alpha=0.6, label="2021 winner %")
ax1.barh([i - 0.2 for i in y], pct26, height=0.35, color=col26, alpha=0.9, label="2026 winner %")
ax1.set_yticks(y)
ax1.set_yticklabels(labels, fontsize=9, color="white")
ax1.set_xlabel("Winner Vote %", color="#9ca3af", fontsize=10)
ax1.set_title("Top 10 Flipped Constituencies by Vote % Swing\n(darker bar = 2026 winner)",
              color="white", fontsize=11, fontweight="bold")
ax1.tick_params(axis="x", colors="#9ca3af")
ax1.spines[:].set_color("#2a2f40")
ax1.grid(axis="x", color="#2a2f40", linestyle="--", alpha=0.4)

# Annotate swing
for i, (_, r) in enumerate(top10.iterrows()):
    ax1.text(max(r["vote_pct_21"], r["vote_pct_26"]) + 0.5,
             y[i], f"−{r['vote_pct_diff']:.1f}pp",
             va="center", fontsize=8, color="#fc8181")

# Party legend
shown = set()
for p, c in PARTY_COLORS.items():
    if p in flipped["party_21"].values or p in flipped["party_26"].values:
        if p not in shown:
            shown.add(p)
ax1.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white", fontsize=9)

# Right: flips by region
ax2.set_facecolor("#141720")
REGION_COLORS = {
    "Chennai Metro": "#63b3ed", "North": "#6ee7b7", "Central": "#fcd34d",
    "Kongu": "#fca5a5", "Delta": "#c4b5fd", "South": "#fdba74",
}
reg_counts = region_summary.sort_values("flipped_seats")
colors_r = [REGION_COLORS.get(r, "#718096") for r in reg_counts["region"]]
ax2.barh(reg_counts["region"], reg_counts["flipped_seats"], color=colors_r, height=0.55)
ax2.set_title("Flips by Region", color="white", fontsize=11, fontweight="bold")
ax2.tick_params(colors="white", labelsize=9)
ax2.spines[:].set_color("#2a2f40")
for v, label in zip(reg_counts["flipped_seats"], reg_counts["region"]):
    ax2.text(v + 0.3, label, str(v), va="center", fontsize=9, color="white")

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q3_flips.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q3_flips.png")
print(f"✅ CSVs saved:  {OUT}/q3_biggest_flips.csv  |  q3_all_flips.csv")
