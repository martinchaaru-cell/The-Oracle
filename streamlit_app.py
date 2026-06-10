import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    /* Navigation tabs */
    .nav-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.5rem;
    }
    .nav-tab {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        color: #94a3b8;
        transition: all 0.2s;
    }
    .nav-tab:hover {
        background-color: #1e293b;
        color: #e2e8f0;
    }
    .nav-tab-active {
        background-color: #3b82f6;
        color: white;
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

# ========== MOCK DATA (Replace with API calls when backend is ready) ==========

# Bankroll data
bankroll = 12450
peak = 13200
drawdown = (peak - bankroll) / peak

# Top picks data
top_picks = [
    {"match": "Arsenal vs Chelsea", "selection": "Arsenal", "odds": 2.10, "prob": 0.62, "edge": 0.081, "confidence": "HIGH"},
    {"match": "Bayern Munich vs Dortmund", "selection": "Bayern Munich", "odds": 1.75, "prob": 0.58, "edge": 0.067, "confidence": "HIGH"},
    {"match": "Inter Milan vs Juventus", "selection": "Inter Milan", "odds": 2.05, "prob": 0.55, "edge": 0.042, "confidence": "MEDIUM"},
]

# League counts
league_counts = [
    {"league": "Premier League", "count": 12},
    {"league": "La Liga", "count": 10},
    {"league": "Bundesliga", "count": 8},
    {"league": "Serie A", "count": 8},
    {"league": "Ligue 1", "count": 6},
    {"league": "Eredivisie", "count": 3},
]

# All legs data (for table)
all_legs = [
    {"id": 0, "match": "Arsenal vs Chelsea", "league": "Premier League", "kickoff": "15:00", "home": "Arsenal", "away": "Chelsea", 
     "selection": "Arsenal", "odds": 2.10, "prob": 0.62, "edge": 0.081, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 1, "match": "Man City vs Liverpool", "league": "Premier League", "kickoff": "17:30", "home": "Man City", "away": "Liverpool", 
     "selection": "Man City", "odds": 1.95, "prob": 0.54, "edge": 0.022, "status": "CAUTION", "confidence": "MEDIUM"},
    {"id": 2, "match": "Real Madrid vs Barcelona", "league": "La Liga", "kickoff": "20:00", "home": "Real Madrid", "away": "Barcelona", 
     "selection": "Real Madrid", "odds": 2.25, "prob": 0.48, "edge": -0.017, "status": "REJECTED", "confidence": "LOW"},
    {"id": 3, "match": "Bayern Munich vs Dortmund", "league": "Bundesliga", "kickoff": "15:00", "home": "Bayern Munich", "away": "Dortmund", 
     "selection": "Bayern Munich", "odds": 1.75, "prob": 0.58, "edge": 0.067, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 4, "match": "Inter Milan vs Juventus", "league": "Serie A", "kickoff": "19:45", "home": "Inter Milan", "away": "Juventus", 
     "selection": "Inter Milan", "odds": 2.05, "prob": 0.55, "edge": 0.042, "status": "APPROVED", "confidence": "MEDIUM"},
    {"id": 5, "match": "PSG vs Marseille", "league": "Ligue 1", "kickoff": "16:00", "home": "PSG", "away": "Marseille", 
     "selection": "PSG", "odds": 1.55, "prob": 0.68, "edge": 0.113, "status": "APPROVED", "confidence": "HIGH"},
    {"id": 6, "match": "Ajax vs Feyenoord", "league": "Eredivisie", "kickoff": "14:30", "home": "Ajax", "away": "Feyenoord", 
     "selection": "Ajax", "odds": 1.85, "prob": 0.57, "edge": 0.051, "status": "APPROVED", "confidence": "HIGH"},
]

# Bankroll history
bankroll_history = pd.DataFrame({
    "Date": ["Jun 1", "Jun 2", "Jun 3", "Jun 4", "Jun 5", "Jun 6", "Jun 7", "Jun 8"],
    "Bankroll": [10000, 10250, 10500, 10300, 10800, 11200, 11800, 12450],
})

# Status distribution
status_counts = {"APPROVED": 12, "REJECTED": 28, "CAUTION": 7}

# Parlays data
parlays_data = {
    "safe": [
        {"legs": ["Arsenal (2.10)", "Bayern (1.75)"], "total_odds": 3.68, "prob": 0.36, "risk": "SAFE"},
        {"legs": ["PSG (1.55)", "Inter (2.05)"], "total_odds": 3.18, "prob": 0.42, "risk": "SAFE"},
    ],
    "balanced": [
        {"legs": ["Arsenal (2.10)", "Bayern (1.75)", "PSG (1.55)"], "total_odds": 5.70, "prob": 0.22, "risk": "BALANCED"},
    ],
    "aggressive": [
        {"legs": ["Arsenal (2.10)", "Bayern (1.75)", "Inter (2.05)", "Ajax (1.85)"], "total_odds": 13.95, "prob": 0.11, "risk": "AGGRESSIVE"},
    ]
}

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

# ========== PAGE: DASHBOARD ==========
def show_dashboard():
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
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${bankroll:,}</div>
            <div class="metric-label">Bankroll</div>
            <div style="font-size: 0.7rem; color: #ef4444;">▼ {drawdown:.1%} from peak</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">47</div>
            <div class="metric-label">Today's Legs</div>
            <div style="font-size: 0.7rem; color: #10b981;">▲ 12 approved</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">$847</div>
            <div class="metric-label">Total Staked</div>
            <div style="font-size: 0.7rem; color: #10b981;">▲ $2,150 potential</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">Grade B</div>
            <div class="metric-label">System Health</div>
            <div style="font-size: 0.7rem; color: #3b82f6;">58% accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 3-column layout
    col_left, col_center, col_right = st.columns(3)
    
    with col_left:
        st.markdown("### 🏆 Top Picks")
        for i, pick in enumerate(top_picks, 1):
            edge_color = get_edge_color(pick["edge"])
            edge_symbol = "+" if pick["edge"] > 0 else ""
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 10px; padding: 0.8rem; margin-bottom: 0.8rem; border-left: 3px solid #3b82f6;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: bold;">#{i}</span>
                        <span style="margin-left: 0.5rem;">{pick['match']}</span>
                    </div>
                    <span class="status-approved" style="background-color: #3b82f620;">{pick['confidence']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                    <span style="font-size: 0.9rem;">{pick['selection']} @ {pick['odds']:.2f}</span>
                    <span style="color: {edge_color};">{edge_symbol}{pick['edge']*100:.1f}% edge</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_center:
        st.markdown("### 📊 Legs by League")
        league_df = pd.DataFrame(league_counts)
        fig = px.bar(league_df, x="league", y="count", color="count", color_continuous_scale="blues", text="count")
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown("### 📈 Status Distribution")
        status_df = pd.DataFrame([
            {"Status": "Approved", "Count": status_counts["APPROVED"]},
            {"Status": "Rejected", "Count": status_counts["REJECTED"]},
            {"Status": "Caution", "Count": status_counts["CAUTION"]},
        ])
        fig = px.pie(status_df, values="Count", names="Status", color="Status",
                     color_discrete_map={"Approved": "#10b981", "Rejected": "#ef4444", "Caution": "#f59e0b"}, hole=0.4)
        fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent Legs preview
    st.markdown("### 📋 Recent Legs")
    preview_legs = all_legs[:5]
    for leg in preview_legs:
        edge_color = get_edge_color(leg["edge"])
        edge_symbol = "+" if leg["edge"] > 0 else ""
        status_html = get_status_badge(leg["status"])
        st.markdown(f"""
        <div style="background-color: #1e293b; border-radius: 10px; padding: 0.8rem; margin-bottom: 0.5rem; cursor: pointer;" onclick="window.location.href='?page=leg_detail'">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: bold;">{leg['match']}</span>
                    <span style="font-size: 0.7rem; color: #64748b; margin-left: 0.5rem;">{leg['league']} • {leg['kickoff']}</span>
                </div>
                {status_html}
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                <span>{leg['selection']} @ {leg['odds']:.2f}</span>
                <span style="color: {edge_color};">{edge_symbol}{leg['edge']*100:.1f}% edge</span>
                <span style="color: #64748b;">{(leg['prob']*100):.0f}% prob</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn2:
        if st.button("🔍 View All Legs", use_container_width=True):
            navigate_to("all_legs")
    
    st.divider()
    
    # Bankroll chart
    st.markdown("### 📉 Bankroll History")
    fig = px.line(bankroll_history, x="Date", y="Bankroll", markers=True, line_shape="spline")
    fig.update_layout(plot_bgcolor="#1e293b", paper_bgcolor="#1e293b", font_color="white", height=350)
    fig.update_traces(line_color="#3b82f6", line_width=2, marker_color="#3b82f6", marker_size=6)
    st.plotly_chart(fig, use_container_width=True)

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
    
    # Filter data
    filtered_legs = all_legs.copy()
    if search_term:
        search_lower = search_term.lower()
        filtered_legs = [leg for leg in filtered_legs if search_lower in leg["match"].lower() or search_lower in leg["league"].lower() or search_lower in leg["selection"].lower()]
    if show_only_approved:
        filtered_legs = [leg for leg in filtered_legs if leg["status"] == "APPROVED"]
    
    # Display table with clickable rows
    st.markdown("### Click any row to view full forensic report")
    
    for leg in filtered_legs:
        edge_color = get_edge_color(leg["edge"])
        edge_symbol = "+" if leg["edge"] > 0 else ""
        status_html = get_status_badge(leg["status"])
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1.5, 0.8, 1, 0.8, 1, 1.2])
        with col1:
            st.write(f"**{leg['match']}**")
        with col2:
            st.write(leg['league'])
        with col3:
            st.write(leg['kickoff'])
        with col4:
            st.write(f"{leg['selection']} @ {leg['odds']:.2f}")
        with col5:
            st.write(f"{(leg['prob']*100):.0f}%")
        with col6:
            st.markdown(f'<span style="color: {edge_color};">{edge_symbol}{leg["edge"]*100:.1f}%</span>', unsafe_allow_html=True)
        with col7:
            st.markdown(status_html, unsafe_allow_html=True)
        
        # View button
        if st.button(f"🔍 View Details", key=f"view_{leg['id']}", use_container_width=True):
            navigate_to("leg_detail", leg_id=leg["id"], leg_data=leg)
        st.divider()
    
    st.caption(f"Showing {len(filtered_legs)} of {len(all_legs)} legs")

# ========== PAGE: LEG DETAIL (2 TABS) ==========
def show_leg_detail():
    leg = st.session_state.selected_leg
    if leg is None:
        st.warning("No leg selected")
        if st.button("← Back to All Legs"):
            navigate_to("all_legs")
        return
    
    # Header
    st.markdown(f'<p class="main-header">🔬 {leg["match"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{leg["league"]} • {leg["kickoff"]} | Selection: {leg["selection"]} @ {leg["odds"]:.2f}</p>', unsafe_allow_html.html, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to All Legs"):
        navigate_to("all_legs")
    
    st.divider()
    
    # Two tabs
    tab1, tab2 = st.tabs(["📊 Season Data", "🔬 Full Forensic Report (M4-M27)"])
    
    # ========== TAB 1: SEASON DATA ==========
    with tab1:
        # Team form
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📈 Form (Last 10 Games)")
            home_form = ["W", "W", "D", "W", "L", "W", "W", "D", "W", "W"]
            away_form = ["L", "L", "D", "L", "W", "L", "L", "D", "L", "L"]
            
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                st.markdown(f"**{leg['home']}**")
                form_html = "".join([f'<span class="check-pass" style="margin: 0 2px;">{r}</span>' for r in home_form])
                st.markdown(form_html, unsafe_allow_html=True)
            with form_col2:
                st.markdown(f"**{leg['away']}**")
                form_html = "".join([f'<span class="check-fail" style="margin: 0 2px;">{r}</span>' if r == "L" else f'<span class="check-pass" style="margin: 0 2px;">{r}</span>' for r in away_form])
                st.markdown(form_html, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🏟️ Home/Away Performance")
            home_perf = pd.DataFrame({
                "Venue": ["Home", "Away"],
                "Win %": [68, 42],
                "Goals/Game": [2.1, 1.3],
                "Clean Sheets %": [45, 28]
            })
            st.dataframe(home_perf, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Goals and xG
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⚽ Goals Analysis")
            goals_data = pd.DataFrame({
                "Metric": ["Goals Scored", "Goals Conceded", "xG", "xGA"],
                "Home": [38, 18, 35.2, 22.5],
                "Away": [24, 28, 26.8, 30.1]
            })
            st.dataframe(goals_data, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📊 League Position")
            st.metric("Current Position", "4th", "▲ +2")
            st.metric("Points", "59", "+3 last 5")
            st.metric("Points to Top 4", "6", "2 games in hand")
        
        st.divider()
        
        # Head to Head
        st.markdown("### 📜 Head to Head History")
        h2h_data = pd.DataFrame([
            {"Date": "2025-02-15", "Venue": "Home", "Result": "2-1", "Outcome": "W"},
            {"Date": "2024-10-20", "Venue": "Away", "Result": "1-1", "Outcome": "D"},
            {"Date": "2024-04-10", "Venue": "Home", "Result": "3-0", "Outcome": "W"},
            {"Date": "2023-12-01", "Venue": "Away", "Result": "0-2", "Outcome": "L"},
            {"Date": "2023-08-25", "Venue": "Home", "Result": "2-2", "Outcome": "D"},
        ])
        st.dataframe(h2h_data, use_container_width=True, hide_index=True)
        
        st.caption(f"Last 5 meetings: {leg['home']} wins 2, Draws 2, {leg['away']} wins 1")
    
    # ========== TAB 2: FORENSIC REPORT (M4-M27) ==========
    with tab2:
        st.markdown("### M4: Asymmetric Pre-filter (8 Checks)")
        m4_checks = [
            {"check": "C1: Season Win Gap", "passed": True, "value": 14, "threshold": 3},
            {"check": "C2: Venue Win Gap", "passed": True, "value": 0.22, "threshold": 0.15},
            {"check": "C3: H2H Favoured", "passed": True, "value": 0.65, "threshold": 0.50},
            {"check": "C4: Transition Favours", "passed": True, "value": 0.58, "threshold": 0.45},
            {"check": "C5: Bounce-back Rate", "passed": False, "value": 0.38, "threshold": 0.45},
            {"check": "C6: Ceiling Proximity", "passed": True, "value": 0.72, "threshold": 0.88},
            {"check": "C7: Momentum Gap", "passed": True, "value": 0.40, "threshold": 0.20},
            {"check": "C8: Resilience Gap", "passed": True, "value": 0.42, "threshold": 0.10},
        ]
        for check in m4_checks:
            status_class = "check-pass" if check["passed"] else "check-fail"
            status_text = "PASS" if check["passed"] else "FAIL"
            st.markdown(f'<div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;"><span>{check["check"]}</span><span class="{status_class}">{status_text}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top: 1rem;"><strong>Result:</strong> 6/8 passed → {"✅ APPROVED" if leg["status"] == "APPROVED" else "❌ REJECTED"}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### M5: Forensic Failures")
        failures = [
            {"failure": "New Manager Bounce (underdog)", "points": 2.0},
            {"failure": "High Draw Probability (25%)", "points": 1.0},
        ]
        for f in failures:
            st.markdown(f'<div style="display: flex; justify-content: space-between;"><span>⚠️ {f["failure"]}</span><span style="color: #ef4444;">+{f["points"]} pts</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top: 1rem;"><strong>Total Failure Score:</strong> 2.5 / 4.5 → {"PASS" if leg["status"] == "APPROVED" else "FAIL"}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### M6: Personnel")
            st.markdown(f"**{leg['home']}**")
            st.markdown(f'<span class="metric-value">82/100</span><br><span class="metric-label">Key injuries: None</span><br><span class="metric-label">Fatigue: LOW</span>', unsafe_allow_html=True)
            st.markdown(f"**{leg['away']}**")
            st.markdown(f'<span class="metric-value">65/100</span><br><span class="metric-label">Key injuries: 1 (midfielder)</span><br><span class="metric-label">Fatigue: MEDIUM</span>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### M7: AI Consensus")
            ai_data = pd.DataFrame({
                "Provider": ["DeepSeek", "Claude", "Gemini", "GPT"],
                "Verdict": ["APPROVE", "APPROVE", "CAUTION", "APPROVE"],
                "Confidence": ["78%", "72%", "55%", "75%"]
            })
            st.dataframe(ai_data, use_container_width=True, hide_index=True)
            st.markdown('<div style="margin-top: 1rem;"><strong>Consensus:</strong> 3/4 APPROVE → ✅ APPROVED</div>', unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### M8: Dual Pattern")
            st.markdown(f'<div><strong>Dual Risk Level:</strong> <span class="check-pass">LOW</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Underdog Threat:</strong> NONE</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Pattern Clash Score:</strong> 0.18</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Resilience Gap:</strong> <span style="color: #10b981;">+0.24</span></div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### M9: Underdog Scanner")
            st.markdown(f'<div><strong>Underdog Edge:</strong> -2.1%</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Threat Level:</strong> <span class="check-pass">LOW</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Pattern Score:</strong> 22/100</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Goldmine:</strong> ❌ No</div>', unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### M10: Tally Matrix")
            st.markdown(f'<div><strong>Matrix Useful:</strong> ✅ YES</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Bilateral Prediction:</strong> HOME</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Bilateral Confidence:</strong> <span class="check-pass">HIGH</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Trap/Value Signal:</strong> NONE</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### M26: Match Context")
            st.markdown(f'<div><strong>Match Importance:</strong> 72%</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Is Rivalry:</strong> ✅ Yes (London Derby)</div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Home Motivation:</strong> <span class="check-pass">HIGH</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div><strong>Away Motivation:</strong> NORMAL</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### M27: H2H Deep Analysis")
        st.markdown(f'<div><strong>H2H Score:</strong> 78/100 (<span class="status-approved">FAV_EDGE</span>)</div>', unsafe_allow_html=True)
        st.markdown(f'<div><strong>Games:</strong> 48 | <span style="color: #10b981;">Fav 29</span> | Draw 11 | <span style="color: #ef4444;">Und 8</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div><strong>Draw Rate:</strong> 23% | <strong>Draw Boost:</strong> 1.00x</div>', unsafe_allow_html=True)
        st.markdown(f'<div><strong>Psychological Block:</strong> ❌ No</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Final verdict
        if leg["status"] == "APPROVED":
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10b98120, #0f172a); border: 1px solid #10b981; border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">✅ FINAL VERDICT: APPROVED</div>
                <div>Confidence: {leg['confidence']} | Weighted Score: 0.78/1.00</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ef444420, #0f172a); border: 1px solid #ef4444; border-radius: 12px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #ef4444;">❌ FINAL VERDICT: {leg['status']}</div>
                <div>Confidence: {leg['confidence']} | Weighted Score: 0.32/1.00</div>
            </div>
            """, unsafe_allow_html=True)

# ========== PAGE: PARLAYS ==========
def show_parlays():
    st.markdown('<p class="main-header">🔗 Parlays & ACCA Slips</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Disjoint parlay builder - no leg reused across slips</p>', unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    # Ultra Safe Parlays
    st.markdown("### 🟢 Ultra Safe Parlays (HIGH Confidence Only)")
    for p in parlays_data["safe"]:
        with st.expander(f"➕ {' + '.join(p['legs'])} = {p['total_odds']:.2f}x"):
            st.markdown(f"**Combined Probability:** {p['prob']:.1%}")
            st.markdown(f"**Risk Level:** <span class='status-approved'>{p['risk']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Suggested Stake:** ${(100 * 0.03):.2f} (3% of bankroll)")
            st.markdown(f"**Potential Return:** ${(100 * 0.03 * p['total_odds']):.2f}")
    
    st.divider()
    
    # Balanced Parlays
    st.markdown("### 🟡 Balanced Parlays (HIGH + MEDIUM)")
    for p in parlays_data["balanced"]:
        with st.expander(f"➕ {' + '.join(p['legs'])} = {p['total_odds']:.2f}x"):
            st.markdown(f"**Combined Probability:** {p['prob']:.1%}")
            st.markdown(f"**Risk Level:** <span class='status-caution'>{p['risk']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Suggested Stake:** ${(100 * 0.02):.2f} (2% of bankroll)")
            st.markdown(f"**Potential Return:** ${(100 * 0.02 * p['total_odds']):.2f}")
    
    st.divider()
    
    # Aggressive Parlays
    st.markdown("### 🔴 Aggressive Parlays (Value Hunting)")
    for p in parlays_data["aggressive"]:
        with st.expander(f"➕ {' + '.join(p['legs'])} = {p['total_odds']:.2f}x"):
            st.markdown(f"**Combined Probability:** {p['prob']:.1%}")
            st.markdown(f"**Risk Level:** <span class='status-rejected'>{p['risk']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Suggested Stake:** ${(100 * 0.01):.2f} (1% of bankroll)")
            st.markdown(f"**Potential Return:** ${(100 * 0.01 * p['total_odds']):.2f}")

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
            time.sleep(1)
            st.success(f"Scan complete for {selected_date}")
    
    st.divider()
    
    # Results preview
    st.markdown(f"### 📊 Oracle Report for {selected_date}")
    
    # Stats for selected date
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Legs", "47", "▲ +12 from yesterday")
    with col2:
        st.metric("Approved", "12", "▲ +3")
    with col3:
        st.metric("Rejected", "28", "▼ -5")
    with col4:
        st.metric("Caution", "7", "0")
    
    st.divider()
    
    # Legs for selected date
    st.markdown("#### Legs Analyzed")
    for leg in all_legs[:5]:
        status_html = get_status_badge(leg["status"])
        st.markdown(f"""
        <div style="background-color: #1e293b; border-radius: 10px; padding: 0.8rem; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between;">
                <span><strong>{leg['match']}</strong> ({leg['league']})</span>
                {status_html}
            </div>
            <div style="font-size: 0.8rem; color: #64748b;">Selection: {leg['selection']} @ {leg['odds']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# ========== MAIN NAVIGATION ==========
def main():
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
        
        st.markdown("### 🔧 Filters")
        st.multiselect("Status", ["APPROVED", "CAUTION", "REJECTED"], key="sidebar_status_filter")
        st.multiselect("League", ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"], key="sidebar_league_filter")
        
        st.divider()
        
        st.markdown("### 📊 Performance")
        st.metric("Overall Accuracy", "58%", "+2%")
        st.metric("HIGH Confidence", "68%", "+5%")
        st.metric("MEDIUM Confidence", "52%", "-3%")
        
        st.divider()
        
        st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption("🎯 Match Oracle v2.0")
        st.caption("⚡ Ready for backend connection")
    
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
