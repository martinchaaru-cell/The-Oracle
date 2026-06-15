# streamlit_app.py - DISPLAYS ALL LEG DATA (EXCLUDING ODDS)
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
    """Fetch complete leg data (excluding odds on free tier)"""
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
            return None
    except Exception as e:
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
        return []

def display_leg_data(leg_data, match_name):
    """Display all leg data excluding odds (since free tier has no odds)"""
    st.subheader(f"📊 MATCH LEG DATA: {match_name}")
    
    # Handle different response structures
    if isinstance(leg_data, dict):
        # If the response has a 'response' wrapper
        if "response" in leg_data:
            leg_data = leg_data["response"]
        
        # Display basic match info
        st.markdown("### 🏟️ MATCH INFORMATION")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**HOME TEAM**")
            home_team = leg_data.get("homeTeam", {})
            st.write(f"Name: {home_team.get('name', 'N/A')}")
            st.write(f"ID: {home_team.get('id', 'N/A')}")
            if home_team.get('logo'):
                st.image(home_team.get('logo'), width=50)
        
        with col2:
            st.markdown("**AWAY TEAM**")
            away_team = leg_data.get("awayTeam", {})
            st.write(f"Name: {away_team.get('name', 'N/A')}")
            st.write(f"ID: {away_team.get('id', 'N/A')}")
            if away_team.get('logo'):
                st.image(away_team.get('logo'), width=50)
        
        # League information
        st.markdown("### 🏆 COMPETITION")
        league = leg_data.get("league", {})
        st.write(f"Name: {league.get('name', 'N/A')}")
        st.write(f"Country: {league.get('country', 'N/A')}")
        st.write(f"Season: {leg_data.get('season', {}).get('name', 'N/A')}")
        st.write(f"Round: {leg_data.get('round', {}).get('name', 'N/A')}")
        
        # Match status
        st.markdown("### 📅 MATCH STATUS")
        status = leg_data.get("status", {})
        st.write(f"Status: {status.get('long', 'N/A')}")
        st.write(f"Short: {status.get('short', 'N/A')}")
        if status.get('elapsed'):
            st.write(f"Elapsed: {status.get('elapsed')} minutes")
        
        # Score if available
        if leg_data.get("scores"):
            st.markdown("### ⚽ SCORES")
            scores = leg_data["scores"]
            st.write(f"Home: {scores.get('home', 0)} - Away: {scores.get('away', 0)}")
            if scores.get('halftime'):
                st.write(f"Half-time: {scores['halftime'].get('home', 0)} - {scores['halftime'].get('away', 0)}")
            if scores.get('fulltime'):
                st.write(f"Full-time: {scores['fulltime'].get('home', 0)} - {scores['fulltime'].get('away', 0)}")
        
        # Venue information
        if leg_data.get("venue"):
            st.markdown("### 🏟️ VENUE")
            venue = leg_data["venue"]
            st.write(f"Name: {venue.get('name', 'N/A')}")
            st.write(f"City: {venue.get('city', 'N/A')}")
            if venue.get('capacity'):
                st.write(f"Capacity: {venue.get('capacity')}")
        
        # Head to Head if available
        if leg_data.get("head_to_head"):
            st.markdown("### 📊 HEAD TO HEAD")
            h2h = leg_data["head_to_head"]
            st.write(f"Total matches: {h2h.get('total', 'N/A')}")
            if h2h.get('home_wins') is not None:
                st.write(f"Home wins: {h2h.get('home_wins')}")
                st.write(f"Draws: {h2h.get('draws')}")
                st.write(f"Away wins: {h2h.get('away_wins')}")
        
        # Recent form
        if leg_data.get("form"):
            st.markdown("### 📈 RECENT FORM")
            form = leg_data["form"]
            if form.get('home'):
                st.write(f"Home team form: {form.get('home')}")
            if form.get('away'):
                st.write(f"Away team form: {form.get('away')}")
        
        # Note about odds
        st.info("ℹ️ Odds data is not available in the free tier. Upgrade to access odds from 100+ bookmakers.")
        
        # Raw data expander
        with st.expander("📄 View Raw API Response"):
            st.json(leg_data)
    
    else:
        st.warning("No leg data available")
        st.json(leg_data)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")
    
    if st.button("🚀 FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            matches = fetch_matches_by_date(date_str)
            if matches and len(matches) > 0:
                st.session_state.all_matches = matches
                st.success(f"✅ Loaded {len(matches)} matches!")
            else:
                st.session_state.all_matches = []
                st.error("No matches found")
            st.rerun()
    
    if st.session_state.all_matches:
        st.info(f"📊 {len(st.session_state.all_matches)} matches loaded")
        st.caption("Click 'VIEW LEG DATA' on any match to see full details")

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
    
    st.subheader(f"📋 MATCHES ({len(matches)})")
    
    for idx, match in enumerate(matches):
        home = match.get("homeTeam", {}).get("name", "Home")
        away = match.get("awayTeam", {}).get("name", "Away")
        league = match.get("league", {}).get("name", "Unknown")
        match_id = match.get("id")
        
        # Determine if odds might be available (free tier doesn't have them)
        odds_status = "⚠️ No odds (free tier)"
        
        with st.expander(f"{idx+1}. {home} vs {away} - {league}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Match ID:** {match_id}")
                st.write(f"**Status:** {match.get('status', {}).get('long', 'Scheduled')}")
                st.caption(odds_status)
            
            with col2:
                # Button to fetch and display leg data
                button_key = f"leg_btn_{match_id}_{idx}"
                if st.button("📊 VIEW LEG DATA", key=button_key, use_container_width=True):
                    with st.spinner(f"Fetching leg data for {home} vs {away}..."):
                        leg_data = fetch_match_leg_data(match_id)
                        if leg_data:
                            st.session_state.selected_leg_data = leg_data
                            st.session_state.selected_leg_name = f"{home} vs {away}"
                            st.success(f"✅ Leg data loaded!")
                        else:
                            st.error(f"❌ Failed to load leg data")
                        st.rerun()
    
    # Display selected leg data
    if st.session_state.selected_leg_data:
        st.divider()
        display_leg_data(st.session_state.selected_leg_data, st.session_state.selected_leg_name)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("❌ Close", use_container_width=True):
                st.session_state.selected_leg_data = None
                st.session_state.selected_leg_name = ""
                st.rerun()

else:
    st.info("👈 Click 'FETCH MATCHES' to load matches")
    
    with st.expander("ℹ️ About Leg Data"):
        st.markdown("""
        **What data is available in the free tier:**
        - ✅ Team names and IDs
        - ✅ League and competition info
        - ✅ Match status (scheduled, live, finished)
        - ✅ Scores (when available)
        - ✅ Venue information
        - ✅ Head-to-head stats
        - ✅ Recent form
        - ❌ Odds (requires paid tier)
        
        **To see leg data:**
        1. Click "FETCH MATCHES" to load matches
        2. Click "VIEW LEG DATA" on any match
        3. All available data will be displayed below
        """)

st.divider()
st.caption(f"Match Oracle | Free Tier (No Odds) | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
