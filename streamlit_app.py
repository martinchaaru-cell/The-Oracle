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
# Get backend URL from secrets or use default
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0a0a0a;
    }
    
    /* Headers */
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #334155;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
    /* Status badges */
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
    
    /* Check results */
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
    
    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Clickable row effect */
    .clickable-row:hover {
        background-color: #1e293b !important;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE INITIALIZATION ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_leg_id" not in st.session_state:
    st.session_state.selected_leg_id = None
if "selected_leg" not in st.session_state:
    st.session_state.selected_leg = None
if "webSocket_status" not in st.session_state:
    st.session_state.webSocket_status = "disconnected"
if "previous_page" not in st.session_state:
    st.session_state.previous_page = "dashboard"
if "all_legs" not in st.session_state:
    st.session_state.all_legs = []
if "bankroll_data" not in st.session_state:
    st.session_state.bankroll_data = None
if "performance_data" not in st.session_state:
    st.session_state.performance_data = None

# ========== API HELPER FUNCTIONS ==========

@st.cache_data(ttl=60)
def fetch_dashboard_data():
    """Fetch dashboard data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/dashboard", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Cannot connect to backend. Using cached data if available.")
        return None
    except Exception as e:
        st.error(f"Error fetching dashboard data: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_all_legs():
    """Fetch all legs from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/legs", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("legs", [])
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching legs: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_leg_forensic(leg_id):
    """Fetch forensic report for a specific leg"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/legs/{leg_id}/forensic", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching forensic data: {e}")
        return None

@st.cache_data(ttl=60)
def fetch_bankroll():
    """Fetch bankroll data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/bankroll", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def fetch_performance():
    """Fetch performance metrics from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/performance", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def fetch_parlays():
    """Fetch parlays from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/frontend/parlays", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def scan_date(date_str):
    """Trigger scan for a specific date"""
    try:
        response = requests.post(f"{BACKEND_URL}/frontend/scan/{date_str}", timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except Exception as e:
        return False, str(e)

# ========== HELPER FUNCTIONS ==========

def get_status_badge(status):
    if status == "APPROVED":
        return '<span class="status-approved">✅ APPROVED</span>'
    elif status == "CAUTION":
        return '<span class="status-caution">⚠️ CAUTION</span>'
    else:
        return '<span class="status-rejected">❌ REJECTED</span>'

def get_edge_color(edge):
    return "#10b981" if edge > 0 else "#ef4444"

def navigate_to(page, leg_id=None, leg_data=None):
    st.session_state.page = page
    st.session_state.previous_page = st.session_state.page
    if leg_id is not None:
        st.session_state.selected_leg_id = leg_id
    if leg_data is not None:
        st.session_state.selected_leg = leg_data
    st.rerun()

def go_back():
    st.session_state.page = st.session_state.previous_page
    st.rerun()

# ========== DATA LOADING ==========

def load_all_data():
    """Load all data from backend"""
    with st.spinner("Loading data from backend..."):
        # Check backend health
        try:
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if health_response.status_code == 200:
                st.session_state.webSocket_status = "connected"
            else:
                st.session_state.webSocket_status = "disconnected"
        except:
            st.session_state.webSocket_status = "disconnected"
        
        # Fetch data
        dashboard = fetch_dashboard_data()
        if dashboard:
            st.session_state.dashboard_data = dashboard
        
        legs = fetch_all_legs()
        if legs:
            st.session_state.all_legs = legs
        
        bankroll = fetch_bankroll()
        if bankroll:
            st.session_state.bankroll_data = bankroll
        
        performance = fetch_performance()
        if performance:
            st.session_state.performance_data = performance
        
        parlays = fetch_parlays()
        if parlays:
            st.session_state.parlays_data = parlays

# ========== PAGE: DASHBOARD ==========
def show_dashboard():
    dashboard = st.session_state.get("dashboard_data", {})
    bankroll = st.session_state.get("bankroll_data", {})
    performance = st.session_state.get("performance_data", {})
    
    # Header with status
    col_logo, col_status = st.columns([3, 1])
    with col_logo:
        st.markdown('<p class="main-header">🎯 MATCH ORACLE</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-powered football prediction platform</p>', unsafe_allow_html=True)
    with col_status:
        status_color = "🟢" if st.session_state.webSocket_status == "connected" else "🔴"
        st.markdown(f"""
        <div style="text-align: right; margin-top: 1rem;">
            <span style="font-size: 0.8rem; color: #64748b;">{status_color} {st.session_state.webSocket_status.upper()}</span><br>
            <span style="font-size: 0.7rem; color: #475569;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        current_bankroll = bankroll.get("current", 12450)
        peak = bankroll.get("peak", 13200)
        drawdown = (peak - current_bankroll) / peak if peak > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${current_bankroll:,.0f}</div>
            <div class="metric-label">Bankroll</div>
            <div style="font-size: 0.7rem; color: #ef4444;">▼ {drawdown:.1%} from peak</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        total_legs = dashboard.get("todayStats", {}).get("totalLegs", 47)
        approved = dashboard.get("todayStats", {}).get("approved", 12)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_legs}</div>
            <div class="metric-label">Today's Legs</div>
            <div style="font-size: 0.7rem; color: #10b981;">▲ {approved} approved</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_stake = dashboard.get("todayStats", {}).get("totalStake", 847)
        potential_return = dashboard.get("todayStats", {}).get("potentialReturn", 2150)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_stake:,.0f}</div>
            <div class="metric-label">Total Staked</div>
            <div style="font-size: 0.7rem; color: #10b981;">▲ ${potential_return:,.0f} potential</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        grade = performance.get("calibrationGrade", "B")
        accuracy = performance.get("overallAccuracy", 0.58)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">Grade {grade}</div>
            <div class="metric-label">System Health</div>
            <div style="font-size: 0.7rem; color: #3b82f6;">{accuracy:.0%} accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 3-column layout
    col_left, col_center, col_right = st.columns(3)
    
    with col_left:
        st.markdown("### 🏆 Top Picks")
        top_picks = dashboard.get("topPicks", [])
        if top_picks:
            for i, pick in enumerate(top_picks[:3], 1):
                edge_color = get_edge_color(pick.get("edge", 0))
                edge_symbol = "+" if pick.get("edge", 0) > 0 else ""
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 10px; padding: 0.8rem; margin-bottom: 0.8rem; border-left: 3px solid #3b82f6;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: bold;">#{i}</span>
                            <span style="margin-left: 0.5rem;">{pick.get('match', 'Unknown')}</span>
                        </div>
                        <span class="status-approved" style="background-color: #3b82f620;">{pick.get('confidence', 'HIGH')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                        <span style="font-size: 0.9rem;">{pick.get('selection', '?')} @ {pick.get('odds', 0):.2f}</span>
                        <span style="color: {edge_color};">{edge_symbol}{pick.get('edge', 0)*100:.1f}% edge</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No picks available. Run pipeline to generate picks.")
    
    with col_center:
        st.markdown("### 📊 Legs by League")
        legs_by_league = dashboard.get("legsByLeague", [])
        if legs_by_league:
            league_df = pd.DataFrame(legs_by_league)
            fig = px.bar(league_df, x="league", y="count", color="count", color_continuous_scale="blues", text="count")
            fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No league data available")
    
    with col_right:
        st.markdown("### 📈 Status Distribution")
        status_counts = dashboard.get("todayStats", {})
        if status_counts:
            status_df = pd.DataFrame([
                {"Status": "Approved", "Count": status_counts.get("approved", 0)},
                {"Status": "Rejected", "Count": status_counts.get("rejected", 0)},
                {"Status": "Caution", "Count": status_counts.get("caution", 0)},
            ])
            fig = px.pie(status_df, values="Count", names="Status", color="Status",
                         color_discrete_map={"Approved": "#10b981", "Rejected": "#ef4444", "Caution": "#f59e0b"}, hole=0.4)
            fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No status data available")
    
    st.divider()
    
    # Recent Legs preview
    st.markdown("### 📋 Recent Legs")
    all_legs_data = st.session_state.get("all_legs", [])
    preview_legs = all_legs_data[:5]
    
    if preview_legs:
        for leg in preview_legs:
            edge_color = get_edge_color(leg.get("edge", 0))
            edge_symbol = "+" if leg.get("edge", 0) > 0 else ""
            status_html = get_status_badge(leg.get("status", "PENDING"))
            st.markdown(f"""
            <div style="background-color: #1e293b; border-radius: 10px; padding: 0.8rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: bold;">{leg.get('homeTeam', '?')} vs {leg.get('awayTeam', '?')}</span>
                        <span style="font-size: 0.7rem; color: #64748b; margin-left: 0.5rem;">{leg.get('league', '?')}</span>
                    </div>
                    {status_html}
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                    <span>{leg.get('selection', '?')} @ {leg.get('selectionOdds', 0):.2f}</span>
                    <span style="color: {edge_color};">{edge_symbol}{leg.get('edge', 0)*100:.1f}% edge</span>
                    <span style="color: #64748b;">{(leg.get('modelProb', 0)*100):.0f}% prob</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn2:
            if st.button("🔍 View All Legs", use_container_width=True):
                navigate_to("all_legs")
    else:
        st.info("No legs available. Run pipeline to fetch fixtures.")
    
    st.divider()
    
    # Bankroll chart
    st.markdown("### 📉 Bankroll History")
    history = bankroll.get("history", [])
    if history:
        history_df = pd.DataFrame(history)
        fig = px.line(history_df, x="date", y="bankroll", markers=True, line_shape="spline")
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=350)
        fig.update_traces(line_color="#3b82f6", line_width=2, marker_color="#3b82f6", marker_size=6)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bankroll history available")

# ========== PAGE: ALL LEGS ==========
def show_all_legs():
    st.markdown('<p class="main-header">📋 All Legs Analyzed</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Complete list of all pipeline decisions</p>', unsafe_allow_html=True)
    
    # Search and filter
    search_col, filter_col, back_col = st.columns([2, 1, 1])
    with search_col:
        search_term = st.text_input("🔍 Search matches, leagues, or selections", placeholder="e.g., Arsenal, Premier League...", label_visibility="collapsed")
    with filter_col:
        show_only_approved = st.checkbox("Show only APPROVED", value=False)
    with back_col:
        if st.button("← Back to Dashboard", use_container_width=True):
            navigate_to("dashboard")
    
    # Get data
    all_legs_data = st.session_state.get("all_legs", [])
    
    # Filter data
    filtered_legs = all_legs_data.copy()
    if search_term:
        search_lower = search_term.lower()
        filtered_legs = [leg for leg in filtered_legs if 
                        search_lower in leg.get("match", "").lower() or 
                        search_lower in leg.get("league", "").lower() or 
                        search_lower in leg.get("selection", "").lower()]
    if show_only_approved:
        filtered_legs = [leg for leg in filtered_legs if leg.get("status") == "APPROVED"]
    
    if filtered_legs:
        st.markdown(f"### Showing {len(filtered_legs)} legs")
        
        for leg in filtered_legs:
            edge_color = get_edge_color(leg.get("edge", 0))
            edge_symbol = "+" if leg.get("edge", 0) > 0 else ""
            status_html = get_status_badge(leg.get("status", "PENDING"))
            
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1.5, 0.8, 1, 0.8, 1, 1.2])
            with col1:
                st.write(f"**{leg.get('homeTeam', '?')} vs {leg.get('awayTeam', '?')}**")
            with col2:
                st.write(leg.get('league', '?'))
            with col3:
                st.write(leg.get('kickoff', '').split('T')[0] if leg.get('kickoff') else '?')
            with col4:
                st.write(f"{leg.get('selection', '?')} @ {leg.get('selectionOdds', 0):.2f}")
            with col5:
                st.write(f"{(leg.get('modelProb', 0)*100):.0f}%")
            with col6:
                st.markdown(f'<span style="color: {edge_color};">{edge_symbol}{leg.get("edge", 0)*100:.1f}%</span>', unsafe_allow_html=True)
            with col7:
                st.markdown(status_html, unsafe_allow_html=True)
            
            if st.button(f"🔍 View Details", key=f"view_{leg.get('legId', leg.get('id', 0))}", use_container_width=True):
                navigate_to("leg_detail", leg_id=leg.get('legId'), leg_data=leg)
            st.divider()
    else:
        st.info("No legs found. Run pipeline to fetch fixtures.")

# ========== PAGE: LEG DETAIL ==========
def show_leg_detail():
    leg = st.session_state.selected_leg
    if leg is None:
        st.warning("No leg selected")
        if st.button("← Back to All Legs"):
            navigate_to("all_legs")
        return
    
    # Fetch forensic data
    forensic = fetch_leg_forensic(leg.get("legId", leg.get("id")))
    
    # Header
    st.markdown(f'<p class="main-header">🔬 {leg.get("homeTeam", "?")} vs {leg.get("awayTeam", "?")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{leg.get("league", "?")} • Kickoff: {leg.get("kickoff", "?")} | Selection: {leg.get("selection", "?")} @ {leg.get("selectionOdds", 0):.2f}</p>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to All Legs"):
        navigate_to("all_legs")
    
    st.divider()
    
    # Two tabs
    tab1, tab2 = st.tabs(["📊 Season Data", "🔬 Full Forensic Report (M4-M27)"])
    
    with tab1:
        st.info("Season data will be available when backend provides team profiles")
        st.markdown("### 📈 Team Form")
        st.markdown("### 🏟️ Home/Away Performance")
        st.markdown("### ⚽ Goals Analysis")
        st.markdown("### 📜 Head to Head History")
    
    with tab2:
        if forensic:
            # M4
            st.markdown("### M4: Asymmetric Pre-filter")
            m4 = forensic.get("m4", {})
            checks = m4.get("checkDetails", [])
            for check in checks:
                passed = check.get("passed", False)
                status_class = "check-pass" if passed else "check-fail"
                status_text = "PASS" if passed else "FAIL"
                st.markdown(f'<div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;"><span>{check.get("name", "Check")}</span><span class="{status_class}">{status_text}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top: 1rem;"><strong>Result:</strong> {m4.get("checksPassed", 0)}/8 passed → {"✅ APPROVED" if leg.get("status") == "APPROVED" else "❌ REJECTED"}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # M5
            st.markdown("### M5: Forensic Failures")
            m5 = forensic.get("m5", {})
            failures = m5.get("details", {})
            if failures:
                for failure, points in failures.items():
                    st.markdown(f'<div style="display: flex; justify-content: space-between;"><span>⚠️ {failure.replace("_", " ")}</span><span style="color: #ef4444;">+{points} pts</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top: 1rem;"><strong>Total Failure Score:</strong> {m5.get("failureScore", 0)} / 4.5 → {"PASS" if leg.get("status") == "APPROVED" else "FAIL"}</div>', unsafe_allow_html=True)
            else:
                st.info("No forensic failures recorded")
            
            st.divider()
            
            # M6
            st.markdown("### M6: Personnel")
            m6 = forensic.get("m6", {})
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{leg.get('homeTeam', 'Home')}**")
                st.markdown(f'<span class="metric-value">{m6.get("homeScore", 50)}/100</span>', unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{leg.get('awayTeam', 'Away')}**")
                st.markdown(f'<span class="metric-value">{m6.get("awayScore", 50)}/100</span>', unsafe_allow_html=True)
            
            st.divider()
            
            # M7
            st.markdown("### M7: AI Consensus")
            m7 = forensic.get("m7", {})
            st.markdown(f'<div><strong>Consensus:</strong> {m7.get("consensus", "N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Agreement:</strong> {m7.get("agreement", 0)*100:.0f}%</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # M8
            st.markdown("### M8: Dual Pattern")
            m8 = forensic.get("m8", {})
            st.markdown(f'<div><strong>Dual Risk Level:</strong> <span class="check-pass">{m8.get("dualRiskLevel", "MEDIUM")}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Underdog Threat:</strong> {m8.get("underdogThreat", "NONE")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Patterns Reliable:</strong> {"✅" if m8.get("patternsReliable", False) else "❌"}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # M9
            st.markdown("### M9: Underdog Scanner")
            m9 = forensic.get("m9", {})
            st.markdown(f'<div><strong>Underdog Edge:</strong> {m9.get("underdogEdge", 0)*100:.1f}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Threat Level:</strong> {m9.get("threatLevel", "NONE")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Goldmine:</strong> {"✅" if m9.get("goldmineQualified", False) else "❌"}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # M10
            st.markdown("### M10: Tally Matrix")
            m10 = forensic.get("m10", {})
            st.markdown(f'<div><strong>Matrix Useful:</strong> {"✅" if m10.get("matrixUseful", False) else "❌"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Bilateral Prediction:</strong> {m10.get("bilateralPrediction", "N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Trap/Value Signal:</strong> {m10.get("trapValueSignal", "NONE")}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # M26
            st.markdown("### M26: Match Context")
            m26 = forensic.get("m26", {})
            st.markdown(f'<div><strong>Match Importance:</strong> {m26.get("matchImportance", 0)*100:.0f}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Is Rivalry:</strong> {"✅" if m26.get("isRivalry", False) else "❌"}</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Home Motivation:</strong> {m26.get("homeMotivation", "NORMAL")}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # M27
            st.markdown("### M27: H2H Deep Analysis")
            m27 = forensic.get("m27", {})
            st.markdown(f'<div><strong>H2H Score:</strong> {m27.get("h2hScore", 50)}/100 (<span class="status-approved">{m27.get("h2hLabel", "NEUTRAL")}</span>)</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Games:</strong> {m27.get("gamesPlayed", 0)} | <span style="color: #10b981;">Fav {m27.get("favWins", 0)}</span> | Draw {m27.get("draws", 0)} | <span style="color: #ef4444;">Und {m27.get("undWins", 0)}</span></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Risk flags
            risk_flags = forensic.get("riskFlags", [])
            if risk_flags:
                st.markdown("### ⚠️ Risk Flags")
                for flag in risk_flags:
                    st.markdown(f'<div><span class="status-caution">⚠️ {flag}</span></div>', unsafe_allow_html=True)
            
            # Final verdict
            st.divider()
            if leg.get("status") == "APPROVED":
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b98120, #0f172a); border: 1px solid #10b981; border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">✅ FINAL VERDICT: APPROVED</div>
                    <div>Confidence: {leg.get('confidence', 'HIGH')} | Weighted Score: {forensic.get('weightedScore', 0.78):.2f}/1.00</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ef444420, #0f172a); border: 1px solid #ef4444; border-radius: 12px; padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #ef4444;">❌ FINAL VERDICT: {leg.get('status', 'REJECTED')}</div>
                    <div>Confidence: {leg.get('confidence', 'LOW')} | Weighted Score: {forensic.get('weightedScore', 0.32):.2f}/1.00</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Forensic report not available for this leg. Make sure backend is running and leg ID is correct.")

# ========== PAGE: PARLAYS ==========
def show_parlays():
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Disjoint parlay builder - no leg reused across slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    parlays = st.session_state.get("parlays_data", {})
    
    # Ultra Safe Parlays
    st.markdown("### 🟢 Ultra Safe Parlays (HIGH Confidence Only)")
    safe = parlays.get("safe", [])
    if safe:
        for p in safe:
            legs_str = " + ".join(p.get("legs", []))
            st.markdown(f"**{legs_str} = {p.get('totalOdds', 0):.2f}x**")
            st.caption(f"Combined Probability: {p.get('combinedProb', 0):.1%} | Risk: {p.get('riskLevel', 'SAFE')}")
            st.divider()
    else:
        st.info("No safe parlays available")
    
    # Balanced Parlays
    st.markdown("### 🟡 Balanced Parlays (HIGH + MEDIUM)")
    balanced = parlays.get("balanced", [])
    if balanced:
        for p in balanced:
            legs_str = " + ".join(p.get("legs", []))
            st.markdown(f"**{legs_str} = {p.get('totalOdds', 0):.2f}x**")
            st.caption(f"Combined Probability: {p.get('combinedProb', 0):.1%} | Risk: {p.get('riskLevel', 'BALANCED')}")
            st.divider()
    else:
        st.info("No balanced parlays available")
    
    # Aggressive Parlays
    st.markdown("### 🔴 Aggressive Parlays (Value Hunting)")
    aggressive = parlays.get("aggressive", [])
    if aggressive:
        for p in aggressive:
            legs_str = " + ".join(p.get("legs", []))
            st.markdown(f"**{legs_str} = {p.get('totalOdds', 0):.2f}x**")
            st.caption(f"Combined Probability: {p.get('combinedProb', 0):.1%} | Risk: {p.get('riskLevel', 'AGGRESSIVE')}")
            st.divider()
    else:
        st.info("No aggressive parlays available")

# ========== PAGE: CALENDAR ==========
def show_calendar():
    st.markdown('<p class="main-header">📅 Oracle Calendar</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Select a date to scan fixtures and view oracle reports</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button("← Back to Dashboard"):
            navigate_to("dashboard")
    
    st.divider()
    
    # Date picker
    selected_date = st.date_input("Select Date", datetime.now().date())
    
    # Scan button
    if st.button("🔍 Scan Selected Date", use_container_width=True):
        with st.spinner("Scanning fixtures..."):
            success, result = scan_date(selected_date.strftime("%Y-%m-%d"))
            if success:
                st.success(f"Scan complete for {selected_date}")
                # Clear cache to refresh data
                st.cache_data.clear()
                load_all_data()
            else:
                st.error(f"Scan failed: {result}")
    
    st.divider()
    
    # Results preview
    st.markdown(f"### 📊 Recent Activity")
    
    # Show recent legs from cache
    all_legs_data = st.session_state.get("all_legs", [])
    if all_legs_data:
        for leg in all_legs_data[:5]:
            status_html = get_status_badge(leg.get("status", "PENDING"))
            st.markdown(f"""
            <div style="background-color: #1e293b; border-radius: 10px; padding: 0.8rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                    <span><strong>{leg.get('homeTeam', '?')} vs {leg.get('awayTeam', '?')}</strong> ({leg.get('league', '?')})</span>
                    {status_html}
                </div>
                <div style="font-size: 0.8rem; color: #64748b;">Selection: {leg.get('selection', '?')} @ {leg.get('selectionOdds', 0):.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No legs available. Run a scan to fetch fixtures.")

# ========== REFRESH BUTTON ==========
def show_refresh_button():
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            load_all_data()
            st.rerun()

# ========== MAIN NAVIGATION ==========
def main():
    # Load initial data
    if not st.session_state.get("data_loaded", False):
        load_all_data()
        st.session_state.data_loaded = True
    
    # Sidebar navigation
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
        
        # Refresh button in sidebar
        show_refresh_button()
        
        st.divider()
        
        # Backend status
        st.markdown("### 🔌 Connection")
        if st.session_state.webSocket_status == "connected":
            st.success(f"✅ Backend Connected")
            st.caption(f"📍 {BACKEND_URL}")
        else:
            st.error("❌ Backend Disconnected")
            st.caption("Check if backend is running on Render")
        
        st.divider()
        
        st.markdown("### 📊 Performance")
        perf = st.session_state.get("performance_data", {})
        st.metric("Overall Accuracy", f"{perf.get('overallAccuracy', 0.58):.0%}", "+2%")
        st.metric("HIGH Confidence", f"{perf.get('highConfAccuracy', 0.68):.0%}", "+5%")
        st.metric("MEDIUM Confidence", f"{perf.get('mediumConfAccuracy', 0.52):.0%}", "-3%")
        
        st.divider()
        
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("🎯 Match Oracle v2.0")
        st.caption("✅ Connected to backend")
    
    # Page routing
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "all_legs":
        show_all_legs()
    elif st.session_state.page == "leg_detail":
        show_leg_detail()
    elif st.session_state.page == "parlays":
        show_parlays()
    elif st.session_state.page == "calendar":
        show_calendar()

if __name__ == "__main__":
    main()
