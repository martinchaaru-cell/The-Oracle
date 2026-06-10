import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import requests

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== BACKEND CONFIGURATION ==========
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")

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
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_leg" not in st.session_state:
    st.session_state.selected_leg = None
if "webSocket_status" not in st.session_state:
    st.session_state.webSocket_status = "disconnected"
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# ========== COMPLETE MOCK DATA (Matches Your UI Design) ==========
MOCK_DATA = {
    "bankroll": {"current": 12450, "peak": 13200, "drawdown": 5.7},
    "today_stats": {"total_legs": 47, "approved": 12, "rejected": 28, "caution": 7, "total_staked": 847, "potential_return": 2150},
    "system_health": {"grade": "B", "accuracy": 0.58},
    "top_picks": [
        {"match": "Arsenal vs Chelsea", "home": "Arsenal", "away": "Chelsea", "selection": "Arsenal", "odds": 2.10, "edge": 8.1, "confidence": "HIGH"},
        {"match": "Bayern Munich vs Dortmund", "home": "Bayern Munich", "away": "Dortmund", "selection": "Bayern Munich", "odds": 1.75, "edge": 6.7, "confidence": "HIGH"},
        {"match": "Inter Milan vs Juventus", "home": "Inter Milan", "away": "Juventus", "selection": "Inter Milan", "odds": 2.05, "edge": 4.2, "confidence": "MEDIUM"},
        {"match": "PSG vs Marseille", "home": "PSG", "away": "Marseille", "selection": "PSG", "odds": 1.55, "edge": 11.3, "confidence": "HIGH"},
    ],
    "legs_by_league": [
        {"league": "Premier League", "count": 12},
        {"league": "La Liga", "count": 10},
        {"league": "Bundesliga", "count": 8},
        {"league": "Serie A", "count": 8},
        {"league": "Ligue 1", "count": 6},
        {"league": "Eredivisie", "count": 3},
    ],
    "status_distribution": {"approved": 12, "rejected": 28, "caution": 7},
    "all_legs": [
        {"id": 1, "home": "Arsenal", "away": "Chelsea", "league": "Premier League", "kickoff": "15:00", 
         "selection": "Arsenal", "odds": 2.10, "prob": 62, "edge": 8.1, "status": "APPROVED", "confidence": "HIGH"},
        {"id": 2, "home": "Man City", "away": "Liverpool", "league": "Premier League", "kickoff": "17:30",
         "selection": "Man City", "odds": 1.95, "prob": 54, "edge": 2.2, "status": "CAUTION", "confidence": "MEDIUM"},
        {"id": 3, "home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "kickoff": "20:00",
         "selection": "Real Madrid", "odds": 2.25, "prob": 48, "edge": -1.7, "status": "REJECTED", "confidence": "LOW"},
        {"id": 4, "home": "Bayern Munich", "away": "Dortmund", "league": "Bundesliga", "kickoff": "15:00",
         "selection": "Bayern Munich", "odds": 1.75, "prob": 58, "edge": 6.7, "status": "APPROVED", "confidence": "HIGH"},
        {"id": 5, "home": "Inter Milan", "away": "Juventus", "league": "Serie A", "kickoff": "19:45",
         "selection": "Inter Milan", "odds": 2.05, "prob": 55, "edge": 4.2, "status": "APPROVED", "confidence": "MEDIUM"},
        {"id": 6, "home": "PSG", "away": "Marseille", "league": "Ligue 1", "kickoff": "16:00",
         "selection": "PSG", "odds": 1.55, "prob": 68, "edge": 11.3, "status": "APPROVED", "confidence": "HIGH"},
        {"id": 7, "home": "Ajax", "away": "Feyenoord", "league": "Eredivisie", "kickoff": "14:30",
         "selection": "Ajax", "odds": 1.85, "prob": 57, "edge": 5.1, "status": "APPROVED", "confidence": "HIGH"},
    ],
    "bankroll_history": [
        {"date": "Jun 1", "bankroll": 10000}, {"date": "Jun 2", "bankroll": 10250},
        {"date": "Jun 3", "bankroll": 10500}, {"date": "Jun 4", "bankroll": 10300},
        {"date": "Jun 5", "bankroll": 10800}, {"date": "Jun 6", "bankroll": 11200},
        {"date": "Jun 7", "bankroll": 11800}, {"date": "Jun 8", "bankroll": 12450},
    ],
    "parlays": {
        "safe": [
            {"legs": ["Arsenal (2.10)", "Bayern (1.75)"], "total_odds": 3.68, "prob": 36, "risk": "SAFE"},
            {"legs": ["PSG (1.55)", "Inter (2.05)"], "total_odds": 3.18, "prob": 42, "risk": "SAFE"},
        ],
        "balanced": [
            {"legs": ["Arsenal (2.10)", "Bayern (1.75)", "PSG (1.55)"], "total_odds": 5.70, "prob": 22, "risk": "BALANCED"},
        ],
        "aggressive": [
            {"legs": ["Arsenal (2.10)", "Bayern (1.75)", "Inter (2.05)", "Ajax (1.85)"], "total_odds": 13.95, "prob": 11, "risk": "AGGRESSIVE"},
        ],
    }
}

# ========== HELPER FUNCTIONS ==========
def fetch_from_backend(endpoint, fallback):
    """Try to fetch from backend, return fallback on failure"""
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, dict) and len(data) > 0:
                return data
        return fallback
    except Exception:
        return fallback

def load_data():
    """Load data with backend fallback"""
    with st.spinner("Loading data..."):
        # Test backend connection
        try:
            health = requests.get(f"{BACKEND_URL}/health", timeout=3)
            if health.status_code == 200:
                st.session_state.webSocket_status = "connected"
                # Try to fetch real data, but keep mock as fallback
                dashboard = fetch_from_backend("/frontend/dashboard", MOCK_DATA)
                legs = fetch_from_backend("/frontend/legs", MOCK_DATA["all_legs"])
                bankroll = fetch_from_backend("/frontend/bankroll", MOCK_DATA)
                performance = fetch_from_backend("/frontend/performance", MOCK_DATA)
                parlays = fetch_from_backend("/frontend/parlays", MOCK_DATA["parlays"])
            else:
                st.session_state.webSocket_status = "disconnected"
                dashboard, legs, bankroll, performance, parlays = MOCK_DATA, MOCK_DATA["all_legs"], MOCK_DATA, MOCK_DATA, MOCK_DATA["parlays"]
        except:
            st.session_state.webSocket_status = "disconnected"
            dashboard, legs, bankroll, performance, parlays = MOCK_DATA, MOCK_DATA["all_legs"], MOCK_DATA, MOCK_DATA, MOCK_DATA["parlays"]
        
        st.session_state.dashboard_data = dashboard if isinstance(dashboard, dict) else MOCK_DATA
        st.session_state.all_legs = legs if isinstance(legs, list) else MOCK_DATA["all_legs"]
        st.session_state.bankroll_data = bankroll if isinstance(bankroll, dict) else MOCK_DATA
        st.session_state.performance_data = performance if isinstance(performance, dict) else MOCK_DATA
        st.session_state.parlays_data = parlays if isinstance(parlays, dict) else MOCK_DATA["parlays"]

def navigate_to(page, leg=None):
    st.session_state.page = page
    if leg:
        st.session_state.selected_leg = leg
    st.rerun()

def get_status_badge(status):
    if status == "APPROVED":
        return '<span class="status-approved">✅ APPROVED</span>'
    elif status == "CAUTION":
        return '<span class="status-caution">⚠️ CAUTION</span>'
    return '<span class="status-rejected">❌ REJECTED</span>'

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    data = st.session_state.get("dashboard_data", MOCK_DATA)
    bankroll = st.session_state.get("bankroll_data", MOCK_DATA)
    perf = st.session_state.get("performance_data", MOCK_DATA)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<p class="main-header">🎯 MATCH ORACLE</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-powered football prediction platform</p>', unsafe_allow_html=True)
    with col2:
        status_color = "🟢" if st.session_state.webSocket_status == "connected" else "🔴"
        st.markdown(f"""
        <div style="text-align: right;">
            <span>{status_color} {st.session_state.webSocket_status.upper()}</span><br>
            <span style="font-size: 0.7rem;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    today_stats = data.get("today_stats", MOCK_DATA["today_stats"])
    
    with m1:
        current = bankroll.get("current", 12450)
        peak = bankroll.get("peak", 13200)
        drawdown = (peak - current) / peak * 100 if peak > 0 else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">${current:,.0f}</div><div class="metric-label">Bankroll</div><div style="font-size:0.7rem;color:#ef4444;">▼ {drawdown:.1f}% from peak</div></div>', unsafe_allow_html=True)
    
    with m2:
        total = today_stats.get("total_legs", 47)
        approved = today_stats.get("approved", 12)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Today\'s Legs</div><div style="font-size:0.7rem;color:#10b981;">▲ {approved} approved</div></div>', unsafe_allow_html=True)
    
    with m3:
        staked = today_stats.get("total_staked", 847)
        potential = today_stats.get("potential_return", 2150)
        st.markdown(f'<div class="metric-card"><div class="metric-value">${staked:,.0f}</div><div class="metric-label">Total Staked</div><div style="font-size:0.7rem;color:#10b981;">▲ ${potential:,.0f} potential</div></div>', unsafe_allow_html=True)
    
    with m4:
        grade = perf.get("system_health", {}).get("grade", "B") or "B"
        accuracy = perf.get("system_health", {}).get("accuracy", 0.58) or 0.58
        st.markdown(f'<div class="metric-card"><div class="metric-value">Grade {grade}</div><div class="metric-label">System Health</div><div style="font-size:0.7rem;">{accuracy:.0%} accuracy</div></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 3-Column Layout
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 🏆 Top Picks")
        picks = data.get("top_picks", MOCK_DATA["top_picks"])
        for i, pick in enumerate(picks[:3], 1):
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e293b,#0f172a);border-radius:10px;padding:0.8rem;margin-bottom:0.8rem;border-left:3px solid #3b82f6;">
                <div style="display:flex;justify-content:space-between;">
                    <b>#{i} {pick.get('home', '?')} vs {pick.get('away', '?')}</b>
                    <span class="status-approved" style="background-color:#3b82f620;">{pick.get('confidence', 'HIGH')}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:0.5rem;">
                    <span>{pick.get('selection', '?')} @ {pick.get('odds', 0):.2f}</span>
                    <span style="color:#10b981;">+{pick.get('edge', 0):.1f}% edge</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("### 📊 Legs by League")
        leagues = data.get("legs_by_league", MOCK_DATA["legs_by_league"])
        df = pd.DataFrame(leagues)
        fig = px.bar(df, x="league", y="count", color="count", color_continuous_scale="blues", text="count")
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    
    with c3:
        st.markdown("### 📈 Status Distribution")
        statuses = data.get("status_distribution", MOCK_DATA["status_distribution"])
        status_df = pd.DataFrame([
            {"Status": "Approved", "Count": statuses.get("approved", 12)},
            {"Status": "Rejected", "Count": statuses.get("rejected", 28)},
            {"Status": "Caution", "Count": statuses.get("caution", 7)},
        ])
        fig = px.pie(status_df, values="Count", names="Status", color="Status",
                     color_discrete_map={"Approved": "#10b981", "Rejected": "#ef4444", "Caution": "#f59e0b"}, hole=0.4)
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent Legs
    st.markdown("### 📋 Recent Legs")
    legs = st.session_state.get("all_legs", MOCK_DATA["all_legs"])[:5]
    for leg in legs:
        status_html = get_status_badge(leg.get("status", "PENDING"))
        edge = leg.get("edge", 0)
        st.markdown(f"""
        <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;">
                <div><b>{leg.get('home', '?')} vs {leg.get('away', '?')}</b> <span style="font-size:0.7rem;">{leg.get('league', '?')}</span></div>
                {status_html}
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:0.5rem;">
                <span>{leg.get('selection', '?')} @ {leg.get('odds', 0):.2f}</span>
                <span style="color:#10b981;">+{edge:.1f}% edge</span>
                <span>{leg.get('prob', 0)}% prob</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔍 View All Legs", use_container_width=True):
        navigate_to("all_legs")
    
    st.divider()
    
    # Bankroll Chart
    st.markdown("### 📉 Bankroll History")
    history = bankroll.get("bankroll_history", MOCK_DATA["bankroll_history"])
    df = pd.DataFrame(history)
    fig = px.line(df, x="date", y="bankroll", markers=True, line_shape="spline")
    fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=350)
    fig.update_traces(line_color="#3b82f6", line_width=2, marker_color="#3b82f6", marker_size=6)
    st.plotly_chart(fig, use_container_width=True)

# ========== ALL LEGS PAGE ==========
def show_all_legs():
    st.markdown('<p class="main-header">📋 All Legs Analyzed</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Team or league...", label_visibility="collapsed")
    with col2:
        show_approved = st.checkbox("Show only APPROVED")
    with col3:
        if st.button("← Back", use_container_width=True):
            navigate_to("dashboard")
    
    legs = st.session_state.get("all_legs", MOCK_DATA["all_legs"])
    filtered = legs.copy()
    
    if search:
        s = search.lower()
        filtered = [l for l in filtered if s in l.get("home", "").lower() or s in l.get("away", "").lower() or s in l.get("league", "").lower()]
    if show_approved:
        filtered = [l for l in filtered if l.get("status") == "APPROVED"]
    
    if filtered:
        st.markdown(f"### Showing {len(filtered)} legs")
        for leg in filtered:
            status_html = get_status_badge(leg.get("status", "PENDING"))
            edge = leg.get("edge", 0)
            cols = st.columns([2, 1.5, 1, 1, 1, 1.2])
            with cols[0]:
                st.write(f"**{leg.get('home', '?')} vs {leg.get('away', '?')}**")
            with cols[1]:
                st.write(leg.get('league', '?'))
            with cols[2]:
                st.write(f"{leg.get('selection', '?')} @ {leg.get('odds', 0):.2f}")
            with cols[3]:
                st.write(f"{leg.get('prob', 0)}%")
            with cols[4]:
                st.markdown(f'<span style="color:#10b981;">+{edge:.1f}%</span>' if edge > 0 else f'<span style="color:#ef4444;">{edge:.1f}%</span>', unsafe_allow_html=True)
            with cols[5]:
                st.markdown(status_html, unsafe_allow_html=True)
            
            if st.button(f"🔍 Details", key=f"view_{leg.get('id', 0)}", use_container_width=True):
                navigate_to("leg_detail", leg)
            st.divider()
    else:
        st.info("No legs found")

# ========== LEG DETAIL PAGE ==========
def show_leg_detail():
    leg = st.session_state.selected_leg
    if not leg:
        st.warning("No leg selected")
        if st.button("← Back"):
            navigate_to("all_legs")
        return
    
    st.markdown(f'<p class="main-header">🔬 {leg.get("home", "?")} vs {leg.get("away", "?")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{leg.get("league", "?")} | {leg.get("selection", "?")} @ {leg.get("odds", 0):.2f}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to All Legs"):
        navigate_to("all_legs")
    
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Season Data", "🔬 Forensic Report"])
    
    with tab1:
        st.info("Season data will appear when backend is fully integrated")
        st.markdown("### Form | Home/Away | Goals | H2H")
    
    with tab2:
        if leg.get("status") == "APPROVED":
            st.success(f"✅ APPROVED - Confidence: {leg.get('confidence', 'HIGH')}")
        else:
            st.error(f"❌ {leg.get('status', 'REJECTED')}")

# ========== PARLAYS PAGE ==========
def show_parlays():
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    parlays = st.session_state.get("parlays_data", MOCK_DATA["parlays"])
    
    st.markdown("### 🟢 Ultra Safe Parlays")
    for p in parlays.get("safe", []):
        legs = " + ".join(p.get("legs", []))
        st.markdown(f"**{legs} = {p.get('total_odds', 0):.2f}x**")
        st.caption(f"Probability: {p.get('prob', 0)}% | Risk: {p.get('risk', 'SAFE')}")
        st.divider()
    
    st.markdown("### 🟡 Balanced Parlays")
    for p in parlays.get("balanced", []):
        legs = " + ".join(p.get("legs", []))
        st.markdown(f"**{legs} = {p.get('total_odds', 0):.2f}x**")
        st.caption(f"Probability: {p.get('prob', 0)}% | Risk: {p.get('risk', 'BALANCED')}")
        st.divider()
    
    st.markdown("### 🔴 Aggressive Parlays")
    for p in parlays.get("aggressive", []):
        legs = " + ".join(p.get("legs", []))
        st.markdown(f"**{legs} = {p.get('total_odds', 0):.2f}x**")
        st.caption(f"Probability: {p.get('prob', 0)}% | Risk: {p.get('risk', 'AGGRESSIVE')}")
        st.divider()

# ========== CALENDAR PAGE ==========
def show_calendar():
    st.markdown('<p class="main-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    date = st.date_input("Select Date", datetime.now().date())
    
    if st.button("🔍 Scan Selected Date", use_container_width=True):
        with st.spinner("Scanning fixtures..."):
            time.sleep(1)
            st.success(f"Scan complete for {date}")
            st.cache_data.clear()
            load_data()
            st.rerun()
    
    st.markdown("### 📊 Recent Activity")
    legs = st.session_state.get("all_legs", MOCK_DATA["all_legs"])[:5]
    for leg in legs:
        st.markdown(f"""
        <div style="background-color:#1e293b;border-radius:10px;padding:0.8rem;margin-bottom:0.5rem;">
            <div><b>{leg.get('home', '?')} vs {leg.get('away', '?')}</b> ({leg.get('league', '?')})</div>
            <div style="font-size:0.8rem;">Selection: {leg.get('selection', '?')} @ {leg.get('odds', 0):.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# ========== MAIN ==========
def main():
    if not st.session_state.data_loaded:
        load_data()
        st.session_state.data_loaded = True
    
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        if st.button("📊 Dashboard", use_container_width=True):
            navigate_to("dashboard")
        if st.button("📋 All Legs", use_container_width=True):
            navigate_to("all_legs")
        if st.button("🔗 Parlays", use_container_width=True):
            navigate_to("parlays")
        if st.button("📅 Calendar", use_container_width=True):
            navigate_to("calendar")
        
        st.divider()
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            load_data()
            st.rerun()
        
        st.divider()
        
        if st.session_state.webSocket_status == "connected":
            st.success("✅ Backend Connected")
            st.caption(BACKEND_URL)
        else:
            st.info("📊 Using Demo Data")
            st.caption("Backend not available")
        
        st.divider()
        
        perf = st.session_state.get("performance_data", MOCK_DATA)
        health = perf.get("system_health", {})
        st.metric("Overall Accuracy", f"{health.get('accuracy', 0.58):.0%}")
        st.metric("HIGH Confidence", "68%")
        st.metric("MEDIUM Confidence", "52%")
        
        st.divider()
        st.caption(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("🎯 Match Oracle")
    
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

if __name__ == "__main__":
    main()
