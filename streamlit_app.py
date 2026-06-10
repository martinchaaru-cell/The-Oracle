import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests
import sys
import os
import pytz

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== TIMEZONE CONFIGURATION ==========
NAIROBI_TZ = pytz.timezone('Africa/Nairobi')  # GMT+3

def get_current_time():
    """Get current time in GMT+3 (Nairobi timezone)"""
    return datetime.now(NAIROBI_TZ)

def format_time(dt):
    """Format datetime to readable string"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# ========== ENVIRONMENT VARIABLES & SECRETS ==========
try:
    FOOTBALL_KEY = st.secrets.get("APIFOOTBALL_KEY", "")
    ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")
    BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")
except:
    FOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
    ODDS_KEY = os.getenv("ODDS_API_KEY", "")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
    .status-caution {
        background-color: #f59e0b20;
        color: #f59e0b;
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
    /* Status bar - positioned in sidebar area to avoid overlap */
    .status-container {
        position: fixed;
        bottom: 10px;
        left: 80px;
        right: 20px;
        background-color: #1e293b;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.7rem;
        color: #94a3b8;
        border: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 100;
        margin-left: 260px; /* Account for sidebar width */
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    /* Add padding to bottom of main content */
    .main-content {
        padding-bottom: 60px;
    }
    /* Ensure main content doesn't overlap */
    .block-container {
        padding-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== MOCK DATA ==========
MOCK_FIXTURES = [
    {"home": "Arsenal", "away": "Chelsea", "league": "Premier League", "time": "15:00", "odds": 2.10},
    {"home": "Manchester City", "away": "Liverpool", "league": "Premier League", "time": "17:30", "odds": 1.95},
    {"home": "Bayern Munich", "away": "Borussia Dortmund", "league": "Bundesliga", "time": "15:00", "odds": 1.75},
    {"home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "time": "20:00", "odds": 2.25},
    {"home": "Inter Milan", "away": "Juventus", "league": "Serie A", "time": "19:45", "odds": 2.05},
    {"home": "PSG", "away": "Marseille", "league": "Ligue 1", "time": "16:00", "odds": 1.55},
    {"home": "Ajax", "away": "Feyenoord", "league": "Eredivisie", "time": "14:30", "odds": 1.85},
]

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_leg" not in st.session_state:
    st.session_state.selected_leg = None
if "live_fixtures" not in st.session_state:
    st.session_state.live_fixtures = MOCK_FIXTURES
if "use_live_data" not in st.session_state:
    st.session_state.use_live_data = False
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"
if "data_source" not in st.session_state:
    st.session_state.data_source = "mock"

# ========== API CALLS ==========
def fetch_from_api_football(endpoint, params):
    """Direct API call to API-Football"""
    if not FOOTBALL_KEY:
        return None
    
    headers = {
        "x-apisports-key": FOOTBALL_KEY,
        "x-apisports-host": "v3.football.api-sports.io"
    }
    
    try:
        response = requests.get(f"https://v3.football.api-sports.io{endpoint}", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_live_fixtures():
    """Fetch live fixtures from API"""
    fixtures = []
    
    if FOOTBALL_KEY:
        with st.spinner("Fetching live fixtures..."):
            params = {"date": get_current_time().strftime("%Y-%m-%d"), "status": "NS"}
            data = fetch_from_api_football("/fixtures", params)
            
            if data and data.get("response"):
                for fx in data["response"][:20]:
                    home = fx.get("teams", {}).get("home", {}).get("name", "?")
                    away = fx.get("teams", {}).get("away", {}).get("name", "?")
                    league = fx.get("league", {}).get("name", "?")
                    date_str = fx.get("fixture", {}).get("date", "")
                    time_str = date_str[11:16] if date_str and len(date_str) > 10 else "TBD"
                    
                    fixtures.append({
                        "home": home,
                        "away": away,
                        "league": league,
                        "time": time_str,
                        "odds": 2.00
                    })
                
                if fixtures:
                    st.session_state.data_source = "api-football"
                    return fixtures
    
    st.session_state.data_source = "mock"
    return MOCK_FIXTURES

def check_backend():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        st.session_state.backend_status = "connected" if response.status_code == 200 else "disconnected"
    except:
        st.session_state.backend_status = "disconnected"

# ========== HELPER FUNCTIONS ==========
def get_status_badge(status):
    if status == "APPROVED":
        return '<span class="status-approved">✅ APPROVED</span>'
    elif status == "CAUTION":
        return '<span class="status-caution">⚠️ CAUTION</span>'
    return '<span class="status-rejected">❌ REJECTED</span>'

def navigate_to(page, leg=None):
    st.session_state.page = page
    if leg:
        st.session_state.selected_leg = leg
    st.rerun()

# ========== STATUS BAR COMPONENT ==========
def show_status_bar():
    """Display status bar at bottom of sidebar area to avoid overlap"""
    source_text = "🔴 LIVE" if st.session_state.data_source == "api-football" else "📊 DEMO"
    source_class = "live-badge" if st.session_state.data_source == "api-football" else "demo-badge"
    backend_status_text = "✅ Backend OK" if st.session_state.backend_status == "connected" else "⚠️ Backend Offline"
    current_time = format_time(get_current_time())
    
    # Status bar in sidebar area (not overlapping with Streamlit's manage app button)
    with st.sidebar:
        st.divider()
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📡 {st.session_state.data_source.upper()}")
        with col2:
            st.caption(f"🕐 {get_current_time().strftime('%H:%M:%S')}")
        st.caption(f"🔌 {backend_status_text}")
        st.caption(f"🎯 Match Oracle v3.0")
    
    # Also show compact version in main area footer
    st.markdown(f"""
    <div style="position: fixed; bottom: 5px; right: 10px; background-color: #1e293b; padding: 4px 12px; border-radius: 20px; font-size: 0.65rem; color: #64748b; z-index: 1000;">
        {get_current_time().strftime('%H:%M:%S')} GMT+3 | {st.session_state.data_source.upper()}
    </div>
    """, unsafe_allow_html=True)

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown('<p class="main-header">🎯 MATCH ORACLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered football prediction platform</p>', unsafe_allow_html=True)
    
    st.divider()
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    fixtures = st.session_state.live_fixtures
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">$12,450</div>
            <div class="metric-label">Bankroll</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(fixtures)}</div>
            <div class="metric-label">Today's Fixtures</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">$847</div>
            <div class="metric-label">Total Staked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">Grade B</div>
            <div class="metric-label">System Health</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Fetch live data button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📡 Fetch Live Fixtures", use_container_width=True):
            with st.spinner("Fetching from API-Football..."):
                st.session_state.live_fixtures = fetch_live_fixtures()
                st.rerun()
    
    # 3-Column Layout
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 🏆 Top Picks")
        for i, fixture in enumerate(fixtures[:3], 1):
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e293b,#0f172a);border-radius:10px;padding:0.8rem;margin-bottom:0.8rem;border-left:3px solid #3b82f6;">
                <div style="display:flex;justify-content:space-between;">
                    <b>#{i} {fixture.get('home', '?')} vs {fixture.get('away', '?')}</b>
                </div>
                <div style="font-size:0.8rem;color:#64748b;">{fixture.get('league', '?')} • {fixture.get('time', 'TBD')}</div>
                <div style="color:#10b981;">+{fixture.get('odds', 0)*5:.1f}% edge</div>
            </div>
            """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("### 📊 Data Source")
        if FOOTBALL_KEY:
            st.success("✅ API-Football Key Configured")
        else:
            st.warning("⚠️ No API Key")
            st.info("Add APIFOOTBALL_KEY to secrets")
    
    with c3:
        st.markdown("### 📈 Actions")
        if st.button("📋 View All Fixtures", use_container_width=True):
            navigate_to("all_legs")
        
        toggle = st.toggle("Use Live API", value=st.session_state.use_live_data)
        if toggle != st.session_state.use_live_data:
            st.session_state.use_live_data = toggle
            if toggle:
                st.session_state.live_fixtures = fetch_live_fixtures()
            else:
                st.session_state.live_fixtures = MOCK_FIXTURES
            st.rerun()
    
    st.divider()
    
    # Fixtures Table
    st.markdown("### 📋 Today's Fixtures")
    
    for fixture in fixtures[:10]:
        st.markdown(f"""
        <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;">
                <div><b>{fixture.get('home', '?')} vs {fixture.get('away', '?')}</b></div>
                <span style="font-size:0.7rem;">{fixture.get('league', '?')}</span>
            </div>
            <div style="font-size:0.8rem;color:#64748b;">Kickoff: {fixture.get('time', 'TBD')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== ALL LEGS PAGE ==========
def show_all_legs():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown('<p class="main-header">📋 All Fixtures</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Team or league...", label_visibility="collapsed")
    with col2:
        if st.button("← Back", use_container_width=True):
            navigate_to("dashboard")
    
    fixtures = st.session_state.live_fixtures
    
    if search:
        s = search.lower()
        fixtures = [f for f in fixtures if 
                   s in f.get('home', '').lower() or 
                   s in f.get('away', '').lower() or 
                   s in f.get('league', '').lower()]
    
    if fixtures:
        st.markdown(f"### Showing {len(fixtures)} fixtures")
        
        for i, fixture in enumerate(fixtures):
            cols = st.columns([2, 1.5, 1, 1])
            with cols[0]:
                st.write(f"**{fixture.get('home', '?')} vs {fixture.get('away', '?')}**")
            with cols[1]:
                st.write(fixture.get('league', '?'))
            with cols[2]:
                st.write(fixture.get('time', 'TBD'))
            with cols[3]:
                if st.button("🔍 View", key=f"view_{i}"):
                    st.info("Oracle analysis will appear here")
            st.divider()
    else:
        st.info("No fixtures found")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== PARLAYS PAGE ==========
def show_parlays():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    fixtures = st.session_state.live_fixtures[:4]
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== CALENDAR PAGE ==========
def show_calendar():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown('<p class="main-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    date = st.date_input("Select Date", get_current_time().date())
    
    if st.button("🔍 Scan Selected Date", use_container_width=True):
        with st.spinner("Scanning fixtures..."):
            time.sleep(1)
            st.success(f"Scan complete for {date}")
    
    st.markdown("### 📊 Upcoming Fixtures")
    for fixture in st.session_state.live_fixtures[:5]:
        st.markdown(f"""
        <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
            <b>{fixture.get('home', '?')} vs {fixture.get('away', '?')}</b>
            <div style="font-size:0.8rem;">{fixture.get('league', '?')} • {fixture.get('time', 'TBD')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== SETTINGS PAGE ==========
def show_settings():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.markdown('<p class="main-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### API Configuration")
    
    if FOOTBALL_KEY:
        st.success("✅ API-Football Key Configured")
        st.code(f"Key: {FOOTBALL_KEY[:8]}...{FOOTBALL_KEY[-4:]}")
    else:
        st.error("❌ API-Football Key Missing")
        st.info("Add APIFOOTBALL_KEY to Streamlit secrets")
    
    st.markdown("### Backend Configuration")
    st.text_input("Backend URL", value=BACKEND_URL, disabled=True)
    
    if st.button("Test Backend Connection"):
        check_backend()
        if st.session_state.backend_status == "connected":
            st.success("✅ Backend connected!")
        else:
            st.error("❌ Cannot connect to backend")
    
    st.markdown("### Timezone")
    st.info("📍 Timezone: GMT+3 (Nairobi)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN ==========
def main():
    # Initial load
    if st.session_state.backend_status == "checking":
        check_backend()
    
    if not st.session_state.live_fixtures:
        st.session_state.live_fixtures = MOCK_FIXTURES
    
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
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            if st.session_state.use_live_data:
                st.session_state.live_fixtures = fetch_live_fixtures()
            else:
                st.session_state.live_fixtures = MOCK_FIXTURES
            st.rerun()
    
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
    
    # Status bar (now in sidebar + compact footer)
    show_status_bar()

if __name__ == "__main__":
    main()
