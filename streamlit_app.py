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
    layout="wide"
)

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

# ========== COMPLETE MOCK DATA WITH FULL REASONING ==========
MOCK_FIXTURES = [
    {"id": 1, "home": "Wexford Youths", "away": "Cork City", "league": "League of Ireland", "time": "19:45", "odds": 1.73, "prob": 62, "edge": 4.2, "confidence": "HIGH", "selection": "Cork City"},
    {"id": 2, "home": "Derry City", "away": "Bohemians FC", "league": "League of Ireland", "time": "19:45", "odds": 2.36, "prob": 54, "edge": 2.3, "confidence": "HIGH", "selection": "Bohemians FC"},
    {"id": 3, "home": "Shamrock Rovers", "away": "Shelbourne FC", "league": "League of Ireland", "time": "19:45", "odds": 1.33, "prob": 68, "edge": -7.2, "confidence": "HIGH", "selection": "Shamrock Rovers"},
    {"id": 4, "home": "Ajax", "away": "Feyenoord", "league": "Eredivisie", "time": "15:00", "odds": 1.85, "prob": 57, "edge": 5.1, "confidence": "HIGH", "selection": "Ajax"},
]

# Complete forensic data with reasoning
FORENSIC_DATA = {
    1: {  # Wexford vs Cork City - APPROVED
        "status": "APPROVED",
        "status_color": "green",
        "verdict_reason": "Clear value: model 62% vs market implied 58%",
        "m4_passed": True, "m4_checks": 6, "m4_total": 8,
        "m5_score": 2.5, "m5_threshold": 4.5, "m5_passed": True,
        "m8_conflict": False,
        "edge": 4.2, "prob": 62, "odds": 1.73,
        "stake": 33.50, "bankroll": 1000,
        "kelly_raw": 0.085, "kelly_adj": 0.0335,
        "selection": "Cork City",
        "m4_details": {
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
        "m6_home": {"score": 82, "status": "Healthy", "injuries": "None", "fatigue": "LOW"},
        "m6_away": {"score": 65, "status": "1 injury", "injuries": "1 (midfielder)", "fatigue": "MEDIUM"},
        "m7_ai": [
            {"provider": "DeepSeek", "verdict": "APPROVE", "confidence": "78%"},
            {"provider": "Claude", "verdict": "APPROVE", "confidence": "72%"},
            {"provider": "Gemini", "verdict": "CAUTION", "confidence": "55%"},
            {"provider": "GPT", "verdict": "APPROVE", "confidence": "75%"},
        ],
        "m8_data": {"dual_risk": "LOW", "underdog_threat": "NONE", "pattern_clash": 0.18, "resilience_gap": 0.24, "patterns_reliable": True},
        "m9_data": {"underdog_edge": -2.1, "threat_level": "LOW", "pattern_score": 22, "goldmine": False},
        "m10_data": {"matrix_useful": True, "bilateral": "HOME", "confidence": "HIGH", "trap_signal": "NONE"},
        "m26_data": {"importance": 72, "is_rivalry": True, "home_motivation": "HIGH", "away_motivation": "NORMAL"},
        "m27_data": {"score": 78, "label": "FAV_EDGE", "games": 48, "fav_wins": 29, "draws": 11, "und_wins": 8, "draw_rate": 23, "psychological_block": False, "draw_boost": 1.00},
        "risk_flags": ["Pattern clash moderate", "H2H bounce-back threat: 45%"],
    },
    2: {  # Derry vs Bohemians - CONFLICT REJECT
        "status": "REJECTED",
        "status_color": "red",
        "verdict_reason": "H2H CONFLICT: Historical H2H favours Derry (46% wins), but current season favours Bohemians (45% WR). M8 v6 Rule: Conflict = HARD REJECT.",
        "m4_passed": True, "m4_checks": 6, "m4_total": 8,
        "m5_score": 2.5, "m5_threshold": 4.5, "m5_passed": True,
        "m8_conflict": True, "m8_severity": "HIGH",
        "edge": 2.3, "prob": 54, "odds": 2.36,
        "stake": 0, "bankroll": 1000,
        "selection": "Bohemians FC",
        "conflict_details": {
            "h2h_wr": 46, "current_wr": 45,
            "h2h_games": 80, "current_games": 20,
            "home_record": "20% wins, 6th place",
            "away_record": "45% wins, 2nd place",
        },
        "m4_details": {
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
        "m6_home": {"score": 68, "status": "2 injuries", "injuries": "2 (CB, ST)", "fatigue": "HIGH"},
        "m6_away": {"score": 72, "status": "Healthy", "injuries": "None", "fatigue": "LOW"},
        "m7_ai": [
            {"provider": "DeepSeek", "verdict": "CAUTION", "confidence": "65%"},
            {"provider": "Claude", "verdict": "APPROVE", "confidence": "70%"},
            {"provider": "Gemini", "verdict": "REJECT", "confidence": "60%"},
            {"provider": "GPT", "verdict": "CAUTION", "confidence": "62%"},
        ],
        "m8_data": {"dual_risk": "HIGH", "underdog_threat": "HIGH", "pattern_clash": 0.45, "resilience_gap": -0.12, "patterns_reliable": False},
        "m9_data": {"underdog_edge": 2.3, "threat_level": "HIGH", "pattern_score": 68, "goldmine": False},
        "m10_data": {"matrix_useful": True, "bilateral": "AWAY", "confidence": "MEDIUM", "trap_signal": "NONE"},
        "m26_data": {"importance": 85, "is_rivalry": True, "home_motivation": "DESPERATE", "away_motivation": "HIGH"},
        "m27_data": {"score": 45, "label": "UND_EDGE", "games": 80, "fav_wins": 37, "draws": 24, "und_wins": 19, "draw_rate": 30, "psychological_block": True, "draw_boost": 1.05},
        "risk_flags": ["🚨 H2H CONFLICT - HARD REJECT", "Pattern clash significant", "Underdog threat elevated"],
    },
    3: {  # Shamrock vs Shelbourne - NEGATIVE EDGE REJECT
        "status": "REJECTED",
        "status_color": "orange",
        "verdict_reason": "Negative edge: Model says 68% win probability, but market implies 75% (odds 1.33). No mathematical value.",
        "m4_passed": True, "m4_checks": 7, "m4_total": 8,
        "m5_score": 1.8, "m5_threshold": 4.5, "m5_passed": True,
        "m8_conflict": False,
        "edge": -7.2, "prob": 68, "odds": 1.33,
        "stake": 0, "bankroll": 1000,
        "selection": "Shamrock Rovers",
        "m4_details": {
            "C1": {"passed": True, "value": 16, "threshold": 3, "message": "fav wins: 22, und wins: 6, gap: +16"},
            "C2": {"passed": True, "value": 0.25, "threshold": 0.15, "message": "fav venue rate: 82%, und away rate: 57%, gap: +25%"},
            "C3": {"passed": True, "value": 0.70, "threshold": 0.50, "message": "fav win rate: 70% over 40 games"},
            "C4": {"passed": True, "value": 0.62, "threshold": 0.45, "message": "W→W probability: 62%"},
            "C5": {"passed": True, "value": 0.48, "threshold": 0.45, "message": "L→W probability: 48%"},
            "C6": {"passed": True, "value": 0.68, "threshold": 0.88, "message": "fav win rate: 68%"},
            "C7": {"passed": True, "value": 0.50, "threshold": 0.20, "message": "gap: +50%"},
            "C8": {"passed": True, "value": 0.55, "threshold": 0.10, "message": "xG gap: +0.55"},
        },
        "m5_failures": [
            {"name": "Saturation Risk", "points": 1.5, "reason": "xG overperformance: actual 2.1 vs xG 1.6"},
        ],
        "m6_home": {"score": 88, "status": "Healthy", "injuries": "None", "fatigue": "LOW"},
        "m6_away": {"score": 58, "status": "3 injuries", "injuries": "3 (LB, CM, RW)", "fatigue": "HIGH"},
        "m7_ai": [
            {"provider": "DeepSeek", "verdict": "APPROVE", "confidence": "82%"},
            {"provider": "Claude", "verdict": "APPROVE", "confidence": "78%"},
            {"provider": "Gemini", "verdict": "APPROVE", "confidence": "75%"},
            {"provider": "GPT", "verdict": "APPROVE", "confidence": "80%"},
        ],
        "m8_data": {"dual_risk": "LOW", "underdog_threat": "LOW", "pattern_clash": 0.12, "resilience_gap": 0.35, "patterns_reliable": True},
        "m9_data": {"underdog_edge": -7.2, "threat_level": "NONE", "pattern_score": 15, "goldmine": False},
        "m10_data": {"matrix_useful": True, "bilateral": "HOME", "confidence": "HIGH", "trap_signal": "TRAP"},
        "m26_data": {"importance": 65, "is_rivalry": False, "home_motivation": "NORMAL", "away_motivation": "LOW"},
        "m27_data": {"score": 85, "label": "FAV_DOMINANT", "games": 30, "fav_wins": 22, "draws": 5, "und_wins": 3, "draw_rate": 17, "psychological_block": False, "draw_boost": 0.95},
        "risk_flags": ["⚠️ NEGATIVE EDGE - NO VALUE", "Favourite priced too short (1.33)", "Market efficient - no edge"],
    },
}

LEAGUE_STATS = [
    {"league": "Premier League", "count": 12, "accuracy": 62, "roi": 15.2},
    {"league": "La Liga", "count": 10, "accuracy": 58, "roi": 9.8},
    {"league": "Bundesliga", "count": 8, "accuracy": 59, "roi": 11.2},
]

BANKROLL_HISTORY = [
    {"date": "Jun 1", "bankroll": 10000}, {"date": "Jun 2", "bankroll": 10250},
    {"date": "Jun 3", "bankroll": 10500}, {"date": "Jun 4", "bankroll": 10300},
    {"date": "Jun 5", "bankroll": 10800}, {"date": "Jun 6", "bankroll": 11200},
    {"date": "Jun 7", "bankroll": 11800}, {"date": "Jun 8", "bankroll": 12450},
]

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_fixture" not in st.session_state:
    st.session_state.selected_fixture = None
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"
if "backend_url" not in st.session_state:
    st.session_state.backend_url = get_backend_url()

def check_backend():
    connected, data = test_backend_connection(st.session_state.backend_url)
    st.session_state.backend_status = "connected" if connected else "disconnected"

if st.session_state.backend_status == "checking":
    check_backend()

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def go_back():
    navigate_to("dashboard")

def safe_get(data, key, default=None):
    if data is None:
        return default
    return data.get(key, default)

# ========== COMPLETE FORENSIC REPORT (Matching Your Example) ==========
def show_forensic_report(fixture):
    if fixture is None:
        st.error("No fixture selected")
        if st.button("← Back"):
            go_back()
        return
    
    fid = safe_get(fixture, 'id', 0)
    fdata = FORENSIC_DATA.get(fid, {})
    
    home = safe_get(fixture, 'home', '?')
    away = safe_get(fixture, 'away', '?')
    league = safe_get(fixture, 'league', '?')
    time = safe_get(fixture, 'time', 'TBD')
    odds = safe_get(fixture, 'odds', 0.0)
    selection = safe_get(fixture, 'selection', safe_get(fdata, 'selection', '?'))
    prob = safe_get(fixture, 'prob', 50)
    edge = safe_get(fdata, 'edge', safe_get(fixture, 'edge', 0))
    confidence = safe_get(fixture, 'confidence', 'MEDIUM')
    
    # Header
    st.markdown(f"# 🔬 {home} vs {away}")
    st.caption(f"📅 {league} | 🕐 {time} | 🎯 Selection: {selection} @ {odds:.2f}")
    
    if st.button("← Back to Fixtures"):
        go_back()
    
    st.divider()
    
    # ===== STATUS BANNER WITH REASON =====
    status = safe_get(fdata, 'status', 'PENDING')
    verdict_reason = safe_get(fdata, 'verdict_reason', 'No reason provided')
    
    if status == "APPROVED":
        st.success(f"### ✅ {status}")
        st.info(f"📝 **Reason:** {verdict_reason}")
    elif status == "REJECTED":
        if safe_get(fdata, 'm8_conflict', False):
            st.error(f"### 🚨 {status} (H2H CONFLICT)")
        else:
            st.warning(f"### ⚠️ {status}")
        st.info(f"📝 **Reason:** {verdict_reason}")
    else:
        st.info(f"### ℹ️ {status}")
    
    st.divider()
    
    # ===== MODULE 4: PRE-FILTER (8 Checks with Values) =====
    st.markdown("## M4: Asymmetric Pre-filter (8 Checks)")
    
    m4_details = safe_get(fdata, 'm4_details', {})
    checks_order = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
    check_names = {
        "C1": "Season Win Gap", "C2": "Venue Win Gap", "C3": "H2H Favoured",
        "C4": "Transition Favours", "C5": "Bounce-back Rate", "C6": "Ceiling Proximity",
        "C7": "Momentum Gap", "C8": "Resilience Gap"
    }
    
    for check_id in checks_order:
        check = m4_details.get(check_id, {})
        passed = check.get("passed", False)
        value = check.get("value", 0)
        threshold = check.get("threshold", 0)
        message = check.get("message", "")
        
        icon = "✅" if passed else "❌"
        col1, col2, col3 = st.columns([1.5, 1, 2.5])
        with col1:
            st.write(f"{icon} **{check_names[check_id]}**")
        with col2:
            st.write(f"Value: {value}")
        with col3:
            st.write(f"Threshold: {threshold} | {message}")
    
    m4_checks = safe_get(fdata, 'm4_checks', 0)
    m4_total = safe_get(fdata, 'm4_total', 8)
    m4_passed = safe_get(fdata, 'm4_passed', False)
    st.markdown(f"**Result:** {m4_checks}/{m4_total} passed → {'✅ PASS' if m4_passed else '❌ FAIL'}")
    
    st.divider()
    
    # ===== MODULE 5: FORENSIC FAILURES =====
    st.markdown("## M5: Forensic Failures")
    
    m5_failures = safe_get(fdata, 'm5_failures', [])
    for failure in m5_failures:
        col1, col2, col3 = st.columns([2, 0.5, 2.5])
        with col1:
            st.write(f"⚠️ **{failure['name']}**")
        with col2:
            st.write(f"+{failure['points']} pts")
        with col3:
            st.write(f"_{failure['reason']}_")
    
    m5_score = safe_get(fdata, 'm5_score', 0)
    m5_threshold = safe_get(fdata, 'm5_threshold', 4.5)
    m5_passed = safe_get(fdata, 'm5_passed', False)
    st.markdown(f"**Total Failure Score:** {m5_score} / {m5_threshold} → {'✅ PASS' if m5_passed else '❌ FAIL'}")
    
    st.divider()
    
    # ===== MODULE 6: PERSONNEL =====
    st.markdown("## M6: Personnel Forensics")
    
    m6_home = safe_get(fdata, 'm6_home', {})
    m6_away = safe_get(fdata, 'm6_away', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{home}**")
        st.metric("Personnel Score", f"{m6_home.get('score', 50)}/100", m6_home.get('status', 'Unknown'))
        st.write(f"🔑 Key injuries: {m6_home.get('injuries', 'None')}")
        st.write(f"⚡ Fatigue: {m6_home.get('fatigue', 'NORMAL')}")
    with col2:
        st.markdown(f"**{away}**")
        st.metric("Personnel Score", f"{m6_away.get('score', 50)}/100", m6_away.get('status', 'Unknown'))
        st.write(f"🔑 Key injuries: {m6_away.get('injuries', 'None')}")
        st.write(f"⚡ Fatigue: {m6_away.get('fatigue', 'NORMAL')}")
    
    st.divider()
    
    # ===== MODULE 7: AI CONSENSUS =====
    st.markdown("## M7: AI Consensus")
    
    m7_ai = safe_get(fdata, 'm7_ai', [])
    ai_df = pd.DataFrame(m7_ai)
    if not ai_df.empty:
        st.dataframe(ai_df, use_container_width=True, hide_index=True)
    
    # Calculate consensus
    approve_count = sum(1 for a in m7_ai if a.get('verdict') == 'APPROVE')
    total_ai = len(m7_ai) if m7_ai else 1
    st.markdown(f"**Consensus:** {approve_count}/{total_ai} APPROVE → {'✅ APPROVED' if approve_count >= 3 else '⚠️ SPLIT'}")
    
    st.divider()
    
    # ===== MODULE 8: DUAL PATTERN (With Conflict Details) =====
    st.markdown("## M8: Dual Pattern Engine")
    
    m8_data = safe_get(fdata, 'm8_data', {})
    
    if safe_get(fdata, 'm8_conflict', False):
        st.error("🚨 **H2H CONFLICT DETECTED - HARD REJECT**")
        conflict = safe_get(fdata, 'conflict_details', {})
        st.markdown(f"""
        **H2H HISTORY ({conflict.get('h2h_games', 80)} matches):**
        - {home}: {conflict.get('h2h_wr', 46)}% wins
        - Draws: 30%
        - {away}: {100 - conflict.get('h2h_wr', 46) - 30}% wins
        
        **CURRENT SEASON ({conflict.get('current_games', 20)} matches):**
        - {home}: {conflict.get('home_record', 'Poor form')}
        - {away}: {conflict.get('away_record', 'Good form')}
        
        **CONFLICT:** H2H and current season directly contradict each other.
        
        **M8 v6 RULE:** "If ANY conflict detected → HARD REJECT (stake multiplier = 0.0)"
        """)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Dual Risk Level", m8_data.get('dual_risk', 'MEDIUM'))
            st.metric("Pattern Clash Score", f"{m8_data.get('pattern_clash', 0):.2f}")
        with col2:
            st.metric("Underdog Threat", m8_data.get('underdog_threat', 'NONE'))
            st.metric("Resilience Gap", f"{m8_data.get('resilience_gap', 0):+.2f}")
        st.caption(f"Patterns Reliable: {'✅ YES' if m8_data.get('patterns_reliable', False) else '⚠️ NO'}")
    
    st.divider()
    
    # ===== MODULE 9: UNDERDOG SCANNER =====
    st.markdown("## M9: Underdog Scanner")
    
    m9_data = safe_get(fdata, 'm9_data', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Underdog Edge", f"{m9_data.get('underdog_edge', 0):+.1f}%")
        st.metric("Threat Level", m9_data.get('threat_level', 'NONE'))
    with col2:
        st.metric("Pattern Score", f"{m9_data.get('pattern_score', 0)}/100")
        st.metric("Goldmine Qualified", "✅ YES" if m9_data.get('goldmine', False) else "❌ NO")
    
    st.divider()
    
    # ===== MODULE 10: TALLY MATRIX =====
    st.markdown("## M10: Tally Matrix")
    
    m10_data = safe_get(fdata, 'm10_data', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Matrix Useful", "✅ YES" if m10_data.get('matrix_useful', False) else "❌ NO")
        st.metric("Bilateral Prediction", m10_data.get('bilateral', 'UNCERTAIN'))
    with col2:
        st.metric("Bilateral Confidence", m10_data.get('confidence', 'LOW'))
        st.metric("Trap/Value Signal", m10_data.get('trap_signal', 'NONE'))
    
    st.divider()
    
    # ===== MODULE 26: MATCH CONTEXT =====
    st.markdown("## M26: Match Context")
    
    m26_data = safe_get(fdata, 'm26_data', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Match Importance", f"{m26_data.get('importance', 50)}%")
        st.write(f"🏆 Is Rivalry: {'✅ YES' if m26_data.get('is_rivalry', False) else '❌ NO'}")
    with col2:
        st.metric("Home Motivation", m26_data.get('home_motivation', 'NORMAL'))
        st.metric("Away Motivation", m26_data.get('away_motivation', 'NORMAL'))
    
    st.divider()
    
    # ===== MODULE 27: H2H DEEP ANALYSIS =====
    st.markdown("## M27: H2H Deep Analysis")
    
    m27_data = safe_get(fdata, 'm27_data', {})
    col1, col2 = st.columns(2)
    with col1:
        st.metric("H2H Score", f"{m27_data.get('score', 50)}/100", m27_data.get('label', 'NEUTRAL'))
        st.write(f"📊 Games: {m27_data.get('games', 0)} | 🟢 Fav {m27_data.get('fav_wins', 0)} | 🟡 Draw {m27_data.get('draws', 0)} | 🔴 Und {m27_data.get('und_wins', 0)}")
    with col2:
        st.metric("Draw Rate", f"{m27_data.get('draw_rate', 0)}%")
        st.metric("Psychological Block", "✅ YES" if m27_data.get('psychological_block', False) else "❌ NO")
        st.metric("Draw Boost Factor", f"{m27_data.get('draw_boost', 1.00):.2f}x")
    
    st.divider()
    
    # ===== RISK FLAGS =====
    st.markdown("## ⚠️ Risk Flags")
    
    risk_flags = safe_get(fdata, 'risk_flags', [])
    for flag in risk_flags:
        if "CONFLICT" in flag or "HARD REJECT" in flag:
            st.error(flag)
        elif "NEGATIVE EDGE" in flag or "NO VALUE" in flag:
            st.warning(flag)
        else:
            st.info(flag)
    
    st.divider()
    
    # ===== FINAL VERDICT WITH STAKE =====
    st.markdown("## ✅ FINAL VERDICT")
    
    stake = safe_get(fdata, 'stake', 0)
    bankroll = safe_get(fdata, 'bankroll', 1000)
    stake_pct = (stake / bankroll) * 100 if bankroll > 0 else 0
    
    if status == "APPROVED":
        st.success(f"""
        **STATUS: APPROVED**
        - Confidence: {confidence}
        - Model Probability: {prob}%
        - Edge: +{edge}%
        - Kelly Stake: **£{stake:.2f}** ({stake_pct:.2f}% of bankroll)
        - Potential Return: £{stake * odds:.2f}
        - Potential Profit: £{stake * (odds - 1):.2f}
        """)
    elif safe_get(fdata, 'm8_conflict', False):
        st.error(f"""
        **STATUS: REJECTED (H2H CONFLICT)**
        - Model Probability: {prob}%
        - Edge: +{edge}% (would be value)
        - Odds: {odds:.2f}
        
        **M8 v6 Rule:** Conflict = HARD REJECT (stake multiplier = 0.0)
        """)
    elif edge < 0:
        implied = (1/odds * 100) if odds > 0 else 0
        st.warning(f"""
        **STATUS: REJECTED (Negative Edge)**
        - Model Probability: {prob}%
        - Implied Probability: {implied:.1f}%
        - Edge: {edge:+.1f}%
        
        **Reason:** No mathematical value. Market is more confident than our model.
        """)
    else:
        st.info(f"**STATUS: {status}**")
    
    st.divider()
    
    # ===== KELLY CALCULATION =====
    if status == "APPROVED":
        st.markdown("## 📊 Kelly Calculation")
        st.markdown(f"""
        - Raw Kelly Fraction: {safe_get(fdata, 'kelly_raw', 0.085)*100:.2f}%
        - Confidence Scaling: {confidence} → 50% of Kelly
        - Adjusted Kelly: {safe_get(fdata, 'kelly_adj', 0.0335)*100:.2f}%
        - Bankroll: £{bankroll:.0f}
        - **Final Stake: £{stake:.2f}**
        """)

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.title("🎯 MATCH ORACLE")
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    
    if st.session_state.backend_status == "connected":
        st.success(f"✅ BACKEND CONNECTED | {st.session_state.backend_url}")
    else:
        st.error(f"❌ BACKEND OFFLINE | {st.session_state.backend_url}")
    
    st.divider()
    
    # Display fixtures
    st.subheader("🏆 Today's Fixtures")
    
    for fixture in MOCK_FIXTURES:
        fid = fixture.get('id', 0)
        fdata = FORENSIC_DATA.get(fid, {})
        status = fdata.get('status', 'PENDING')
        
        if status == "APPROVED":
            status_icon = "✅"
        elif fdata.get('m8_conflict', False):
            status_icon = "🚨"
        elif fdata.get('edge', 0) < 0:
            status_icon = "⚠️"
        else:
            status_icon = "❓"
        
        col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1, 0.8, 0.8, 1, 0.8])
        
        with col1:
            st.markdown(f"**{status_icon} {fixture.get('home', '?')} vs {fixture.get('away', '?')}**")
        with col2:
            st.write(fixture.get('time', 'TBD'))
        with col3:
            st.write(f"{fixture.get('odds', 0):.2f}")
        with col4:
            edge_val = fixture.get('edge', 0)
            edge_color = "🟢" if edge_val > 0 else "🔴" if edge_val < 0 else "⚪"
            st.write(f"{edge_color} {abs(edge_val):.1f}%")
        with col5:
            st.write(f"{fixture.get('prob', 0)}%")
        with col6:
            if st.button("🔍", key=f"btn_{fixture.get('id', 0)}"):
                st.session_state.selected_fixture = fixture
                navigate_to("forensic")
        st.divider()
    
    # Top Picks
    st.subheader("🏆 Top Picks (Ranked)")
    approved = [f for f in MOCK_FIXTURES if FORENSIC_DATA.get(f.get('id', 0), {}).get('status') == 'APPROVED']
    
    if approved:
        for i, fixture in enumerate(approved, 1):
            fid = fixture.get('id', 0)
            fdata = FORENSIC_DATA.get(fid, {})
            stake = fdata.get('stake', 0)
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
            with col1:
                st.write(f"**#{i} {fixture.get('home', '?')} vs {fixture.get('away', '?')}**")
            with col2:
                st.write(f"{fixture.get('selection', '?')} @ {fixture.get('odds', 0):.2f}")
            with col3:
                st.write(f"{fixture.get('prob', 0)}%")
            with col4:
                st.write(f"Stake: £{stake:.2f}")
            st.divider()
    else:
        st.info("No approved picks for today")

# ========== OTHER PAGES ==========
def show_performance():
    st.title("📈 Performance Metrics")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.dataframe(pd.DataFrame(LEAGUE_STATS), use_container_width=True, hide_index=True)

def show_bankroll():
    st.title("💰 Bankroll Manager")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    fig = px.line(pd.DataFrame(BANKROLL_HISTORY), x="date", y="bankroll", markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_top_picks():
    st.title("🏆 Top Picks")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    for fixture in MOCK_FIXTURES:
        fdata = FORENSIC_DATA.get(fixture.get('id', 0), {})
        if fdata.get('status') == 'APPROVED':
            st.write(f"**{fixture.get('home', '?')} vs {fixture.get('away', '?')}** - {fixture.get('selection', '?')} @ {fixture.get('odds', 0):.2f}")

def show_parlays():
    st.title("🔗 Parlay Builder")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.info("Parlay builder coming soon")

def show_all_legs():
    st.title("📋 All Legs")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    for fixture in MOCK_FIXTURES:
        st.write(f"{fixture.get('home', '?')} vs {fixture.get('away', '?')} - {fixture.get('league', '?')} - {fixture.get('time', 'TBD')}")

def show_countries():
    st.title("🌍 Country Explorer")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.info("Country explorer coming soon")

def show_calendar():
    st.title("📅 Oracle Calendar")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.date_input("Select Date", datetime.now().date())

def show_settings():
    st.title("⚙️ Settings")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.markdown("### Backend Configuration")
    st.text_input("Backend URL", value=st.session_state.backend_url, disabled=True)
    if st.button("Test Connection"):
        check_backend()
        if st.session_state.backend_status == "connected":
            st.success("✅ Connected!")
        else:
            st.error("❌ Not connected")

# ========== MAIN ==========
def main():
    with st.sidebar:
        st.markdown("### 🎯 MATCH ORACLE")
        st.markdown("---")
        
        if st.session_state.backend_status == "connected":
            st.success("🟢 BACKEND ONLINE")
        else:
            st.error("🔴 BACKEND OFFLINE")
        
        st.markdown("---")
        
        st.markdown("**📋 TODAY**")
        if st.button("🏠 Today's Fixtures", use_container_width=True):
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
    
    page = st.session_state.page
    if page == "dashboard":
        show_dashboard()
    elif page == "forensic":
        if st.session_state.selected_fixture:
            show_forensic_report(st.session_state.selected_fixture)
        else:
            navigate_to("dashboard")
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
