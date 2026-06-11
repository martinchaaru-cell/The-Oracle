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

def go_back():
    navigate_to("dashboard")

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.markdown('<p class="gold-header">🎯 Match Oracle</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">Forensic Betting Intelligence | AI-Powered Match Analysis</p>', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    ### Welcome to Match Oracle
    
    This system provides **forensic-level analysis** for football matches using:
    - 10-module verification system
    - Quad-AI consensus intelligence
    - Dual-pattern conflict detection
    - Asymmetric pre-filtering
    
    **How to use:** Click "View Forensic Report" below to see the complete analysis.
    """)
    
    # Match card
    with st.container():
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        
        with col1:
            st.markdown(f"### 🏠 {FORENSIC_DATA['home']}")
            st.markdown(f"**Record:** {FORENSIC_DATA['m1_home_metrics']['wins']}-{FORENSIC_DATA['m1_home_metrics']['draws']}-{FORENSIC_DATA['m1_home_metrics']['losses']}")
            st.markdown(f"**PPG:** {FORENSIC_DATA['m1_home_metrics']['ppg']}")
        
        with col2:
            st.markdown("### VS")
            st.markdown(f"**Odds:** {FORENSIC_DATA['home_odds']}")
        
        with col3:
            st.markdown(f"### ✈️ {FORENSIC_DATA['away']}")
            st.markdown(f"**Record:** {FORENSIC_DATA['m1_away_metrics']['wins']}-{FORENSIC_DATA['m1_away_metrics']['draws']}-{FORENSIC_DATA['m1_away_metrics']['losses']}")
            st.markdown(f"**PPG:** {FORENSIC_DATA['m1_away_metrics']['ppg']}")
        
        with col4:
            st.markdown(f"**Odds:** {FORENSIC_DATA['away_odds']}")
            st.markdown(f"**Draw:** {FORENSIC_DATA['draw_odds']}")
        
        st.markdown("---")
        
        # Verdict banner
        verdict = FORENSIC_DATA['final_verdict']
        if "REJECTED" in verdict:
            st.error(f"🚨 **FINAL VERDICT: {verdict}**")
            st.warning(f"**Reason:** {FORENSIC_DATA['final_reason']}")
            st.info(f"**Recommended Stake:** €{FORENSIC_DATA['final_stake']}")
        else:
            st.success(f"✅ **FINAL VERDICT: {verdict}**")
        
        # View report button
        if st.button("🔬 View Forensic Report", use_container_width=True):
            navigate_to("forensic_report")

# ========== COMPLETE FORENSIC REPORT PAGE ==========
def show_forensic_report():
    d = FORENSIC_DATA
    
    # Header
    st.markdown(f'<p class="gold-header">🔬 {d["home"]} vs {d["away"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="gold-subheader">{d["league"]} | {d["venue"]} | {d["date"]} | Odds: H {d["home_odds"]} | D {d["draw_odds"]} | A {d["away_odds"]}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    
    # ========== MODULE 0 ==========
    st.markdown('<p class="module-header">MODULE 0: GUARDRAIL & DATA INTEGRITY</p>', unsafe_allow_html=True)
    
    st.markdown("**Raw Data Validation**")
    for check in d["m0_checks"]:
        status = "✅ PASS" if check["result"] == "PASS" else "❌ FAIL"
        st.markdown(f"- {check['check']}: {check['value']} → {status}")
    
    st.markdown("**Hard Filters**")
    for f in d["m0_hard_filters"]:
        status = "✅ PASS" if "PASS" in f["result"] else "❌ FAIL"
        st.markdown(f"- {f['filter']}: {status}")
    
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
    st.markdown(f"- All-time (80+ matches): {d['m1_h2h']['all_time']}")
    st.markdown(f"- Last 10 (2016-2026): {d['m1_h2h']['last_10']}")
    st.markdown(f"- Last 6 (2023-2026): {d['m1_h2h']['last_6']}")
    st.markdown(f"**Insight:** {d['m1_h2h']['insight']}")
    
    st.success("**M1 Verdict:** ✅ Leg built successfully")
    
    st.divider()
    
    # ========== MODULE 3 ==========
    st.markdown('<p class="module-header">MODULE 3: PROBABILITY ENGINE</p>', unsafe_allow_html=True)
    
    mo = d["m3_odds_analysis"]
    st.markdown("**Odds Analysis**")
    
    odds_df = pd.DataFrame([
        {"Outcome": d['home'], "Odds": mo['home_odds'], "Implied Prob": f"{mo['home_implied']}%", "Normalized": f"{mo['home_model']}%"},
        {"Outcome": "Draw", "Odds": mo['draw_odds'], "Implied Prob": f"{mo['draw_implied']}%", "Normalized": f"{mo['draw_model']}%"},
        {"Outcome": d['away'], "Odds": mo['away_odds'], "Implied Prob": f"{mo['away_implied']}%", "Normalized": f"{mo['away_model']}%"},
    ])
    st.table(odds_df)
    
    st.markdown(f"**Bookmaker Margin:** {mo['margin']}%")
    
    st.markdown("**Edge Calculation**")
    st.markdown(f"- Model Probability: {mo['away_model']}%")
    st.markdown(f"- Implied Probability (1/{mo['away_odds']}): {mo['away_implied']}%")
    st.warning(f"**Edge: {mo['edge']:+}% (NEGATIVE)**")
    
    st.info("**M3 Verdict:** ⚠️ Negative edge detected")
    
    st.divider()
    
    # ========== MODULE 4 ==========
    st.markdown('<p class="module-header">MODULE 4: ASYMMETRIC PRE-FILTER</p>', unsafe_allow_html=True)
    
    st.markdown("**Check Results**")
    for c in d["m4_checks"]:
        status = "✅ PASS" if c["passed"] else "❌ FAIL"
        st.markdown(f"- {c['check']}: {c['value']} (Threshold: {c['threshold']}) → {status} | {c['points']} pts")
    
    st.success(f"**Passed:** {d['m4_passed']}/{d['m4_total']} → ✅ PASS")
    
    st.divider()
    
    # ========== MODULE 5 ==========
    st.markdown('<p class="module-header">MODULE 5: FORENSIC CHECKS</p>', unsafe_allow_html=True)
    
    for f in d["m5_failures"]:
        st.markdown(f"- {f['name']}: +{f['points']} pts")
    st.success(f"**TOTAL:** {d['m5_total']} / {d['m5_threshold']} → ✅ PASS")
    
    st.divider()
    
    # ========== MODULE 6 ==========
    st.markdown('<p class="module-header">MODULE 6: PERSONNEL FORENSICS</p>', unsafe_allow_html=True)
    
    st.markdown("**Injuries & Suspensions**")
    for inj in d["m6_injuries"]:
        st.markdown(f"- {inj['team']}: {inj['player']} ({inj['position']}) - {inj['reason']} - {inj['status']}")
    
    st.markdown(f"**Personnel Scores:** {d['home']}: {d['m6_scores']['Derry City']}/100 | {d['away']}: {d['m6_scores']['Bohemians FC']}/100")
    st.info("**M6 Verdict:** ⚠️ Personnel edge to Derry (Bohemians missing GK is significant)")
    
    st.divider()
    
    # ========== MODULE 7 ==========
    st.markdown('<p class="module-header">MODULE 7: QUAD-AI INTELLIGENCE</p>', unsafe_allow_html=True)
    
    for ai in d["m7_ai"]:
        st.markdown(f"- **{ai['provider']}**: {ai['verdict']} ({ai['confidence']} confidence) - {ai['reasoning']}")
    
    st.markdown(f"**Consensus:** {d['m7_consensus']} (Agreement: {d['m7_agreement']}%)")
    st.info("**M7 Verdict:** ⚠️ CAUTION (split decision)")
    
    st.divider()
    
    # ========== MODULE 8 ==========
    st.markdown('<p class="module-header">MODULE 8: DUAL PATTERN ENGINE (v6)</p>', unsafe_allow_html=True)
    
    st.markdown("**H2H vs Current Season CONFLICT DETECTION**")
    st.markdown(f"- H2H all-time: {d['home']} DOMINANT ({d['m8_h2h_all_time']['derry']}% vs {d['m8_h2h_all_time']['bohemians']}%)")
    st.markdown(f"- H2H recent (last 6): {d['home']} still leads ({d['m8_h2h_last6']['derry']}% vs {d['m8_h2h_last6']['bohemians']}%)")
    st.markdown(f"- Current season: {d['away']} DOMINANT ({d['m8_current_season']['bohemians']}% vs {d['m8_current_season']['derry']}%)")
    st.error(f"**Conflict severity:** {d['m8_severity']}")
    
    st.error("**🚨 CONFLICT DETECTED**")
    st.markdown("**M8 v6 Rule:** *If ANY conflict detected → HARD REJECT (stake multiplier = 0.0)*")
    st.error(f"**M8 Verdict:** 🚨 {d['m8_verdict']}")
    
    st.divider()
    
    # ========== MODULE 9 ==========
    st.markdown('<p class="module-header">MODULE 9: UNDERDOG SCANNER</p>', unsafe_allow_html=True)
    
    st.markdown(f"- Underdog Edge: {d['m9_underdog_edge']:+}%")
    st.markdown(f"- Threat Level: {d['m9_threat_level']}")
    st.markdown(f"- Goldmine Qualified: {'Yes' if d['m9_goldmine'] else 'No'}")
    st.info("**M9 Verdict:** ⚠️ Low underdog threat")
    
    st.divider()
    
    # ========== MODULE 10 ==========
    st.markdown('<p class="module-header">MODULE 10: SEASON TALLY MATRIX</p>', unsafe_allow_html=True)
    
    st.markdown("**Bilateral Intersection**")
    matrix_df = pd.DataFrame([
        {"Outcome": d['home'], "Probability": f"{d['m10_bilateral']['home']}%"},
        {"Outcome": "Draw", "Probability": f"{d['m10_bilateral']['draw']}%"},
        {"Outcome": d['away'], "Probability": f"{d['m10_bilateral']['away']}%"},
    ])
    st.table(matrix_df)
    
    st.markdown(f"**Confidence:** {d['m10_confidence']}")
    st.markdown(f"**Trap/Value Signal:** {d['m10_trap_signal']}")
    st.info("**M10 Verdict:** ⚠️ No value detected")
    
    st.divider()
    
    # ========== FINAL VERDICT ==========
    st.markdown('<p class="module-header">FINAL VERDICT</p>', unsafe_allow_html=True)
    
    st.error(f"**Verdict:** {d['final_verdict']}")
    st.warning(f"**Recommended Stake:** €{d['final_stake']}")
    st.info(f"**Reasoning:** {d['final_reason']}")
    
    st.divider()
    
    # Summary table
    st.markdown("### Module Summary")
    summary_data = {
        "Module": ["M0", "M1", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10"],
        "Status": ["✅ PASS", "✅ PASS", "⚠️ EDGE", "✅ PASS", "✅ PASS", "⚠️ CAUTION", "⚠️ CAUTION", "🚨 REJECT", "⚠️ LOW", "⚠️ NO VALUE"],
        "Description": [
            "Data integrity passed",
            "Stats ingested",
            "Negative edge",
            "7/8 checks passed",
            "Below threshold",
            "Personnel concerns",
            "Split decision",
            "CONFLICT DETECTED",
            "Low underdog threat",
            "No value found"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)

# ========== MAIN ROUTING ==========
if st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "forensic_report":
    show_forensic_report()
