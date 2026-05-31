"""
Chart-building functions. Each function:
  - Takes a tidy dataframe (output of metrics.py helpers).
  - Writes a PNG to `out_path`.
  - Returns the matplotlib Figure for inline display in notebooks.

Design rules baked in here for tone-discipline compliance:
  - The deck-wide neutral palette (PALETTE below). NO party-specific colours
    used to encode emotional polarity. Each party simply gets a stable
    visual identity.
  - Light bar = 2021, solid bar = 2026 — convention used across every
    paired-bar chart in the deck for visual continuity.
  - No reds for losses or greens for gains. Magnitude is encoded by bold
    text where helpful.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from pathlib import Path as Pathlib

PALETTE = {
    "DMK":    "#4C78A8", "AIADMK": "#F58518", "TVK":    "#54A24B",
    "INC":    "#B279A2", "BJP":    "#EECA3B", "PMK":    "#72B7B2",
    "VCK":    "#E45756", "NTK":    "#FF7F0E", "AMMK":   "#79706E",
    "NOTA":   "#A9A9A9", "IND":    "#BCBD22", "MNM":    "#17BECF",
    "DMDK":   "#FF9DA6", "CPI":    "#9D755D", "CPI(M)": "#BAB0AC",
    "IUML":   "#D7B5A6", "Other":  "#CFCFCF",
}


def party_colour(p: str) -> str:
    return PALETTE.get(p, "#999999")


def _setup_paired_bar_axes(ax, x_max, x_ticks, n_rows, party_labels):
    """Common formatting for paired-bar charts (used by seats + vote share)."""
    y_pos = np.arange(n_rows)[::-1]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(party_labels, fontsize=12, fontweight="bold")
    ax.set_xlim(0, x_max)
    ax.set_xticks(x_ticks)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#DDD")
    ax.spines["bottom"].set_color("#DDD")
    ax.grid(axis="x", alpha=0.3, linestyle=":", linewidth=0.7)
    ax.set_axisbelow(True)
    return y_pos


def chart_seats_statewide(seats: pd.DataFrame, out_path: str | Pathlib) -> plt.Figure:
    """Slide 2: seat count comparison 2021 vs 2026."""
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=150)
    bar_h = 0.36
    y_pos = _setup_paired_bar_axes(
        ax, x_max=155, x_ticks=[0, 25, 50, 75, 100, 125],
        n_rows=len(seats), party_labels=seats.index.tolist(),
    )
    ax.set_xticklabels([str(t) for t in [0, 25, 50, 75, 100, 125]], fontsize=10)
    for j, (party, row) in enumerate(seats.iterrows()):
        y = y_pos[j]
        v21, v26 = int(row["2021"]), int(row["2026"])
        col = party_colour(party)
        if v21 > 0:
            ax.barh(y + bar_h/2, v21, height=bar_h, color=col, alpha=0.35, edgecolor="none")
            ax.text(v21 + 1.5, y + bar_h/2, str(v21), va="center", ha="left", fontsize=11, color="#888")
        if v26 > 0:
            ax.barh(y - bar_h/2, v26, height=bar_h, color=col, alpha=1.0, edgecolor="none")
            ax.text(v26 + 1.5, y - bar_h/2, str(v26), va="center", ha="left",
                    fontsize=13, color="#222", fontweight="bold")
        delta = int(row["change"])
        sign = "+" if delta > 0 else ""
        is_large = abs(delta) >= 20
        ax.text(150, y, f"{sign}{delta}", va="center", ha="right",
                fontsize=12, color="#333" if is_large else "#777",
                fontweight="bold" if is_large else "normal")
    ax.text(150, len(seats) + 0.15, "Change", va="bottom", ha="right",
            fontsize=10, color="#555", fontweight="bold")
    ax.axvline(117, color="#aaaaaa", linestyle="--", linewidth=1, alpha=0.6, zorder=0)
    ax.text(117, len(seats) + 0.15, "majority (117)", va="bottom", ha="center",
            fontsize=9, color="#888")
    fig.text(0.05, 0.96, "Tamil Nadu's two-party era ended in 2026",
             ha="left", va="top", fontsize=20, fontweight="bold", color="#1a1a1a")
    fig.text(0.05, 0.915,
             "Seats won by party, 2021 vs 2026. Light bar = 2021, solid bar = 2026.  "
             "TVK won 108 seats, more than DMK and AIADMK combined.",
             ha="left", va="top", fontsize=12, color="#666")
    fig.text(0.05, 0.03,
             "Source: Election Commission of India.  Total seats = 234.  "
             "Parties shown: those with at least one seat in either year.",
             ha="left", va="top", fontsize=9, color="#888")
    plt.tight_layout(rect=[0.05, 0.06, 0.97, 0.88])
    plt.savefig(out_path, dpi=180, facecolor="white", bbox_inches="tight")
    return fig


def chart_voteshare_statewide(state: pd.DataFrame, out_path: str | Pathlib) -> plt.Figure:
    """Slide 3: state-wide vote share dumbbell with neutral 'Change' column."""
    pivot = state.pivot_table(index="display_party", columns="year",
                              values="vote_share_pct", fill_value=0)
    pivot = pivot.reindex(columns=[2021, 2026], fill_value=0)
    pivot["max_share"] = pivot[[2021, 2026]].max(axis=1)
    keep = pivot[pivot["max_share"] >= 1.0].sort_values(2026, ascending=False).head(8)

    fig, ax = plt.subplots(figsize=(13, 7), dpi=150)
    bar_h = 0.36
    y_pos = _setup_paired_bar_axes(
        ax, x_max=47, x_ticks=[0, 10, 20, 30, 40],
        n_rows=len(keep), party_labels=keep.index.tolist(),
    )
    ax.set_xticklabels(["0%", "10%", "20%", "30%", "40%"], fontsize=10)
    for j, (party, row) in enumerate(keep.iterrows()):
        y = y_pos[j]
        v21, v26 = row[2021], row[2026]
        col = party_colour(party)
        ax.barh(y + bar_h/2, v21, height=bar_h, color=col, alpha=0.35, edgecolor="none")
        ax.barh(y - bar_h/2, v26, height=bar_h, color=col, alpha=1.0, edgecolor="none")
        if v21 > 0:
            ax.text(v21 + 0.4, y + bar_h/2, f"{v21:.1f}%", va="center", ha="left",
                    fontsize=11, color="#888")
        if v26 > 0:
            ax.text(v26 + 0.4, y - bar_h/2, f"{v26:.1f}%", va="center", ha="left",
                    fontsize=12, color="#222", fontweight="bold")
        delta = v26 - v21
        sign = "+" if delta > 0 else ""
        is_large = abs(delta) >= 5
        ax.text(45, y, f"{sign}{delta:.1f} pts", va="center", ha="right",
                fontsize=11, color="#333" if is_large else "#777",
                fontweight="bold" if is_large else "normal")
    ax.text(45, len(keep) + 0.1, "Change", va="bottom", ha="right",
            fontsize=10, color="#555", fontweight="bold")
    fig.text(0.05, 0.96, "TVK entered with 34.9% of the state-wide vote",
             ha="left", va="top", fontsize=20, fontweight="bold", color="#1a1a1a")
    fig.text(0.05, 0.91,
             "State-wide vote share by party, 2021 vs 2026.  Light bar = 2021, solid bar = 2026.",
             ha="left", va="top", fontsize=12, color="#666")
    fig.text(0.05, 0.03,
             "Source: Election Commission of India.  Vote share = total candidate votes / "
             "total valid votes polled (including NOTA).  "
             "Parties shown: those with ≥1% share in either year (top 8 by 2026 share).",
             ha="left", va="top", fontsize=9, color="#888")
    plt.tight_layout(rect=[0.05, 0.07, 0.97, 0.88])
    plt.savefig(out_path, dpi=180, facecolor="white", bbox_inches="tight")
    return fig


def _small_multiples_paired_bar(panel_data_func, panels: list[str], parties: list[str],
                                 x_max: int, x_ticks: list[int],
                                 panel_seat_count_func, suptitle: str, subtitle: str,
                                 footer: str, out_path: str | Pathlib,
                                 value_formatter=str) -> plt.Figure:
    """Generic 2x3 small-multiples paired-bar chart.

    panel_data_func(panel_name, party, year) -> numeric value
    panel_seat_count_func(panel_name) -> int (seat count for the panel header)
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), dpi=150, sharex=True, sharey=True)
    axes = axes.flatten()
    bar_h = 0.36
    for i, panel in enumerate(panels):
        ax = axes[i]
        y_pos = np.arange(len(parties))[::-1]
        for j, p in enumerate(parties):
            y = y_pos[j]
            v21 = panel_data_func(panel, p, 2021)
            v26 = panel_data_func(panel, p, 2026)
            col = party_colour(p)
            if v21 > 0:
                ax.barh(y + bar_h/2, v21, height=bar_h, color=col, alpha=0.35, edgecolor="none")
                ax.text(v21 + 0.4, y + bar_h/2, value_formatter(v21), va="center",
                        ha="left", fontsize=9, color="#999")
            if v26 > 0:
                ax.barh(y - bar_h/2, v26, height=bar_h, color=col, alpha=1.0, edgecolor="none")
                ax.text(v26 + 0.4, y - bar_h/2, value_formatter(v26), va="center",
                        ha="left", fontsize=10, color="#222", fontweight="bold")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(parties, fontsize=10)
        ax.set_xlim(0, x_max)
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([str(t) for t in x_ticks], fontsize=9)
        ax.tick_params(axis="y", length=0)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#DDD")
        ax.spines["bottom"].set_color("#DDD")
        ax.grid(axis="x", alpha=0.3, linestyle=":", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.set_title(f"{panel}   ({panel_seat_count_func(panel)} seats)",
                     loc="left", fontsize=12, fontweight="bold", color="#1a1a1a", pad=8)
    fig.text(0.02, 0.98, suptitle, ha="left", va="top",
             fontsize=18, fontweight="bold", color="#1a1a1a")
    fig.text(0.02, 0.945, subtitle, ha="left", va="top", fontsize=11, color="#666")
    fig.text(0.02, 0.015, footer, ha="left", va="top", fontsize=8.5, color="#888")
    plt.tight_layout(rect=[0, 0.04, 1, 0.91])
    plt.savefig(out_path, dpi=180, facecolor="white", bbox_inches="tight")
    return fig


def chart_voteshare_by_region(region: pd.DataFrame, winners_2026: pd.DataFrame,
                              out_path: str | Pathlib) -> plt.Figure:
    """Slide 4: regional vote share small multiples."""
    parties = ["TVK", "DMK", "AIADMK", "NTK", "BJP", "INC"]
    regions = ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]

    def panel_data(panel, party, year):
        s = region[(region["region"] == panel) & (region["year"] == year)
                   & (region["display_party"] == party)]["vote_share_pct"]
        return float(s.iloc[0]) if len(s) else 0.0

    def panel_seats(panel):
        return int((winners_2026["region"] == panel).sum())

    return _small_multiples_paired_bar(
        panel_data, regions, parties, x_max=50, x_ticks=[0, 10, 20, 30, 40],
        panel_seat_count_func=panel_seats,
        suptitle="TVK's vote share was remarkably even across Tamil Nadu",
        subtitle="Vote share by region, 2021 vs 2026.  TVK pulled 31–47% in every region in 2026; "
                 "DMK and AIADMK each fell in all six.",
        footer="Source: Election Commission of India.  "
               "Vote share = candidate votes / total valid votes polled (including NOTA).  "
               "Bars sized as % of total votes in each region.  "
               "Six-region grouping is editorial (see metadata).",
        out_path=out_path,
        value_formatter=lambda v: f"{v:.0f}%",
    )


def chart_seats_by_region(winners_2021: pd.DataFrame, winners_2026: pd.DataFrame,
                          out_path: str | Pathlib) -> plt.Figure:
    """Slide 6: regional seat shift small multiples."""
    w21 = winners_2021.assign(year=2021)
    w26 = winners_2026.assign(year=2026)
    both = pd.concat([w21, w26], ignore_index=True)
    grid = (both.groupby(["region", "party_canonical", "year"]).size()
                  .reset_index(name="seats"))
    parties = ["TVK", "DMK", "AIADMK", "INC", "PMK", "Other"]
    regions = ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]
    named = set(parties) - {"Other"}

    def panel_data(panel, party, year):
        sub = grid[(grid["region"] == panel) & (grid["year"] == year)]
        if party == "Other":
            return int(sub[~sub["party_canonical"].isin(named)]["seats"].sum())
        return int(sub[sub["party_canonical"] == party]["seats"].sum())

    def panel_seats(panel):
        return int((winners_2026["region"] == panel).sum())

    return _small_multiples_paired_bar(
        panel_data, regions, parties, x_max=42, x_ticks=[0, 10, 20, 30, 40],
        panel_seat_count_func=panel_seats,
        suptitle="Three different leading parties, in three regions",
        subtitle="Seats won by region, 2021 vs 2026. Light bar = 2021, solid bar = 2026.  "
                 "TVK leads in Chennai Metro, Kongu, and South; AIADMK in Central; "
                 "DMK in Delta; TVK & AIADMK tied in North.",
        footer="Source: Election Commission of India.  Bars sized as seat count per region.  "
               "\"Other\" combines all parties not shown individually.  "
               "Six-region grouping is editorial (see metadata).",
        out_path=out_path,
    )


def chart_margins_distribution(winners_2021: pd.DataFrame, winners_2026: pd.DataFrame,
                                out_path: str | Pathlib) -> plt.Figure:
    """Slide 7: distribution of winner's vote share."""
    n21_50 = (winners_2021["winner_pct"] >= 50).sum()
    n26_50 = (winners_2026["winner_pct"] >= 50).sum()
    n21_35 = (winners_2021["winner_pct"] < 35).sum()
    n26_35 = (winners_2026["winner_pct"] < 35).sum()
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), dpi=150, sharey=True)
    bins = np.arange(20, 80, 2.5)
    for ax, df, year, n50, n35 in [
        (axes[0], winners_2021, 2021, n21_50, n21_35),
        (axes[1], winners_2026, 2026, n26_50, n26_35),
    ]:
        counts, edges = np.histogram(df["winner_pct"], bins=bins)
        for c, e in zip(counts, edges[:-1]):
            if e + 1.25 < 35:
                col = "#C8C8C8"
            elif e + 1.25 >= 50:
                col = "#4C78A8"
            else:
                col = "#9FB8D1"
            ax.bar(e, c, width=2.4, color=col, edgecolor="white", linewidth=0.6, align="edge")
        for x in (35, 50):
            ax.axvline(x, color="#555", linewidth=1.2, linestyle="--", alpha=0.7)
        ax.text(35, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 35,
                "  35%", va="top", ha="left", fontsize=10, color="#555")
        ax.text(50, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 35,
                "  50%", va="top", ha="left", fontsize=10, color="#555")
        ax.text(22, 35, f"{n35}\nwinners\n<35%", fontsize=14, fontweight="bold",
                color="#444", ha="left", va="top", linespacing=1.2)
        ax.text(72, 35, f"{n50}\nwinners\n≥50%", fontsize=14, fontweight="bold",
                color="#4C78A8", ha="right", va="top", linespacing=1.2)
        ax.set_title(f"{year}", loc="left", fontsize=16, fontweight="bold",
                     color="#1a1a1a", pad=12)
        ax.set_xlabel("Winner's vote share (% of total valid votes)", fontsize=11, color="#444")
        if ax is axes[0]:
            ax.set_ylabel("Number of constituencies", fontsize=11, color="#444")
        ax.set_xlim(20, 80)
        ax.set_xticks([20, 30, 35, 40, 50, 60, 70, 80])
        ax.set_xticklabels(["20%", "30%", "35%", "40%", "50%", "60%", "70%", "80%"], fontsize=10)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color("#DDD")
        ax.spines["bottom"].set_color("#DDD")
        ax.grid(axis="y", alpha=0.3, linestyle=":", linewidth=0.7)
        ax.set_axisbelow(True)
    fig.text(0.05, 0.97, "Margins collapsed: 64 winners under 35%, up from 2",
             ha="left", va="top", fontsize=20, fontweight="bold", color="#1a1a1a")
    fig.text(0.05, 0.92,
             "Distribution of the winning candidate's vote share, 2021 vs 2026.  "
             "Dominant wins (≥50%) fell from 70 to 13.  Narrow wins (<35%) jumped from 2 to 64.",
             ha="left", va="top", fontsize=12, color="#666")
    fig.text(0.05, 0.025,
             "Source: Election Commission of India.  Each bar counts constituencies where the "
             "winner's vote share fell in that 2.5%-point bin.  "
             "Mean winning margin: 11.7% (2021) → 7.7% (2026).  Median: 9.5% → 5.7%.",
             ha="left", va="top", fontsize=9, color="#888")
    plt.tight_layout(rect=[0.04, 0.06, 0.97, 0.88])
    plt.savefig(out_path, dpi=180, facecolor="white", bbox_inches="tight")
    return fig


def chart_sankey_png(flow: pd.DataFrame, out_path: str | Pathlib) -> plt.Figure:
    """Slide 5: hand-drawn matplotlib Sankey (for deck PNG).

    For the interactive HTML version see notebook 04 (uses Plotly).
    """
    left_order = (flow.groupby("winner_2021")["seats"].sum()
                       .sort_values(ascending=False).index.tolist())
    right_order = (flow.groupby("winner_2026")["seats"].sum()
                        .sort_values(ascending=False).index.tolist())
    left_totals = flow.groupby("winner_2021")["seats"].sum().to_dict()
    right_totals = flow.groupby("winner_2026")["seats"].sum().to_dict()
    total_seats = int(flow["seats"].sum())

    fig = plt.figure(figsize=(15, 9), dpi=150)
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.78])
    ax.set_xlim(0, 10); ax.set_ylim(0, 100); ax.axis("off")
    LEFT_X0, LEFT_X1 = 1.2, 1.75
    RIGHT_X0, RIGHT_X1 = 8.25, 8.8
    TOP, BOTTOM = 96, 6
    GAP = 1.8
    usable_h = (TOP - BOTTOM) - GAP * (max(len(left_order), len(right_order)) - 1)

    def stack_positions(order, totals):
        pos = {}
        y = TOP
        for p in order:
            h = (totals[p] / total_seats) * usable_h
            pos[p] = (y, y - h)
            y = y - h - GAP
        return pos

    left_pos = stack_positions(left_order, left_totals)
    right_pos = stack_positions(right_order, right_totals)
    left_cursor = {p: left_pos[p][0] for p in left_order}
    right_cursor = {p: right_pos[p][0] for p in right_order}

    def ribbon(x0, y0t, y0b, x1, y1t, y1b, color, alpha):
        cp_x = (x0 + x1) / 2
        verts = [(x0, y0t), (cp_x, y0t), (cp_x, y1t), (x1, y1t),
                 (x1, y1b), (cp_x, y1b), (cp_x, y0b), (x0, y0b), (x0, y0t)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                 Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        ax.add_patch(mpatches.PathPatch(Path(verts, codes),
                     facecolor=color, edgecolor="none", alpha=alpha, linewidth=0))

    flow_sorted = flow.sort_values(["winner_2021", "seats"], ascending=[True, False])
    for _, r in flow_sorted.iterrows():
        src, tgt, seats = r["winner_2021"], r["winner_2026"], int(r["seats"])
        h = (seats / total_seats) * usable_h
        y0t = left_cursor[src];  y0b = y0t - h
        y1t = right_cursor[tgt]; y1b = y1t - h
        left_cursor[src] = y0b; right_cursor[tgt] = y1b
        col, alpha = ("#C8C8C8", 0.55) if src == tgt else (party_colour(src), 0.55)
        ribbon(LEFT_X1, y0t, y0b, RIGHT_X0, y1t, y1b, col, alpha)

    def draw_bars(order, pos, x0, x1, side):
        for p in order:
            y_top, y_bot = pos[p]
            ax.add_patch(mpatches.Rectangle((x0, y_bot), x1 - x0, y_top - y_bot,
                          facecolor=party_colour(p), edgecolor="white", linewidth=0.5))
            seats = (left_totals if side == "L" else right_totals)[p]
            label = f"{p}  {seats}"
            if side == "L":
                ax.text(x0 - 0.15, (y_top + y_bot) / 2, label,
                        ha="right", va="center", fontsize=11, fontweight="bold", color="#222")
            else:
                ax.text(x1 + 0.15, (y_top + y_bot) / 2, label,
                        ha="left", va="center", fontsize=11, fontweight="bold", color="#222")

    draw_bars(left_order, left_pos, LEFT_X0, LEFT_X1, "L")
    draw_bars(right_order, right_pos, RIGHT_X0, RIGHT_X1, "R")
    ax.text(LEFT_X1, TOP + 1.5, "2021 winning party", ha="right", va="bottom",
            fontsize=11, color="#555", fontweight="bold")
    ax.text(RIGHT_X0, TOP + 1.5, "2026 winning party", ha="left", va="bottom",
            fontsize=11, color="#555", fontweight="bold")
    fig.text(0.02, 0.95, "Where Tamil Nadu's 234 seats went",
             ha="left", va="top", fontsize=20, fontweight="bold", color="#1a1a1a")
    fig.text(0.02, 0.905,
             "2021 winning party → 2026 winning party. Ribbon width = number of seats.",
             ha="left", va="top", fontsize=12, color="#666")
    fig.text(0.02, 0.025,
             "Source: Election Commission of India.  "
             "163 of 234 seats (70%) changed winning party between 2021 and 2026.  "
             "Grey ribbons = seat held by the same party.",
             ha="left", va="top", fontsize=10, color="#777")
    plt.savefig(out_path, dpi=180, facecolor="white")
    return fig
