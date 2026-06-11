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

# ========== MOCK DATA ==========
MOCK_FIXTURES = [
    {"id": 1, "home": "Wexford Youths", "away": "Cork City", "league": "League of Ireland", "time": "19:45", "odds": 1.73, "status": "NS", "prob": 62, "edge": 4.2, "confidence": "HIGH", "selection": "Cork City"},
    {"id": 2, "home": "Derry City", "away": "Bohemians FC", "league": "League of Ireland", "time": "19:45", "odds": 2.36, "status": "NS", "prob": 54, "edge": 2.3, "confidence": "HIGH", "selection": "Bohemians FC"},
    {"id": 3, "home": "Shamrock Rovers", "away": "Shelbourne FC", "league": "League of Ireland", "time": "19:45", "odds": 1.33, "status": "NS", "prob": 68, "edge": -7.2, "confidence": "HIGH", "selection": "Shamrock Rovers"},
    {"id": 4, "home": "Treaty United", "away": "Bray Wanderers", "league": "League of Ireland", "time": "19:45", "odds": 1.79, "status": "NS", "prob": 54, "edge": -1.9, "confidence": "MEDIUM", "selection": "Bray Wanderers"},
    {"id": 5, "home": "Finn Harps", "away": "UCD Dublin", "league": "League of Ireland", "time": "19:45", "odds": 1.85, "status": "NS", "prob": 53, "edge": -1.1, "confidence": "MEDIUM", "selection": "UCD Dublin"},
    {"id": 6, "home": "Waterford", "away": "Sligo Rovers", "league": "League of Ireland", "time": "19:45", "odds": 2.50, "status": "NS", "prob": 36, "edge": 3.2, "confidence": "LOW", "selection": "Sligo Rovers"},
]

# Mock forensic data for each fixture
FORENSIC_DATA = {
    1: {  # Wexford vs Cork City (APPROVED)
        "status": "APPROVED",
        "m4_passed": True, "m4_checks": 6, "m4_total": 8,
        "m5_score": 2.5, "m5_threshold": 4.5,
        "m8_conflict": False,
        "edge": 4.2, "prob": 62, "odds": 1.73,
        "stake": 33.50, "bankroll": 1000,
        "reason": "Clear value: model 62% vs implied 58%",
        "h2h_conflict": False,
        "current_season_wr": 45, "h2h_wr": 38,
        "kelly_raw": 0.085, "kelly_adj": 0.0335,
    },
    2: {  # Derry vs Bohemians (CONFLICT REJECT)
        "status": "REJECTED",
        "m4_passed": True, "m4_checks": 6, "m4_total": 8,
        "m5_score": 2.5, "m5_threshold": 4.5,
        "m8_conflict": True, "m8_severity": "HIGH",
        "edge": 2.3, "prob": 54, "odds": 2.36,
        "stake": 0, "bankroll": 1000,
        "reason": "H2H CONFLICT: Historical favours Derry, current season favours Bohemians",
        "h2h_conflict": True,
        "current_season_wr": 45, "h2h_wr": 46,
        "conflict_details": "H2H history (80+ matches): Derry 46% wins | Current season: Bohemians 45% WR",
    },
    3: {  # Shamrock vs Shelbourne (NEGATIVE EDGE)
        "status": "REJECTED",
        "m4_passed": True, "m4_checks": 6, "m4_total": 8,
        "m5_score": 2.5, "m5_threshold": 4.5,
        "m8_conflict": False,
        "edge": -7.2, "prob": 68, "odds": 1.33,
        "stake": 0, "bankroll": 1000,
        "reason": "Negative edge: model 68% vs market 75% (implied)",
        "h2h_conflict": False,
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

# ========== CHECK BACKEND ==========
def check_backend():
    connected, data = test_backend_connection(st.session_state.backend_url)
    st.session_state.backend_status = "connected" if connected else "disconnected"

if st.session_state.backend_status == "checking":
    check_backend()

# ========== PAGE ROUTING ==========
def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def go_back():
    navigate_to("dashboard")

# ========== FORENSIC REPORT PAGE (DETAILED) ==========
def show_forensic_report(fixture):
    fid = fixture['id']
    fdata = FORENSIC_DATA.get(fid, {})
    
    # Header
    st.title(f"🔬 {fixture['home']} vs {fixture['away']}")
    st.caption(f"{fixture['league']} | Kickoff: {fixture['time']} | Selection: {fixture['selection']} @ {fixture['odds']:.2f}")
    
    if st.button("← Back to Fixtures"):
        go_back()
    
    st.divider()
    
    # Status Banner
    if fdata.get("status") == "APPROVED":
        st.success("✅ QUALIFIED - RECOMMENDED BET")
    elif fdata.get("m8_conflict"):
        st.error("🚨 H2H CONFLICT DETECTED - HARD REJECT")
    elif fdata.get("edge", 0) < 0:
        st.warning("⚠️ REJECTED - Negative Edge (No Value)")
    else:
        st.info("ℹ️ PENDING REVIEW")
    
    st.divider()
    
    # ===== MODULE 4: PRE-FILTER =====
    st.markdown("### M4: Asymmetric Pre-filter (8 Checks)")
    m4_passed = fdata.get("m4_passed", False)
    m4_checks = fdata.get("m4_checks", 0)
    m4_total = fdata.get("m4_total", 8)
    
    checks = [
        {"name": "C1: Season Win Gap", "passed": True, "value": 14, "threshold": 3},
        {"name": "C2: Venue Win Gap", "passed": True, "value": 0.22, "threshold": 0.15},
        {"name": "C3: H2H Favoured", "passed": True, "value": 0.65, "threshold": 0.50},
        {"name": "C4: Transition Favours", "passed": True, "value": 0.58, "threshold": 0.45},
        {"name": "C5: Bounce-back Rate", "passed": False, "value": 0.38, "threshold": 0.45},
        {"name": "C6: Ceiling Proximity", "passed": True, "value": 0.72, "threshold": 0.88},
        {"name": "C7: Momentum Gap", "passed": True, "value": 0.40, "threshold": 0.20},
        {"name": "C8: Resilience Gap", "passed": True, "value": 0.42, "threshold": 0.10},
    ]
    
    for check in checks:
        icon = "✅" if check["passed"] else "❌"
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"{icon} {check['name']}")
        with col2:
            st.write(f"Value: {check['value']}")
        with col3:
            st.write(f"Threshold: {check['threshold']}")
    
    st.markdown(f"**Result:** {m4_checks}/{m4_total} passed → {'✅ PASS' if m4_passed else '❌ FAIL'}")
    
    st.divider()
    
    # ===== MODULE 5: FORENSIC FAILURES =====
    st.markdown("### M5: Forensic Failures")
    failures = [
        {"name": "New Manager Bounce (underdog)", "points": 2.0},
        {"name": "High Draw Probability (25%)", "points": 1.0},
    ]
    for f in failures:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"⚠️ {f['name']}")
        with col2:
            st.write(f"+{f['points']} pts")
    
    m5_score = fdata.get("m5_score", 0)
    m5_threshold = fdata.get("m5_threshold", 4.5)
    st.markdown(f"**Total Failure Score:** {m5_score} / {m5_threshold} → {'✅ PASS' if m5_score < m5_threshold else '❌ FAIL'}")
    
    st.divider()
    
    # ===== MODULE 6: PERSONNEL =====
    st.markdown("### M6: Personnel Forensics")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{fixture['home']}**")
        st.metric("Personnel Score", "82/100", "Healthy")
        st.write("Key injuries: None")
        st.write("Fatigue: LOW")
    with col2:
        st.markdown(f"**{fixture['away']}**")
        st.metric("Personnel Score", "65/100", "1 injury")
        st.write("Key injuries: 1 (midfielder)")
        st.write("Fatigue: MEDIUM")
    
    st.divider()
    
    # ===== MODULE 7: AI CONSENSUS =====
    st.markdown("### M7: AI Consensus")
    ai_data = pd.DataFrame([
        {"Provider": "DeepSeek", "Verdict": "APPROVE", "Confidence": "78%"},
        {"Provider": "Claude", "Verdict": "APPROVE", "Confidence": "72%"},
        {"Provider": "Gemini", "Verdict": "CAUTION", "Confidence": "55%"},
        {"Provider": "GPT", "Verdict": "APPROVE", "Confidence": "75%"},
    ])
    st.dataframe(ai_data, use_container_width=True, hide_index=True)
    st.markdown("**Consensus:** 3/4 APPROVE → ✅ APPROVED")
    
    st.divider()
    
    # ===== MODULE 8: DUAL PATTERN (CONFLICT DETECTION) =====
    st.markdown("### M8: Dual Pattern Engine")
    
    if fdata.get("h2h_conflict", False):
        st.error("🚨 H2H CONFLICT DETECTED - HARD REJECT")
        st.markdown(f"""
        **H2H HISTORY (80+ matches):**
        - {fixture['home']}: {fdata.get('h2h_wr', 46)}% wins
        - Draws: 30%
        - {fixture['away']}: {100 - fdata.get('h2h_wr', 46) - 30}% wins
        
        **CURRENT SEASON (20 matches):**
        - {fixture['home']}: 20% wins, 6th place
        - {fixture['away']}: {fdata.get('current_season_wr', 45)}% wins, 2nd place
        
        **CONFLICT:** H2H and current season directly contradict each other.
        
        **M8 v6 RULE:** "If ANY conflict detected → HARD REJECT (stake multiplier = 0.0)"
        """)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Dual Risk Level", "LOW")
            st.metric("Underdog Threat", "NONE")
        with col2:
            st.metric("Pattern Clash Score", "0.18")
            st.metric("Resilience Gap", "+0.24")
    
    st.divider()
    
    # ===== MODULE 9: UNDERDOG SCANNER =====
    st.markdown("### M9: Underdog Scanner")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Underdog Edge", f"{fdata.get('edge', 0):+.1f}%")
        st.metric("Threat Level", "LOW")
    with col2:
        st.metric("Pattern Score", "22/100")
        st.metric("Goldmine Qualified", "❌ No")
    
    st.divider()
    
    # ===== MODULE 10: TALLY MATRIX =====
    st.markdown("### M10: Tally Matrix")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Matrix Useful", "✅ YES")
        st.metric("Bilateral Prediction", "HOME")
    with col2:
        st.metric("Bilateral Confidence", "HIGH")
        st.metric("Trap/Value Signal", "NONE")
    
    st.divider()
    
    # ===== MODULE 26: MATCH CONTEXT =====
    st.markdown("### M26: Match Context")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Match Importance", "72%")
        st.write("Is Rivalry: ✅ Yes")
    with col2:
        st.metric("Home Motivation", "HIGH")
        st.metric("Away Motivation", "NORMAL")
    
    st.divider()
    
    # ===== MODULE 27: H2H DEEP ANALYSIS =====
    st.markdown("### M27: H2H Deep Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("H2H Score", "78/100", "FAV_EDGE")
        st.write(f"Games: 48 | Fav 29 | Draw 11 | Und 8")
    with col2:
        st.metric("Draw Rate", "23%")
        st.metric("Psychological Block", "❌ No")
        st.metric("Draw Boost Factor", "1.00x")
    
    st.divider()
    
    # ===== RISK FLAGS =====
    st.markdown("### ⚠️ Risk Flags")
    risk_flags = ["Pattern clash moderate", "H2H bounce-back threat: 45%"]
    for flag in risk_flags:
        st.warning(flag)
    
    st.divider()
    
    # ===== FINAL VERDICT & STAKE =====
    st.markdown("### ✅ FINAL VERDICT")
    
    if fdata.get("status") == "APPROVED":
        stake = fdata.get("stake", 0)
        bankroll = fdata.get("bankroll", 1000)
        stake_pct = (stake / bankroll) * 100 if bankroll > 0 else 0
        
        st.success(f"""
        **STATUS: APPROVED**
        - Confidence: {fixture['confidence']}
        - Edge: +{fdata.get('edge', 0)}%
        - Model Probability: {fdata.get('prob', 0)}%
        - Kelly Stake: £{stake:.2f} ({stake_pct:.2f}% of bankroll)
        - Potential Return: £{stake * fixture['odds']:.2f}
        - Potential Profit: £{stake * (fixture['odds'] - 1):.2f}
        """)
    elif fdata.get("m8_conflict"):
        st.error(f"""
        **STATUS: REJECTED (H2H CONFLICT)**
        - Edge: +{fdata.get('edge', 0)}% (would be value)
        - Model Probability: {fdata.get('prob', 0)}%
        - Odds: {fixture['odds']:.2f}
        
        **Reason:** {fdata.get('reason', 'H2H vs current season contradiction')}
        
        **M8 v6 Rule:** Conflict = HARD REJECT (stake multiplier = 0.0)
        """)
    elif fdata.get("edge", 0) < 0:
        st.warning(f"""
        **STATUS: REJECTED (Negative Edge)**
        - Model Probability: {fdata.get('prob', 0)}%
        - Implied Probability: {(1/fixture['odds'] * 100):.1f}%
        - Edge: {fdata.get('edge', 0):+.1f}%
        
        **Reason:** Model says {fdata.get('prob', 0)}%, market says {(1/fixture['odds'] * 100):.1f}%. No value.
        """)
    else:
        st.info(f"**STATUS: {fdata.get('status', 'PENDING')}**")
    
    st.divider()
    
    # ===== KELLY CALCULATION DETAILS =====
    if fdata.get("status") == "APPROVED":
        st.markdown("### 📊 Kelly Calculation")
        st.markdown(f"""
        - Raw Kelly Fraction: {fdata.get('kelly_raw', 0.085)*100:.2f}%
        - Confidence Scaling: {fdata.get('confidence', 'HIGH')} → 50% of Kelly
        - Adjusted Kelly: {fdata.get('kelly_adj', 0.0335)*100:.2f}%
        - Bankroll: £{fdata.get('bankroll', 1000):.0f}
        - Final Stake: **£{fdata.get('stake', 0):.2f}**
        """)

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.title("🎯 MATCH ORACLE")
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    
    # Backend status banner
    if st.session_state.backend_status == "connected":
        st.success(f"✅ BACKEND CONNECTED | {st.session_state.backend_url}")
    elif st.session_state.backend_status == "disconnected":
        st.error(f"❌ BACKEND DISCONNECTED | {st.session_state.backend_url}")
    
    st.divider()
    
    # Group fixtures by league
    st.subheader("🏆 League of Ireland")
    
    for fixture in MOCK_FIXTURES:
        # Determine status color/icon
        fid = fixture['id']
        fdata = FORENSIC_DATA.get(fid, {})
        
        if fdata.get("status") == "APPROVED":
            status_icon = "✅"
            status_color = "green"
        elif fdata.get("m8_conflict"):
            status_icon = "🚨"
            status_color = "red"
        elif fdata.get("edge", 0) < 0:
            status_icon = "⚠️"
            status_color = "orange"
        else:
            status_icon = "❓"
            status_color = "gray"
        
        col1, col2, col3, col4, col5, col6 = st.columns([2.5, 1, 0.8, 0.8, 1, 0.8])
        
        with col1:
            st.markdown(f"**{status_icon} {fixture['home']} vs {fixture['away']}**")
        with col2:
            st.write(fixture['time'])
        with col3:
            st.write(f"{fixture['odds']:.2f}")
        with col4:
            edge = fixture.get('edge', 0)
            edge_color = "🟢" if edge > 0 else "🔴" if edge < 0 else "⚪"
            st.write(f"{edge_color} {abs(edge):.1f}%")
        with col5:
            st.write(f"{fixture['prob']}%")
        with col6:
            if st.button("🔍", key=f"btn_{fixture['id']}", help="View forensic report"):
                st.session_state.selected_fixture = fixture
                navigate_to("forensic")
        st.divider()
    
    # Top Picks Summary
    st.subheader("🏆 Top Picks (Ranked)")
    approved_fixtures = [f for f in MOCK_FIXTURES if FORENSIC_DATA.get(f['id'], {}).get("status") == "APPROVED"]
    
    if approved_fixtures:
        for i, fixture in enumerate(approved_fixtures, 1):
            fdata = FORENSIC_DATA.get(fixture['id'], {})
            stake = fdata.get('stake', 0)
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
            with col1:
                st.write(f"**#{i} {fixture['home']} vs {fixture['away']}**")
            with col2:
                st.write(f"{fixture['selection']} @ {fixture['odds']:.2f}")
            with col3:
                st.write(f"{fixture['prob']}% prob")
            with col4:
                st.write(f"Stake: £{stake:.2f}")
            st.divider()
    else:
        st.info("No approved picks for today")

# ========== OTHER PAGES (simplified for brevity) ==========
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
        fdata = FORENSIC_DATA.get(fixture['id'], {})
        if fdata.get("status") == "APPROVED":
            st.write(f"**{fixture['home']} vs {fixture['away']}** - {fixture['selection']} @ {fixture['odds']:.2f}")

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
        st.write(f"{fixture['home']} vs {fixture['away']} - {fixture['league']} - {fixture['time']}")

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
        
        # Backend Status
        if st.session_state.backend_status == "connected":
            st.success("🟢 BACKEND ONLINE")
        else:
            st.error("🔴 BACKEND OFFLINE")
        
        st.markdown("---")
        
        # Menu
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
    
    # Page routing
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
