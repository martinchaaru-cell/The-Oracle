import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import requests
import json

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
    .check-pass {
        background-color: #10b98120;
        color: #10b981;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }
    .check-fail {
        background-color: #ef444420;
        color: #ef4444;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
for key in ["page", "selected_leg_id", "selected_leg", "webSocket_status", "previous_page",
            "all_legs", "bankroll_data", "performance_data", "dashboard_data", "parlays_data", "data_loaded"]:
    if key not in st.session_state:
        if key == "page":
            st.session_state.page = "dashboard"
        elif key == "webSocket_status":
            st.session_state.webSocket_status = "disconnected"
        elif key in ["all_legs", "data_loaded"]:
            st.session_state[key] = [] if key == "all_legs" else False
        else:
            st.session_state[key] = None

# ========== MOCK FALLBACK DATA ==========
MOCK_LEGS = [
    {"id": 0, "legId": "leg_001", "match": "Arsenal vs Chelsea", "homeTeam": "Arsenal", "awayTeam": "Chelsea",
     "league": "Premier League", "kickoff": "2025-06-10T15:00:00Z", "selection": "Arsenal",
     "selectionOdds": 2.10, "modelProb": 0.62, "edge": 0.081, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 1, "legId": "leg_002", "match": "Bayern Munich vs Dortmund", "homeTeam": "Bayern Munich", "awayTeam": "Dortmund",
     "league": "Bundesliga", "kickoff": "2025-06-10T17:30:00Z", "selection": "Bayern Munich",
     "selectionOdds": 1.75, "modelProb": 0.58, "edge": 0.067, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 2, "legId": "leg_003", "match": "Inter Milan vs Juventus", "homeTeam": "Inter Milan", "awayTeam": "Juventus",
     "league": "Serie A", "kickoff": "2025-06-10T19:45:00Z", "selection": "Inter Milan",
     "selectionOdds": 2.05, "modelProb": 0.55, "edge": 0.042, "status": "APPROVED", "confidence": "MEDIUM"},
]

MOCK_DASHBOARD = {
    "todayStats": {"totalLegs": 47, "approved": 12, "rejected": 28, "caution": 7, "totalStake": 847, "potentialReturn": 2150},
    "topPicks": [
        {"match": "Arsenal vs Chelsea", "selection": "Arsenal", "odds": 2.10, "edge": 0.081, "confidence": "HIGH"},
        {"match": "Bayern Munich vs Dortmund", "selection": "Bayern Munich", "odds": 1.75, "edge": 0.067, "confidence": "HIGH"},
        {"match": "Inter Milan vs Juventus", "selection": "Inter Milan", "odds": 2.05, "edge": 0.042, "confidence": "MEDIUM"},
    ],
    "legsByLeague": [
        {"league": "Premier League", "count": 12}, {"league": "La Liga", "count": 10},
        {"league": "Bundesliga", "count": 8}, {"league": "Serie A", "count": 8},
        {"league": "Ligue 1", "count": 6}, {"league": "Eredivisie", "count": 3}
    ]
}

MOCK_BANKROLL = {"current": 12450, "peak": 13200, "history": [
    {"date": "Jun 1", "bankroll": 10000}, {"date": "Jun 2", "bankroll": 10250},
    {"date": "Jun 3", "bankroll": 10500}, {"date": "Jun 4", "bankroll": 10300},
    {"date": "Jun 5", "bankroll": 10800}, {"date": "Jun 6", "bankroll": 11200},
    {"date": "Jun 7", "bankroll": 11800}, {"date": "Jun 8", "bankroll": 12450}
]}

MOCK_PERFORMANCE = {"calibrationGrade": "B", "overallAccuracy": 0.58, "highConfAccuracy": 0.68, "mediumConfAccuracy": 0.52}

MOCK_PARLAYS = {
    "safe": [{"legs": ["Arsenal (2.10)", "Bayern (1.75)"], "totalOdds": 3.68, "combinedProb": 0.36, "riskLevel": "SAFE"}],
    "balanced": [{"legs": ["Arsenal (2.10)", "Bayern (1.75)", "PSG (1.55)"], "totalOdds": 5.70, "combinedProb": 0.22, "riskLevel": "BALANCED"}],
    "aggressive": [{"legs": ["Arsenal (2.10)", "Bayern (1.75)", "Inter (2.05)", "Ajax (1.85)"], "totalOdds": 13.95, "combinedProb": 0.11, "riskLevel": "AGGRESSIVE"}]
}

# ========== API HELPER FUNCTIONS ==========
def safe_get(data, key, default=None):
    """Safely get value from dict, returning default if None or key missing"""
    if data is None:
        return default
    return data.get(key, default)

def safe_float(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default

@st.cache_data(ttl=60)
def fetch_from_backend(endpoint, default=None):
    """Generic fetch function with fallback to default"""
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return default
    except Exception:
        return default

def load_all_data():
    """Load data with fallback to mock data"""
    with st.spinner("Loading data from backend..."):
        # Check backend health
        try:
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            st.session_state.webSocket_status = "connected" if health_response.status_code == 200 else "disconnected"
        except:
            st.session_state.webSocket_status = "disconnected"
        
        # Fetch data with fallbacks
        legs = fetch_from_backend("/frontend/legs", MOCK_LEGS)
        st.session_state.all_legs = legs if legs else MOCK_LEGS
        
        dashboard = fetch_from_backend("/frontend/dashboard", MOCK_DASHBOARD)
        st.session_state.dashboard_data = dashboard if dashboard else MOCK_DASHBOARD
        
        bankroll = fetch_from_backend("/frontend/bankroll", MOCK_BANKROLL)
        st.session_state.bankroll_data = bankroll if bankroll else MOCK_BANKROLL
        
        performance = fetch_from_backend("/frontend/performance", MOCK_PERFORMANCE)
        st.session_state.performance_data = performance if performance else MOCK_PERFORMANCE
        
        parlays = fetch_from_backend("/frontend/parlays", MOCK_PARLAYS)
        st.session_state.parlays_data = parlays if parlays else MOCK_PARLAYS

# ========== HELPER FUNCTIONS ==========
def get_status_badge(status):
    if status == "APPROVED":
        return '<span class="status-approved">✅ APPROVED</span>'
    elif status == "CAUTION":
        return '<span class="status-caution">⚠️ CAUTION</span>'
    return '<span class="status-rejected">❌ REJECTED</span>'

def get_edge_color(edge):
    return "#10b981" if edge > 0 else "#ef4444"

def navigate_to(page, leg_id=None, leg_data=None):
    st.session_state.page = page
    st.session_state.previous_page = st.session_state.page
    if leg_id:
        st.session_state.selected_leg_id = leg_id
    if leg_data:
        st.session_state.selected_leg = leg_data
    st.rerun()

# ========== PAGE: DASHBOARD ==========
def show_dashboard():
    dashboard = st.session_state.get("dashboard_data", MOCK_DASHBOARD)
    bankroll = st.session_state.get("bankroll_data", MOCK_BANKROLL)
    performance = st.session_state.get("performance_data", MOCK_PERFORMANCE)
    today_stats = safe_get(dashboard, "todayStats", {})
    
    # Header
    col_logo, col_status = st.columns([3, 1])
    with col_logo:
        st.markdown('<p class="main-header">🎯 MATCH ORACLE</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-powered football prediction platform</p>', unsafe_allow_html=True)
    with col_status:
        status_color = "🟢" if st.session_state.webSocket_status == "connected" else "🔴"
        st.markdown(f"""
        <div style="text-align: right; margin-top: 1rem;">
            <span style="font-size: 0.8rem;">{status_color} {st.session_state.webSocket_status.upper()}</span><br>
            <span style="font-size: 0.7rem; color: #475569;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        current = safe_float(safe_get(bankroll, "current", 12450), 12450)
        peak = safe_float(safe_get(bankroll, "peak", 13200), 13200)
        drawdown = (peak - current) / peak if peak > 0 else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">${current:,.0f}</div><div class="metric-label">Bankroll</div><div style="font-size:0.7rem;color:#ef4444;">▼ {drawdown:.1%} from peak</div></div>', unsafe_allow_html=True)
    with col2:
        total_legs = safe_int(safe_get(today_stats, "totalLegs", 47), 47)
        approved = safe_int(safe_get(today_stats, "approved", 12), 12)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_legs}</div><div class="metric-label">Today\'s Legs</div><div style="font-size:0.7rem;color:#10b981;">▲ {approved} approved</div></div>', unsafe_allow_html=True)
    with col3:
        total_stake = safe_float(safe_get(today_stats, "totalStake", 847), 847)
        potential = safe_float(safe_get(today_stats, "potentialReturn", 2150), 2150)
        st.markdown(f'<div class="metric-card"><div class="metric-value">${total_stake:,.0f}</div><div class="metric-label">Total Staked</div><div style="font-size:0.7rem;color:#10b981;">▲ ${potential:,.0f} potential</div></div>', unsafe_allow_html=True)
    with col4:
        grade = safe_get(performance, "calibrationGrade", "B")
        accuracy = safe_float(safe_get(performance, "overallAccuracy", 0.58), 0.58)
        st.markdown(f'<div class="metric-card"><div class="metric-value">Grade {grade}</div><div class="metric-label">System Health</div><div style="font-size:0.7rem;">{accuracy:.0%} accuracy</div></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 3-Column Layout
    col_left, col_center, col_right = st.columns(3)
    
    with col_left:
        st.markdown("### 🏆 Top Picks")
        top_picks = safe_get(dashboard, "topPicks", [])
        if top_picks:
            for i, pick in enumerate(top_picks[:3], 1):
                edge = safe_float(pick.get("edge", 0), 0)
                edge_color = get_edge_color(edge)
                edge_symbol = "+" if edge > 0 else ""
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 10px; padding: 0.8rem; margin-bottom: 0.8rem; border-left: 3px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between;">
                        <span><b>#{i}</b> {pick.get('match', 'Unknown')}</span>
                        <span class="status-approved" style="background-color:#3b82f620;">{pick.get('confidence', 'HIGH')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span>{pick.get('selection', '?')} @ {safe_float(pick.get('odds', 0), 0):.2f}</span>
                        <span style="color:{edge_color};">{edge_symbol}{edge*100:.1f}% edge</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No picks available")
    
    with col_center:
        st.markdown("### 📊 Legs by League")
        legs_by_league = safe_get(dashboard, "legsByLeague", [])
        if legs_by_league:
            fig = px.bar(pd.DataFrame(legs_by_league), x="league", y="count", color="count", color_continuous_scale="blues", text="count")
            fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No league data")
    
    with col_right:
        st.markdown("### 📈 Status Distribution")
        status_df = pd.DataFrame([
            {"Status": "Approved", "Count": safe_int(safe_get(today_stats, "approved", 12), 12)},
            {"Status": "Rejected", "Count": safe_int(safe_get(today_stats, "rejected", 28), 28)},
            {"Status": "Caution", "Count": safe_int(safe_get(today_stats, "caution", 7), 7)},
        ])
        fig = px.pie(status_df, values="Count", names="Status", color="Status",
                     color_discrete_map={"Approved": "#10b981", "Rejected": "#ef4444", "Caution": "#f59e0b"}, hole=0.4)
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent Legs
    st.markdown("### 📋 Recent Legs")
    legs = st.session_state.get("all_legs", MOCK_LEGS)[:5]
    if legs:
        for leg in legs:
            edge = safe_float(leg.get("edge", 0), 0)
            edge_color = get_edge_color(edge)
            edge_symbol = "+" if edge > 0 else ""
            status_html = get_status_badge(leg.get("status", "PENDING"))
            st.markdown(f"""
            <div style="background-color:#1e293b; border-radius:10px; padding:0.8rem; margin-bottom:0.5rem;">
                <div style="display:flex; justify-content:space-between;">
                    <div><b>{leg.get('homeTeam', '?')} vs {leg.get('awayTeam', '?')}</b> <span style="font-size:0.7rem;color:#64748b;">{leg.get('league', '?')}</span></div>
                    {status_html}
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:0.5rem;">
                    <span>{leg.get('selection', '?')} @ {safe_float(leg.get('selectionOdds', 0), 0):.2f}</span>
                    <span style="color:{edge_color};">{edge_symbol}{edge*100:.1f}% edge</span>
                    <span>{safe_float(leg.get('modelProb', 0), 0)*100:.0f}% prob</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🔍 View All Legs", use_container_width=True):
            navigate_to("all_legs")
    else:
        st.info("No legs available")
    
    st.divider()
    
    # Bankroll Chart
    st.markdown("### 📉 Bankroll History")
    history = safe_get(bankroll, "history", [])
    if history:
        fig = px.line(pd.DataFrame(history), x="date", y="bankroll", markers=True, line_shape="spline")
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=350)
        fig.update_traces(line_color="#3b82f6", line_width=2, marker_color="#3b82f6", marker_size=6)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bankroll history")

# ========== PAGE: ALL LEGS ==========
def show_all_legs():
    st.markdown('<p class="main-header">📋 All Legs Analyzed</p>', unsafe_allow_html=True)
    
    search_col, filter_col, back_col = st.columns([2, 1, 1])
    with search_col:
        search_term = st.text_input("🔍 Search", placeholder="Team or league...", label_visibility="collapsed")
    with filter_col:
        show_only_approved = st.checkbox("Show only APPROVED", value=False)
    with back_col:
        if st.button("← Back", use_container_width=True):
            navigate_to("dashboard")
    
    legs = st.session_state.get("all_legs", MOCK_LEGS)
    filtered = legs.copy()
    if search_term:
        term = search_term.lower()
        filtered = [l for l in filtered if term in l.get("homeTeam", "").lower() or term in l.get("awayTeam", "").lower() or term in l.get("league", "").lower()]
    if show_only_approved:
        filtered = [l for l in filtered if l.get("status") == "APPROVED"]
    
    if filtered:
        st.markdown(f"### Showing {len(filtered)} legs")
        for leg in filtered:
            edge = safe_float(leg.get("edge", 0), 0)
            edge_color = get_edge_color(edge)
            edge_symbol = "+" if edge > 0 else ""
            status_html = get_status_badge(leg.get("status", "PENDING"))
            
            cols = st.columns([2, 1.5, 1, 1, 1, 1.2])
            with cols[0]:
                st.write(f"**{leg.get('homeTeam', '?')} vs {leg.get('awayTeam', '?')}**")
            with cols[1]:
                st.write(leg.get('league', '?'))
            with cols[2]:
                st.write(f"{leg.get('selection', '?')} @ {safe_float(leg.get('selectionOdds', 0), 0):.2f}")
            with cols[3]:
                st.write(f"{safe_float(leg.get('modelProb', 0), 0)*100:.0f}%")
            with cols[4]:
                st.markdown(f'<span style="color:{edge_color};">{edge_symbol}{edge*100:.1f}%</span>', unsafe_allow_html=True)
            with cols[5]:
                st.markdown(status_html, unsafe_allow_html=True)
            
            if st.button(f"🔍 Details", key=f"view_{leg.get('legId', leg.get('id', 0))}", use_container_width=True):
                navigate_to("leg_detail", leg_data=leg)
            st.divider()
    else:
        st.info("No legs found")

# ========== PAGE: LEG DETAIL ==========
def show_leg_detail():
    leg = st.session_state.selected_leg
    if not leg:
        st.warning("No leg selected")
        if st.button("← Back"):
            navigate_to("all_legs")
        return
    
    st.markdown(f'<p class="main-header">🔬 {leg.get("homeTeam", "?")} vs {leg.get("awayTeam", "?")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{leg.get("league", "?")} | Selection: {leg.get("selection", "?")} @ {safe_float(leg.get("selectionOdds", 0), 0):.2f}</p>', unsafe_allow_html=True)
    
    if st.button("← Back to All Legs"):
        navigate_to("all_legs")
    
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Season Data", "🔬 Forensic Report"])
    
    with tab1:
        st.info("Season data will appear here when backend provides team profiles")
        st.markdown("### 📈 Form | 🏟️ Home/Away | ⚽ Goals | 📜 H2H")
    
    with tab2:
        st.markdown("### M4: Pre-filter")
        st.markdown("### M5: Forensic Failures")
        st.markdown("### M6: Personnel")
        st.markdown("### M7: AI Consensus")
        st.markdown("### M8: Dual Pattern")
        st.markdown("### M9: Underdog")
        st.markdown("### M10: Matrix")
        st.markdown("### M26: Context")
        st.markdown("### M27: H2H")
        
        if leg.get("status") == "APPROVED":
            st.success(f"✅ FINAL VERDICT: APPROVED (Confidence: {leg.get('confidence', 'HIGH')})")
        else:
            st.error(f"❌ FINAL VERDICT: {leg.get('status', 'REJECTED')}")

# ========== PAGE: PARLAYS ==========
def show_parlays():
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    parlays = st.session_state.get("parlays_data", MOCK_PARLAYS)
    
    st.markdown("### 🟢 Ultra Safe Parlays")
    for p in safe_get(parlays, "safe", []):
        st.markdown(f"**{' + '.join(p.get('legs', []))} = {safe_float(p.get('totalOdds', 0), 0):.2f}x**")
        st.caption(f"Prob: {safe_float(p.get('combinedProb', 0), 0):.1%} | Risk: {p.get('riskLevel', 'SAFE')}")
        st.divider()
    
    st.markdown("### 🟡 Balanced Parlays")
    for p in safe_get(parlays, "balanced", []):
        st.markdown(f"**{' + '.join(p.get('legs', []))} = {safe_float(p.get('totalOdds', 0), 0):.2f}x**")
        st.caption(f"Prob: {safe_float(p.get('combinedProb', 0), 0):.1%} | Risk: {p.get('riskLevel', 'BALANCED')}")
        st.divider()
    
    st.markdown("### 🔴 Aggressive Parlays")
    for p in safe_get(parlays, "aggressive", []):
        st.markdown(f"**{' + '.join(p.get('legs', []))} = {safe_float(p.get('totalOdds', 0), 0):.2f}x**")
        st.caption(f"Prob: {safe_float(p.get('combinedProb', 0), 0):.1%} | Risk: {p.get('riskLevel', 'AGGRESSIVE')}")
        st.divider()

# ========== PAGE: CALENDAR ==========
def show_calendar():
    st.markdown('<p class="main-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    selected_date = st.date_input("Select Date", datetime.now().date())
    
    if st.button("🔍 Scan Selected Date", use_container_width=True):
        with st.spinner("Scanning fixtures..."):
            time.sleep(1)
            st.success(f"Scan complete for {selected_date}")
            st.cache_data.clear()
            load_all_data()
            st.rerun()
    
    st.markdown("### 📊 Recent Activity")
    legs = st.session_state.get("all_legs", MOCK_LEGS)[:5]
    if legs:
        for leg in legs:
            status_html = get_status_badge(leg.get("status", "PENDING"))
            st.markdown(f"""
            <div style="background-color:#1e293b; border-radius:10px; padding:0.8rem; margin-bottom:0.5rem;">
                <div style="display:flex; justify-content:space-between;">
                    <span><b>{leg.get('homeTeam', '?')} vs {leg.get('awayTeam', '?')}</b> ({leg.get('league', '?')})</span>
                    {status_html}
                </div>
                <div style="font-size:0.8rem; color:#64748b;">Selection: {leg.get('selection', '?')} @ {safe_float(leg.get('selectionOdds', 0), 0):.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No legs available")

# ========== MAIN ==========
def main():
    if not st.session_state.get("data_loaded", False):
        load_all_data()
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
            load_all_data()
            st.rerun()
        
        st.divider()
        
        if st.session_state.webSocket_status == "connected":
            st.success("✅ Backend Connected")
            st.caption(BACKEND_URL)
        else:
            st.warning("⚠️ Using Mock Data")
            st.caption("Backend not available")
        
        st.divider()
        
        perf = st.session_state.get("performance_data", MOCK_PERFORMANCE)
        st.metric("Overall Accuracy", f"{safe_float(safe_get(perf, 'overallAccuracy', 0.58), 0.58):.0%}")
        st.metric("HIGH Confidence", f"{safe_float(safe_get(perf, 'highConfAccuracy', 0.68), 0.68):.0%}")
        st.metric("MEDIUM Confidence", f"{safe_float(safe_get(perf, 'mediumConfAccuracy', 0.52), 0.52):.0%}")
        
        st.divider()
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("🎯 Match Oracle v2.0")
    
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
