"""
07_story_women_nota_thirdgender.py
====================================
Analysis B — Women in politics      (23/234 winners = 9.8%, TVK won 13)
Analysis C — NOTA deep dive         (199,805 NOTA = 0.41%)
Analysis D — Third gender equity    (58.5% turnout vs 86.2% female)
Analysis E — Gender gap x party     (INC seats had highest F-M gap +9.89pp)
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
import matplotlib.patches as mpatches, os

RAW  = "data/raw";  PROC = "data/processed";  OUT = "outputs/charts"
os.makedirs(OUT, exist_ok=True)

BG="#0d0f14"; SURF="#141720"; SURF2="#1c2030"; BORD="#2a2f40"
TEXT="#e8eaf0"; MUTED="#6b7280"; GOLD="#f0a500"
TEAL="#38a169"; CORAL="#e53e3e"; PURPLE="#9f7aea"
PARTY_COLORS={"TVK":"#9f7aea","AIADMK":"#38a169","ADMK":"#38a169","DMK":"#e53e3e",
              "INC":"#63b3ed","BJP":"#f6ad55","PMK":"#ecc94b","VCK":"#81e6d9",
              "NTK":"#a0aec0","CPI(M)":"#b794f4","DMDK":"#d69e2e","Others":"#718096"}
REGION_COLORS={"Chennai Metro":"#63b3ed","North":"#6ee7b7","Central":"#fcd34d",
               "Kongu":"#fca5a5","Delta":"#c4b5fd","South":"#fdba74"}
MAJOR=["TVK","AIADMK","DMK","INC","BJP","PMK","VCK"]

master   = pd.read_csv(f"{RAW}/constituency_master.csv")
df26_csv = pd.read_csv(f"{RAW}/tn_2026_results.csv")
winners_26 = (df26_csv[df26_csv.party!="NOTA"].sort_values("votes",ascending=False)
              .drop_duplicates("ac_number")[["ac_number","party"]]
              .rename(columns={"party":"winning_party"}))
winners_26["wp"] = winners_26["winning_party"].apply(lambda p: p if p in MAJOR else "Others")

def load_voters_26():
    df = pd.read_csv(f"{RAW}/voters_2026.csv")
    df.columns = df.columns.str.strip()
    col_map = {}
    for c in df.columns:
        cl = c.upper()
        if "AC" in cl and "NO" in cl and "NAME" not in cl:                            col_map[c] = "ac_number"
        elif "MALE" in cl and "ELECTOR" in cl and "FEMALE" not in cl:                 col_map[c] = "male_electors"
        elif "FEMALE" in cl and "ELECTOR" in cl:                                      col_map[c] = "female_electors"
        elif ("THIRD" in cl or "TG" in cl) and "ELECTOR" in cl:                      col_map[c] = "tg_electors"
        elif "TOTAL" in cl and "ELECTOR" in cl:                                       col_map[c] = "total_electors"
        elif "MALE" in cl and ("VOTED" in cl or "VOTER" in cl) and "FEMALE" not in cl: col_map[c] = "male_voters"
        elif "FEMALE" in cl and ("VOTED" in cl or "VOTER" in cl):                    col_map[c] = "female_voters"
        elif ("THIRD" in cl or "TG" in cl) and ("VOTED" in cl or "VOTER" in cl):     col_map[c] = "tg_voters"
        elif "TOTAL" in cl and ("VOTED" in cl or "VOTER" in cl):                     col_map[c] = "total_voters"
        elif "POLL" in cl:                                                            col_map[c] = "turnout_pct"
    df = df.rename(columns=col_map)
    df = df[pd.to_numeric(df.get("ac_number", pd.Series(dtype=float)), errors="coerce").notna()].copy()
    df["ac_number"] = df["ac_number"].astype(int)
    for c in df.columns[1:]: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def load_electors_26():
    df = pd.read_csv(f"{RAW}/electors_2026.csv")
    df.columns = df.columns.str.strip()
    col_map = {}
    for c in df.columns:
        cl = c.upper()
        if "AC" in cl and "NO" in cl and "NAME" not in cl:   col_map[c] = "ac_number"
        elif "MALE" in cl and "FEMALE" not in cl:            col_map[c] = "male_electors"
        elif "FEMALE" in cl:                                 col_map[c] = "female_electors"
        elif "THIRD" in cl or "TG" in cl:                   col_map[c] = "tg_electors"
        elif "TOTAL" in cl:                                  col_map[c] = "total_electors"
    df = df.rename(columns=col_map)
    df = df[pd.to_numeric(df.get("ac_number", pd.Series(dtype=float)), errors="coerce").notna()].copy()
    df["ac_number"] = df["ac_number"].astype(int)
    for c in df.columns[1:]: df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# ══ ANALYSIS B — WOMEN IN POLITICS ══════════════════════════════════════════
print("="*55); print("ANALYSIS B — WOMEN IN POLITICS"); print("="*55)
df7 = pd.read_csv(f"{RAW}/women_candidates_raw.csv")
df7 = df7.iloc[1:].reset_index(drop=True)
df7 = df7[pd.to_numeric(df7.iloc[:,0],errors="coerce").notna()].copy()
df7.columns = [str(c) for c in df7.columns]
# rename with actual col names (contain \n)
col_map = {}
for c in df7.columns:
    if "AC No" in c: col_map[c]="ac_number"
    elif "Name of AC" in c: col_map[c]="ac_name"
    elif "Name of candidate" in c: col_map[c]="candidate"
    elif c.strip()=="Party": col_map[c]="party"
    elif "Type" in c: col_map[c]="party_type"
    elif "Secured" in c: col_map[c]="votes"
    elif "Status" in c: col_map[c]="status"
    elif "Total votes" in c: col_map[c]="total_votes"
    elif "Valid Votes" in c and "%" not in c: col_map[c]="valid_votes"
df7.rename(columns=col_map, inplace=True)
df7["ac_number"]   = pd.to_numeric(df7["ac_number"],errors="coerce").astype("Int64")
df7["votes"]       = pd.to_numeric(df7["votes"],errors="coerce")
df7["valid_votes"] = pd.to_numeric(df7["valid_votes"],errors="coerce")
df7["vote_share"]  = (df7["votes"]/df7["valid_votes"]*100).round(2)
df7 = df7.merge(master[["ac_number","region","reserved"]], on="ac_number", how="left")

w_win = df7[df7["status"]=="W"]; w_non = df7[df7["status"]!="W"]
total_cands = len(df26_csv[df26_csv.party!="NOTA"])
print(f"  Women candidates:  {len(df7)} ({len(df7)/total_cands*100:.1f}% of all)")
print(f"  Women winners:     {len(w_win)} of 234 = {len(w_win)/234*100:.1f}%")
print(f"  Women win rate:    {len(w_win)/len(df7)*100:.1f}% vs overall {234/total_cands*100:.1f}%")
print(f"  Avg vote share — winners: {w_win.vote_share.mean():.1f}% | non-winners: {w_non.vote_share.mean():.1f}%")
print("  Winners by party:"); print(w_win["party"].value_counts().to_string())
df7.to_csv(f"{PROC}/women_candidates.csv", index=False)

fig,axes=plt.subplots(1,3,figsize=(16,5)); fig.patch.set_facecolor(BG)
fig.suptitle("Analysis B — Women in Tamil Nadu Politics 2026",color=TEXT,fontsize=14,fontweight="bold")
# B1: winners by party
ax=axes[0]; ax.set_facecolor(SURF)
wvc=w_win["party"].value_counts()
bars=ax.barh(wvc.index.tolist(),wvc.values.tolist(),color=[PARTY_COLORS.get(p,"#718096") for p in wvc.index],height=0.55,edgecolor="none")
for bar,val in zip(bars,wvc.values):
    ax.text(bar.get_width()+0.05,bar.get_y()+bar.get_height()/2,str(val),va="center",fontsize=9,color=TEXT)
ax.set_title("Women winners by party",color=GOLD,fontsize=11,fontweight="bold")
ax.tick_params(colors=TEXT,labelsize=10); ax.spines[:].set_color(BORD)
ax.set_xlabel("Winners",color=MUTED,fontsize=9); ax.grid(axis="x",color=BORD,linestyle="--",alpha=0.4)
# B2: representation funnel
ax2=axes[1]; ax2.set_facecolor(SURF)
steps=["Women among\nall candidates","Women among\nall winners","Parity\ntarget"]
vals=[len(df7)/total_cands*100, len(w_win)/234*100, 50.0]
bars2=ax2.bar(steps,vals,color=[PURPLE,TEAL,GOLD],width=0.5,edgecolor="none",alpha=0.9)
for bar,val in zip(bars2,vals):
    ax2.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.5,f"{val:.1f}%",ha="center",fontsize=10,color=TEXT,fontweight="bold")
ax2.set_ylabel("Percentage %",color=MUTED,fontsize=9); ax2.set_ylim(0,60)
ax2.set_title("Representation funnel\n(parity = 50%)",color=GOLD,fontsize=11,fontweight="bold")
ax2.tick_params(colors=TEXT,labelsize=9); ax2.spines[:].set_color(BORD); ax2.grid(axis="y",color=BORD,linestyle="--",alpha=0.4)
# B3: regional distribution
ax3=axes[2]; ax3.set_facecolor(SURF)
reg_w=w_win["region"].value_counts()
colors_rw=[REGION_COLORS.get(r,"#718096") for r in reg_w.index]
bars3=ax3.barh(reg_w.index.tolist(),reg_w.values.tolist(),color=colors_rw,height=0.55,edgecolor="none")
for bar,val in zip(bars3,reg_w.values):
    ax3.text(bar.get_width()+0.05,bar.get_y()+bar.get_height()/2,str(val),va="center",fontsize=9,color=TEXT)
ax3.set_title("Women winners by region",color=GOLD,fontsize=11,fontweight="bold")
ax3.tick_params(colors=TEXT,labelsize=10); ax3.spines[:].set_color(BORD)
ax3.set_xlabel("Winners",color=MUTED,fontsize=9); ax3.grid(axis="x",color=BORD,linestyle="--",alpha=0.4)
plt.tight_layout(); plt.savefig(f"{OUT}/women_win_rate.png",dpi=150,bbox_inches="tight",facecolor=BG); plt.close()
print(f"  Chart: {OUT}/women_win_rate.png")

# ══ ANALYSIS C — NOTA ═══════════════════════════════════════════════════════
print("\n"+"="*55); print("ANALYSIS C — NOTA"); print("="*55)
nota_df = df26_csv[df26_csv["party"] == "NOTA"][["ac_number", "votes"]].rename(columns={"votes": "NOTA Votes"})
total_valid = df26_csv[df26_csv["party"] != "NOTA"].groupby("ac_number")["votes"].sum().reset_index(name="Valid Votes Polled")
voters_26 = nota_df.merge(total_valid, on="ac_number")
voters_26["nota_pct"] = (voters_26["NOTA Votes"] / voters_26["Valid Votes Polled"] * 100).round(3)
nota = voters_26.merge(master[["ac_number","constituency","region","reserved"]], on="ac_number")
state_nota = nota["NOTA Votes"].sum()/nota["Valid Votes Polled"].sum()*100
print(f"  Total NOTA: {nota['NOTA Votes'].sum():,.0f}  |  State %: {state_nota:.4f}%")
nota.to_csv(f"{PROC}/nota_by_ac.csv", index=False)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,6)); fig.patch.set_facecolor(BG)
fig.suptitle("Analysis C — NOTA Voting Patterns 2026",color=TEXT,fontsize=14,fontweight="bold")
top15=nota.nlargest(15,"nota_pct").sort_values("nota_pct")
ax1.set_facecolor(SURF)
bars=ax1.barh(top15["constituency"],top15["nota_pct"],color=[REGION_COLORS.get(r,"#718096") for r in top15["region"]],height=0.6,edgecolor="none")
ax1.axvline(state_nota,color=GOLD,linewidth=1.2,linestyle="--",label=f"State avg {state_nota:.2f}%")
for bar,val in zip(bars,top15["nota_pct"]):
    ax1.text(bar.get_width()+0.005,bar.get_y()+bar.get_height()/2,f"{val:.3f}%",va="center",fontsize=8,color=TEXT)
ax1.set_title("Top 15 constituencies by NOTA %",color=GOLD,fontsize=11,fontweight="bold")
ax1.tick_params(colors=TEXT,labelsize=8); ax1.spines[:].set_color(BORD)
legend_p=[mpatches.Patch(color=c,label=r) for r,c in REGION_COLORS.items()]
legend_p.append(plt.Line2D([0],[0],color=GOLD,linestyle="--",label=f"State avg {state_nota:.2f}%"))
ax1.legend(handles=legend_p,facecolor=SURF2,edgecolor=BORD,labelcolor=TEXT,fontsize=7)
ax1.grid(axis="x",color=BORD,linestyle="--",alpha=0.4)
reg_nota=nota.groupby("region")["nota_pct"].mean().sort_values(ascending=False)
ax2.set_facecolor(SURF)
bars2=ax2.bar(reg_nota.index,reg_nota.values,color=[REGION_COLORS.get(r,"#718096") for r in reg_nota.index],width=0.6,edgecolor="none")
ax2.axhline(state_nota,color=GOLD,linewidth=1.2,linestyle="--")
for bar,val in zip(bars2,reg_nota.values):
    ax2.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.003,f"{val:.3f}%",ha="center",fontsize=9,color=TEXT)
ax2.set_title("Avg NOTA % by region",color=GOLD,fontsize=11,fontweight="bold")
ax2.tick_params(colors=TEXT,labelsize=9); ax2.set_xticklabels(reg_nota.index,rotation=20,ha="right")
ax2.spines[:].set_color(BORD); ax2.grid(axis="y",color=BORD,linestyle="--",alpha=0.4)
plt.tight_layout(); plt.savefig(f"{OUT}/nota_top15.png",dpi=150,bbox_inches="tight",facecolor=BG); plt.close()
print(f"  Chart: {OUT}/nota_top15.png")

# ══ ANALYSIS D — THIRD GENDER ═══════════════════════════════════════════════
print("\n"+"="*55); print("ANALYSIS D — THIRD GENDER"); print("="*55)
el26=load_electors_26(); v26=load_voters_26()
tg_el=el26["tg_electors"].sum()
tg_v =v26["tg_voters"].sum()
m_el=el26["male_electors"].sum(); f_el=el26["female_electors"].sum()
m_v=v26["male_voters"].sum(); f_v=v26["female_voters"].sum()
tg_t=tg_v/tg_el*100; m_t=m_v/m_el*100; f_t=f_v/f_el*100
print(f"  TG registered:{tg_el:,.0f} voted:{tg_v:,.0f} turnout:{tg_t:.2f}%")
print(f"  Male:{m_t:.2f}%  Female:{f_t:.2f}%  Gaps: vs male {tg_t-m_t:.1f}pp | vs female {tg_t-f_t:.1f}pp")
tg_ac=el26[["ac_number","tg_electors"]].rename(columns={"tg_electors":"tg_el"}).merge(
    v26[["ac_number","tg_voters"]].rename(columns={"tg_voters":"tg_v"}), on="ac_number")
tg_ac=tg_ac[tg_ac["tg_el"]>0].copy()
tg_ac["tg_turnout"]=(tg_ac["tg_v"]/tg_ac["tg_el"]*100).round(1)
tg_ac.to_csv(f"{PROC}/third_gender_ac.csv",index=False)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,5)); fig.patch.set_facecolor(BG)
fig.suptitle("Analysis D — Third Gender Voter Participation 2026",color=TEXT,fontsize=14,fontweight="bold")
ax1.set_facecolor(SURF)
groups=["Third gender\n(58.5%)","Male\n(83.8%)","Female\n(86.2%)"]
vals_d=[tg_t,m_t,f_t]; colors_d=[PURPLE,TEAL,CORAL]
bars=ax1.bar(groups,vals_d,color=colors_d,width=0.5,edgecolor="none",alpha=0.9)
for bar,val in zip(bars,vals_d):
    ax1.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,f"{val:.1f}%",ha="center",fontsize=11,color=TEXT,fontweight="bold")
ax1.set_title("Turnout by gender group\n(TG lags by 25–28pp)",color=GOLD,fontsize=11,fontweight="bold")
ax1.tick_params(colors=TEXT,labelsize=10); ax1.spines[:].set_color(BORD); ax1.set_ylim(0,100)
ax1.grid(axis="y",color=BORD,linestyle="--",alpha=0.4)
ax2.set_facecolor(SURF)
ax2.hist(tg_ac["tg_turnout"].dropna(),bins=20,color=PURPLE,alpha=0.8,edgecolor=BORD,linewidth=0.5)
ax2.axvline(tg_ac["tg_turnout"].mean(),color=GOLD,linewidth=1.5,linestyle="--",label=f"Mean {tg_ac['tg_turnout'].mean():.1f}%")
ax2.axvline(f_t,color=CORAL,linewidth=1.2,linestyle=":",label=f"Female avg {f_t:.1f}%")
ax2.set_xlabel("TG turnout % per AC",color=MUTED,fontsize=9); ax2.set_ylabel("ACs",color=MUTED,fontsize=9)
ax2.set_title("Distribution of TG turnout\nacross 233 ACs",color=GOLD,fontsize=11,fontweight="bold")
ax2.tick_params(colors=MUTED); ax2.spines[:].set_color(BORD)
ax2.legend(facecolor=SURF2,edgecolor=BORD,labelcolor=TEXT,fontsize=9)
ax2.grid(color=BORD,linestyle="--",alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUT}/third_gender_turnout.png",dpi=150,bbox_inches="tight",facecolor=BG); plt.close()
print(f"  Chart: {OUT}/third_gender_turnout.png")

# ══ ANALYSIS E — GENDER GAP × WINNING PARTY ═════════════════════════════════
print("\n"+"="*55); print("ANALYSIS E — GENDER GAP vs WINNING PARTY"); print("="*55)
v26e=load_voters_26()
v26e["male_t"]  =(v26e["male_voters"]  /v26e["male_electors"]  *100).round(2)
v26e["female_t"]=(v26e["female_voters"]/v26e["female_electors"]*100).round(2)
v26e["gap"]=(v26e["female_t"]-v26e["male_t"]).round(2)
gap_df=v26e[["ac_number","male_t","female_t","gap"]].merge(winners_26,on="ac_number").merge(master[["ac_number","constituency","region","reserved"]],on="ac_number")
party_gap=gap_df.groupby("wp").agg(avg_gap=("gap","mean"),seats=("ac_number","count"),f_leads=("gap",lambda x:(x>0).sum())).reset_index().round(2)
party_gap["f_pct"]=(party_gap["f_leads"]/party_gap["seats"]*100).round(0)
party_gap=party_gap.sort_values("avg_gap",ascending=False)
print("  Avg gap by winning party:")
for _,r in party_gap.iterrows():
    print(f"    {r.wp:<10} {r.avg_gap:>+6.2f}pp  ({r.seats} seats, {r.f_pct:.0f}% F>M)")
gap_df.to_csv(f"{PROC}/gender_gap_by_party.csv",index=False)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,6)); fig.patch.set_facecolor(BG)
fig.suptitle("Analysis E — Gender Turnout Gap by Winning Party 2026",color=TEXT,fontsize=14,fontweight="bold")
ax1.set_facecolor(SURF)
sp=party_gap.sort_values("avg_gap")
bars=ax1.barh(sp["wp"],sp["avg_gap"],color=[CORAL if v<0 else TEAL for v in sp["avg_gap"]],height=0.55,edgecolor="none")
ax1.axvline(0,color=MUTED,linewidth=0.8)
for bar,val in zip(bars,sp["avg_gap"]):
    sign="+"; ha="left"; offset=0.05
    if val<0: sign=""; ha="right"; offset=-0.05
    ax1.text(val+offset,bar.get_y()+bar.get_height()/2,f"{sign}{val:.2f}pp",va="center",ha=ha,fontsize=9,color=TEXT)
ax1.set_title("Avg gender gap in seats\nwon by each party",color=GOLD,fontsize=11,fontweight="bold")
ax1.tick_params(colors=TEXT,labelsize=10); ax1.spines[:].set_color(BORD)
ax1.set_xlabel("Gender gap (F−M pp)",color=MUTED,fontsize=9); ax1.grid(axis="x",color=BORD,linestyle="--",alpha=0.4)
ax2.set_facecolor(SURF)
party_order=["TVK","AIADMK","DMK","INC","PMK","VCK","Others","BJP"]
y_pos={p:i for i,p in enumerate(party_order)}
for _,row in gap_df.iterrows():
    p=row["wp"]
    if p in y_pos:
        ax2.scatter(row["gap"],y_pos[p]+np.random.uniform(-0.2,0.2),
                    color=TEAL if row["gap"]>=0 else CORAL,alpha=0.55,s=18,zorder=3)
ax2.axvline(0,color=MUTED,linewidth=0.8)
ax2.set_yticks(list(y_pos.values())); ax2.set_yticklabels(list(y_pos.keys()),color=TEXT,fontsize=10)
ax2.set_xlabel("Gender gap per constituency (F−M pp)",color=MUTED,fontsize=9)
ax2.set_title("Distribution of gender gap\nby winning party (each dot = 1 AC)",color=GOLD,fontsize=11,fontweight="bold")
ax2.tick_params(axis="x",colors=MUTED); ax2.spines[:].set_color(BORD); ax2.grid(axis="x",color=BORD,linestyle="--",alpha=0.3)
ax2.legend(handles=[mpatches.Patch(color=TEAL,label="F > M"),mpatches.Patch(color=CORAL,label="M > F")],
           facecolor=SURF2,edgecolor=BORD,labelcolor=TEXT,fontsize=9)
plt.tight_layout(); plt.savefig(f"{OUT}/gender_gap_by_party.png",dpi=150,bbox_inches="tight",facecolor=BG); plt.close()
print(f"  Chart: {OUT}/gender_gap_by_party.png")

print("\n✅ Done. CSVs + 4 charts saved.")
