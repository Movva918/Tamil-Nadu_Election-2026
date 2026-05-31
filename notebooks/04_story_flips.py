"""
Notebook 04 — Story 2: Seat flips (the Sankey)
=============================================

Produces:
- data/processed/flips_per_ac.csv
- data/processed/flips_flow.csv
- outputs/charts/sankey_2021_to_2026.png   (slide 5, deck PNG)
- outputs/charts/sankey_2021_to_2026.html  (interactive, for dashboard)

Headline: 163 of 234 seats (70%) changed winning party between 2021 and 2026.
Largest single flow: DMK -> TVK (65 seats). Second: AIADMK -> TVK (26 seats).
"""

# %%
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt
from src import build_flips, flip_flow
from src.charts import chart_sankey_png, party_colour

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CHARTS = ROOT / "outputs" / "charts"
PROCESSED.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(parents=True, exist_ok=True)

# %% Load winners and build flip table
w21 = pd.read_csv(PROCESSED / "winners_2021.csv")
w26 = pd.read_csv(PROCESSED / "winners_2026.csv")
flips = build_flips(w21, w26)
flow = flip_flow(flips)

flips.to_csv(PROCESSED / "flips_per_ac.csv", index=False)
flow.to_csv(PROCESSED / "flips_flow.csv", index=False)
print(f"[ok] {len(flips)} ACs in flip table; "
      f"{flips['flipped'].sum()} flipped ({flips['flipped'].mean():.1%})")

# %% Headline flows
print("\n=== Top 10 individual flows ===")
print(flow.head(10).to_string(index=False))

# %% PNG Sankey for the deck
fig = chart_sankey_png(flow, CHARTS / "sankey_2021_to_2026.png")
plt.close(fig)
print("[ok] sankey_2021_to_2026.png written")

# %% HTML Sankey (interactive) — needs plotly
try:
    import plotly.graph_objects as go
except ImportError:
    print("[skip] plotly not installed; HTML sankey not produced.")
    print("       Run `pip install plotly` to enable.")
else:
    left_order = (flow.groupby("winner_2021")["seats"].sum()
                       .sort_values(ascending=False).index.tolist())
    right_order = (flow.groupby("winner_2026")["seats"].sum()
                        .sort_values(ascending=False).index.tolist())
    left_nodes = [f"{p} (2021)" for p in left_order]
    right_nodes = [f"{p} (2026)" for p in right_order]
    nodes = left_nodes + right_nodes
    node_idx = {label: i for i, label in enumerate(nodes)}
    node_colours = [party_colour(p) for p in left_order + right_order]

    sources, targets, values, link_colours, hovers = [], [], [], [], []
    for _, r in flow.iterrows():
        sources.append(node_idx[f"{r['winner_2021']} (2021)"])
        targets.append(node_idx[f"{r['winner_2026']} (2026)"])
        values.append(int(r["seats"]))
        if r["winner_2021"] == r["winner_2026"]:
            link_colours.append("rgba(200,200,200,0.45)")
        else:
            c = party_colour(r["winner_2021"]).lstrip("#")
            rr, gg, bb = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            link_colours.append(f"rgba({rr},{gg},{bb},0.55)")
        hovers.append(f"{r['winner_2021']} -> {r['winner_2026']}: {int(r['seats'])} seats")

    fig_html = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(pad=14, thickness=20,
                  line=dict(color="rgba(0,0,0,0.3)", width=0.5),
                  label=nodes, color=node_colours,
                  hovertemplate="%{label}: %{value} seats<extra></extra>"),
        link=dict(source=sources, target=targets, value=values,
                  color=link_colours, customdata=hovers,
                  hovertemplate="%{customdata}<extra></extra>"),
    ))
    fig_html.update_layout(
        title=dict(text="Where Tamil Nadu's 234 seats went: 2021 winners → 2026 winners",
                   font=dict(size=18), x=0.02, xanchor="left"),
        font=dict(family="Arial, sans-serif", size=12, color="#222"),
        paper_bgcolor="white", plot_bgcolor="white",
        width=1200, height=700, margin=dict(l=20, r=20, t=70, b=50),
        annotations=[
            dict(text="<b>2021 winning party</b>", x=0.0, y=1.06,
                 xref="paper", yref="paper", showarrow=False,
                 font=dict(size=12, color="#555")),
            dict(text="<b>2026 winning party</b>", x=1.0, y=1.06,
                 xref="paper", yref="paper", showarrow=False,
                 font=dict(size=12, color="#555"), xanchor="right"),
            dict(text="Source: Election Commission of India. 163 of 234 seats "
                      "(70%) changed winning party between 2021 and 2026.",
                 x=0.0, y=-0.08, xref="paper", yref="paper", showarrow=False,
                 font=dict(size=10, color="#777"), xanchor="left"),
        ],
    )
    fig_html.write_html(CHARTS / "sankey_2021_to_2026.html",
                        include_plotlyjs="cdn", full_html=True)
    print("[ok] sankey_2021_to_2026.html written")
