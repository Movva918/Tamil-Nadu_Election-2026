"""
Notebook 03 — Story 1: Vote share
=================================

Produces:
- data/processed/vote_share_statewide.csv
- data/processed/vote_share_by_region.csv
- outputs/charts/voteshare_statewide_neutral.png  (slide 3)
- outputs/charts/voteshare_by_region.png          (slide 4)

The headline finding: TVK pulled 34.9% of the state-wide vote and 31-47%
in every region. DMK and AIADMK fell in all six regions.
"""

# %%
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt
from src import load_results, vote_share
from src.charts import chart_voteshare_statewide, chart_voteshare_by_region

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CHARTS = ROOT / "outputs" / "charts"
PROCESSED.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

# %% Load cleaned data
df21 = load_results(2021)
df26 = load_results(2026)

# %% Compute state-wide and regional vote share
sw = pd.concat([
    vote_share(df21).assign(year=2021),
    vote_share(df26).assign(year=2026),
], ignore_index=True)
sw.to_csv(PROCESSED / "vote_share_statewide.csv", index=False)

rs = pd.concat([
    vote_share(df21, by=["region"]).assign(year=2021),
    vote_share(df26, by=["region"]).assign(year=2026),
], ignore_index=True)
rs.to_csv(PROCESSED / "vote_share_by_region.csv", index=False)

# %% Sanity: every group sums to 100%
for yr in (2021, 2026):
    total = sw[sw["year"] == yr]["vote_share_pct"].sum()
    assert abs(total - 100.0) < 0.01, f"state {yr} sums to {total}"
for yr in (2021, 2026):
    for region in rs["region"].unique():
        total = rs[(rs["year"] == yr) & (rs["region"] == region)]["vote_share_pct"].sum()
        assert abs(total - 100.0) < 0.01, f"{region} {yr} sums to {total}"
print("[ok] all vote-share groups sum to 100%")

# %% Headline numbers
pivot = sw.pivot_table(index="display_party", columns="year",
                       values="vote_share_pct", fill_value=0)
pivot["change"] = pivot[2026] - pivot[2021]
print("\n=== State-wide vote share ===")
print(pivot.sort_values(2026, ascending=False).round(2).to_string())

# %% State-wide accounting check (sanity for the speaker notes)
tvk_gain = pivot.loc["TVK", "change"]
dmk_loss = -pivot.loc["DMK", "change"]
aiadmk_loss = -pivot.loc["AIADMK", "change"]
other_loss = -(pivot[pivot["change"] < 0]
                .drop(["DMK", "AIADMK"])["change"].sum())
print(f"\nTVK gain      = +{tvk_gain:.2f} pts")
print(f"DMK loss      = -{dmk_loss:.2f} pts")
print(f"AIADMK loss   = -{aiadmk_loss:.2f} pts")
print(f"Other losses  = -{other_loss:.2f} pts")
print(f"Loss balance  = {dmk_loss + aiadmk_loss + other_loss:.2f} pts vs TVK +{tvk_gain:.2f}")

# %% Build charts
w26 = pd.read_csv(PROCESSED / "winners_2026.csv")

fig1 = chart_voteshare_statewide(sw, CHARTS / "voteshare_statewide_neutral.png")
plt.close(fig1)
print("[ok] voteshare_statewide_neutral.png written")

fig2 = chart_voteshare_by_region(rs, w26, CHARTS / "voteshare_by_region.png")
plt.close(fig2)
print("[ok] voteshare_by_region.png written")
