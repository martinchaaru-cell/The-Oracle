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
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    .dataframe thead tr th {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    /* Clickable row effect */
    .clickable-row:hover {
        background-color: #1e293b !important;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE INITIALIZATION ==========
if "selected_leg" not in st.session_state:
    st.session_state.selected_leg = None
if "show_detail" not in st.session_state:
    st.session_state.show_detail = False
if "webSocket_status" not in st.session_state:
    st.session_state.webSocket_status = "disconnected"

# ========== MOCK DATA (Replace with API calls later) ==========
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

# All legs data (clickable)
all_legs = [
    {"match": "Arsenal vs Chelsea", "league": "Premier League", "kickoff": "15:00", "home": "Arsenal", "away": "Chelsea", 
     "selection": "Arsenal", "odds": 2.10, "prob": 0.62, "edge": 0.081, "status": "APPROVED", "confidence": "HIGH"},
    {"match": "Man City vs Liverpool", "league": "Premier League", "kickoff": "17:30", "home": "Man City", "away": "Liverpool", 
     "selection": "Man City", "odds": 1.95, "prob": 0.54, "edge": 0.022, "status": "CAUTION", "confidence": "MEDIUM"},
    {"match": "Real Madrid vs Barcelona", "league": "La Liga", "kickoff": "20:00", "home": "Real Madrid", "away": "Barcelona", 
     "selection": "Real Madrid", "odds": 2.25, "prob": 0.48, "edge": -0.017, "status": "REJECTED", "confidence": "LOW"},
    {"match": "Bayern Munich vs Dortmund", "league": "Bundesliga", "kickoff": "15:00", "home": "Bayern Munich", "away": "Dortmund", 
     "selection": "Bayern Munich", "odds": 1.75, "prob": 0.58, "edge": 0.067, "status": "APPROVED", "confidence": "HIGH"},
    {"match": "Inter Milan vs Juventus", "league": "Serie A", "kickoff": "19:45", "home": "Inter Milan", "away": "Juventus", 
     "selection": "Inter Milan", "odds": 2.05, "prob": 0.55, "edge": 0.042, "status": "APPROVED", "confidence": "MEDIUM"},
    {"match": "PSG vs Marseille", "league": "Ligue 1", "kickoff": "16:00", "home": "PSG", "away": "Marseille", 
     "selection": "PSG", "odds": 1.55, "prob": 0.68, "edge": 0.113, "status": "APPROVED", "confidence": "HIGH"},
    {"match": "Ajax vs Feyenoord", "league": "Eredivisie", "kickoff": "14:30", "home": "Ajax", "away": "Feyenoord", 
     "selection": "Ajax", "odds": 1.85, "prob": 0.57, "edge": 0.051, "status": "APPROVED", "confidence": "HIGH"},
]

# Bankroll history
bankroll_history = pd.DataFrame({
    "Date": ["Jun 1", "Jun 2", "Jun 3", "Jun 4", "Jun 5", "Jun 6", "Jun 7", "Jun 8"],
    "Bankroll": [10000, 10250, 10500, 10300, 10800, 11200, 11800, 12450],
})

# Status distribution
status_counts = {"APPROVED": 12, "REJECTED": 28, "CAUTION": 7}

# ========== HEADER SECTION ==========
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

# ========== METRICS ROW (4 cards) ==========
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

# ========== 3-COLUMN LAYOUT ==========
col_left, col_center, col_right = st.columns(3)

# ----- LEFT COLUMN: TOP PICKS -----
with col_left:
    st.markdown("### 🏆 Top Picks")
    
    for i, pick in enumerate(top_picks, 1):
        edge_color = "#10b981" if pick["edge"] > 0 else "#ef4444"
        edge_symbol = "+" if pick["edge"] > 0 else ""
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 10px; padding: 0.8rem; margin-bottom: 0.8rem; border-left: 3px solid #3b82f6;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: bold;">#{i}</span>
                    <span style="margin-left: 0.5rem;">{pick['match']}</span>
                </div>
                <span style="background-color: #3b82f620; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem;">{pick['confidence']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                <span style="font-size: 0.9rem;">{pick['selection']} @ {pick['odds']:.2f}</span>
                <span style="color: {edge_color};">{edge_symbol}{pick['edge']*100:.1f}% edge</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----- CENTER COLUMN: LEGS BY LEAGUE (BAR CHART) -----
with col_center:
    st.markdown("### 📊 Legs by League")
    
    league_df = pd.DataFrame(league_counts)
    fig = px.bar(
        league_df,
        x="league",
        y="count",
        color="count",
        color_continuous_scale="blues",
        text="count"
    )
    fig.update_layout(
        plot_bgcolor="#1e293b",
        paper_bgcolor="#1e293b",
        font_color="white",
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title=None,
        yaxis_title=None
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ----- RIGHT COLUMN: STATUS PIE CHART -----
with col_right:
    st.markdown("### 📈 Status Distribution")
    
    status_df = pd.DataFrame([
        {"Status": "Approved", "Count": status_counts["APPROVED"], "Color": "#10b981"},
        {"Status": "Rejected", "Count": status_counts["REJECTED"], "Color": "#ef4444"},
        {"Status": "Caution", "Count": status_counts["CAUTION"], "Color": "#f59e0b"},
    ])
    
    fig = px.pie(
        status_df,
        values="Count",
        names="Status",
        color="Status",
        color_discrete_map={
            "Approved": "#10b981",
            "Rejected": "#ef4444",
            "Caution": "#f59e0b"
        },
        hole=0.4
    )
    fig.update_layout(
        plot_bgcolor="#1e293b",
        paper_bgcolor="#1e293b",
        font_color="white",
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ========== ALL LEGS TABLE ==========
st.markdown("### 📋 All Legs Analyzed")

# Search bar
search_col, filter_col = st.columns([3, 1])
with search_col:
    search_term = st.text_input("🔍 Search matches, leagues, or selections", placeholder="e.g., Arsenal, Premier League...", label_visibility="collapsed")
with filter_col:
    show_only_approved = st.checkbox("Show only APPROVED", value=False)

# Filter data
filtered_legs = all_legs.copy()

if search_term:
    search_lower = search_term.lower()
    filtered_legs = [
        leg for leg in filtered_legs
        if search_lower in leg["match"].lower()
        or search_lower in leg["league"].lower()
        or search_lower in leg["selection"].lower()
    ]

if show_only_approved:
    filtered_legs = [leg for leg in filtered_legs if leg["status"] == "APPROVED"]

# Create display dataframe
display_df = pd.DataFrame([
    {
        "Match": leg["match"],
        "League": leg["league"],
        "Kickoff": leg["kickoff"],
        "Selection": leg["selection"],
        "Odds": leg["odds"],
        "Prob": f"{leg['prob']*100:.0f}%",
        "Edge": f"{'+' if leg['edge']>0 else ''}{leg['edge']*100:.1f}%",
        "Status": leg["status"],
        "Confidence": leg["confidence"],
        "leg_index": i  # Hidden for click handling
    }
    for i, leg in enumerate(filtered_legs)
])

# Display table with custom formatting
st.dataframe(
    display_df.drop(columns=["leg_index"]),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Odds": st.column_config.NumberColumn(format="%.2f"),
        "Status": st.column_config.Column(
            width="small",
        ),
        "Confidence": st.column_config.Column(width="small"),
    }
)

st.caption(f"Showing {len(filtered_legs)} of {len(all_legs)} legs")

st.divider()

# ========== BANKROLL HISTORY CHART ==========
st.markdown("### 📉 Bankroll History")

fig = px.line(
    bankroll_history,
    x="Date",
    y="Bankroll",
    markers=True,
    line_shape="spline"
)
fig.update_layout(
    plot_bgcolor="#1e293b",
    paper_bgcolor="#1e293b",
    font_color="white",
    height=350,
    xaxis_title=None,
    yaxis_title="Bankroll ($)"
)
fig.update_traces(line_color="#3b82f6", line_width=2, marker_color="#3b82f6", marker_size=6)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ========== FOOTER ==========
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
    <div style="font-size: 0.7rem; color: #475569;">
        ⚠️ Demo with mock data | Connect backend for live predictions
    </div>
    <div style="font-size: 0.7rem; color: #475569;">
        Match Oracle v1.0
    </div>
</div>
""", unsafe_allow_html=True)

# ========== HIDDEN LEG DETAIL (For future click handling) ==========
# This will be expanded when backend is connected
# Clicking a leg will show full forensic report here
if st.session_state.show_detail and st.session_state.selected_leg:
    st.divider()
    st.markdown("### 🔬 Forensic Report")
    st.info(f"Leg details for {st.session_state.selected_leg['match']} will appear here when backend is connected.")
