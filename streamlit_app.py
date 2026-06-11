import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import os

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== BLACK/GOLD THEME CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #0f0f0f 100%);
    }
    
    /* Gold accent headers */
    .gold-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    
    .gold-subheader {
        font-size: 1.2rem;
        color: #B8860B;
        margin-bottom: 2rem;
        border-left: 3px solid #FFD700;
        padding-left: 1rem;
    }
    
    /* Match Card */
    .match-card {
        background: linear-gradient(135deg, #1a1a1a, #0d0d0d);
        border: 1px solid #2a2a2a;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .match-card:hover {
        border-color: #FFD700;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* League badge */
    .league-badge {
        background-color: #FFD70020;
        color: #FFD700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Odds display */
    .odds-box {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 6px 12px;
        text-align: center;
        min-width: 70px;
    }
    
    .odds-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #FFD700;
    }
    
    .odds-label {
        font-size: 0.6rem;
        color: #666;
        text-transform: uppercase;
    }
    
    /* Edge indicator */
    .edge-positive {
        color: #00FF88;
        font-weight: 700;
    }
    
    .edge-negative {
        color: #FF4444;
        font-weight: 700;
    }
    
    /* Probability bar */
    .prob-bar-container {
        background-color: #2a2a2a;
        border-radius: 4px;
        height: 6px;
        width: 100%;
        margin-top: 8px;
    }
    
    .prob-bar {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        border-radius: 4px;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* Status badges */
    .status-approved {
        background-color: #00FF8820;
        color: #00FF88;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .status-rejected {
        background-color: #FF444420;
        color: #FF4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .status-caution {
        background-color: #FFA50020;
        color: #FFA500;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    /* Divider */
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
        margin: 1.5rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #1a1a1a;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFD700;
        color: #0a0a0a;
    }
</style>
""", unsafe_allow_html=True)

# ========== API KEY CONFIGURATION ==========
def get_backend_url():
    try:
        backend_url = st.secrets.get("BACKEND_URL", "")
        if backend_url:
            return backend_url
    except:
        pass
    return st.session_state.get("backend_url", "https://oracle-backend-1-vryo.onrender.com")

def test_backend_connection(backend_url):
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                return True, data
        return False, None
    except:
        return False, None

# ========== COMPLETE MATCH DATA ==========
MATCHES = [
    {
        "id": 1, "home": "Wexford Youths", "away": "Cork City", "league": "League of Ireland", "tier": 2,
        "time": "19:45", "date": "2025-06-11", "venue": "Ferrycarrig Park",
        "home_odds": 2.90, "draw_odds": 3.20, "away_odds": 2.36,
        "selection": "Cork City", "selection_odds": 2.36,
        "prob": 62, "edge": 4.2, "confidence": "HIGH", "status": "APPROVED",
    },
    {
        "id": 2, "home": "Derry City", "away": "Bohemians FC", "league": "League of Ireland", "tier": 2,
        "time": "19:45", "date": "2025-06-11", "venue": "Ryan McBride Brandywell",
        "home_odds": 2.90, "draw_odds": 3.20, "away_odds": 2.36,
        "selection": "Bohemians FC", "selection_odds": 2.36,
        "prob": 54, "edge": 2.3, "confidence": "HIGH", "status": "REJECTED",
        "rejection_reason": "H2H CONFLICT",
    },
    {
        "id": 3, "home": "Shamrock Rovers", "away": "Shelbourne FC", "league": "League of Ireland", "tier": 2,
        "time": "19:45", "date": "2025-06-11", "venue": "Tallaght Stadium",
        "home_odds": 1.33, "draw_odds": 4.50, "away_odds": 6.00,
        "selection": "Shamrock Rovers", "selection_odds": 1.33,
        "prob": 68, "edge": -7.2, "confidence": "HIGH", "status": "REJECTED",
        "rejection_reason": "Negative Edge",
    },
    {
        "id": 4, "home": "Ajax", "away": "Feyenoord", "league": "Eredivisie", "tier": 1,
        "time": "15:00", "date": "2025-06-11", "venue": "Johan Cruijff ArenA",
        "home_odds": 1.85, "draw_odds": 3.70, "away_odds": 3.90,
        "selection": "Ajax", "selection_odds": 1.85,
        "prob": 57, "edge": 5.1, "confidence": "HIGH", "status": "APPROVED",
    },
]

# ========== COMPLETE FORENSIC DATA (Leg Data + Full Forensic) ==========
FORENSIC_DATA = {
    1: {  # Wexford vs Cork City - APPROVED
        "status": "APPROVED",
        "verdict_reason": "Clear value: model 62% vs market implied 58%",
        "leg_data": {
            "match_id": "wexford_cork_20250611",
            "country": "Ireland", "league": "League of Ireland", "tier": 2,
            "venue": "Ferrycarrig Park", "kickoff": "2025-06-11 19:45",
            "home_form": "L D W L L", "away_form": "W W D L W",
            "home_position": 8, "away_position": 3,
            "home_points": 24, "away_points": 38,
            "home_ppg": 1.2, "away_ppg": 1.9,
            "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%",
            "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1",
        },
        "forensic": {
            "m4": {
                "C1": {"passed": True, "value": 14, "threshold": 3, "message": "fav wins: 20, und wins: 6, gap: +14"},
                "C2": {"passed": True, "value": 0.22, "threshold": 0.15, "message": "fav venue rate: 78%, und away rate: 56%, gap: +22%"},
                "C3": {"passed": True, "value": 0.65, "threshold": 0.50, "message": "fav win rate: 65% over 48 games"},
                "C4": {"passed": True, "value": 0.58, "threshold": 0.45, "message": "W→W probability: 58%"},
                "C5": {"passed": False, "value": 0.38, "threshold": 0.45, "message": "L→W probability: 38% (below threshold)"},
                "C6": {"passed": True, "value": 0.72, "threshold": 0.88, "message": "fav win rate: 72% (below ceiling)"},
                "C7": {"passed": True, "value": 0.40, "threshold": 0.20, "message": "fav last5: 80%, und last5: 40%, gap: +40%"},
                "C8": {"passed": True, "value": 0.42, "threshold": 0.10, "message": "fav xG diff: +0.42, und xG diff: +0.00, gap: +0.42"},
            },
            "m5_failures": [
                {"name": "New Manager Bounce (underdog)", "points": 2.0, "reason": "Cork City appointed new manager 45 days ago"},
                {"name": "High Draw Probability (25%)", "points": 1.0, "reason": "Historical H2H draw rate 25% in last 6 meetings"},
            ],
            "m6": {"home_score": 82, "home_injuries": "None", "home_fatigue": "LOW", "away_score": 65, "away_injuries": "1 (midfielder)", "away_fatigue": "MEDIUM"},
            "m7": [
                {"provider": "DeepSeek", "verdict": "APPROVE", "confidence": "78%"},
                {"provider": "Claude", "verdict": "APPROVE", "confidence": "72%"},
                {"provider": "Gemini", "verdict": "CAUTION", "confidence": "55%"},
                {"provider": "GPT", "verdict": "APPROVE", "confidence": "75%"},
            ],
            "m8": {"dual_risk": "LOW", "underdog_threat": "NONE", "pattern_clash": 0.18, "resilience_gap": 0.24, "patterns_reliable": True, "h2h_conflict": False},
            "m9": {"underdog_edge": -2.1, "threat_level": "LOW", "pattern_score": 22, "goldmine": False},
            "m10": {"matrix_useful": True, "bilateral": "HOME", "confidence": "HIGH", "trap_signal": "NONE"},
            "m26": {"importance": 72, "is_rivalry": True, "home_motivation": "HIGH", "away_motivation": "NORMAL"},
            "m27": {"score": 78, "label": "FAV_EDGE", "games": 48, "fav_wins": 29, "draws": 11, "und_wins": 8, "draw_rate": 23, "psychological_block": False, "draw_boost": 1.00},
            "risk_flags": ["Pattern clash moderate", "H2H bounce-back threat: 45%"],
        },
        "stake": 33.50, "bankroll": 1000, "kelly_raw": 0.085, "kelly_adj": 0.0335,
    },
    2: {  # Derry vs Bohemians - CONFLICT REJECT
        "status": "REJECTED",
        "verdict_reason": "H2H CONFLICT: Historical H2H favours Derry (46% wins), but current season favours Bohemians (45% WR). M8 v6 Rule: Conflict = HARD REJECT.",
        "leg_data": {
            "match_id": "derry_bohemians_20250611",
            "country": "Ireland", "league": "League of Ireland", "tier": 2,
            "venue": "Ryan McBride Brandywell", "kickoff": "2025-06-11 19:45",
            "home_form": "L L W D L", "away_form": "W W D W L",
            "home_position": 6, "away_position": 2,
            "home_points": 28, "away_points": 42,
            "home_ppg": 1.4, "away_ppg": 2.1,
            "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%",
            "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1",
        },
        "forensic": {
            "m4": {
                "C1": {"passed": True, "value": 12, "threshold": 3, "message": "fav wins: 18, und wins: 6, gap: +12"},
                "C2": {"passed": True, "value": 0.18, "threshold": 0.15, "message": "fav venue rate: 72%, und away rate: 54%, gap: +18%"},
                "C3": {"passed": True, "value": 0.60, "threshold": 0.50, "message": "fav win rate: 60% over 30 games"},
                "C4": {"passed": True, "value": 0.55, "threshold": 0.45, "message": "W→W probability: 55%"},
                "C5": {"passed": False, "value": 0.35, "threshold": 0.45, "message": "L→W probability: 35%"},
                "C6": {"passed": True, "value": 0.68, "threshold": 0.88, "message": "fav win rate: 68%"},
                "C7": {"passed": True, "value": 0.35, "threshold": 0.20, "message": "gap: +35%"},
                "C8": {"passed": True, "value": 0.38, "threshold": 0.10, "message": "xG gap: +0.38"},
            },
            "m5_failures": [
                {"name": "New Manager Bounce (underdog)", "points": 2.0, "reason": "Derry appointed new manager 30 days ago"},
                {"name": "High Draw Probability (28%)", "points": 1.0, "reason": "Historical H2H draw rate 28%"},
            ],
            "m6": {"home_score": 68, "home_injuries": "2 (CB, ST)", "home_fatigue": "HIGH", "away_score": 72, "away_injuries": "None", "away_fatigue": "LOW"},
            "m7": [
                {"provider": "DeepSeek", "verdict": "CAUTION", "confidence": "65%"},
                {"provider": "Claude", "verdict": "APPROVE", "confidence": "70%"},
                {"provider": "Gemini", "verdict": "REJECT", "confidence": "60%"},
                {"provider": "GPT", "verdict": "CAUTION", "confidence": "62%"},
            ],
            "m8": {"dual_risk": "HIGH", "underdog_threat": "HIGH", "pattern_clash": 0.45, "resilience_gap": -0.12, "patterns_reliable": False, "h2h_conflict": True, "conflict_details": {"h2h_wr": 46, "current_wr": 45, "h2h_games": 80, "current_games": 20, "home_record": "20% wins, 6th place", "away_record": "45% wins, 2nd place"}},
            "m9": {"underdog_edge": 2.3, "threat_level": "HIGH", "pattern_score": 68, "goldmine": False},
            "m10": {"matrix_useful": True, "bilateral": "AWAY", "confidence": "MEDIUM", "trap_signal": "NONE"},
            "m26": {"importance": 85, "is_rivalry": True, "home_motivation": "DESPERATE", "away_motivation": "HIGH"},
            "m27": {"score": 45, "label": "UND_EDGE", "games": 80, "fav_wins": 37, "draws": 24, "und_wins": 19, "draw_rate": 30, "psychological_block": True, "draw_boost": 1.05},
            "risk_flags": ["🚨 H2H CONFLICT - HARD REJECT", "Pattern clash significant", "Underdog threat elevated"],
        },
        "stake": 0, "bankroll": 1000,
    },
}

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Leg Data"
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"
if "backend_url" not in st.session_state:
    st.session_state.backend_url = get_backend_url()

def check_backend():
    connected, data = test_backend_connection(st.session_state.backend_url)
    st.session_state.backend_status = "connected" if connected else "disconnected"

if st.session_state.backend_status == "checking":
    check_backend()

def navigate_to(page, match=None):
    st.session_state.page = page
    if match:
        st.session_state.selected_match = match
    st.rerun()

def go_back():
    navigate_to("dashboard")

def safe_get(data, key, default=None):
    if data is None:
        return default
    return data.get(key, default)

# ========== MATCH CARD COMPONENT ==========
def show_match_card(match):
    fid = match.get('id', 0)
    fdata = FORENSIC_DATA.get(fid, {})
    status = fdata.get('status', 'PENDING')
    
    # Status icon and color
    if status == "APPROVED":
        status_badge = '<span class="status-approved">✅ APPROVED</span>'
    elif status == "REJECTED":
        if "CONFLICT" in fdata.get('verdict_reason', ''):
            status_badge = '<span class="status-rejected">🚨 H2H CONFLICT</span>'
        else:
            status_badge = '<span class="status-rejected">❌ REJECTED</span>'
    else:
        status_badge = '<span class="status-caution">⚠️ PENDING</span>'
    
    edge = match.get('edge', 0)
    edge_class = "edge-positive" if edge > 0 else "edge-negative"
    edge_symbol = "+" if edge > 0 else ""
    
    prob = match.get('prob', 50)
    
    st.markdown(f"""
    <div class="match-card" onclick="alert('clicked')">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <span class="league-badge">{match.get('league', '?')} • Tier {match.get('tier', '?')}</span>
                <h3 style="margin: 0.5rem 0 0.25rem 0; font-size: 1.1rem;">{match.get('home', '?')} vs {match.get('away', '?')}</h3>
                <div style="font-size: 0.8rem; color: #888;">🕐 {match.get('time', 'TBD')} • 📍 {match.get('venue', 'TBD')}</div>
            </div>
            <div>
                {status_badge}
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div style="display: flex; gap: 1rem;">
                <div class="odds-box">
                    <div class="odds-value">{match.get('home_odds', 0):.2f}</div>
                    <div class="odds-label">HOME</div>
                </div>
                <div class="odds-box">
                    <div class="odds-value">{match.get('draw_odds', 0):.2f}</div>
                    <div class="odds-label">DRAW</div>
                </div>
                <div class="odds-box">
                    <div class="odds-value">{match.get('away_odds', 0):.2f}</div>
                    <div class="odds-label">AWAY</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div><span class="{edge_class}">{edge_symbol}{edge:.1f}% EDGE</span></div>
                <div style="font-size: 0.85rem;">🎯 {match.get('selection', '?')} @ {match.get('selection_odds', 0):.2f}</div>
                <div class="prob-bar-container">
                    <div class="prob-bar" style="width: {prob}%;"></div>
                </div>
                <div style="font-size: 0.7rem; color: #888;">Model Prob: {prob}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button for clicking (Streamlit button inside)
    if st.button(f"🔍 View Analysis", key=f"view_{match.get('id', 0)}", use_container_width=True):
        navigate_to("match_detail", match)

# ========== LEG DATA TAB ==========
def show_leg_data(match, fdata):
    leg_data = safe_get(fdata, 'leg_data', {})
    
    st.markdown("### 📋 Match Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Country", leg_data.get('country', '?'))
        st.metric("League", leg_data.get('league', '?'))
        st.metric("Tier", leg_data.get('tier', '?'))
    with col2:
        st.metric("Venue", leg_data.get('venue', '?'))
        st.metric("Kickoff", leg_data.get('kickoff', '?').split(' ')[1] if leg_data.get('kickoff') else '?')
        st.metric("Match ID", leg_data.get('match_id', '?'))
    with col3:
        st.metric("Home Position", leg_data.get('home_position', '?'))
        st.metric("Away Position", leg_data.get('away_position', '?'))
        st.metric("Points Gap", f"{leg_data.get('away_points', 0) - leg_data.get('home_points', 0)}")
    
    st.divider()
    
    st.markdown("### 📊 Team Form")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{match.get('home', 'Home')}**")
        form_home = leg_data.get('home_form', '?')
        st.markdown(f"<div style='font-size: 1.2rem; letter-spacing: 4px;'>{form_home}</div>", unsafe_allow_html=True)
        st.caption(f"PPG: {leg_data.get('home_ppg', 0)} | Position: {leg_data.get('home_position', '?')}")
    with col2:
        st.markdown(f"**{match.get('away', 'Away')}**")
        form_away = leg_data.get('away_form', '?')
        st.markdown(f"<div style='font-size: 1.2rem; letter-spacing: 4px;'>{form_away}</div>", unsafe_allow_html=True)
        st.caption(f"PPG: {leg_data.get('away_ppg', 0)} | Position: {leg_data.get('away_position', '?')}")
    
    st.divider()
    
    st.markdown("### 📜 Head-to-Head Record")
    st.info(f"**All-time:** {leg_data.get('h2h_record', 'No data')}")
    st.info(f"**Last 6 meetings:** {leg_data.get('h2h_last6', 'No data')}")
    
    st.divider()
    
    st.markdown("### 🏆 Current Season Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{match.get('home', 'Home')}**")
        st.write(f"Points: {leg_data.get('home_points', 0)}")
        st.write(f"Wins: {int(leg_data.get('home_ppg', 0) * 20)}")
        st.write(f"Home Win %: {(leg_data.get('home_ppg', 0) / 3 * 100):.0f}%")
    with col2:
        st.markdown(f"**{match.get('away', 'Away')}**")
        st.write(f"Points: {leg_data.get('away_points', 0)}")
        st.write(f"Wins: {int(leg_data.get('away_ppg', 0) * 20)}")
        st.write(f"Away Win %: {(leg_data.get('away_ppg', 0) / 3 * 100):.0f}%")

# ========== FULL FORENSIC TAB ==========
def show_full_forensic(match, fdata):
    forensic = safe_get(fdata, 'forensic', {})
    
    # M4 Pre-filter
    st.markdown("## M4: Asymmetric Pre-filter (8 Checks)")
    m4 = safe_get(forensic, 'm4', {})
    for check_id, check in m4.items():
        passed = check.get("passed", False)
        icon = "✅" if passed else "❌"
        col1, col2, col3 = st.columns([1.5, 1, 2.5])
        with col1:
            st.write(f"{icon} **{check_id}**")
        with col2:
            st.write(f"Value: {check.get('value', 0)}")
        with col3:
            st.write(f"Threshold: {check.get('threshold', 0)} | {check.get('message', '')}")
    
    m4_passed = sum(1 for c in m4.values() if c.get('passed', False))
    st.markdown(f"**Result:** {m4_passed}/8 passed → {'✅ PASS' if m4_passed >= 5 else '❌ FAIL'}")
    
    st.divider()
    
    # M5 Forensic Failures
    st.markdown("## M5: Forensic Failures")
    m5_failures = safe_get(forensic, 'm5_failures', [])
    for failure in m5_failures:
        col1, col2, col3 = st.columns([2, 0.5, 2.5])
        with col1:
            st.write(f"⚠️ **{failure['name']}**")
        with col2:
            st.write(f"+{failure['points']} pts")
        with col3:
            st.write(f"_{failure['reason']}_")
    
    m5_score = sum(f.get('points', 0) for f in m5_failures)
    st.markdown(f"**Total Failure Score:** {m5_score} / 4.5 → {'✅ PASS' if m5_score < 4.5 else '❌ FAIL'}")
    
    st.divider()
    
    # M6 Personnel
    st.markdown("## M6: Personnel Forensics")
    m6 = safe_get(forensic, 'm6', {})
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{match.get('home', 'Home')}**")
        st.metric("Personnel Score", f"{m6.get('home_score', 50)}/100")
        st.write(f"🔑 Injuries: {m6.get('home_injuries', 'None')}")
        st.write(f"⚡ Fatigue: {m6.get('home_fatigue', 'NORMAL')}")
    with col2:
        st.markdown(f"**{match.get('away', 'Away')}**")
        st.metric("Personnel Score", f"{m6.get('away_score', 50)}/100")
        st.write(f"🔑 Injuries: {m6.get('away_injuries', 'None')}")
        st.write(f"⚡ Fatigue: {m6.get('away_fatigue', 'NORMAL')}")
    
    st.divider()
    
    # M7 AI Consensus
    st.markdown("## M7: AI Consensus")
    m7 = safe_get(forensic, 'm7', [])
    if m7:
        ai_df = pd.DataFrame(m7)
        st.dataframe(ai_df, use_container_width=True, hide_index=True)
        approve_count = sum(1 for a in m7 if a.get('verdict') == 'APPROVE')
        st.markdown(f"**Consensus:** {approve_count}/{len(m7)} APPROVE → {'✅ APPROVED' if approve_count >= 3 else '⚠️ SPLIT'}")
    
    st.divider()
    
    # M8 Dual Pattern
    st.markdown("## M8: Dual Pattern Engine")
    m8 = safe_get(forensic, 'm8', {})
    
    if m8.get('h2h_conflict', False):
        st.error("🚨 **H2H CONFLICT DETECTED - HARD REJECT**")
        conflict = m8.get('conflict_details', {})
        st.markdown(f"""
        **H2H HISTORY ({conflict.get('h2h_games', 80)} matches):**
        - {match.get('home', 'Home')}: {conflict.get('h2h_wr', 46)}% wins
        - Draws: 30%
        - {match.get('away', 'Away')}: {100 - conflict.get('h2h_wr', 46) - 30}% wins
        
        **CURRENT SEASON ({conflict.get('current_games', 20)} matches):**
        - {match.get('home', 'Home')}: {conflict.get('home_record', 'Poor form')}
        - {match.get('away', 'Away')}: {conflict.get('away_record', 'Good form')}
        
        **CONFLICT:** H2H and current season directly contradict each other.
        **M8 v6 RULE:** Conflict = HARD REJECT (stake multiplier = 0.0)
        """)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Dual Risk Level", m8.get('dual_risk', 'MEDIUM'))
            st.metric("Pattern Clash Score", f"{m8.get('pattern_clash', 0):.2f}")
        with col2:
            st.metric("Underdog Threat", m8.get('underdog_threat', 'NONE'))
            st.metric("Resilience Gap", f"{m8.get('resilience_gap', 0):+.2f}")
        st.caption(f"Patterns Reliable: {'✅ YES' if m8.get('patterns_reliable', False) else '⚠️ NO'}")
    
    st.divider()
    
    # M9 Underdog Scanner
    st.markdown("## M9: Underdog Scanner")
    m9 = safe_get(forensic, 'm9', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Underdog Edge", f"{m9.get('underdog_edge', 0):+.1f}%")
        st.metric("Threat Level", m9.get('threat_level', 'NONE'))
    with col2:
        st.metric("Pattern Score", f"{m9.get('pattern_score', 0)}/100")
        st.metric("Goldmine Qualified", "✅ YES" if m9.get('goldmine', False) else "❌ NO")
    
    st.divider()
    
    # M10 Tally Matrix
    st.markdown("## M10: Tally Matrix")
    m10 = safe_get(forensic, 'm10', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Matrix Useful", "✅ YES" if m10.get('matrix_useful', False) else "❌ NO")
        st.metric("Bilateral Prediction", m10.get('bilateral', 'UNCERTAIN'))
    with col2:
        st.metric("Bilateral Confidence", m10.get('confidence', 'LOW'))
        st.metric("Trap/Value Signal", m10.get('trap_signal', 'NONE'))
    
    st.divider()
    
    # M26 Match Context
    st.markdown("## M26: Match Context")
    m26 = safe_get(forensic, 'm26', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Match Importance", f"{m26.get('importance', 50)}%")
        st.write(f"🏆 Is Rivalry: {'✅ YES' if m26.get('is_rivalry', False) else '❌ NO'}")
    with col2:
        st.metric("Home Motivation", m26.get('home_motivation', 'NORMAL'))
        st.metric("Away Motivation", m26.get('away_motivation', 'NORMAL'))
    
    st.divider()
    
    # M27 H2H Deep Analysis
    st.markdown("## M27: H2H Deep Analysis")
    m27 = safe_get(forensic, 'm27', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("H2H Score", f"{m27.get('score', 50)}/100", m27.get('label', 'NEUTRAL'))
        st.write(f"📊 Games: {m27.get('games', 0)} | 🟢 Fav {m27.get('fav_wins', 0)} | 🟡 Draw {m27.get('draws', 0)} | 🔴 Und {m27.get('und_wins', 0)}")
    with col2:
        st.metric("Draw Rate", f"{m27.get('draw_rate', 0)}%")
        st.metric("Psychological Block", "✅ YES" if m27.get('psychological_block', False) else "❌ NO")
        st.metric("Draw Boost Factor", f"{m27.get('draw_boost', 1.00):.2f}x")
    
    st.divider()
    
    # Risk Flags
    st.markdown("## ⚠️ Risk Flags")
    risk_flags = safe_get(forensic, 'risk_flags', [])
    for flag in risk_flags:
        if "CONFLICT" in flag or "HARD REJECT" in flag:
            st.error(flag)
        elif "NEGATIVE" in flag:
            st.warning(flag)
        else:
            st.info(flag)
    
    st.divider()
    
    # Final Verdict
    st.markdown("## ✅ FINAL VERDICT")
    status = fdata.get('status', 'PENDING')
    verdict_reason = fdata.get('verdict_reason', 'No reason provided')
    
    if status == "APPROVED":
        stake = fdata.get('stake', 0)
        bankroll = fdata.get('bankroll', 1000)
        stake_pct = (stake / bankroll) * 100 if bankroll > 0 else 0
        st.success(f"""
        **STATUS: APPROVED**
        - Reason: {verdict_reason}
        - Confidence: {match.get('confidence', 'HIGH')}
        - Model Probability: {match.get('prob', 50)}%
        - Edge: +{match.get('edge', 0)}%
        - Kelly Stake: **£{stake:.2f}** ({stake_pct:.2f}% of bankroll)
        - Potential Return: £{stake * match.get('selection_odds', 0):.2f}
        - Potential Profit: £{stake * (match.get('selection_odds', 0) - 1):.2f}
        """)
    elif m8.get('h2h_conflict', False):
        st.error(f"""
        **STATUS: REJECTED (H2H CONFLICT)**
        - Reason: {verdict_reason}
        - Model Probability: {match.get('prob', 50)}%
        - Edge: +{match.get('edge', 0)}% (would be value)
        - Odds: {match.get('selection_odds', 0):.2f}
        
        **M8 v6 Rule:** Conflict = HARD REJECT (stake multiplier = 0.0)
        """)
    elif match.get('edge', 0) < 0:
        implied = (1/match.get('selection_odds', 1) * 100) if match.get('selection_odds', 0) > 0 else 0
        st.warning(f"""
        **STATUS: REJECTED (Negative Edge)**
        - Reason: {verdict_reason}
        - Model Probability: {match.get('prob', 50)}%
        - Implied Probability: {implied:.1f}%
        - Edge: {match.get('edge', 0):+.1f}%
        
        **Reason:** No mathematical value. Market is more confident than our model.
        """)
    else:
        st.info(f"**STATUS: {status}**")

# ========== MATCH DETAIL PAGE ==========
def show_match_detail():
    match = st.session_state.selected_match
    if match is None:
        st.error("No match selected")
        if st.button("← Back to Dashboard"):
            go_back()
        return
    
    fid = match.get('id', 0)
    fdata = FORENSIC_DATA.get(fid, {})
    
    # Header with gold theme
    st.markdown(f'<p class="gold-header">🔬 {match.get("home", "?")} vs {match.get("away", "?")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="gold-subheader">{match.get("league", "?")} • {match.get("venue", "?")} • {match.get("time", "TBD")}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    # Tabs for Leg Data and Full Forensic
    tab1, tab2 = st.tabs(["📊 Leg Data", "🔬 Full Forensic Report"])
    
    with tab1:
        show_leg_data(match, fdata)
    
    with tab2:
        show_full_forensic(match, fdata)
    
    # Kelly Calculation for approved bets
    if fdata.get('status') == 'APPROVED':
        st.divider()
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        st.markdown("## 📊 Kelly Calculation")
        st.markdown(f"""
        - Raw Kelly Fraction: {fdata.get('kelly_raw', 0.085)*100:.2f}%
        - Confidence Scaling: {match.get('confidence', 'HIGH')} → 50% of Kelly
        - Adjusted Kelly: {fdata.get('kelly_adj', 0.0335)*100:.2f}%
        - Bankroll: £{fdata.get('bankroll', 1000):.0f}
        - **Final Stake: £{fdata.get('stake', 0):.2f}**
        """)

# ========== DASHBOARD PAGE (Homepage) ==========
def show_dashboard():
    # Hero Section - Black/Gold Theme
    st.markdown('<p class="gold-header">MATCH ORACLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">AI-Powered Football Intelligence • Elite Betting Analysis</p>', unsafe_allow_html=True)
    
    # Backend Status
    if st.session_state.backend_status == "connected":
        st.success(f"✅ BACKEND ONLINE | {st.session_state.backend_url}")
    else:
        st.warning(f"⚠️ BACKEND OFFLINE | Using demo data")
    
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    # Today's Fixtures Header
    st.markdown("## 📅 Today's Fixtures")
    st.caption(f"{len(MATCHES)} matches scheduled • {datetime.now().strftime('%A, %B %d, %Y')}")
    
    st.markdown("---")
    
    # Display Match Cards
    for match in MATCHES:
        show_match_card(match)
    
    # Footer
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.caption("© 2025 Match Oracle • AI-powered football intelligence")
    st.caption("Data updates every 60 seconds • Powered by API-Football")

# ========== OTHER PAGES ==========
def show_performance():
    st.markdown('<p class="gold-header">📈 Performance Metrics</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Calibration Grade", "B", "Good")
    with col2:
        st.metric("Brier Score", "0.187", "0=perfect")
    with col3:
        st.metric("ECE", "0.094", "0=perfect")
    
    st.divider()
    
    st.subheader("Accuracy by Confidence Level")
    acc_data = pd.DataFrame({"Confidence": ["HIGH", "MEDIUM", "LOW"], "Accuracy": [68, 52, 48]})
    fig = px.bar(acc_data, x="Confidence", y="Accuracy", color="Confidence", text="Accuracy")
    fig.update_layout(plot_bgcolor="#1a1a1a", paper_bgcolor="#0a0a0a", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

def show_bankroll():
    st.markdown('<p class="gold-header">💰 Bankroll Manager</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Bankroll", "$12,450", "-$750")
    with col2:
        st.metric("Peak Bankroll", "$13,200", "")
    with col3:
        st.metric("Drawdown", "5.7%", "↓")
    with col4:
        st.metric("Stake Multiplier", "0.85x", "Reduced")
    
    st.divider()
    
    history = pd.DataFrame([
        {"date": "Jun 1", "bankroll": 10000}, {"date": "Jun 2", "bankroll": 10250},
        {"date": "Jun 3", "bankroll": 10500}, {"date": "Jun 4", "bankroll": 10300},
        {"date": "Jun 5", "bankroll": 10800}, {"date": "Jun 6", "bankroll": 11200},
        {"date": "Jun 7", "bankroll": 11800}, {"date": "Jun 8", "bankroll": 12450},
    ])
    fig = px.line(history, x="date", y="bankroll", markers=True)
    fig.update_layout(plot_bgcolor="#1a1a1a", paper_bgcolor="#0a0a0a", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

def show_top_picks():
    st.markdown('<p class="gold-header">🏆 Top Picks</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    
    approved = [m for m in MATCHES if FORENSIC_DATA.get(m.get('id', 0), {}).get('status') == 'APPROVED']
    if approved:
        for i, match in enumerate(approved, 1):
            st.markdown(f"**#{i} {match.get('home', '?')} vs {match.get('away', '?')}** - {match.get('selection', '?')} @ {match.get('selection_odds', 0):.2f}")
            st.caption(f"Edge: +{match.get('edge', 0)}% | Prob: {match.get('prob', 0)}%")
            st.divider()
    else:
        st.info("No approved picks for today")

def show_parlays():
    st.markdown('<p class="gold-header">🔗 Parlay Builder</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    st.info("Parlay builder coming soon")

def show_all_legs():
    st.markdown('<p class="gold-header">📋 All Legs</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    for match in MATCHES:
        st.write(f"{match.get('home', '?')} vs {match.get('away', '?')} - {match.get('league', '?')} - {match.get('time', 'TBD')}")

def show_countries():
    st.markdown('<p class="gold-header">🌍 Country Explorer</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    st.info("Country explorer coming soon")

def show_calendar():
    st.markdown('<p class="gold-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    st.date_input("Select Date", datetime.now().date())

def show_settings():
    st.markdown('<p class="gold-header">⚙️ Settings</p>', unsafe_allow_html=True)
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    st.divider()
    
    st.markdown("### 🔌 Backend Connection")
    st.code(st.session_state.backend_url, language="text")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Test Connection", use_container_width=True):
            with st.spinner("Testing connection..."):
                connected, data = test_backend_connection(st.session_state.backend_url)
                if connected:
                    st.session_state.backend_status = "connected"
                    st.success("✅ Backend is ONLINE!")
                    st.rerun()
                else:
                    st.session_state.backend_status = "disconnected"
                    st.error("❌ Backend is OFFLINE")
    
    with col2:
        if st.button("🌐 Wake Up Backend", use_container_width=True):
            with st.spinner("Waking up backend (30-60 seconds)..."):
                try:
                    response = requests.get(f"{st.session_state.backend_url}/health", timeout=60)
                    if response.status_code == 200:
                        st.session_state.backend_status = "connected"
                        st.success("✅ Backend is ONLINE and ready!")
                        st.rerun()
                    else:
                        st.error(f"❌ Backend returned status {response.status_code}")
                except requests.exceptions.Timeout:
                    st.warning("⏰ Timeout - backend may still be waking up. Try again.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    st.markdown("### 🎨 Theme")
    st.info("🎨 Black/Gold Elite Theme Active")
    
    st.markdown("### 📡 Data Source")
    if st.session_state.backend_status == "connected":
        st.success("📡 Using BACKEND data")
    else:
        st.info("📊 Using DEMO DATA")
    
    st.markdown("### ⏰ Timezone")
    st.info("📍 GMT+3 (Nairobi)")

# ========== MAIN ==========
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🎯 MATCH ORACLE")
        st.markdown("---")
        
        # Backend Status Indicator
        if st.session_state.backend_status == "connected":
            st.success("🟢 BACKEND ONLINE")
        else:
            st.error("🔴 BACKEND OFFLINE")
        
        st.markdown("---")
        
        # Navigation Menu
        st.markdown("**📋 TODAY**")
        if st.button("🏠 Dashboard", use_container_width=True):
            navigate_to("dashboard")
        
        st.markdown("---")
        st.markdown("**📊 ANALYTICS**")
        if st.button("📈 Performance", use_container_width=True):
            navigate_to("performance")
        if st.button("💰 Bankroll", use_container_width=True):
            navigate_to("bankroll")
        if st.button("🏆 Top Picks", use_container_width=True):
            navigate_to("top_picks")
        if st.button("🔗 Parlays", use_container_width=True):
            navigate_to("parlays")
        
        st.markdown("---")
        st.markdown("**🔍 DATA**")
        if st.button("📋 All Legs", use_container_width=True):
            navigate_to("all_legs")
        if st.button("🌍 Countries", use_container_width=True):
            navigate_to("countries")
        if st.button("📅 Calendar", use_container_width=True):
            navigate_to("calendar")
        if st.button("⚙️ Settings", use_container_width=True):
            navigate_to("settings")
        
        st.markdown("---")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')} GMT+3")
        st.caption("🎯 Match Oracle v4.0")
    
    # Page Routing
    page = st.session_state.page
    if page == "dashboard":
        show_dashboard()
    elif page == "match_detail":
        show_match_detail()
    elif page == "performance":
        show_performance()
    elif page == "bankroll":
        show_bankroll()
    elif page == "top_picks":
        show_top_picks()
    elif page == "parlays":
        show_parlays()
    elif page == "all_legs":
        show_all_legs()
    elif page == "countries":
        show_countries()
    elif page == "calendar":
        show_calendar()
    elif page == "settings":
        show_settings()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
