import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests
import sys
import os

# ========== ADD BACKEND MODULES TO PATH ==========
# This allows importing your existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== ENVIRONMENT VARIABLES & SECRETS ==========
# Try to get from secrets (Streamlit Cloud) or environment (local)
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
    .status-rejected {
        background-color: #ef444420;
        color: #ef4444;
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
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ========== IMPORT YOUR M1 MODULE ==========
try:
    from module1 import load_todays_legs, LEAGUE_MAP
    M1_AVAILABLE = True
except ImportError as e:
    st.warning(f"M1 module not available: {e}. Using mock data.")
    M1_AVAILABLE = False
    LEAGUE_MAP = {
        39: {"label": "Premier League", "country": "england", "tier": 1},
        140: {"label": "La Liga", "country": "spain", "tier": 1},
        78: {"label": "Bundesliga", "country": "germany", "tier": 1},
        135: {"label": "Serie A", "country": "italy", "tier": 1},
        61: {"label": "Ligue 1", "country": "france", "tier": 1},
    }

# ========== DIRECT API-FOOTBALL CALLS (Fallback) ==========
API_FOOTBALL_URL = "https://v3.football.api-sports.io"

def fetch_from_api_football(endpoint, params):
    """Direct API call to API-Football"""
    if not FOOTBALL_KEY:
        return None
    
    headers = {
        "x-apisports-key": FOOTBALL_KEY,
        "x-apisports-host": "v3.football.api-sports.io"
    }
    
    try:
        response = requests.get(f"{API_FOOTBALL_URL}{endpoint}", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.warning(f"API-Football error: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_live_fixtures(league_id=39):
    """Fetch live fixtures using M1 module or direct API"""
    
    # Try M1 module first
    if M1_AVAILABLE and FOOTBALL_KEY and ODDS_KEY:
        try:
            legs = load_todays_legs(
                football_key=FOOTBALL_KEY,
                odds_key=ODDS_KEY,
                league_ids=[league_id],
                verbose=False,
                use_mock=False
            )
            return legs
        except Exception as e:
            st.warning(f"M1 module error: {e}. Falling back to direct API.")
    
    # Fallback to direct API
    params = {
        "league": league_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "season": 2025,
        "status": "NS"
    }
    data = fetch_from_api_football("/fixtures", params)
    if data and data.get("response"):
        return data["response"]
    return []

@st.cache_data(ttl=3600)
def fetch_standings(league_id=39):
    """Fetch league standings"""
    params = {"league": league_id, "season": 2025}
    data = fetch_from_api_football("/standings", params)
    if data and data.get("response"):
        return data["response"]
    return []

@st.cache_data(ttl=3600)
def fetch_team_stats(team_id):
    """Fetch team statistics"""
    params = {"team": team_id, "season": 2025}
    data = fetch_from_api_football("/teams/statistics", params)
    if data and data.get("response"):
        return data["response"]
    return None

# ========== BACKEND API CALLS ==========
def fetch_from_backend(endpoint):
    """Fetch data from your deployed backend"""
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def trigger_backend_scan(date_str):
    """Trigger pipeline scan via backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/frontend/scan/{date_str}", timeout=30)
        return response.status_code == 200
    except:
        return False

# ========== MOCK DATA FALLBACK ==========
MOCK_LEGS = [
    {"id": 1, "home": "Arsenal", "away": "Chelsea", "league": "Premier League", 
     "selection": "Arsenal", "odds": 2.10, "prob": 62, "edge": 8.1, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 2, "home": "Bayern Munich", "away": "Dortmund", "league": "Bundesliga",
     "selection": "Bayern Munich", "odds": 1.75, "prob": 58, "edge": 6.7, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 3, "home": "Inter Milan", "away": "Juventus", "league": "Serie A",
     "selection": "Inter Milan", "odds": 2.05, "prob": 55, "edge": 4.2, "status": "APPROVED", "confidence": "MEDIUM"},
]

MOCK_STANDINGS = {
    "Premier League": [
        {"position": 1, "team": "Arsenal", "played": 38, "points": 89, "form": "WWDWW"},
        {"position": 2, "team": "Man City", "played": 38, "points": 85, "form": "WWLDW"},
        {"position": 3, "team": "Liverpool", "played": 38, "points": 82, "form": "WWWWD"},
    ]
}

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_leg" not in st.session_state:
    st.session_state.selected_leg = None
if "live_fixtures" not in st.session_state:
    st.session_state.live_fixtures = []
if "use_live_data" not in st.session_state:
    st.session_state.use_live_data = True
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "checking"

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

def check_backend():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=3)
        st.session_state.backend_status = "connected" if response.status_code == 200 else "disconnected"
    except:
        st.session_state.backend_status = "disconnected"

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.markdown('<p class="main-header">🎯 MATCH ORACLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered football prediction platform</p>', unsafe_allow_html=True)
    
    # Status row
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.use_live_data and M1_AVAILABLE:
            st.markdown('<span class="live-badge">🔴 LIVE DATA</span>', unsafe_allow_html=True)
        else:
            st.info("📊 Using Demo Data")
    with col2:
        if st.session_state.backend_status == "connected":
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Offline")
    with col3:
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.divider()
    
    # Fetch live fixtures if enabled
    if st.session_state.use_live_data and M1_AVAILABLE:
        with st.spinner("Fetching live fixtures..."):
            # Try multiple leagues
            all_legs = []
            for league_id in [39, 140, 78, 135, 61]:  # Major leagues
                legs = fetch_live_fixtures(league_id)
                if legs:
                    all_legs.extend(legs)
            if all_legs:
                st.session_state.live_fixtures = all_legs
                st.success(f"Loaded {len(all_legs)} fixtures from {len([39,140,78,135,61])} leagues")
            else:
                st.warning("No live fixtures found. Using demo data.")
                st.session_state.live_fixtures = MOCK_LEGS
    else:
        st.session_state.live_fixtures = MOCK_LEGS
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">$12,450</div>
            <div class="metric-label">Bankroll</div>
            <div style="font-size:0.7rem;color:#ef4444;">▼ 5.7% from peak</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m2:
        total_legs = len(st.session_state.live_fixtures)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_legs}</div>
            <div class="metric-label">Today's Fixtures</div>
            <div style="font-size:0.7rem;color:#10b981;">▲ Live from API</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">$847</div>
            <div class="metric-label">Total Staked</div>
            <div style="font-size:0.7rem;color:#10b981;">▲ $2,150 potential</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">Grade B</div>
            <div class="metric-label">System Health</div>
            <div style="font-size:0.7rem;">58% accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 3-Column Layout
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 🏆 Top Picks")
        # Show first 3 fixtures as picks
        for i, leg in enumerate(st.session_state.live_fixtures[:3], 1):
            if isinstance(leg, dict):
                home = leg.get("teams", {}).get("home", {}).get("name", "?")
                away = leg.get("teams", {}).get("away", {}).get("name", "?")
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1e293b,#0f172a);border-radius:10px;padding:0.8rem;margin-bottom:0.8rem;border-left:3px solid #3b82f6;">
                    <div style="display:flex;justify-content:space-between;">
                        <b>#{i} {home} vs {away}</b>
                        <span class="status-approved">LIVE</span>
                    </div>
                    <div style="font-size:0.8rem;color:#64748b;">Kickoff: Today</div>
                </div>
                """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("### 📊 Data Source")
        if M1_AVAILABLE and FOOTBALL_KEY:
            st.success("✅ M1 Module Loaded")
            st.caption("Using your existing module1.py")
            st.code("from module1 import load_todays_legs", language="python")
        else:
            st.warning("⚠️ M1 Module Not Available")
            st.caption("Make sure module1.py is in the same directory")
        
        st.markdown("### 🔌 Backend Status")
        if st.session_state.backend_status == "connected":
            st.success(f"Connected to {BACKEND_URL}")
        else:
            st.error("Backend not reachable")
    
    with c3:
        st.markdown("### 📈 Quick Actions")
        if st.button("🔄 Refresh Live Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📋 View All Fixtures", use_container_width=True):
            navigate_to("all_legs")
        
        toggle = st.toggle("Use Live Data", value=st.session_state.use_live_data)
        if toggle != st.session_state.use_live_data:
            st.session_state.use_live_data = toggle
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # Live Fixtures Table
    st.markdown("### 📋 Today's Live Fixtures")
    
    if st.session_state.live_fixtures:
        for fixture in st.session_state.live_fixtures[:10]:
            if isinstance(fixture, dict):
                home = fixture.get("teams", {}).get("home", {}).get("name", "?")
                away = fixture.get("teams", {}).get("away", {}).get("name", "?")
                date_str = fixture.get("fixture", {}).get("date", "")
                time_str = date_str[11:16] if date_str else "TBD"
                league = fixture.get("league", {}).get("name", "?")
                
                st.markdown(f"""
                <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
                    <div style="display:flex;justify-content:space-between;">
                        <div><b>{home} vs {away}</b> <span style="font-size:0.7rem;">{league}</span></div>
                        <span class="live-badge">LIVE</span>
                    </div>
                    <div style="font-size:0.8rem;color:#64748b;">Kickoff: {time_str}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No live fixtures available. Check API key or try demo mode.")
    
    st.divider()
    
    # League Standings Preview
    st.markdown("### 🏆 League Standings")
    league_id = st.selectbox("Select League", [39, 140, 78], format_func=lambda x: {39: "Premier League", 140: "La Liga", 78: "Bundesliga"}.get(x, "Unknown"))
    
    standings = fetch_standings(league_id)
    if standings:
        for league_data in standings:
            if league_data.get("league", {}).get("id") == league_id:
                for entry in league_data.get("league", {}).get("standings", [[]])[0][:5]:
                    st.write(f"{entry.get('rank')}. {entry.get('team', {}).get('name')} - {entry.get('points')} pts")
    else:
        # Show mock standings
        for standing in MOCK_STANDINGS.get("Premier League", [])[:5]:
            st.write(f"{standing['position']}. {standing['team']} - {standing['points']} pts")

# ========== ALL LEGS PAGE ==========
def show_all_legs():
    st.markdown('<p class="main-header">📋 All Fixtures</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Team or league...", label_visibility="collapsed")
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        if st.button("← Back", use_container_width=True):
            navigate_to("dashboard")
    
    fixtures = st.session_state.live_fixtures
    
    if search:
        s = search.lower()
        fixtures = [f for f in fixtures if s in str(f).lower()]
    
    if fixtures:
        st.markdown(f"### Showing {len(fixtures)} fixtures")
        for fixture in fixtures[:20]:
            if isinstance(fixture, dict):
                home = fixture.get("teams", {}).get("home", {}).get("name", "?")
                away = fixture.get("teams", {}).get("away", {}).get("name", "?")
                league = fixture.get("league", {}).get("name", "?")
                date_str = fixture.get("fixture", {}).get("date", "")
                time_str = date_str[11:16] if date_str else "TBD"
                
                cols = st.columns([2, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{home} vs {away}**")
                with cols[1]:
                    st.write(league)
                with cols[2]:
                    st.write(time_str)
                with cols[3]:
                    if st.button("🔍 View", key=f"view_{fixture.get('fixture', {}).get('id', 0)}"):
                        st.info("Forensic report available when pipeline runs")
                st.divider()
    else:
        st.info("No fixtures found")

# ========== PARLAYS PAGE ==========
def show_parlays():
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    # Build parlays from live fixtures
    fixtures = st.session_state.live_fixtures[:4]
    
    st.markdown("### 🟢 Safe Parlay (2 legs)")
    if len(fixtures) >= 2:
        f1, f2 = fixtures[0], fixtures[1]
        home1 = f1.get("teams", {}).get("home", {}).get("name", "?")
        home2 = f2.get("teams", {}).get("home", {}).get("name", "?")
        st.markdown(f"**{home1} (2.10) + {home2} (1.85) = 3.89x**")
        st.caption("Combined Probability: 42% | Risk: SAFE")
    
    st.divider()
    
    st.markdown("### 🟡 Balanced Parlay (3 legs)")
    if len(fixtures) >= 3:
        f1, f2, f3 = fixtures[0], fixtures[1], fixtures[2]
        home1 = f1.get("teams", {}).get("home", {}).get("name", "?")
        home2 = f2.get("teams", {}).get("home", {}).get("name", "?")
        home3 = f3.get("teams", {}).get("home", {}).get("name", "?")
        st.markdown(f"**{home1} (2.10) + {home2} (1.85) + {home3} (1.95) = 7.58x**")
        st.caption("Combined Probability: 28% | Risk: BALANCED")
    
    st.divider()
    
    st.markdown("### 🔴 Aggressive Parlay (4 legs)")
    if len(fixtures) >= 4:
        f1, f2, f3, f4 = fixtures[0], fixtures[1], fixtures[2], fixtures[3]
        home1 = f1.get("teams", {}).get("home", {}).get("name", "?")
        home2 = f2.get("teams", {}).get("home", {}).get("name", "?")
        home3 = f3.get("teams", {}).get("home", {}).get("name", "?")
        home4 = f4.get("teams", {}).get("home", {}).get("name", "?")
        st.markdown(f"**{home1} (2.10) + {home2} (1.85) + {home3} (1.95) + {home4} (1.75) = 13.27x**")
        st.caption("Combined Probability: 15% | Risk: AGGRESSIVE")

# ========== CALENDAR PAGE ==========
def show_calendar():
    st.markdown('<p class="main-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    date = st.date_input("Select Date", datetime.now().date())
    
    if st.button("🔍 Scan Selected Date", use_container_width=True):
        with st.spinner("Scanning fixtures..."):
            # Try backend first
            if trigger_backend_scan(date.strftime("%Y-%m-%d")):
                st.success(f"Backend scan complete for {date}")
            else:
                st.warning(f"Backend not available. Using direct API for {date}")
            
            # Also fetch directly
            params = {"date": date.strftime("%Y-%m-%d")}
            fixtures = fetch_from_api_football("/fixtures", params)
            if fixtures:
                st.session_state.live_fixtures = fixtures.get("response", [])
                st.rerun()
    
    st.markdown("### 📊 Upcoming Fixtures")
    for fixture in st.session_state.live_fixtures[:5]:
        if isinstance(fixture, dict):
            home = fixture.get("teams", {}).get("home", {}).get("name", "?")
            away = fixture.get("teams", {}).get("away", {}).get("name", "?")
            st.markdown(f"""
            <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
                <b>{home} vs {away}</b>
            </div>
            """, unsafe_allow_html=True)

# ========== LEG DETAIL PAGE ==========
def show_leg_detail():
    leg = st.session_state.selected_leg
    if not leg:
        st.warning("No selection")
        if st.button("← Back"):
            navigate_to("all_legs")
        return
    
    home = leg.get("teams", {}).get("home", {}).get("name", "?") if isinstance(leg, dict) else "?"
    away = leg.get("teams", {}).get("away", {}).get("name", "?") if isinstance(leg, dict) else "?"
    
    st.markdown(f'<p class="main-header">🔬 {home} vs {away}</p>', unsafe_allow_html=True)
    
    if st.button("← Back"):
        navigate_to("all_legs")
    
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Match Info", "🔬 Oracle Analysis"])
    
    with tab1:
        if isinstance(leg, dict):
            st.json({
                "Home Team": home,
                "Away Team": away,
                "League": leg.get("league", {}).get("name", "?"),
                "Date": leg.get("fixture", {}).get("date", "?"),
                "Venue": leg.get("fixture", {}).get("venue", {}).get("name", "?"),
                "Status": leg.get("fixture", {}).get("status", {}).get("long", "?")
            })
    
    with tab2:
        st.info("Oracle analysis will appear when pipeline is run on this fixture")

# ========== SETTINGS PAGE ==========
def show_settings():
    st.markdown('<p class="main-header">⚙️ Settings</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### Data Source Configuration")
    
    st.session_state.use_live_data = st.toggle("Enable Live Data from API-Football", value=st.session_state.use_live_data)
    
    if FOOTBALL_KEY:
        st.success("✅ API-Football key configured")
        st.code(f"Key: {FOOTBALL_KEY[:8]}...{FOOTBALL_KEY[-4:]}")
    else:
        st.error("❌ API-Football key not found")
        st.info("Add APIFOOTBALL_KEY to Streamlit secrets or environment variables")
    
    st.markdown("### Backend Configuration")
    st.text_input("Backend URL", value=BACKEND_URL, disabled=True)
    
    if st.button("Test Backend Connection"):
        check_backend()
        if st.session_state.backend_status == "connected":
            st.success("Backend connected successfully!")
        else:
            st.error("Cannot connect to backend")

# ========== MAIN ==========
def main():
    # Check backend status on startup
    if st.session_state.backend_status == "checking":
        check_backend()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        nav_options = ["📊 Dashboard", "📋 All Legs", "🔗 Parlays", "📅 Calendar", "⚙️ Settings"]
        for option in nav_options:
            if st.button(option, use_container_width=True):
                page_map = {
                    "📊 Dashboard": "dashboard",
                    "📋 All Legs": "all_legs",
                    "🔗 Parlays": "parlays",
                    "📅 Calendar": "calendar",
                    "⚙️ Settings": "settings"
                }
                navigate_to(page_map[option])
        
        st.divider()
        
        if st.button("🔄 Refresh All Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        if st.session_state.backend_status == "connected":
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Offline")
        
        st.divider()
        
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("🎯 Match Oracle v3.0")
        
        if M1_AVAILABLE:
            st.caption("✅ M1 Module Active")
        else:
            st.caption("⚠️ M1 Module Missing")
    
    # Page routing
    page = st.session_state.page
    if page == "dashboard":
        show_dashboard()
    elif page == "all_legs":
        show_all_legs()
    elif page == "leg_detail":
        show_leg_detail()
    elif page == "parlays":
        show_parlays()
    elif page == "calendar":
        show_calendar()
    elif page == "settings":
        show_settings()

if __name__ == "__main__":
    main()
