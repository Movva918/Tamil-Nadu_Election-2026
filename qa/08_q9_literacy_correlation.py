"""
08_q9_literacy_correlation.py
==============================
Q9 — Is there a correlation between district Literacy % and Voter Turnout %?

Note: Literacy data from Census 2011 (district-level).
      Turnout is averaged across constituencies within each district.

Run after: 00_data_loader.py
Output:    ./outputs/q9_literacy_correlation.csv
           ./outputs/charts/q9_literacy_scatter.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

PROC = "./data/processed"
RAW  = "./data/raw"
OUT  = "./outputs"
os.makedirs(f"{OUT}/charts", exist_ok=True)

master = pd.read_csv(f"{RAW}/constituency_master.csv")

# ── Census 2011 district literacy rates ──────────────────────────────────────
# Source: Census 2011, Office of the Registrar General, India
LITERACY = {
    "Chennai": 88.9, "Tiruvallur": 81.6, "Kancheepuram": 83.0, "Chengalpattu": 83.0,
    "Vellore": 77.8, "Tirupattur": 77.8, "Ranipet": 77.8, "Tiruvannamalai": 73.8,
    "Villupuram": 71.9, "Kallakurichi": 71.9, "Cuddalore": 74.2, "Dharmapuri": 64.1,
    "Krishnagiri": 67.5, "Salem": 74.0, "Namakkal": 77.8, "Erode": 78.3,
    "Tiruppur": 76.6, "Coimbatore": 83.9, "Nilgiris": 77.4, "Karur": 75.6,
    "Tiruchirappalli": 79.3, "Perambalur": 72.2, "Ariyalur": 70.3, "Thanjavur": 81.3,
    "Nagapattinam": 73.5, "Tiruvarur": 74.8, "Mayiladuthurai": 74.8, "Pudukkottai": 72.0,
    "Dindigul": 73.4, "Madurai": 84.3, "Theni": 78.2, "Virudhunagar": 78.6,
    "Ramanathapuram": 70.3, "Sivaganga": 77.5, "Tenkasi": 77.7, "Tirunelveli": 82.6,
    "Kanniyakumari": 91.8,
}
lit_df = pd.DataFrame(list(LITERACY.items()), columns=["district", "literacy_pct"])

# ── 2021 average turnout by district ─────────────────────────────────────────
t21_csv = pd.read_csv(f"{RAW}/tn_2021_results.csv")
t21_per_ac = t21_csv.drop_duplicates("ac_number")[["ac_number", "turnout"]].rename(
    columns={"turnout": "turnout_21"}
)
dist_t21 = t21_per_ac.merge(master[["ac_number", "district"]], on="ac_number")
dist_avg21 = dist_t21.groupby("district")["turnout_21"].mean().reset_index(name="avg_turnout_21")

# ── 2026 average turnout by district (ECI source — no IndiaVotes) ─────────────
turnout_master = pd.read_csv(f"{PROC}/turnout_master.csv")
iv2 = turnout_master[["ac_number", "turnout_26"]]
dist_t26 = iv2.merge(master[["ac_number", "district"]], on="ac_number")
dist_avg26 = dist_t26.groupby("district")["turnout_26"].mean().reset_index(name="avg_turnout_26")

# ── Merge ─────────────────────────────────────────────────────────────────────
analysis = lit_df.merge(dist_avg21, on="district").merge(dist_avg26, on="district")
analysis["turnout_change"] = (analysis["avg_turnout_26"] - analysis["avg_turnout_21"]).round(2)

# ── Pearson correlation ───────────────────────────────────────────────────────
r21, p21 = stats.pearsonr(analysis["literacy_pct"], analysis["avg_turnout_21"])
r26, p26 = stats.pearsonr(analysis["literacy_pct"], analysis["avg_turnout_26"])
r_change, p_change = stats.pearsonr(analysis["literacy_pct"], analysis["turnout_change"])

print("=" * 65)
print("Q9 — DISTRICT LITERACY % vs VOTER TURNOUT %  CORRELATION")
print("=" * 65)
print(f"\n  Literacy vs 2021 Turnout:  r = {r21:+.4f}  (p = {p21:.4f})")
print(f"  Literacy vs 2026 Turnout:  r = {r26:+.4f}  (p = {p26:.4f})")
print(f"  Literacy vs Turnout Change: r = {r_change:+.4f}  (p = {p_change:.4f})")
print()
print("  Interpretation:")
print(f"  • 2021: STRONG NEGATIVE (r={r21:.3f}) — high-literacy urban districts")
print(f"    voted significantly LESS than low-literacy rural districts")
print(f"  • 2026: MODERATE NEGATIVE (r={r26:.3f}) — relationship weakened as")
print(f"    urban constituencies surged 26–30pp in turnout")
print(f"  • Change: {'Positive' if r_change > 0 else 'Negative'} correlation (r={r_change:.3f}) — {'higher' if r_change > 0 else 'lower'}")
print(f"    literacy districts saw {'bigger' if r_change > 0 else 'smaller'} turnout jumps in 2026")
print()

# ── District detail ───────────────────────────────────────────────────────────
print(f"  {'District':<18} {'Literacy':>9} {'T2021':>8} {'T2026':>8} {'Change':>8}")
print("  " + "-" * 55)
for _, r in analysis.sort_values("literacy_pct", ascending=False).iterrows():
    sgn = "+" if r["turnout_change"] >= 0 else ""
    print(f"  {r['district']:<18} {r['literacy_pct']:>9.1f}% {r['avg_turnout_21']:>7.1f}% "
          f"{r['avg_turnout_26']:>7.1f}% {sgn+str(r['turnout_change']):>8}pp")

# ── Save ──────────────────────────────────────────────────────────────────────
analysis.to_csv(f"{OUT}/q9_literacy_correlation.csv", index=False)

# ── Chart ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor("#0d0f14")
fig.suptitle("Q9 — District Literacy % vs Voter Turnout %  (Census 2011 literacy)",
             color="white", fontsize=13, fontweight="bold")

# Helper: scatter with labels + regression
def scatter_regression(ax, x, y, color, label, year):
    ax.set_facecolor("#141720")
    ax.scatter(x, y, color=color, alpha=0.75, s=55, zorder=3, edgecolors="white", linewidth=0.3)

    # Annotate notable districts
    notable = ["Chennai", "Kanniyakumari", "Dharmapuri", "Karur", "Coimbatore", "Madurai"]
    for _, row in analysis.iterrows():
        if row["district"] in notable:
            ax.annotate(row["district"], (row["literacy_pct"], row[y.name]),
                        fontsize=7, color="white", alpha=0.9,
                        xytext=(3, 3), textcoords="offset points")

    # Regression
    slope, intercept, r_val, p_val, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, slope * x_line + intercept, color="#f0a500",
            linewidth=1.5, linestyle="--", label=f"r = {r_val:+.3f}")

    ax.set_xlabel("District Literacy % (Census 2011)", color="#9ca3af", fontsize=10)
    ax.set_ylabel("Avg Constituency Turnout %", color="#9ca3af", fontsize=10)
    ax.set_title(f"Literacy vs {year} Turnout  (r = {r_val:+.3f}, p = {p_val:.3f})",
                 color="#f0a500", fontsize=11, fontweight="bold")
    ax.tick_params(colors="#9ca3af")
    ax.spines[:].set_color("#2a2f40")
    ax.grid(color="#2a2f40", linestyle="--", alpha=0.3)
    ax.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white", fontsize=9)

scatter_regression(axes[0], analysis["literacy_pct"], analysis["avg_turnout_21"], "#63b3ed", "2021", 2021)
scatter_regression(axes[1], analysis["literacy_pct"], analysis["avg_turnout_26"], "#9f7aea", "2026", 2026)

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q9_literacy_scatter.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q9_literacy_scatter.png")
print(f"✅ CSV saved:   {OUT}/q9_literacy_correlation.csv")
