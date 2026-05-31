"""
Tamil Nadu Elections 2021 vs 2026 — Complete Dashboard
Streamlit recreation of tn_dashboard_light.html
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TN Elections 2026 — Complete Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS (mirrors the HTML theme)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&family=Playfair+Display:wght@700;900&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #f0f2f7 !important;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── HIDE default Streamlit sidebar toggle & collapse button ── */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[kind="header"] { display: none !important; }

/* ── SIDEBAR base — 190px, white, shadow ── */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e5ef !important;
    box-shadow: 2px 0 8px rgba(0,0,0,.04) !important;
    min-width: 190px !important;
    max-width: 190px !important;
    width: 190px !important;
}

/* ── SIDEBAR — kill ALL default Streamlit widget spacing ── */
[data-testid="stSidebar"] { padding-top: 0 !important; }
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] section { padding: 0 !important; }
[data-testid="stSidebar"] .block-container { padding: 0 !important; }
/* Kill the paragraph wrapper Streamlit puts around sidebar markdown */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}
/* Sidebar nav links hover (CSS-only, no JS needed) */
[data-testid="stSidebar"] a:hover {
    background: #f9fafc !important;
    color: #1a1d2e !important;
}

/* ── FULL-WIDTH TOP RIBBON ── */
.hdr {
    background: linear-gradient(135deg, #0f1428 0%, #1a2050 50%, #2d3561 100%);
    border-bottom: 3px solid #f0a500;
    padding: 1.6rem 2.2rem;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    position: relative;
    overflow: hidden;
    margin-left: -4rem;
    margin-right: -4rem;
    margin-top: -4rem;
    padding-left: 2.6rem;
    padding-right: 2.8rem;
    min-height: 90px;
}
.hdr::before {
    content: '';
    position: absolute;
    top: -30%; right: -3%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(240,165,0,.13) 0%, transparent 65%);
    pointer-events: none;
}
.hdr::after {
    content: '';
    position: absolute;
    bottom: -60%; left: 10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(124,58,237,.08) 0%, transparent 70%);
    pointer-events: none;
}
.hdr-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.85rem;
    font-weight: 900;
    color: #fff;
    line-height: 1.1;
    white-space: nowrap;
    letter-spacing: -.01em;
}
.hdr-title span { color: #f0a500; }
.hdr-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    color: rgba(255,255,255,.60);
    margin-top: .35rem;
    letter-spacing: .05em;
}
.hdr-kpis {
    display: flex;
    gap: 1.6rem;
    flex-wrap: wrap;
    align-items: center;
}
.hkpi {
    border-left: 2px solid rgba(240,165,0,.6);
    padding-left: .8rem;
}
.hkpi-n {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.45rem;
    font-weight: 500;
    color: #f0a500;
    line-height: 1.1;
}
.hkpi-l { font-size: 11px; color: rgba(255,255,255,.60); margin-top: 2px; letter-spacing: .03em; }
.hdr-left { flex-shrink: 0; }

/* ── KPI CARDS — fixed height, all identical ── */
.kcard {
    background: #fff;
    border: 1px solid #e2e5ef;
    border-radius: 10px;
    padding: 1rem 1rem 0.85rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    border-bottom: 3px solid var(--c, #f0a500);
    /* fixed height — every card identical */
    height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    box-sizing: border-box;
}
.kn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--c, #c47d00);
    line-height: 1;
}
.kl {
    font-size: 11px;
    color: #6b7280;
    margin-top: .25rem;
    line-height: 1.4;
}
.ks {
    font-size: 10px;
    color: #9ca3af;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: .15rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.card {
    background: #fff;
    border: 1px solid #e2e5ef;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
    margin-bottom: 1rem;
}
.ct {
    font-size: 10px;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: .09em;
    margin-bottom: .6rem;
    font-family: 'IBM Plex Mono', monospace;
}
.insight {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: .75rem .9rem;
    font-size: 13px;
    line-height: 1.65;
    color: #92400e;
    margin-bottom: 1rem;
}
.insight strong { color: #78350f; }
/* ── PAGE HEADING — Playfair serif title + muted desc ── */
.pg-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: .2rem;
    color: #1a1d2e;
    line-height: 1.3;
}
.pg-desc {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 1.25rem;
    line-height: 1.6;
}
/* ── TABLE — matches HTML .tbl exactly ── */
.tbl { width: 100%; border-collapse: collapse; }
.tbl th {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: .07em;
    padding: .45rem .6rem;
    border-bottom: 2px solid #e2e5ef;
    text-align: left;
    font-family: 'IBM Plex Mono', monospace;
    white-space: nowrap;
    background: #fff;
}
.tbl td {
    padding: .45rem .6rem;
    font-size: 12px;
    border-bottom: 1px solid #f0f2f7;
    color: #1a1d2e;
}
.tbl tr:last-child td { border-bottom: none; }
.tbl tr:hover td { background: #fafbfd; }
.tscroll {
    overflow-x: auto;
    max-height: 500px;
    overflow-y: auto;
    border-radius: 8px;
    border: 1px solid #e2e5ef;
}
.tscroll::-webkit-scrollbar { width: 5px; height: 5px; }
.tscroll::-webkit-scrollbar-track { background: #f5f6fa; }
.tscroll::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
.tscroll .tbl thead th { position: sticky; top: 0; background: #fff; z-index: 1; }
/* ── BADGES ── */
.badge { display:inline-block; font-size:10px; font-weight:700; padding:.1rem .38rem; border-radius:4px; font-family:'IBM Plex Mono',monospace; }
.b-TVK  { background:#ede9ff; color:#6d28d9; }
.b-DMK  { background:#fee2e2; color:#b91c1c; }
.b-AIADMK { background:#dcfce7; color:#15803d; }
.b-INC  { background:#dbeafe; color:#1d4ed8; }
.b-BJP  { background:#ffedd5; color:#c2410c; }
.b-PMK  { background:#fef9c3; color:#a16207; }
.b-VCK  { background:#ccfbf1; color:#0f766e; }
.b-NTK, .b-Others { background:#f3f4f6; color:#4b5563; }
.b-CPI  { background:#fee2e2; color:#991b1b; }
.b-DMDK { background:#fef3c7; color:#b45309; }
.b-IUML { background:#e0f2fe; color:#0369a1; }
.b-GEN  { background:#f3f4f6; color:#6b7280; }
.b-SC   { background:#dbeafe; color:#1e40af; }
.b-ST   { background:#dcfce7; color:#166534; }
.flip-y { background:#fee2e2; color:#b91c1c; font-size:9px; padding:.1rem .35rem; border-radius:4px; font-family:'IBM Plex Mono',monospace; font-weight:700; }
.flip-n { background:#f3f4f6; color:#6b7280; font-size:9px; padding:.1rem .35rem; border-radius:4px; font-family:'IBM Plex Mono',monospace; }
.num { font-family:'IBM Plex Mono',monospace; font-size:11px; }
/* ── CORRELATION CARDS ── */
.corr-big {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.8rem;
    font-weight: 500;
    line-height: 1;
}
.corr-lbl { font-size: 11px; color: #6b7280; margin-top: .2rem; }
.corr-txt { font-size: 12px; margin-top: .45rem; line-height: 1.6; color: #1a1d2e; }
.swing-pos { color: #16a34a; font-weight: 600; }
.swing-neg { color: #dc2626; font-weight: 600; }
div[data-testid="stMetric"] {
    background: #fff;
    border: 1px solid #e2e5ef;
    border-radius: 10px;
    padding: .75rem 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
div[data-testid="stMetric"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    color: #9ca3af !important;
    text-transform: uppercase;
    letter-spacing: .07em;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #c47d00 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
PC = {
    "TVK": "#7c3aed", "DMK": "#dc2626", "AIADMK": "#16a34a",
    "INC": "#2563eb", "BJP": "#ea580c", "PMK": "#ca8a04",
    "VCK": "#0d9488", "NTK": "#6b7280", "Others": "#9ca3af",
    "CPI": "#e11d48", "CPI(M)": "#9333ea", "IUML": "#0284c7", "DMDK": "#b45309"
}
RC = {
    "Chennai Metro": "#2563eb", "North": "#16a34a",
    "Central": "#ca8a04", "Kongu": "#dc2626",
    "Delta": "#7c3aed", "South": "#ea580c"
}
REGIONS = ["Chennai Metro", "North", "Central", "Kongu", "Delta", "South"]

REGINSIGHTS = {
    "Chennai Metro": "TVK won 46.63% — its highest regional share. DMK dropped 21pts from its 45% stronghold. Bottom-5 turnout in 2021 became +26-30pt surge zones in 2026.",
    "North": "DMK lost 16.35pts. TVK took 33.06%. PMK fell from 10.33% to 5.46% — significant erosion in their traditional belt.",
    "Central": "TVK (31.02%) vs combined DMK+AIADMK. VCK gained 1.44pts — the only party besides BJP to gain share here.",
    "Kongu": "AIADMK lost most here: −15.65pts (39.51%→23.86%). TVK took 34.49%. BJP relatively stable (5.38%→4.29%).",
    "Delta": "BJP surged +2.64pts — its only region of meaningful gain. TVK got 32.87%. Both DMK and AIADMK fell ~13-14pts.",
    "South": "Most contested — AIADMK lost 14.97pts, DMK dropped 8.53pts. INC strongest here (5.92%). BJP gained +1.01pt.",
}

KPIS = {"constituencies": 234, "seats_flipped": 163, "avg_turnout_21": 73.4,
        "avg_turnout_26": 86.2, "total_votes_26": 49124320, "total_votes_21": 45890954}

SEATS26 = [{"pg":"TVK","seats":108},{"pg":"DMK","seats":59},{"pg":"AIADMK","seats":47},
           {"pg":"INC","seats":5},{"pg":"PMK","seats":4},{"pg":"VCK","seats":2},
           {"pg":"CPI","seats":2},{"pg":"CPI(M)","seats":2},{"pg":"IUML","seats":2},
           {"pg":"BJP","seats":1},{"pg":"DMDK","seats":1},{"pg":"Others","seats":1}]

SEATS21 = [{"pg":"DMK","seats":133},{"pg":"AIADMK","seats":66},{"pg":"INC","seats":18},
           {"pg":"PMK","seats":5},{"pg":"BJP","seats":4},{"pg":"VCK","seats":4},
           {"pg":"CPI(M)","seats":2},{"pg":"CPI","seats":2}]

VS26 = [{"pg":"TVK","votes":17226209,"pct":35.07},{"pg":"DMK","votes":11929144,"pct":24.28},
        {"pg":"AIADMK","votes":10462146,"pct":21.3},{"pg":"NTK","votes":1972537,"pct":4.02},
        {"pg":"INC","votes":1661312,"pct":3.38},{"pg":"BJP","votes":1467024,"pct":2.99},
        {"pg":"Others","votes":1442877,"pct":2.94},{"pg":"PMK","votes":1070745,"pct":2.18},
        {"pg":"DMDK","votes":589500,"pct":1.2},{"pg":"VCK","votes":540056,"pct":1.1},
        {"pg":"CPI","votes":326488,"pct":0.66},{"pg":"CPI(M)","votes":293817,"pct":0.6},
        {"pg":"IUML","votes":142465,"pct":0.29}]

VS21 = [{"pg":"DMK","votes":17430100,"pct":37.98},{"pg":"AIADMK","votes":15390974,"pct":33.54},
        {"pg":"Others","votes":3303557,"pct":7.2},{"pg":"NTK","votes":3041974,"pct":6.63},
        {"pg":"INC","votes":1976527,"pct":4.31},{"pg":"PMK","votes":1758774,"pct":3.83},
        {"pg":"BJP","votes":1213510,"pct":2.64},{"pg":"CPI","votes":504537,"pct":1.1},
        {"pg":"VCK","votes":457763,"pct":1.0},{"pg":"CPI(M)","votes":390819,"pct":0.85},
        {"pg":"IUML","votes":222263,"pct":0.48},{"pg":"DMDK","votes":200156,"pct":0.44}]

FLIP_SUMMARY = [{"party":"AIADMK","gained":25,"lost":44},{"party":"BJP","gained":1,"lost":4},
                {"party":"CPI(M)","gained":1,"lost":1},{"party":"DMDK","gained":1,"lost":0},
                {"party":"DMK","gained":19,"lost":93},{"party":"INC","gained":1,"lost":14},
                {"party":"IUML","gained":2,"lost":0},{"party":"Others","gained":1,"lost":0},
                {"party":"PMK","gained":3,"lost":4},{"party":"TVK","gained":108,"lost":0},
                {"party":"VCK","gained":1,"lost":3}]

REG_SEATS = [
    {"region":"Central","pg":"AIADMK","seats":15},{"region":"Central","pg":"DMDK","seats":1},
    {"region":"Central","pg":"DMK","seats":8},{"region":"Central","pg":"PMK","seats":3},
    {"region":"Central","pg":"TVK","seats":12},{"region":"Central","pg":"VCK","seats":2},
    {"region":"Chennai Metro","pg":"AIADMK","seats":1},{"region":"Chennai Metro","pg":"DMK","seats":2},
    {"region":"Chennai Metro","pg":"TVK","seats":29},{"region":"Delta","pg":"AIADMK","seats":4},
    {"region":"Delta","pg":"CPI","seats":1},{"region":"Delta","pg":"CPI(M)","seats":1},
    {"region":"Delta","pg":"DMK","seats":14},{"region":"Delta","pg":"INC","seats":1},
    {"region":"Delta","pg":"IUML","seats":1},{"region":"Delta","pg":"Others","seats":1},
    {"region":"Delta","pg":"TVK","seats":10},{"region":"Kongu","pg":"AIADMK","seats":7},
    {"region":"Kongu","pg":"BJP","seats":1},{"region":"Kongu","pg":"DMK","seats":9},
    {"region":"Kongu","pg":"TVK","seats":16},{"region":"North","pg":"AIADMK","seats":15},
    {"region":"North","pg":"CPI","seats":1},{"region":"North","pg":"DMK","seats":4},
    {"region":"North","pg":"IUML","seats":1},{"region":"North","pg":"PMK","seats":1},
    {"region":"North","pg":"TVK","seats":15},{"region":"South","pg":"AIADMK","seats":5},
    {"region":"South","pg":"CPI(M)","seats":1},{"region":"South","pg":"DMK","seats":22},
    {"region":"South","pg":"INC","seats":4},{"region":"South","pg":"TVK","seats":26}
]

REG_VS = [
    {"region":"Central","pg":"AIADMK","pct":27.09},{"region":"Central","pg":"BJP","pct":0.68},
    {"region":"Central","pg":"DMDK","pct":2.3},{"region":"Central","pg":"DMK","pct":23.26},
    {"region":"Central","pg":"INC","pct":1.21},{"region":"Central","pg":"NTK","pct":2.92},
    {"region":"Central","pg":"Others","pct":2.51},{"region":"Central","pg":"PMK","pct":5.58},
    {"region":"Central","pg":"TVK","pct":31.13},{"region":"Central","pg":"VCK","pct":3.32},
    {"region":"Chennai Metro","pg":"AIADMK","pct":16.01},{"region":"Chennai Metro","pg":"BJP","pct":1.02},
    {"region":"Chennai Metro","pg":"CPI(M)","pct":0.8},{"region":"Chennai Metro","pg":"DMDK","pct":1.9},
    {"region":"Chennai Metro","pg":"DMK","pct":24.43},{"region":"Chennai Metro","pg":"INC","pct":2.76},
    {"region":"Chennai Metro","pg":"NTK","pct":3.55},{"region":"Chennai Metro","pg":"Others","pct":2.03},
    {"region":"Chennai Metro","pg":"PMK","pct":0.63},{"region":"Chennai Metro","pg":"TVK","pct":46.86},
    {"region":"Delta","pg":"AIADMK","pct":19.62},{"region":"Delta","pg":"BJP","pct":3.47},
    {"region":"Delta","pg":"CPI","pct":1.15},{"region":"Delta","pg":"CPI(M)","pct":1.59},
    {"region":"Delta","pg":"DMK","pct":27.77},{"region":"Delta","pg":"INC","pct":2.8},
    {"region":"Delta","pg":"IUML","pct":1.07},{"region":"Delta","pg":"NTK","pct":4.56},
    {"region":"Delta","pg":"Others","pct":3.6},{"region":"Delta","pg":"PMK","pct":1.38},
    {"region":"Delta","pg":"TVK","pct":33.0},{"region":"Kongu","pg":"AIADMK","pct":23.97},
    {"region":"Kongu","pg":"BJP","pct":4.31},{"region":"Kongu","pg":"CPI","pct":1.69},
    {"region":"Kongu","pg":"DMK","pct":25.75},{"region":"Kongu","pg":"INC","pct":3.57},
    {"region":"Kongu","pg":"NTK","pct":3.51},{"region":"Kongu","pg":"Others","pct":2.54},
    {"region":"Kongu","pg":"TVK","pct":34.66},{"region":"North","pg":"AIADMK","pct":25.03},
    {"region":"North","pg":"BJP","pct":1.73},{"region":"North","pg":"CPI","pct":0.97},
    {"region":"North","pg":"DMDK","pct":2.45},{"region":"North","pg":"DMK","pct":20.58},
    {"region":"North","pg":"INC","pct":2.88},{"region":"North","pg":"IUML","pct":0.91},
    {"region":"North","pg":"NTK","pct":2.68},{"region":"North","pg":"Others","pct":1.86},
    {"region":"North","pg":"PMK","pct":5.48},{"region":"North","pg":"TVK","pct":33.2},
    {"region":"North","pg":"VCK","pct":2.22},{"region":"South","pg":"AIADMK","pct":16.87},
    {"region":"South","pg":"BJP","pct":5.72},{"region":"South","pg":"CPI","pct":0.48},
    {"region":"South","pg":"CPI(M)","pct":1.14},{"region":"South","pg":"DMDK","pct":0.46},
    {"region":"South","pg":"DMK","pct":24.73},{"region":"South","pg":"INC","pct":5.94},
    {"region":"South","pg":"NTK","pct":6.03},{"region":"South","pg":"Others","pct":4.4},
    {"region":"South","pg":"TVK","pct":33.64},{"region":"South","pg":"VCK","pct":0.56}
]

SURGE20 = [
    {"constituency":"Villivakkam","region":"Chennai Metro","t21":55.92,"t26":86.68,"delta":30.76},
    {"constituency":"Anna Nagar","region":"Chennai Metro","t21":57.33,"t26":86.51,"delta":29.18},
    {"constituency":"Velachery","region":"Chennai Metro","t21":56.18,"t26":85.19,"delta":29.01},
    {"constituency":"Virugampakkam","region":"Chennai Metro","t21":57.59,"t26":86.17,"delta":28.58},
    {"constituency":"Tiruppur (South)","region":"Kongu","t21":62.74,"t26":91.29,"delta":28.55},
    {"constituency":"Theayagaraya Nagar","region":"Chennai Metro","t21":55.99,"t26":84.48,"delta":28.49},
    {"constituency":"Thousand Lights","region":"Chennai Metro","t21":56.25,"t26":83.72,"delta":27.47},
    {"constituency":"Perambur","region":"Chennai Metro","t21":63.0,"t26":90.4,"delta":27.4},
    {"constituency":"Chepauk-Thiruvallikeni","region":"Chennai Metro","t21":58.33,"t26":84.81,"delta":26.48},
    {"constituency":"Alandur","region":"Chennai Metro","t21":60.82,"t26":86.9,"delta":26.08},
    {"constituency":"Kolathur","region":"Chennai Metro","t21":61.04,"t26":86.99,"delta":25.95},
    {"constituency":"Harbour","region":"Chennai Metro","t21":57.64,"t26":82.93,"delta":25.29},
    {"constituency":"Egmore","region":"Chennai Metro","t21":61.13,"t26":86.4,"delta":25.27},
    {"constituency":"Shozhinganallur","region":"Chennai Metro","t21":55.51,"t26":80.76,"delta":25.25},
    {"constituency":"Tambaram","region":"Chennai Metro","t21":59.55,"t26":84.51,"delta":24.96},
    {"constituency":"Palladam","region":"Kongu","t21":66.7,"t26":91.34,"delta":24.64},
    {"constituency":"Erode (East)","region":"Kongu","t21":66.24,"t26":90.52,"delta":24.28},
    {"constituency":"Chengalpattu","region":"Chennai Metro","t21":63.54,"t26":86.91,"delta":23.37},
    {"constituency":"Pallavaram","region":"Chennai Metro","t21":60.86,"t26":84.2,"delta":23.34},
    {"constituency":"Coimbatore South","region":"Kongu","t21":60.69,"t26":82.95,"delta":22.26},
]

TURNOUT_TOP5_21 = [{"constituency":"Palacode","turnout":87.37,"region":"North"},
                   {"constituency":"Kulithalai","turnout":86.16,"region":"Kongu"},
                   {"constituency":"Edapadi","turnout":85.64,"region":"Central"},
                   {"constituency":"Veerapandi","turnout":85.64,"region":"Central"},
                   {"constituency":"Viralimalai","turnout":85.43,"region":"Delta"}]
TURNOUT_BOT5_21 = [{"constituency":"Shozhinganallur","turnout":55.51,"region":"Chennai Metro"},
                   {"constituency":"Villivakkam","turnout":55.92,"region":"Chennai Metro"},
                   {"constituency":"Theayagaraya Nagar","turnout":55.99,"region":"Chennai Metro"},
                   {"constituency":"Velachery","turnout":56.18,"region":"Chennai Metro"},
                   {"constituency":"Thousand Lights","turnout":56.25,"region":"Chennai Metro"}]
TURNOUT_TOP5_26 = [{"constituency":"Karur","turnout":94.0,"region":"Kongu"},
                   {"constituency":"Veerapandi","turnout":93.9,"region":"Central"},
                   {"constituency":"Kulithalai","turnout":93.4,"region":"Kongu"},
                   {"constituency":"Sankari","turnout":93.3,"region":"Central"},
                   {"constituency":"Palacode","turnout":93.2,"region":"North"}]
TURNOUT_BOT5_26 = [{"constituency":"Palayamcottai","turnout":69.9,"region":"South"},
                   {"constituency":"Killiyoor","turnout":72.2,"region":"South"},
                   {"constituency":"Madurai North","turnout":72.8,"region":"South"},
                   {"constituency":"Madurai Central","turnout":74.1,"region":"South"},
                   {"constituency":"Karaikudi","turnout":74.8,"region":"South"}]

SAME_PARTY_TOP10 = [
    {"constituency":"Edapadi","party":"AIADMK","vote_pct_21":66.27,"vote_pct_26":57.97,"region":"Central"},
    {"constituency":"Viralimalai","party":"AIADMK","vote_pct_21":52.93,"vote_pct_26":51.97,"region":"Delta"},
    {"constituency":"Oddanchatram","party":"DMK","vote_pct_21":54.9,"vote_pct_26":46.52,"region":"South"},
    {"constituency":"Palacode","party":"AIADMK","vote_pct_21":53.63,"vote_pct_26":45.9,"region":"North"},
    {"constituency":"Harbour","party":"DMK","vote_pct_21":58.88,"vote_pct_26":45.7,"region":"Chennai Metro"},
    {"constituency":"Kattumannarkoil","party":"VCK","vote_pct_21":49.2,"vote_pct_26":45.44,"region":"Central"},
    {"constituency":"Tiruchirapalli (West)","party":"DMK","vote_pct_21":65.27,"vote_pct_26":45.19,"region":"Delta"},
    {"constituency":"Chepauk-Thiruvallikeni","party":"DMK","vote_pct_21":68.92,"vote_pct_26":44.96,"region":"Chennai Metro"},
    {"constituency":"Athoor","party":"DMK","vote_pct_21":72.6,"vote_pct_26":44.95,"region":"South"},
    {"constituency":"Nannilam","party":"AIADMK","vote_pct_21":46.95,"vote_pct_26":44.88,"region":"Delta"},
]

FLIPPED_TOP10 = [
    {"constituency":"Tirukkoyilur","party_21":"DMK","vote_pct_21":57.15,"party_26":"AIADMK","vote_pct_26":33.68,"vote_pct_diff":23.47,"region":"Central"},
    {"constituency":"Sankarapuram","party_21":"DMK","vote_pct_21":56.41,"party_26":"AIADMK","vote_pct_26":34.13,"vote_pct_diff":22.28,"region":"Central"},
    {"constituency":"Palani","party_21":"DMK","vote_pct_21":53.15,"party_26":"AIADMK","vote_pct_26":32.23,"vote_pct_diff":20.92,"region":"South"},
    {"constituency":"Krishnarayapuram","party_21":"DMK","vote_pct_21":53.72,"party_26":"TVK","vote_pct_26":33.03,"vote_pct_diff":20.69,"region":"Kongu"},
    {"constituency":"Avanashi","party_21":"AIADMK","vote_pct_21":55.78,"party_26":"TVK","vote_pct_26":36.61,"vote_pct_diff":19.17,"region":"Kongu"},
    {"constituency":"Uthangarai","party_21":"AIADMK","vote_pct_21":53.34,"party_26":"TVK","vote_pct_26":34.3,"vote_pct_diff":19.04,"region":"North"},
    {"constituency":"Gingee","party_21":"DMK","vote_pct_21":53.58,"party_26":"PMK","vote_pct_26":36.18,"vote_pct_diff":17.4,"region":"Central"},
    {"constituency":"Gummidipundi","party_21":"DMK","vote_pct_21":57.4,"party_26":"TVK","vote_pct_26":40.73,"vote_pct_diff":16.67,"region":"Chennai Metro"},
    {"constituency":"Kallakurichi","party_21":"AIADMK","vote_pct_21":49.26,"party_26":"TVK","vote_pct_26":32.62,"vote_pct_diff":16.64,"region":"Central"},
    {"constituency":"Sulur","party_21":"AIADMK","vote_pct_21":49.77,"party_26":"TVK","vote_pct_26":33.26,"vote_pct_diff":16.51,"region":"Kongu"},
]

MARGIN_TOP5_21 = [{"constituency":"Athoor","candidate":"PERIYASAMY I","party":"DMK","votes":165809,"runner_votes":30238,"margin":135571,"region":"South"},
                  {"constituency":"Tiruvannamalai","candidate":"E V VELU","party":"DMK","votes":137876,"runner_votes":43203,"margin":94673,"region":"North"},
                  {"constituency":"Poonamallee","candidate":"Krishnaswamy A","party":"DMK","votes":149578,"runner_votes":55468,"margin":94110,"region":"Chennai Metro"},
                  {"constituency":"Edapadi","candidate":"EDAPPADI PALANISWAMI. K","party":"AIADMK","votes":163154,"runner_votes":69352,"margin":93802,"region":"Central"},
                  {"constituency":"Tiruchirapalli (West)","candidate":"Nehru, K.N.","party":"DMK","votes":118133,"runner_votes":33024,"margin":85109,"region":"Delta"}]
MARGIN_BOT5_21 = [{"constituency":"Theayagaraya Nagar","candidate":"KARUNANITHI J","party":"DMK","votes":56035,"runner_votes":55898,"margin":137,"region":"Chennai Metro"},
                  {"constituency":"Modakurichi","candidate":"SARASWATHI.C","party":"BJP","votes":78125,"runner_votes":77844,"margin":281,"region":"Kongu"},
                  {"constituency":"Tenkasi","candidate":"PALANI NADAR.S","party":"INC","votes":89315,"runner_votes":88945,"margin":370,"region":"South"},
                  {"constituency":"Mettur","candidate":"SADHASIVAM.S","party":"PMK","votes":97055,"runner_votes":96399,"margin":656,"region":"Central"},
                  {"constituency":"Katpadi","candidate":"DURAIMURUGAN","party":"DMK","votes":85140,"runner_votes":84394,"margin":746,"region":"North"}]
MARGIN_TOP5_26 = [{"constituency":"Edappadi","candidate":"EDAPPADI PALANISWAMI. K","party":"AIADMK","votes":148933,"runner_votes":50823,"margin":98110,"region":"Central"},
                  {"constituency":"Shozhinganallur","candidate":"ECR P SARAVANAN","party":"TVK","votes":220382,"runner_votes":123602,"margin":96780,"region":"Chennai Metro"},
                  {"constituency":"Madavaram","candidate":"M.L.VIJAYPRABHU","party":"TVK","votes":190462,"runner_votes":95477,"margin":94985,"region":"Chennai Metro"},
                  {"constituency":"Avadi","candidate":"R.RAMESH KUMAR","party":"TVK","votes":180384,"runner_votes":104073,"margin":76311,"region":"Chennai Metro"},
                  {"constituency":"Salem (West)","candidate":"LAKSHMANAN.S","party":"TVK","votes":120407,"runner_votes":45540,"margin":74867,"region":"Central"}]
MARGIN_BOT5_26 = [{"constituency":"Tiruppattur","candidate":"SEENIVASA SETHUPATHY. R","party":"TVK","votes":83375,"runner_votes":83374,"margin":1,"region":"South"},
                  {"constituency":"Veppanahalli","candidate":"SRINIVASAN.P.S","party":"DMK","votes":74691,"runner_votes":74553,"margin":138,"region":"North"},
                  {"constituency":"Kanniyakumari","candidate":"THALAVAI SUNDARAM. N","party":"AIADMK","votes":75045,"runner_votes":74831,"margin":214,"region":"South"},
                  {"constituency":"Polur","candidate":"ABISHEK. R","party":"TVK","votes":67961,"runner_votes":67734,"margin":227,"region":"North"},
                  {"constituency":"Tirukkoyilur","candidate":"PALANISAMY S","party":"AIADMK","votes":73033,"runner_votes":72748,"margin":285,"region":"Central"}]

NOTA_TOP10_21 = [{"constituency":"Chepauk-Thiruvallikeni","nota_21":2061,"nota_pct_21":1.5,"region":"Chennai Metro"},
                 {"constituency":"Modakurichi","nota_21":2342,"nota_pct_21":1.288,"region":"Kongu"},
                 {"constituency":"Vasudevanallur","nota_21":2171,"nota_pct_21":1.234,"region":"South"},
                 {"constituency":"Periyakulam","nota_21":2451,"nota_pct_21":1.215,"region":"South"},
                 {"constituency":"Mettupalayam","nota_21":2733,"nota_pct_21":1.214,"region":"Kongu"},
                 {"constituency":"Theayagaraya Nagar","nota_21":1617,"nota_pct_21":1.171,"region":"Chennai Metro"},
                 {"constituency":"Tiruchirapalli (West)","nota_21":2117,"nota_pct_21":1.156,"region":"Delta"},
                 {"constituency":"Harur","nota_21":2249,"nota_pct_21":1.133,"region":"North"},
                 {"constituency":"Rishivandiam","nota_21":2420,"nota_pct_21":1.125,"region":"Central"},
                 {"constituency":"Chengalpattu","nota_21":3075,"nota_pct_21":1.122,"region":"Chennai Metro"}]
NOTA_TOP10_26 = [{"constituency":"Udhagamandalam","nota_26":1525,"nota_pct_26":1.026,"region":"Kongu"},
                 {"constituency":"Bhavanisagar","nota_26":1804,"nota_pct_26":0.841,"region":"Kongu"},
                 {"constituency":"Thalli","nota_26":1550,"nota_pct_26":0.753,"region":"North"},
                 {"constituency":"Oddanchatram","nota_26":1491,"nota_pct_26":0.739,"region":"South"},
                 {"constituency":"Velachery","nota_26":1336,"nota_pct_26":0.723,"region":"Chennai Metro"},
                 {"constituency":"Periyakulam","nota_26":1506,"nota_pct_26":0.713,"region":"South"},
                 {"constituency":"Veppanahalli","nota_26":1570,"nota_pct_26":0.705,"region":"North"},
                 {"constituency":"Bhavani","nota_26":1409,"nota_pct_26":0.676,"region":"Kongu"},
                 {"constituency":"Avanashi","nota_26":1563,"nota_pct_26":0.675,"region":"Kongu"},
                 {"constituency":"Gandharvakottai","nota_26":1127,"nota_pct_26":0.672,"region":"Delta"}]

STATE_SHARE = [{"pg":"TVK","y21":None,"y26":34.92,"swing":None},
               {"pg":"DMK","y21":37.7,"y26":24.19,"swing":-13.51},
               {"pg":"AIADMK","y21":33.29,"y26":21.21,"swing":-12.08},
               {"pg":"Others","y21":8.06,"y26":4.41,"swing":-3.65},
               {"pg":"NTK","y21":6.58,"y26":4.0,"swing":-2.58},
               {"pg":"INC","y21":4.27,"y26":3.37,"swing":-0.9},
               {"pg":"BJP","y21":2.62,"y26":2.97,"swing":0.35},
               {"pg":"PMK","y21":3.8,"y26":2.17,"swing":-1.63},
               {"pg":"VCK","y21":0.99,"y26":1.09,"swing":0.1},
               {"pg":"CPI","y21":1.09,"y26":0.66,"swing":-0.43},
               {"pg":"CPI(M)","y21":0.85,"y26":0.6,"swing":-0.25},
               {"pg":"NOTA","y21":0.75,"y26":0.41,"swing":-0.34}]

REGION_SHARE = [
    {"region":"Central","pg":"AIADMK","y21":35.55,"y26":27.0,"swing":-8.55},
    {"region":"Central","pg":"DMK","y21":38.91,"y26":23.18,"swing":-15.73},
    {"region":"Central","pg":"PMK","y21":8.06,"y26":5.56,"swing":-2.5},
    {"region":"Central","pg":"TVK","y21":None,"y26":31.02,"swing":None},
    {"region":"Central","pg":"VCK","y21":1.86,"y26":3.3,"swing":1.44},
    {"region":"Central","pg":"NTK","y21":4.93,"y26":2.91,"swing":-2.02},
    {"region":"Central","pg":"INC","y21":2.97,"y26":1.2,"swing":-1.77},
    {"region":"Central","pg":"BJP","y21":1.35,"y26":0.68,"swing":-0.67},
    {"region":"Chennai Metro","pg":"AIADMK","y21":28.34,"y26":15.94,"swing":-12.4},
    {"region":"Chennai Metro","pg":"DMK","y21":45.34,"y26":24.31,"swing":-21.03},
    {"region":"Chennai Metro","pg":"TVK","y21":None,"y26":46.63,"swing":None},
    {"region":"Chennai Metro","pg":"NTK","y21":8.47,"y26":3.53,"swing":-4.94},
    {"region":"Chennai Metro","pg":"INC","y21":4.25,"y26":2.74,"swing":-1.51},
    {"region":"Chennai Metro","pg":"PMK","y21":2.36,"y26":0.63,"swing":-1.73},
    {"region":"Delta","pg":"AIADMK","y21":33.56,"y26":19.54,"swing":-14.02},
    {"region":"Delta","pg":"DMK","y21":40.62,"y26":27.66,"swing":-12.96},
    {"region":"Delta","pg":"TVK","y21":None,"y26":32.87,"swing":None},
    {"region":"Delta","pg":"BJP","y21":0.81,"y26":3.45,"swing":2.64},
    {"region":"Delta","pg":"NTK","y21":7.47,"y26":4.55,"swing":-2.92},
    {"region":"Kongu","pg":"AIADMK","y21":39.51,"y26":23.86,"swing":-15.65},
    {"region":"Kongu","pg":"DMK","y21":34.38,"y26":25.62,"swing":-8.76},
    {"region":"Kongu","pg":"TVK","y21":None,"y26":34.49,"swing":None},
    {"region":"Kongu","pg":"BJP","y21":5.38,"y26":4.29,"swing":-1.09},
    {"region":"Kongu","pg":"NTK","y21":5.36,"y26":3.49,"swing":-1.87},
    {"region":"North","pg":"AIADMK","y21":31.72,"y26":24.93,"swing":-6.79},
    {"region":"North","pg":"DMK","y21":36.85,"y26":20.5,"swing":-16.35},
    {"region":"North","pg":"TVK","y21":None,"y26":33.06,"swing":None},
    {"region":"North","pg":"PMK","y21":10.33,"y26":5.46,"swing":-4.87},
    {"region":"North","pg":"NTK","y21":5.26,"y26":2.67,"swing":-2.59},
    {"region":"South","pg":"AIADMK","y21":31.78,"y26":16.81,"swing":-14.97},
    {"region":"South","pg":"DMK","y21":33.17,"y26":24.64,"swing":-8.53},
    {"region":"South","pg":"TVK","y21":None,"y26":33.52,"swing":None},
    {"region":"South","pg":"BJP","y21":4.69,"y26":5.7,"swing":1.01},
    {"region":"South","pg":"INC","y21":7.73,"y26":5.92,"swing":-1.81},
    {"region":"South","pg":"NTK","y21":7.81,"y26":6.01,"swing":-1.8},
]

POSTAL_DATA_26 = [
    {"ac_number":1,"postal_pct":0.698,"t26":91.1,"constituency":"Gummidipundi","region":"Chennai Metro"},
    {"ac_number":2,"postal_pct":0.504,"t26":89.9,"constituency":"Ponneri","region":"Chennai Metro"},
    {"ac_number":3,"postal_pct":1.331,"t26":90.7,"constituency":"Tiruttani","region":"Chennai Metro"},
    {"ac_number":4,"postal_pct":0.786,"t26":89.8,"constituency":"Thiruvallur","region":"Chennai Metro"},
    {"ac_number":5,"postal_pct":0.587,"t26":83.4,"constituency":"Poonamallee","region":"Chennai Metro"},
    {"ac_number":6,"postal_pct":0.721,"t26":79.0,"constituency":"Avadi","region":"Chennai Metro"},
    {"ac_number":7,"postal_pct":0.402,"t26":78.3,"constituency":"Maduravoyal","region":"Chennai Metro"},
    {"ac_number":8,"postal_pct":0.383,"t26":76.7,"constituency":"Ambattur","region":"Chennai Metro"},
    {"ac_number":9,"postal_pct":0.512,"t26":83.5,"constituency":"Madavaram","region":"Chennai Metro"},
    {"ac_number":10,"postal_pct":0.344,"t26":84.2,"constituency":"Thiruvottiyur","region":"Chennai Metro"},
    {"ac_number":33,"postal_pct":0.612,"t26":88.7,"constituency":"Thiruporur","region":"North"},
    {"ac_number":34,"postal_pct":1.045,"t26":91.6,"constituency":"Cheyyur","region":"North"},
    {"ac_number":57,"postal_pct":1.237,"t26":93.2,"constituency":"Palacode","region":"North"},
    {"ac_number":59,"postal_pct":2.253,"t26":91.1,"constituency":"Dharmapuri","region":"North"},
    {"ac_number":60,"postal_pct":2.016,"t26":91.9,"constituency":"Pappireddippatti","region":"North"},
    {"ac_number":61,"postal_pct":2.152,"t26":89.2,"constituency":"Harur","region":"North"},
    {"ac_number":98,"postal_pct":0.747,"t26":90.0,"constituency":"Erode (East)","region":"Kongu"},
    {"ac_number":100,"postal_pct":1.652,"t26":91.4,"constituency":"Modakurichi","region":"Kongu"},
    {"ac_number":108,"postal_pct":1.463,"t26":77.9,"constituency":"Udhagamandalam","region":"Kongu"},
    {"ac_number":135,"postal_pct":0.913,"t26":94.0,"constituency":"Karur","region":"Kongu"},
    {"ac_number":184,"postal_pct":0.99,"t26":74.8,"constituency":"Karaikudi","region":"South"},
    {"ac_number":226,"postal_pct":1.826,"t26":69.9,"constituency":"Palayamcottai","region":"South"},
    {"ac_number":229,"postal_pct":1.739,"t26":82.5,"constituency":"Kanniyakumari","region":"South"},
    {"ac_number":233,"postal_pct":1.903,"t26":76.8,"constituency":"Vilavancode","region":"South"},
]

LIT_DATA = [
    {"district":"Karur","literacy_pct":75.6,"avg_t21":83.955,"avg_t26":93.175},
    {"district":"Dharmapuri","literacy_pct":64.1,"avg_t21":82.534,"avg_t26":91.42},
    {"district":"Salem","literacy_pct":74.0,"avg_t21":79.154,"avg_t26":91.318},
    {"district":"Namakkal","literacy_pct":77.8,"avg_t21":80.042,"avg_t26":91.25},
    {"district":"Erode","literacy_pct":78.3,"avg_t21":75.999,"avg_t26":90.788},
    {"district":"Tiruvannamalai","literacy_pct":73.8,"avg_t21":79.091,"avg_t26":90.288},
    {"district":"Nilgiris","literacy_pct":77.4,"avg_t21":68.337,"avg_t26":90.067},
    {"district":"Dindigul","literacy_pct":73.4,"avg_t21":76.831,"avg_t26":89.757},
    {"district":"Vellore","literacy_pct":77.8,"avg_t21":76.132,"avg_t26":89.585},
    {"district":"Villupuram","literacy_pct":71.9,"avg_t21":79.191,"avg_t26":89.409},
    {"district":"Ariyalur","literacy_pct":70.3,"avg_t21":82.46,"avg_t26":88.05},
    {"district":"Perambalur","literacy_pct":72.2,"avg_t21":79.125,"avg_t26":86.35},
    {"district":"Krishnagiri","literacy_pct":67.5,"avg_t21":77.402,"avg_t26":86.317},
    {"district":"Cuddalore","literacy_pct":74.2,"avg_t21":76.708,"avg_t26":86.178},
    {"district":"Tiruchirappalli","literacy_pct":79.3,"avg_t21":73.79,"avg_t26":86.122},
    {"district":"Virudhunagar","literacy_pct":78.6,"avg_t21":73.813,"avg_t26":85.529},
    {"district":"Coimbatore","literacy_pct":83.9,"avg_t21":67.976,"avg_t26":84.97},
    {"district":"Nagapattinam","literacy_pct":73.5,"avg_t21":75.373,"avg_t26":84.75},
    {"district":"Tiruvallur","literacy_pct":81.6,"avg_t21":70.643,"avg_t26":84.66},
    {"district":"Pudukkottai","literacy_pct":72.0,"avg_t21":76.225,"avg_t26":84.317},
    {"district":"Tiruvarur","literacy_pct":74.8,"avg_t21":76.353,"avg_t26":84.05},
    {"district":"Chennai","literacy_pct":88.9,"avg_t21":59.285,"avg_t26":83.8},
    {"district":"Theni","literacy_pct":78.2,"avg_t21":72.65,"avg_t26":82.15},
    {"district":"Tirunelveli","literacy_pct":82.6,"avg_t21":69.687,"avg_t26":81.06},
    {"district":"Thanjavur","literacy_pct":81.3,"avg_t21":74.096,"avg_t26":81.0},
    {"district":"Madurai","literacy_pct":84.3,"avg_t21":70.329,"avg_t26":80.79},
    {"district":"Ramanathapuram","literacy_pct":70.3,"avg_t21":69.603,"avg_t26":77.775},
    {"district":"Sivaganga","literacy_pct":77.5,"avg_t21":69.138,"avg_t26":77.35},
    {"district":"Kanniyakumari","literacy_pct":91.8,"avg_t21":68.717,"avg_t26":76.4},
]

DRILL_DATA = [
    {"ac_number":28,"constituency":"Alandur","district":"Kanchipuram","region":"Chennai Metro","reserved":"GEN","winner":"M.HARISH","party_21":"DMK","party_26":"TVK","votes":112205,"t21":60.8,"t26":86.9,"margin":29609,"flipped":True},
    {"ac_number":182,"constituency":"Alangudi","district":"Pudukkottai","region":"Delta","reserved":"GEN","winner":"SIVA.V.MEYYANATHAN","party_21":"DMK","party_26":"DMK","votes":64929,"t21":78.5,"t26":85.1,"margin":12977,"flipped":False},
    {"ac_number":223,"constituency":"Alangulam","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"PAUL MANOJ PANDIAN","party_21":"AIADMK","party_26":"DMK","votes":69170,"t21":77.4,"t26":86.5,"margin":7798,"flipped":True},
    {"ac_number":225,"constituency":"Ambasamudram","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"DR.ESAKKI SUBAYA","party_21":"AIADMK","party_26":"AIADMK","votes":65589,"t21":72.0,"t26":84.0,"margin":10245,"flipped":False},
    {"ac_number":8,"constituency":"Ambattur","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"BALAMURUGAN.G","party_21":"DMK","party_26":"TVK","votes":133339,"t21":62.0,"t26":77.3,"margin":58781,"flipped":True},
    {"ac_number":48,"constituency":"Ambur","district":"Vellore","region":"North","reserved":"GEN","winner":"VILWANATHAN. A.C.","party_21":"DMK","party_26":"DMK","votes":74102,"t21":74.0,"t26":91.1,"margin":7131,"flipped":False},
    {"ac_number":44,"constituency":"Anaikattu","district":"Vellore","region":"North","reserved":"GEN","winner":"D.VELAZHAGAN","party_21":"DMK","party_26":"AIADMK","votes":76302,"t21":77.0,"t26":90.2,"margin":7081,"flipped":True},
    {"ac_number":198,"constituency":"Andipatti","district":"Theni","region":"South","reserved":"GEN","winner":"MAHARAJAN.A","party_21":"DMK","party_26":"DMK","votes":74324,"t21":74.8,"t26":84.4,"margin":9554,"flipped":False},
    {"ac_number":21,"constituency":"Anna Nagar","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"V.K.RAMKUMAR","party_21":"DMK","party_26":"TVK","votes":71375,"t21":57.3,"t26":86.5,"margin":21363,"flipped":True},
    {"ac_number":105,"constituency":"Anthiyur","district":"Erode","region":"Kongu","reserved":"GEN","winner":"HARIBASKAR.P","party_21":"DMK","party_26":"AIADMK","votes":60042,"t21":79.7,"t26":89.7,"margin":1260,"flipped":True},
    {"ac_number":38,"constituency":"Arakonam","district":"Vellore","region":"North","reserved":"SC","winner":"V. GANDHIRAJ","party_21":"AIADMK","party_26":"TVK","votes":73776,"t21":74.9,"t26":90.8,"margin":23121,"flipped":True},
    {"ac_number":67,"constituency":"Arani","district":"Tiruvannamalai","region":"North","reserved":"GEN","winner":"JAYASUDHA. L","party_21":"AIADMK","party_26":"AIADMK","votes":76735,"t21":79.8,"t26":90.1,"margin":5631,"flipped":False},
    {"ac_number":183,"constituency":"Arantangi","district":"Pudukkottai","region":"Delta","reserved":"GEN","winner":"MOHAMED FARVAS. J","party_21":"INC","party_26":"TVK","votes":73244,"t21":70.2,"t26":79.5,"margin":10062,"flipped":True},
    {"ac_number":134,"constituency":"Aravakurichi","district":"Karur","region":"Kongu","reserved":"GEN","winner":"ELANGO. R","party_21":"DMK","party_26":"DMK","votes":70827,"t21":81.9,"t26":92.6,"margin":19382,"flipped":False},
    {"ac_number":42,"constituency":"Arcot","district":"Vellore","region":"North","reserved":"GEN","winner":"S.M.SUKUMAR","party_21":"DMK","party_26":"AIADMK","votes":105608,"t21":79.6,"t26":91.6,"margin":42720,"flipped":True},
    {"ac_number":149,"constituency":"Ariyalur","district":"Ariyalur","region":"Central","reserved":"GEN","winner":"RAJENDRAN S","party_21":"DMK","party_26":"AIADMK","votes":95219,"t21":84.5,"t26":89.7,"margin":24498,"flipped":True},
    {"ac_number":207,"constituency":"Aruppukottai","district":"Virudhunagar","region":"South","reserved":"GEN","winner":"RAMACHANDRAN. K.K.S.S.R","party_21":"DMK","party_26":"DMK","votes":65104,"t21":75.6,"t26":85.8,"margin":4943,"flipped":False},
    {"ac_number":129,"constituency":"Athoor","district":"Dindigul","region":"South","reserved":"GEN","winner":"I. PERIASAMY","party_21":"DMK","party_26":"DMK","votes":106240,"t21":78.0,"t26":90.5,"margin":22368,"flipped":False},
    {"ac_number":82,"constituency":"Attur","district":"Salem","region":"Central","reserved":"SC","winner":"JAYASANKARAN. A.P.","party_21":"AIADMK","party_26":"AIADMK","votes":80843,"t21":77.3,"t26":91.4,"margin":15318,"flipped":False},
    {"ac_number":6,"constituency":"Avadi","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"R.RAMESH KUMAR","party_21":"DMK","party_26":"TVK","votes":180384,"t21":67.4,"t26":79.3,"margin":76311,"flipped":True},
    {"ac_number":112,"constituency":"Avanashi","district":"Tirupur","region":"Kongu","reserved":"SC","winner":"KAMALI.S","party_21":"AIADMK","party_26":"TVK","votes":84209,"t21":75.2,"t26":91.5,"margin":15373,"flipped":True},
    {"ac_number":52,"constituency":"Bargur","district":"Krishnagiri","region":"North","reserved":"GEN","winner":"E.C. GOVINDARASAN","party_21":"DMK","party_26":"AIADMK","votes":71240,"t21":79.1,"t26":89.0,"margin":4241,"flipped":True},
    {"ac_number":104,"constituency":"Bhavani","district":"Erode","region":"Kongu","reserved":"GEN","winner":"KARUPPANAN. K.C","party_21":"AIADMK","party_26":"AIADMK","votes":75577,"t21":83.5,"t26":93.4,"margin":7396,"flipped":False},
    {"ac_number":107,"constituency":"Bhavanisagar","district":"Tirupur","region":"Kongu","reserved":"SC","winner":"V.P.TAMILSELVI","party_21":"AIADMK","party_26":"TVK","votes":72391,"t21":77.4,"t26":90.4,"margin":4569,"flipped":True},
    {"ac_number":157,"constituency":"Bhuvanagiri","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"ARUNMOZHITHEVAN . A","party_21":"AIADMK","party_26":"AIADMK","votes":75707,"t21":78.6,"t26":88.9,"margin":2487,"flipped":False},
    {"ac_number":200,"constituency":"Bodinayakanur","district":"Theni","region":"South","reserved":"GEN","winner":"PANNEERSELVAM.O","party_21":"AIADMK","party_26":"DMK","votes":85206,"t21":76.3,"t26":83.6,"margin":6805,"flipped":True},
    {"ac_number":32,"constituency":"Chengalpattu","district":"Kanchipuram","region":"Chennai Metro","reserved":"GEN","winner":"S. THIYAGARAJAN","party_21":"DMK","party_26":"TVK","votes":137136,"t21":63.5,"t26":86.9,"margin":35641,"flipped":True},
    {"ac_number":62,"constituency":"Chengam","district":"Tiruvannamalai","region":"North","reserved":"SC","winner":"S.VELU","party_21":"DMK","party_26":"AIADMK","votes":87802,"t21":80.7,"t26":90.4,"margin":13278,"flipped":True},
    {"ac_number":19,"constituency":"Chepauk-Thiruvallikeni","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"UDHAYANIDHI STALIN","party_21":"DMK","party_26":"DMK","votes":62992,"t21":58.3,"t26":84.8,"margin":7140,"flipped":False},
    {"ac_number":68,"constituency":"Cheyyar","district":"Tiruvannamalai","region":"North","reserved":"GEN","winner":"MUKKUR N. SUBRAMANIAN","party_21":"DMK","party_26":"AIADMK","votes":86680,"t21":81.7,"t26":92.9,"margin":21081,"flipped":True},
    {"ac_number":34,"constituency":"Cheyyur","district":"Kanchipuram","region":"North","reserved":"SC","winner":"RAJASEKAR. E","party_21":"VCK","party_26":"AIADMK","votes":63809,"t21":77.9,"t26":92.2,"margin":5668,"flipped":True},
    {"ac_number":158,"constituency":"Chidambaram","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"THAMIMUN ANSARI. M","party_21":"AIADMK","party_26":"DMK","votes":69739,"t21":71.9,"t26":85.2,"margin":5747,"flipped":True},
    {"ac_number":118,"constituency":"Coimbatore North","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"V. SAMPATHKUMAR","party_21":"AIADMK","party_26":"TVK","votes":92500,"t21":59.2,"t26":76.2,"margin":21992,"flipped":True},
    {"ac_number":120,"constituency":"Coimbatore South","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"V SENTHILBALAJI","party_21":"BJP","party_26":"DMK","votes":59724,"t21":60.7,"t26":83.0,"margin":2271,"flipped":True},
    {"ac_number":231,"constituency":"Colachel","district":"Kanniyakumari","region":"South","reserved":"GEN","winner":"THARAHAI CUTHBERT","party_21":"INC","party_26":"INC","votes":66207,"t21":67.3,"t26":75.1,"margin":2833,"flipped":False},
    {"ac_number":110,"constituency":"Coonoor","district":"Tirupur","region":"Kongu","reserved":"GEN","winner":"M. RAJU","party_21":"DMK","party_26":"DMK","votes":50470,"t21":69.8,"t26":79.6,"margin":8099,"flipped":False},
    {"ac_number":155,"constituency":"Cuddalore","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"B.RAJKUMAR","party_21":"DMK","party_26":"TVK","votes":70856,"t21":74.8,"t26":85.4,"margin":15519,"flipped":True},
    {"ac_number":201,"constituency":"Cumbum","district":"Theni","region":"South","reserved":"GEN","winner":"JEGANATHMISHRA PLA","party_21":"DMK","party_26":"TVK","votes":85394,"t21":69.5,"t26":82.0,"margin":751,"flipped":True},
    {"ac_number":101,"constituency":"Dharapuram","district":"Erode","region":"Kongu","reserved":"SC","winner":"SATHYABAMA.P","party_21":"DMK","party_26":"AIADMK","votes":81100,"t21":74.2,"t26":90.0,"margin":16727,"flipped":True},
    {"ac_number":59,"constituency":"Dharmapuri","district":"Dharmapuri","region":"North","reserved":"GEN","winner":"SOWMIYA ANBUMANI","party_21":"PMK","party_26":"PMK","votes":93713,"t21":79.7,"t26":91.5,"margin":20896,"flipped":False},
    {"ac_number":132,"constituency":"Dindigul","district":"Dindigul","region":"South","reserved":"GEN","winner":"SENTHILKUMAR. I.P","party_21":"AIADMK","party_26":"DMK","votes":74489,"t21":69.3,"t26":87.6,"margin":1131,"flipped":True},
    {"ac_number":11,"constituency":"Dr. Radhakrishnan Nagar","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"N. MARIE WILSON","party_21":"DMK","party_26":"TVK","votes":97800,"t21":71.0,"t26":91.0,"margin":49668,"flipped":True},
    {"ac_number":86,"constituency":"Edapadi","district":"Salem","region":"Central","reserved":"GEN","winner":"EDAPPADI PALANISWAMI. K","party_21":"AIADMK","party_26":"AIADMK","votes":148933,"t21":85.6,"t26":93.5,"margin":98110,"flipped":False},
    {"ac_number":16,"constituency":"Egmore","district":"Chennai","region":"Chennai Metro","reserved":"SC","winner":"RAJMOHAN","party_21":"DMK","party_26":"TVK","votes":53901,"t21":61.1,"t26":86.4,"margin":10804,"flipped":True},
    {"ac_number":98,"constituency":"Erode (East)","district":"Erode","region":"Kongu","reserved":"GEN","winner":"M.VIJAY BALAJI","party_21":"INC","party_26":"TVK","votes":69747,"t21":66.2,"t26":90.5,"margin":23966,"flipped":True},
    {"ac_number":99,"constituency":"Erode (West)","district":"Erode","region":"Kongu","reserved":"GEN","winner":"ANANTH MOGHAN K.K.","party_21":"DMK","party_26":"TVK","votes":96836,"t21":69.4,"t26":88.9,"margin":22250,"flipped":True},
    {"ac_number":178,"constituency":"Gandharvakottai","district":"Pudukkottai","region":"Delta","reserved":"SC","winner":"N. SUBRAMANIAN","party_21":"CPI(M)","party_26":"TVK","votes":58795,"t21":74.4,"t26":85.6,"margin":11039,"flipped":True},
    {"ac_number":81,"constituency":"Gangavalli","district":"Salem","region":"Central","reserved":"SC","winner":"NALLATHAMBI. A","party_21":"AIADMK","party_26":"AIADMK","votes":73167,"t21":77.1,"t26":90.2,"margin":14404,"flipped":False},
    {"ac_number":70,"constituency":"Gingee","district":"Villupuram","region":"Central","reserved":"GEN","winner":"GANESHKUMAR A","party_21":"DMK","party_26":"PMK","votes":78201,"t21":78.2,"t26":89.6,"margin":12645,"flipped":True},
    {"ac_number":106,"constituency":"Gobichettipalayam","district":"Tirupur","region":"Kongu","reserved":"GEN","winner":"SENGOTTAIYAN.K.A","party_21":"AIADMK","party_26":"TVK","votes":82612,"t21":82.5,"t26":92.0,"margin":16620,"flipped":True},
    {"ac_number":109,"constituency":"Gudalur","district":"Tirupur","region":"Kongu","reserved":"SC","winner":"DHRAVIDAMANI.M","party_21":"AIADMK","party_26":"DMK","votes":65590,"t21":72.2,"t26":81.6,"margin":22833,"flipped":True},
    {"ac_number":46,"constituency":"Gudiyatham","district":"Vellore","region":"North","reserved":"SC","winner":"K.SINDU","party_21":"DMK","party_26":"TVK","votes":82858,"t21":72.6,"t26":91.0,"margin":10097,"flipped":True},
    {"ac_number":1,"constituency":"Gummidipundi","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"S.VIJAYAKUMAR","party_21":"DMK","party_26":"TVK","votes":94320,"t21":78.1,"t26":91.5,"margin":27945,"flipped":True},
    {"ac_number":18,"constituency":"Harbour","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"P K SEKARBABU","party_21":"DMK","party_26":"DMK","votes":45254,"t21":57.6,"t26":82.9,"margin":11750,"flipped":False},
    {"ac_number":61,"constituency":"Harur","district":"Dharmapuri","region":"North","reserved":"SC","winner":"SAMPATHKUMAR. V","party_21":"AIADMK","party_26":"AIADMK","votes":75523,"t21":78.5,"t26":89.6,"margin":3329,"flipped":False},
    {"ac_number":55,"constituency":"Hosur","district":"Krishnagiri","region":"North","reserved":"GEN","winner":"BALAKRISHNAREDDY. P","party_21":"DMK","party_26":"AIADMK","votes":109867,"t21":70.1,"t26":81.0,"margin":27803,"flipped":True},
    {"ac_number":150,"constituency":"Jayankondam","district":"Ariyalur","region":"Central","reserved":"GEN","winner":"VAITHILINGAM G.","party_21":"DMK","party_26":"PMK","votes":88992,"t21":80.4,"t26":86.8,"margin":18490,"flipped":True},
    {"ac_number":49,"constituency":"Jolarpet","district":"Vellore","region":"North","reserved":"GEN","winner":"VEERAMANI K.C.","party_21":"DMK","party_26":"AIADMK","votes":78633,"t21":81.0,"t26":89.9,"margin":16083,"flipped":True},
    {"ac_number":221,"constituency":"Kadayanallur","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"RAJENDRAN. T. M","party_21":"AIADMK","party_26":"DMK","votes":79832,"t21":70.4,"t26":82.4,"margin":6253,"flipped":True},
    {"ac_number":65,"constituency":"Kalasapakkam","district":"Tiruvannamalai","region":"North","reserved":"GEN","winner":"AGRI KRISHNAMURTHY. S S","party_21":"DMK","party_26":"AIADMK","votes":89629,"t21":80.4,"t26":91.7,"margin":26740,"flipped":True},
    {"ac_number":80,"constituency":"Kallakurichi","district":"Villupuram","region":"Central","reserved":"SC","winner":"ARUL VIGNESH C","party_21":"AIADMK","party_26":"TVK","votes":81132,"t21":78.2,"t26":88.7,"margin":798,"flipped":True},
    {"ac_number":37,"constituency":"Kancheepuram","district":"Kanchipuram","region":"North","reserved":"GEN","winner":"R.V. RANJITHKUMAR","party_21":"DMK","party_26":"TVK","votes":91350,"t21":73.3,"t26":88.5,"margin":15488,"flipped":True},
    {"ac_number":102,"constituency":"Kangayam","district":"Erode","region":"Kongu","reserved":"GEN","winner":"NSN NATARAJ","party_21":"DMK","party_26":"AIADMK","votes":71122,"t21":77.2,"t26":92.8,"margin":8133,"flipped":True},
    {"ac_number":229,"constituency":"Kanniyakumari","district":"Kanniyakumari","region":"South","reserved":"GEN","winner":"THALAVAI SUNDARAM. N","party_21":"AIADMK","party_26":"AIADMK","votes":75045,"t21":75.2,"t26":82.9,"margin":214,"flipped":False},
    {"ac_number":184,"constituency":"Karaikudi","district":"Sivaganga","region":"South","reserved":"GEN","winner":"DR.PRABHU. TK","party_21":"INC","party_26":"TVK","votes":101358,"t21":66.2,"t26":75.0,"margin":46074,"flipped":True},
    {"ac_number":135,"constituency":"Karur","district":"Karur","region":"Kongu","reserved":"GEN","winner":"M.R. VIJAYABHASKAR","party_21":"DMK","party_26":"AIADMK","votes":71542,"t21":83.6,"t26":94.4,"margin":1821,"flipped":True},
    {"ac_number":40,"constituency":"Katpadi","district":"Vellore","region":"North","reserved":"GEN","winner":"DR M SUDHAKAR","party_21":"DMK","party_26":"TVK","votes":69868,"t21":74.0,"t26":88.8,"margin":5870,"flipped":True},
    {"ac_number":159,"constituency":"Kattumannarkoil","district":"Cuddalore","region":"Central","reserved":"SC","winner":"L.E. JOTHIMANI","party_21":"VCK","party_26":"VCK","votes":85179,"t21":75.9,"t26":83.1,"margin":33063,"flipped":False},
    {"ac_number":117,"constituency":"Kavundampalayam","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"KANIMOZHI SANTHOSH","party_21":"AIADMK","party_26":"TVK","votes":146466,"t21":66.1,"t26":86.3,"margin":42140,"flipped":True},
    {"ac_number":234,"constituency":"Killiyoor","district":"Kanniyakumari","region":"South","reserved":"GEN","winner":"RAJESH KUMAR. S","party_21":"INC","party_26":"INC","votes":66434,"t21":65.9,"t26":72.2,"margin":1311,"flipped":False},
    {"ac_number":64,"constituency":"Kilpennathur","district":"Tiruvannamalai","region":"North","reserved":"GEN","winner":"RAMACHANDRAN.S","party_21":"DMK","party_26":"AIADMK","votes":90503,"t21":79.4,"t26":91.2,"margin":30465,"flipped":True},
    {"ac_number":45,"constituency":"Kilvaithinankuppam","district":"Vellore","region":"North","reserved":"SC","winner":"THENRAL KUMAR. E","party_21":"AIADMK","party_26":"TVK","votes":74305,"t21":76.5,"t26":87.7,"margin":20255,"flipped":True},
    {"ac_number":164,"constituency":"Kilvelur","district":"Nagapattinam","region":"Delta","reserved":"SC","winner":"LATHA. T","party_21":"CPI(M)","party_26":"CPI(M)","votes":56108,"t21":79.4,"t26":88.9,"margin":2278,"flipped":False},
    {"ac_number":122,"constituency":"Kinathukadavu","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"VIGNESH K","party_21":"AIADMK","party_26":"TVK","votes":99950,"t21":70.6,"t26":87.8,"margin":11710,"flipped":True},
    {"ac_number":13,"constituency":"Kolathur","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"V. S. BABU","party_21":"DMK","party_26":"TVK","votes":82997,"t21":61.0,"t26":87.0,"margin":8795,"flipped":True},
    {"ac_number":218,"constituency":"Kovilpatti","district":"Thoothukudi","region":"South","reserved":"GEN","winner":"KARUNANITHI.K","party_21":"AIADMK","party_26":"DMK","votes":61643,"t21":67.4,"t26":80.2,"margin":843,"flipped":True},
    {"ac_number":53,"constituency":"Krishnagiri","district":"Krishnagiri","region":"North","reserved":"GEN","winner":"MUKUNDHAN.P","party_21":"AIADMK","party_26":"TVK","votes":89374,"t21":78.5,"t26":85.8,"margin":18844,"flipped":True},
    {"ac_number":136,"constituency":"Krishnarayapuram","district":"Karur","region":"Kongu","reserved":"SC","winner":"SATHYA. M","party_21":"DMK","party_26":"TVK","votes":62378,"t21":84.2,"t26":93.4,"margin":3503,"flipped":True},
    {"ac_number":137,"constituency":"Kulithalai","district":"Karur","region":"Kongu","reserved":"GEN","winner":"SURIYANUR. A. CHANDRAN","party_21":"DMK","party_26":"DMK","votes":68138,"t21":86.2,"t26":93.7,"margin":579,"flipped":False},
    {"ac_number":97,"constituency":"Kumarapalayam","district":"Namakkal","region":"Central","reserved":"GEN","winner":"C.VIJAYALAKSHMI","party_21":"AIADMK","party_26":"TVK","votes":81179,"t21":78.8,"t26":93.3,"margin":7696,"flipped":True},
    {"ac_number":171,"constituency":"Kumbakonam","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"VINOTH","party_21":"DMK","party_26":"TVK","votes":78650,"t21":71.4,"t26":81.9,"margin":679,"flipped":True},
    {"ac_number":148,"constituency":"Kunnam","district":"Perambalur","region":"Central","reserved":"GEN","winner":"SIVASANKAR. S.S","party_21":"DMK","party_26":"DMK","votes":87237,"t21":80.0,"t26":86.0,"margin":15557,"flipped":False},
    {"ac_number":156,"constituency":"Kurinjipadi","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"M.R.K.PANNEERSELVAM","party_21":"DMK","party_26":"DMK","votes":76695,"t21":82.1,"t26":89.9,"margin":7589,"flipped":False},
    {"ac_number":143,"constituency":"Lalgudi","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"LEEMAROSE MARTIN","party_21":"DMK","party_26":"AIADMK","votes":60795,"t21":79.2,"t26":87.4,"margin":2739,"flipped":True},
    {"ac_number":126,"constituency":"Madathukulam","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"R JAYARAMAKRISHNAN","party_21":"AIADMK","party_26":"DMK","votes":70458,"t21":72.4,"t26":87.7,"margin":15968,"flipped":True},
    {"ac_number":9,"constituency":"Madavaram","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"M.L.VIJAYPRABHU","party_21":"DMK","party_26":"TVK","votes":190462,"t21":66.4,"t26":83.9,"margin":94985,"flipped":True},
    {"ac_number":193,"constituency":"Madurai Central","district":"Madurai","region":"South","reserved":"GEN","winner":"MADHAR BADHURUDEEN","party_21":"DMK","party_26":"TVK","votes":63414,"t21":61.0,"t26":74.5,"margin":19128,"flipped":True},
    {"ac_number":189,"constituency":"Madurai East","district":"Madurai","region":"South","reserved":"GEN","winner":"KARTHIKEYAN S","party_21":"DMK","party_26":"TVK","votes":118777,"t21":71.3,"t26":80.8,"margin":16547,"flipped":True},
    {"ac_number":191,"constituency":"Madurai North","district":"Madurai","region":"South","reserved":"GEN","winner":"A.KALLANAI","party_21":"DMK","party_26":"TVK","votes":72853,"t21":63.6,"t26":73.2,"margin":18038,"flipped":True},
    {"ac_number":192,"constituency":"Madurai South","district":"Madurai","region":"South","reserved":"GEN","winner":"M.M.GOPISON","party_21":"DMK","party_26":"TVK","votes":62415,"t21":63.8,"t26":78.7,"margin":21529,"flipped":True},
    {"ac_number":194,"constituency":"Madurai West","district":"Madurai","region":"South","reserved":"GEN","winner":"THANGAPANDI SR","party_21":"AIADMK","party_26":"TVK","votes":88250,"t21":65.1,"t26":78.7,"margin":11931,"flipped":True},
    {"ac_number":35,"constituency":"Maduranthakam","district":"Kanchipuram","region":"North","reserved":"SC","winner":"MARAGATHAM KUMARAVEL.K","party_21":"AIADMK","party_26":"AIADMK","votes":69284,"t21":80.6,"t26":93.4,"margin":7194,"flipped":False},
    {"ac_number":7,"constituency":"Maduravoyal","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"RHEVANTH CHARAN","party_21":"DMK","party_26":"TVK","votes":141725,"t21":60.3,"t26":78.8,"margin":61509,"flipped":True},
    {"ac_number":71,"constituency":"Mailam","district":"Villupuram","region":"Central","reserved":"GEN","winner":"SHANMUGAM C VE","party_21":"PMK","party_26":"AIADMK","votes":82353,"t21":79.5,"t26":90.6,"margin":30041,"flipped":True},
    {"ac_number":144,"constituency":"Manachanallur","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"KATHIRAVAN. S","party_21":"DMK","party_26":"DMK","votes":81447,"t21":79.6,"t26":88.7,"margin":12364,"flipped":False},
    {"ac_number":187,"constituency":"Manamadurai","district":"Sivaganga","region":"South","reserved":"SC","winner":"ELANGOVAN.D","party_21":"DMK","party_26":"TVK","votes":69971,"t21":72.0,"t26":80.4,"margin":1208,"flipped":True},
    {"ac_number":138,"constituency":"Manapparai","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"R. KATHIRAVAN","party_21":"DMK","party_26":"TVK","votes":83041,"t21":76.0,"t26":90.0,"margin":1426,"flipped":True},
    {"ac_number":167,"constituency":"Mannargudi","district":"Tiruvarur","region":"Delta","reserved":"GEN","winner":"KAMARAJ. S","party_21":"DMK","party_26":"Others","votes":68416,"t21":74.3,"t26":82.8,"margin":1566,"flipped":True},
    {"ac_number":161,"constituency":"Mayiladuthurai","district":"Nagapattinam","region":"Delta","reserved":"GEN","winner":"JAMAL MOHAMED YOUNOOS. Y.N","party_21":"INC","party_26":"INC","votes":68011,"t21":70.1,"t26":80.4,"margin":10845,"flipped":False},
    {"ac_number":188,"constituency":"Melur","district":"Madurai","region":"South","reserved":"GEN","winner":"P.VISWANATHAN","party_21":"AIADMK","party_26":"INC","votes":60080,"t21":74.2,"t26":82.9,"margin":2724,"flipped":True},
    {"ac_number":111,"constituency":"Mettupalayam","district":"Tirupur","region":"Kongu","reserved":"GEN","winner":"SUNILANAND","party_21":"AIADMK","party_26":"TVK","votes":75664,"t21":75.1,"t26":86.6,"margin":7768,"flipped":True},
    {"ac_number":85,"constituency":"Mettur","district":"Salem","region":"Central","reserved":"GEN","winner":"VENKATACHALAM. G","party_21":"PMK","party_26":"AIADMK","votes":86498,"t21":75.0,"t26":90.5,"margin":19105,"flipped":True},
    {"ac_number":100,"constituency":"Modakurichi","district":"Erode","region":"Kongu","reserved":"GEN","winner":"D.SHANMUGAN","party_21":"BJP","party_26":"TVK","votes":60715,"t21":75.3,"t26":91.9,"margin":2430,"flipped":True},
    {"ac_number":212,"constituency":"Mudukulathur","district":"Ramanathapuram","region":"South","reserved":"GEN","winner":"R.S.RAJAKANNAPPAN","party_21":"DMK","party_26":"DMK","votes":68003,"t21":70.3,"t26":77.2,"margin":16598,"flipped":False},
    {"ac_number":145,"constituency":"Musiri","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"M.VIGNESH","party_21":"DMK","party_26":"TVK","votes":71281,"t21":76.0,"t26":88.4,"margin":17442,"flipped":True},
    {"ac_number":25,"constituency":"Mylapore","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"VENKATARAMANAN. P","party_21":"DMK","party_26":"TVK","votes":70070,"t21":56.6,"t26":75.6,"margin":28972,"flipped":True},
    {"ac_number":163,"constituency":"Nagapattinam","district":"Nagapattinam","region":"Delta","reserved":"GEN","winner":"M.H.JAWAHIRULLAH","party_21":"VCK","party_26":"DMK","votes":56305,"t21":72.0,"t26":86.7,"margin":9781,"flipped":True},
    {"ac_number":230,"constituency":"Nagercoil","district":"Kanniyakumari","region":"South","reserved":"GEN","winner":"AUSTIN","party_21":"BJP","party_26":"DMK","votes":69880,"t21":67.1,"t26":75.8,"margin":7570,"flipped":True},
    {"ac_number":94,"constituency":"Namakkal","district":"Namakkal","region":"Central","reserved":"GEN","winner":"DILIP C S","party_21":"DMK","party_26":"TVK","votes":79744,"t21":78.6,"t26":89.3,"margin":11008,"flipped":True},
    {"ac_number":227,"constituency":"Nanguneri","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"REDDIARPATTI V. NARAYANAN","party_21":"INC","party_26":"TVK","votes":74952,"t21":68.6,"t26":81.4,"margin":16419,"flipped":True},
    {"ac_number":169,"constituency":"Nannilam","district":"Tiruvarur","region":"Delta","reserved":"GEN","winner":"KAMARAJ. R","party_21":"AIADMK","party_26":"AIADMK","votes":103462,"t21":81.1,"t26":86.6,"margin":41724,"flipped":False},
    {"ac_number":131,"constituency":"Natham","district":"Dindigul","region":"South","reserved":"GEN","winner":"NATHAM VISWANATHAN R","party_21":"AIADMK","party_26":"AIADMK","votes":85708,"t21":79.0,"t26":91.6,"margin":11869,"flipped":False},
    {"ac_number":153,"constituency":"Neyveli","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"RAJENDRAN.R","party_21":"DMK","party_26":"AIADMK","votes":63731,"t21":74.2,"t26":88.4,"margin":10962,"flipped":True},
    {"ac_number":130,"constituency":"Nilakottai","district":"Dindigul","region":"South","reserved":"SC","winner":"AYYANAR.R","party_21":"AIADMK","party_26":"TVK","votes":68580,"t21":75.1,"t26":89.3,"margin":2925,"flipped":True},
    {"ac_number":128,"constituency":"Oddanchatram","district":"Dindigul","region":"South","reserved":"GEN","winner":"SAKKARAPANI. R","party_21":"DMK","party_26":"DMK","votes":93099,"t21":83.1,"t26":91.6,"margin":43249,"flipped":False},
    {"ac_number":84,"constituency":"Omalur","district":"Salem","region":"Central","reserved":"GEN","winner":"MANI. R","party_21":"AIADMK","party_26":"AIADMK","votes":112246,"t21":83.3,"t26":92.1,"margin":14539,"flipped":False},
    {"ac_number":175,"constituency":"Orathanad","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"R. VAITHILINGAM","party_21":"AIADMK","party_26":"DMK","votes":86759,"t21":78.3,"t26":83.6,"margin":35028,"flipped":True},
    {"ac_number":217,"constituency":"Ottapidaram","district":"Thoothukudi","region":"South","reserved":"SC","winner":"P .MATHANRAJA","party_21":"DMK","party_26":"TVK","votes":81625,"t21":69.8,"t26":80.3,"margin":29083,"flipped":True},
    {"ac_number":232,"constituency":"Padmanabhapuram","district":"Kanniyakumari","region":"South","reserved":"GEN","winner":"CHELLASWAMY. R","party_21":"DMK","party_26":"CPI(M)","votes":68938,"t21":70.1,"t26":76.6,"margin":15569,"flipped":True},
    {"ac_number":57,"constituency":"Palacode","district":"Dharmapuri","region":"North","reserved":"GEN","winner":"ANBALAGAN. K.P.","party_21":"AIADMK","party_26":"AIADMK","votes":102807,"t21":87.4,"t26":93.6,"margin":39042,"flipped":False},
    {"ac_number":127,"constituency":"Palani","district":"Dindigul","region":"South","reserved":"GEN","winner":"RAVIMANOHARAN. K","party_21":"DMK","party_26":"AIADMK","votes":66986,"t21":73.3,"t26":87.0,"margin":693,"flipped":True},
    {"ac_number":226,"constituency":"Palayamcottai","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"M.ABDUL WAHAB","party_21":"DMK","party_26":"DMK","votes":79744,"t21":57.8,"t26":70.3,"margin":13805,"flipped":False},
    {"ac_number":115,"constituency":"Palladam","district":"Nilgiris","region":"Kongu","reserved":"GEN","winner":"K.RAMKUMAR","party_21":"AIADMK","party_26":"TVK","votes":121297,"t21":66.7,"t26":91.3,"margin":37897,"flipped":True},
    {"ac_number":30,"constituency":"Pallavaram","district":"Kanchipuram","region":"Chennai Metro","reserved":"GEN","winner":"J.KAMATCHI","party_21":"DMK","party_26":"TVK","votes":133611,"t21":60.9,"t26":84.2,"margin":54693,"flipped":True},
    {"ac_number":154,"constituency":"Panruti","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"MOHAN. K","party_21":"DMK","party_26":"AIADMK","votes":78398,"t21":79.6,"t26":87.2,"margin":10663,"flipped":True},
    {"ac_number":172,"constituency":"Papanasam","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"A.M. SHAHJAHAN","party_21":"DMK","party_26":"IUML","votes":69284,"t21":74.8,"t26":81.0,"margin":1065,"flipped":True},
    {"ac_number":60,"constituency":"Pappireddippatti","district":"Dharmapuri","region":"North","reserved":"GEN","winner":"MARAGATHAM VETRIVEL","party_21":"AIADMK","party_26":"AIADMK","votes":101829,"t21":82.2,"t26":92.3,"margin":33114,"flipped":False},
    {"ac_number":209,"constituency":"Paramakudi","district":"Ramanathapuram","region":"South","reserved":"SC","winner":"ADVOCATE. KATHIRAVAN. K.K","party_21":"DMK","party_26":"DMK","votes":59161,"t21":70.6,"t26":80.8,"margin":3548,"flipped":False},
    {"ac_number":95,"constituency":"Paramathi-Velur","district":"Namakkal","region":"Central","reserved":"GEN","winner":"SEKAR S","party_21":"AIADMK","party_26":"AIADMK","votes":61349,"t21":81.1,"t26":92.1,"margin":308,"flipped":False},
    {"ac_number":176,"constituency":"Pattukkottai","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"ANNADURAI K","party_21":"DMK","party_26":"DMK","votes":65963,"t21":71.7,"t26":76.0,"margin":13754,"flipped":False},
    {"ac_number":58,"constituency":"Pennagaram","district":"Dharmapuri","region":"North","reserved":"GEN","winner":"GAJENDRAN. S.","party_21":"PMK","party_26":"TVK","votes":81240,"t21":85.0,"t26":92.0,"margin":3165,"flipped":True},
    {"ac_number":147,"constituency":"Perambalur","district":"Perambalur","region":"Central","reserved":"SC","winner":"SIVAKUMAR. K","party_21":"DMK","party_26":"TVK","votes":90882,"t21":78.2,"t26":87.3,"margin":14393,"flipped":True},
    {"ac_number":12,"constituency":"Perambur","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"C. JOSEPH VIJAY","party_21":"DMK","party_26":"TVK","votes":120365,"t21":63.0,"t26":90.4,"margin":53715,"flipped":True},
    {"ac_number":177,"constituency":"Peravurani","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"ASHOKKUMAR. N","party_21":"DMK","party_26":"DMK","votes":60919,"t21":77.0,"t26":82.5,"margin":3162,"flipped":False},
    {"ac_number":199,"constituency":"Periyakulam","district":"Theni","region":"South","reserved":"SC","winner":"SABARI IYNGARAN G.","party_21":"DMK","party_26":"TVK","votes":85656,"t21":69.9,"t26":79.4,"margin":19321,"flipped":True},
    {"ac_number":103,"constituency":"Perundurai","district":"Erode","region":"Kongu","reserved":"GEN","winner":"JAYAKUMAR. S","party_21":"AIADMK","party_26":"AIADMK","votes":70302,"t21":82.6,"t26":93.8,"margin":9693,"flipped":False},
    {"ac_number":123,"constituency":"Pollachi","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"K. NITHYANANDHAN","party_21":"AIADMK","party_26":"DMK","votes":62013,"t21":77.3,"t26":88.9,"margin":4627,"flipped":True},
    {"ac_number":66,"constituency":"Polur","district":"Tiruvannamalai","region":"North","reserved":"GEN","winner":"ABISHEK. R","party_21":"AIADMK","party_26":"TVK","votes":67961,"t21":82.3,"t26":90.3,"margin":227,"flipped":True},
    {"ac_number":2,"constituency":"Ponneri","district":"Tiruvallur","region":"Chennai Metro","reserved":"SC","winner":"DR.RAVI.M.S","party_21":"INC","party_26":"TVK","votes":110439,"t21":78.2,"t26":90.2,"margin":55768,"flipped":True},
    {"ac_number":162,"constituency":"Poompuhar","district":"Nagapattinam","region":"Delta","reserved":"GEN","winner":"NIVEDHA M MURUGAN","party_21":"DMK","party_26":"DMK","votes":81096,"t21":75.2,"t26":84.8,"margin":8260,"flipped":False},
    {"ac_number":5,"constituency":"Poonamallee","district":"Tiruvallur","region":"Chennai Metro","reserved":"SC","winner":"PRAKASAM.R","party_21":"DMK","party_26":"TVK","votes":161309,"t21":73.0,"t26":83.8,"margin":72740,"flipped":True},
    {"ac_number":180,"constituency":"Pudukkottai","district":"Pudukkottai","region":"Delta","reserved":"GEN","winner":"V. MUTHURAJA","party_21":"DMK","party_26":"DMK","votes":66825,"t21":72.9,"t26":84.3,"margin":1867,"flipped":False},
    {"ac_number":228,"constituency":"Radhapuram","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"DR.SATHISH CHRISTOPHER","party_21":"DMK","party_26":"TVK","votes":69947,"t21":68.1,"t26":81.0,"margin":12313,"flipped":True},
    {"ac_number":202,"constituency":"Rajapalayam","district":"Virudhunagar","region":"South","reserved":"GEN","winner":"JEGADESHWARI. K","party_21":"DMK","party_26":"TVK","votes":65548,"t21":73.9,"t26":85.4,"margin":10605,"flipped":True},
    {"ac_number":211,"constituency":"Ramanathapuram","district":"Ramanathapuram","region":"South","reserved":"GEN","winner":"KATHARBATCHA MUTHURAMALINGAM","party_21":"DMK","party_26":"DMK","votes":89137,"t21":68.8,"t26":76.1,"margin":12459,"flipped":False},
    {"ac_number":41,"constituency":"Ranipet","district":"Vellore","region":"North","reserved":"GEN","winner":"THAHIRA","party_21":"DMK","party_26":"TVK","votes":91149,"t21":77.2,"t26":88.9,"margin":5787,"flipped":True},
    {"ac_number":92,"constituency":"Rasipuram","district":"Namakkal","region":"Central","reserved":"SC","winner":"LOGESH TAMILSELVAN D","party_21":"DMK","party_26":"TVK","votes":74808,"t21":82.0,"t26":92.2,"margin":14511,"flipped":True},
    {"ac_number":78,"constituency":"Rishivandiam","district":"Villupuram","region":"Central","reserved":"GEN","winner":"KARTHIKEYAN K","party_21":"DMK","party_26":"DMK","votes":89711,"t21":80.2,"t26":89.5,"margin":4862,"flipped":False},
    {"ac_number":17,"constituency":"Royapuram","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"K.V. VIJAY DAMU","party_21":"DMK","party_26":"TVK","votes":59091,"t21":62.6,"t26":79.8,"margin":14249,"flipped":True},
    {"ac_number":23,"constituency":"Saidapet","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"ARUL PRAKASAM. M","party_21":"DMK","party_26":"TVK","votes":81205,"t21":57.4,"t26":78.6,"margin":28514,"flipped":True},
    {"ac_number":89,"constituency":"Salem (North)","district":"Salem","region":"Central","reserved":"GEN","winner":"SIVAKUMAR. K","party_21":"DMK","party_26":"TVK","votes":85710,"t21":72.1,"t26":88.4,"margin":14034,"flipped":True},
    {"ac_number":90,"constituency":"Salem (South)","district":"Salem","region":"Central","reserved":"GEN","winner":"VIJAY TAMILAN PARTHIBAN. A","party_21":"AIADMK","party_26":"TVK","votes":91371,"t21":76.0,"t26":91.7,"margin":33369,"flipped":True},
    {"ac_number":88,"constituency":"Salem (West)","district":"Salem","region":"Central","reserved":"GEN","winner":"LAKSHMANAN.S","party_21":"PMK","party_26":"TVK","votes":120407,"t21":71.8,"t26":91.0,"margin":74867,"flipped":True},
    {"ac_number":219,"constituency":"Sankarankovil","district":"Tirunelveli","region":"South","reserved":"SC","winner":"DR. DHILIPAN JAISHANKAR","party_21":"DMK","party_26":"AIADMK","votes":64865,"t21":71.5,"t26":82.7,"margin":6489,"flipped":True},
    {"ac_number":79,"constituency":"Sankarapuram","district":"Villupuram","region":"Central","reserved":"GEN","winner":"RAKESH R","party_21":"DMK","party_26":"AIADMK","votes":80250,"t21":79.6,"t26":88.6,"margin":3440,"flipped":True},
    {"ac_number":87,"constituency":"Sankari","district":"Salem","region":"Central","reserved":"GEN","winner":"VETRIVEL. S","party_21":"AIADMK","party_26":"AIADMK","votes":87342,"t21":83.7,"t26":93.6,"margin":9517,"flipped":False},
    {"ac_number":204,"constituency":"Sattur","district":"Virudhunagar","region":"South","reserved":"GEN","winner":"KADARKARAIRAJ. A","party_21":"DMK","party_26":"DMK","votes":62060,"t21":75.2,"t26":86.5,"margin":5989,"flipped":False},
    {"ac_number":93,"constituency":"Sendamangalam","district":"Namakkal","region":"Central","reserved":"ST","winner":"P CHANDRASEKAR","party_21":"DMK","party_26":"TVK","votes":68815,"t21":80.9,"t26":91.4,"margin":2655,"flipped":True},
    {"ac_number":190,"constituency":"Sholavandan","district":"Madurai","region":"South","reserved":"SC","winner":"KARUPPAIAH.M.V","party_21":"DMK","party_26":"TVK","votes":63907,"t21":79.5,"t26":87.9,"margin":2678,"flipped":True},
    {"ac_number":39,"constituency":"Sholinghur","district":"Vellore","region":"North","reserved":"GEN","winner":"G.KAPIL","party_21":"INC","party_26":"TVK","votes":84506,"t21":80.1,"t26":90.7,"margin":5686,"flipped":True},
    {"ac_number":27,"constituency":"Shozhinganallur","district":"Kanchipuram","region":"Chennai Metro","reserved":"GEN","winner":"ECR P SARAVANAN","party_21":"DMK","party_26":"TVK","votes":220382,"t21":55.5,"t26":80.8,"margin":96780,"flipped":True},
    {"ac_number":121,"constituency":"Singanallur","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"K.S.SRI GIRI PRASATH","party_21":"AIADMK","party_26":"TVK","votes":84163,"t21":61.7,"t26":81.9,"margin":19139,"flipped":True},
    {"ac_number":160,"constituency":"Sirkali","district":"Nagapattinam","region":"Delta","reserved":"SC","winner":"SENTHILSELVAN.R","party_21":"DMK","party_26":"DMK","votes":71449,"t21":74.9,"t26":83.1,"margin":11417,"flipped":False},
    {"ac_number":186,"constituency":"Sivaganga","district":"Sivaganga","region":"South","reserved":"GEN","winner":"KULANTHAI RANI A","party_21":"AIADMK","party_26":"TVK","votes":73737,"t21":66.3,"t26":77.1,"margin":15081,"flipped":True},
    {"ac_number":205,"constituency":"Sivakasi","district":"Virudhunagar","region":"South","reserved":"GEN","winner":"KEERTHANA S","party_21":"INC","party_26":"TVK","votes":68709,"t21":70.2,"t26":84.7,"margin":11670,"flipped":True},
    {"ac_number":29,"constituency":"Sriperumbudur","district":"Kanchipuram","region":"Chennai Metro","reserved":"SC","winner":"THENNARASU.K","party_21":"INC","party_26":"TVK","votes":147611,"t21":73.9,"t26":86.7,"margin":54246,"flipped":True},
    {"ac_number":139,"constituency":"Srirangam","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"RAMESH","party_21":"DMK","party_26":"TVK","votes":103235,"t21":76.2,"t26":88.9,"margin":33590,"flipped":True},
    {"ac_number":216,"constituency":"Srivaikuntam","district":"Thoothukudi","region":"South","reserved":"GEN","winner":"SARAVANAN. G","party_21":"INC","party_26":"TVK","votes":58814,"t21":72.3,"t26":82.3,"margin":1186,"flipped":True},
    {"ac_number":203,"constituency":"Srivilliputhur","district":"Virudhunagar","region":"South","reserved":"SC","winner":"KARTHIK.A","party_21":"AIADMK","party_26":"TVK","votes":65653,"t21":73.1,"t26":86.1,"margin":8581,"flipped":True},
    {"ac_number":116,"constituency":"Sulur","district":"Nilgiris","region":"Kongu","reserved":"GEN","winner":"NM.SUKUMAR","party_21":"AIADMK","party_26":"TVK","votes":90531,"t21":75.6,"t26":89.0,"margin":4790,"flipped":True},
    {"ac_number":31,"constituency":"Tambaram","district":"Kanchipuram","region":"Chennai Metro","reserved":"GEN","winner":"D.SARATHKUMAR","party_21":"DMK","party_26":"TVK","votes":118967,"t21":59.6,"t26":84.5,"margin":35621,"flipped":True},
    {"ac_number":222,"constituency":"Tenkasi","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"DR.KALAI KATHIRAVAN","party_21":"INC","party_26":"DMK","votes":79699,"t21":72.4,"t26":83.4,"margin":10299,"flipped":True},
    {"ac_number":56,"constituency":"Thalli","district":"Krishnagiri","region":"North","reserved":"GEN","winner":"RAMACHANDRAN. T","party_21":"CPI","party_26":"CPI","votes":78283,"t21":77.1,"t26":86.6,"margin":5240,"flipped":False},
    {"ac_number":174,"constituency":"Thanjavur","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"R. VIJAYSARAVANAN","party_21":"DMK","party_26":"TVK","votes":87705,"t21":65.7,"t26":78.7,"margin":16955,"flipped":True},
    {"ac_number":24,"constituency":"Theayagaraya Nagar","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"ANAND N","party_21":"DMK","party_26":"TVK","votes":51632,"t21":56.0,"t26":84.5,"margin":13027,"flipped":True},
    {"ac_number":15,"constituency":"Thiru-Vi-Ka-Nagar","district":"Chennai","region":"Chennai Metro","reserved":"SC","winner":"M. R. PALLAVI","party_21":"DMK","party_26":"TVK","votes":69125,"t21":60.6,"t26":79.2,"margin":22333,"flipped":True},
    {"ac_number":196,"constituency":"Thirumangalam","district":"Madurai","region":"South","reserved":"GEN","winner":"MANIMARAN.M","party_21":"AIADMK","party_26":"DMK","votes":88291,"t21":78.1,"t26":88.1,"margin":23807,"flipped":True},
    {"ac_number":181,"constituency":"Thirumayam","district":"Pudukkottai","region":"Delta","reserved":"GEN","winner":"REGUPATHY.S","party_21":"DMK","party_26":"DMK","votes":58201,"t21":75.8,"t26":82.8,"margin":1492,"flipped":False},
    {"ac_number":195,"constituency":"Thiruparankundram","district":"Madurai","region":"South","reserved":"GEN","winner":"NIRMALKUMAR. R.","party_21":"AIADMK","party_26":"TVK","votes":114316,"t21":72.7,"t26":82.1,"margin":41553,"flipped":True},
    {"ac_number":33,"constituency":"Thiruporur","district":"Kanchipuram","region":"North","reserved":"GEN","winner":"B.VIJAYARAJ","party_21":"VCK","party_26":"TVK","votes":110095,"t21":76.4,"t26":89.2,"margin":39351,"flipped":True},
    {"ac_number":166,"constituency":"Thiruthuraipundi","district":"Tiruvarur","region":"Delta","reserved":"SC","winner":"MARIMUTHU.K","party_21":"CPI","party_26":"CPI","votes":74062,"t21":76.7,"t26":84.2,"margin":12922,"flipped":False},
    {"ac_number":173,"constituency":"Thiruvaiyaru","district":"Thanjavur","region":"Delta","reserved":"GEN","winner":"DURAI. CHANDRASEKARAN","party_21":"DMK","party_26":"DMK","votes":80425,"t21":78.1,"t26":85.9,"margin":8555,"flipped":False},
    {"ac_number":4,"constituency":"Thiruvallur","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"DR. T. ARUNKUMAR","party_21":"DMK","party_26":"TVK","votes":92190,"t21":77.2,"t26":90.3,"margin":24760,"flipped":True},
    {"ac_number":168,"constituency":"Thiruvarur","district":"Tiruvarur","region":"Delta","reserved":"GEN","winner":"KALAIVANAN POONDI  K","party_21":"DMK","party_26":"DMK","votes":93408,"t21":73.2,"t26":83.8,"margin":18148,"flipped":False},
    {"ac_number":142,"constituency":"Thiruverambur","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"VIJAYAKUMAR (A) NAVALPATTU S. VIJI","party_21":"DMK","party_26":"TVK","votes":89837,"t21":66.6,"t26":82.3,"margin":8705,"flipped":True},
    {"ac_number":170,"constituency":"Thiruvidamarudur","district":"Thanjavur","region":"Delta","reserved":"SC","winner":"GOVI.CHEZHIAAN","party_21":"DMK","party_26":"DMK","votes":79951,"t21":75.8,"t26":81.5,"margin":14116,"flipped":False},
    {"ac_number":10,"constituency":"Thiruvottiyur","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"SENTHIL KUMAR. N","party_21":"DMK","party_26":"TVK","votes":110067,"t21":65.2,"t26":84.6,"margin":53564,"flipped":True},
    {"ac_number":119,"constituency":"Thondamuthur","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"S.P.VELUMANI","party_21":"AIADMK","party_26":"AIADMK","votes":93316,"t21":70.2,"t26":88.2,"margin":14725,"flipped":False},
    {"ac_number":214,"constituency":"Thoothukkudi","district":"Thoothukudi","region":"South","reserved":"GEN","winner":"SRINATH","party_21":"DMK","party_26":"TVK","votes":100536,"t21":65.1,"t26":81.7,"margin":37731,"flipped":True},
    {"ac_number":20,"constituency":"Thousand Lights","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"PRABHAKAR.J.C.D","party_21":"DMK","party_26":"TVK","votes":58965,"t21":56.2,"t26":83.7,"margin":15141,"flipped":True},
    {"ac_number":146,"constituency":"Thuraiyur","district":"Tiruchirappalli","region":"Delta","reserved":"SC","winner":"RAVISANKAR.M","party_21":"DMK","party_26":"TVK","votes":66263,"t21":76.6,"t26":87.6,"margin":9614,"flipped":True},
    {"ac_number":72,"constituency":"Tindivanam","district":"Villupuram","region":"Central","reserved":"SC","winner":"VANNI ARASU","party_21":"AIADMK","party_26":"VCK","votes":63833,"t21":78.4,"t26":89.5,"margin":734,"flipped":True},
    {"ac_number":215,"constituency":"Tiruchendur","district":"Thoothukudi","region":"South","reserved":"GEN","winner":"ANITHA R. RADHAKRISHNAN","party_21":"DMK","party_26":"DMK","votes":72723,"t21":70.0,"t26":80.0,"margin":5872,"flipped":False},
    {"ac_number":96,"constituency":"Tiruchengode","district":"Namakkal","region":"Central","reserved":"GEN","winner":"ARUNRAJ K G","party_21":"DMK","party_26":"TVK","votes":79500,"t21":78.7,"t26":91.4,"margin":28172,"flipped":True},
    {"ac_number":141,"constituency":"Tiruchirapalli (East)","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"C. JOSEPH VIJAY","party_21":"DMK","party_26":"TVK","votes":91381,"t21":66.9,"t26":83.0,"margin":27416,"flipped":True},
    {"ac_number":140,"constituency":"Tiruchirapalli (West)","district":"Tiruchirappalli","region":"Delta","reserved":"GEN","winner":"K.N.NEHRU","party_21":"DMK","party_26":"DMK","votes":88235,"t21":67.0,"t26":82.2,"margin":4786,"flipped":False},
    {"ac_number":208,"constituency":"Tiruchuli","district":"Virudhunagar","region":"South","reserved":"GEN","winner":"THANGAM THENARASU","party_21":"DMK","party_26":"DMK","votes":75085,"t21":77.5,"t26":88.3,"margin":13485,"flipped":False},
    {"ac_number":76,"constituency":"Tirukkoyilur","district":"Villupuram","region":"Central","reserved":"GEN","winner":"PALANISAMY S","party_21":"DMK","party_26":"AIADMK","votes":73033,"t21":76.3,"t26":89.5,"margin":285,"flipped":True},
    {"ac_number":224,"constituency":"Tirunelveli","district":"Tirunelveli","region":"South","reserved":"GEN","winner":"MURUGHAN.R.S.","party_21":"BJP","party_26":"TVK","votes":75840,"t21":66.9,"t26":79.3,"margin":11414,"flipped":True},
    {"ac_number":50,"constituency":"Tiruppattur","district":"Vellore","region":"North","reserved":"GEN","winner":"DR.THIRUPATHI. N","party_21":"DMK","party_26":"TVK","votes":105098,"t21":77.0,"t26":89.4,"margin":48263,"flipped":True},
    {"ac_number":185,"constituency":"Tiruppattur","district":"Sivaganga","region":"South","reserved":"GEN","winner":"SEENIVASA SETHUPATHY. R","party_21":"DMK","party_26":"TVK","votes":83375,"t21":72.0,"t26":78.3,"margin":1,"flipped":True},
    {"ac_number":113,"constituency":"Tiruppur (North)","district":"Tirupur","region":"Kongu","reserved":"GEN","winner":"V.SATHYABAMA","party_21":"AIADMK","party_26":"TVK","votes":131401,"t21":62.4,"t26":83.4,"margin":69992,"flipped":True},
    {"ac_number":114,"constituency":"Tiruppur (South)","district":"Nilgiris","region":"Kongu","reserved":"GEN","winner":"BALAMURUGAN. S","party_21":"DMK","party_26":"TVK","votes":73793,"t21":62.7,"t26":91.3,"margin":12901,"flipped":True},
    {"ac_number":3,"constituency":"Tiruttani","district":"Tiruvallur","region":"Chennai Metro","reserved":"GEN","winner":"G.HARI","party_21":"DMK","party_26":"AIADMK","votes":89169,"t21":78.8,"t26":91.2,"margin":5793,"flipped":True},
    {"ac_number":210,"constituency":"Tiruvadanai","district":"Ramanathapuram","region":"South","reserved":"GEN","winner":"RAJEEV","party_21":"INC","party_26":"TVK","votes":69551,"t21":68.7,"t26":77.6,"margin":2513,"flipped":True},
    {"ac_number":63,"constituency":"Tiruvannamalai","district":"Tiruvannamalai","region":"North","reserved":"GEN","winner":"VELU. E.V","party_21":"DMK","party_26":"DMK","votes":88273,"t21":71.7,"t26":88.0,"margin":2455,"flipped":False},
    {"ac_number":151,"constituency":"Tittakudi","district":"Cuddalore","region":"Central","reserved":"SC","winner":"GANESAN C.V","party_21":"DMK","party_26":"DMK","votes":63106,"t21":76.3,"t26":84.2,"margin":2629,"flipped":False},
    {"ac_number":108,"constituency":"Udhagamandalam","district":"Tirupur","region":"Kongu","reserved":"GEN","winner":"BHOJARAJAN.M","party_21":"INC","party_26":"BJP","votes":48488,"t21":67.8,"t26":78.9,"margin":976,"flipped":True},
    {"ac_number":125,"constituency":"Udumalpet","district":"Coimbatore","region":"Kongu","reserved":"GEN","winner":"JAYAKUMAR M.","party_21":"AIADMK","party_26":"DMK","votes":68549,"t21":71.3,"t26":88.3,"margin":2882,"flipped":True},
    {"ac_number":77,"constituency":"Ulundurpet","district":"Villupuram","region":"Central","reserved":"GEN","winner":"VASANTHAVEL G R","party_21":"DMK","party_26":"DMK","votes":98471,"t21":82.6,"t26":90.1,"margin":2277,"flipped":False},
    {"ac_number":197,"constituency":"Usilampatti","district":"Madurai","region":"South","reserved":"GEN","winner":"VIJAY. M","party_21":"AIADMK","party_26":"TVK","votes":65743,"t21":73.8,"t26":83.8,"margin":1805,"flipped":True},
    {"ac_number":51,"constituency":"Uthangarai","district":"Krishnagiri","region":"North","reserved":"SC","winner":"N ELAIYARAJA","party_21":"AIADMK","party_26":"TVK","votes":70201,"t21":78.4,"t26":87.2,"margin":5198,"flipped":True},
    {"ac_number":36,"constituency":"Uthiramerur","district":"Kanchipuram","region":"North","reserved":"GEN","winner":"MUNIRATHINAM.J","party_21":"DMK","party_26":"TVK","votes":84917,"t21":80.1,"t26":92.7,"margin":14223,"flipped":True},
    {"ac_number":124,"constituency":"Valparai","district":"Coimbatore","region":"Kongu","reserved":"SC","winner":"KUTTY (ALIAS) SUDHAKAR. A","party_21":"AIADMK","party_26":"DMK","votes":54671,"t21":70.0,"t26":86.7,"margin":9371,"flipped":True},
    {"ac_number":69,"constituency":"Vandavasi","district":"Tiruvannamalai","region":"North","reserved":"SC","winner":"AMBETHKUMAR. S","party_21":"DMK","party_26":"DMK","votes":63805,"t21":76.8,"t26":89.6,"margin":3333,"flipped":False},
    {"ac_number":47,"constituency":"Vaniayambadi","district":"Vellore","region":"North","reserved":"GEN","winner":"SYED FAROOQ BASHA SSB","party_21":"AIADMK","party_26":"IUML","votes":73181,"t21":75.6,"t26":87.4,"margin":2982,"flipped":True},
    {"ac_number":73,"constituency":"Vanur","district":"Villupuram","region":"Central","reserved":"SC","winner":"GOWTHAM D","party_21":"AIADMK","party_26":"DMK","votes":68873,"t21":79.8,"t26":91.8,"margin":7034,"flipped":True},
    {"ac_number":220,"constituency":"Vasudevanallur","district":"Tirunelveli","region":"South","reserved":"SC","winner":"E. RAJA","party_21":"DMK","party_26":"DMK","votes":63045,"t21":71.9,"t26":83.0,"margin":6583,"flipped":False},
    {"ac_number":165,"constituency":"Vedaranyam","district":"Nagapattinam","region":"Delta","reserved":"GEN","winner":"MANIAN. O.S","party_21":"AIADMK","party_26":"AIADMK","votes":59172,"t21":80.6,"t26":86.6,"margin":7331,"flipped":False},
    {"ac_number":133,"constituency":"Vedasandur","district":"Dindigul","region":"South","reserved":"GEN","winner":"SAMINATHAN. T","party_21":"DMK","party_26":"DMK","votes":84948,"t21":80.2,"t26":92.9,"margin":10063,"flipped":False},
    {"ac_number":91,"constituency":"Veerapandi","district":"Salem","region":"Central","reserved":"GEN","winner":"PALANIVEL. M.S","party_21":"AIADMK","party_26":"TVK","votes":79907,"t21":85.6,"t26":94.3,"margin":4071,"flipped":True},
    {"ac_number":26,"constituency":"Velachery","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"KUMAR. R","party_21":"INC","party_26":"TVK","votes":80430,"t21":56.2,"t26":85.2,"margin":33305,"flipped":True},
    {"ac_number":43,"constituency":"Vellore","district":"Vellore","region":"North","reserved":"GEN","winner":"M.M.VINOTH KANNAN","party_21":"DMK","party_26":"TVK","votes":73032,"t21":70.2,"t26":88.7,"margin":6777,"flipped":True},
    {"ac_number":54,"constituency":"Veppanahalli","district":"Krishnagiri","region":"North","reserved":"GEN","winner":"SRINIVASAN.P.S","party_21":"AIADMK","party_26":"DMK","votes":74691,"t21":81.3,"t26":90.3,"margin":138,"flipped":True},
    {"ac_number":75,"constituency":"Vikravandi","district":"Villupuram","region":"Central","reserved":"GEN","winner":"SIVAKUMAR C","party_21":"DMK","party_26":"PMK","votes":69727,"t21":81.4,"t26":91.6,"margin":910,"flipped":True},
    {"ac_number":213,"constituency":"Vilathikulam","district":"Thoothukudi","region":"South","reserved":"GEN","winner":"MARKANDAYAN G V","party_21":"DMK","party_26":"DMK","votes":58395,"t21":76.5,"t26":85.2,"margin":8228,"flipped":False},
    {"ac_number":233,"constituency":"Vilavancode","district":"Kanniyakumari","region":"South","reserved":"GEN","winner":"PRAVEEN T.T","party_21":"INC","party_26":"INC","votes":70755,"t21":66.8,"t26":76.7,"margin":20970,"flipped":False},
    {"ac_number":14,"constituency":"Villivakkam","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"AADHAV ARJUNA","party_21":"DMK","party_26":"TVK","votes":66445,"t21":55.9,"t26":86.7,"margin":17302,"flipped":True},
    {"ac_number":74,"constituency":"Villupuram","district":"Villupuram","region":"Central","reserved":"GEN","winner":"LAKSHMANAN R","party_21":"DMK","party_26":"DMK","votes":72982,"t21":77.0,"t26":87.8,"margin":4119,"flipped":False},
    {"ac_number":179,"constituency":"Viralimalai","district":"Pudukkottai","region":"Delta","reserved":"GEN","winner":"VIJAYABASKAR. C","party_21":"AIADMK","party_26":"AIADMK","votes":105773,"t21":85.4,"t26":90.6,"margin":62073,"flipped":False},
    {"ac_number":206,"constituency":"Virudhunagar","district":"Virudhunagar","region":"South","reserved":"GEN","winner":"SELVAM P","party_21":"DMK","party_26":"TVK","votes":63653,"t21":71.3,"t26":83.9,"margin":9391,"flipped":True},
    {"ac_number":22,"constituency":"Virugampakkam","district":"Chennai","region":"Chennai Metro","reserved":"GEN","winner":"SABARINATHAN.R","party_21":"DMK","party_26":"TVK","votes":76092,"t21":57.6,"t26":86.2,"margin":27086,"flipped":True},
    {"ac_number":152,"constituency":"Vriddhachalam","district":"Cuddalore","region":"Central","reserved":"GEN","winner":"PREMALLATHA VIJAYAKANT","party_21":"INC","party_26":"DMDK","votes":69351,"t21":77.0,"t26":87.0,"margin":2387,"flipped":True},
    {"ac_number":83,"constituency":"Yercaud","district":"Salem","region":"Central","reserved":"ST","winner":"USHARANI. P","party_21":"AIADMK","party_26":"AIADMK","votes":87772,"t21":83.1,"t26":93.0,"margin":2189,"flipped":False}
]


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def party_color(p):
    return PC.get(p, "#6b7280")

def region_color(r):
    return RC.get(r, "#6b7280")

def fmt_num(n):
    if n is None: return "—"
    return f"{int(n):,}"

def swing_str(v):
    if v is None: return "New"
    return f"+{v}pp" if v >= 0 else f"{v}pp"

def hex_to_rgba(hex_color, alpha=0.73):
    """Convert #rrggbb to rgba(r,g,b,alpha) string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def party_badge(p):
    c = party_color(p)
    return f'<span style="background:{c}22;color:{c};font-size:11px;font-weight:700;padding:2px 7px;border-radius:4px;font-family:IBM Plex Mono,monospace">{p}</span>'

def region_badge(r):
    c = region_color(r)
    return f'<span style="background:{c}22;color:{c};font-size:11px;font-weight:700;padding:2px 7px;border-radius:4px;font-family:IBM Plex Mono,monospace">{r}</span>'

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_family="IBM Plex Sans",
    font_color="#374151",
    margin=dict(l=10, r=10, t=30, b=10),
)

def donut_chart(labels, values, colors, title="", height=280):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(
            colors=[hex_to_rgba(c, 0.87) for c in colors],
            line=dict(color=colors, width=1.5),
        ),
        hole=0.62,
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>",
        hoverlabel=dict(
            bgcolor=colors,
            font_color="#ffffff",
            bordercolor=colors,
            font_size=12,
        ),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=height,
                      showlegend=True,
                      legend=dict(font_size=10, orientation="v", x=1.02))
    if title:
        fig.update_layout(title=dict(text=title, font_size=11, font_color="#9ca3af", x=0))
    return fig

def grouped_bar(labels, d1, d2, n1, n2, colors2=None, height=260):
    fig = go.Figure()
    fig.add_bar(name=n1, x=labels, y=d1,
                marker_color="rgba(156,163,175,.5)",
                marker_line_color="rgba(107,114,128,.8)",
                marker_line_width=1,
                hovertemplate="<b>%{x}</b><br>" + n1 + ": %{y}%<extra></extra>")
    fig.add_bar(name=n2, x=labels, y=d2,
                marker_color=[hex_to_rgba(c, 0.8) for c in (colors2 or ["#6b7280"] * len(labels))],
                marker_line_color=colors2 or ["#6b7280"] * len(labels),
                marker_line_width=1,
                hovertemplate="<b>%{x}</b><br>" + n2 + ": %{y}%<extra></extra>",
                hoverlabel=dict(
                    bgcolor=[hex_to_rgba(c, 0.95) for c in (colors2 or ["#6b7280"]*len(labels))],
                    font_color="#fff",
                    bordercolor=[c for c in (colors2 or ["#6b7280"]*len(labels))]
                ))
    fig.update_layout(**PLOTLY_LAYOUT, height=height, barmode="group",
                      legend=dict(font_size=10), xaxis_tickfont_size=9)
    return fig

def hbar(labels, values, colors, height=300):
    fig = go.Figure(go.Bar(
        y=labels, x=values, orientation="h",
        marker_color=[hex_to_rgba(c, 0.8) for c in colors],
        marker_line_color=colors, marker_line_width=1,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=height,
                      showlegend=False,
                      yaxis=dict(autorange="reversed", tickfont_size=9),
                      xaxis_tickfont_size=9)
    return fig

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION — pure HTML, mirrors HTML dashboard exactly
# ─────────────────────────────────────────────

# Read active page from query params (falls back to "overview")
_qp = st.query_params.get("page", "overview")
VALID_PAGES = {"overview","seats","turnout","flips","drill",
               "q1","q2","q3","q4","q5","q6","q7","q8","q9"}
page = _qp if _qp in VALID_PAGES else "overview"

_NAV = [
    ("sec",      "",    "Overview"),
    ("overview", "▣",  "Dashboard"),
    ("sec",      "",    "Stories"),
    ("seats",    "◉",  "Seat & Vote Share"),
    ("turnout",  "↑",  "Turnout Story"),
    ("flips",    "⇄",  "Flips Analysis"),
    ("drill",    "≡",  "Constituency Drill"),
    ("sec",      "",    "Research Q&amp;A"),
    ("q1",  "Q1", "Turnout Top/Bot"),
    ("q2",  "Q2", "Same Party Streak"),
    ("q3",  "Q3", "Biggest Flips"),
    ("q4",  "Q4", "Margin Analysis"),
    ("q5",  "Q5", "Regional Vote Split"),
    ("q6",  "Q6", "State Vote Split"),
    ("q7",  "Q7", "NOTA Analysis"),
    ("q8",  "Q8", "Postal Correlation"),
    ("q9",  "Q9", "Literacy Correlation"),
]

def _nav_html(current):
    rows = []
    for (key, dot, label) in _NAV:
        if key == "sec":
            rows.append(
                f'<div style="font-size:9px;font-weight:700;color:#9ca3af;'
                f'text-transform:uppercase;letter-spacing:.12em;'
                f'padding:.65rem 1.1rem .25rem;font-family:IBM Plex Mono,monospace;">'
                f'{label}</div>'
            )
        else:
            active = (key == current)
            bg     = "#fff8e6" if active else "transparent"
            col    = "#c47d00" if active else "#6b7280"
            fw     = "600"     if active else "500"
            border = "#f0a500" if active else "transparent"
            rows.append(
                f'<a href="?page={key}" target="_self" style="'
                f'display:flex;align-items:center;gap:.55rem;'
                f'padding:.55rem 1.1rem;'
                f'border-left:3px solid {border};'
                f'background:{bg};'
                f'color:{col};'
                f'font-weight:{fw};'
                f'font-size:12px;'
                f'font-family:IBM Plex Sans,sans-serif;'
                f'text-decoration:none;'
                f'transition:background .15s,color .15s;'
                f'cursor:pointer;">'
                f'<span style="font-size:13px;font-family:IBM Plex Mono,monospace;'
                f'min-width:18px;flex-shrink:0;">{dot}</span>'
                f'<span>{label}</span>'
                f'</a>'
            )
    return "\n".join(rows)

st.sidebar.markdown(_nav_html(page), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hdr">
  <div class="hdr-left">
    <div class="hdr-title">🗳️ Tamil Nadu Elections <span>2021 vs 2026</span></div>
    <div class="hdr-sub">234 constituencies &nbsp;·&nbsp; Complete Deep Analysis &nbsp;·&nbsp; All 6 Regions &nbsp;·&nbsp; Source: ECI</div>
  </div>
  <div class="hdr-kpis">
    <div class="hkpi"><div class="hkpi-n">234</div><div class="hkpi-l">Constituencies</div></div>
    <div class="hkpi"><div class="hkpi-n">163</div><div class="hkpi-l">Seats Flipped</div></div>
    <div class="hkpi"><div class="hkpi-n">108</div><div class="hkpi-l">TVK Seats Won</div></div>
    <div class="hkpi"><div class="hkpi-n">86.2%</div><div class="hkpi-l">Avg Turnout 2026</div></div>
    <div class="hkpi"><div class="hkpi-n">+12.8pp</div><div class="hkpi-l">Turnout Surge</div></div>
    <div class="hkpi"><div class="hkpi-n">34.9%</div><div class="hkpi-l">TVK Vote Share</div></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════
if page == "overview":
    st.markdown('''<div class="pg-title">📊 Dashboard Overview</div><div class="pg-desc">Key headline numbers from the 2026 Tamil Nadu Assembly Election across all 234 constituencies.</div>''', unsafe_allow_html=True)

    kpi_cards = [
        {"num": "234", "lbl": "Constituencies", "s": "", "c": "#c47d00"},
        {"num": "163", "lbl": "Seats Flipped", "s": "69.7% of all seats", "c": "#dc2626"},
        {"num": "71", "lbl": "Seats Retained", "s": "Same party both elections", "c": "#16a34a"},
        {"num": "86.2%", "lbl": "Avg Turnout 2026", "s": "Up from 73.4% in 2021", "c": "#7c3aed"},
        {"num": "+12.8pp", "lbl": "Statewide Surge", "s": "", "c": "#d97706"},
        {"num": "4.91Cr", "lbl": "Total Votes 2026", "s": "vs 4.59Cr in 2021", "c": "#2563eb"},
    ]
    cols = st.columns(6)
    for col, k in zip(cols, kpi_cards):
        with col:
            sub = f"<div class='ks'>{k['s']}</div>" if k['s'] else "<div class='ks'>&nbsp;</div>"
            st.markdown(f"""
            <div class="kcard" style="--c:{k['c']}">
                <div class="kn" style="color:{k['c']}">{k['num']}</div>
                <div class="kl">{k['lbl']}</div>
                {sub}
            </div>""", unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)

    def seats_bar(data, title):
        df = pd.DataFrame(data)
        mx = df["seats"].max()
        rows = ""
        for _, r in df.head(9).iterrows():
            c = party_color(r["pg"])
            w = r["seats"] / mx * 100
            rows += f"""
            <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem">
              {party_badge(r['pg'])}
              <div style="flex:1;background:#e5e7eb;border-radius:2px;height:8px;overflow:hidden">
                <div style="width:{w:.1f}%;height:100%;background:{c};border-radius:2px"></div>
              </div>
              <span style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#6b7280;min-width:22px;text-align:right">{int(r['seats'])}</span>
            </div>"""
        return f'<div class="card"><div class="ct">{title}</div>{rows}</div>'

    with col1:
        st.markdown(seats_bar(SEATS26, "🏛️ Seats Won — 2026"), unsafe_allow_html=True)
    with col2:
        st.markdown(seats_bar(SEATS21, "🏛️ Seats Won — 2021"), unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Headline shift:</strong> TVK entered as a new party and won 108 of 234 seats (46%).
        DMK fell from 133→59 and AIADMK from 66→47.
        Statewide turnout surged from 73.4% to 86.2%, adding ~3.2 crore voters.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: SEATS & VOTE SHARE
# ════════════════════════════════════════════
elif page == "seats":
    st.markdown('''<div class="pg-title">🏛️ Seat &amp; Vote Share</div><div class="pg-desc">Party seat counts and vote share. Filter by region to see how each party performed across Tamil Nadu's six editorial regions.</div>''', unsafe_allow_html=True)

    reg_filter = st.radio("Region", ["All Regions"] + REGIONS, horizontal=True, key="seats_reg")
    reg = None if reg_filter == "All Regions" else reg_filter

    if reg is None:
        sd = SEATS26
        vd = VS26
    else:
        m = {}
        for r in REG_SEATS:
            if r["region"] == reg:
                m[r["pg"]] = m.get(r["pg"], 0) + r["seats"]
        sd = sorted([{"pg": k, "seats": v} for k, v in m.items()], key=lambda x: -x["seats"])
        vd = sorted([r for r in REG_VS if r["region"] == reg], key=lambda x: -x["pct"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="ct">🏛️ Seats Won — 2026 {"— " + reg if reg else ""}</div>', unsafe_allow_html=True)
        labels = [r["pg"] for r in sd]
        vals = [r["seats"] for r in sd]
        colors = [party_color(p) for p in labels]
        fig = donut_chart(labels, vals, colors)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="ct">📊 Vote Share % — 2026</div>', unsafe_allow_html=True)
        vl = [r["pg"] for r in vd]
        vv = [r["pct"] for r in vd]
        vc = [party_color(p) for p in vl]
        fig2 = donut_chart(vl, vv, vc)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="ct">📊 Vote Share — 2021 vs 2026 Comparison</div>', unsafe_allow_html=True)
    maj = ["TVK", "DMK", "AIADMK", "INC", "BJP", "PMK", "VCK", "NTK"]
    d21 = [next((r["pct"] for r in VS21 if r["pg"] == p), 0) for p in maj]
    d26 = [next((r["pct"] for r in VS26 if r["pg"] == p), 0) for p in maj]
    fig3 = grouped_bar(maj, d21, d26, "2021 %", "2026 %",
                       colors2=[party_color(p) for p in maj], height=260)
    st.plotly_chart(fig3, use_container_width=True)


# ════════════════════════════════════════════
# PAGE: TURNOUT STORY
# ════════════════════════════════════════════
elif page == "turnout":
    st.markdown('''<div class="pg-title">📈 Turnout Story</div><div class="pg-desc">Voter turnout surged from 73.4% in 2021 to 86.2% in 2026. Chennai Metro led with some constituencies jumping 30+ pp.</div>''', unsafe_allow_html=True)

    # KPI number cards
    turnout_kpis = [
        {"num": "73.4%", "lbl": "Avg Turnout 2021", "s": "Statewide baseline", "c": "#2563eb"},
        {"num": "86.2%", "lbl": "Avg Turnout 2026", "s": "Record high", "c": "#16a34a"},
        {"num": "+12.8pp", "lbl": "Statewide Surge", "s": "Biggest jump in decades", "c": "#d97706"},
        {"num": "+30.8pp", "lbl": "Biggest (Villivakkam)", "s": "Chennai Metro", "c": "#7c3aed"},
    ]
    t_cols = st.columns(4)
    for col, k in zip(t_cols, turnout_kpis):
        with col:
            st.markdown(f"""<div class="kcard" style="--c:{k['c']}">
                <div class="kn" style="color:{k['c']}">{k['num']}</div>
                <div class="kl">{k['lbl']}</div>
                {"<div class='ks'>" + k['s'] + "</div>" if k['s'] else ""}
            </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight" style="margin-top:.75rem">
        <strong>Chennai story:</strong> Every constituency in the bottom-5 of 2021 (55–56%) surged by 25–31pp in 2026.
        The bottom-5 in 2026 shifted entirely to the South region.
    </div>""", unsafe_allow_html=True)

    df = pd.DataFrame(SURGE20)
    fig = hbar(
        df["constituency"].tolist(),
        df["delta"].tolist(),
        [region_color(r) for r in df["region"].tolist()],
        height=520,
    )
    fig.update_layout(title="🚀 Turnout Surge — Visual", title_font_size=11)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="ct">🚀 Top 20 Turnout Surge Constituencies</div>', unsafe_allow_html=True)
    rows = ""
    for i, r in enumerate(SURGE20):
        w = r["delta"] / 35 * 100
        rows += f"""<tr>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{i+1}</td>
          <td>{r['constituency']}</td>
          <td>{region_badge(r['region'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['t21']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['t26']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#16a34a;font-weight:600">+{r['delta']:.1f}pp</td>
          <td style="width:100px"><div style="background:#e5e7eb;border-radius:2px;height:8px;overflow:hidden">
            <div style="width:{w:.1f}%;height:100%;background:#16a34a;border-radius:2px"></div>
          </div></td>
        </tr>"""
    st.markdown(f"""
    <div class="card" style="overflow-x:auto">
      <table class="tbl">
        <thead><tr><th>#</th>
          <th>📍 Constituency</th>
          <th>🗺️ Region</th>
          <th>📅 2021%</th>
          <th>📅 2026%</th>
          <th>🚀 Surge</th>
          <th>📊 Bar</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table></div></div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: FLIPS ANALYSIS
# ════════════════════════════════════════════
elif page == "flips":
    st.markdown('''<div class="pg-title">🔄 Flips Analysis</div><div class="pg-desc">163 of 234 seats (69.7%) changed winning party between 2021 and 2026.</div>''', unsafe_allow_html=True)

    # KPI number cards
    flip_kpis = [
        {"num": "163", "lbl": "Total Seats Flipped", "s": "69.7% of all seats", "c": "#dc2626"},
        {"num": "71", "lbl": "Seats Retained", "s": "Same party both elections", "c": "#16a34a"},
        {"num": "108", "lbl": "TVK Gains (New Party)", "s": "From 0 seats in 2021", "c": "#7c3aed"},
    ]
    f_cols = st.columns(3)
    for col, k in zip(f_cols, flip_kpis):
        with col:
            st.markdown(f"""<div class="kcard" style="--c:{k['c']}">
                <div class="kn" style="color:{k['c']}">{k['num']}</div>
                <div class="kl">{k['lbl']}</div>
                {"<div class='ks'>" + k['s'] + "</div>" if k['s'] else ""}
            </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown('<div class="ct">⇄ Gains vs Losses by Party</div>', unsafe_allow_html=True)
        fs = [r for r in FLIP_SUMMARY if r["gained"] or r["lost"]]
        fs.sort(key=lambda x: -x["gained"])
        mx_g = max(r["gained"] for r in fs)
        mx_l = max(r["lost"] for r in fs)
        rows = ""
        for r in fs:
            gw = r["gained"] / mx_g * 44 if mx_g else 0
            lw = r["lost"] / mx_l * 44 if mx_l else 0
            rows += f"""
            <div style="display:flex;align-items:center;gap:.5rem;padding:.4rem 0;border-bottom:1px solid #f0f2f7">
              <div style="min-width:62px">{party_badge(r['party'])}</div>
              <div style="flex:1;display:flex;gap:3px;align-items:center">
                <div style="background:#dcfce7;border-radius:3px;height:16px;display:flex;align-items:center;justify-content:flex-end;padding-right:4px;font-size:9px;font-family:IBM Plex Mono,monospace;color:#15803d;font-weight:700;min-width:{max(gw,1):.1f}%">{r['gained'] or ''}</div>
                <div style="color:#d1d5db;font-size:9px;width:6px;text-align:center">|</div>
                <div style="background:#fee2e2;border-radius:3px;height:16px;display:flex;align-items:center;padding-left:4px;font-size:9px;font-family:IBM Plex Mono,monospace;color:#b91c1c;font-weight:700;min-width:{max(lw,1):.1f}%">{r['lost'] or ''}</div>
              </div>
            </div>"""
        st.markdown(f"""<div class="card">{rows}
          <div style="display:flex;gap:1rem;margin-top:.5rem;font-size:10px;font-family:IBM Plex Mono,monospace">
            <span style="color:#16a34a">■ Gained</span>
            <span style="color:#dc2626">■ Lost</span>
          </div></div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ct">🗺️ Seats by Region — 2026</div>', unsafe_allow_html=True)
        parties = ["TVK", "DMK", "AIADMK", "INC", "PMK", "VCK", "BJP", "Others", "CPI", "CPI(M)", "IUML", "DMDK"]
        fig = go.Figure()
        for p in parties:
            vals = []
            for reg in REGIONS:
                v = next((r["seats"] for r in REG_SEATS if r["region"] == reg and r["pg"] == p), 0)
                vals.append(v)
            if any(v > 0 for v in vals):
                c = party_color(p)
                fig.add_bar(name=p, x=REGIONS, y=vals,
                            marker_color=hex_to_rgba(c, 0.8), marker_line_color=c,
                            marker_line_width=1)
        fig.update_layout(**PLOTLY_LAYOUT, barmode="stack", height=340,
                          legend=dict(font_size=9, orientation="v"),
                          xaxis_tickfont_size=9)
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE: CONSTITUENCY DRILL
# ════════════════════════════════════════════
elif page == "drill":
    st.markdown('''<div class="pg-title">🔍 Constituency Drill-through</div><div class="pg-desc">All 234 constituencies — searchable and filterable.</div>''', unsafe_allow_html=True)

    # Search box with icon + styled dropdowns (mirrors HTML dashboard)
    st.markdown("""
    <style>
    /* Search box icon overlay */
    div[data-testid="stTextInput"] > div > div > div > input {
        padding-left: 2rem !important;
        background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' fill='none' stroke='%239ca3af' stroke-width='2' viewBox='0 0 24 24'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='M21 21l-4.35-4.35'/%3E%3C/svg%3E") no-repeat 0.5rem center !important;
        border: 1px solid #e2e5ef !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: #1a1d2e !important;
    }
    div[data-testid="stTextInput"] > div > div > div > input:focus {
        border-color: #f0a500 !important;
        box-shadow: 0 0 0 1px #f0a500 !important;
    }
    /* Dropdown styling to match HTML filter buttons */
    div[data-testid="stSelectbox"] > div > div > div {
        border: 1px solid #e2e5ef !important;
        border-radius: 6px !important;
        background: #fff !important;
        font-size: 12px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        color: #6b7280 !important;
    }
    div[data-testid="stSelectbox"] > div > div > div:focus-within {
        border-color: #f0a500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    with c1:
        search = st.text_input("🔍 Search", "", placeholder="Search constituency, winner, district…", label_visibility="collapsed")
    with c2:
        party_filter = st.selectbox("Party", ["All parties"] + sorted(set(r["party_26"] for r in DRILL_DATA)), label_visibility="collapsed")
    with c3:
        region_filter = st.selectbox("Region", ["All regions"] + REGIONS, label_visibility="collapsed")
    with c4:
        flip_filter = st.selectbox("Status", ["All", "Flipped", "Held"], label_visibility="collapsed")

    filtered = []
    for r in DRILL_DATA:
        q = search.lower()
        if q and not (q in r["constituency"].lower() or q in r["winner"].lower() or q in r.get("district", "").lower()):
            continue
        if party_filter != "All parties" and r["party_26"] != party_filter:
            continue
        if region_filter != "All regions" and r["region"] != region_filter:
            continue
        if flip_filter == "Flipped" and not r["flipped"]:
            continue
        if flip_filter == "Held" and r["flipped"]:
            continue
        filtered.append(r)

    st.markdown(f'<div style="font-size:11px;color:#6b7280;margin-bottom:.65rem">Showing {len(filtered)} of {len(DRILL_DATA)} constituencies</div>', unsafe_allow_html=True)

    rows = ""
    RES_CLS = {"GEN":"b-GEN","SC":"b-SC","ST":"b-ST"}
    for i, r in enumerate(filtered):
        flip_span = '<span class="flip-y">FLIPPED</span>' if r["flipped"] else '<span class="flip-n">held</span>'
        res_cls   = RES_CLS.get(r.get("reserved","GEN"), "b-GEN")
        rows += f"""<tr>
          <td class="num">{i+1}</td>
          <td style="white-space:nowrap">{r['constituency']}</td>
          <td style="font-size:11px;color:#6b7280">{r.get('district','')}</td>
          <td>{region_badge(r['region'])}</td>
          <td><span class="badge {res_cls}">{r.get('reserved','GEN')}</span></td>
          <td style="font-size:11px">{r['winner']}</td>
          <td>{party_badge(r['party_26'])}</td>
          <td>{party_badge(r['party_21'])}</td>
          <td class="num">{fmt_num(r['votes'])}</td>
          <td class="num" style="color:#c47d00;font-weight:600">{fmt_num(r['margin'])}</td>
          <td class="num">{r['t21']}%</td>
          <td class="num">{r['t26']}%</td>
          <td>{flip_span}</td>
        </tr>"""

    st.markdown(f"""
    <div class="tscroll">
      <table class="tbl">
        <thead><tr>
          <th>#</th><th>📍 Constituency</th><th>🏙️ District</th><th>🗺️ Region</th>
          <th>🏷️ Res</th><th>🏆 Winner 2026</th><th>🎯 2026</th><th>📅 2021</th>
          <th>🗳️ Votes</th><th>📊 Margin</th><th>📈 T%21</th><th>📈 T%26</th><th>🔄 Status</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: Q1 — TURNOUT TOP / BOTTOM
# ════════════════════════════════════════════
elif page == "q1":
    st.markdown('''<div class="pg-title">Q1 — Voter Turnout: Top 5 &amp; Bottom 5</div><div class="pg-desc">Constituency-level voter turnout % for 2021 and 2026 Assembly elections.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Key Pattern:</strong> In 2021, bottom-5 constituencies (all Chennai Metro, 55–56%) and top-5 (North/Kongu/Central, 85–87%) were separated by ~30pp.
        In 2026, the top-5 shifted to Kongu/Central with 91–94%, while the bottom-5 moved entirely to the <strong>South region</strong> (74–77%) — a dramatic regional reversal.
        The 2021 bottom-5 constituencies each surged by 25–31pp, the highest gains in the state.
    </div>""", unsafe_allow_html=True)

    def turnout_tbl(rows, vk, max_val, title):
        html = f'<div class="ct">{title}</div>'
        trows = ""
        for i, r in enumerate(rows):
            c = region_color(r["region"])
            w = r[vk] / max_val * 100
            trows += f"""<tr>
              <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{i+1}</td>
              <td style="font-size:12px">{r['constituency']}</td>
              <td>{region_badge(r['region'])}</td>
              <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r[vk]}%</td>
              <td style="width:100px"><div style="background:#e5e7eb;border-radius:2px;height:8px;overflow:hidden">
                <div style="width:{w:.1f}%;height:100%;background:{c};border-radius:2px"></div>
              </div></td>
            </tr>"""
        return html + f"""
        <table class="tbl">
          <thead><tr><th>#</th>
            <th>📍 Constituency</th>
            <th>🗺️ Region</th>
            <th>📈 Turnout</th>
            <th>📊 Bar</th>
          </tr></thead><tbody>{trows}</tbody>
        </table>"""

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">' + turnout_tbl(TURNOUT_TOP5_21, "turnout", 90, "🔼 Top 5 — 2021 Turnout") + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">' + turnout_tbl(TURNOUT_BOT5_21, "turnout", 90, "🔽 Bottom 5 — 2021 Turnout") + '</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">' + turnout_tbl(TURNOUT_TOP5_26, "turnout", 100, "🔼 Top 5 — 2026 Turnout") + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">' + turnout_tbl(TURNOUT_BOT5_26, "turnout", 100, "🔽 Bottom 5 — 2026 Turnout") + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="ct" style="margin-top:1rem">🚀 Top 10 Biggest Turnout Jumps 2021→2026</div>', unsafe_allow_html=True)
    surge10 = SURGE20[:10]
    rows = ""
    for i, r in enumerate(surge10):
        w = r["delta"] / 35 * 100
        rows += f"""<tr>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{i+1}</td>
          <td style="font-size:12px">{r['constituency']}</td>
          <td>{region_badge(r['region'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['t21']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['t26']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#16a34a;font-weight:600">+{r['delta']:.1f}pp</td>
          <td style="width:100px"><div style="background:#e5e7eb;border-radius:2px;height:8px;overflow:hidden">
            <div style="width:{w:.1f}%;height:100%;background:#16a34a;border-radius:2px"></div>
          </div></td>
        </tr>"""
    st.markdown(f"""<div class="card">
      <table class="tbl">
        <thead><tr><th>#</th>
          <th>📍 Constituency</th>
          <th>🗺️ Region</th>
          <th>📅 2021%</th>
          <th>📅 2026%</th>
          <th>🚀 Delta</th>
          <th>📊 Bar</th>
        </tr></thead><tbody>{rows}</tbody>
      </table></div></div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: Q2 — SAME PARTY STREAK
# ════════════════════════════════════════════
elif page == "q2":
    st.markdown('''<div class="pg-title">Q2 — Same Party Both Elections</div><div class="pg-desc">71 of 234 constituencies returned the same winning party in both 2021 and 2026. Ranked by 2026 winner vote %.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Key finding:</strong> Edapadi tops at 57.97% — AIADMK held despite statewide erosion. Every retained seat shows vote share compression of 5–28 points.
    </div>""", unsafe_allow_html=True)

    labels = [r["constituency"] for r in SAME_PARTY_TOP10]
    d21 = [r["vote_pct_21"] for r in SAME_PARTY_TOP10]
    d26 = [r["vote_pct_26"] for r in SAME_PARTY_TOP10]
    colors2 = [party_color(r["party"]) for r in SAME_PARTY_TOP10]
    fig = grouped_bar(labels, d21, d26, "2021%", "2026%", colors2=colors2, height=300)
    fig.update_layout(yaxis=dict(range=[30, 80]), title="📊 Vote % Comparison — 2021 vs 2026", title_font_size=11)
    st.plotly_chart(fig, use_container_width=True)

    rows = ""
    for i, r in enumerate(SAME_PARTY_TOP10):
        chg = r["vote_pct_26"] - r["vote_pct_21"]
        cls = "swing-pos" if chg >= 0 else "swing-neg"
        rows += f"""<tr>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{i+1}</td>
          <td style="font-size:12px">{r['constituency']}</td>
          <td>{party_badge(r['party'])}</td>
          <td>{region_badge(r['region'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['vote_pct_21']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['vote_pct_26']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px"><span class="{cls}">{"+" if chg>=0 else ""}{chg:.2f}pp</span></td>
        </tr>"""
    st.markdown(f"""<div class="card"><div class="ct">🔒 Top 10 Retained Seats — ranked by 2026 vote %</div>
      <table class="tbl">
        <thead><tr><th>#</th>
          <th>📍 Constituency</th>
          <th>🎯 Party</th>
          <th>🗺️ Region</th>
          <th>📅 2021%</th>
          <th>📅 2026%</th>
          <th>📊 Change</th>
        </tr></thead><tbody>{rows}</tbody>
      </table></div></div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: Q3 — BIGGEST FLIPS
# ════════════════════════════════════════════
elif page == "q3":
    st.markdown('''<div class="pg-title">Q3 — Top 10 Flipped Constituencies by Vote % Swing</div><div class="pg-desc">163 seats changed party. Ranked by absolute winner vote % difference between elections.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Key finding:</strong> Tirukkoyilur — DMK won 57.15% in 2021 but AIADMK won at only 33.68% in 2026, a 23.5pp collapse.
    </div>""", unsafe_allow_html=True)

    from collections import Counter
    reg_cnt = Counter(r["region"] for r in FLIPPED_TOP10)
    rl = list(reg_cnt.keys())
    rv = [reg_cnt[r] for r in rl]
    rc_colors = [region_color(r) for r in rl]

    rows = ""
    for i, r in enumerate(FLIPPED_TOP10):
        rows += f"""<tr>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{i+1}</td>
          <td style="font-size:12px">{r['constituency']}</td>
          <td>{party_badge(r['party_21'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['vote_pct_21']}%</td>
          <td>{party_badge(r['party_26'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['vote_pct_26']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#dc2626;font-weight:600">−{r['vote_pct_diff']}pp</td>
          <td>{region_badge(r['region'])}</td>
        </tr>"""
    st.markdown(f"""<div class="card">
      <table class="tbl">
        <thead><tr><th>#</th>
          <th>📍 Constituency</th>
          <th>📅 2021 Winner</th>
          <th>📊 2021%</th>
          <th>🏆 2026 Winner</th>
          <th>📊 2026%</th>
          <th>🔄 Swing</th>
          <th>🗺️ Region</th>
        </tr></thead><tbody>{rows}</tbody>
      </table></div></div>""", unsafe_allow_html=True)

    fig = go.Figure(go.Bar(x=rl, y=rv,
                           marker_color=[hex_to_rgba(c, 0.8) for c in rc_colors],
                           marker_line_color=rc_colors, marker_line_width=1))
    fig.update_layout(**PLOTLY_LAYOUT, height=240, showlegend=False,
                      title="🔄 Flips by Region (top 10)", title_font_size=11)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE: Q4 — MARGIN ANALYSIS
# ════════════════════════════════════════════
elif page == "q4":
    st.markdown('''<div class="pg-title">Q4 — Top 5 &amp; Bottom 5 Candidates by Winning Margin</div><div class="pg-desc">Winning margin = winner votes minus runner-up votes.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Incredible:</strong> Tiruppattur 2026 — TVK won by just 1 vote. In 2021, Theayagaraya Nagar had a 137-vote margin. Edapadi Palaniswami appears in both years' Top 5.
    </div>""", unsafe_allow_html=True)


    def margin_tbl(data, title):
        rows = ""
        for i, r in enumerate(data):
            rows += f"""<tr>
              <td class="num">{i+1}</td>
              <td style="white-space:nowrap">{r['constituency']}</td>
              <td style="font-size:11px;color:#6b7280">{r['candidate']}</td>
              <td>{party_badge(r['party'])}</td>
              <td class="num">{fmt_num(r['votes'])}</td>
              <td class="num">{fmt_num(r['runner_votes'])}</td>
              <td class="num" style="color:#c47d00;font-weight:700">{fmt_num(r['margin'])}</td>
              <td>{region_badge(r['region'])}</td>
            </tr>"""
        return f"""<div class="card" style="overflow-x:auto;margin-bottom:1rem">
          <div class="ct">{title}</div>
          <div class="tscroll" style="max-height:260px">
          <table class="tbl" style="min-width:500px">
            <thead><tr>
              <th>#</th><th>📍 Constituency</th><th>👤 Candidate</th><th>🎯 Party</th>
              <th>🗳️ Votes</th><th>🥈 Runner</th><th>📊 Margin</th><th>🗺️ Region</th>
            </tr></thead>
            <tbody>{rows}</tbody>
          </table></div></div>"""

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(margin_tbl(MARGIN_TOP5_21, "🏆 Top 5 Margins — 2021"), unsafe_allow_html=True)
        st.markdown(margin_tbl(MARGIN_BOT5_21, "⚔️ Bottom 5 Margins — 2021"), unsafe_allow_html=True)
    with col2:
        st.markdown(margin_tbl(MARGIN_TOP5_26, "🏆 Top 5 Margins — 2026"), unsafe_allow_html=True)
        st.markdown(margin_tbl(MARGIN_BOT5_26, "⚔️ Bottom 5 Margins — 2026"), unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: Q5 — REGIONAL VOTE SPLIT
# ════════════════════════════════════════════
elif page == "q5":
    st.markdown('''<div class="pg-title">Q5 — Party Vote Share by Region (2021 vs 2026)</div><div class="pg-desc">Vote share % per major party per region. TVK's 2021 share is "—" as the party did not exist.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Key finding:</strong> TVK's highest regional share was in Chennai Metro (46.86%), nearly double its next-best region. AIADMK's steepest loss was in Kongu (−15.65pp), its traditional belt. DMK held best in Delta and South.
    </div>""", unsafe_allow_html=True)

    sel_reg = st.radio("Select Region", REGIONS, horizontal=True, key="q5reg")
    rows_rs = [r for r in REGION_SHARE if r["region"] == sel_reg]
    maj_rs = sorted([r for r in rows_rs if r["y26"] > 1], key=lambda x: -x["y26"])

    st.markdown(f'<div class="insight"><strong>{sel_reg}:</strong> {REGINSIGHTS.get(sel_reg,"")}</div>', unsafe_allow_html=True)

    tbl_rows = ""
    for r in rows_rs:
        tbl_rows += f"""<tr>
          <td>{party_badge(r['pg'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{str(r['y21'])+'%' if r['y21'] is not None else '—'}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['y26']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">
            {'<span class="swing-pos">+'+str(r["swing"])+'pp</span>' if r["swing"] is not None and r["swing"]>=0 else ('<span class="swing-neg">'+str(r["swing"])+'pp</span>' if r["swing"] is not None else '<span style="color:#9ca3af">New</span>')}
          </td>
        </tr>"""
    st.markdown(f"""<div class="card"><div class="ct">📊 Vote Share Table</div>
      <table class="tbl">
        <thead><tr><th>🎯 Party</th>
          <th>📅 2021%</th>
          <th>📅 2026%</th>
          <th>📊 Swing</th>
        </tr></thead><tbody>{tbl_rows}</tbody>
      </table></div></div>""", unsafe_allow_html=True)

    ll = [r["pg"] for r in maj_rs]
    d21 = [r["y21"] if r["y21"] is not None else 0 for r in maj_rs]
    d26 = [r["y26"] for r in maj_rs]
    fig = grouped_bar(ll, d21, d26, "2021", "2026",
                      colors2=[party_color(p) for p in ll], height=300)
    fig.update_layout(title=f"Vote Share by Party — {sel_reg} (2021 vs 2026)", title_font_size=11)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE: Q6 — STATE VOTE SPLIT
# ════════════════════════════════════════════
elif page == "q6":
    st.markdown('''<div class="pg-title">Q6 — Party Vote Share at State Level (2021 vs 2026)</div><div class="pg-desc">Aggregate vote share across all 234 constituencies.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Where did TVK's 34.9% come from?</strong> DMK dropped 13.5pp and AIADMK 12.1pp — together 25.6pp of TVK's 34.9%. The remaining ~9pp came from NTK (−2.6), Others (−3.7), and the massive turnout surge.
    </div>""", unsafe_allow_html=True)

    tbl_rows = ""
    for r in STATE_SHARE:
        tbl_rows += f"""<tr>
          <td>{party_badge(r['pg'])}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{str(r['y21'])+'%' if r['y21'] is not None else '—'}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['y26']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">
            {'<span class="swing-pos">+'+str(r["swing"])+'pp</span>' if r["swing"] is not None and r["swing"]>=0 else ('<span class="swing-neg">'+str(r["swing"])+'pp</span>' if r["swing"] is not None else '<span style="color:#9ca3af">New</span>')}
          </td>
        </tr>"""
    st.markdown(f"""<div class="card"><div class="ct">📊 State-wide Vote Share Comparison</div>
      <table class="tbl">
        <thead><tr><th>🎯 Party</th>
          <th>📅 2021%</th>
          <th>📅 2026%</th>
          <th>📊 Swing</th>
        </tr></thead><tbody>{tbl_rows}</tbody>
      </table></div></div>""", unsafe_allow_html=True)

    sw = sorted([r for r in STATE_SHARE if r["swing"] is not None], key=lambda x: x["swing"])
    colors = ["rgba(22,163,74,.6)" if s["swing"] >= 0 else "rgba(220,38,38,.6)" for s in sw]
    bc = ["#16a34a" if s["swing"] >= 0 else "#dc2626" for s in sw]
    fig = go.Figure(go.Bar(
        y=[r["pg"] for r in sw], x=[r["swing"] for r in sw],
        orientation="h", marker_color=colors,
        marker_line_color=bc, marker_line_width=1,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                      title="📊 Vote Share Swing 2021→2026", title_font_size=11,
                      yaxis=dict(tickfont_size=11), xaxis_tickfont_size=9)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE: Q7 — NOTA ANALYSIS
# ════════════════════════════════════════════
elif page == "q7":
    st.markdown('''<div class="pg-title">Q7 — NOTA Voting Analysis</div><div class="pg-desc">NOTA fell statewide from 0.75% to 0.41% — consistent with TVK absorbing protest votes.</div>''', unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <strong>Key insight:</strong> NOTA peaked at 1.5% in 2021 (Chepauk-Thiruvallikeni) and 1.03% in 2026 (Udhagamandalam). TVK gave disenchanted voters a new option.
    </div>""", unsafe_allow_html=True)


    b8 = NOTA_TOP10_21[:8]
    m26 = []
    for r in b8:
        f = next((x for x in NOTA_TOP10_26 if x["constituency"] == r["constituency"]), None)
        m26.append(f["nota_pct_26"] if f else None)

    fig = go.Figure()
    fig.add_bar(name="NOTA% 2021", x=[r["constituency"] for r in b8], y=[r["nota_pct_21"] for r in b8],
                marker_color="rgba(156,163,175,.6)", marker_line_color="rgba(107,114,128,.8)", marker_line_width=1)
    fig.add_bar(name="NOTA% 2026", x=[r["constituency"] for r in b8], y=m26,
                marker_color="rgba(220,38,38,.5)", marker_line_color="#dc2626", marker_line_width=1)
    fig.update_layout(**PLOTLY_LAYOUT, barmode="group", height=280,
                      title="📋 NOTA % Comparison",
                      title_font_size=11,
                      xaxis_tickfont_size=9, legend=dict(font_size=10))
    st.plotly_chart(fig, use_container_width=True)

    def nota_tbl(rows, vk, pk, title):
        trows = ""
        for i, r in enumerate(rows):
            trows += f"""<tr>
              <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{i+1}</td>
              <td style="font-size:12px">{r['constituency']}</td>
              <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{fmt_num(r[vk])}</td>
              <td style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#c47d00;font-weight:600">{r[pk]}%</td>
              <td>{region_badge(r['region'])}</td>
            </tr>"""
        return f"""<div class="card"><div class="ct">{title}</div><div class="tscroll"><table class="tbl">
            <thead><tr><th>#</th>
              <th>📍 Constituency</th>
              <th>✗ NOTA Votes</th>
              <th>📊 NOTA%</th>
              <th>🗺️ Region</th>
            </tr></thead><tbody>{trows}</tbody>
          </table></div></div>"""

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(nota_tbl(NOTA_TOP10_21, "nota_21", "nota_pct_21", "📋 Top 10 NOTA % — 2021"), unsafe_allow_html=True)
    with c2:
        st.markdown(nota_tbl(NOTA_TOP10_26, "nota_26", "nota_pct_26", "📋 Top 10 NOTA % — 2026"), unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: Q8 — POSTAL CORRELATION
# ════════════════════════════════════════════
elif page == "q8":
    st.markdown('''<div class="pg-title">Q8 — Postal Votes % vs Voter Turnout % Correlation</div><div class="pg-desc">Pearson correlation between postal vote % and overall constituency turnout %.</div>''', unsafe_allow_html=True)

    q8_c1, q8_c2 = st.columns(2)
    with q8_c1:
        st.markdown("""<div class="card" style="text-align:center;padding:1.5rem"><div class="corr-big" style="color:#7c3aed">+0.171</div><div class="corr-lbl">Pearson r — 2021</div><div class="corr-txt">Weak positive. Rural/service constituencies with more postal votes had slightly higher turnout — not a strong signal.</div></div>""", unsafe_allow_html=True)
    with q8_c2:
        st.markdown("""<div class="card" style="text-align:center;padding:1.5rem"><div class="corr-big" style="color:#dc2626">−0.016</div><div class="corr-lbl">Pearson r — 2026</div><div class="corr-txt">Near-zero. The massive uniform turnout surge erased any prior relationship between postal votes and turnout.</div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight" style="margin-top:.75rem">
        <strong>Interpretation:</strong> Postal votes are 0.3–2.3% of totals. High turnout in 2026 was broadly distributed — not concentrated in high-postal-vote areas.
    </div>""", unsafe_allow_html=True)

    df = pd.DataFrame(POSTAL_DATA_26)
    fig = go.Figure()
    for reg in df["region"].unique():
        sub = df[df["region"] == reg]
        c = region_color(reg)
        fig.add_scatter(
            x=sub["postal_pct"], y=sub["t26"],
            mode="markers", name=reg,
            marker=dict(size=8, color=hex_to_rgba(c, 0.73), line=dict(color=c, width=1)),
            text=sub["constituency"],
            hovertemplate="<b>%{text}</b><br>Postal: %{x}%<br>Turnout: %{y}%<extra></extra>"
        )
    fig.update_layout(
        **PLOTLY_LAYOUT, height=420,
        title="📬 Scatter: Postal % vs Turnout % — 2026", title_font_size=11,
        xaxis=dict(title="Postal Votes %", tickfont_size=10),
        yaxis=dict(title="Turnout %", tickfont_size=10),
        legend=dict(font_size=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
# PAGE: Q9 — LITERACY CORRELATION
# ════════════════════════════════════════════
elif page == "q9":
    st.markdown('''<div class="pg-title">Q9 — District Literacy % vs Voter Turnout % Correlation</div><div class="pg-desc">Census 2011 district literacy rates vs average constituency turnout per district.</div>''', unsafe_allow_html=True)

    q9_c1, q9_c2 = st.columns(2)
    with q9_c1:
        st.markdown("""<div class="card" style="text-align:center;padding:1.5rem"><div class="corr-big" style="color:#dc2626">−0.720</div><div class="corr-lbl">Pearson r — Literacy vs 2021 Turnout</div><div class="corr-txt">Strong negative. Higher-literacy districts (Chennai, Coimbatore) had significantly lower turnout in 2021 — urban apathy was real.</div></div>""", unsafe_allow_html=True)
    with q9_c2:
        st.markdown("""<div class="card" style="text-align:center;padding:1.5rem"><div class="corr-big" style="color:#d97706">−0.457</div><div class="corr-lbl">Pearson r — Literacy vs 2026 Turnout</div><div class="corr-txt">Moderate negative — weakened as urban constituencies surged. Chennai went from 59% to 84% avg turnout, closing the gap.</div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight" style="margin-top:.75rem">
        <strong>Urbanisation paradox:</strong> In 2021 the most literate districts voted least (r=−0.72). In 2026 urban areas saw the biggest surges (+26–30pp in Chennai Metro), weakening the correlation to −0.46.
    </div>""", unsafe_allow_html=True)

    ld = sorted(LIT_DATA, key=lambda x: x["literacy_pct"])
    fig = go.Figure()
    fig.add_scatter(
        x=[r["literacy_pct"] for r in ld], y=[r["avg_t21"] for r in ld],
        mode="markers", name="2021 Turnout",
        marker=dict(size=8, color="rgba(37,99,235,.6)", line=dict(color="#2563eb", width=1)),
        text=[r["district"] for r in ld],
        hovertemplate="<b>%{text}</b><br>Literacy: %{x}%<br>2021 Turnout: %{y:.1f}%<extra></extra>"
    )
    fig.add_scatter(
        x=[r["literacy_pct"] for r in ld], y=[r["avg_t26"] for r in ld],
        mode="markers", name="2026 Turnout",
        marker=dict(size=8, color="rgba(124,58,237,.6)", line=dict(color="#7c3aed", width=1)),
        text=[r["district"] for r in ld],
        hovertemplate="<b>%{text}</b><br>Literacy: %{x}%<br>2026 Turnout: %{y:.1f}%<extra></extra>"
    )
    fig.update_layout(
        **PLOTLY_LAYOUT, height=420,
        title="📚 District Literacy % vs Avg Turnout % — 2021 & 2026", title_font_size=11,
        xaxis=dict(title="Literacy % (Census 2011)", range=[60, 95], tickfont_size=10),
        yaxis=dict(title="Avg Turnout %", range=[55, 100], tickfont_size=10),
        legend=dict(font_size=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    lt = sorted(LIT_DATA, key=lambda x: -x["avg_t26"])
    rows = ""
    for r in lt:
        chg = r["avg_t26"] - r["avg_t21"]
        rows += f"""<tr>
          <td style="font-size:12px">{r['district']}</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['literacy_pct']}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['avg_t21']:.1f}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px">{r['avg_t26']:.1f}%</td>
          <td style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#16a34a;font-weight:600">+{chg:.1f}pp</td>
        </tr>"""
    st.markdown(f"""<div class="card">
      <div class="ct">📚 District Data Table</div>
      <div style="max-height:380px;overflow-y:auto">
      <table class="tbl">
        <thead style="position:sticky;top:0;background:#fff;z-index:1">
          <tr><th>🏙️ District</th>
            <th>📚 Literacy%</th>
            <th>📅 Avg T% 2021</th>
            <th>📅 Avg T% 2026</th>
            <th>📈 Change</th>
          </tr></thead><tbody>{rows}</tbody>
      </table></div></div></div>""", unsafe_allow_html=True)
