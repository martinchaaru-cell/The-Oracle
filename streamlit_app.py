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

# ========== BLACK/GOLD THEME CSS ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #0f0f0f 100%);
    }
    .gold-header {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .gold-subheader {
        font-size: 0.8rem;
        color: #B8860B;
        margin-bottom: 0.5rem;
        border-left: 3px solid #FFD700;
        padding-left: 1rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    hr {
        margin: 0.1rem 0;
        border-color: #2a2a2a;
    }
    .stButton button {
        padding: 0rem 0.2rem;
        min-height: 0px;
        font-size: 0.6rem;
    }
    div[data-testid="column"] {
        padding: 0 0.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== LIVE CLOCK ==========
st.markdown("""
<div id="live-clock" style="position: fixed; top: 5px; right: 15px; color: #FFD700; font-family: monospace; font-size: 0.7rem; z-index: 999;"></div>
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

# ========== API CONFIG ==========
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

# ========== MATCH DATA ==========
MATCHES = [
    {"id": 1, "home": "Wexford Youths", "away": "Cork City", "league": "Ireland", "tier": 2,
     "time": "19:45", "venue": "Ferrycarrig Park", "home_odds": 2.90, "draw_odds": 3.20, "away_odds": 2.36,
     "selection": "Cork City", "selection_odds": 2.36, "prob": 62, "edge": 4.2, "status": "APPROVED"},
    {"id": 2, "home": "Derry City", "away": "Bohemians FC", "league": "Ireland", "tier": 2,
     "time": "19:45", "venue": "Ryan McBride Brandywell", "home_odds": 2.90, "draw_odds": 3.20, "away_odds": 2.36,
     "selection": "Bohemians FC", "selection_odds": 2.36, "prob": 54, "edge": 2.3, "status": "REJECTED",
     "rejection_reason": "H2H CONFLICT"},
    {"id": 3, "home": "Shamrock Rovers", "away": "Shelbourne FC", "league": "Ireland", "tier": 2,
     "time": "19:45", "venue": "Tallaght Stadium", "home_odds": 1.33, "draw_odds": 4.50, "away_odds": 6.00,
     "selection": "Shamrock Rovers", "selection_odds": 1.33, "prob": 68, "edge": -7.2, "status": "REJECTED",
     "rejection_reason": "Negative Edge"},
    {"id": 4, "home": "Ajax", "away": "Feyenoord", "league": "Netherlands", "tier": 1,
     "time": "15:00", "venue": "Johan Cruijff ArenA", "home_odds": 1.85, "draw_odds": 3.70, "away_odds": 3.90,
     "selection": "Ajax", "selection_odds": 1.85, "prob": 57, "edge": 5.1, "status": "APPROVED"},
]

FORENSIC_DATA = {
    1: {"status": "APPROVED", "verdict_reason": "Clear value: model 62% vs market implied 58%",
        "leg_data": {"country": "Ireland", "league": "League of Ireland", "venue": "Ferrycarrig Park",
                     "home_form": "L D W L L", "away_form": "W W D L W", "home_position": 8, "away_position": 3",
                     "home_points": 24, "away_points": 38,
                     "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%", "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1"},
        "stake": 33.50, "bankroll": 1000},
    2: {"status": "REJECTED", "verdict_reason": "H2H CONFLICT: Historical favours Derry, current season favours Bohemians",
        "leg_data": {"country": "Ireland", "league": "League of Ireland", "venue": "Ryan McBride Brandywell",
                     "home_form": "L L W D L", "away_form": "W W D W L", "home_position": 6, "away_position": 2,
                     "home_points": 28, "away_points": 42,
                     "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%", "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1"},
        "stake": 0},
    3: {"status": "REJECTED", "verdict_reason": "Negative edge: model 68% vs market 75%",
        "leg_data": {"country": "Ireland", "league": "League of Ireland", "venue": "Tallaght Stadium",
                     "home_form": "W W D W L", "away_form": "L L D L W", "home_position": 1, "away_position": 7,
                     "home_points": 52, "away_points": 28,
                     "h2h_record": "Shamrock 65% | Draw 20% | Shelbourne 15%", "h2h_last6": "Shamrock 4 | Draw 1 | Shelbourne 1"},
        "stake": 0},
}

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"

def check_backend():
    backend_url = get_backend_url()
    connected, _ = test_backend_connection(backend_url)
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

# ========== ULTRA COMPACT MATCH CARD (Single Line) ==========
def show_match_card(match):
    fid = match.get('id', 0)
    fdata = FORENSIC_DATA.get(fid, {})
    status = fdata.get('status', 'PENDING')
    
    if status == "APPROVED":
        status_color = "#00FF88"
        status_icon = "✅"
    elif status == "REJECTED":
        if "CONFLICT" in fdata.get('verdict_reason', ''):
            status_color = "#FF4444"
            status_icon = "🚨"
        else:
            status_color = "#FFA500"
            status_icon = "❌"
    else:
        status_color = "#FFD700"
        status_icon = "⚠️"
    
    edge = match.get('edge', 0)
    edge_symbol = "+" if edge > 0 else ""
    edge_color = "#00FF88" if edge > 0 else "#FF4444"
    prob = match.get('prob', 50)
    
    # Single line - 8 columns
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([0.8, 2.2, 0.8, 0.8, 0.8, 0.8, 1, 0.8])
    
    with c1:
        st.markdown(f"<span style='font-size: 0.7rem; color: #FFD700;'>🏆{match.get('tier', '?')}</span>", unsafe_allow_html=True)
    
    with c2:
        home_short = match.get('home', '?')[:12]
        away_short = match.get('away', '?')[:12]
        st.markdown(f"<span style='font-size: 0.75rem; font-weight: 500;'>{home_short} vs {away_short}</span>", unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"<span style='font-size: 0.65rem; color: #888;'>{match.get('time', 'TBD')}</span>", unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"<span style='font-size: 0.7rem; font-weight: 600; color: #FFD700;'>{match.get('home_odds', 0):.2f}</span>", unsafe_allow_html=True)
    
    with c5:
        st.markdown(f"<span style='font-size: 0.7rem; font-weight: 600; color: #FFD700;'>{match.get('draw_odds', 0):.2f}</span>", unsafe_allow_html=True)
    
    with c6:
        st.markdown(f"<span style='font-size: 0.7rem; font-weight: 600; color: #FFD700;'>{match.get('away_odds', 0):.2f}</span>", unsafe_allow_html=True)
    
    with c7:
        st.markdown(f"<span style='font-size: 0.7rem; font-weight: 600; color: {edge_color};'>{edge_symbol}{edge:.1f}%</span><br><span style='font-size: 0.55rem; color: #666;'>{prob}%</span>", unsafe_allow_html=True)
    
    with c8:
        st.markdown(f"<span style='font-size: 0.9rem; color: {status_color};'>{status_icon}</span>", unsafe_allow_html=True)
        if st.button("🔍", key=f"view_{match.get('id', 0)}", help="View Analysis"):
            navigate_to("match_detail", match)
    
    st.markdown("<hr>", unsafe_allow_html=True)

# ========== LEG DATA TAB ==========
def show_leg_data(match, fdata):
    leg_data = fdata.get('leg_data', {})
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Country", leg_data.get('country', '?'))
        st.metric("League", leg_data.get('league', '?'))
    with c2:
        st.metric("Venue", leg_data.get('venue', '?'))
        st.metric("Kickoff", leg_data.get('kickoff', '?').split(' ')[1] if leg_data.get('kickoff') else '?')
    with c3:
        st.metric("Home Position", leg_data.get('home_position', '?'))
        st.metric("Away Position", leg_data.get('away_position', '?'))
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{match.get('home', 'Home')} Form**")
        st.code(leg_data.get('home_form', '?'), language="text")
    with c2:
        st.markdown(f"**{match.get('away', 'Away')} Form**")
        st.code(leg_data.get('away_form', '?'), language="text")
    
    st.divider()
    st.markdown("### 📜 Head-to-Head Record")
    st.info(f"**All-time:** {leg_data.get('h2h_record', 'No data')}")
    st.info(f"**Last 6 meetings:** {leg_data.get('h2h_last6', 'No data')}")

# ========== FORENSIC TAB ==========
def show_forensic_tab(match, fdata):
    st.markdown("### M4: Pre-filter")
    st.progress(0.75)
    st.info("6/8 checks passed - C5 (Bounce-back Rate) failed")
    
    st.markdown("### M5: Forensic Failures")
    st.warning("⚠️ New Manager Bounce (underdog) - +2.0 pts")
    st.warning("⚠️ High Draw Probability (25%) - +1.0 pts")
    st.success("Total Failure Score: 2.5 / 4.5 → PASS")
    
    st.markdown("### M6: Personnel")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(f"{match.get('home', 'Home')}", "82/100", "Healthy")
    with c2:
        st.metric(f"{match.get('away', 'Away')}", "65/100", "1 injury")
    
    st.markdown("### M7: AI Consensus")
    st.dataframe(pd.DataFrame([
        {"Provider": "DeepSeek", "Verdict": "APPROVE", "Confidence": "78%"},
        {"Provider": "Claude", "Verdict": "APPROVE", "Confidence": "72%"},
        {"Provider": "Gemini", "Verdict": "CAUTION", "Confidence": "55%"},
        {"Provider": "GPT", "Verdict": "APPROVE", "Confidence": "75%"},
    ]), use_container_width=True, hide_index=True)
    st.success("Consensus: 3/4 APPROVE")
    
    st.markdown("### M8: Dual Pattern")
    if "CONFLICT" in fdata.get('verdict_reason', ''):
        st.error("🚨 H2H CONFLICT DETECTED - HARD REJECT")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Dual Risk Level", "LOW")
        with c2:
            st.metric("Underdog Threat", "NONE")
    
    st.markdown("### M9: Underdog Scanner")
    st.metric("Underdog Edge", f"{match.get('edge', 0):+.1f}%")
    
    st.markdown("### M10: Tally Matrix")
    st.success("Bilateral Prediction: HOME (HIGH confidence)")
    
    st.markdown("### M26: Match Context")
    st.metric("Match Importance", "72%")
    st.write("Is Rivalry: ✅ Yes")
    
    st.markdown("### M27: H2H Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("H2H Score", "78/100", "FAV_EDGE")
    with c2:
        st.metric("Draw Rate", "23%")
    
    st.divider()
    st.markdown("### ⚠️ Risk Flags")
    st.warning("Pattern clash moderate")
    st.info("H2H bounce-back threat: 45%")

# ========== MATCH DETAIL PAGE ==========
def show_match_detail():
    match = st.session_state.selected_match
    if not match:
        st.error("No match selected")
        if st.button("← Back"):
            go_back()
        return
    
    fid = match.get('id', 0)
    fdata = FORENSIC_DATA.get(fid, {})
    
    st.markdown(f'<p class="gold-header">🔬 {match.get("home", "?")} vs {match.get("away", "?")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="gold-subheader">{match.get("league", "?")} • {match.get("venue", "?")} • {match.get("time", "TBD")}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        go_back()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Leg Data", "🔬 Full Forensic Report"])
    with tab1:
        show_leg_data(match, fdata)
    with tab2:
        show_forensic_tab(match, fdata)
    
    if fdata.get('status') == 'APPROVED':
        st.success(f"✅ FINAL VERDICT: APPROVED | Stake: £{fdata.get('stake', 0):.2f}")
    elif "CONFLICT" in fdata.get('verdict_reason', ''):
        st.error("🚨 FINAL VERDICT: REJECTED (H2H CONFLICT)")

# ========== DASHBOARD ==========
def show_dashboard():
    st.markdown('<p class="gold-header">MATCH ORACLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">AI-Powered Football Intelligence • Elite Betting Analysis</p>', unsafe_allow_html=True)
    
    if st.session_state.backend_status == "connected":
        st.success("✅ BACKEND ONLINE")
    else:
        st.warning("⚠️ BACKEND OFFLINE - Using demo data")
    
    st.markdown(f"## 📅 Today's Fixtures")
    st.caption(f"{len(MATCHES)} matches • {datetime.now(NAIROBI_TZ).strftime('%A, %B %d, %Y')}")
    
    for match in MATCHES:
        show_match_card(match)
    
    st.caption("© 2025 Match Oracle")

# ========== OTHER PAGES ==========
def show_performance():
    st.markdown('<p class="gold-header">📈 Performance Metrics</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Calibration Grade", "B")
    with c2:
        st.metric("Brier Score", "0.187")
    with c3:
        st.metric("ECE", "0.094")

def show_bankroll():
    st.markdown('<p class="gold-header">💰 Bankroll Manager</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Current", "$12,450")
    with c2:
        st.metric("Peak", "$13,200")
    with c3:
        st.metric("Drawdown", "5.7%")
    with c4:
        st.metric("Stake Multiplier", "0.85x")

def show_top_picks():
    st.markdown('<p class="gold-header">🏆 Top Picks</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    for match in MATCHES:
        if FORENSIC_DATA.get(match.get('id', 0), {}).get('status') == 'APPROVED':
            st.write(f"**{match.get('home')} vs {match.get('away')}** - {match.get('selection')} @ {match.get('selection_odds'):.2f}")

def show_parlays():
    st.markdown('<p class="gold-header">🔗 Parlay Builder</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.info("Coming soon")

def show_all_legs():
    st.markdown('<p class="gold-header">📋 All Legs</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    for match in MATCHES:
        st.write(f"**{match.get('home')} vs {match.get('away')}** - {match.get('league')} - {match.get('time')}")

def show_countries():
    st.markdown('<p class="gold-header">🌍 Country Explorer</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.info("Coming soon")

def show_calendar():
    st.markdown('<p class="gold-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.date_input("Select Date", datetime.now(NAIROBI_TZ).date())

def show_settings():
    st.markdown('<p class="gold-header">⚙️ Settings</p>', unsafe_allow_html=True)
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Test Connection", use_container_width=True):
            check_backend()
            if st.session_state.backend_status == "connected":
                st.success("✅ Connected!")
            else:
                st.error("❌ Not connected")
    with c2:
        if st.button("🌐 Wake Up Backend", use_container_width=True):
            with st.spinner("Waking up..."):
                try:
                    response = requests.get(f"{get_backend_url()}/health", timeout=60)
                    if response.status_code == 200:
                        st.session_state.backend_status = "connected"
                        st.success("✅ Backend online!")
                        st.rerun()
                except:
                    st.warning("Still waking up...")

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
        st.caption("🎯 Match Oracle v4.0")
    
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
