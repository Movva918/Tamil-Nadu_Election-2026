"""
02_q2_same_party_streak.py
===========================
Q2 — Constituencies that elected the SAME party in both 2021 and 2026
      Ranked by winning party's vote % in 2026

Run after: 00_data_loader.py
Output:    ./outputs/q2_same_party_streak.csv
           ./outputs/charts/q2_same_party.png
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

# ── Build same-party table ────────────────────────────────────────────────────
merged = w21[["ac_number", "constituency", "party", "vote_pct", "region", "reserved"]].merge(
    w26[["ac_number", "party", "vote_pct"]], on="ac_number", suffixes=("_21", "_26")
)
same = merged[merged["party_21"] == merged["party_26"]].copy()
same = same.sort_values("vote_pct_26", ascending=False).reset_index(drop=True)
same["rank"]       = same.index + 1
same["pct_change"] = (same["vote_pct_26"] - same["vote_pct_21"]).round(2)

# ── Print ─────────────────────────────────────────────────────────────────────
print("=" * 70)
print(f"Q2 — SAME PARTY ELECTED BOTH 2021 AND 2026  ({len(same)} constituencies)")
print("     Ranked by 2026 winner vote %")
print("=" * 70)
print(f"\n{'#':<4} {'Constituency':<28} {'Party':<8} {'Region':<15} {'2021 %':>7} {'2026 %':>7} {'Change':>8}")
print("-" * 70)
for _, r in same.iterrows():
    sgn = "+" if r["pct_change"] >= 0 else ""
    print(f"{r['rank']:<4} {r['constituency']:<28} {r['party_21']:<8} {r['region']:<15} "
          f"{r['vote_pct_21']:>7.2f} {r['vote_pct_26']:>7.2f} {sgn+str(r['pct_change']):>8}pp")

# ── Save ──────────────────────────────────────────────────────────────────────
same.to_csv(f"{OUT}/q2_same_party_streak.csv", index=False)

# ── Chart — top 15 ───────────────────────────────────────────────────────────
PARTY_COLORS = {
    "DMK": "#e53e3e", "AIADMK": "#38a169", "TVK": "#9f7aea",
    "INC": "#63b3ed", "BJP": "#f6ad55", "PMK": "#ecc94b",
    "VCK": "#81e6d9", "NTK": "#a0aec0", "CPI": "#fc8181",
}

top15 = same.head(15)
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor("#0d0f14")
ax.set_facecolor("#141720")

x = range(len(top15))
w = 0.35
bars1 = ax.bar([i - w/2 for i in x], top15["vote_pct_21"], width=w,
               label="2021 vote %", color="#4a5568", alpha=0.85, zorder=3)
bars2 = ax.bar([i + w/2 for i in x], top15["vote_pct_26"], width=w,
               label="2026 vote %",
               color=[PARTY_COLORS.get(p, "#718096") for p in top15["party_21"]],
               alpha=0.9, zorder=3)

ax.set_xticks(list(x))
ax.set_xticklabels(
    [f"{r['constituency']}\n({r['party_21']})" for _, r in top15.iterrows()],
    rotation=45, ha="right", fontsize=8, color="white"
)
ax.set_ylabel("Vote Share %", color="#9ca3af", fontsize=10)
ax.set_title(
    f"Q2 — Constituencies That Voted Same Party in 2021 & 2026 (Top 15 by 2026 vote %)\n"
    f"Total: {len(same)} of 234 constituencies retained same party",
    color="white", fontsize=11, fontweight="bold", pad=12
)
ax.tick_params(axis="y", colors="#9ca3af")
ax.spines[:].set_color("#2a2f40")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_ylim(0, 80)
ax.grid(axis="y", color="#2a2f40", linestyle="--", alpha=0.5, zorder=0)
ax.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white", fontsize=9)

# Annotate change arrows
for bar1, bar2, (_, row) in zip(bars1, bars2, top15.iterrows()):
    chg = row["vote_pct_26"] - row["vote_pct_21"]
    color = "#68d391" if chg >= 0 else "#fc8181"
    ax.annotate("", xy=(bar2.get_x() + bar2.get_width() / 2, bar2.get_height()),
                xytext=(bar1.get_x() + bar1.get_width() / 2, bar1.get_height()),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2))

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q2_same_party.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q2_same_party.png")
print(f"✅ CSV saved:   {OUT}/q2_same_party_streak.csv")
