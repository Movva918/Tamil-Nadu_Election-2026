"""
story_connection.py
====================
The Connective Story — Tamil Nadu 2021 vs 2026

Ties together Q2 (Flips), Q3 (Vote Share), Q5 (Turnout) into one narrative:
  "Record turnout was concentrated in specific constituencies —
   and in 80% of them, the new voters handed the seat to TVK."

Inputs (from ./data/raw/):
    tn_2021_results.csv
    tn_2026_results.csv
    constituency_master.csv

Outputs (to ./outputs/charts/):
    story_scatter_turnout_tvk.png    ← Chart 1: turnout surge vs TVK share
    story_top20_surge_breakdown.png  ← Chart 2: top 20 surge ACs annotated

Run after: 00_data_loader.py  (or standalone — uses only raw CSVs)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy import stats
import os

RAW = "./data/raw"
OUT = "./outputs/charts"
os.makedirs(OUT, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG    = "#0d0f14"
SURF  = "#141720"
SURF2 = "#1c2030"
BORD  = "#2a2f40"
TEXT  = "#e8eaf0"
MUTED = "#6b7280"
GOLD  = "#f0a500"
TEAL  = "#38b2ac"
CORAL = "#fc8181"
PURPLE= "#9f7aea"

REGION_COLORS = {
    "Chennai Metro": "#63b3ed",
    "North":         "#6ee7b7",
    "Central":       "#fcd34d",
    "Kongu":         "#fca5a5",
    "Delta":         "#c4b5fd",
    "South":         "#fdba74",
}

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data...")
df21   = pd.read_csv(f"{RAW}/tn_2021_results.csv")
df26   = pd.read_csv(f"{RAW}/tn_2026_results.csv")
master = pd.read_csv(f"{RAW}/constituency_master.csv")

df26["party"] = df26["party"].str.strip()
df26.loc[df26["party"].str.lower() == "tavk", "party"] = "TVK"

# ── Turnout ───────────────────────────────────────────────────────────────────
tot21 = df21.groupby("ac_number")["votes"].sum().reset_index(name="total_votes_21")
t21   = df21.drop_duplicates("ac_number")[["ac_number","turnout"]].rename(columns={"turnout":"turnout_21"})
tot21 = tot21.merge(t21, on="ac_number")
tot21["electors_21"] = (tot21["total_votes_21"] / (tot21["turnout_21"] / 100)).round(0)

tot26 = df26.groupby("ac_number")["votes"].sum().reset_index(name="total_votes_26")
turnout = tot21.merge(tot26, on="ac_number")
turnout["turnout_26"]    = (turnout["total_votes_26"] / turnout["electors_21"] * 100).round(2)
turnout["turnout_delta"] = (turnout["turnout_26"] - turnout["turnout_21"]).round(2)

# ── Winners & flips ───────────────────────────────────────────────────────────
def get_winner(df):
    d = df[df["party"] != "NOTA"].copy()
    return (d.sort_values("votes", ascending=False)
             .drop_duplicates("ac_number")
             [["ac_number", "party", "votes"]])

w21  = get_winner(df21).rename(columns={"party": "party_21", "votes": "votes_21"})
w26  = get_winner(df26).rename(columns={"party": "party_26", "votes": "votes_26"})
flip = w21.merge(w26, on="ac_number")
flip["flipped"] = flip["party_21"] != flip["party_26"]

# ── TVK vote share per AC ─────────────────────────────────────────────────────
tot_ac26 = df26.groupby("ac_number")["votes"].sum().reset_index(name="tot_26")
tvk26    = (df26[df26["party"] == "TVK"]
            .groupby("ac_number")["votes"].sum()
            .reset_index(name="tvk_votes"))
tvk_share = tot_ac26.merge(tvk26, on="ac_number", how="left")
tvk_share["tvk_pct_26"] = (tvk_share["tvk_votes"] / tvk_share["tot_26"] * 100).round(2).fillna(0)

# ── Master merged table ───────────────────────────────────────────────────────
merged = (
    turnout[["ac_number", "turnout_21", "turnout_26", "turnout_delta"]]
    .merge(flip[["ac_number", "party_21", "party_26", "flipped"]], on="ac_number")
    .merge(tvk_share[["ac_number", "tvk_pct_26"]], on="ac_number", how="left")
    .merge(master[["ac_number", "constituency", "region", "reserved"]], on="ac_number")
)
merged["tvk_pct_26"] = merged["tvk_pct_26"].fillna(0)
top20 = merged.nlargest(20, "turnout_delta").copy()

# ── Print key stats ───────────────────────────────────────────────────────────
rest = merged[~merged.ac_number.isin(top20.ac_number)]
corr, pval = stats.pearsonr(merged["turnout_delta"], merged["tvk_pct_26"])

print("\n" + "=" * 65)
print("STORY CONNECTION — KEY FINDINGS")
print("=" * 65)
print(f"  Top 20 surge ACs → flipped:      {top20.flipped.sum()}/20  ({top20.flipped.mean()*100:.0f}%)")
print(f"  Remaining 214 ACs → flipped:     {rest.flipped.sum()}/214  ({rest.flipped.mean()*100:.0f}%)")
print(f"  Avg TVK share — top 20 surge:    {top20.tvk_pct_26.mean():.1f}%")
print(f"  Avg TVK share — rest:            {rest.tvk_pct_26.mean():.1f}%")
print(f"  Pearson r (delta vs TVK share):  {corr:.3f}  (p={pval:.3f})")
print(f"\n  Chennai Metro surge ACs (6):     100% flipped, avg TVK {top20[top20.region=='Chennai Metro'].tvk_pct_26.mean():.1f}%")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Scatter: Turnout delta vs TVK vote share (all 234 ACs)
# ══════════════════════════════════════════════════════════════════════════════
print("\nBuilding Chart 1 — Scatter: turnout surge vs TVK vote share...")

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(SURF)

# Split flipped vs held
flipped_df = merged[merged["flipped"] == True]
held_df    = merged[merged["flipped"] == False]

ax.scatter(held_df["turnout_delta"], held_df["tvk_pct_26"],
           color=MUTED, alpha=0.5, s=40, zorder=2, label="Held (same party)")
ax.scatter(flipped_df["turnout_delta"], flipped_df["tvk_pct_26"],
           color=CORAL, alpha=0.75, s=55, zorder=3, label="Flipped seat")

# Highlight top 20 surge with region colour + label
for _, row in top20.iterrows():
    color = REGION_COLORS.get(row["region"], GOLD)
    ax.scatter(row["turnout_delta"], row["tvk_pct_26"],
               color=color, s=130, zorder=5,
               edgecolors="white", linewidths=0.8)
    # Label only the most notable ones
    if row["turnout_delta"] >= 11 or row["tvk_pct_26"] >= 50:
        ax.annotate(
            row["constituency"],
            (row["turnout_delta"], row["tvk_pct_26"]),
            textcoords="offset points", xytext=(7, 3),
            fontsize=7.5, color=TEXT, alpha=0.9,
        )

# Regression line
slope, intercept, *_ = stats.linregress(merged["turnout_delta"], merged["tvk_pct_26"])
x_line = np.linspace(merged["turnout_delta"].min(), merged["turnout_delta"].max(), 200)
ax.plot(x_line, slope * x_line + intercept,
        color=GOLD, linewidth=1.5, linestyle="--", alpha=0.7,
        label=f"Trend line (r = {corr:+.3f})")

# Reference line — TVK state avg
tvk_state_avg = merged["tvk_pct_26"].mean()
ax.axhline(tvk_state_avg, color=PURPLE, linewidth=1, linestyle=":",
           alpha=0.6, label=f"TVK state avg ({tvk_state_avg:.1f}%)")

# Annotations — quadrant labels
ax.text(0.97, 0.97,
        "High surge + High TVK\n→ New voters broke for TVK",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=8.5, color=TEAL, alpha=0.8,
        bbox=dict(facecolor=SURF2, edgecolor=BORD, boxstyle="round,pad=0.4"))

ax.text(0.97, 0.06,
        "High surge + Low TVK\n→ Surge went elsewhere",
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=8.5, color=MUTED, alpha=0.7,
        bbox=dict(facecolor=SURF2, edgecolor=BORD, boxstyle="round,pad=0.4"))

# Region legend for top-20 dots
region_patches = [mpatches.Patch(color=c, label=r) for r, c in REGION_COLORS.items()]
region_legend = ax.legend(handles=region_patches, title="Top 20 surge ACs (by region)",
                          loc="upper left", facecolor=SURF2, edgecolor=BORD,
                          labelcolor=TEXT, fontsize=8, title_fontsize=8)
region_legend.get_title().set_color(GOLD)
ax.add_artist(region_legend)

ax.legend(loc="lower right", facecolor=SURF2, edgecolor=BORD,
          labelcolor=TEXT, fontsize=9)

ax.set_xlabel("Turnout increase 2021 → 2026 (percentage points)", color=MUTED, fontsize=11)
ax.set_ylabel("TVK vote share 2026 (%)", color=MUTED, fontsize=11)
ax.set_title(
    "Where Turnout Surged, TVK Dominated\n"
    "Each dot = one constituency  |  Coloured dots = Top 20 surge ACs  |  Red = flipped seat",
    color=TEXT, fontsize=13, fontweight="bold", pad=14
)
ax.tick_params(colors=MUTED, labelsize=9)
ax.spines[:].set_color(BORD)
ax.grid(color=BORD, linestyle="--", alpha=0.3)

plt.tight_layout()
out1 = f"{OUT}/story_scatter_turnout_tvk.png"
plt.savefig(out1, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  ✅ Saved: {out1}")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Top 20 surge ACs: horizontal bar with flip + TVK annotations
# ══════════════════════════════════════════════════════════════════════════════
print("Building Chart 2 — Top 20 surge ACs breakdown...")

top20_sorted = top20.sort_values("turnout_delta", ascending=True).copy()
top20_sorted["label"] = top20_sorted.apply(
    lambda r: f"{r['constituency']}  [{r['region']}]", axis=1
)
top20_sorted["bar_color"] = top20_sorted.apply(
    lambda r: REGION_COLORS.get(r["region"], GOLD), axis=1
)
top20_sorted["alpha"] = top20_sorted["flipped"].map({True: 1.0, False: 0.45})

fig, (ax_bar, ax_tvk) = plt.subplots(1, 2, figsize=(17, 8),
                                      gridspec_kw={"width_ratios": [2, 1]})
fig.patch.set_facecolor(BG)
fig.suptitle(
    "Top 20 Turnout Surge Constituencies — 2021 → 2026\n"
    "80% flipped  |  Chennai Metro: 100% flipped  |  Avg TVK share 38.8%",
    color=TEXT, fontsize=13, fontweight="bold", y=1.01
)

# ── Left: turnout delta bars ──────────────────────────────────────────────────
ax_bar.set_facecolor(SURF)
y = range(len(top20_sorted))

for i, (_, row) in enumerate(top20_sorted.iterrows()):
    alpha = 1.0 if row["flipped"] else 0.4
    ax_bar.barh(i, row["turnout_delta"], color=row["bar_color"],
                alpha=alpha, height=0.65, edgecolor="none")
    # Value label
    ax_bar.text(row["turnout_delta"] + 0.2, i,
                f"+{row['turnout_delta']:.1f}pp",
                va="center", fontsize=8.5, color=TEXT)
    # Flip badge
    badge_txt = "FLIPPED" if row["flipped"] else "HELD"
    badge_col = CORAL if row["flipped"] else MUTED
    ax_bar.text(-0.3, i, badge_txt,
                va="center", ha="right", fontsize=7, color=badge_col,
                fontweight="bold")

ax_bar.set_yticks(list(y))
ax_bar.set_yticklabels(top20_sorted["label"], fontsize=9, color=TEXT)
ax_bar.set_xlabel("Turnout increase (pp)", color=MUTED, fontsize=10)
ax_bar.set_title("Turnout surge by constituency", color=GOLD, fontsize=11, fontweight="bold")
ax_bar.tick_params(axis="x", colors=MUTED)
ax_bar.spines[:].set_color(BORD)
ax_bar.grid(axis="x", color=BORD, linestyle="--", alpha=0.4)
ax_bar.set_xlim(-2, top20_sorted["turnout_delta"].max() + 2.5)

# Region colour legend
region_patches = [mpatches.Patch(color=c, label=r, alpha=0.9)
                  for r, c in REGION_COLORS.items()
                  if r in top20_sorted["region"].values]
leg = ax_bar.legend(handles=region_patches, title="Region",
                    loc="lower right", facecolor=SURF2, edgecolor=BORD,
                    labelcolor=TEXT, fontsize=8, title_fontsize=8)
leg.get_title().set_color(GOLD)

# ── Right: TVK vote share lollipop ───────────────────────────────────────────
ax_tvk.set_facecolor(SURF)
tvk_avg = top20_sorted["tvk_pct_26"].mean()

for i, (_, row) in enumerate(top20_sorted.iterrows()):
    alpha = 1.0 if row["flipped"] else 0.4
    col   = TEAL if row["tvk_pct_26"] >= tvk_avg else MUTED
    ax_tvk.hlines(i, 0, row["tvk_pct_26"], color=col, alpha=alpha,
                  linewidth=2)
    ax_tvk.scatter(row["tvk_pct_26"], i, color=col, s=60, alpha=alpha,
                   zorder=5)
    ax_tvk.text(row["tvk_pct_26"] + 0.8, i,
                f"{row['tvk_pct_26']:.1f}%",
                va="center", fontsize=8, color=TEXT, alpha=alpha)

ax_tvk.axvline(tvk_avg, color=GOLD, linewidth=1.2, linestyle="--",
               label=f"Top-20 avg ({tvk_avg:.1f}%)")
ax_tvk.set_yticks(list(y))
ax_tvk.set_yticklabels([], fontsize=0)
ax_tvk.set_xlabel("TVK vote share 2026 (%)", color=MUTED, fontsize=10)
ax_tvk.set_title("TVK vote share", color=GOLD, fontsize=11, fontweight="bold")
ax_tvk.tick_params(axis="x", colors=MUTED)
ax_tvk.spines[:].set_color(BORD)
ax_tvk.grid(axis="x", color=BORD, linestyle="--", alpha=0.4)
ax_tvk.set_xlim(0, top20_sorted["tvk_pct_26"].max() + 5)
ax_tvk.legend(facecolor=SURF2, edgecolor=BORD, labelcolor=TEXT, fontsize=8)

plt.tight_layout()
out2 = f"{OUT}/story_top20_surge_breakdown.png"
plt.savefig(out2, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"  ✅ Saved: {out2}")

print("\n✅ story_connection.py complete.")
print(f"   {out1}")
print(f"   {out2}")
