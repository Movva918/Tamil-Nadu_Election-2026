"""
Canonical party mapping + cleaning utilities for the TN 2021/2026 election data.

DESIGN NOTES (read before changing this file):

1. Party label canonicalisation
   The raw CSVs contain ~100+ distinct party labels per year. Many are tiny
   regional parties, splinter outfits, or alternate naming. We canonicalise
   ONLY where evidence supports it.

   Conservative rule: when a long-form label LOOKS similar to a major-party
   abbreviation but has near-zero votes and zero winners, treat it as a
   DIFFERENT party. Do not merge. Examples:
     - "TVK" (Vijay's party, real, 108 winners in 2026) is NOT the same as
       "Tamizhaga Vaazhvurimai Katchi" (small outfit, 0 winners, ~75K total).
     - "AIADMK" (real, 47 winners 2026) is NOT the same as
       "All India Puratchi Thalaivar Makkal Munnettra Kazhagam" (splinter,
       0 winners, ~133K total).
     - "AMMK" (real) is NOT the same as
       "Anna Puratchi Thalaivar Amma Dravida Munnetra Kazhagam" (splinter,
       0 winners).

2. Grouping for vote-share charts
   Vote-share narratives use a "display party" grouping where:
     - Major parties keep their identity (DMK, AIADMK, TVK, INC, BJP, PMK,
       VCK, NTK, CPI, CPI(M), AMMK, DMDK, MNM, IUML)
     - NOTA is treated as its own bucket (not "Other")
     - IND (independents) is its own bucket
     - Everything else is "Other"
   This grouping is applied as a separate `display_party` column. The
   `party_canonical` column keeps the full unmerged identity so we can
   audit any aggregation.

3. Constituency names
   Spellings differ between years for 34 ACs. Use ac_number for all joins.
   The constituency_master.csv name is the canonical display name.
"""

import pandas as pd
from pathlib import Path

# -----------------------------------------------------------------------------
# Canonical party identity. Maps raw party label -> canonical short code.
# Only includes mappings where canonicalisation differs from the raw label.
# Everything not listed here is passed through unchanged via `party_canonical`.
# -----------------------------------------------------------------------------
# Currently no merges are applied — the raw codes are already canonical for
# the major parties (DMK, AIADMK, TVK, INC, BJP, PMK, etc.). The splinter
# lookalikes intentionally stay separate (see DESIGN NOTES above).
PARTY_RENAMES: dict[str, str] = {
    # Reserved for future use if we discover a true alias.
    # Example shape:  "INC(I)": "INC",
}

# -----------------------------------------------------------------------------
# Display-party grouping for vote-share charts.
# Anything not in MAJOR_PARTIES becomes "Other" — except NOTA and IND, which
# get their own buckets so charts can show them as a separate slice.
# -----------------------------------------------------------------------------
MAJOR_PARTIES: set[str] = {
    "DMK", "AIADMK", "TVK",
    "INC", "BJP",
    "PMK", "VCK", "NTK",
    "CPI", "CPI(M)",
    "AMMK", "DMDK", "MNM", "IUML",
}

SPECIAL_BUCKETS: set[str] = {"NOTA", "IND"}


def canonical_party(raw: str) -> str:
    """Return the canonical party code for a raw label."""
    return PARTY_RENAMES.get(raw, raw)


def display_party(canonical: str) -> str:
    """Return the display bucket for vote-share charts."""
    if canonical in MAJOR_PARTIES:
        return canonical
    if canonical in SPECIAL_BUCKETS:
        return canonical
    return "Other"


def load_results(year: int, raw_dir: str | Path = "data/raw") -> pd.DataFrame:
    """Load and clean a year's results CSV.

    Adds two columns:
      - party_canonical: full identity after rename map (currently == party)
      - display_party:   bucketed identity for charts
    """
    raw_dir = Path(raw_dir)
    fname = {2021: "tn_2021_results.csv", 2026: "tn_2026_results.csv"}[year]
    df = pd.read_csv(raw_dir / fname)
    df["party_canonical"] = df["party"].map(canonical_party)
    df["display_party"] = df["party_canonical"].map(display_party)
    df["year"] = year
    return df


def load_master(raw_dir: str | Path = "data/raw") -> pd.DataFrame:
    """Load the constituency master table."""
    return pd.read_csv(Path(raw_dir) / "constituency_master.csv")


def compute_winners(df: pd.DataFrame) -> pd.DataFrame:
    """One row per AC: the candidate with the highest votes.

    Returns columns: ac_number, constituency, candidate, party_canonical,
    display_party, votes, runner_up_party, runner_up_votes, margin,
    total_votes_polled, winner_pct, margin_pct.
    """
    # Sort so highest votes per AC is first
    s = df.sort_values(["ac_number", "votes"], ascending=[True, False])

    # Per-AC totals (sum of all candidate votes incl. NOTA — this matches
    # ECI's "total valid votes polled" convention when NOTA is included)
    totals = s.groupby("ac_number")["votes"].sum().rename("total_votes_polled")

    # Winner + runner-up (rank within each AC)
    s = s.assign(_rank=s.groupby("ac_number").cumcount())
    winners = s[s["_rank"] == 0].drop(columns="_rank").copy()
    runners = (s[s["_rank"] == 1]
               .rename(columns={"party_canonical": "runner_up_party",
                                "votes": "runner_up_votes"})
               [["ac_number", "runner_up_party", "runner_up_votes"]])

    out = winners.merge(runners, on="ac_number", how="left")
    out = out.merge(totals, on="ac_number", how="left")
    out["margin"] = out["votes"] - out["runner_up_votes"]
    out["winner_pct"] = (out["votes"] / out["total_votes_polled"]) * 100
    out["margin_pct"] = (out["margin"] / out["total_votes_polled"]) * 100

    cols = ["ac_number", "constituency", "reserved", "region",
            "candidate", "party_canonical", "display_party", "votes",
            "runner_up_party", "runner_up_votes", "margin",
            "total_votes_polled", "winner_pct", "margin_pct"]
    return out[cols].sort_values("ac_number").reset_index(drop=True)
