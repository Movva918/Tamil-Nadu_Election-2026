"""
Analytical helpers shared across notebooks.

Every function in this module takes cleaned dataframes (output of
`load_results` in clean.py) and returns a tidy dataframe ready for
charting. Keeping the math here means the notebooks only do
loading, calling, and plotting — never any computation that can't
be unit-tested in isolation.
"""
from __future__ import annotations
import pandas as pd
from typing import Iterable


def vote_share(df: pd.DataFrame, by: Iterable[str] | None = None) -> pd.DataFrame:
    """Vote share by display_party, optionally within groups.

    Vote share = sum(votes) by display_party / total votes
    (state-wide if ``by`` is None, otherwise within each group of ``by``).

    NOTA and IND are kept as their own buckets. Every group sums to 100%.
    """
    by = list(by) if by else []
    grp_cols = by + ["display_party"]
    s = df.groupby(grp_cols)["votes"].sum().reset_index(name="votes")
    if by:
        totals = df.groupby(by)["votes"].sum().reset_index(name="total")
        s = s.merge(totals, on=by, how="left")
    else:
        s["total"] = df["votes"].sum()
    s["vote_share_pct"] = s["votes"] / s["total"] * 100
    return s


def seat_counts(winners: pd.DataFrame, by: Iterable[str] | None = None) -> pd.DataFrame:
    """Seat counts by party_canonical, optionally within groups."""
    by = list(by) if by else []
    grp_cols = by + ["party_canonical"]
    return (winners.groupby(grp_cols).size()
                   .reset_index(name="seats")
                   .sort_values("seats", ascending=False))


def build_flips(w2021: pd.DataFrame, w2026: pd.DataFrame) -> pd.DataFrame:
    """Per-AC flip table joining on ac_number (never on constituency name).

    Returns columns: ac_number, constituency, region, reserved,
                     winner_2021, winner_2026, flipped.
    """
    flips = (
        w2021[["ac_number", "constituency", "region", "reserved", "party_canonical"]]
        .rename(columns={"party_canonical": "winner_2021"})
        .merge(
            w2026[["ac_number", "party_canonical"]]
            .rename(columns={"party_canonical": "winner_2026"}),
            on="ac_number", how="inner",
        )
    )
    if len(flips) != 234:
        raise ValueError(f"Expected 234 AC joins, got {len(flips)}")
    flips["flipped"] = flips["winner_2021"] != flips["winner_2026"]
    return flips


def flip_flow(flips: pd.DataFrame) -> pd.DataFrame:
    """Aggregate flip table into a source-target flow (Sankey input)."""
    flow = (flips.groupby(["winner_2021", "winner_2026"]).size()
                  .reset_index(name="seats"))
    return flow.sort_values("seats", ascending=False).reset_index(drop=True)


def margin_summary(winners: pd.DataFrame) -> dict:
    """Headline margin statistics for the fragmentation slide."""
    return {
        "n_above_50pct": int((winners["winner_pct"] >= 50).sum()),
        "n_below_35pct": int((winners["winner_pct"] < 35).sum()),
        "mean_margin_pct": round(float(winners["margin_pct"].mean()), 2),
        "median_margin_pct": round(float(winners["margin_pct"].median()), 2),
    }
