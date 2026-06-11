import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import os

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Match Oracle",
    page_icon="🎯",
    layout="wide"
)

# ========== SIMPLE MOCK DATA (Works without any APIs) ==========
MOCK_FIXTURES = [
    {"home": "Arsenal", "away": "Chelsea", "league": "Premier League", "time": "15:00", "odds": 2.10},
    {"home": "Manchester City", "away": "Liverpool", "league": "Premier League", "time": "17:30", "odds": 1.95},
    {"home": "Bayern Munich", "away": "Borussia Dortmund", "league": "Bundesliga", "time": "15:00", "odds": 1.75},
    {"home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "time": "20:00", "odds": 2.25},
    {"home": "Inter Milan", "away": "Juventus", "league": "Serie A", "time": "19:45", "odds": 2.05},
    {"home": "PSG", "away": "Marseille", "league": "Ligue 1", "time": "16:00", "odds": 1.55},
]

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# ========== PAGE ROUTING ==========
def navigate_to(page):
    st.session_state.page = page
    st.rerun()

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.title("🎯 MATCH ORACLE")
    st.caption("AI-powered football prediction platform")
    
    st.divider()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Bankroll", "$12,450", "-5.7%")
    with col2:
        st.metric("Today's Fixtures", "47", "+12")
    with col3:
        st.metric("Total Staked", "$847", "+$2,150 potential")
    with col4:
        st.metric("System Health", "Grade B", "58% accuracy")
    
    st.divider()
    
    # Top Picks
    st.subheader("🏆 Top Picks")
    
    top_picks = [
        {"match": "Arsenal vs Chelsea", "selection": "Arsenal", "odds": 2.10, "edge": "+8.1%"},
        {"match": "Bayern Munich vs Dortmund", "selection": "Bayern Munich", "odds": 1.75, "edge": "+6.7%"},
        {"match": "Inter Milan vs Juventus", "selection": "Inter Milan", "odds": 2.05, "edge": "+4.2%"},
    ]
    
    for pick in top_picks:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{pick['match']}**")
            with col2:
                st.write(f"{pick['selection']} @ {pick['odds']}")
            with col3:
                st.write(pick['edge'])
            st.divider()
    
    # Legs by League Chart
    st.subheader("📊 Legs by League")
    
    league_data = pd.DataFrame({
        "League": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
        "Count": [12, 10, 8, 8, 6]
    })
    
    fig = px.bar(league_data, x="League", y="Count", color="Count", text="Count")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Today's Fixtures
    st.subheader("📋 Today's Fixtures")
    
    for fixture in MOCK_FIXTURES:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{fixture['home']} vs {fixture['away']}**")
            with col2:
                st.write(fixture['league'])
            with col3:
                st.write(fixture['time'])
            st.divider()
    
    # Bankroll Chart
    st.subheader("📉 Bankroll History")
    
    history_data = pd.DataFrame({
        "Date": ["Jun 1", "Jun 2", "Jun 3", "Jun 4", "Jun 5", "Jun 6", "Jun 7", "Jun 8"],
        "Bankroll": [10000, 10250, 10500, 10300, 10800, 11200, 11800, 12450]
    })
    
    fig = px.line(history_data, x="Date", y="Bankroll", markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ========== ALL LEGS PAGE ==========
def show_all_legs():
    st.title("📋 All Fixtures")
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    search = st.text_input("🔍 Search", placeholder="Team or league...")
    
    fixtures = MOCK_FIXTURES
    if search:
        s = search.lower()
        fixtures = [f for f in fixtures if s in f['home'].lower() or s in f['away'].lower() or s in f['league'].lower()]
    
    st.write(f"Showing {len(fixtures)} fixtures")
    
    for fixture in fixtures:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{fixture['home']} vs {fixture['away']}**")
            with col2:
                st.write(fixture['league'])
            with col3:
                st.write(fixture['time'])
            st.divider()

# ========== PARLAYS PAGE ==========
def show_parlays():
    st.title("🔗 Parlays & ACCA Slips")
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### 🟢 Safe Parlay (2 legs)")
    st.markdown("**Arsenal (2.10) + Bayern Munich (1.75) = 3.68x**")
    st.caption("Combined Probability: 36% | Risk: SAFE")
    
    st.divider()
    
    st.markdown("### 🟡 Balanced Parlay (3 legs)")
    st.markdown("**Arsenal (2.10) + Bayern (1.75) + PSG (1.55) = 5.70x**")
    st.caption("Combined Probability: 22% | Risk: BALANCED")
    
    st.divider()
    
    st.markdown("### 🔴 Aggressive Parlay (4 legs)")
    st.markdown("**Arsenal (2.10) + Bayern (1.75) + Inter (2.05) + Ajax (1.85) = 13.95x**")
    st.caption("Combined Probability: 11% | Risk: AGGRESSIVE")

# ========== CALENDAR PAGE ==========
def show_calendar():
    st.title("📅 Oracle Calendar")
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    date = st.date_input("Select Date", datetime.now().date())
    
    if st.button("🔍 Scan Selected Date"):
        st.success(f"Scan complete for {date}")
    
    st.markdown("### 📊 Upcoming Fixtures")
    for fixture in MOCK_FIXTURES[:5]:
        st.write(f"**{fixture['home']} vs {fixture['away']}** - {fixture['league']} - {fixture['time']}")

# ========== SETTINGS PAGE ==========
def show_settings():
    st.title("⚙️ Settings")
    
    if st.button("← Back to Dashboard"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### Data Source")
    st.info("📊 Currently using DEMO DATA")
    st.caption("When backend is ready, this will automatically switch to LIVE DATA.")
    
    st.markdown("### Timezone")
    st.info("📍 GMT+3 (Nairobi)")

# ========== SIDEBAR ==========
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
    if st.button("⚙️ Settings", use_container_width=True):
        navigate_to("settings")
    
    st.divider()
    st.caption("Match Oracle v3.0")
    st.caption("📡 Source: DEMO DATA")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# ========== MAIN ==========
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
