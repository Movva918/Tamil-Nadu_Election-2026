"""
00_data_loader.py
=================
Tamil Nadu Elections 2021 vs 2026 — Unified Data Loader
Run this FIRST before any other script.

Combines Pipeline 1 (story notebooks) and Pipeline 2 (Q&A scripts) into a
single source of truth. All downstream scripts read from data/processed/ and
outputs/ — never from raw CSVs directly (except 07/08/09 story scripts that
are self-contained by design).

Requirements:
    pip install pandas numpy

Input files expected in ./data/raw/:
    Core:
        tn_2021_results.csv
        tn_2026_results.csv
        constituency_master.csv
    Supplementary (exported from ECI Excel via Power Query):
        gender_2021.csv       ← from 8-_Constituency_Data_Summary.xlsx
        voters_2026.csv       ← from 12_-_AC_Wise_Voters_Information_1778165153.xlsx
        electors_2026.csv     ← from 11_-_AC_Wise_Number_Of_Electors_1778165153.xlsx

Outputs written to ./data/processed/:
    winners_2021.csv          ← one row per AC, 2021 winner
    winners_2026.csv          ← one row per AC, 2026 winner
    turnout_master.csv        ← ac-level turnout_21, turnout_26, delta
    flip_table.csv            ← per-AC party 2021 vs 2026, flipped flag
    vote_share_ac.csv         ← per-AC party vote % both years
    state_share_pivot.csv     ← state-wide party vote % pivot (2021|2026|swing)
    region_share_pivot.csv    ← regional party vote % pivot
    vote_share_statewide.csv  ← long-format state vote share (for P1 charts)
    vote_share_by_region.csv  ← long-format regional vote share (for P1 charts)
    flips_per_ac.csv          ← per-AC flip detail (for P1 Sankey)
    flips_flow.csv            ← aggregated flow table (for P1 Sankey)
    nota_analysis.csv         ← per-AC NOTA votes and % both years

Output also written to ./outputs/:
    turnout_delta.csv         ← top-20 turnout surge (for 06_story_turnout.py)
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW  = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT  = ROOT / "outputs"

for d in [PROC, OUT, OUT / "charts"]:
    d.mkdir(parents=True, exist_ok=True)

# ── Validate required raw files are present ───────────────────────────────────
REQUIRED = [
    "tn_2021_results.csv",
    "tn_2026_results.csv",
    "constituency_master.csv",
    "gender_2021.csv",
    "voters_2026.csv",
    "electors_2026.csv",
]
missing = [f for f in REQUIRED if not (RAW / f).exists()]
if missing:
    print(f"\n❌ Missing raw files in data/raw/: {missing}")
    print("   Please add them before running.\n")
    raise SystemExit(1)

print("=" * 60)
print("UNIFIED DATA LOADER — Tamil Nadu 2021 vs 2026")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════
# 1. LOAD & CLEAN RAW RESULTS
# ═══════════════════════════════════════════════════════════════
print("\n[1/9] Loading raw results CSVs ...")
df21 = pd.read_csv(RAW / "tn_2021_results.csv")
df26 = pd.read_csv(RAW / "tn_2026_results.csv")

# Normalise party names
df26["party"] = df26["party"].str.strip()
df26.loc[df26["party"].str.lower() == "tavk", "party"] = "TVK"

master = pd.read_csv(RAW / "constituency_master.csv")

# Sanity checks (from P1 data_audit)
assert df21["ac_number"].nunique() == 234, f"2021: expected 234 ACs, got {df21['ac_number'].nunique()}"
assert df26["ac_number"].nunique() == 234, f"2026: expected 234 ACs, got {df26['ac_number'].nunique()}"
assert master["ac_number"].nunique() == 234, "master: expected 234 ACs"
print(f"  ✓ 2021: {len(df21):,} rows across 234 ACs")
print(f"  ✓ 2026: {len(df26):,} rows across 234 ACs")

# Name drift info (joining must always use ac_number)
names21 = df21[["ac_number", "constituency"]].drop_duplicates()
names26 = df26[["ac_number", "constituency"]].drop_duplicates()
joined  = names21.merge(names26, on="ac_number", suffixes=("_21", "_26"))
diff    = joined[joined["constituency_21"] != joined["constituency_26"]]
if len(diff):
    print(f"  ⚠  {len(diff)} ACs have different name spellings — always join on ac_number")

# ═══════════════════════════════════════════════════════════════
# 2. TURNOUT — 2026 from voters_2026.csv
# ═══════════════════════════════════════════════════════════════
print("\n[2/9] Loading 2026 turnout from voters_2026.csv ...")
ac_voters = pd.read_csv(RAW / "voters_2026.csv")
ac_voters.columns = ac_voters.columns.str.strip()
ac_voters = ac_voters.rename(columns=lambda c:
    "ac_number"  if ("AC" in c and "No" in c) else
    "turnout_26" if ("POLL" in c.upper() or "Poll" in c) else c)
ac_voters = ac_voters[["ac_number", "turnout_26"]].dropna()
ac_voters["ac_number"]  = pd.to_numeric(ac_voters["ac_number"],  errors="coerce")
ac_voters["turnout_26"] = pd.to_numeric(ac_voters["turnout_26"], errors="coerce")
ac_voters = ac_voters.dropna().astype({"ac_number": int})

# Total electors from electors_2026.csv
print("[2/9] Loading 2026 electors from electors_2026.csv ...")
ac_electors = pd.read_csv(RAW / "electors_2026.csv")
ac_electors.columns = ac_electors.columns.str.strip()
tot_col     = next((c for c in ac_electors.columns if "TOTAL" in c.upper() and "ELECTOR" in c.upper()), None)
ac_elec_col = next((c for c in ac_electors.columns if "AC" in c and "No" in c), None)

if tot_col and ac_elec_col:
    ac_electors = ac_electors[[ac_elec_col, tot_col]].copy()
    ac_electors.columns = ["ac_number", "total_electors_26"]
    ac_electors["ac_number"] = pd.to_numeric(
        ac_electors["ac_number"].dropna(), errors="coerce")
    ac_electors = ac_electors.dropna(subset=["ac_number"]).astype({"ac_number": int})
    iv_clean = ac_voters.merge(ac_electors, on="ac_number", how="left")
else:
    iv_clean = ac_voters.copy()
    iv_clean["total_electors_26"] = np.nan

print(f"  ✓ 2026 turnout loaded for {len(iv_clean)} ACs")

# ═══════════════════════════════════════════════════════════════
# 3. TURNOUT — 2021 from gender_2021.csv
# ═══════════════════════════════════════════════════════════════
print("\n[3/9] Loading 2021 turnout from gender_2021.csv ...")
t21_raw = pd.read_csv(RAW / "gender_2021.csv")
t21_raw.columns = t21_raw.columns.str.strip()
t21_raw = t21_raw.rename(columns=lambda c:
    "ac_number"         if ("AC" in c and "No" in c) else
    "turnout_21"        if ("POLL" in c.upper() or ("Polling" in c and "%" in c)) else
    "total_electors_21" if ("TOTAL" in c.upper() and "ELECTOR" in c.upper()) else
    "total_voters_21"   if ("TOTAL" in c.upper() and "VOTER" in c.upper()) else c)
t21_raw["ac_number"] = pd.to_numeric(
    t21_raw.get("ac_number", pd.Series(dtype=float)), errors="coerce")
t21_turnout = t21_raw[
    ["ac_number", "turnout_21"] +
    [c for c in ["total_electors_21", "total_voters_21"] if c in t21_raw.columns]
].dropna(subset=["ac_number"])
t21_turnout["ac_number"] = t21_turnout["ac_number"].astype(int)
print(f"  ✓ 2021 turnout loaded for {len(t21_turnout)} ACs")

# ═══════════════════════════════════════════════════════════════
# 4. WINNERS TABLE
# ═══════════════════════════════════════════════════════════════
print("\n[4/9] Building winners tables ...")

def get_winners(df, year):
    """One row per AC: winner candidate, party, votes, vote_pct, margin."""
    d = df[df["party"] != "NOTA"].copy()
    total   = d.groupby("ac_number")["votes"].sum().reset_index(name="total_valid")
    d_sorted = d.sort_values(["ac_number", "votes"], ascending=[True, False])
    d_sorted["rank"] = d_sorted.groupby("ac_number").cumcount() + 1
    winner  = d_sorted[d_sorted["rank"] == 1].copy()
    runner  = d_sorted[d_sorted["rank"] == 2][["ac_number", "votes"]].rename(
        columns={"votes": "runner_votes"})
    w = winner.merge(total, on="ac_number").merge(runner, on="ac_number", how="left")
    w["vote_pct"] = (w["votes"] / w["total_valid"] * 100).round(2)
    w["margin"]   = w["votes"] - w["runner_votes"]
    w["winner_pct"] = w["vote_pct"]
    w["margin_pct"] = (w["margin"] / w["total_valid"] * 100).round(2)
    w["year"]     = year
    # Add canonical party column used by P1 src module convention
    w["party_canonical"] = w["party"]
    return w[["ac_number", "constituency", "party", "party_canonical", "candidate",
              "votes", "runner_votes", "total_valid", "vote_pct", "winner_pct", "margin", "margin_pct",
              "region", "reserved", "year"]]

winners_21 = get_winners(df21, 2021)
winners_26 = get_winners(df26, 2026)
assert len(winners_21) == 234 and len(winners_26) == 234, "Expected 234 winners per year"
assert (winners_21["votes"] > winners_21["runner_votes"]).all(), "2021: negative margins found"
assert (winners_26["votes"] > winners_26["runner_votes"]).all(), "2026: negative margins found"
print(f"  ✓ 234 winners per year, all margins positive")

print("\n  Seat counts 2021:")
for party, n in winners_21["party"].value_counts().head(6).items():
    print(f"    {party:<10} {n}")
print("\n  Seat counts 2026:")
for party, n in winners_26["party"].value_counts().head(6).items():
    print(f"    {party:<10} {n}")

# ═══════════════════════════════════════════════════════════════
# 5. TURNOUT MASTER + TURNOUT DELTA
# ═══════════════════════════════════════════════════════════════
print("\n[5/9] Building turnout tables ...")
turnout = (
    winners_21[["ac_number", "constituency", "region", "reserved"]]
    .merge(t21_turnout[["ac_number", "turnout_21"]], on="ac_number")
    .merge(iv_clean[["ac_number", "turnout_26"]], on="ac_number")
)
turnout["delta"] = (turnout["turnout_26"] - turnout["turnout_21"]).round(2)

# turnout_delta.csv — used by 06_story_turnout.py
# Column names match what that script expects: constituency, region, delta,
# turnout_2021, turnout_2026
turnout_delta = turnout.rename(columns={
    "turnout_21": "turnout_2021",
    "turnout_26": "turnout_2026",
}).sort_values("delta", ascending=False)

print(f"  ✓ Turnout data built for {len(turnout)} ACs")

# ═══════════════════════════════════════════════════════════════
# 6. FLIP TABLE + FLOW (for P1 Sankey)
# ═══════════════════════════════════════════════════════════════
print("\n[6/9] Building flip tables ...")
flip = winners_21[["ac_number", "constituency", "party", "vote_pct", "region", "reserved"]].merge(
    winners_26[["ac_number", "party", "vote_pct", "margin"]], on="ac_number",
    suffixes=("_21", "_26"))
flip["flipped"]       = flip["party_21"] != flip["party_26"]
flip["vote_pct_diff"] = (flip["vote_pct_26"] - flip["vote_pct_21"]).abs().round(2)

total_flipped  = flip["flipped"].sum()
total_retained = (~flip["flipped"]).sum()
print(f"  ✓ {total_flipped} seats flipped ({total_flipped/234*100:.0f}%), "
      f"{total_retained} retained")

# flips_per_ac.csv — P1 Sankey input (needs winner_2021, winner_2026 column names)
flips_per_ac = flip.rename(columns={"party_21": "winner_2021", "party_26": "winner_2026"}).copy()

# flips_flow.csv — aggregated flow for Sankey
flips_flow = (
    flips_per_ac.groupby(["winner_2021", "winner_2026"])
    .size().reset_index(name="seats")
    .sort_values("seats", ascending=False)
)

# ═══════════════════════════════════════════════════════════════
# 7. VOTE SHARE (both P1 long-format and P2 pivot format)
# ═══════════════════════════════════════════════════════════════
print("\n[7/9] Building vote share tables ...")

MAJOR = ["DMK", "AIADMK", "TVK", "INC", "BJP", "PMK", "VCK",
         "CPI", "CPI(M)", "NTK", "NOTA"]

def compute_vote_share_ac(df, year):
    d = df.copy()
    d["party_grp"] = d["party"].apply(lambda p: p if p in MAJOR else "Others")
    total_ac = d.groupby("ac_number")["votes"].sum().reset_index(name="total_ac")
    g = d.groupby(["ac_number", "region", "party_grp"])["votes"].sum().reset_index()
    g = g.merge(total_ac, on="ac_number")
    g["vote_pct"] = (g["votes"] / g["total_ac"] * 100).round(3)
    g["year"] = year
    return g

def state_share(df, year):
    d = df.copy()
    d["party_grp"] = d["party"].apply(lambda p: p if p in MAJOR else "Others")
    total = d["votes"].sum()
    g = d.groupby("party_grp")["votes"].sum().reset_index()
    g["vote_pct"] = (g["votes"] / total * 100).round(2)
    g["year"] = year
    return g

def region_share(df, year):
    d = df.copy()
    d["party_grp"] = d["party"].apply(lambda p: p if p in MAJOR else "Others")
    total_r = d.groupby("region")["votes"].sum().rename("rtot")
    g = d.groupby(["region", "party_grp"])["votes"].sum().reset_index()
    g = g.merge(total_r, on="region")
    g["vote_pct"] = (g["votes"] / g["rtot"] * 100).round(2)
    g["year"] = year
    return g

# P2-style pivots (state_share_pivot, region_share_pivot)
state21 = state_share(df21, 2021)
state26 = state_share(df26, 2026)
state_share_df = pd.concat([state21, state26]).pivot_table(
    index="party_grp", columns="year", values="vote_pct").reset_index()
state_share_df.columns.name = None
state_share_df["swing"] = (state_share_df[2026] - state_share_df[2021]).round(2)

r21 = region_share(df21, 2021)
r26 = region_share(df26, 2026)
region_share_df = pd.concat([r21, r26]).pivot_table(
    index=["region", "party_grp"], columns="year", values="vote_pct").reset_index()
region_share_df.columns.name = None
region_share_df["swing"] = (region_share_df[2026] - region_share_df[2021]).round(2)

# P1-style long format (vote_share_statewide, vote_share_by_region)
# vote_share_statewide: party_grp + vote_share_pct + year (100% per year)
sw21 = state21.rename(columns={"vote_pct": "vote_share_pct", "party_grp": "display_party"})
sw26 = state26.rename(columns={"vote_pct": "vote_share_pct", "party_grp": "display_party"})
vote_share_statewide = pd.concat([sw21, sw26], ignore_index=True)

# vote_share_by_region: region + party_grp + vote_share_pct + year
rs21 = r21.rename(columns={"vote_pct": "vote_share_pct", "party_grp": "display_party"}).drop(columns=["rtot"])
rs26 = r26.rename(columns={"vote_pct": "vote_share_pct", "party_grp": "display_party"}).drop(columns=["rtot"])
vote_share_by_region = pd.concat([rs21, rs26], ignore_index=True)

# Sanity: all groups sum to 100%
for yr in (2021, 2026):
    total = vote_share_statewide[vote_share_statewide["year"] == yr]["vote_share_pct"].sum()
    assert abs(total - 100.0) < 0.1, f"State {yr} vote share sums to {total:.2f}"
print("  ✓ All vote-share groups sum to 100%")

# AC-level vote share
vs21 = compute_vote_share_ac(df21, 2021)
vs26 = compute_vote_share_ac(df26, 2026)
vote_share_ac = pd.concat([vs21, vs26], ignore_index=True)

# ═══════════════════════════════════════════════════════════════
# 8. NOTA ANALYSIS
# ═══════════════════════════════════════════════════════════════
print("\n[8/9] Building NOTA analysis ...")
nota21 = df21[df21["party"] == "NOTA"][["ac_number", "constituency", "votes", "region"]].rename(
    columns={"votes": "nota_21"})
nota26 = df26[df26["party"] == "NOTA"][["ac_number", "votes"]].rename(
    columns={"votes": "nota_26"})
tot21 = df21.groupby("ac_number")["votes"].sum().reset_index(name="tot_21")
tot26 = df26.groupby("ac_number")["votes"].sum().reset_index(name="tot_26")
nota = (nota21
        .merge(nota26, on="ac_number")
        .merge(tot21, on="ac_number")
        .merge(tot26, on="ac_number"))
nota["nota_pct_21"] = (nota["nota_21"] / nota["tot_21"] * 100).round(3)
nota["nota_pct_26"] = (nota["nota_26"] / nota["tot_26"] * 100).round(3)
nota["nota_delta"]  = (nota["nota_pct_26"] - nota["nota_pct_21"]).round(3)

state_nota_21 = nota["nota_21"].sum() / nota["tot_21"].sum() * 100
state_nota_26 = nota["nota_26"].sum() / nota["tot_26"].sum() * 100
print(f"  ✓ State-wide NOTA: 2021 = {state_nota_21:.3f}%  |  2026 = {state_nota_26:.3f}%  "
      f"(change: {state_nota_26 - state_nota_21:+.3f}pp)")

# ═══════════════════════════════════════════════════════════════
# 9. SAVE ALL FILES
# ═══════════════════════════════════════════════════════════════
print("\n[9/9] Saving all processed files ...")

saves = {
    # Core tables (used by both pipelines)
    PROC / "winners_2021.csv":         winners_21,
    PROC / "winners_2026.csv":         winners_26,
    PROC / "turnout_master.csv":       turnout,
    PROC / "flip_table.csv":           flip,
    PROC / "nota_analysis.csv":        nota,
    # P2-style pivots
    PROC / "vote_share_ac.csv":        vote_share_ac,
    PROC / "state_share_pivot.csv":    state_share_df,
    PROC / "region_share_pivot.csv":   region_share_df,
    # P1-style long format
    PROC / "vote_share_statewide.csv": vote_share_statewide,
    PROC / "vote_share_by_region.csv": vote_share_by_region,
    PROC / "flips_per_ac.csv":         flips_per_ac,
    PROC / "flips_flow.csv":           flips_flow,
    # outputs/ (used by story scripts)
    OUT  / "turnout_delta.csv":        turnout_delta,
}

for path, df in saves.items():
    df.to_csv(path, index=False)
    print(f"  ✓ {path.relative_to(ROOT)}")

print(f"""
{'='*60}
✅ Data loader complete — {len(saves)} files written

data/processed/
  winners_2021.csv          winners_2026.csv
  turnout_master.csv        flip_table.csv
  nota_analysis.csv         vote_share_ac.csv
  state_share_pivot.csv     region_share_pivot.csv
  vote_share_statewide.csv  vote_share_by_region.csv
  flips_per_ac.csv          flips_flow.csv

outputs/
  turnout_delta.csv
{'='*60}
""")
