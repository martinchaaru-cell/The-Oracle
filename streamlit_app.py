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

# ========== API KEY CONFIGURATION ==========
def get_api_keys():
    """Get API keys from secrets or session state"""
    try:
        football_key = st.secrets.get("APIFOOTBALL_KEY", "")
        odds_key = st.secrets.get("ODDS_API_KEY", "")
        backend_url = st.secrets.get("BACKEND_URL", "")
        if football_key:
            return football_key, odds_key, backend_url
    except:
        pass
    
    football_key = st.session_state.get("football_key", "")
    odds_key = st.session_state.get("odds_key", "")
    backend_url = st.session_state.get("backend_url", "https://oracle-backend-1-vryo.onrender.com")
    
    return football_key, odds_key, backend_url

# ========== MOCK DATA ==========
# Today's fixtures sorted by time (earliest first)
MOCK_FIXTURES = [
    {"id": 1, "home": "Ajax", "away": "Feyenoord", "league": "Eredivisie", "time": "12:30", "odds": 1.85, "status": "NS"},
    {"id": 2, "home": "Arsenal", "away": "Chelsea", "league": "Premier League", "time": "15:00", "odds": 2.10, "status": "NS"},
    {"id": 3, "home": "Bayern Munich", "away": "Dortmund", "league": "Bundesliga", "time": "15:00", "odds": 1.75, "status": "NS"},
    {"id": 4, "home": "PSG", "away": "Marseille", "league": "Ligue 1", "time": "16:00", "odds": 1.55, "status": "NS"},
    {"id": 5, "home": "Manchester City", "away": "Liverpool", "league": "Premier League", "time": "17:30", "odds": 1.95, "status": "NS"},
    {"id": 6, "home": "Inter Milan", "away": "Juventus", "league": "Serie A", "time": "19:45", "odds": 2.05, "status": "NS"},
    {"id": 7, "home": "Real Madrid", "away": "Barcelona", "league": "La Liga", "time": "20:00", "odds": 2.25, "status": "NS"},
]

# Live matches
MOCK_LIVE = [
    {"id": 8, "home": "AC Milan", "away": "Roma", "league": "Serie A", "time": "LIVE 67'", "home_score": 2, "away_score": 1, "status": "LIVE"},
]

# League stats
LEAGUE_STATS = [
    {"league": "Premier League", "count": 12, "accuracy": 62, "roi": 15.2},
    {"league": "La Liga", "count": 10, "accuracy": 58, "roi": 9.8},
    {"league": "Bundesliga", "count": 8, "accuracy": 59, "roi": 11.2},
    {"league": "Serie A", "count": 8, "accuracy": 51, "roi": 4.5},
    {"league": "Ligue 1", "count": 6, "accuracy": 61, "roi": 13.4},
]

# Bankroll history
BANKROLL_HISTORY = [
    {"date": "Jun 1", "bankroll": 10000}, {"date": "Jun 2", "bankroll": 10250},
    {"date": "Jun 3", "bankroll": 10500}, {"date": "Jun 4", "bankroll": 10300},
    {"date": "Jun 5", "bankroll": 10800}, {"date": "Jun 6", "bankroll": 11200},
    {"date": "Jun 7", "bankroll": 11800}, {"date": "Jun 8", "bankroll": 12450},
]

# Top picks
TOP_PICKS = [
    {"match": "Arsenal vs Chelsea", "selection": "Arsenal", "odds": 2.10, "prob": 62, "edge": 8.1},
    {"match": "Bayern vs Dortmund", "selection": "Bayern", "odds": 1.75, "prob": 58, "edge": 6.7},
    {"match": "Inter vs Juventus", "selection": "Inter", "odds": 2.05, "prob": 55, "edge": 4.2},
]

# Parlays
PARLAYS = {
    "safe": {"legs": ["Arsenal (2.10)", "Bayern (1.75)"], "odds": 3.68, "prob": 36},
    "balanced": {"legs": ["Arsenal (2.10)", "Bayern (1.75)", "PSG (1.55)"], "odds": 5.70, "prob": 22},
    "aggressive": {"legs": ["Arsenal (2.10)", "Bayern (1.75)", "Inter (2.05)", "Ajax (1.85)"], "odds": 13.95, "prob": 11},
}

# Countries data
COUNTRIES = [
    {"flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "name": "England", "leagues": ["Premier League", "Championship", "League One"]},
    {"flag": "🇪🇸", "name": "Spain", "leagues": ["La Liga", "Segunda Division"]},
    {"flag": "🇩🇪", "name": "Germany", "leagues": ["Bundesliga", "2. Bundesliga"]},
    {"flag": "🇮🇹", "name": "Italy", "leagues": ["Serie A", "Serie B"]},
    {"flag": "🇫🇷", "name": "France", "leagues": ["Ligue 1", "Ligue 2"]},
    {"flag": "🇳🇱", "name": "Netherlands", "leagues": ["Eredivisie"]},
    {"flag": "🇵🇹", "name": "Portugal", "leagues": ["Primeira Liga"]},
    {"flag": "🇧🇷", "name": "Brazil", "leagues": ["Serie A"]},
    {"flag": "🇦🇷", "name": "Argentina", "leagues": ["Primera Division"]},
    {"flag": "🇯🇵", "name": "Japan", "leagues": ["J1 League"]},
]

# ========== HELPER FUNCTIONS ==========
def group_fixtures_by_league(fixtures):
    """Group fixtures by league and sort by time"""
    grouped = {}
    for f in fixtures:
        league = f['league']
        if league not in grouped:
            grouped[league] = []
        grouped[league].append(f)
    for league in grouped:
        grouped[league].sort(key=lambda x: x['time'])
    return grouped

# ========== SESSION STATE ==========
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_fixture" not in st.session_state:
    st.session_state.selected_fixture = None

# ========== PAGE ROUTING ==========
def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def go_back():
    navigate_to("dashboard")

# ========== FORENSIC REPORT PAGE ==========
def show_forensic_report(fixture):
    st.title(f"🔬 {fixture['home']} vs {fixture['away']}")
    st.caption(f"{fixture['league']} | Kickoff: {fixture['time']}")
    
    if st.button("← Back to Fixtures"):
        go_back()
    
    st.divider()
    
    tab1, tab2 = st.tabs(["📊 Match Data", "🔬 Forensic Report"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Home Form", "W W D W L", "+2")
            st.metric("Home Goals/Game", "2.1", "↑")
            st.metric("Home xG", "1.8", "↓")
        with col2:
            st.metric("Away Form", "L L D L W", "-3")
            st.metric("Away Goals/Game", "1.2", "↓")
            st.metric("Away xG", "1.4", "↑")
    
    with tab2:
        st.markdown("### M4: Pre-filter (6/8 passed)")
        st.progress(0.75)
        
        st.markdown("### M5: Forensic Failures")
        st.metric("Total Failure Score", "2.5 / 4.5", "PASS")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### M6: Personnel")
            st.metric(f"{fixture['home']}", "82/100", "Healthy")
            st.metric(f"{fixture['away']}", "65/100", "1 injury")
        with col2:
            st.markdown("### M7: AI Consensus")
            st.write("DeepSeek: ✅ APPROVE")
            st.write("Claude: ✅ APPROVE")
            st.write("Gemini: ⚠️ CAUTION")
            st.write("GPT: ✅ APPROVE")
        
        st.markdown("### M8: Dual Pattern")
        st.info("Risk Level: LOW | Underdog Threat: NONE")
        
        st.markdown("### M9: Underdog Scanner")
        st.metric("Underdog Edge", "-2.1%", "No value")
        
        st.markdown("### M10: Tally Matrix")
        st.success("Bilateral Prediction: HOME (HIGH confidence)")
        
        st.markdown("### M26: Match Context")
        st.write("🏆 London Derby | Importance: 72%")
        
        st.markdown("### M27: H2H Analysis")
        st.write("H2H Score: 78/100 (FAV_EDGE)")
        st.write("Games: 48 | Fav 29 | Draw 11 | Und 8")
        
        st.divider()
        st.success("✅ FINAL VERDICT: APPROVED (HIGH confidence)")

# ========== DASHBOARD PAGE ==========
def show_dashboard():
    st.title("🎯 MATCH ORACLE")
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y')} | Live football intelligence")
    
    st.divider()
    
    # Live matches section
    if MOCK_LIVE:
        st.subheader("🔴 LIVE NOW")
        for live in MOCK_LIVE:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{live['home']} {live['home_score']} - {live['away_score']} {live['away']}**")
                st.caption(live['league'])
            with col2:
                st.markdown(f"**{live['time']}**")
            with col3:
                st.markdown("🔴 LIVE")
            st.divider()
    
    # Group fixtures by league
    grouped_fixtures = group_fixtures_by_league(MOCK_FIXTURES)
    
    for league, fixtures in grouped_fixtures.items():
        st.subheader(f"🏆 {league}")
        
        for fixture in fixtures:
            col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 1, 0.8])
            
            with col1:
                st.markdown(f"**{fixture['home']} vs {fixture['away']}**")
            
            with col2:
                st.markdown(f"**{fixture['time']}**")
                st.caption("Kickoff")
            
            with col3:
                st.markdown(f"**{fixture['odds']:.2f}**")
                st.caption("Odds")
            
            with col4:
                # Calculate edge
                edge = (1/fixture['odds'] - 0.45) * 100
                edge_color = "🟢" if edge > 0 else "🔴"
                st.markdown(f"{edge_color} **{abs(edge):.1f}%**")
                st.caption("Edge")
            
            with col5:
                if st.button("🔍", key=f"btn_{fixture['id']}", help="View forensic report"):
                    st.session_state.selected_fixture = fixture
                    navigate_to("forensic")
            
            st.divider()
    
    if not MOCK_FIXTURES and not MOCK_LIVE:
        st.info("No fixtures scheduled for today.")

# ========== PERFORMANCE PAGE ==========
def show_performance():
    st.title("📈 Performance Metrics")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Calibration Grade", "B", "Good")
    with col2:
        st.metric("Brier Score", "0.187", "0=perfect")
    with col3:
        st.metric("ECE", "0.094", "0=perfect")
    
    st.divider()
    
    st.subheader("Accuracy by Confidence Level")
    acc_data = pd.DataFrame({
        "Confidence": ["HIGH", "MEDIUM", "LOW"],
        "Accuracy": [68, 52, 48],
        "Bets": [145, 89, 67]
    })
    fig = px.bar(acc_data, x="Confidence", y="Accuracy", color="Confidence", text="Accuracy")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("Performance by League")
    league_df = pd.DataFrame(LEAGUE_STATS)
    st.dataframe(league_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.subheader("ROI Trend")
    roi_data = pd.DataFrame([
        {"month": "Jan", "roi": 2.1}, {"month": "Feb", "roi": 3.5},
        {"month": "Mar", "roi": 4.2}, {"month": "Apr", "roi": 5.8},
        {"month": "May", "roi": 7.1}, {"month": "Jun", "roi": 12.4},
    ])
    fig = px.line(roi_data, x="month", y="roi", markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ========== BANKROLL PAGE ==========
def show_bankroll():
    st.title("💰 Bankroll Manager")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Bankroll", "$12,450", "-$750")
    with col2:
        st.metric("Peak Bankroll", "$13,200", "")
    with col3:
        st.metric("Drawdown", "5.7%", "↓")
    with col4:
        st.metric("Stake Multiplier", "0.85x", "Reduced")
    
    st.divider()
    
    st.subheader("Bankroll History")
    history_df = pd.DataFrame(BANKROLL_HISTORY)
    fig = px.line(history_df, x="date", y="bankroll", markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("Active Stakes")
    stakes_data = pd.DataFrame([
        {"Match": "Arsenal vs Chelsea", "Stake": "$127.50", "Odds": 2.10, "Potential": "$267.75"},
        {"Match": "Bayern vs Dortmund", "Stake": "$150.00", "Odds": 1.75, "Potential": "$262.50"},
        {"Match": "Inter vs Juventus", "Stake": "$100.00", "Odds": 2.05, "Potential": "$205.00"},
    ])
    st.dataframe(stakes_data, use_container_width=True, hide_index=True)

# ========== TOP PICKS PAGE ==========
def show_top_picks():
    st.title("🏆 Top Picks")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    for i, pick in enumerate(TOP_PICKS, 1):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.markdown(f"**#{i} {pick['match']}**")
        with col2:
            st.write(f"{pick['selection']} @ {pick['odds']:.2f}")
        with col3:
            st.write(f"{pick['prob']}% prob")
        with col4:
            st.write(f"+{pick['edge']}% edge")
        st.divider()
    
    st.info("Top picks are based on highest model probability and edge.")

# ========== PARLAYS PAGE ==========
def show_parlays():
    st.title("🔗 Parlay Builder")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### 🟢 Ultra Safe Parlay")
    st.markdown(f"**{' + '.join(PARLAYS['safe']['legs'])} = {PARLAYS['safe']['odds']:.2f}x**")
    st.caption(f"Combined Probability: {PARLAYS['safe']['prob']}% | Stake: 3% of bankroll")
    
    st.divider()
    
    st.markdown("### 🟡 Balanced Parlay")
    st.markdown(f"**{' + '.join(PARLAYS['balanced']['legs'])} = {PARLAYS['balanced']['odds']:.2f}x**")
    st.caption(f"Combined Probability: {PARLAYS['balanced']['prob']}% | Stake: 2% of bankroll")
    
    st.divider()
    
    st.markdown("### 🔴 Aggressive Parlay")
    st.markdown(f"**{' + '.join(PARLAYS['aggressive']['legs'])} = {PARLAYS['aggressive']['odds']:.2f}x**")
    st.caption(f"Combined Probability: {PARLAYS['aggressive']['prob']}% | Stake: 1% of bankroll")

# ========== ALL LEGS PAGE ==========
def show_all_legs():
    st.title("📋 All Legs Analyzed")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    search = st.text_input("🔍 Search", placeholder="Team or league...")
    
    fixtures = MOCK_FIXTURES
    if search:
        s = search.lower()
        fixtures = [f for f in fixtures if s in f['home'].lower() or s in f['away'].lower() or s in f['league'].lower()]
    
    st.caption(f"Showing {len(fixtures)} legs")
    
    for fixture in fixtures:
        col1, col2, col3, col4 = st.columns([2.5, 1.5, 1, 1])
        with col1:
            st.write(f"**{fixture['home']} vs {fixture['away']}**")
        with col2:
            st.write(fixture['league'])
        with col3:
            st.write(fixture['time'])
        with col4:
            if st.button("🔍 View", key=f"view_{fixture['id']}"):
                st.session_state.selected_fixture = fixture
                navigate_to("forensic")
        st.divider()

# ========== COUNTRIES PAGE ==========
def show_countries():
    st.title("🌍 Country Explorer")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    for country in COUNTRIES:
        with st.expander(f"{country['flag']} {country['name']}"):
            for league in country['leagues']:
                st.write(f"• {league}")

# ========== CALENDAR PAGE ==========
def show_calendar():
    st.title("📅 Oracle Calendar")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    date = st.date_input("Select Date", datetime.now().date())
    
    if st.button("🔍 Scan Selected Date"):
        with st.spinner("Scanning fixtures..."):
            import time
            time.sleep(1)
            st.success(f"Scan complete for {date}")
            st.info(f"Found 12 fixtures on {date}")
    
    st.markdown("### 📊 Recent Activity")
    for fixture in MOCK_FIXTURES[:5]:
        st.write(f"📅 {datetime.now().strftime('%b %d')} | {fixture['home']} vs {fixture['away']} - {fixture['league']}")

# ========== SETTINGS PAGE ==========
def show_settings():
    st.title("⚙️ Settings")
    
    if st.button("← Back"):
        navigate_to("dashboard")
    
    st.divider()
    
    st.markdown("### Data Source")
    st.info("📊 Currently using DEMO DATA")
    
    st.markdown("### API Configuration")
    api_key = st.text_input("API-Football Key", type="password", placeholder="Enter your API key")
    if api_key:
        st.success("API key saved (demo mode)")
    
    st.markdown("### Thresholds")
    st.slider("Home Win Threshold", 0.50, 0.70, 0.57, 0.01)
    st.slider("Minimum Edge", 0.00, 0.15, 0.04, 0.01)
    
    st.markdown("### Timezone")
    st.info("📍 GMT+3 (Nairobi)")
    
    if st.button("Save Settings"):
        st.success("Settings saved (demo mode)")

# ========== MAIN ==========
def main():
    # Get API keys (for future use)
    football_key, odds_key, backend_url = get_api_keys()
    
    # Sidebar - Main Menu
    with st.sidebar:
        st.markdown("### 🎯 MATCH ORACLE")
        st.markdown("---")
        
        # API Key section
        with st.expander("🔑 API Keys", expanded=False):
            st.markdown("**Get free keys from:**")
            st.markdown("- [API-Football](https://api-football.com/)")
            st.markdown("- [The Odds API](https://the-odds-api.com/)")
            
            key_input = st.text_input(
                "API-Football Key", 
                type="password",
                placeholder="Enter your key",
                key="api_key_input"
            )
            if key_input:
                st.session_state.football_key = key_input
                st.success("✅ Key saved")
        
        # Show key status
        if football_key:
            st.success(f"🔑 API Key: {football_key[:6]}...")
        else:
            st.warning("⚠️ No API Key")
        
        st.markdown("---")
        
        # Menu Items
        st.markdown("**📋 TODAY**")
        if st.button("🏠 Today's Fixtures", use_container_width=True):
            navigate_to("dashboard")
        
        st.markdown("---")
        st.markdown("**📊 ANALYTICS**")
        if st.button("📈 Performance", use_container_width=True):
            navigate_to("performance")
        if st.button("💰 Bankroll", use_container_width=True):
            navigate_to("bankroll")
        if st.button("🏆 Top Picks", use_container_width=True):
            navigate_to("top_picks")
        if st.button("🔗 Parlays", use_container_width=True):
            navigate_to("parlays")
        
        st.markdown("---")
        st.markdown("**🔍 DATA**")
        if st.button("📋 All Legs", use_container_width=True):
            navigate_to("all_legs")
        if st.button("🌍 Countries", use_container_width=True):
            navigate_to("countries")
        if st.button("📅 Calendar", use_container_width=True):
            navigate_to("calendar")
        if st.button("⚙️ Settings", use_container_width=True):
            navigate_to("settings")
        
        st.markdown("---")
        
        # Status footer
        st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')} GMT+3")
        if football_key:
            st.caption("🔑 API: Configured")
        else:
            st.caption("📡 DEMO MODE")
    
    # Page routing
    page = st.session_state.page
    
    if page == "dashboard":
        show_dashboard()
    elif page == "forensic":
        if st.session_state.selected_fixture:
            show_forensic_report(st.session_state.selected_fixture)
        else:
            navigate_to("dashboard")
    elif page == "performance":
        show_performance()
    elif page == "bankroll":
        show_bankroll()
    elif page == "top_picks":
        show_top_picks()
    elif page == "parlays":
        show_parlays()
    elif page == "all_legs":
        show_all_legs()
    elif page == "countries":
        show_countries()
    elif page == "calendar":
        show_calendar()
    elif page == "settings":
        show_settings()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
