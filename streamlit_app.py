# streamlit_app.py - Complete Working Version
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Match Oracle", page_icon="🔮", layout="wide")

# ============================================================
# CONFIGURATION
# ============================================================

HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
HIGHLIGHTLY_URL = "https://sports.highlightly.net"

# ============================================================
# FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)
def fetch_leagues() -> dict:
    """Fetch all leagues from Highlightly"""
    if not HIGHLIGHTLY_KEY:
        return {}
    
    url = f"{HIGHLIGHTLY_URL}/football/leagues?limit=200"
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            leagues = data.get("data", []) if isinstance(data, dict) else data
            
            # Process leagues
            league_dict = {}
            for league in leagues:
                league_id = league.get("id")
                league_name = league.get("name", "")
                country = league.get("country", {}).get("name", "Unknown")
                
                if league_id and league_name:
                    league_dict[league_id] = {
                        "name": league_name,
                        "country": country,
                        "id": league_id
                    }
            return league_dict
    except Exception as e:
        st.error(f"Error fetching leagues: {e}")
    
    # Fallback leagues
    return {
        39: {"name": "Premier League", "country": "England", "id": 39},
        140: {"name": "La Liga", "country": "Spain", "id": 140},
        78: {"name": "Bundesliga", "country": "Germany", "id": 78},
        135: {"name": "Serie A", "country": "Italy", "id": 135},
        61: {"name": "Ligue 1", "country": "France", "id": 61},
    }


@st.cache_data(ttl=60)
def fetch_matches(date: str, league_id: int) -> list:
    """Fetch matches for a specific date and league"""
    if not HIGHLIGHTLY_KEY:
        return []
    
    url = f"{HIGHLIGHTLY_URL}/football/matches"
    params = {
        "date": date,
        "leagueId": league_id,
        "limit": 50
    }
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", []) if isinstance(data, dict) else data
            return matches
        else:
            st.warning(f"API returned {response.status_code} for league {league_id}")
            return []
    except Exception as e:
        st.error(f"Error fetching matches: {e}")
        return []


def extract_odds(match: dict) -> tuple:
    """Extract odds from match data"""
    home_odds = 2.00
    draw_odds = 3.25
    away_odds = 3.50
    
    bookmakers = match.get("bookmakers", [])
    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []):
            if market.get("key") == "h2h":
                for outcome in market.get("outcomes", []):
                    name = outcome.get("name", "").lower()
                    price = outcome.get("price", 0)
                    if name == "home" and price > 0:
                        home_odds = price
                    elif name == "draw" and price > 0:
                        draw_odds = price
                    elif name == "away" and price > 0:
                        away_odds = price
                break
    return home_odds, draw_odds, away_odds


def display_match_card(match: dict):
    """Display a single match card"""
    home = match.get("homeTeam", {}).get("name", "?")
    away = match.get("awayTeam", {}).get("name", "?")
    league = match.get("league", {}).get("name", "?")
    status = match.get("state", {}).get("description", "Scheduled")
    score = match.get("state", {}).get("score", {}).get("current", "vs")
    
    # Extract date/time
    date_str = match.get("date", "")
    time_str = ""
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M")
        except:
            time_str = "TBD"
    
    home_odds, draw_odds, away_odds = extract_odds(match)
    
    # Create expandable card
    with st.expander(f"⚽ {home} vs {away} - {league}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**🏠 {home}**")
            st.markdown(f"Odds: `{home_odds}`")
            if home_odds < away_odds:
                st.markdown("⭐ **Favorite**")
        
        with col2:
            st.markdown(f"**🤝 Draw**")
            st.markdown(f"Odds: `{draw_odds}`")
            st.markdown(f"Status: {status}")
        
        with col3:
            st.markdown(f"**✈️ {away}**")
            st.markdown(f"Odds: `{away_odds}`")
            if away_odds < home_odds:
                st.markdown("⭐ **Favorite**")
        
        st.divider()
        
        # CSV format for backend processing
        csv_line = f"{home},{away},{home if home_odds < away_odds else away},{home_odds},{draw_odds},{away_odds},{league}"
        st.code(f"📋 CSV: {csv_line}", language="csv")


# ============================================================
# MAIN UI
# ============================================================

st.title("🔮 Match Oracle - Football Intelligence")

# Check API key
if not HIGHLIGHTLY_KEY:
    st.error("❌ HIGHLIGHTLY_API_KEY not found in secrets!")
    st.info("Please add your Highlightly API key to Streamlit secrets.")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Date picker
    match_date = st.date_input("📅 Match Date", datetime.now())
    date_str = match_date.strftime("%Y-%m-%d")
    
    st.divider()
    
    # League selection
    st.subheader("🏆 Select Leagues")
    
    with st.spinner("Loading leagues..."):
        leagues = fetch_leagues()
    
    selected_leagues = []
    
    # Group leagues by country
    leagues_by_country = {}
    for league_id, league_info in leagues.items():
        country = league_info.get("country", "Other")
        if country not in leagues_by_country:
            leagues_by_country[country] = []
        leagues_by_country[country].append(league_info)
    
    # Display leagues grouped by country
    for country in sorted(leagues_by_country.keys()):
        with st.expander(f"🌍 {country}"):
            for league in leagues_by_country[country]:
                if st.checkbox(league["name"], key=f"league_{league['id']}"):
                    selected_leagues.append(league["id"])
    
    st.divider()
    
    # Fetch button
    if st.button("🔍 Fetch Matches", type="primary", use_container_width=True):
        if not selected_leagues:
            st.warning("Please select at least one league")
        else:
            st.session_state.fetch_triggered = True
            st.rerun()


# Main content area
if st.session_state.get("fetch_triggered", False):
    with st.spinner("Fetching matches from Highlightly..."):
        all_matches = []
        
        for league_id in selected_leagues:
            league_name = leagues.get(league_id, {}).get("name", str(league_id))
            matches = fetch_matches(date_str, league_id)
            
            if matches:
                all_matches.extend(matches)
                st.success(f"✅ {league_name}: {len(matches)} matches")
            else:
                st.info(f"📭 {league_name}: No matches found on {date_str}")
        
        st.session_state.matches = all_matches
        st.session_state.fetch_triggered = False
        
        if all_matches:
            st.balloons()
        st.rerun()


# Display matches
if st.session_state.get("matches"):
    matches = st.session_state.matches
    st.subheader(f"📋 Matches Found ({len(matches)})")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        leagues_list = sorted(set(m.get("league", {}).get("name", "Unknown") for m in matches))
        selected_league_filter = st.multiselect("Filter by League", leagues_list, default=leagues_list)
    
    with col2:
        status_list = sorted(set(m.get("state", {}).get("description", "Unknown") for m in matches))
        selected_status_filter = st.multiselect("Filter by Status", status_list, default=status_list)
    
    # Filter matches
    filtered = [m for m in matches 
                if m.get("league", {}).get("name", "Unknown") in selected_league_filter
                and m.get("state", {}).get("description", "Unknown") in selected_status_filter]
    
    if not filtered:
        st.info("No matches match the selected filters")
    else:
        st.caption(f"Showing {len(filtered)} of {len(matches)} matches")
        
        # Group by league for better display
        matches_by_league = {}
        for match in filtered:
            league = match.get("league", {}).get("name", "Unknown")
            if league not in matches_by_league:
                matches_by_league[league] = []
            matches_by_league[league].append(match)
        
        for league, league_matches in matches_by_league.items():
            st.markdown(f"### 🏆 {league}")
            for match in league_matches:
                display_match_card(match)
else:
    st.info("👈 Select leagues and click 'Fetch Matches' to see today's fixtures")


# Footer
st.divider()
st.caption(f"🔮 Match Oracle | Data from Highlightly API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
