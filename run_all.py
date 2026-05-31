"""
run_all.py
==========
Tamil Nadu Elections 2021 vs 2026 — Full Merged Pipeline

Runs all 14 analysis scripts in order:
  00  Unified data loader (must run first)

  STORY CHAPTERS (Pipeline 1 — narrative deck)
  01  03_story_voteshare.py     Vote share state + regional
  02  04_story_flips.py         Seat flips Sankey (PNG + HTML)
  03  05_story_geography.py     Seats by region, margins distribution
  04  06_story_turnout.py       Turnout surge top 20
  05  07_story_gender.py        Gender turnout analysis
  06  08_story_women_nota.py    Women candidates + NOTA
  07  09_story_connection.py    Connective story: surge → TVK


  Q&A DEEP DIVES (Pipeline 2 — data questions)
  08  01_q1_turnout_top_bottom.py   Q1: Turnout top/bottom 5
  09  02_q2_same_party_streak.py    Q2: Same party both elections
  10  03_q3_biggest_flips.py        Q3: Biggest flip swings
  11  04_q4_margin_analysis.py      Q4: Winning margins
  12  05_q5_q6_vote_share.py        Q5+Q6: Vote share splits
  13  06_q7_nota_analysis.py        Q7: NOTA voting patterns
  14  07_q8_postal_correlation.py   Q8: Postal votes correlation
  15  08_q9_literacy_correlation.py Q9: Literacy correlation

Usage:
    python run_all.py               # run everything
    python run_all.py --story       # story chapters only (01–07)
    python run_all.py --qa          # Q&A deep dives only (08–15)
    python run_all.py --from 05     # resume from step 05 onwards

Folder structure expected:
    ./data/raw/          ← all raw CSV files here
    ./data/processed/    ← auto-created by step 00
    ./outputs/           ← auto-created
    ./outputs/charts/    ← all PNG charts saved here
    ./notebooks/         ← story scripts live here (01–07)
                           Q&A scripts live in root (08–15)

Requirements:
    pip install pandas numpy matplotlib scipy
    pip install plotly   (optional — for interactive Sankey HTML)
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ── Script registry ───────────────────────────────────────────────────────────
# Each entry: (step_label, relative_path_from_root, description, group)
SCRIPTS = [
    ("00", "00_data_loader.py",                      "Data loading & preprocessing",     "loader"),

    # Story chapters — live in notebooks/
    ("01", "notebooks/03_story_voteshare.py",        "Vote share state + regional",       "story"),
    ("02", "notebooks/04_story_flips.py",            "Seat flips — Sankey chart",         "story"),
    ("03", "notebooks/05_story_geography.py",        "Seats by region + margins dist.",   "story"),
    ("04", "notebooks/06_story_turnout.py",          "Turnout surge top 20",              "story"),
    ("05", "notebooks/07_story_gender.py",           "Gender turnout analysis",           "story"),
    ("06", "notebooks/08_story_women_nota.py",       "Women candidates + NOTA",           "story"),
    ("07", "notebooks/09_story_connection.py",       "Connective story: surge → TVK",     "story"),

  
    
    # Q&A deep dives — live in qa/
    ("08", "qa/01_q1_turnout_top_bottom.py",         "Q1 — Turnout top/bottom 5",         "qa"),
    ("09", "qa/02_q2_same_party_streak.py",          "Q2 — Same party streak",            "qa"),
    ("10", "qa/03_q3_biggest_flips.py",              "Q3 — Biggest flips",                "qa"),
    ("11", "qa/04_q4_margin_analysis.py",            "Q4 — Margin analysis",              "qa"),
    ("12", "qa/05_q5_q6_vote_share.py",              "Q5 + Q6 — Vote share splits",       "qa"),
    ("13", "qa/06_q7_nota_analysis.py",              "Q7 — NOTA analysis",                "qa"),
    ("14", "qa/07_q8_postal_correlation.py",         "Q8 — Postal correlation",           "qa"),
    ("15", "qa/08_q9_literacy_correlation.py",       "Q9 — Literacy correlation",         "qa"),
]

# ── Argument parsing ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="TN Election 2026 — merged pipeline runner")
group = parser.add_mutually_exclusive_group()
group.add_argument("--story", action="store_true",
                   help="Run only story chapter scripts (steps 01–07)")
group.add_argument("--qa",    action="store_true",
                   help="Run only Q&A deep-dive scripts (steps 08–15)")
parser.add_argument("--from", dest="from_step", metavar="STEP",
                    help="Resume from step number (e.g. --from 05)")
args = parser.parse_args()

# ── Filter scripts based on flags ─────────────────────────────────────────────
def select_scripts():
    selected = SCRIPTS[:]
    if args.story:
        # Always include loader; add story scripts
        selected = [s for s in SCRIPTS if s[3] in ("loader", "story")]
    elif args.qa:
        # Always include loader; add Q&A scripts
        selected = [s for s in SCRIPTS if s[3] in ("loader", "qa")]
    if args.from_step:
        start = args.from_step.zfill(2)
        selected = [s for s in selected if s[0] >= start]
    return selected

to_run = select_scripts()

# ── Banner ────────────────────────────────────────────────────────────────────
print("=" * 65)
print("TAMIL NADU ELECTIONS 2021 vs 2026 — FULL ANALYSIS PIPELINE")
if args.story:
    print("  Mode: Story chapters only")
elif args.qa:
    print("  Mode: Q&A deep dives only")
else:
    print("  Mode: Full pipeline (story + Q&A)")
if args.from_step:
    print(f"  Resuming from step {args.from_step}")
print(f"  Scripts to run: {len(to_run)}")
print("=" * 65)

# ── Run ───────────────────────────────────────────────────────────────────────
total_start = time.time()
passed, failed = [], []

prev_group = None
for step, rel_path, description, grp in to_run:
    # Print group header when group changes
    if grp != prev_group:
        if grp == "story":
            print("\n── STORY CHAPTERS ────────────────────────────────────────")
        elif grp == "qa":
            print("\n── Q&A DEEP DIVES ────────────────────────────────────────")
        prev_group = grp

    script_path = ROOT / rel_path
    if not script_path.exists():
        print(f"\n[{step}] ⚠  {description}")
        print(f"      SKIPPED — file not found: {rel_path}")
        failed.append((step, rel_path, "file not found"))
        continue

    print(f"\n[{step}] {description}")
    print(f"     {rel_path}")
    start = time.time()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(ROOT),
        capture_output=False,
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"     ✅ Done in {elapsed:.1f}s")
        passed.append(step)
    else:
        print(f"     ❌ FAILED (exit code {result.returncode})")
        failed.append((step, rel_path, f"exit code {result.returncode}"))

# ── Summary ───────────────────────────────────────────────────────────────────
total_elapsed = time.time() - total_start
print("\n" + "=" * 65)
print(f"PIPELINE COMPLETE  ({total_elapsed:.1f}s total)")
print(f"  Passed : {len(passed)}/{len(to_run)}")
if failed:
    print(f"  Failed : {len(failed)}")
    for step, path, reason in failed:
        print(f"    [{step}] {path}  —  {reason}")
print("=" * 65)

if not failed:
    print("""
Outputs:
  data/processed/      — all cleaned + derived CSV tables
  outputs/             — per-question result CSVs
  outputs/charts/      — all PNG charts (story + Q&A)
  outputs/charts/sankey_2021_to_2026.html  — interactive Sankey
""")
else:
    sys.exit(1)
