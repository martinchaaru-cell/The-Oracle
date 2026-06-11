import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests
import sys
import os
import pytz
import threading

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== TIMEZONE CONFIGURATION ==========
NAIROBI_TZ = pytz.timezone('Africa/Nairobi')

def get_current_time():
    return datetime.now(NAIROBI_TZ)

def format_time(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# ========== BACKEND CONFIGURATION ==========
try:
    BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")
except:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# API-Football key (will be used by backend, not directly by frontend)
try:
    FOOTBALL_KEY = st.secrets.get("APIFOOTBALL_KEY", "")
except:
    FOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header { color: #64748b; font-size: 0.9rem; margin-bottom: 1rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #334155;
    }
    .metric-value { font-size: 1.8rem; font-weight: bold; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; }
    .status-approved {
        background-color: #10b98120;
        color: #10b981;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    .live-badge {
        background-color: #ef4444;
        color: white;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
        animation: pulse 1s infinite;
    }
    .demo-badge {
        background-color: #f59e0b;
        color: white;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }
    .real-badge {
        background-color: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }
    .status-tab {
        display: inline-block;
        padding: 4px 12px;
        margin-right: 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        cursor: pointer;
    }
    .status-tab-active {
        background-color: #3b82f6;
        color: white;
    }
    .status-tab-inactive {
        background-color: #1e293b;
        color: #94a3b8;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ========== COMPLETE MOCK DATA (Fallback when backend unavailable) ==========
MOCK_FIXTURES = {
    "upcoming": [
        {"id": 1, "home": "Arsenal", "away": "Chelsea", "league": "Premier League", "time": "15:00", "odds": 2.10, "status": "NS"},
        {"id": 2, "home": "Manchester City", "away": "Liverpool", "league": "Premier League", "time": "17:30", "odds": 1.95, "status": "NS"},
        {"id": 3, "home": "Bayern Munich", "away": "Borussia Dortmund", "league": "Bundesliga", "time": "15:00", "odds": 1.75, "status": "NS"},
        {"id": 4, "home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "time": "20:00", "odds": 2.25, "status": "NS"},
        {"id": 5, "home": "Inter Milan", "away": "Juventus", "league": "Serie A", "time": "19:45", "odds": 2.05, "status": "NS"},
        {"id": 6, "home": "PSG", "away": "Marseille", "league": "Ligue 1", "time": "16:00", "odds": 1.55, "status": "NS"},
    ],
    "live": [
        {"id": 7, "home": "AC Milan", "away": "Roma", "league": "Serie A", "time": "Live 67'", "home_score": 2, "away_score": 1, "odds": 1.85, "status": "LIVE"},
    ],
    "finished": [
        {"id": 8, "home": "Tottenham", "away": "Man United", "league": "Premier League", "time": "FT", "home_score": 1, "away_score": 1, "result": "DRAW", "status": "FT"},
    ]
}

MOCK_FORENSIC = {
    "m4": {"passed": True, "checksPassed": 6, "checksTotal": 8},
    "m5": {"failureScore": 2.5, "passed": True},
    "m6": {"homeScore": 82, "awayScore": 65},
    "m7": {"consensus": "APPROVE", "agreement": 0.78},
    "m8": {"dualRiskLevel": "LOW", "underdogThreat": "LOW"},
    "m9": {"underdogEdge": -0.021, "threatLevel": "LOW"},
    "m10": {"matrixUseful": True, "bilateralPrediction": "HOME"},
    "m26": {"matchImportance": 0.72, "isRivalry": True},
    "m27": {"h2hScore": 78, "h2hLabel": "FAV_EDGE"},
    "riskFlags": ["Pattern clash moderate"],
    "finalStatus": "APPROVED",
    "finalConfidence": "HIGH",
    "weightedScore": 0.78
}

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_leg" not in st.session_state:
    st.session_state.selected_leg = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "upcoming"
if "data_source" not in st.session_state:
    st.session_state.data_source = "mock"
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"
if "fixtures" not in st.session_state:
    st.session_state.fixtures = MOCK_FIXTURES
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = get_current_time()

# ========== BACKEND API CALLS (Auto-detects real data) ==========
def check_backend():
    """Check if backend is available and has real data endpoints"""
    try:
        # Check health endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if response.status_code != 200:
            st.session_state.backend_status = "disconnected"
            return False
        
        # Try to fetch real fixtures (if endpoint exists)
        fixtures_response = requests.get(f"{BACKEND_URL}/api/fixtures/today", timeout=5)
        if fixtures_response.status_code == 200:
            data = fixtures_response.json()
            if data.get("response") and len(data.get("response", [])) > 0:
                st.session_state.backend_status = "connected_real"
                st.session_state.data_source = "real"
                return True
        
        # Backend connected but no real data endpoint
        st.session_state.backend_status = "connected_demo"
        st.session_state.data_source = "mock"
        return False
        
    except requests.exceptions.ConnectionError:
        st.session_state.backend_status = "disconnected"
        st.session_state.data_source = "mock"
        return False
    except Exception as e:
        st.session_state.backend_status = "disconnected"
        st.session_state.data_source = "mock"
        return False

def fetch_real_fixtures():
    """Fetch real fixtures from backend (when available)"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/fixtures/today", timeout=10)
        if response.status_code == 200:
            data = response.json()
            fixtures = {"upcoming": [], "live": [], "finished": []}
            
            for fx in data.get("response", []):
                status = fx.get("fixture", {}).get("status", {}).get("short", "NS")
                fixture_data = {
                    "id": fx.get("fixture", {}).get("id"),
                    "home": fx.get("teams", {}).get("home", {}).get("name", "?"),
                    "away": fx.get("teams", {}).get("away", {}).get("name", "?"),
                    "league": fx.get("league", {}).get("name", "?"),
                    "time": fx.get("fixture", {}).get("date", "")[11:16] if fx.get("fixture", {}).get("date") else "TBD",
                }
                
                if status in ["NS"]:
                    fixtures["upcoming"].append(fixture_data)
                elif status in ["1H", "HT", "2H"]:
                    fixtures["live"].append(fixture_data)
                elif status in ["FT", "AET", "PEN"]:
                    fixtures["finished"].append(fixture_data)
            
            if any(fixtures.values()):
                return fixtures
    
    except Exception as e:
        pass
    
    return None

def fetch_forensic_report(leg_id):
    """Fetch forensic report from backend when available"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/legs/{leg_id}/forensic", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return MOCK_FORENSIC

def refresh_fixtures():
    """Refresh fixtures data - tries real backend first, falls back to mock"""
    with st.spinner("Refreshing fixtures..."):
        if st.session_state.backend_status == "connected_real":
            real_fixtures = fetch_real_fixtures()
            if real_fixtures:
                st.session_state.fixtures = real_fixtures
                st.session_state.data_source = "real"
                st.session_state.last_refresh = get_current_time()
                return
    
    # Fallback to mock
    st.session_state.fixtures = MOCK_FIXTURES
    st.session_state.data_source = "mock"
    st.session_state.last_refresh = get_current_time()

# ========== HELPER FUNCTIONS ==========
def get_status_badge(status):
    if status == "APPROVED":
        return '<span class="status-approved">✅ APPROVED</span>'
    return '<span class="status-approved">⚠️ PENDING</span>'

def navigate_to(page, leg=None):
    st.session_state.page = page
    if leg:
        st.session_state.selected_leg = leg
    st.rerun()

def get_data_source_badge():
    if st.session_state.data_source == "real":
        return '<span class="real-badge">🔴 LIVE DATA</span>'
    elif st.session_state.data_source == "mock":
        return '<span class="demo-badge">📊 DEMO DATA</span>'
    return '<span class="demo-badge">📊 DEMO DATA</span>'

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.markdown('<p class="main-header">🎯 MATCH ORACLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered football prediction platform</p>', unsafe_allow_html=True)
    
    # Status bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(get_data_source_badge(), unsafe_allow_html=True)
    with col2:
        if st.session_state.backend_status == "connected_real":
            st.success("✅ Backend (Live)")
        elif st.session_state.backend_status == "connected_demo":
            st.warning("⚠️ Backend (Demo Mode)")
        else:
            st.error("❌ Backend Offline")
    with col3:
        st.caption(f"🕐 Last refresh: {format_time(st.session_state.last_refresh)}")
    with col4:
        if st.button("🔄 Refresh", use_container_width=True):
            refresh_fixtures()
            st.rerun()
    
    st.divider()
    
    # Status Tabs
    tab_cols = st.columns(3)
    with tab_cols[0]:
        upcoming_class = "status-tab-active" if st.session_state.active_tab == "upcoming" else "status-tab-inactive"
        if st.button("📅 Upcoming", key="tab_upcoming", use_container_width=True):
            st.session_state.active_tab = "upcoming"
            st.rerun()
    with tab_cols[1]:
        if st.button("🔴 Live", key="tab_live", use_container_width=True):
            st.session_state.active_tab = "live"
            st.rerun()
    with tab_cols[2]:
        if st.button("✅ Finished", key="tab_finished", use_container_width=True):
            st.session_state.active_tab = "finished"
            st.rerun()
    
    st.divider()
    
    # Auto-refresh toggle
    auto_refresh_col1, auto_refresh_col2 = st.columns([1, 3])
    with auto_refresh_col1:
        st.session_state.auto_refresh = st.checkbox("Auto-refresh (60s)", value=st.session_state.auto_refresh)
    
    # Display fixtures based on active tab
    fixtures = st.session_state.fixtures.get(st.session_state.active_tab, [])
    
    if st.session_state.active_tab == "upcoming":
        st.markdown("### 📋 Upcoming Fixtures")
        for fixture in fixtures:
            st.markdown(f"""
            <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;">
                    <div><b>{fixture.get('home', '?')} vs {fixture.get('away', '?')}</b></div>
                    <span style="font-size:0.7rem;">{fixture.get('league', '?')}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:0.5rem;">
                    <span style="color:#64748b;">Kickoff: {fixture.get('time', 'TBD')}</span>
                    <span class="status-approved">PRE-MATCH</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif st.session_state.active_tab == "live":
        st.markdown("### 🔴 Live Matches")
        if fixtures:
            for fixture in fixtures:
                home_score = fixture.get('home_score', 0)
                away_score = fixture.get('away_score', 0)
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#ef444420,#1e293b);border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;border-left:3px solid #ef4444;">
                    <div style="display:flex;justify-content:space-between;">
                        <div><b>{fixture.get('home', '?')} {home_score} - {away_score} {fixture.get('away', '?')}</b></div>
                        <span class="live-badge">LIVE</span>
                    </div>
                    <div style="font-size:0.8rem;color:#64748b;">{fixture.get('time', 'In Progress')} • {fixture.get('league', '?')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No live matches at the moment")
    
    elif st.session_state.active_tab == "finished":
        st.markdown("### ✅ Recent Results")
        for fixture in fixtures:
            result_icon = "🟡" if fixture.get('result') == "DRAW" else ("🟢" if fixture.get('result') == "HOME" else "🔴")
            st.markdown(f"""
            <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
                <div style="display:flex;justify-content:space-between;">
                    <div><b>{fixture.get('home', '?')} {fixture.get('home_score', 0)} - {fixture.get('away_score', 0)} {fixture.get('away', '?')}</b></div>
                    <span>{result_icon} {fixture.get('result', 'FT')}</span>
                </div>
                <div style="font-size:0.8rem;color:#64748b;">{fixture.get('league', '?')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Auto-refresh logic
    if st.session_state.auto_refresh and st.session_state.data_source == "real":
        time.sleep(1)
        st.rerun()

# ========== ALL LEGS PAGE ==========
def show_all_legs():
    st.markdown('<p class="main-header">📋 All Fixtures</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Team or league...", label_visibility="collapsed")
    with col2:
        if st.button("← Back", use_container_width=True):
            navigate_to("dashboard")
    
    all_fixtures = []
    for category in ["upcoming", "live", "finished"]:
        all_fixtures.extend(st.session_state.fixtures.get(category, []))
    
    if search:
        s = search.lower()
        all_fixtures = [f for f in all_fixtures if 
                       s in f.get('home', '').lower() or 
                       s in f.get('away', '').lower() or 
                       s in f.get('league', '').lower()]
    
    if all_fixtures:
        st.markdown(f"### Showing {len(all_fixtures)} fixtures")
        
        for i, fixture in enumerate(all_fixtures):
            cols = st.columns([2, 1.5, 1, 1])
            with cols[0]:
                st.write(f"**{fixture.get('home', '?')} vs {fixture.get('away', '?')}**")
            with cols[1]:
                st.write(fixture.get('league', '?'))
            with cols[2]:
                st.write(fixture.get('time', 'TBD'))
            with cols[3]:
                if st.button("🔍 Forensic", key=f"view_{i}"):
                    forensic = fetch_forensic_report(fixture.get('id', i))
                    st.json(forensic)
            st.divider()
    else:
        st.info("No fixtures found")

# ========== PARLAYS PAGE ==========
def show_parlays():
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    fixtures = st.session_state.fixtures.get("upcoming", [])[:4]
    
    st.markdown("### 🟢 Safe Parlay (2 legs)")
    if len(fixtures) >= 2:
        f1, f2 = fixtures[0], fixtures[1]
        st.markdown(f"**{f1.get('home', '?')} (2.10) + {f2.get('home', '?')} (1.85) = 3.89x**")
    
    st.divider()
    
    st.markdown("### 🟡 Balanced Parlay (3 legs)")
    if len(fixtures) >= 3:
        f1, f2, f3 = fixtures[0], fixtures[1], fixtures[2]
        st.markdown(f"**{f1.get('home', '?')} (2.10) + {f2.get('home', '?')} (1.85) + {f3.get('home', '?')} (1.95) = 7.58x**")
    
    st.divider()
    
    st.markdown("### 🔴 Aggressive Parlay (4 legs)")
    if len(fixtures) >= 4:
        f1, f2, f3, f4 = fixtures[0], fixtures[1], fixtures[2], fixtures[3]
        st.markdown(f"**{f1.get('home', '?')} (2.10) + {f2.get('home', '?')} (1.85) + {f3.get('home', '?')} (1.95) + {f4.get('home', '?')} (1.75) = 13.27x**")
    
    st.caption("💡 Parlays are built from available fixtures. Real parlays will appear when backend data is available.")

# ========== CALENDAR PAGE ==========
def show_calendar():
    st.markdown('<p class="main-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    date = st.date_input("Select Date", get_current_time().date())
    
    if st.button("🔍 Scan Selected Date", use_container_width=True):
        with st.spinner("Scanning fixtures..."):
            time.sleep(1)
            st.success(f"Scan complete for {date}")
            if st.session_state.backend_status == "connected_real":
                refresh_fixtures()
    
    st.markdown("### 📊 Upcoming Fixtures")
    for fixture in st.session_state.fixtures.get("upcoming", [])[:5]:
        st.markdown(f"""
        <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
            <b>{fixture.get('home', '?')} vs {fixture.get('away', '?')}</b>
            <div style="font-size:0.8rem;">{fixture.get('league', '?')} • {fixture.get('time', 'TBD')}</div>
        </div>
        """, unsafe_allow_html=True)

# ========== SETTINGS PAGE ==========
def show_settings():
    st.markdown('<p class="main-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### Data Source Status")
    st.info(f"**Current Source:** {st.session_state.data_source.upper()}")
    st.caption("When backend endpoints are available, this will automatically switch to REAL data.")
    
    st.markdown("### Backend Configuration")
    st.text_input("Backend URL", value=BACKEND_URL, disabled=True)
    
    if st.button("Test Backend Connection"):
        check_backend()
        if st.session_state.backend_status == "connected_real":
            st.success("✅ Backend connected with REAL data!")
        elif st.session_state.backend_status == "connected_demo":
            st.warning("⚠️ Backend connected but using demo data")
        else:
            st.error("❌ Cannot connect to backend")
    
    st.markdown("### API-Football Status")
    if FOOTBALL_KEY:
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ API Key not configured (backend will use it)")
    
    st.markdown("### Timezone")
    st.info("📍 Timezone: GMT+3 (Nairobi)")
    
    st.markdown("---")
    st.markdown("### About")
    st.caption("Match Oracle v3.0")
    st.caption("When backend is ready, this app will automatically switch to live data.")
    st.caption("No restart needed - just click Refresh.")

# ========== MAIN ==========
def main():
    # Check backend status on startup
    if st.session_state.backend_status == "checking":
        check_backend()
        refresh_fixtures()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        nav_items = ["📊 Dashboard", "📋 All Legs", "🔗 Parlays", "📅 Calendar", "⚙️ Settings"]
        for item in nav_items:
            if st.button(item, use_container_width=True):
                page_map = {
                    "📊 Dashboard": "dashboard",
                    "📋 All Legs": "all_legs",
                    "🔗 Parlays": "parlays",
                    "📅 Calendar": "calendar",
                    "⚙️ Settings": "settings"
                }
                navigate_to(page_map[item])
        
        st.divider()
        
        if st.button("🔄 Refresh All", use_container_width=True):
            check_backend()
            refresh_fixtures()
            st.rerun()
        
        st.divider()
        
        # Status in sidebar
        if st.session_state.data_source == "real":
            st.success("🔴 LIVE DATA ACTIVE")
        else:
            st.info("📊 DEMO DATA (Backend ready? Click Refresh)")
        
        st.caption(f"🕐 {get_current_time().strftime('%H:%M:%S')}")
        st.caption(f"📡 Source: {st.session_state.data_source.upper()}")
    
    # Page routing
    page = st.session_state.page
    if page == "dashboard":
        show_dashboard()
    elif page == "all_legs":
        show_all_legs()
    elif page == "parlays":
        show_parlays()
    elif page == "calendar":
        show_calendar()
    elif page == "settings":
        show_settings()

if __name__ == "__main__":
    main()
