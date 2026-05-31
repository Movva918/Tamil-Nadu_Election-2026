"""
06_story_gender_turnout.py
===========================
Gender Turnout Story — Tamil Nadu 2021 vs 2026

Key finding: Women didn't just keep up in 2026 — they outpaced men.
  - Female turnout rose +13.2pp vs male's +10.5pp
  - Gender gap flipped: -0.23pp (2021, male-led) → +2.43pp (2026, female-led)
  - 168 of 234 ACs had women voting more in 2026 (vs only 83 in 2021)
  - 85 constituencies individually flipped from male-dominant to female-dominant

Data sources:
  2021: data/raw/gender_2021.csv   (exported from 8-_Constituency_Data_Summary.xlsx via Power Query)
  2026: data/raw/voters_2026.csv   (exported from 12_-_AC_Wise_Voters_Information_1778165153.xlsx)

Run after: 02_cleaning.py
Output:
  data/processed/gender_turnout_master.csv
  outputs/charts/gender_gap_summary.png
  outputs/charts/gender_gap_regional.png
  outputs/charts/gender_surge_top10.png
  outputs/charts/gender_scatter.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

RAW  = "data/raw"
PROC = "data/processed"
OUT  = "outputs/charts"
os.makedirs(OUT, exist_ok=True)

REGION_COLORS = {
    "Chennai Metro": "#63b3ed",
    "North":         "#6ee7b7",
    "Central":       "#fcd34d",
    "Kongu":         "#fca5a5",
    "Delta":         "#c4b5fd",
    "South":         "#fdba74",
}

# ── 1. Load 2021 gender data from CSV (exported from ECI Constituency Data Summary) ──
print("Loading 2021 gender data from gender_2021.csv ...")
df21 = pd.read_csv(f"{RAW}/gender_2021.csv")
df21.columns = df21.columns.str.strip()
# Normalise to expected column names
col_map_21 = {}
for c in df21.columns:
    cl = c.upper()
    if "AC" in cl and "NO" in cl:                                          col_map_21[c] = "ac_number"
    elif "MALE" in cl and "ELECTOR" in cl and "FEMALE" not in cl:          col_map_21[c] = "male_electors_21"
    elif "FEMALE" in cl and "ELECTOR" in cl:                               col_map_21[c] = "female_electors_21"
    elif ("THIRD" in cl or "TG" in cl) and "ELECTOR" in cl:               col_map_21[c] = "tg_electors_21"
    elif "TOTAL" in cl and "ELECTOR" in cl:                                col_map_21[c] = "total_electors_21"
    elif "MALE" in cl and "VOTER" in cl and "FEMALE" not in cl:            col_map_21[c] = "male_voters_21"
    elif "FEMALE" in cl and "VOTER" in cl:                                 col_map_21[c] = "female_voters_21"
    elif ("THIRD" in cl or "TG" in cl) and "VOTER" in cl:                 col_map_21[c] = "tg_voters_21"
    elif "TOTAL" in cl and "VOTER" in cl:                                  col_map_21[c] = "total_voters_21"
    elif "POLL" in cl or ("POLLING" in cl and "%" in cl):                  col_map_21[c] = "turnout_21"
df21 = df21.rename(columns=col_map_21)
df21["ac_number"] = pd.to_numeric(df21["ac_number"], errors="coerce")
df21 = df21.dropna(subset=["ac_number"]).copy()
df21["ac_number"] = df21["ac_number"].astype(int)
for c in [c for c in df21.columns if c != "ac_number"]:
    df21[c] = pd.to_numeric(df21[c], errors="coerce")
df21["male_turnout_21"]   = (df21.male_voters_21   / df21.male_electors_21   * 100).round(2)
df21["female_turnout_21"] = (df21.female_voters_21 / df21.female_electors_21 * 100).round(2)
df21["gender_gap_21"]     = (df21.female_turnout_21 - df21.male_turnout_21).round(2)
print(f"  2021 gender data: {len(df21)} ACs")

# ── 2. Load 2026 gender data from CSV ────────────────────────────────────────
print("Loading 2026 AC Voters Information from voters_2026.csv ...")
df_v = pd.read_csv(f"{RAW}/voters_2026.csv")
df_v.columns = df_v.columns.str.strip()

# Normalise to expected column names using keyword matching
col_map_26 = {}
for c in df_v.columns:
    cl = c.upper()
    if "AC" in cl and "NO" in cl and "NAME" not in cl:                           col_map_26[c] = "ac_number"
    elif "MALE" in cl and "ELECTOR" in cl and "FEMALE" not in cl:                col_map_26[c] = "male_electors_26"
    elif "FEMALE" in cl and "ELECTOR" in cl:                                     col_map_26[c] = "female_electors_26"
    elif ("THIRD" in cl or "TG" in cl) and "ELECTOR" in cl:                     col_map_26[c] = "tg_electors_26"
    elif "TOTAL" in cl and "ELECTOR" in cl:                                      col_map_26[c] = "total_electors_26"
    elif "MALE" in cl and ("VOTED" in cl or "VOTER" in cl) and "FEMALE" not in cl: col_map_26[c] = "male_voters_26"
    elif "FEMALE" in cl and ("VOTED" in cl or "VOTER" in cl):                   col_map_26[c] = "female_voters_26"
    elif ("THIRD" in cl or "TG" in cl) and ("VOTED" in cl or "VOTER" in cl):    col_map_26[c] = "tg_voters_26"
    elif "TOTAL" in cl and ("VOTED" in cl or "VOTER" in cl):                    col_map_26[c] = "total_voters_26"
    elif "POLL" in cl:                                                           col_map_26[c] = "turnout_26"
df26 = df_v.rename(columns=col_map_26)
df26 = df26[[c for c in ["ac_number", "male_electors_26", "female_electors_26", "tg_electors_26",
                          "total_electors_26", "male_voters_26", "female_voters_26", "tg_voters_26",
                          "total_voters_26", "turnout_26"] if c in df26.columns]].copy()
df26 = df26[pd.to_numeric(df26["ac_number"], errors="coerce").notna()].copy()
df26["ac_number"] = df26["ac_number"].astype(int)
for c in df26.columns[1:]:
    df26[c] = pd.to_numeric(df26[c], errors="coerce")

df26["male_turnout_26"]   = (df26.male_voters_26   / df26.male_electors_26   * 100).round(2)
df26["female_turnout_26"] = (df26.female_voters_26 / df26.female_electors_26 * 100).round(2)
df26["gender_gap_26"]     = (df26.female_turnout_26 - df26.male_turnout_26).round(2)
print(f"  2026 gender data: {len(df26)} ACs")

# ── 3. Merge + derive ─────────────────────────────────────────────────────────
master = pd.read_csv(f"{RAW}/constituency_master.csv")

gender = (
    df21.merge(df26, on="ac_number")
        .merge(master[["ac_number", "constituency", "region", "reserved", "district"]], on="ac_number")
)

gender["male_delta"]    = (gender.male_turnout_26   - gender.male_turnout_21).round(2)
gender["female_delta"]  = (gender.female_turnout_26 - gender.female_turnout_21).round(2)
gender["gap_change"]    = (gender.gender_gap_26     - gender.gender_gap_21).round(2)
gender["female_surge"]  = (gender.female_delta      - gender.male_delta).round(2)   # extra female pp vs male
gender["gap_flipped"]   = (gender.gender_gap_21 < 0) & (gender.gender_gap_26 > 0)   # M→F flip

gender.to_csv(f"{PROC}/gender_turnout_master.csv", index=False)
print(f"\n  Saved: {PROC}/gender_turnout_master.csv")

# ── 4. Print headline findings ────────────────────────────────────────────────
print("\n" + "=" * 65)
print("GENDER TURNOUT STORY — KEY FINDINGS")
print("=" * 65)

print(f"\n  {'Metric':<35} {'2021':>8} {'2026':>8} {'Change':>8}")
print("  " + "-" * 60)
print(f"  {'Male turnout (state avg)':<35} {gender.male_turnout_21.mean():>7.2f}% {gender.male_turnout_26.mean():>7.2f}% {gender.male_delta.mean():>+7.2f}pp")
print(f"  {'Female turnout (state avg)':<35} {gender.female_turnout_21.mean():>7.2f}% {gender.female_turnout_26.mean():>7.2f}% {gender.female_delta.mean():>+7.2f}pp")
print(f"  {'Gender gap F-M (state avg)':<35} {gender.gender_gap_21.mean():>7.2f}pp {gender.gender_gap_26.mean():>7.2f}pp {gender.gap_change.mean():>+7.2f}pp")
print(f"  {'ACs where F > M':<35} {(gender.gender_gap_21 > 0).sum():>8} {(gender.gender_gap_26 > 0).sum():>8}")
print(f"  {'ACs that flipped M→F dominance':<35} {'—':>8} {gender.gap_flipped.sum():>8}")

print("\n\nREGIONAL BREAKDOWN:")
reg = gender.groupby("region").agg(
    male_t21=("male_turnout_21", "mean"),
    female_t21=("female_turnout_21", "mean"),
    gap_21=("gender_gap_21", "mean"),
    male_t26=("male_turnout_26", "mean"),
    female_t26=("female_turnout_26", "mean"),
    gap_26=("gender_gap_26", "mean"),
    gap_change=("gap_change", "mean"),
).round(2)
print(f"\n  {'Region':<18} {'M 2021':>7} {'F 2021':>7} {'Gap21':>7} {'M 2026':>7} {'F 2026':>7} {'Gap26':>7} {'Change':>7}")
print("  " + "-" * 68)
for region, r in reg.iterrows():
    print(f"  {region:<18} {r.male_t21:>7.2f} {r.female_t21:>7.2f} {r.gap_21:>+7.2f} {r.male_t26:>7.2f} {r.female_t26:>7.2f} {r.gap_26:>+7.2f} {r.gap_change:>+7.2f}")

print("\n\nTOP 10 BIGGEST FEMALE SURPLUS SURGE:")
top10 = gender.nlargest(10, "female_surge")[[
    "constituency", "region", "gender_gap_21", "gender_gap_26", "female_surge"
]]
print(f"\n  {'#':<3} {'Constituency':<28} {'Region':<15} {'Gap 2021':>9} {'Gap 2026':>9} {'F surplus':>10}")
print("  " + "-" * 76)
for i, (_, r) in enumerate(top10.iterrows()):
    print(f"  {i+1:<3} {r.constituency:<28} {r.region:<15} {r.gender_gap_21:>+9.2f}pp {r.gender_gap_26:>+9.2f}pp {r.female_surge:>+10.2f}pp")

# ── 5. Bridge to flip story ───────────────────────────────────────────────────
# Load flip table
try:
    flip = pd.read_csv(f"{PROC}/flip_table.csv")
    flipped_acs  = set(flip[flip["flipped"] == True]["ac_number"].tolist())
    flipped_gender_acs = set(gender[gender["gap_flipped"] == True]["ac_number"].tolist())
    overlap = flipped_acs & flipped_gender_acs
    print(f"\n\nBRIDGE TO FLIP STORY:")
    print(f"  Seat flips (party changed):            {len(flipped_acs)}")
    print(f"  Gender flips (M→F dominant):           {len(flipped_gender_acs)}")
    print(f"  Overlap (both flipped):                {len(overlap)}")
    print(f"  % of gender-flip ACs that also seat-flipped: {len(overlap)/len(flipped_gender_acs)*100:.1f}%")
except FileNotFoundError:
    print("\n  (flip_table.csv not found — run 02_cleaning.py first for bridge analysis)")

# ── 6. Charts ─────────────────────────────────────────────────────────────────
plt.style.use("dark_background")
BG    = "#0d0f14"
SURF  = "#141720"
SURF2 = "#1c2030"
BORD  = "#2a2f40"
TEXT  = "#e8eaf0"
MUTED = "#6b7280"
TEAL  = "#38a169"
CORAL = "#e53e3e"
GOLD  = "#f0a500"

# ── Chart 1: State summary ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor(BG)
fig.suptitle("Gender Turnout Story — Tamil Nadu 2021 vs 2026",
             color=TEXT, fontsize=14, fontweight="bold", y=1.01)

# Grouped bar: male vs female each year
ax = axes[0]
ax.set_facecolor(SURF)
cats  = ["2021 Male", "2021 Female", "2026 Male", "2026 Female"]
vals  = [
    gender.male_turnout_21.mean(),
    gender.female_turnout_21.mean(),
    gender.male_turnout_26.mean(),
    gender.female_turnout_26.mean(),
]
colors = [TEAL, CORAL, TEAL, CORAL]
alphas = [0.55, 0.55, 1.0, 1.0]
bars = ax.bar(cats, vals, color=colors,
              alpha=1, edgecolor="none", width=0.6)
for bar, a in zip(bars, alphas):
    bar.set_alpha(a)
for bar, val in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f"{val:.1f}%", ha="center", fontsize=9, color=TEXT, fontweight="bold")
ax.set_ylabel("Average turnout %", color=MUTED, fontsize=9)
ax.set_title("State avg turnout by gender", color=GOLD, fontsize=11, fontweight="bold")
ax.tick_params(colors=TEXT, labelsize=9)
ax.spines[:].set_color(BORD)
ax.set_ylim(60, 95)
ax.grid(axis="y", color=BORD, linestyle="--", alpha=0.4)
legend_elements = [mpatches.Patch(color=TEAL, label="Male"),
                   mpatches.Patch(color=CORAL, label="Female")]
ax.legend(handles=legend_elements, facecolor=SURF2, edgecolor=BORD,
          labelcolor=TEXT, fontsize=9)

# Gender gap bar
ax2 = axes[1]
ax2.set_facecolor(SURF)
gaps   = [gender.gender_gap_21.mean(), gender.gender_gap_26.mean()]
gcols  = [CORAL if g < 0 else TEAL for g in gaps]
bars2  = ax2.bar(["2021", "2026"], gaps, color=gcols, width=0.4, edgecolor="none")
for bar, val in zip(bars2, gaps):
    sign = "+" if val >= 0 else ""
    ypos = val + 0.05 if val >= 0 else val - 0.2
    ax2.text(bar.get_x() + bar.get_width() / 2, ypos,
             f"{sign}{val:.2f}pp", ha="center", fontsize=10, color=TEXT, fontweight="bold")
ax2.axhline(0, color=MUTED, linewidth=0.8)
ax2.set_ylabel("Gender gap (Female − Male) pp", color=MUTED, fontsize=9)
ax2.set_title("Gender gap (F−M) flipped\n−0.23pp → +2.43pp", color=GOLD, fontsize=11, fontweight="bold")
ax2.tick_params(colors=TEXT)
ax2.spines[:].set_color(BORD)
ax2.grid(axis="y", color=BORD, linestyle="--", alpha=0.4)

# Donut: ACs where F > M
ax3 = axes[2]
ax3.set_facecolor(SURF)
for year, f_more, label in [
    (2021, 83,  "2021 — 83 ACs"),
    (2026, 168, "2026 — 168 ACs"),
]:
    pass
sizes21 = [83, 234 - 83]
sizes26 = [168, 234 - 168]
wedges21, _ = ax3.pie(sizes21, radius=0.75, startangle=90,
                       colors=[CORAL, SURF2], wedgeprops=dict(width=0.3, edgecolor=BG))
wedges26, _ = ax3.pie(sizes26, radius=1.0, startangle=90,
                       colors=[TEAL, SURF2], wedgeprops=dict(width=0.3, edgecolor=BG))
ax3.text(0, 0.12, "168", ha="center", va="center", fontsize=20, color=TEAL, fontweight="bold")
ax3.text(0, -0.15, "83", ha="center", va="center", fontsize=14, color=CORAL, fontweight="bold")
ax3.set_title("ACs where women voted more\nouter=2026 (teal), inner=2021 (coral)",
              color=GOLD, fontsize=11, fontweight="bold")

plt.tight_layout()
plt.savefig(f"{OUT}/gender_gap_summary.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"\n  Saved: {OUT}/gender_gap_summary.png")

# ── Chart 2: Regional diverging bar ──────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.patch.set_facecolor(BG)
fig.suptitle("Gender Gap by Region — 2021 vs 2026 (F − M percentage points)",
             color=TEXT, fontsize=13, fontweight="bold")

for ax, year_col, year_label in [
    (axes[0], "gap_21", "2021"),
    (axes[1], "gap_26", "2026"),
]:
    ax.set_facecolor(SURF)
    data = reg[year_col].sort_values()
    colors_r = [TEAL if v >= 0 else CORAL for v in data]
    bars = ax.barh(data.index, data.values, color=colors_r, height=0.55, edgecolor="none")
    ax.axvline(0, color=MUTED, linewidth=0.8)
    for bar, val in zip(bars, data.values):
        sign = "+" if val >= 0 else ""
        offset = 0.05 if val >= 0 else -0.05
        ha = "left" if val >= 0 else "right"
        ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
                f"{sign}{val:.2f}pp", va="center", ha=ha, fontsize=9, color=TEXT)
    ax.set_title(f"Gender gap {year_label}", color=GOLD, fontsize=11, fontweight="bold")
    ax.tick_params(colors=TEXT, labelsize=10)
    ax.spines[:].set_color(BORD)
    ax.grid(axis="x", color=BORD, linestyle="--", alpha=0.4)
    ax.set_xlabel("F − M (pp) — positive = women voted more", color=MUTED, fontsize=9)

plt.tight_layout()
plt.savefig(f"{OUT}/gender_gap_regional.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"  Saved: {OUT}/gender_gap_regional.png")

# ── Chart 3: Top 10 female surge constituencies ───────────────────────────────
fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(SURF)

top10_plot = gender.nlargest(10, "female_surge").sort_values("female_surge")
y = range(len(top10_plot))
colors_r = [REGION_COLORS.get(r, "#718096") for r in top10_plot["region"]]

ax.barh([i + 0.2 for i in y], top10_plot["gender_gap_21"],
        height=0.35, color=CORAL, alpha=0.55, label="Gender gap 2021 (F−M)")
ax.barh([i - 0.2 for i in y], top10_plot["gender_gap_26"],
        height=0.35, color=TEAL, alpha=0.9, label="Gender gap 2026 (F−M)")
ax.axvline(0, color=MUTED, linewidth=0.8)

ax.set_yticks(list(y))
ax.set_yticklabels(
    [f"{r['constituency']} [{r['region']}]" for _, r in top10_plot.iterrows()],
    fontsize=9, color=TEXT
)
ax.set_xlabel("Gender gap (Female − Male pp) — positive = women voted more",
              color=MUTED, fontsize=9)
ax.set_title(
    "Top 10 Constituencies: Biggest Female Surge 2021→2026\n"
    "(ranked by how much more women surged than men)",
    color=TEXT, fontsize=11, fontweight="bold"
)
ax.tick_params(axis="x", colors=MUTED)
ax.spines[:].set_color(BORD)
ax.grid(axis="x", color=BORD, linestyle="--", alpha=0.4)
ax.legend(facecolor=SURF2, edgecolor=BORD, labelcolor=TEXT, fontsize=9)

plt.tight_layout()
plt.savefig(f"{OUT}/gender_surge_top10.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"  Saved: {OUT}/gender_surge_top10.png")

# ── Chart 4: Scatter — female delta vs male delta ────────────────────────────
fig, ax = plt.subplots(figsize=(9, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(SURF)

for region, grp in gender.groupby("region"):
    ax.scatter(grp["male_delta"], grp["female_delta"],
               color=REGION_COLORS.get(region, "#718096"),
               alpha=0.75, s=28, label=region, zorder=3)

# Diagonal reference line (y = x)
lim_min = min(gender.male_delta.min(), gender.female_delta.min()) - 1
lim_max = max(gender.male_delta.max(), gender.female_delta.max()) + 1
ax.plot([lim_min, lim_max], [lim_min, lim_max],
        color=MUTED, linewidth=1.2, linestyle="--", label="Equal surge (y = x)")
ax.fill_between([lim_min, lim_max], [lim_min, lim_max], lim_max,
                alpha=0.04, color=TEAL)   # region above line = female surged more
ax.text(lim_min + 1, lim_max - 1, "Women surged more\n(above the line)",
        fontsize=9, color=TEAL, alpha=0.7)
ax.text(lim_max - 8, lim_min + 1, "Men surged more\n(below the line)",
        fontsize=9, color=CORAL, alpha=0.7)

ax.set_xlabel("Male turnout change 2021→2026 (pp)", color=MUTED, fontsize=10)
ax.set_ylabel("Female turnout change 2021→2026 (pp)", color=MUTED, fontsize=10)
ax.set_title(
    "Female vs Male Turnout Delta — Each dot = one constituency\n"
    "Dots above the line = women surged more than men",
    color=TEXT, fontsize=11, fontweight="bold"
)
ax.tick_params(colors=MUTED)
ax.spines[:].set_color(BORD)
ax.grid(color=BORD, linestyle="--", alpha=0.3)
ax.legend(facecolor=SURF2, edgecolor=BORD, labelcolor=TEXT, fontsize=9, markerscale=1.3)

# % above the line
above = (gender.female_delta > gender.male_delta).sum()
ax.text(0.02, 0.97,
        f"{above}/234 constituencies above the line\n({above/234*100:.0f}% — women surged more)",
        transform=ax.transAxes, fontsize=10, color=TEAL, va="top",
        bbox=dict(facecolor=SURF2, edgecolor=BORD, boxstyle="round,pad=0.4"))

plt.tight_layout()
plt.savefig(f"{OUT}/gender_scatter.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close()
print(f"  Saved: {OUT}/gender_scatter.png")

print("\n✅ Gender turnout story complete.")
print("   Processed CSV: data/processed/gender_turnout_master.csv")
print("   Charts: outputs/charts/gender_gap_summary.png")
print("           outputs/charts/gender_gap_regional.png")
print("           outputs/charts/gender_surge_top10.png")
print("           outputs/charts/gender_scatter.png")
