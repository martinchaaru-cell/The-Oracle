import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import os
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
    .gold-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FFD700;
        margin-bottom: 0;
        margin-top: -20px;
    }
    .gold-subheader {
        font-size: 0.8rem;
        color: #B8860B;
        margin-bottom: 1rem;
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
    .verdict-pass {
        color: #00FF88;
        font-weight: bold;
    }
    .verdict-fail {
        color: #FF4444;
        font-weight: bold;
    }
    .verdict-warn {
        color: #FFA500;
        font-weight: bold;
    }
    .verdict-reject {
        color: #FF4444;
        font-weight: bold;
    }
    hr {
        margin: 10px 0;
        border-color: #333;
    }
    .data-table {
        font-size: 0.8rem;
        width: 100%;
    }
    .data-table td {
        padding: 4px 8px;
    }
    .check-pass {
        color: #00FF88;
    }
    .check-fail {
        color: #FF4444;
    }
    .nav-button {
        width: 100%;
        margin: 5px 0;
    }
    .sidebar-content {
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

# ========== COMPLETE FORENSIC DATA ==========
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
    
    # M0 Data
    "m0_checks": [
        {"check": "Fixture Status", "value": "NS (upcoming)", "result": "PASS"},
        {"check": "Goals present", "value": "None (NS fixture)", "result": "PASS"},
        {"check": "Odds present", "value": "2.90/3.20/2.36", "result": "PASS"},
        {"check": "Odds bounds", "value": "All >1.01, <100", "result": "PASS"},
        {"check": "Fixture ID", "value": "Present", "result": "PASS"},
        {"check": "Team IDs", "value": "Derry City, Bohemians FC", "result": "PASS"},
        {"check": "Competition type", "value": "League", "result": "PASS"},
    ],
    "m0_hard_filters": [
        {"filter": "Senior Men's League", "result": "PASS"},
        {"filter": "League Tier", "result": "PASS (Ireland Tier 1)"},
        {"filter": "Format (Playoff/Knockout)", "result": "PASS"},
        {"filter": "Maturity (≥10 games)", "result": "PASS (20 games each)"},
    ],
    
    # M1 Data
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
        "insight": "Derry City has HISTORICAL dominance (46% wins vs 24%), but recent H2H is balanced with many draws (50% in last 6)"
    },
    
    # M3 Probability
    "m3_odds_analysis": {
        "home_odds": 2.90, "home_implied": 34.5, "home_model": 30,
        "draw_odds": 3.20, "draw_implied": 31.3, "draw_model": 30,
        "away_odds": 2.36, "away_implied": 42.4, "away_model": 40,
        "margin": 8.2, "edge": -2.4
    },
    
    # M4 Checks
    "m4_checks": [
        {"check": "C1: Season Win Gap", "passed": True, "value": "+5 wins", "threshold": "≥3", "points": 10},
        {"check": "C2: Venue Win Gap", "passed": True, "value": "+30%", "threshold": "≥15%", "points": 10},
        {"check": "C3: H2H Favoured", "passed": False, "value": "24%", "threshold": "≥50%", "points": 0},
        {"check": "C4: Transition Favours", "passed": True, "value": "~50%", "threshold": ">45%", "points": 8},
        {"check": "C5: Bounce-back Rate", "passed": True, "value": "~48%", "threshold": ">45%", "points": 8},
        {"check": "C6: Ceiling Proximity", "passed": True, "value": "45%", "threshold": "≤88%", "points": 10},
        {"check": "C7: Momentum Gap", "passed": True, "value": "+40%", "threshold": "≥20%", "points": 10},
        {"check": "C8: Resilience Gap", "passed": True, "value": "+0.55", "threshold": "≥0.10", "points": 10},
    ],
    "m4_passed": 7, "m4_total": 8,
    
    # M5 Failures
    "m5_failures": [
        {"name": "Low Season Win Count (Derry)", "points": 0.5},
        {"name": "Low Home Wins at Venue (Derry)", "points": 1.0},
        {"name": "Marginal Home Win Probability", "points": 0.5},
        {"name": "Elevated Away Win Risk", "points": 0.5},
    ],
    "m5_total": 2.5, "m5_threshold": 4.5,
    
    # M6 Personnel
    "m6_injuries": [
        {"team": "Derry City", "player": "P. McClean", "position": "D", "reason": "Yellow Card Suspension", "status": "OUT"},
        {"team": "Bohemians FC", "player": "B. Maher", "position": "G", "reason": "Wrist Fracture", "status": "OUT"},
        {"team": "Bohemians FC", "player": "B. Fleming", "position": "D", "reason": "Yellow Card Suspension", "status": "OUT"},
    ],
    "m6_scores": {"Derry City": 55, "Bohemians FC": 45},
    
    # M7 AI
    "m7_ai": [
        {"provider": "DeepSeek", "verdict": "CAUTION", "confidence": "MEDIUM", "reasoning": "Bohemians form strong but H2H favours Derry"},
        {"provider": "Claude", "verdict": "CAUTION", "confidence": "LOW", "reasoning": "Missing GK for Bohemians is concern"},
        {"provider": "Gemini", "verdict": "APPROVE", "confidence": "LOW", "reasoning": "Bohemians league position dominant"},
        {"provider": "GPT", "verdict": "REJECT", "confidence": "LOW", "reasoning": "H2H conflict, personnel issues"},
    ],
    "m7_consensus": "CAUTION", "m7_agreement": 25,
    
    # M8 Conflict
    "m8_h2h_all_time": {"derry": 46, "draw": 30, "bohemians": 24},
    "m8_h2h_last6": {"derry": 33, "draw": 50, "bohemians": 17},
    "m8_current_season": {"derry": 20, "bohemians": 45},
    "m8_conflict_detected": True,
    "m8_severity": "HIGH",
    "m8_verdict": "HARD REJECT",
    
    # M9 Underdog
    "m9_underdog_edge": -5,
    "m9_threat_level": "LOW",
    "m9_goldmine": False,
    
    # M10 Matrix
    "m10_bilateral": {"home": 28, "draw": 32, "away": 40},
    "m10_confidence": "LOW",
    "m10_trap_signal": "NONE",
    
    # Final
    "final_verdict": "REJECTED (H2H CONFLICT)",
    "final_stake": 0.00,
    "final_reason": "H2H conflict between historical dominance (Derry) and current form (Bohemians) makes this fixture unpredictable. Even without conflict, odds offer negative edge."
}

# Additional matches data for the matches page
ALL_MATCHES = [
    {
        "match_id": 1,
        "home": "Derry City",
        "away": "Bohemians FC",
        "league": "Ireland Premier League",
        "date": "June 12, 2026",
        "home_odds": 2.90,
        "draw_odds": 3.20,
        "away_odds": 2.36,
        "final_verdict": "REJECTED",
        "confidence": "LOW"
    },
    {
        "match_id": 2,
        "home": "Shamrock Rovers",
        "away": "Dundalk FC",
        "league": "Ireland Premier League",
        "date": "June 13, 2026",
        "home_odds": 1.85,
        "draw_odds": 3.40,
        "away_odds": 4.20,
        "final_verdict": "APPROVED",
        "confidence": "HIGH"
    },
    {
        "match_id": 3,
        "home": "Cork City",
        "away": "St Patrick's",
        "league": "Ireland Premier League",
        "date": "June 14, 2026",
        "home_odds": 2.50,
        "draw_odds": 3.10,
        "away_odds": 2.80,
        "final_verdict": "CAUTION",
        "confidence": "MEDIUM"
    }
]

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None
if "selected_match_id" not in st.session_state:
    st.session_state.selected_match_id = None

def navigate_to(page, match=None, match_id=None):
    st.session_state.page = page
    if match:
        st.session_state.selected_match = match
    if match_id:
        st.session_state.selected_match_id = match_id
    st.rerun()

def go_back():
    navigate_to("dashboard")

# ========== SIDEBAR NAVIGATION ==========
def sidebar_navigation():
    with st.sidebar:
        st.markdown("## 🎯 Match Oracle")
        st.markdown("---")
        
        # Navigation Buttons
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
            navigate_to("dashboard")
        
        if st.button("🔬 Forensic Report", use_container_width=True, key="nav_forensic"):
            if st.session_state.selected_match_id:
                navigate_to("forensic_report", match_id=st.session_state.selected_match_id)
            else:
                navigate_to("forensic_report")
        
        if st.button("📋 All Matches", use_container_width=True, key="nav_matches"):
            navigate_to("matches")
        
        if st.button("📈 Performance", use_container_width=True, key="nav_performance"):
            navigate_to("performance")
        
        if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
            navigate_to("settings")
        
        st.markdown("---")
        
        # System Status
        st.markdown("### System Status")
        st.markdown("✅ AI Engine: Active")
        st.markdown("✅ Data Feed: Connected")
        st.markdown(f"🕐 Local Time: {datetime.now(NAIROBI_TZ).strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Version Info
        st.markdown("**Version:** 2.0.0")
        st.markdown("**Last Update:** June 2026")

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    d = FORENSIC_DATA
    
    st.markdown(f'<p class="gold-header">🎯 Match Oracle Dashboard</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="gold-subheader">Forensic Betting Intelligence | AI-Powered Match Analysis</p>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Matches", len(ALL_MATCHES), delta="+2")
    with col2:
        st.metric("Approval Rate", "33%", delta="+5%")
    with col3:
        st.metric("AI Confidence", "MEDIUM", delta="Stable")
    with col4:
        st.metric("Total Value", "€0.00", delta="No active bets")
    
    st.divider()
    
    # Featured Match Card
    st.markdown("### 🔥 Featured Match")
    
    col1, col2, col3 = st.columns([2,1,2])
    with col1:
        st.markdown(f"### 🏠 {d['home']}")
        st.metric("League Position", "8th", delta="-2")
        st.metric("PPG", d['m1_home_metrics']['ppg'])
        st.metric("Recent Form", d['m1_home_metrics']['recent_form'])
        st.metric("Home Record", d['m1_home_metrics']['home_record'])
    with col2:
        st.markdown("### VS")
        st.markdown(f"**Odds**")
        st.markdown(f"🏠 **{d['home_odds']}**")
        st.markdown(f"🤝 **{d['draw_odds']}**")
        st.markdown(f"✈️ **{d['away_odds']}**")
        st.markdown("---")
        st.markdown(f"**Verdict:** {d['final_verdict']}")
    with col3:
        st.markdown(f"### ✈️ {d['away']}")
        st.metric("League Position", "2nd", delta="+5")
        st.metric("PPG", d['m1_away_metrics']['ppg'])
        st.metric("Recent Form", d['m1_away_metrics']['recent_form'])
        st.metric("Away Record", d['m1_away_metrics']['away_record'])
    
    st.divider()
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("H2H (All Time)", "Derry 46%", delta="Historical Edge")
    with col2:
        st.metric("H2H (Last 6)", "Draw 50%", delta="Recent Pattern")
    with col3:
        st.metric("AI Consensus", d['m7_consensus'], delta=f"{d['m7_agreement']}% agreement")
    with col4:
        st.metric("Module Status", f"{d['m4_passed']}/8 Passed", delta="M4 Filter")
    
    st.divider()
    
    # Recent Matches Table
    st.markdown("### 📋 Recent Matches")
    
    matches_df = pd.DataFrame(ALL_MATCHES)
    matches_df = matches_df[["home", "away", "league", "date", "final_verdict", "confidence"]]
    st.dataframe(matches_df, use_container_width=True)
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔬 View Full Forensic Report", use_container_width=True):
            navigate_to("forensic_report", match_id=1)
    with col2:
        if st.button("📋 View All Matches", use_container_width=True):
            navigate_to("matches")
    
    st.divider()
    
    # AI Insights
    st.markdown("### 🤖 AI Insights")
    st.info("🔍 **DeepSeek:** Bohemians form strong but H2H favours Derry - CAUTION advised")
    st.warning("⚠️ **Claude:** Missing GK for Bohemians is a significant concern")
    st.success("💡 **Gemini:** Bohemians league position dominant, but historical data conflicts")
    st.error("🚨 **GPT:** H2H conflict and personnel issues suggest REJECT")

# ========== FORENSIC REPORT PAGE ==========
def show_forensic_report():
    d = FORENSIC_DATA
    
    # Header
    st.markdown(f'<p class="gold-header">🔬 Forensic Report: {d["home"]} vs {d["away"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="gold-subheader">{d["league"]} | {d["venue"]} | {d["date"]} | Odds: H {d["home_odds"]} | D {d["draw_odds"]} | A {d["away_odds"]}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    
    # ========== MODULE 0 ==========
    st.markdown('<p class="module-header">MODULE 0: GUARDRAIL & DATA INTEGRITY</p>', unsafe_allow_html=True)
    
    st.markdown("**Raw Data Validation**")
    for check in d["m0_checks"]:
        status = "✅ PASS" if check["result"] == "PASS" else "❌ FAIL"
        st.markdown(f"| {check['check']} | {check['value']} | {status} |")
    
    st.markdown("**Hard Filters**")
    for f in d["m0_hard_filters"]:
        status = "✅ PASS" if "PASS" in f["result"] else "❌ FAIL"
        st.markdown(f"| {f['filter']} | {status} |")
    
    st.success("**M0 Verdict:** ✅ PASS")
    
    st.divider()
    
    # ========== MODULE 1 ==========
    st.markdown('<p class="module-header">MODULE 1: DATA INGESTION</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{d['home']} (Home)**")
        hm = d["m1_home_metrics"]
        st.markdown(f"Games: {hm['games']} | W-D-L: {hm['wins']}-{hm['draws']}-{hm['losses']}")
        st.markdown(f"Goals: {hm['goals_for']}/{hm['goals_against']} (GD: {hm['goals_for'] - hm['goals_against']})")
        st.markdown(f"Home Record: {hm['home_record']} ({hm['home_wr']}% WR)")
        st.markdown(f"Recent Form: {hm['recent_form']}")
        st.markdown(f"PPG: {hm['ppg']} | Clean Sheets: {hm['clean_sheets']}/20")
    with col2:
        st.markdown(f"**{d['away']} (Away)**")
        am = d["m1_away_metrics"]
        st.markdown(f"Games: {am['games']} | W-D-L: {am['wins']}-{am['draws']}-{am['losses']}")
        st.markdown(f"Goals: {am['goals_for']}/{am['goals_against']} (GD: {am['goals_for'] - am['goals_against']})")
        st.markdown(f"Away Record: {am['away_record']} ({am['away_wr']}% WR)")
        st.markdown(f"Recent Form: {am['recent_form']}")
        st.markdown(f"PPG: {am['ppg']} | Clean Sheets: {am['clean_sheets']}/20")
    
    st.markdown("**H2H Record**")
    st.markdown(f"All-time (80+ matches): {d['m1_h2h']['all_time']}")
    st.markdown(f"Last 10 (2016-2026): {d['m1_h2h']['last_10']}")
    st.markdown(f"Last 6 (2023-2026): {d['m1_h2h']['last_6']}")
    st.markdown(f"**Insight:** {d['m1_h2h']['insight']}")
    
    st.success("**M1 Verdict:** ✅ Leg built successfully")
    
    st.divider()
    
    # ========== MODULE 3 ==========
    st.markdown('<p class="module-header">MODULE 3: PROBABILITY ENGINE</p>', unsafe_allow_html=True)
    
    mo = d["m3_odds_analysis"]
    st.markdown("**Odds Analysis**")
    st.markdown(f"| Outcome | Odds | Implied Prob | Normalized |")
    st.markdown(f"| {d['home']} (H) | {mo['home_odds']} | {mo['home_implied']}% | {mo['home_model']}% |")
    st.markdown(f"| Draw | {mo['draw_odds']} | {mo['draw_implied']}% | {mo['draw_model']}% |")
    st.markdown(f"| {d['away']} (A) | {mo['away_odds']} | {mo['away_implied']}% | {mo['away_model']}% |")
    st.markdown(f"**Bookmaker Margin:** {mo['margin']}%")
    
    st.markdown("**Edge Calculation**")
    st.markdown(f"Model Probability: {mo['away_model']}%")
    st.markdown(f"Implied Probability (1/{mo['away_odds']}): {mo['away_implied']}%")
    st.warning(f"**Edge: {mo['edge']:+}% (NEGATIVE)**")
    
    st.info("**M3 Verdict:** ⚠️ Negative edge detected")
    
    st.divider()
    
    # ========== MODULE 4 ==========
    st.markdown('<p class="module-header">MODULE 4: ASYMMETRIC PRE-FILTER</p>', unsafe_allow_html=True)
    
    st.markdown("**Check Results**")
    for c in d["m4_checks"]:
        status = "✅ PASS" if c["passed"] else "❌ FAIL"
        st.markdown(f"| {c['check']} | Value: {c['value']} | Threshold: {c['threshold']} | {status} | {c['points']} pts |")
    
    st.success(f"**Passed:** {d['m4_passed']}/{d['m4_total']} → ✅ PASS")
    
    st.divider()
    
    # ========== MODULE 5 ==========
    st.markdown('<p class="module-header">MODULE 5: FORENSIC CHECKS</p>', unsafe_allow_html=True)
    
    for f in d["m5_failures"]:
        st.markdown(f"| {f['name']} | +{f['points']} pts |")
    st.success(f"**TOTAL:** {d['m5_total']} / {d['m5_threshold']} → ✅ PASS")
    
    st.divider()
    
    # ========== MODULE 6 ==========
    st.markdown('<p class="module-header">MODULE 6: PERSONNEL FORENSICS</p>', unsafe_allow_html=True)
    
    st.markdown("**Injuries & Suspensions**")
    for inj in d["m6_injuries"]:
        st.markdown(f"| {inj['team']} | {inj['player']} ({inj['position']}) | {inj['reason']} | {inj['status']} |")
    
    st.markdown(f"**Personnel Scores:** {d['home']}: {d['m6_scores']['Derry City']}/100 | {d['away']}: {d['m6_scores']['Bohemians FC']}/100")
    st.info("**M6 Verdict:** ⚠️ Personnel edge to Derry (Bohemians missing GK is significant)")
    
    st.divider()
    
    # ========== MODULE 7 ==========
    st.markdown('<p class="module-header">MODULE 7: QUAD-AI INTELLIGENCE</p>', unsafe_allow_html=True)
    
    for ai in d["m7_ai"]:
        st.markdown(f"| {ai['provider']} | {ai['verdict']} | {ai['confidence']} | {ai['reasoning']} |")
    
    st.markdown(f"**Consensus:** {d['m7_consensus']} (Agreement: {d['m7_agreement']}%)")
    st.info("**M7 Verdict:** ⚠️ CAUTION (split decision)")
    
    st.divider()
    
    # ========== MODULE 8 ==========
    st.markdown('<p class="module-header">MODULE 8: DUAL PATTERN ENGINE (v6)</p>', unsafe_allow_html=True)
    
    st.markdown("**H2H vs Current Season CONFLICT DETECTION**")
    st.markdown(f"| Signal | Value |")
    st.markdown(f"| H2H all-time | {d['home']} DOMINANT ({d['m8_h2h_all_time']['derry']}% vs {d['m8_h2h_all_time']['bohemians']}%) |")
    st.markdown(f"| H2H recent (last 6) | {d['home']} still leads ({d['m8_h2h_last6']['derry']}% vs {d['m8_h2h_last6']['bohemians']}%) |")
    st.markdown(f"| Current season | {d['away']} DOMINANT ({d['m8_current_season']['bohemians']}% vs {d['m8_current_season']['derry']}%) |")
    st.error(f"**Conflict severity:** {d['m8_severity']}")
    
    st.error("**🚨 CONFLICT DETECTED**")
    st.markdown("**M8 v6 Rule:** *If ANY conflict detected → HARD REJECT (stake multiplier = 0.0)*")
    st.error(f"**M8 Verdict:** 🚨 {d['m8_verdict']}")
    
    st.divider()
    
    # ========== MODULE 9 ==========
    st.markdown('<p class="module-header">MODULE 9: UNDERDOG SCANNER</p>', unsafe_allow_html=True)
    
    st.markdown(f"Underdog Edge: {d['m9_underdog_edge']:+}%")
    st.markdown(f"Threat Level: {d['m9_threat_level']}")
    st.markdown(f"Goldmine Qualified: {'Yes' if d['m9_goldmine'] else 'No'}")
    st.info("**M9 Verdict:** ⚠️ Low underdog threat")
    
    st.divider()
    
    # ========== MODULE 10 ==========
    st.markdown('<p class="module-header">MODULE 10: SEASON TALLY MATRIX</p>', unsafe_allow_html=True)
    
    st.markdown("**Bilateral Intersection**")
    st.markdown(f"| Outcome | Probability |")
    st.markdown(f"| {d['home']} Win | {d['m10_bilateral']['home']}% |")
    st.markdown(f"| Draw | {d['m10_bilateral']['draw']}% |")
    st.markdown(f"| {d['away']} Win | {d['m10_bilateral']['away']}% |")
    st.markdown(f"**Confidence:** {d['m10_confidence']}")
    st.markdown(f"**Trap/Value Signal:** {d['m10_trap_signal']}")
    st.info("**M10 Verdict:** ⚠️ No value detected")
    
    st.divider()
    
    # ========== FINAL VERDICT ==========
    st.markdown('<p class="module-header">FINAL VERDICT</p>', unsafe_allow_html=True)
    
    st.error(f"**Verdict:** {d['final_verdict']}")
    st.warning(f"**Recommended Stake:** €{d['final_stake']}")
    st.info(f"**Reasoning:** {d['final_reason']}")

# ========== ALL MATCHES PAGE ==========
def show_matches():
    st.markdown('<p class="gold-header">📋 All Matches</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">Browse and analyze all available fixtures</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    
    # Display matches in a grid
    for match in ALL_MATCHES:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
            
            with col1:
                st.markdown(f"**🏠 {match['home']}**")
                st.markdown(f"*{match['league']}*")
            
            with col2:
                st.markdown(f"**VS**")
                st.markdown(f"Odds: {match['home_odds']}")
            
            with col3:
                st.markdown(f"**✈️ {match['away']}**")
                st.markdown(f"{match['date']}")
            
            with col4:
                verdict_color = "🟢" if match['final_verdict'] == "APPROVED" else "🟡" if match['final_verdict'] == "CAUTION" else "🔴"
                st.markdown(f"{verdict_color} **{match['final_verdict']}**")
                st.markdown(f"Confidence: {match['confidence']}")
                if st.button(f"Analyze", key=f"btn_{match['match_id']}"):
                    navigate_to("forensic_report", match_id=match['match_id'])
            
            st.divider()

# ========== PERFORMANCE PAGE ==========
def show_performance():
    st.markdown('<p class="gold-header">📈 Performance Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">System performance and betting history</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    
    # Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Bets", "0", delta="No active bets")
    with col2:
        st.metric("Win Rate", "0%", delta="No data")
    with col3:
        st.metric("ROI", "0%", delta="No data")
    with col4:
        st.metric("Profit/Loss", "€0", delta="No data")
    
    st.divider()
    
    # Historical Performance Chart (Placeholder)
    st.markdown("### Historical Performance")
    
    # Sample data for chart
    performance_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Bets': [0, 0, 0, 0, 0, 0],
        'Wins': [0, 0, 0, 0, 0, 0]
    })
    
    fig = px.line(performance_data, x='Month', y=['Bets', 'Wins'], 
                  title='Monthly Betting Activity',
                  labels={'value': 'Count', 'variable': 'Metric'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # System Accuracy
    st.markdown("### System Accuracy Metrics")
    st.info("📊 **AI Model Accuracy:** 0% (Insufficient data)")
    st.info("🎯 **Module 4 Filter Accuracy:** 0%")
    st.info("🤖 **Quad-AI Consensus Accuracy:** 0%")
    
    st.divider()
    
    # Recent Activity
    st.markdown("### Recent Activity")
    st.write("No recent betting activity to display.")

# ========== SETTINGS PAGE ==========
def show_settings():
    st.markdown('<p class="gold-header">⚙️ Settings</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">Configure system parameters and preferences</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    
    # System Settings
    st.markdown("### System Configuration")
    
    # AI Settings
    st.markdown("#### AI Intelligence Settings")
    ai_consensus_threshold = st.slider("AI Consensus Threshold (%)", 0, 100, 60)
    st.checkbox("Enable DeepSeek Analysis", value=True)
    st.checkbox("Enable Claude Analysis", value=True)
    st.checkbox("Enable Gemini Analysis", value=True)
    st.checkbox("Enable GPT Analysis", value=True)
    
    st.divider()
    
    # Filter Settings
    st.markdown("#### Filter Configuration")
    m4_threshold = st.slider("Module 4 Pass Threshold (out of 8)", 1, 8, 6)
    m5_threshold = st.slider("Module 5 Failure Threshold (points)", 0.0, 10.0, 4.5)
    
    st.divider()
    
    # Stake Settings
    st.markdown("#### Stake Management")
    base_stake = st.number_input("Base Stake (€)", min_value=0.0, max_value=1000.0, value=10.0)
    max_stake = st.number_input("Maximum Stake (€)", min_value=0.0, max_value=10000.0, value=100.0)
    
    st.divider()
    
    # Notification Settings
    st.markdown("#### Notifications")
    st.checkbox("Email notifications for new matches", value=True)
    st.checkbox("Push notifications for bet approvals", value=True)
    email = st.text_input("Notification Email", placeholder="your@email.com")
    
    st.divider()
    
    # Save Button
    if st.button("Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")

# ========== MAIN ROUTING ==========
# Display sidebar navigation
sidebar_navigation()

# Main content routing
if st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "forensic_report":
    show_forensic_report()
elif st.session_state.page == "matches":
    show_matches()
elif st.session_state.page == "performance":
    show_performance()
elif st.session_state.page == "settings":
    show_settings()
