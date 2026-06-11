import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== TIMEZONE ==========
NAIROBI_TZ = pytz.timezone('Africa/Nairobi')

# ========== CSS ==========
st.markdown("""
<style>
    .stApp {
        background: #0a0a0a;
    }
    
    .main > div {
        padding: 0 1rem;
    }
    
    .gold-header {
        font-size: 2rem;
        font-weight: bold;
        color: #FFD700;
        margin-bottom: 0;
        margin-top: -10px;
    }
    
    .gold-subheader {
        font-size: 0.9rem;
        color: #B8860B;
        margin-bottom: 1.5rem;
    }
    
    .module-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FFD700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #FFD700;
        padding-left: 10px;
    }
    
    .match-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid #FFD70030;
    }
    
    .match-title {
        font-size: 2rem;
        font-weight: bold;
        color: #FFD700;
    }
    
    .match-venue {
        font-size: 0.9rem;
        color: #888;
    }
    
    .match-time {
        font-size: 1.2rem;
        color: #FFD700;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #FFD700;
        margin: 20px 0 15px 0;
        border-left: 4px solid #FFD700;
        padding-left: 12px;
    }
    
    .stat-card {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #333;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FFD700;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #888;
    }
    
    .prob-bar-container {
        background: #333;
        border-radius: 10px;
        height: 30px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .prob-bar-home {
        background: #00FF88;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0a0a0a;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .prob-bar-draw {
        background: #FFA500;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0a0a0a;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .prob-bar-away {
        background: #FF4444;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .odds-button {
        background: #1a1a1a;
        border: 1px solid #FFD700;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .odds-value {
        font-size: 1.3rem;
        font-weight: bold;
        color: #FFD700;
    }
    
    hr {
        margin: 20px 0;
        border-color: #333;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1a1a1a;
        border-radius: 8px;
        padding: 8px 16px;
        color: #888;
    }
    
    .stTabs [aria-selected="true"] {
        background: #FFD700;
        color: #0a0a0a;
    }
    
    .stMetric {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 10px;
    }
    
    .dashboard-card {
        background: #1a1a1a;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #FFD70030;
        transition: all 0.3s;
    }
    
    .dashboard-card:hover {
        border-color: #FFD700;
        transform: translateY(-2px);
    }
    
    .verdict-pass { color: #00FF88; font-weight: bold; }
    .verdict-fail { color: #FF4444; font-weight: bold; }
    .verdict-warn { color: #FFA500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ========== LIVE CLOCK ==========
st.markdown("""
<div id="live-clock" style="position: fixed; top: 8px; right: 20px; color: #FFD700; font-family: monospace; font-size: 0.7rem; z-index: 999;"></div>
<script>
function updateClock() {
    const now = new Date();
    const options = { timeZone: 'Africa/Nairobi', hour12: false };
    const timeStr = now.toLocaleTimeString('en-US', options);
    document.getElementById('live-clock').innerHTML = timeStr + ' GMT+3';
}
setInterval(updateClock, 1000);
updateClock();
</script>
""", unsafe_allow_html=True)

# ========== FORENSIC DATA ==========
FORENSIC_DATA = {
    "match_id": 1,
    "home": "Derry City",
    "away": "Bohemians FC",
    "league": "Ireland Premier League",
    "venue": "Brandywell Stadium",
    "date": "June 12, 2026",
    "home_odds": 2.90,
    "draw_odds": 3.20,
    "away_odds": 2.36,
    "final_verdict": "REJECTED (H2H CONFLICT)",
    "final_stake": 0.00,
    "final_reason": "H2H conflict between historical dominance (Derry) and current form (Bohemians)",
    
    "m0_checks": [
        {"check": "Fixture Status", "value": "NS (upcoming)", "result": "PASS"},
        {"check": "Odds present", "value": "2.90/3.20/2.36", "result": "PASS"},
        {"check": "Odds bounds", "value": "All >1.01, <100", "result": "PASS"},
    ],
    "m0_hard_filters": [
        {"filter": "Senior Men's League", "result": "PASS"},
        {"filter": "League Tier", "result": "PASS (Ireland Tier 1)"},
        {"filter": "Maturity (≥10 games)", "result": "PASS (20 games each)"},
    ],
    
    "m1_home_metrics": {
        "games": 20, "wins": 4, "draws": 10, "losses": 6,
        "goals_for": 22, "goals_against": 23,
        "home_record": "3-5-2", "home_wr": 30,
        "recent_form": "L, D, D, D, L, L",
        "ppg": 1.10, "clean_sheets": 5
    },
    "m1_away_metrics": {
        "games": 20, "wins": 9, "draws": 7, "losses": 4,
        "goals_for": 31, "goals_against": 21,
        "away_record": "6-2-2", "away_wr": 60,
        "recent_form": "W, L, W, D, W, W",
        "ppg": 1.70, "clean_sheets": 7
    },
    "m1_h2h": {
        "all_time": "Derry 46% (37), Draw 30% (24), Bohemians 24% (19)",
        "last_10": "Derry 4, Draw 3, Bohemians 3",
        "last_6": "Derry 2, Draw 3, Bohemians 1",
        "insight": "Derry City has HISTORICAL dominance but recent H2H is balanced"
    },
    
    "m3_odds_analysis": {
        "home_odds": 2.90, "home_implied": 34.5, "home_model": 30,
        "draw_odds": 3.20, "draw_implied": 31.3, "draw_model": 30,
        "away_odds": 2.36, "away_implied": 42.4, "away_model": 40,
        "margin": 8.2, "edge": -2.4
    },
    
    "m4_checks": [
        {"check": "C1: Season Win Gap", "passed": True, "value": "+5 wins", "points": 10},
        {"check": "C2: Venue Win Gap", "passed": True, "value": "+30%", "points": 10},
        {"check": "C3: H2H Favoured", "passed": False, "value": "24%", "points": 0},
        {"check": "C4: Transition Favours", "passed": True, "value": "~50%", "points": 8},
    ],
    "m4_passed": 7, "m4_total": 8,
    
    "m5_failures": [
        {"name": "Low Season Win Count (Derry)", "points": 0.5},
        {"name": "Low Home Wins at Venue (Derry)", "points": 1.0},
    ],
    "m5_total": 2.5, "m5_threshold": 4.5,
    
    "m6_injuries": [
        {"team": "Derry City", "player": "P. McClean", "position": "D", "status": "OUT"},
        {"team": "Bohemians FC", "player": "B. Maher", "position": "G", "status": "OUT"},
    ],
    "m6_scores": {"Derry City": 55, "Bohemians FC": 45},
    
    "m7_ai": [
        {"provider": "DeepSeek", "verdict": "CAUTION", "reasoning": "Form strong but H2H favours Derry"},
        {"provider": "Claude", "verdict": "CAUTION", "reasoning": "Missing GK is concern"},
        {"provider": "Gemini", "verdict": "APPROVE", "reasoning": "League position dominant"},
        {"provider": "GPT", "verdict": "REJECT", "reasoning": "H2H conflict"},
    ],
    "m7_consensus": "CAUTION", "m7_agreement": 25,
    
    "m8_h2h_all_time": {"derry": 46, "bohemians": 24},
    "m8_h2h_last6": {"derry": 33, "bohemians": 17},
    "m8_current_season": {"derry": 20, "bohemians": 45},
    "m8_severity": "HIGH",
    "m8_verdict": "HARD REJECT",
    
    "m9_underdog_edge": -5,
    "m9_threat_level": "LOW",
    
    "m10_bilateral": {"home": 28, "draw": 32, "away": 40},
    "m10_confidence": "LOW",
}

# ========== LEAGUE DATA ==========
LEAGUE_DATA = {
    "home": "Shabab (KUW)",
    "away": "Jahra FC",
    "league": "Kuwait Premier League",
    "venue": "Al Ramadi Stadium",
    "date": "11/06/2026",
    "time": "20:45",
    "temperature": "42°",
    "home_odds": 1.95,
    "draw_odds": 3.40,
    "away_odds": 3.80,
    "home_win_prob": 42,
    "draw_prob": 28,
    "away_win_prob": 30,
    "prediction": "2",
    "correct_score": "2-1",
    
    "standings": [
        {"pos": 1, "team": "Kuwait SC", "pts": 43, "gp": 17, "w": 13, "d": 4, "l": 0, "gf": 46, "ga": 10, "gd": 36},
        {"pos": 2, "team": "Qadisiya Kuwait", "pts": 31, "gp": 17, "w": 9, "d": 4, "l": 4, "gf": 32, "ga": 14, "gd": 18},
        {"pos": 3, "team": "Al Arabi Kuwait", "pts": 29, "gp": 17, "w": 8, "d": 5, "l": 4, "gf": 28, "ga": 13, "gd": 15},
        {"pos": 4, "team": "Salmiya SC", "pts": 29, "gp": 17, "w": 8, "d": 5, "l": 4, "gf": 21, "ga": 12, "gd": 9},
        {"pos": 5, "team": "Kazma SC", "pts": 27, "gp": 17, "w": 7, "d": 6, "l": 4, "gf": 20, "ga": 16, "gd": 4},
        {"pos": 6, "team": "Fahaheel SC", "pts": 21, "gp": 17, "w": 6, "d": 3, "l": 8, "gf": 21, "ga": 35, "gd": -14},
        {"pos": 7, "team": "Al Nasr (KUW)", "pts": 16, "gp": 17, "w": 4, "d": 4, "l": 9, "gf": 16, "ga": 22, "gd": -6},
        {"pos": 8, "team": "Tadamon (KUW)", "pts": 15, "gp": 17, "w": 4, "d": 3, "l": 10, "gf": 15, "ga": 28, "gd": -13},
        {"pos": 9, "team": "Shabab (KUW)", "pts": 15, "gp": 17, "w": 3, "d": 6, "l": 8, "gf": 11, "ga": 33, "gd": -22},
        {"pos": 10, "team": "Jahra FC", "pts": 8, "gp": 17, "w": 2, "d": 2, "l": 13, "gf": 11, "ga": 38, "gd": -27},
    ],
    
    "home_last_6": [
        {"date": "29/05/2026", "opponent": "Tadamon (KUW)", "score": "0-2", "result": "L"},
        {"date": "23/05/2026", "opponent": "Salmiya SC", "score": "0-3", "result": "L", "away": True},
        {"date": "15/05/2026", "opponent": "Kazma SC", "score": "0-2", "result": "L"},
        {"date": "22/02/2026", "opponent": "Kuwait SC", "score": "1-5", "result": "L", "away": True},
        {"date": "12/02/2026", "opponent": "Fahaheel SC", "score": "2-3", "result": "L", "away": True},
        {"date": "05/02/2026", "opponent": "Fahaheel SC", "score": "1-1", "result": "D"},
    ],
    
    "away_last_6": [
        {"date": "29/05/2026", "opponent": "Qadisiya Kuwait", "score": "0-3", "result": "L", "away": True},
        {"date": "25/05/2026", "opponent": "Al Arabi Kuwait", "score": "1-1", "result": "D"},
        {"date": "14/05/2026", "opponent": "Al Nasr (KUW)", "score": "0-2", "result": "L"},
        {"date": "24/02/2026", "opponent": "Tadamon (KUW)", "score": "1-4", "result": "L", "away": True},
        {"date": "13/02/2026", "opponent": "Tadamon (KUW)", "score": "0-0", "result": "D", "away": True},
        {"date": "07/02/2026", "opponent": "Salmiya SC", "score": "0-1", "result": "L"},
    ],
    
    "home_matches": [
        {"date": "29/05/2026", "opponent": "Tadamon (KUW)", "score": "0-2"},
        {"date": "15/05/2026", "opponent": "Kazma SC", "score": "0-2"},
        {"date": "05/02/2026", "opponent": "Fahaheel SC", "score": "1-1"},
        {"date": "07/01/2026", "opponent": "Qadisiya Kuwait", "score": "0-2"},
        {"date": "02/01/2026", "opponent": "Al Arabi Kuwait", "score": "0-5"},
    ],
    
    "home_stats": {"wins": 1, "draws": 3, "losses": 5, "win_pct": 11, "draw_pct": 33, "loss_pct": 56},
    
    "away_matches": [
        {"date": "29/05/2026", "opponent": "Qadisiya Kuwait", "score": "0-3"},
        {"date": "24/02/2026", "opponent": "Tadamon (KUW)", "score": "1-4"},
        {"date": "13/02/2026", "opponent": "Tadamon (KUW)", "score": "0-0"},
        {"date": "25/01/2026", "opponent": "Kazma SC", "score": "1-2"},
        {"date": "14/01/2026", "opponent": "Kuwait SC", "score": "0-2"},
    ],
    
    "away_stats": {"wins": 1, "draws": 1, "losses": 9, "win_pct": 9, "draw_pct": 9, "loss_pct": 82},
    
    "h2h": [
        {"date": "19/12/2025", "home": "Jahra FC", "away": "Shabab (KUW)", "score": "1-2"},
        {"date": "03/05/2025", "home": "Shabab (KUW)", "away": "Jahra FC", "score": "3-0"},
        {"date": "28/03/2025", "home": "Jahra FC", "away": "Shabab (KUW)", "score": "2-1"},
        {"date": "03/02/2025", "home": "Shabab (KUW)", "away": "Jahra FC", "score": "2-0"},
        {"date": "05/01/2025", "home": "Jahra FC", "away": "Shabab (KUW)", "score": "2-1"},
    ]
}

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

# ========== SIDEBAR NAVIGATION ==========
with st.sidebar:
    st.markdown("## 🎯 Match Oracle")
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True):
        navigate_to("dashboard")
    
    if st.button("🔬 Forensic Report", use_container_width=True):
        navigate_to("forensic_report")
    
    if st.button("📋 League Analysis", use_container_width=True):
        navigate_to("league_analysis")
    
    if st.button("📈 Performance", use_container_width=True):
        navigate_to("performance")
    
    if st.button("⚙️ Settings", use_container_width=True):
        navigate_to("settings")
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown("✅ AI Engine: Active")
    st.markdown("✅ Data Feed: Connected")
    st.markdown(f"🕐 {datetime.now(NAIROBI_TZ).strftime('%H:%M:%S')} GMT+3")
    st.markdown("---")
    st.markdown("**Version:** 2.0.0")

# ========== DASHBOARD PAGE (CLEAN & MINIMAL) ==========
def show_dashboard():
    d = FORENSIC_DATA
    
    st.markdown('<p class="gold-header">🎯 Match Oracle Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">Forensic Betting Intelligence | AI-Powered Match Analysis</p>', unsafe_allow_html=True)
    
    # Featured Match Card
    st.markdown("### 🔥 Featured Match")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f"### 🏠 {d['home']}")
        st.metric("League Position", "8th", delta="-2")
        st.metric("PPG", d['m1_home_metrics']['ppg'])
        st.metric("Recent Form", d['m1_home_metrics']['recent_form'])
        st.metric("Odds", d['home_odds'])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### VS")
        st.markdown("---")
        st.markdown(f"**Draw Odds:** {d['draw_odds']}")
        st.markdown("---")
        st.error(f"**Verdict:** {d['final_verdict']}")
    
    with col3:
        st.markdown(f"### ✈️ {d['away']}")
        st.metric("League Position", "2nd", delta="+5")
        st.metric("PPG", d['m1_away_metrics']['ppg'])
        st.metric("Recent Form", d['m1_away_metrics']['recent_form'])
        st.metric("Odds", d['away_odds'])
    
    st.divider()
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("H2H All Time", "Derry 46%", delta="Historical Edge")
    with col2:
        st.metric("AI Consensus", d['m7_consensus'], delta=f"{d['m7_agreement']}% agreement")
    with col3:
        st.metric("Module Status", f"{d['m4_passed']}/8 Passed")
    with col4:
        st.metric("Conflict Severity", d['m8_severity'])
    
    st.divider()
    
    # Quick Navigation Cards
    st.markdown("### Quick Navigation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="dashboard-card">
                <h3>🔬 Forensic Report</h3>
                <p>10-module verification system including:</p>
                <ul style="text-align: left;">
                    <li>Data Integrity (M0)</li>
                    <li>Probability Engine (M3)</li>
                    <li>Asymmetric Pre-filter (M4)</li>
                    <li>Quad-AI Intelligence (M7)</li>
                    <li>Dual Pattern Engine (M8)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Forensic Report →", key="forensic_btn", use_container_width=True):
                navigate_to("forensic_report")
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="dashboard-card">
                <h3>📋 League Analysis</h3>
                <p>Comprehensive match statistics including:</p>
                <ul style="text-align: left;">
                    <li>League Standings</li>
                    <li>Last 6 Matches</li>
                    <li>Home/Away Splits</li>
                    <li>Head-to-Head History</li>
                    <li>Win Probabilities</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View League Analysis →", key="league_btn", use_container_width=True):
                navigate_to("league_analysis")

# ========== FORENSIC REPORT PAGE ==========
def show_forensic_report():
    d = FORENSIC_DATA
    
    st.markdown(f'<p class="gold-header">🔬 Forensic Report: {d["home"]} vs {d["away"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="gold-subheader">{d["league"]} | {d["venue"]} | {d["date"]} | Odds: H {d["home_odds"]} | D {d["draw_odds"]} | A {d["away_odds"]}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    # Module 0
    st.markdown('<p class="module-header">MODULE 0: GUARDRAIL & DATA INTEGRITY</p>', unsafe_allow_html=True)
    for check in d["m0_checks"]:
        st.markdown(f"✅ {check['check']}: {check['value']}")
    for f in d["m0_hard_filters"]:
        st.markdown(f"✅ {f['filter']}: {f['result']}")
    st.success("**M0 Verdict:** ✅ PASS")
    st.divider()
    
    # Module 1
    st.markdown('<p class="module-header">MODULE 1: DATA INGESTION</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{d['home']}**")
        st.markdown(f"Games: {d['m1_home_metrics']['games']} | W-D-L: {d['m1_home_metrics']['wins']}-{d['m1_home_metrics']['draws']}-{d['m1_home_metrics']['losses']}")
        st.markdown(f"Goals: {d['m1_home_metrics']['goals_for']}/{d['m1_home_metrics']['goals_against']}")
        st.markdown(f"PPG: {d['m1_home_metrics']['ppg']}")
    with col2:
        st.markdown(f"**{d['away']}**")
        st.markdown(f"Games: {d['m1_away_metrics']['games']} | W-D-L: {d['m1_away_metrics']['wins']}-{d['m1_away_metrics']['draws']}-{d['m1_away_metrics']['losses']}")
        st.markdown(f"Goals: {d['m1_away_metrics']['goals_for']}/{d['m1_away_metrics']['goals_against']}")
        st.markdown(f"PPG: {d['m1_away_metrics']['ppg']}")
    st.markdown(f"**H2H:** {d['m1_h2h']['insight']}")
    st.success("**M1 Verdict:** ✅ PASS")
    st.divider()
    
    # Module 3
    st.markdown('<p class="module-header">MODULE 3: PROBABILITY ENGINE</p>', unsafe_allow_html=True)
    mo = d["m3_odds_analysis"]
    st.markdown(f"Home: {mo['home_odds']} (Implied {mo['home_implied']}% | Model {mo['home_model']}%)")
    st.markdown(f"Draw: {mo['draw_odds']} (Implied {mo['draw_implied']}% | Model {mo['draw_model']}%)")
    st.markdown(f"Away: {mo['away_odds']} (Implied {mo['away_implied']}% | Model {mo['away_model']}%)")
    st.warning(f"**Edge: {mo['edge']:+}% (NEGATIVE)**")
    st.divider()
    
    # Module 4
    st.markdown('<p class="module-header">MODULE 4: ASYMMETRIC PRE-FILTER</p>', unsafe_allow_html=True)
    for c in d["m4_checks"]:
        status = "✅" if c["passed"] else "❌"
        st.markdown(f"{status} {c['check']}: {c['value']} (+{c['points']} pts)")
    st.success(f"**Passed:** {d['m4_passed']}/{d['m4_total']} → ✅ PASS")
    st.divider()
    
    # Module 5
    st.markdown('<p class="module-header">MODULE 5: FORENSIC CHECKS</p>', unsafe_allow_html=True)
    for f in d["m5_failures"]:
        st.markdown(f"⚠️ {f['name']}: +{f['points']} pts")
    st.success(f"**TOTAL:** {d['m5_total']} / {d['m5_threshold']} → ✅ PASS")
    st.divider()
    
    # Module 6
    st.markdown('<p class="module-header">MODULE 6: PERSONNEL FORENSICS</p>', unsafe_allow_html=True)
    for inj in d["m6_injuries"]:
        st.markdown(f"⚠️ {inj['team']}: {inj['player']} ({inj['position']}) - {inj['status']}")
    st.markdown(f"**Personnel Scores:** {d['home']}: {d['m6_scores']['Derry City']}/100 | {d['away']}: {d['m6_scores']['Bohemians FC']}/100")
    st.divider()
    
    # Module 7
    st.markdown('<p class="module-header">MODULE 7: QUAD-AI INTELLIGENCE</p>', unsafe_allow_html=True)
    for ai in d["m7_ai"]:
        st.markdown(f"**{ai['provider']}:** {ai['verdict']} - {ai['reasoning']}")
    st.info(f"**Consensus:** {d['m7_consensus']} (Agreement: {d['m7_agreement']}%)")
    st.divider()
    
    # Module 8
    st.markdown('<p class="module-header">MODULE 8: DUAL PATTERN ENGINE</p>', unsafe_allow_html=True)
    st.markdown(f"H2H all-time: {d['home']} DOMINANT ({d['m8_h2h_all_time']['derry']}% vs {d['m8_h2h_all_time']['bohemians']}%)")
    st.markdown(f"Current season: {d['away']} DOMINANT ({d['m8_current_season']['bohemians']}% vs {d['m8_current_season']['derry']}%)")
    st.error(f"**Conflict severity:** {d['m8_severity']}")
    st.error(f"**M8 Verdict:** 🚨 {d['m8_verdict']}")
    st.divider()
    
    # Module 9
    st.markdown('<p class="module-header">MODULE 9: UNDERDOG SCANNER</p>', unsafe_allow_html=True)
    st.markdown(f"Underdog Edge: {d['m9_underdog_edge']:+}%")
    st.markdown(f"Threat Level: {d['m9_threat_level']}")
    st.divider()
    
    # Module 10
    st.markdown('<p class="module-header">MODULE 10: SEASON TALLY MATRIX</p>', unsafe_allow_html=True)
    st.markdown(f"Home Win: {d['m10_bilateral']['home']}% | Draw: {d['m10_bilateral']['draw']}% | Away: {d['m10_bilateral']['away']}%")
    st.info(f"**Confidence:** {d['m10_confidence']}")
    st.divider()
    
    # Final Verdict
    st.markdown('<p class="module-header">FINAL VERDICT</p>', unsafe_allow_html=True)
    st.error(f"**Verdict:** {d['final_verdict']}")
    st.warning(f"**Recommended Stake:** €{d['final_stake']}")
    st.info(f"**Reasoning:** {d['final_reason']}")

# ========== LEAGUE ANALYSIS PAGE ==========
def show_league_analysis():
    d = LEAGUE_DATA
    
    st.markdown(f"""
    <div class="match-header">
        <div class="match-title">{d['home']} VS {d['away']}</div>
        <div class="match-venue">{d['venue']} {d['temperature']}</div>
        <div class="match-time">{d['date']} {d['time']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown(f'<div class="section-header">Win Probability</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="prob-bar-container">
            <div class="prob-bar-home" style="width: {d['home_win_prob']}%">{d['home']} {d['home_win_prob']}%</div>
        </div>
        <div class="prob-bar-container">
            <div class="prob-bar-draw" style="width: {d['draw_prob']}%">Draw {d['draw_prob']}%</div>
        </div>
        <div class="prob-bar-container">
            <div class="prob-bar-away" style="width: {d['away_win_prob']}%">{d['away']} {d['away_win_prob']}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Prediction</div>
            <div class="stat-value">{d['prediction']}</div>
            <div class="stat-label">Correct Score: {d['correct_score']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Standings", "Last 6", "Home/Away", "H2H", "Match Intro"])
        
        with tab1:
            standings_df = pd.DataFrame(d['standings'])
            st.dataframe(standings_df, use_container_width=True, hide_index=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {d['home']}")
                for match in d['home_last_6']:
                    away_indicator = "✈️ " if match.get('away') else "🏠 "
                    st.markdown(f"{match['date']} | {away_indicator}{match['opponent']} | {match['score']}")
            with col2:
                st.markdown(f"### {d['away']}")
                for match in d['away_last_6']:
                    away_indicator = "✈️ " if match.get('away') else "🏠 "
                    st.markdown(f"{match['date']} | {away_indicator}{match['opponent']} | {match['score']}")
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {d['home']} - HOME")
                st.markdown(f"W {d['home_stats']['win_pct']}% | D {d['home_stats']['draw_pct']}% | L {d['home_stats']['loss_pct']}%")
                for match in d['home_matches']:
                    st.markdown(f"{match['date']} | {match['opponent']} | {match['score']}")
            with col2:
                st.markdown(f"### {d['away']} - AWAY")
                st.markdown(f"W {d['away_stats']['win_pct']}% | D {d['away_stats']['draw_pct']}% | L {d['away_stats']['loss_pct']}%")
                for match in d['away_matches']:
                    st.markdown(f"{match['date']} | {match['opponent']} | {match['score']}")
        
        with tab4:
            for match in d['h2h']:
                st.markdown(f"{match['date']} | {match['home']} vs {match['away']} | {match['score']}")
        
        with tab5:
            st.markdown(f"""
            **{d['home']}** and **{d['away']}** face off in the {d['league']} at {d['venue']} on {d['date']}.
            
            {d['home']} holds 9th place with 15 points, while {d['away']} sits in 10th with 8 points.
            
            Recent form: {d['home']} has lost 67% of home matches, {d['away']} has lost 82% of away matches.
            
            **Prediction:** {d['home']} to win {d['correct_score']}.
            """)
    
    with col_right:
        st.markdown("### 1x2")
        st.markdown(f"""
        <div class="odds-button">
            <div class="stat-label">🏠 {d['home']}</div>
            <div class="odds-value">{d['home_odds']}</div>
        </div>
        <br>
        <div class="odds-button">
            <div class="stat-label">🤝 Draw</div>
            <div class="odds-value">{d['draw_odds']}</div>
        </div>
        <br>
        <div class="odds-button">
            <div class="stat-label">✈️ {d['away']}</div>
            <div class="odds-value">{d['away_odds']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### Match Info")
        st.markdown(f"**Round 18, Regular Season**")
        st.markdown(f"**League:** {d['league']}")
        st.markdown(f"**Venue:** {d['venue']}")

# ========== PERFORMANCE PAGE ==========
def show_performance():
    st.markdown('<p class="gold-header">📈 Performance Analytics</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bets", "0")
    with col2:
        st.metric("Win Rate", "0%")
    with col3:
        st.metric("ROI", "0%")
    with col4:
        st.metric("Profit/Loss", "€0")
    
    perf_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Bets': [0, 0, 0, 0, 0, 0],
        'Wins': [0, 0, 0, 0, 0, 0]
    })
    
    fig = px.line(perf_data, x='Month', y=['Bets', 'Wins'], title='Monthly Activity')
    st.plotly_chart(fig, use_container_width=True)

# ========== SETTINGS PAGE ==========
def show_settings():
    st.markdown('<p class="gold-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### AI Settings")
    ai_threshold = st.slider("AI Consensus Threshold", 0, 100, 60)
    st.checkbox("Enable DeepSeek", True)
    st.checkbox("Enable Claude", True)
    st.checkbox("Enable Gemini", True)
    st.checkbox("Enable GPT", True)
    
    st.divider()
    
    st.markdown("### Stake Management")
    st.number_input("Base Stake (€)", 0.0, 1000.0, 10.0)
    st.number_input("Max Stake (€)", 0.0, 10000.0, 100.0)
    
    if st.button("Save Settings"):
        st.success("Settings saved!")

# ========== MAIN ROUTING ==========
if st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "forensic_report":
    show_forensic_report()
elif st.session_state.page == "league_analysis":
    show_league_analysis()
elif st.session_state.page == "performance":
    show_performance()
elif st.session_state.page == "settings":
    show_settings()
