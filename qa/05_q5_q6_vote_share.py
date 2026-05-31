"""
05_q5_q6_vote_share.py
=======================
Q5 — % Split of party votes at REGIONAL level (2021 vs 2026)
Q6 — % Split of party votes at STATE level   (2021 vs 2026)

Run after: 00_data_loader.py
Output:    ./outputs/q5_regional_share.csv
           ./outputs/q6_state_share.csv
           ./outputs/charts/q5_regional_heatmap.png
           ./outputs/charts/q6_state_swing.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os

PROC = "./data/processed"
OUT  = "./outputs"
os.makedirs(f"{OUT}/charts", exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
state_df  = pd.read_csv(f"{PROC}/state_share_pivot.csv")
region_df = pd.read_csv(f"{PROC}/region_share_pivot.csv")

# ── Q6 — State level ──────────────────────────────────────────────────────────
print("=" * 65)
print("Q6 — STATE-WIDE VOTE SHARE  (2021 vs 2026)")
print("=" * 65)
print(f"\n{'Party':<10} {'2021 %':>8} {'2026 %':>8} {'Swing':>8}")
print("-" * 40)
state_sorted = state_df.sort_values('2026', ascending=False, na_position="last")
for _, r in state_sorted.iterrows():
    v21  = f"{r['2021']:.2f}%" if pd.notna(r['2021']) else "New"
    v26  = f"{r['2026']:.2f}%"
    swg  = f"{r['swing']:+.2f}pp" if pd.notna(r["swing"]) else "—"
    print(f"  {r['party_grp']:<10} {v21:>8} {v26:>8} {swg:>8}")

# ── Q5 — Regional level ───────────────────────────────────────────────────────
print("\n\n" + "=" * 65)
print("Q5 — REGIONAL VOTE SHARE  (2021 vs 2026)")
print("=" * 65)
for region in ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]:
    sub = region_df[region_df["region"] == region].sort_values('2026', ascending=False, na_position="last")
    print(f"\n  ── {region} ──")
    print(f"  {'Party':<10} {'2021 %':>8} {'2026 %':>8} {'Swing':>8}")
    print("  " + "-" * 40)
    for _, r in sub.iterrows():
        v21 = f"{r['2021']:.2f}%" if pd.notna(r['2021']) else "New"
        v26 = f"{r['2026']:.2f}%"
        swg = f"{r['swing']:+.2f}pp" if pd.notna(r["swing"]) else "—"
        print(f"  {r['party_grp']:<10} {v21:>8} {v26:>8} {swg:>8}")

# ── Save ──────────────────────────────────────────────────────────────────────
state_df.to_csv(f"{OUT}/q6_state_share.csv", index=False)
region_df.to_csv(f"{OUT}/q5_regional_share.csv", index=False)

# ── Chart Q6: State swing diverging bar ───────────────────────────────────────
PARTY_COLORS = {
    "DMK": "#e53e3e", "AIADMK": "#38a169", "TVK": "#9f7aea",
    "INC": "#63b3ed", "BJP": "#f6ad55", "PMK": "#ecc94b",
    "VCK": "#81e6d9", "NTK": "#a0aec0", "CPI": "#fc8181",
    "CPI(M)": "#b794f4", "NOTA": "#718096", "Others": "#4a5568",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor("#0d0f14")

# Left: 2021 vs 2026 grouped bar
ax1.set_facecolor("#141720")
plot_df = state_sorted[state_sorted['2026'].notna()].head(10)
x = range(len(plot_df))
w = 0.35
ax1.bar([i - w/2 for i in x], plot_df['2021'].fillna(0), width=w,
        label="2021", color="#4a5568", alpha=0.85)
ax1.bar([i + w/2 for i in x], plot_df['2026'], width=w,
        label="2026", color=[PARTY_COLORS.get(p, "#718096") for p in plot_df['party_grp']],
        alpha=0.9)
ax1.set_xticks(list(x))
ax1.set_xticklabels(plot_df['party_grp'], rotation=0, color="white", fontsize=10)
ax1.set_ylabel("Vote Share %", color="#9ca3af")
ax1.set_title("State-wide Vote Share: 2021 vs 2026", color="white", fontsize=12, fontweight="bold")
ax1.tick_params(axis="y", colors="#9ca3af")
ax1.spines[:].set_color("#2a2f40")
ax1.grid(axis="y", color="#2a2f40", linestyle="--", alpha=0.4)
ax1.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white")

# Right: swing diverging bar (exclude TVK — no 2021 base)
ax2.set_facecolor("#141720")
swing_df = state_df[pd.notna(state_df["swing"])].sort_values("swing")
colors = ["#68d391" if v >= 0 else "#fc8181" for v in swing_df["swing"]]
ax2.barh(swing_df['party_grp'], swing_df["swing"], color=colors, height=0.55)
ax2.axvline(0, color="#6b7280", linewidth=0.8)
for _, r in swing_df.iterrows():
    sgn = "+" if r["swing"] >= 0 else ""
    ax2.text(r["swing"] + (0.1 if r["swing"] >= 0 else -0.1),
             r['party_grp'], f"{sgn}{r['swing']:.1f}pp",
             va="center", ha="left" if r["swing"] >= 0 else "right",
             fontsize=8, color="white")
ax2.set_title("Vote Share Swing 2021→2026 (pp)", color="white", fontsize=12, fontweight="bold")
ax2.tick_params(colors="white", labelsize=10)
ax2.spines[:].set_color("#2a2f40")
ax2.grid(axis="x", color="#2a2f40", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q6_state_swing.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()

# ── Chart Q5: Regional heatmap ────────────────────────────────────────────────
REGIONS  = ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]
PARTIES  = ["TVK", "DMK", "AIADMK", "BJP", "INC", "PMK", "VCK", "NTK"]

def make_heatmap(year_col, title, ax):
    matrix = []
    for party in PARTIES:
        row = []
        for region in REGIONS:
            sub = region_df[(region_df["region"] == region) & (region_df['party_grp'] == party)]
            val = sub[year_col].values[0] if len(sub) > 0 and pd.notna(sub[year_col].values[0]) else 0
            row.append(val)
        matrix.append(row)
    mat = np.array(matrix, dtype=float)
    im = ax.imshow(mat, cmap="YlOrRd", aspect="auto", vmin=0, vmax=50)
    ax.set_xticks(range(len(REGIONS)));  ax.set_xticklabels(REGIONS, rotation=30, ha="right", color="white", fontsize=8)
    ax.set_yticks(range(len(PARTIES)));  ax.set_yticklabels(PARTIES, color="white", fontsize=9)
    for i in range(len(PARTIES)):
        for j in range(len(REGIONS)):
            val = mat[i, j]
            if val > 0:
                ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=7,
                        color="black" if val > 25 else "white")
    ax.set_title(title, color="white", fontsize=11, fontweight="bold")
    return im

fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 6))
fig2.patch.set_facecolor("#0d0f14")
ax1.set_facecolor("#141720"); ax2.set_facecolor("#141720")
make_heatmap('2021', "Party Vote Share by Region — 2021", ax1)
im = make_heatmap('2026', "Party Vote Share by Region — 2026", ax2)
plt.colorbar(im, ax=ax2, label="Vote %", shrink=0.8)
fig2.suptitle("Q5 — Regional Party Vote Share Heatmap (2021 vs 2026)",
              color="white", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/charts/q5_regional_heatmap.png", dpi=150, bbox_inches="tight",
            facecolor=fig2.get_facecolor())
plt.close()

print(f"\n✅ Charts saved: {OUT}/charts/q5_regional_heatmap.png  |  q6_state_swing.png")
print(f"✅ CSVs saved:   {OUT}/q5_regional_share.csv  |  q6_state_share.csv")
