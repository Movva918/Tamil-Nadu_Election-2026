"""
Notebook 05 — Story 3: Geography + fragmentation
================================================

Produces:
- outputs/charts/seats_statewide.png        (slide 2)
- outputs/charts/seats_by_region.png        (slide 6)
- outputs/charts/margins_distribution.png   (slide 7)

Headlines:
- Slide 2: TVK 108 seats, more than DMK and AIADMK combined.
- Slide 6: Three different leading parties across the six regions.
- Slide 7: 64 winners under 35% in 2026 (up from 2); 13 winners >=50%
  (down from 70).
"""

# %%
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt
from src import margin_summary
from src.charts import (
    chart_seats_statewide, chart_seats_by_region, chart_margins_distribution,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CHARTS = ROOT / "outputs" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# %% Load winners
w21 = pd.read_csv(PROCESSED / "winners_2021.csv")
w26 = pd.read_csv(PROCESSED / "winners_2026.csv")

# %% Seat-count comparison (slide 2)
s21 = w21["party_canonical"].value_counts().rename("2021")
s26 = w26["party_canonical"].value_counts().rename("2026")
seats = pd.concat([s21, s26], axis=1).fillna(0).astype(int)
seats["change"] = seats["2026"] - seats["2021"]
seats = seats.sort_values("2026", ascending=False)
seats = seats[(seats["2021"] > 0) | (seats["2026"] > 0)]
print("=== Seat counts 2021 vs 2026 ===")
print(seats.to_string())

fig = chart_seats_statewide(seats, CHARTS / "seats_statewide.png")
plt.close(fig)
print("[ok] seats_statewide.png written")

# %% Regional seat shift (slide 6)
fig = chart_seats_by_region(w21, w26, CHARTS / "seats_by_region.png")
plt.close(fig)
print("[ok] seats_by_region.png written")

# Sanity: which party leads in each region in 2026?
print("\n=== Largest party by region in 2026 ===")
for reg in ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]:
    vc = w26[w26["region"] == reg]["party_canonical"].value_counts()
    print(f"  {reg}: largest = {vc.index[0]} ({vc.iloc[0]} seats)")

# %% Margins distribution (slide 7)
fig = chart_margins_distribution(w21, w26, CHARTS / "margins_distribution.png")
plt.close(fig)
print("[ok] margins_distribution.png written")

# Headline margin numbers
print("\n=== Margin headline numbers ===")
print(f"2021: {margin_summary(w21)}")
print(f"2026: {margin_summary(w26)}")
