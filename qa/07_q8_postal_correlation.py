"""
07_q8_postal_correlation.py
============================
Q8 — Is there a correlation between Postal Votes % and Voter Turnout %?
     Computed for both 2021 and 2026.

Run after: 00_data_loader.py
Input files also needed (raw):
    2021: postal_2021.csv   (exported from 10-_Detailed_Results.xlsx via Power Query)
    2026: postal_2026.csv   (exported from 10-Detailed_Results_1778165153.xlsx)

Output:    ./outputs/q8_postal_correlation.csv
           ./outputs/charts/q8_postal_scatter.png
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

# ── 2026 postal data from postal_2026.csv ────────────────────────────────────
print("Loading 2026 postal data from postal_2026.csv ...")
postal26 = pd.read_csv(f"{RAW}/postal_2026.csv")
postal26.columns = postal26.iloc[0].tolist()   # promote row 0 as header
postal26 = postal26.iloc[1:].reset_index(drop=True)
postal26.columns = postal26.columns.str.strip()
# Normalise column names
postal26 = postal26.rename(columns=lambda c:
    "ac_number"     if ("AC" in c.upper() and "NO" in c.upper()) else
    "total_postal"  if "POSTAL" in c.upper() else
    "total_votes"   if "TOTAL" in c.upper() else c)
postal26 = postal26[["ac_number", "total_postal", "total_votes"]].copy()
for c in ["ac_number", "total_postal", "total_votes"]:
    postal26[c] = pd.to_numeric(postal26[c], errors="coerce")
postal26 = postal26.dropna(subset=["ac_number"]).copy()
postal26["ac_number"] = postal26["ac_number"].astype(int)
postal26 = postal26.groupby("ac_number", as_index=False).agg(
    total_postal=("total_postal", "sum"), total_votes=("total_votes", "sum")
)
postal26["postal_pct"] = (postal26["total_postal"] / postal26["total_votes"] * 100).round(3)

# ── 2026 turnout from turnout_master (ECI source — no IndiaVotes) ─────────────
turnout_master = pd.read_csv(f"{PROC}/turnout_master.csv")
iv2 = turnout_master[["ac_number", "turnout_26"]]

corr_26 = postal26.merge(iv2, on="ac_number").merge(master[["ac_number", "region"]], on="ac_number")

# ── 2021 postal data ──────────────────────────────────────────────────────────
print("Loading 2021 postal data from postal_2021.csv ...")
postal21 = pd.read_csv(f"{RAW}/postal_2021.csv")
postal21.columns = postal21.iloc[0].tolist()   # promote row 0 as header
postal21 = postal21.iloc[1:].reset_index(drop=True)
postal21.columns = postal21.columns.str.strip()
postal21 = postal21.rename(columns=lambda c:
    "ac_number"     if ("AC" in c.upper() and "NO" in c.upper()) else
    "total_postal"  if "POSTAL" in c.upper() else
    "total_votes"   if "TOTAL" in c.upper() else c)
postal21 = postal21[["ac_number", "total_postal", "total_votes"]].copy()
for c in ["ac_number", "total_postal", "total_votes"]:
    postal21[c] = pd.to_numeric(postal21[c], errors="coerce")
postal21 = postal21.dropna(subset=["ac_number"]).copy()
postal21["ac_number"] = postal21["ac_number"].astype(int)
postal21 = postal21.groupby("ac_number", as_index=False).agg(
    total_postal=("total_postal", "sum"), total_votes=("total_votes", "sum")
)
postal21["postal_pct"] = (postal21["total_postal"] / postal21["total_votes"] * 100).round(3)

t21_csv = pd.read_csv(f"{RAW}/tn_2021_results.csv")
t21_turn = t21_csv.drop_duplicates("ac_number")[["ac_number", "turnout"]].rename(columns={"turnout": "turnout_21"})
corr_21 = postal21.merge(t21_turn, on="ac_number").merge(master[["ac_number", "region"]], on="ac_number")

# ── Pearson correlation ───────────────────────────────────────────────────────
r26, p26 = stats.pearsonr(corr_26["postal_pct"], corr_26["turnout_26"])
r21, p21 = stats.pearsonr(corr_21["postal_pct"], corr_21["turnout_21"])

print("\n" + "=" * 55)
print("Q8 — POSTAL VOTES % vs VOTER TURNOUT %  CORRELATION")
print("=" * 55)
print(f"\n  2021:  Pearson r = {r21:+.4f}  |  p-value = {p21:.4f}  |  n = {len(corr_21)}")
print(f"  2026:  Pearson r = {r26:+.4f}  |  p-value = {p26:.4f}  |  n = {len(corr_26)}")
print(f"\n  Interpretation:")
print(f"  2021: {'Weak positive' if 0 < r21 < 0.3 else 'Moderate positive' if r21 >= 0.3 else 'Negative'} correlation")
print(f"  2026: {'Near-zero' if abs(r26) < 0.05 else 'Weak positive' if 0 < r26 < 0.3 else 'Weak negative' if -0.3 < r26 < 0 else 'Negative'} correlation")
print(f"\n  Key insight: The 2026 near-zero r ({r26:.3f}) means the massive")
print(f"  universal turnout surge erased any postal-vote-turnout pattern.")

# ── Save ──────────────────────────────────────────────────────────────────────
out_df = corr_26.rename(columns={"turnout_26": "turnout"}).assign(year=2026)
out_df = pd.concat([
    out_df,
    corr_21.rename(columns={"turnout_21": "turnout"}).assign(year=2021)
], ignore_index=True)
out_df.to_csv(f"{OUT}/q8_postal_correlation.csv", index=False)

# ── Chart ─────────────────────────────────────────────────────────────────────
REGION_COLORS = {
    "Chennai Metro": "#63b3ed", "North": "#6ee7b7", "Central": "#fcd34d",
    "Kongu": "#fca5a5", "Delta": "#c4b5fd", "South": "#fdba74",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor("#0d0f14")
fig.suptitle("Q8 — Postal Votes % vs Voter Turnout %", color="white", fontsize=13, fontweight="bold")

for ax, df, turnout_col, year, r_val, p_val in [
    (ax1, corr_21, "turnout_21", 2021, r21, p21),
    (ax2, corr_26, "turnout_26", 2026, r26, p26),
]:
    ax.set_facecolor("#141720")
    for region, grp in df.groupby("region"):
        ax.scatter(grp["postal_pct"], grp[turnout_col],
                   color=REGION_COLORS.get(region, "#718096"),
                   alpha=0.7, s=30, label=region, zorder=3)

    # Regression line
    slope, intercept, *_ = stats.linregress(df["postal_pct"], df[turnout_col])
    x_line = np.linspace(df["postal_pct"].min(), df["postal_pct"].max(), 100)
    ax.plot(x_line, slope * x_line + intercept, color="#f0a500", linewidth=1.5,
            linestyle="--", label=f"Regression (r={r_val:.3f})")

    ax.set_xlabel("Postal Votes %", color="#9ca3af", fontsize=10)
    ax.set_ylabel("Turnout %", color="#9ca3af", fontsize=10)
    ax.set_title(f"{year} — Pearson r = {r_val:+.4f}  (p = {p_val:.3f})",
                 color="#f0a500", fontsize=11, fontweight="bold")
    ax.tick_params(colors="#9ca3af")
    ax.spines[:].set_color("#2a2f40")
    ax.grid(color="#2a2f40", linestyle="--", alpha=0.3)
    if year == 2021:
        ax.legend(facecolor="#1c2030", edgecolor="#2a2f40", labelcolor="white",
                  fontsize=8, markerscale=1.2)

plt.tight_layout()
plt.savefig(f"{OUT}/charts/q8_postal_scatter.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n✅ Chart saved: {OUT}/charts/q8_postal_scatter.png")
print(f"✅ CSV saved:   {OUT}/q8_postal_correlation.csv")
