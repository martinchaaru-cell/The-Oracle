import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Match Oracle", layout="wide")

# Title
st.title("🎯 Match Oracle")
st.caption("AI-powered football prediction platform")

# Mock data
bankroll = 12450
peak = 13200
drawdown = (peak - bankroll) / peak

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Bankroll", f"${bankroll:,}", f"-{drawdown:.1%}" if drawdown > 0 else None)
with col2:
    st.metric("Today's Legs", 47, "12 approved")
with col3:
    st.metric("Total Staked", "$847.50", "$2,150 potential")
with col4:
    st.metric("System Health", "B", "58% accuracy")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Legs by League")
    league_data = pd.DataFrame({
        "League": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
        "Count": [12, 10, 8, 8, 6]
    })
    fig = px.bar(league_data, x="League", y="Count", color="Count")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Status Distribution")
    status_data = pd.DataFrame({
        "Status": ["Approved", "Rejected", "Caution"],
        "Count": [12, 28, 7]
    })
    fig = px.pie(status_data, values="Count", names="Status", color="Status",
                 color_discrete_map={"Approved": "green", "Rejected": "red", "Caution": "orange"})
    st.plotly_chart(fig, use_container_width=True)

# Top picks
st.subheader("🏆 Top Picks")
top_picks = pd.DataFrame([
    {"Match": "Arsenal vs Chelsea", "Selection": "Arsenal", "Odds": 2.10, "Probability": "62%", "Edge": "+8.1%"},
    {"Match": "Bayern vs Dortmund", "Selection": "Bayern", "Odds": 1.75, "Probability": "58%", "Edge": "+6.7%"},
    {"Match": "Inter vs Juventus", "Selection": "Inter", "Odds": 2.05, "Probability": "55%", "Edge": "+4.2%"},
])
st.dataframe(top_picks, use_container_width=True)

# All legs table
st.subheader("📋 All Legs")
all_legs = pd.DataFrame([
    {"Match": "Arsenal vs Chelsea", "League": "Premier League", "Selection": "Arsenal", "Odds": 2.10, "Status": "✅ APPROVED"},
    {"Match": "Man City vs Liverpool", "League": "Premier League", "Selection": "Man City", "Odds": 1.95, "Status": "⚠️ CAUTION"},
    {"Match": "Real Madrid vs Barcelona", "League": "La Liga", "Selection": "Real Madrid", "Odds": 2.25, "Status": "❌ REJECTED"},
    {"Match": "Bayern vs Dortmund", "League": "Bundesliga", "Selection": "Bayern", "Odds": 1.75, "Status": "✅ APPROVED"},
])
st.dataframe(all_legs, use_container_width=True)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    status_filter = st.multiselect("Status", ["Approved", "Caution", "Rejected"], default=["Approved"])
    league_filter = st.multiselect("League", ["Premier League", "La Liga", "Bundesliga", "Serie A"])
    
    st.header("System Status")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Backend: Connecting soon...")
