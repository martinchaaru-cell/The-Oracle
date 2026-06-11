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
    
    /* Gold headers */
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
    
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #FFD700, transparent);
        margin: 1.5rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ========== LIVE CLOCK ==========
st.markdown("""
<div id="live-clock" style="position: fixed; top: 10px; right: 20px; color: #FFD700; font-family: monospace; font-size: 1rem; z-index: 999;"></div>
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

# ========== MATCH DATA ==========
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

FORENSIC_DATA = {
    1: {
        "status": "APPROVED",
        "verdict_reason": "Clear value: model 62% vs market implied 58%",
        "leg_data": {
            "country": "Ireland", "league": "League of Ireland", "tier": 2,
            "venue": "Ferrycarrig Park", "kickoff": "2025-06-11 19:45",
            "home_form": "L D W L L", "away_form": "W W D L W",
            "home_position": 8, "away_position": 3,
            "home_points": 24, "away_points": 38,
            "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%",
            "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1",
        },
        "stake": 33.50, "bankroll": 1000, "kelly_raw": 0.085, "kelly_adj": 0.0335,
    },
    2: {
        "status": "REJECTED",
        "verdict_reason": "H2H CONFLICT: Historical favours Derry, current season favours Bohemians",
        "leg_data": {
            "country": "Ireland", "league": "League of Ireland", "tier": 2,
            "venue": "Ryan McBride Brandywell", "kickoff": "2025-06-11 19:45",
            "home_form": "L L W D L", "away_form": "W W D W L",
            "home_position": 6, "away_position": 2,
            "home_points": 28, "away_points": 42,
            "h2h_record": "Derry 46% | Draw 30% | Bohemians 24%",
            "h2h_last6": "Derry 2 | Draw 3 | Bohemians 1",
        },
        "stake": 0,
    },
    3: {
        "status": "REJECTED",
        "verdict_reason": "Negative edge: model 68% vs market 75%",
        "leg_data": {
            "country": "Ireland", "league": "League of Ireland", "tier": 2,
            "venue": "Tallaght Stadium", "kickoff": "2025-06-11 19:45",
            "home_form": "W W D W L", "away_form": "L L D L W",
            "home_position": 1, "away_position": 7,
            "home_points": 52, "away_points": 28,
            "h2h_record": "Shamrock 65% | Draw 20% | Shelbourne 15%",
            "h2h_last6": "Shamrock 4 | Draw 1 | Shelbourne 1",
        },
        "stake": 0,
    },
}

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None
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

# ========== MATCH CARD ==========
def show_match_card(match):
    fid = match.get('id', 0)
    fdata = FORENSIC_DATA.get(fid, {})
    status = fdata.get('status', 'PENDING')
    
    # Status badge
    if status == "APPROVED":
        status_badge = '<span style="background-color: #00FF8820; color: #00FF88; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem;">✅ APPROVED</span>'
    elif status == "REJECTED":
        if "CONFLICT" in fdata.get('verdict_reason', ''):
            status_badge = '<span style="background-color: #FF444420; color: #FF4444; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem;">🚨 H2H CONFLICT</span>'
        else:
            status_badge = '<span style="background-color: #FF444420; color: #FF4444; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem;">❌ REJECTED</span>'
    else:
        status_badge = '<span style="background-color: #FFA50020; color: #FFA500; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem;">⚠️ PENDING</span>'
    
    edge = match.get('edge', 0)
    edge_color = "#00FF88" if edge > 0 else "#FF4444"
    edge_symbol = "+" if edge > 0 else ""
    
    prob = match.get('prob', 50)
    
    card_html = f"""
    <div style="background: linear-gradient(135deg, #1a1a1a, #0d0d0d); border: 1px solid #2a2a2a; border-radius: 16px; padding: 1.2rem; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <span style="background-color: #FFD70020; color: #FFD700; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem;">{match.get('league', '?')} • Tier {match.get('tier', '?')}</span>
                <h3 style="margin: 0.5rem 0 0.25rem 0; font-size: 1.1rem; color: white;">{match.get('home', '?')} vs {match.get('away', '?')}</h3>
                <div style="font-size: 0.8rem; color: #888;">🕐 {match.get('time', 'TBD')} • 📍 {match.get('venue', 'TBD')}</div>
            </div>
            <div>{status_badge}</div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div style="display: flex; gap: 1rem;">
                <div style="background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 6px 12px; text-align: center; min-width: 70px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #FFD700;">{match.get('home_odds', 0):.2f}</div>
                    <div style="font-size: 0.6rem; color: #666;">HOME</div>
                </div>
                <div style="background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 6px 12px; text-align: center; min-width: 70px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #FFD700;">{match.get('draw_odds', 0):.2f}</div>
                    <div style="font-size: 0.6rem; color: #666;">DRAW</div>
                </div>
                <div style="background-color: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 6px 12px; text-align: center; min-width: 70px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #FFD700;">{match.get('away_odds', 0):.2f}</div>
                    <div style="font-size: 0.6rem; color: #666;">AWAY</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div><span style="color: {edge_color}; font-weight: 700;">{edge_symbol}{edge:.1f}% EDGE</span></div>
                <div style="font-size: 0.85rem;">🎯 {match.get('selection', '?')} @ {match.get('selection_odds', 0):.2f}</div>
                <div style="background-color: #2a2a2a; border-radius: 4px; height: 6px; width: 200px; margin-top: 8px;">
                    <div style="background: linear-gradient(90deg, #FFD700, #FFA500); border-radius: 4px; height: 100%; width: {prob}%;"></div>
                </div>
                <div style="font-size: 0.7rem; color: #888;">Model Prob: {prob}%</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🔍 View Analysis", key=f"view_{match.get('id', 0)}", use_container_width=True):
            navigate_to("match_detail", match)

# ========== LEG DATA TAB ==========
def show_leg_data(match, fdata):
    leg_data = fdata.get('leg_data', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Country", leg_data.get('country', '?'))
        st.metric("League", leg_data.get('league', '?'))
    with col2:
        st.metric("Venue", leg_data.get('venue', '?'))
        st.metric("Kickoff", leg_data.get('kickoff', '?').split(' ')[1] if leg_data.get('kickoff') else '?')
    with col3:
        st.metric("Home Position", leg_data.get('home_position', '?'))
        st.metric("Away Position", leg_data.get('away_position', '?'))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{match.get('home', 'Home')} Form**")
        st.markdown(f"<div style='font-size: 1.2rem; letter-spacing: 4px;'>{leg_data.get('home_form', '?')}</div>", unsafe_allow_html=True)
        st.caption(f"Position: {leg_data.get('home_position', '?')} | Points: {leg_data.get('home_points', 0)}")
    with col2:
        st.markdown(f"**{match.get('away', 'Away')} Form**")
        st.markdown(f"<div style='font-size: 1.2rem; letter-spacing: 4px;'>{leg_data.get('away_form', '?')}</div>", unsafe_allow_html=True)
        st.caption(f"Position: {leg_data.get('away_position', '?')} | Points: {leg_data.get('away_points', 0)}")
    
    st.divider()
    
    st.markdown("### 📜 Head-to-Head Record")
    st.info(f"**All-time:** {leg_data.get('h2h_record', 'No data')}")
    st.info(f"**Last 6 meetings:** {leg_data.get('h2h_last6', 'No data')}")

# ========== FORENSIC TAB ==========
def show_forensic_tab(match, fdata):
    st.markdown("### M4: Pre-filter")
    st.info("6/8 checks passed - C5 (Bounce-back Rate) failed")
    
    st.markdown("### M5: Forensic Failures")
    st.warning("⚠️ New Manager Bounce (underdog) - +2.0 pts")
    st.warning("⚠️ High Draw Probability (25%) - +1.0 pts")
    st.success("Total Failure Score: 2.5 / 4.5 → PASS")
    
    st.markdown("### M6: Personnel")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"{match.get('home', 'Home')}", "82/100", "Healthy")
        st.write("Injuries: None")
    with col2:
        st.metric(f"{match.get('away', 'Away')}", "65/100", "1 injury")
        st.write("Injuries: 1 (midfielder)")
    
    st.markdown("### M7: AI Consensus")
    st.write("DeepSeek: ✅ APPROVE | Claude: ✅ APPROVE | Gemini: ⚠️ CAUTION | GPT: ✅ APPROVE")
    st.success("Consensus: 3/4 APPROVE")
    
    st.markdown("### M8: Dual Pattern")
    if "CONFLICT" in fdata.get('verdict_reason', ''):
        st.error("🚨 H2H CONFLICT DETECTED - HARD REJECT")
    else:
        st.info("Dual Risk Level: LOW | Underdog Threat: NONE")
    
    st.markdown("### M9: Underdog Scanner")
    st.metric("Underdog Edge", f"{match.get('edge', 0):+.1f}%")
    
    st.markdown("### M10: Tally Matrix")
    st.success("Bilateral Prediction: HOME (HIGH confidence)")
    
    st.markdown("### M26: Match Context")
    st.write("Match Importance: 72% | Is Rivalry: Yes")
    
    st.markdown("### M27: H2H Analysis")
    st.write("H2H Score: 78/100 (FAV_EDGE)")

# ========== MATCH DETAIL PAGE ==========
def show_match_detail():
    match = st.session_state.selected_match
    if match is None:
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
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Leg Data", "🔬 Full Forensic Report"])
    
    with tab1:
        show_leg_data(match, fdata)
    
    with tab2:
        show_forensic_tab(match, fdata)
    
    if fdata.get('status') == 'APPROVED':
        st.divider()
        stake = fdata.get('stake', 0)
        st.success(f"✅ FINAL VERDICT: APPROVED | Stake: £{stake:.2f}")

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.markdown('<p class="gold-header">MATCH ORACLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="gold-subheader">AI-Powered Football Intelligence • Elite Betting Analysis</p>', unsafe_allow_html=True)
    
    if st.session_state.backend_status == "connected":
        st.success(f"✅ BACKEND ONLINE")
    else:
        st.warning(f"⚠️ BACKEND OFFLINE - Using demo data")
    
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    st.markdown(f"## 📅 Today's Fixtures")
    st.caption(f"{len(MATCHES)} matches • {datetime.now(NAIROBI_TZ).strftime('%A, %B %d, %Y')}")
    st.markdown("---")
    
    for match in MATCHES:
        show_match_card(match)
    
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.caption("© 2025 Match Oracle • AI-powered football intelligence")

# ========== OTHER PAGES (Simplified) ==========
def show_performance():
    st.markdown('<p class="gold-header">📈 Performance Metrics</p>', unsafe_allow_html=True)
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
    st.markdown('<p class="gold-header">💰 Bankroll Manager</p>', unsafe_allow_html=True)
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
        st.write(f"{match.get('home')} vs {match.get('away')} - {match.get('league')} - {match.get('time')}")

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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Test Connection", use_container_width=True):
            check_backend()
            if st.session_state.backend_status == "connected":
                st.success("✅ Connected!")
            else:
                st.error("❌ Not connected")
    with col2:
        if st.button("🌐 Wake Up Backend", use_container_width=True):
            with st.spinner("Waking up..."):
                try:
                    response = requests.get(f"{st.session_state.backend_url}/health", timeout=60)
                    if response.status_code == 200:
                        st.session_state.backend_status = "connected"
                        st.success("✅ Backend is online!")
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
