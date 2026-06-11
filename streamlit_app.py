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
    
    /* Match card styling */
    .match-card {
        background: #1a1a1a;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border: 1px solid #333;
        transition: all 0.3s;
    }
    
    .match-card:hover {
        border-color: #FFD700;
        transform: translateX(5px);
    }
    
    .match-teams {
        font-size: 1.1rem;
        font-weight: bold;
        color: #FFD700;
        margin-bottom: 5px;
    }
    
    .match-meta {
        font-size: 0.7rem;
        color: #888;
        margin-bottom: 10px;
    }
    
    .odds-row {
        display: flex;
        gap: 15px;
        margin: 10px 0;
    }
    
    .odds-item {
        background: #0a0a0a;
        border-radius: 8px;
        padding: 5px 12px;
        text-align: center;
        border: 1px solid #333;
    }
    
    .odds-label {
        font-size: 0.6rem;
        color: #888;
    }
    
    .odds-value {
        font-size: 1rem;
        font-weight: bold;
        color: #FFD700;
    }
    
    .verdict-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    
    .verdict-approved {
        background: #00FF8820;
        color: #00FF88;
        border: 1px solid #00FF88;
    }
    
    .verdict-rejected {
        background: #FF444420;
        color: #FF4444;
        border: 1px solid #FF4444;
    }
    
    .verdict-caution {
        background: #FFA50020;
        color: #FFA500;
        border: 1px solid #FFA500;
    }
    
    .confidence-bar {
        background: #333;
        border-radius: 10px;
        height: 4px;
        margin-top: 8px;
        overflow: hidden;
    }
    
    .confidence-fill {
        background: #FFD700;
        height: 100%;
        border-radius: 10px;
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
    }
    
    .odds-value-large {
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

# ========== MATCHES DATA ==========
MATCHES = [
    {
        "id": 1,
        "home": "Manchester City",
        "away": "Bournemouth",
        "date": "2026-06-11",
        "venue": "Etihad Stadium",
        "home_odds": 2.15,
        "draw_odds": 4.30,
        "away_odds": 7.52,
        "verdict": "REJECTED",
        "confidence": 46.5,
        "home_win_prob": 46.5,
        "draw_prob": 22.5,
        "away_win_prob": 31.0
    },
    {
        "id": 2,
        "home": "Liverpool",
        "away": "Sheffield United",
        "date": "2026-06-11",
        "venue": "Anfield",
        "home_odds": 2.35,
        "draw_odds": 4.70,
        "away_odds": 8.22,
        "verdict": "REJECTED",
        "confidence": 42.5,
        "home_win_prob": 42.5,
        "draw_prob": 21.3,
        "away_win_prob": 36.2
    },
    {
        "id": 3,
        "home": "Arsenal",
        "away": "Nottingham Forest",
        "date": "2026-06-11",
        "venue": "Emirates Stadium",
        "home_odds": 2.10,
        "draw_odds": 4.20,
        "away_odds": 7.35,
        "verdict": "REJECTED",
        "confidence": 47.6,
        "home_win_prob": 47.6,
        "draw_prob": 23.8,
        "away_win_prob": 28.6
    },
    {
        "id": 4,
        "home": "Chelsea",
        "away": "Burnley",
        "date": "2026-06-11",
        "venue": "Stamford Bridge",
        "home_odds": 2.55,
        "draw_odds": 5.10,
        "away_odds": 8.92,
        "verdict": "REJECTED",
        "confidence": 39.2,
        "home_win_prob": 39.2,
        "draw_prob": 19.6,
        "away_win_prob": 41.2
    },
    {
        "id": 5,
        "home": "Real Madrid",
        "away": "Almeria",
        "date": "2026-06-11",
        "venue": "Santiago Bernabeu",
        "home_odds": 2.05,
        "draw_odds": 4.10,
        "away_odds": 7.17,
        "verdict": "REJECTED",
        "confidence": 48.8,
        "home_win_prob": 48.8,
        "draw_prob": 24.4,
        "away_win_prob": 26.8
    }
]

# ========== FORENSIC DATA (for first match) ==========
FORENSIC_DATA = {
    "match_id": 1,
    "home": "Manchester City",
    "away": "Bournemouth",
    "league": "Premier League",
    "venue": "Etihad Stadium",
    "date": "June 12, 2026",
    "home_odds": 2.15,
    "draw_odds": 4.30,
    "away_odds": 7.52,
    "final_verdict": "REJECTED",
    "final_stake": 0.00,
    "final_reason": "Negative edge detected with low confidence",
    
    "m0_checks": [
        {"check": "Fixture Status", "value": "NS (upcoming)", "result": "PASS"},
        {"check": "Odds present", "value": "2.15/4.30/7.52", "result": "PASS"},
    ],
    "m0_hard_filters": [
        {"filter": "Senior Men's League", "result": "PASS"},
        {"filter": "League Tier", "result": "PASS (Tier 1)"},
    ],
    
    "m1_home_metrics": {
        "games": 20, "wins": 14, "draws": 4, "losses": 2,
        "goals_for": 48, "goals_against": 18,
        "home_record": "8-1-1", "home_wr": 80,
        "recent_form": "W, W, D, W, W, L",
        "ppg": 2.30
    },
    "m1_away_metrics": {
        "games": 20, "wins": 5, "draws": 6, "losses": 9,
        "goals_for": 22, "goals_against": 31,
        "away_record": "2-3-5", "away_wr": 20,
        "recent_form": "L, D, L, L, W, D",
        "ppg": 1.05
    },
    "m1_h2h": {
        "all_time": "Man City 70%, Draw 20%, Bournemouth 10%",
        "insight": "Man City has complete historical dominance"
    },
    
    "m3_odds_analysis": {
        "home_odds": 2.15, "home_implied": 46.5, "home_model": 42,
        "draw_odds": 4.30, "draw_implied": 23.3, "draw_model": 25,
        "away_odds": 7.52, "away_implied": 13.3, "away_model": 33,
        "margin": 16.9, "edge": -4.5
    },
    
    "m4_checks": [
        {"check": "C1: Season Win Gap", "passed": True, "value": "+9 wins", "points": 10},
        {"check": "C2: Venue Win Gap", "passed": True, "value": "+60%", "points": 10},
        {"check": "C3: H2H Favoured", "passed": True, "value": "70%", "points": 10},
    ],
    "m4_passed": 7, "m4_total": 8,
    
    "m5_failures": [
        {"name": "Negative Edge Detected", "points": 2.0},
        {"name": "Low Confidence Threshold", "points": 1.5},
    ],
    "m5_total": 3.5, "m5_threshold": 4.5,
    
    "m6_injuries": [
        {"team": "Manchester City", "player": "J. Grealish", "position": "M", "status": "DOUBTFUL"},
    ],
    "m6_scores": {"Manchester City": 75, "Bournemouth": 65},
    
    "m7_ai": [
        {"provider": "DeepSeek", "verdict": "CAUTION", "reasoning": "Low confidence in prediction"},
        {"provider": "Claude", "verdict": "REJECT", "reasoning": "Negative edge"},
        {"provider": "Gemini", "verdict": "CAUTION", "reasoning": "Injury concerns"},
        {"provider": "GPT", "verdict": "REJECT", "reasoning": "Value not found"},
    ],
    "m7_consensus": "REJECT", "m7_agreement": 75,
    
    "m8_h2h_all_time": {"home": 70, "away": 10},
    "m8_current_season": {"home": 70, "away": 25},
    "m8_severity": "LOW",
    "m8_verdict": "APPROVE",
    
    "m9_underdog_edge": -8,
    "m9_threat_level": "LOW",
    
    "m10_bilateral": {"home": 45, "draw": 25, "away": 30},
    "m10_confidence": "MEDIUM",
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
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None

def navigate_to(page, match=None):
    st.session_state.page = page
    if match:
        st.session_state.selected_match = match
    st.rerun()

# ========== SIDEBAR NAVIGATION ==========
with st.sidebar:
    st.markdown("## 🎯 Match Oracle")
    st.markdown("---")
    
    if st.button("📊 Dashboard", use_container_width=True):
        navigate_to("dashboard")
    
    if st.button("🔬 Forensic Report", use_container_width=True):
        if st.session_state.selected_match:
            navigate_to("forensic_report")
        else:
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

# ========== DASHBOARD PAGE (MATCH LIST STYLE) ==========
def show_dashboard():
    st.markdown('<p class="gold-header">🎯 Match Oracle</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">Forensic Betting Intelligence | AI-Powered Match Analysis</p>', unsafe_allow_html=True)
    
    # Header row with H D A labels
    col1, col2, col3, col4, col5 = st.columns([2.5, 1.5, 1, 1, 1.5])
    with col1:
        st.markdown("**Match**")
    with col2:
        st.markdown("**H**")
    with col3:
        st.markdown("**D**")
    with col4:
        st.markdown("**A**")
    with col5:
        st.markdown("**Verdict**")
    
    st.divider()
    
    # Display each match as a row
    for match in MATCHES:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2.5, 1.5, 1, 1, 1.5])
            
            with col1:
                st.markdown(f"**{match['home']} vs {match['away']}**")
                st.caption(f"{match['date']} · {match['venue'].split()[0]}")
            
            with col2:
                st.markdown(f"**{match['home_odds']}**")
            
            with col3:
                st.markdown(f"**{match['draw_odds']}**")
            
            with col4:
                st.markdown(f"**{match['away_odds']}**")
            
            with col5:
                # Verdict badge
                if match['verdict'] == "REJECTED":
                    st.markdown(f'<span class="verdict-badge verdict-rejected">🚫 {match["verdict"]}</span>', unsafe_allow_html=True)
                elif match['verdict'] == "APPROVED":
                    st.markdown(f'<span class="verdict-badge verdict-approved">✅ {match["verdict"]}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="verdict-badge verdict-caution">⚠️ {match["verdict"]}</span>', unsafe_allow_html=True)
                
                # Confidence bar
                st.markdown(f"""
                <div style="margin-top: 8px;">
                    <div style="font-size: 0.7rem; color: #888;">{match['confidence']}%</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {match['confidence']}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # View button for each match
            if st.button(f"Analyze", key=f"view_{match['id']}"):
                # Update forensic data with selected match
                global FORENSIC_DATA
                FORENSIC_DATA.update({
                    "home": match['home'],
                    "away": match['away'],
                    "venue": match['venue'],
                    "home_odds": match['home_odds'],
                    "draw_odds": match['draw_odds'],
                    "away_odds": match['away_odds'],
                    "final_verdict": f"{match['verdict']} ({match['confidence']}%)",
                })
                navigate_to("forensic_report", match)
    
    st.divider()
    
    # Footer
    st.caption("Select a match and click 'Analyze' to view the complete forensic report.")

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
    st.warning(f"**Edge: {mo['edge']:+}%**")
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
    status = "✅ PASS" if d['m5_total'] < d['m5_threshold'] else "❌ FAIL"
    st.markdown(f"**TOTAL:** {d['m5_total']} / {d['m5_threshold']} → {status}")
    st.divider()
    
    # Module 6
    st.markdown('<p class="module-header">MODULE 6: PERSONNEL FORENSICS</p>', unsafe_allow_html=True)
    for inj in d["m6_injuries"]:
        st.markdown(f"⚠️ {inj['team']}: {inj['player']} ({inj['position']}) - {inj['status']}")
    st.divider()
    
    # Module 7
    st.markdown('<p class="module-header">MODULE 7: QUAD-AI INTELLIGENCE</p>', unsafe_allow_html=True)
    for ai in d["m7_ai"]:
        st.markdown(f"**{ai['provider']}:** {ai['verdict']} - {ai['reasoning']}")
    st.info(f"**Consensus:** {d['m7_consensus']} (Agreement: {d['m7_agreement']}%)")
    st.divider()
    
    # Module 8
    st.markdown('<p class="module-header">MODULE 8: DUAL PATTERN ENGINE</p>', unsafe_allow_html=True)
    st.markdown(f"H2H all-time: {d['home']} DOMINANT ({d['m8_h2h_all_time']['home']}% vs {d['m8_h2h_all_time']['away']}%)")
    st.markdown(f"Current season: {d['home']} DOMINANT ({d['m8_current_season']['home']}% vs {d['m8_current_season']['away']}%)")
    st.info(f"**Conflict severity:** {d['m8_severity']}")
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
            <div class="odds-value-large">{d['home_odds']}</div>
        </div>
        <br>
        <div class="odds-button">
            <div class="stat-label">🤝 Draw</div>
            <div class="odds-value-large">{d['draw_odds']}</div>
        </div>
        <br>
        <div class="odds-button">
            <div class="stat-label">✈️ {d['away']}</div>
            <div class="odds-value-large">{d['away_odds']}</div>
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
    st.slider("AI Consensus Threshold", 0, 100, 60)
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
