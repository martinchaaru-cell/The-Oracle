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
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #0f0f0f 100%);
    }
    
    /* Headers - moved up by removing top padding/margin */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -30px;
        margin-bottom: 0;
        padding-top: 0;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #B8860B;
        margin-top: -10px;
        margin-bottom: 15px;
        border-left: 3px solid #FFD700;
        padding-left: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Thinner separators */
    hr {
        margin: 2px 0;
        border-color: #2a2a2a;
    }
    
    /* Smaller buttons */
    .stButton button {
        padding: 0px 5px;
        min-height: 25px;
        font-size: 0.7rem;
    }
    
    /* Compact columns */
    div[data-testid="column"] {
        padding: 0 2px;
    }
    
    /* Match row styling */
    .match-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 0;
        border-bottom: 1px solid #2a2a2a;
    }
    
    .match-cell {
        font-size: 0.85rem;
    }
    
    .odds-cell {
        font-size: 0.85rem;
        font-weight: 600;
        color: #FFD700;
        min-width: 50px;
        text-align: center;
    }
    
    .edge-positive {
        color: #00FF88;
        font-weight: 600;
    }
    
    .edge-negative {
        color: #FF4444;
        font-weight: 600;
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
    {
        "id": 1, "home": "Wexford Youths", "away": "Cork City", "tier": 2,
        "time": "19:45", "home_odds": 2.90, "draw_odds": 3.20, "away_odds": 2.36,
        "prob": 62, "edge": 4.2, "status": "APPROVED"
    },
    {
        "id": 2, "home": "Derry City", "away": "Bohemians FC", "tier": 2,
        "time": "19:45", "home_odds": 2.90, "draw_odds": 3.20, "away_odds": 2.36,
        "prob": 54, "edge": 2.3, "status": "REJECTED", "rejection_reason": "H2H CONFLICT"
    },
    {
        "id": 3, "home": "Shamrock Rovers", "away": "Shelbourne FC", "tier": 2,
        "time": "19:45", "home_odds": 1.33, "draw_odds": 4.50, "away_odds": 6.00,
        "prob": 68, "edge": -7.2, "status": "REJECTED", "rejection_reason": "Negative Edge"
    },
    {
        "id": 4, "home": "Ajax", "away": "Feyenoord", "tier": 1,
        "time": "15:00", "home_odds": 1.85, "draw_odds": 3.70, "away_odds": 3.90,
        "prob": 57, "edge": 5.1, "status": "APPROVED"
    }
]

FORENSIC_DATA = {
    1: {"status": "APPROVED", "verdict_reason": "Clear value: model 62% vs market implied 58%",
        "leg_data": {"home_form": "L D W L L", "away_form": "W W D L W", "home_position": 8, "away_position": 3,
                     "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%", "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1"},
        "stake": 33.50},
    2: {"status": "REJECTED", "verdict_reason": "H2H CONFLICT",
        "leg_data": {"home_form": "L L W D L", "away_form": "W W D W L", "home_position": 6, "away_position": 2,
                     "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%", "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1"},
        "stake": 0},
    3: {"status": "REJECTED", "verdict_reason": "Negative edge",
        "leg_data": {"home_form": "W W D W L", "away_form": "L L D L W", "home_position": 1, "away_position": 7,
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

# ========== MATCH CARD (COMPACT ROW) ==========
def show_match_card(match):
    fid = match.get("id", 0)
    fdata = FORENSIC_DATA.get(fid, {})
    status = fdata.get("status", "PENDING")
    
    # Status icon
    if status == "APPROVED":
        status_icon = "✅"
    elif status == "REJECTED":
        if "CONFLICT" in fdata.get("verdict_reason", ""):
            status_icon = "🚨"
        else:
            status_icon = "❌"
    else:
        status_icon = "⚠️"
    
    edge = match.get("edge", 0)
    edge_symbol = "+" if edge > 0 else ""
    edge_color = "#00FF88" if edge > 0 else "#FF4444"
    prob = match.get("prob", 50)
    
    # Single row using columns - much more compact
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.4, 2.0, 0.7, 0.7, 0.7, 0.7, 1.0, 0.5])
    
    with col1:
        st.write(f"**{match.get('tier', '?')}**")
    
    with col2:
        home_short = match.get("home", "?")[:12]
        away_short = match.get("away", "?")[:12]
        st.write(f"{home_short} vs {away_short}")
    
    with col3:
        st.write(match.get("time", "TBD"))
    
    with col4:
        st.write(f"{match.get('home_odds', 0):.2f}")
    
    with col5:
        st.write(f"{match.get('draw_odds', 0):.2f}")
    
    with col6:
        st.write(f"{match.get('away_odds', 0):.2f}")
    
    with col7:
        st.markdown(f"<span style='color:{edge_color};'>{edge_symbol}{edge:.1f}%</span> {prob}%", unsafe_allow_html=True)
    
    with col8:
        st.write(status_icon)
        if st.button("🔍", key=f"view_{match.get('id', 0)}"):
            navigate_to("match_detail", match)
    
    st.divider()

# ========== LEG DATA TAB ==========
def show_leg_data(match, fdata):
    leg_data = fdata.get("leg_data", {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{match.get('home', 'Home')} Form**")
        st.code(leg_data.get("home_form", "?"), language="text")
        st.metric("Position", leg_data.get("home_position", "?"))
    with col2:
        st.markdown(f"**{match.get('away', 'Away')} Form**")
        st.code(leg_data.get("away_form", "?"), language="text")
        st.metric("Position", leg_data.get("away_position", "?"))
    
    st.divider()
    st.markdown("### Head-to-Head Record")
    st.info(f"All-time: {leg_data.get('h2h_record', 'No data')}")
    st.info(f"Last 6: {leg_data.get('h2h_last6', 'No data')}")

# ========== FORENSIC TAB ==========
def show_forensic_tab(match, fdata):
    st.markdown("### M4: Pre-filter")
    st.progress(0.75)
    st.info("6/8 checks passed")
    
    st.markdown("### M5: Forensic Failures")
    st.warning("New Manager Bounce - +2.0 pts")
    st.warning("High Draw Probability - +1.0 pts")
    st.success("Total: 2.5 / 4.5 -> PASS")
    
    st.markdown("### M6: Personnel")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"{match.get('home', 'Home')}", "82/100")
    with col2:
        st.metric(f"{match.get('away', 'Away')}", "65/100")
    
    st.markdown("### M7: AI Consensus")
    df = pd.DataFrame([
        ["DeepSeek", "APPROVE", "78%"],
        ["Claude", "APPROVE", "72%"],
        ["Gemini", "CAUTION", "55%"],
        ["GPT", "APPROVE", "75%"]
    ], columns=["Provider", "Verdict", "Confidence"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("### M8: Dual Pattern")
    if "CONFLICT" in fdata.get("verdict_reason", ""):
        st.error("H2H CONFLICT - HARD REJECT")
    else:
        st.metric("Dual Risk Level", "LOW")
    
    st.markdown("### M9: Underdog Scanner")
    st.metric("Underdog Edge", f"{match.get('edge', 0):+.1f}%")
    
    st.markdown("### M10: Tally Matrix")
    st.success("Bilateral Prediction: HOME")
    
    st.markdown("### M26: Match Context")
    st.metric("Match Importance", "72%")
    
    st.markdown("### M27: H2H Analysis")
    st.metric("H2H Score", "78/100")
    
    st.divider()
    if fdata.get("status") == "APPROVED":
        st.success(f"FINAL: APPROVED | Stake: ${fdata.get('stake', 0):.2f}")
    elif "CONFLICT" in fdata.get("verdict_reason", ""):
        st.error("FINAL: REJECTED (H2H CONFLICT)")

# ========== MATCH DETAIL ==========
def show_match_detail():
    match = st.session_state.selected_match
    if not match:
        st.error("No match selected")
        if st.button("Back"):
            go_back()
        return
    
    fid = match.get("id", 0)
    fdata = FORENSIC_DATA.get(fid, {})
    
    st.markdown(f"## {match.get('home', '?')} vs {match.get('away', '?')}")
    st.caption(f"Kickoff: {match.get('time', 'TBD')}")
    
    if st.button("← Back"):
        go_back()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["Leg Data", "Forensic Report"])
    with tab1:
        show_leg_data(match, fdata)
    with tab2:
        show_forensic_tab(match, fdata)

# ========== DASHBOARD ==========
def show_dashboard():
    # Header moved UP by reducing margin
    st.markdown('<h1 class="main-header">MATCH ORACLE</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Football Intelligence</p>', unsafe_allow_html=True)
    
    if st.session_state.backend_status == "connected":
        st.success("✅ BACKEND ONLINE")
    else:
        st.warning("⚠️ BACKEND OFFLINE - Using demo data")
    
    st.markdown("## Today's Fixtures")
    st.caption(f"{len(MATCHES)} matches • {datetime.now(NAIROBI_TZ).strftime('%A, %B %d, %Y')}")
    
    # Table header
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([0.4, 2.0, 0.7, 0.7, 0.7, 0.7, 1.0, 0.5])
    with c1:
        st.markdown("**Tier**")
    with c2:
        st.markdown("**Match**")
    with c3:
        st.markdown("**Time**")
    with c4:
        st.markdown("**Home**")
    with c5:
        st.markdown("**Draw**")
    with c6:
        st.markdown("**Away**")
    with c7:
        st.markdown("**Edge/Prob**")
    with c8:
        st.markdown("**Status**")
    
    st.divider()
    
    for match in MATCHES:
        show_match_card(match)

# ========== OTHER PAGES ==========
def show_performance():
    st.markdown("## Performance Metrics")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Calibration Grade", "B")
    with col2:
        st.metric("Brier Score", "0.187")
    with col3:
        st.metric("ECE", "0.094")

def show_bankroll():
    st.markdown("## Bankroll Manager")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current", "$12,450")
    with col2:
        st.metric("Peak", "$13,200")
    with col3:
        st.metric("Drawdown", "5.7%")
    with col4:
        st.metric("Multiplier", "0.85x")

def show_top_picks():
    st.markdown("## Top Picks")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    for match in MATCHES:
        if FORENSIC_DATA.get(match.get("id", 0), {}).get("status") == "APPROVED":
            st.write(f"{match.get('home')} vs {match.get('away')}")

def show_parlays():
    st.markdown("## Parlays")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.info("Coming soon")

def show_all_legs():
    st.markdown("## All Legs")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    for match in MATCHES:
        st.write(f"{match.get('home')} vs {match.get('away')}")

def show_countries():
    st.markdown("## Countries")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.info("Coming soon")

def show_calendar():
    st.markdown("## Calendar")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    st.date_input("Select Date", datetime.now(NAIROBI_TZ).date())

def show_settings():
    st.markdown("## Settings")
    if st.button("← Back"):
        navigate_to("dashboard")
    st.divider()
    
    if st.button("Test Connection", use_container_width=True):
        check_backend()
        if st.session_state.backend_status == "connected":
            st.success("Connected!")
        else:
            st.error("Not connected")

# ========== MAIN ==========
def main():
    with st.sidebar:
        st.markdown("### MATCH ORACLE")
        st.markdown("---")
        
        if st.session_state.backend_status == "connected":
            st.success("🟢 ONLINE")
        else:
            st.error("🔴 OFFLINE")
        
        st.markdown("---")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            navigate_to("dashboard")
        
        st.markdown("---")
        st.markdown("**ANALYTICS**")
        if st.button("📈 Performance", use_container_width=True):
            navigate_to("performance")
        if st.button("💰 Bankroll", use_container_width=True):
            navigate_to("bankroll")
        if st.button("🏆 Top Picks", use_container_width=True):
            navigate_to("top_picks")
        if st.button("🔗 Parlays", use_container_width=True):
            navigate_to("parlays")
        
        st.markdown("---")
        st.markdown("**DATA**")
        if st.button("📋 All Legs", use_container_width=True):
            navigate_to("all_legs")
        if st.button("🌍 Countries", use_container_width=True):
            navigate_to("countries")
        if st.button("📅 Calendar", use_container_width=True):
            navigate_to("calendar")
        if st.button("⚙️ Settings", use_container_width=True):
            navigate_to("settings")
        
        st.markdown("---")
        st.caption("v4.0")
    
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
