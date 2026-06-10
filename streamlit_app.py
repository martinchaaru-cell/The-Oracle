import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Match Oracle",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #3b82f6;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🎯 Match Oracle</p>', unsafe_allow_html=True)
st.caption("AI-powered football prediction platform")

# ========== MOCK DATA ==========
bankroll = 12450
peak = 13200
drawdown = (peak - bankroll) / peak

# ========== METRICS ROW ==========
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Bankroll",
        value=f"${bankroll:,}",
        delta=f"-{drawdown:.1%}" if drawdown > 0 else None,
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Today's Legs",
        value="47",
        delta="12 approved"
    )

with col3:
    st.metric(
        label="Total Staked",
        value="$847.50",
        delta="$2,150 potential"
    )

with col4:
    st.metric(
        label="System Health",
        value="Grade B",
        delta="58% accuracy"
    )

st.divider()

# ========== CHARTS ROW ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Legs by League")
    league_data = pd.DataFrame({
        "League": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Eredivisie"],
        "Count": [12, 10, 8, 8, 6, 3]
    })
    fig = px.bar(
        league_data, 
        x="League", 
        y="Count", 
        color="Count",
        color_continuous_scale="blues",
        title="Fixtures by Competition"
    )
    fig.update_layout(
        plot_bgcolor="#1e293b",
        paper_bgcolor="#1e293b",
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 Status Distribution")
    status_data = pd.DataFrame({
        "Status": ["Approved ✅", "Rejected ❌", "Caution ⚠️"],
        "Count": [12, 28, 7]
    })
    fig = px.pie(
        status_data, 
        values="Count", 
        names="Status",
        color="Status",
        color_discrete_map={
            "Approved ✅": "#10b981",
            "Rejected ❌": "#ef4444", 
            "Caution ⚠️": "#f59e0b"
        },
        title="Pipeline Results"
    )
    fig.update_layout(
        plot_bgcolor="#1e293b",
        paper_bgcolor="#1e293b",
        font_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ========== TOP PICKS ==========
st.subheader("🏆 Top Picks")

top_picks_data = {
    "Match": ["Arsenal vs Chelsea", "Bayern Munich vs Dortmund", "Inter Milan vs Juventus", "PSG vs Marseille"],
    "Selection": ["Arsenal", "Bayern Munich", "Inter Milan", "PSG"],
    "Odds": [2.10, 1.75, 2.05, 1.55],
    "Probability": ["62%", "58%", "55%", "68%"],
    "Edge": ["+8.1%", "+6.7%", "+4.2%", "+11.3%"],
    "Confidence": ["HIGH", "HIGH", "MEDIUM", "HIGH"]
}
top_picks_df = pd.DataFrame(top_picks_data)
st.dataframe(top_picks_df, use_container_width=True, hide_index=True)

st.divider()

# ========== ALL LEGS TABLE ==========
st.subheader("📋 All Legs Analyzed")

all_legs_data = {
    "Match": ["Arsenal vs Chelsea", "Man City vs Liverpool", "Real Madrid vs Barcelona", "Bayern vs Dortmund", "Inter vs Juventus", "PSG vs Marseille", "Ajax vs Feyenoord"],
    "League": ["Premier League", "Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Eredivisie"],
    "Kickoff": ["15:00", "17:30", "20:00", "15:00", "19:45", "16:00", "14:30"],
    "Selection": ["Arsenal", "Man City", "Real Madrid", "Bayern", "Inter", "PSG", "Ajax"],
    "Odds": [2.10, 1.95, 2.25, 1.75, 2.05, 1.55, 1.85],
    "Probability": ["62%", "54%", "48%", "58%", "55%", "68%", "57%"],
    "Edge": ["+8.1%", "+2.2%", "-1.7%", "+6.7%", "+4.2%", "+11.3%", "+5.1%"],
    "Status": ["✅ APPROVED", "⚠️ CAUTION", "❌ REJECTED", "✅ APPROVED", "✅ APPROVED", "✅ APPROVED", "✅ APPROVED"],
    "Confidence": ["HIGH", "MEDIUM", "LOW", "HIGH", "MEDIUM", "HIGH", "HIGH"]
}
all_legs_df = pd.DataFrame(all_legs_data)

# Display the dataframe without styling (simpler to avoid errors)
st.dataframe(all_legs_df, use_container_width=True, hide_index=True)

st.divider()

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("🔍 Filters")
    
    status_filter = st.multiselect(
        "Status",
        ["APPROVED", "CAUTION", "REJECTED"],
        default=["APPROVED"]
    )
    
    league_filter = st.multiselect(
        "League",
        ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "Eredivisie"],
        default=[]
    )
    
    st.divider()
    
    st.header("📊 Performance")
    
    # Performance metrics
    st.metric("Overall Accuracy", "58%", "+2%")
    st.metric("HIGH Confidence", "68%", "+5%")
    st.metric("MEDIUM Confidence", "52%", "-3%")
    st.metric("LOW Confidence", "48%", "0%")
    
    st.divider()
    
    st.header("💰 Bankroll")
    st.metric("Current", "$12,450", "-$750")
    st.metric("Peak", "$13,200", "")
    st.metric("Drawdown", "5.7%", "↓")
    
    st.divider()
    
    # Apply filters (simple version)
    if status_filter or league_filter:
        st.subheader("📊 Filtered Results")
        filtered_df = all_legs_df.copy()
        
        if status_filter:
            # Convert status values for filtering
            status_map = {
                "APPROVED": "✅ APPROVED",
                "CAUTION": "⚠️ CAUTION", 
                "REJECTED": "❌ REJECTED"
            }
            filter_values = [status_map[s] for s in status_filter]
            filtered_df = filtered_df[filtered_df["Status"].isin(filter_values)]
        
        if league_filter:
            filtered_df = filtered_df[filtered_df["League"].isin(league_filter)]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.info("No matches match the selected filters")
    
    st.divider()
    
    st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("🎯 Match Oracle v1.0")
    st.caption("Backend: Connecting soon...")

# ========== BANKROLL HISTORY CHART ==========
st.subheader("📉 Bankroll History")

bankroll_history = pd.DataFrame({
    "Date": ["Jun 1", "Jun 2", "Jun 3", "Jun 4", "Jun 5", "Jun 6", "Jun 7", "Jun 8"],
    "Bankroll": [10000, 10250, 10500, 10300, 10800, 11200, 11800, 12450],
    "Profit": [0, 250, 250, -200, 500, 400, 600, 650]
})

fig = px.line(
    bankroll_history,
    x="Date",
    y="Bankroll",
    title="Bankroll Progression",
    markers=True
)
fig.update_layout(
    plot_bgcolor="#1e293b",
    paper_bgcolor="#1e293b",
    font_color="white"
)
fig.update_traces(line_color="#3b82f6", marker_color="#3b82f6")
st.plotly_chart(fig, use_container_width=True)

# ========== FOOTER ==========
st.divider()
st.caption("⚠️ This is a demo with mock data. Connect your backend for live predictions.")
