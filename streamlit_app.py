# streamlit_app.py - PROPER LEG DATA FROM API
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Initialize session state
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "selected_leg_data" not in st.session_state:
    st.session_state.selected_leg_data = None
if "selected_leg_name" not in st.session_state:
    st.session_state.selected_leg_name = ""

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
API_HOST = "sports.highlightly.net"

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def fetch_match_leg_data(match_id):
    """Fetch complete leg data including odds from the match details endpoint"""
    url = f"https://sports.highlightly.net/football/matches/{match_id}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch leg data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching leg data: {str(e)}")
        return None

def fetch_matches_by_date(date_str):
    """Fetch matches for a specific date"""
    url = f"https://sports.highlightly.net/football/matches"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    params = {"date": date_str}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                if "response" in data:
                    return data["response"]
                elif "data" in data:
                    return data["data"]
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def extract_odds_from_leg_data(leg_data):
    """Extract REAL odds from the leg data response"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Check all possible odds locations in the response
    if isinstance(leg_data, dict):
        # Check for odds at root level
        if "odds" in leg_data:
            odds_list = leg_data["odds"]
            if isinstance(odds_list, list):
                for odd in odds_list:
                    if odd.get("market") == "Full Time Result" or odd.get("name") == "Match Odds":
                        outcomes = odd.get("outcomes", [])
                        for outcome in outcomes:
                            name = outcome.get("name", "").lower()
                            price = outcome.get("price", 0)
                            if price > 0:
                                if "home" in name:
                                    home_odds = price
                                elif "draw" in name:
                                    draw_odds = price
                                elif "away" in name:
                                    away_odds = price
        
        # Check for bookmakers
        if home_odds is None and "bookmakers" in leg_data:
            for bookmaker in leg_data["bookmakers"]:
                for market in bookmaker.get("markets", []):
                    if market.get("key") == "h2h":
                        for outcome in market.get("outcomes", []):
                            name = outcome.get("name", "").lower()
                            price = outcome.get("price", 0)
                            if price > 0:
                                if "home" in name:
                                    home_odds = price
                                elif "draw" in name:
                                    draw_odds = price
                                elif "away" in name:
                                    away_odds = price
                                if home_odds and draw_odds and away_odds:
                                    break
    
    return home_odds, draw_odds, away_odds

def display_leg_data(leg_data, match_name):
    """Display the complete leg data with real odds"""
    st.subheader(f"📊 LEG DATA: {match_name}")
    
    # Extract real odds from the leg data
    home_odds, draw_odds, away_odds = extract_odds_from_leg_data(leg_data)
    
    if home_odds and draw_odds and away_odds:
        st.success("✅ REAL ODDS SUCCESSFULLY FETCHED FROM API")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("HOME ODDS", f"{home_odds:.2f}")
        with col2:
            st.metric("DRAW ODDS", f"{draw_odds:.2f}")
        with col3:
            st.metric("AWAY ODDS", f"{away_odds:.2f}")
        
        # Calculate prediction with real odds
        if home_odds < away_odds:
            selection = match_name.split(" vs ")[0] if " vs " in match_name else "Home"
            odds = home_odds
        else:
            selection = match_name.split(" vs ")[1] if " vs " in match_name else "Away"
            odds = away_odds
        
        implied_prob = 1/odds
        edge = (implied_prob - 0.33) * 100
        
        st.subheader("🔮 PREDICTION")
        st.write(f"**Selection:** {selection}")
        st.write(f"**Odds:** {odds:.2f}")
        st.write(f"**Edge:** {edge:.1f}%")
        
        if edge > 8:
            st.success("✅ APPROVED - Strong value detected")
        elif edge > 3:
            st.warning("⚠️ CAUTION - Moderate value")
        else:
            st.error("❌ REJECTED - No value")
    
    else:
        st.warning("⚠️ No odds data found in the API response")
        st.info("The API returned data but no odds were available for this match")
    
    # Show the raw API response for transparency
    with st.expander("View Raw API Response (Leg Data)"):
        st.json(leg_data)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")
    
    if st.button("🚀 FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches from API..."):
            matches = fetch_matches_by_date(date_str)
            if matches and len(matches) > 0:
                st.session_state.all_matches = matches
                st.success(f"✅ Loaded {len(matches)} matches!")
            else:
                st.session_state.all_matches = []
                st.warning(f"No matches found for {date_str}")
            st.rerun()
    
    if st.session_state.all_matches:
        st.info(f"📊 {len(st.session_state.all_matches)} matches available")
        st.caption("Click 'View Leg Data' on any match to fetch real odds")

# Main content
if st.session_state.all_matches:
    matches = st.session_state.all_matches
    
    # Apply league filter
    if league_filter:
        filtered_matches = []
        for match in matches:
            league_name = match.get("league", {}).get("name", "")
            if league_filter.lower() in league_name.lower():
                filtered_matches.append(match)
        matches = filtered_matches
    
    st.subheader(f"📋 AVAILABLE MATCHES: {len(matches)}")
    
    for idx, match in enumerate(matches):
        home_name = match.get("homeTeam", {}).get("name", "Home")
        away_name = match.get("awayTeam", {}).get("name", "Away")
        league_name = match.get("league", {}).get("name", "Unknown")
        match_id = match.get("id")
        match_name = f"{home_name} vs {away_name}"
        
        with st.expander(f"{idx+1}. {match_name} - {league_name}"):
            st.write(f"**Match ID:** {match_id}")
            st.write(f"**Status:** {match.get('status', {}).get('long', 'Scheduled')}")
            
            # This button fetches the ACTUAL leg data with odds
            button_key = f"fetch_leg_{match_id}_{idx}"
            if st.button("🎯 VIEW LEG DATA (FETCH REAL ODDS)", key=button_key, use_container_width=True):
                with st.spinner(f"Fetching leg data for {match_name}..."):
                    leg_data = fetch_match_leg_data(match_id)
                    if leg_data:
                        st.session_state.selected_leg_data = leg_data
                        st.session_state.selected_leg_name = match_name
                        st.success(f"✅ Leg data fetched successfully!")
                    else:
                        st.error("Failed to fetch leg data from API")
                    st.rerun()
    
    # Display the selected leg data
    if st.session_state.selected_leg_data:
        st.divider()
        display_leg_data(st.session_state.selected_leg_data, st.session_state.selected_leg_name)
        
        if st.button("❌ Close Leg Data"):
            st.session_state.selected_leg_data = None
            st.session_state.selected_leg_name = ""
            st.rerun()

else:
    st.info("👈 Click 'FETCH MATCHES' to load available matches")
    
    with st.expander("📖 How it works"):
        st.markdown("""
        1. **FETCH MATCHES** - Gets list of matches for selected date
        2. **VIEW LEG DATA** - Click this button on any match to fetch:
           - Real odds from bookmakers
           - Complete match statistics
           - Head-to-head data
           - Player information
           - And more
        
        The leg data is fetched directly from the Highlightly API endpoint:
        `https://sports.highlightly.net/football/matches/{match_id}`
        """)

st.divider()
st.caption(f"Match Oracle | Fetches real leg data from Highlightly API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
