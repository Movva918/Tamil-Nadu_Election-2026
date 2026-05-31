"""
06_q7_nota_analysis.py
=======================
Q7 — Which constituency voted most for NOTA? (2021 and 2026)

Run after: 00_data_loader.py
Output:    ./outputs/q7_nota_analysis.csv
           ./outputs/charts/q7_nota.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

PROC = "./data/processed"
OUT  = "./outputs"
os.makedirs(f"{OUT}/charts", exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
nota = pd.read_csv(f"{PROC}/nota_analysis.csv")

# ── Top 10 each year ──────────────────────────────────────────────────────────
top10_21 = nota.nlargest(10, "nota_pct_21")[
    ["constituency", "nota_21", "nota_pct_21", "region"]
].reset_index(drop=True)
top10_26 = nota.nlargest(10, "nota_pct_26")[
    ["constituency", "nota_26", "nota_pct_26", "region"]
].reset_index(drop=True)

# ── Print ─────────────────────────────────────────────────────────────────────
state_nota_21 = nota["nota_21"].sum() / nota["tot_21"].sum() * 100
state_nota_26 = nota["nota_26"].sum() / nota["tot_26"].sum() * 100

print("=" * 60)
print("Q7 — NOTA ANALYSIS")
print("=" * 60)
print(f"\n  State-wide NOTA:  2021 = {state_nota_21:.3f}%  |  2026 = {state_nota_26:.3f}%")
print(f"  Change: {state_nota_26 - state_nota_21:+.3f}pp")

print("\n\nTOP 10 NOTA % — 2021")
print("-" * 55)
print(f"  {'#':<3} {'Constituency':<28} {'NOTA Votes':>10} {'NOTA %':>7}  Region")
for i, r in top10_21.iterrows():
    print(f"  {i+1:<3} {r['constituency']:<28} {r['nota_21']:>10,} {r['nota_pct_21']:>7.3f}%  {r['region']}")

print("\n\nTOP 10 NOTA % — 2026")
print("-" * 55)
print(f"  {'#':<3} {'Constituency':<28} {'NOTA Votes':>10} {'NOTA %':>7}  Region")
for i, r in top10_26.iterrows():
    print(f"  {i+1:<3} {r['constituency']:<28} {r['nota_26']:>10,} {r['nota_pct_26']:>7.3f}%  {r['region']}")

# ── Constituencies in both top-10 ────────────────────────────────────────────
both = set(top10_21["constituency"]) & set(top10_26["constituency"])
print(f"\n  In BOTH top-10 (persistent high-NOTA seats): {', '.join(both) if both else 'None'}")

# ── Save ──────────────────────────────────────────────────────────────────────
nota.sort_values("nota_pct_26", ascending=False).to_csv(f"{OUT}/q7_nota_analysis.csv", index=False)

# ── Chart ─────────────────────────────────────────────────────────────────────
REGION_COLORS = {
    "Chennai Metro": "#63b3ed", "North": "#6ee7b7", "Central": "#fcd34d",
    "Kongu": "#fca5a5", "Delta": "#c4b5fd", "South": "#fdba74",
}

# Use top 8 from 2021 and match their 2026 values
plot_labels = top10_21.head(8)["constituency"].tolist()
vals_21 = top10_21.head(8)["nota_pct_21"].tolist()
vals_26 = [nota[nota["constituency"] == c]["nota_pct_26"].values[0]
           if len(nota[nota["constituency"] == c]) > 0 else 0
           for c in plot_labels]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor("#0d0f14")

# Left: comparison bars
ax1.set_facecolor("#141720")
x = range(len(plot_labels))
w = 0.35
ax1.bar([i - w/2 for i in x], vals_21, width=w, label="2021 NOTA %",
        color="#a0aec0", alpha=0.85)
ax1.bar([i + w/2 for i in x], vals_26, width=w, label="2026 NOTA %",
        color="#fc8181", alpha=0.85)
ax1.set_xticks(list(x))
ax1.set_xticklabels(plot_labels, rotation=40, ha="right", fontsize=8, color="white")
ax1.set_ylabel("NOTA %", color="#9ca3af")
ax1.set_title("Top NOTA Constituencies: 2021 vs 2026", color="white", fontsize=11, fontweight="bold")
ax1.tick_params(axis="y", colors="#9ca3af")
ax1.spines[:].set_color("#2a2f40")
ax1.grid(axis="y", color="#2a2f40", linestyle="--", alpha=0.4)
ax1.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white", fontsize=9)

# Add state average lines
ax1.axhline(state_nota_21, color="#a0aec0", linestyle=":", linewidth=1.2,
            label=f"State avg 2021 ({state_nota_21:.2f}%)")
ax1.axhline(state_nota_26, color="#fc8181", linestyle=":", linewidth=1.2,
            label=f"State avg 2026 ({state_nota_26:.2f}%)")
ax1.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white", fontsize=8)

# Right: top 10 2026 horizontal bars
ax2.set_facecolor("#141720")
t26 = top10_26.sort_values("nota_pct_26")
colors_r = [REGION_COLORS.get(r, "#718096") for r in t26["region"]]
ax2.barh(t26["constituency"], t26["nota_pct_26"], color=colors_r, height=0.55)
for v, c in zip(t26["nota_pct_26"], t26["constituency"]):
    ax2.text(v + 0.01, c, f"{v:.3f}%", va="center", fontsize=8, color="white")
ax2.set_title("Top 10 NOTA % — 2026", color="white", fontsize=11, fontweight="bold")
ax2.tick_params(colors="white", labelsize=9)
ax2.spines[:].set_color("#2a2f40")
ax2.grid(axis="x", color="#2a2f40", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q7_nota.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q7_nota.png")
print(f"✅ CSV saved:   {OUT}/q7_nota_analysis.csv")
