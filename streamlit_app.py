# streamlit_app.py - IMMEDIATE LEG DATA DISPLAY
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
    """Fetch complete leg data"""
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
                st.warning("No matches found")
            st.rerun()
    
    if st.session_state.all_matches:
        st.info(f"📊 {len(st.session_state.all_matches)} matches loaded")

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
    
    # Track which leg data to show
    if "show_leg_for_match" not in st.session_state:
        st.session_state.show_leg_for_match = None
    
    for idx, match in enumerate(matches):
        home = match.get("homeTeam", {}).get("name", "Home")
        away = match.get("awayTeam", {}).get("name", "Away")
        league = match.get("league", {}).get("name", "Unknown")
        match_id = match.get("id")
        
        with st.expander(f"{idx+1}. {home} vs {away} - {league}"):
            st.write(f"**Match ID:** {match_id}")
            st.write(f"**Status:** {match.get('status', {}).get('long', 'Scheduled')}")
            
            # Button to fetch leg data
            button_key = f"leg_btn_{match_id}_{idx}"
            if st.button("📊 FETCH LEG DATA", key=button_key, use_container_width=True):
                with st.spinner(f"Fetching leg data for {home} vs {away}..."):
                    leg_data = fetch_match_leg_data(match_id)
                    if leg_data:
                        # Store in session state immediately
                        st.session_state.selected_leg_data = leg_data
                        st.session_state.selected_leg_name = f"{home} vs {away}"
                        st.session_state.show_leg_for_match = match_id
                        st.success(f"✅ Leg data loaded! Scroll down to see details.")
                    else:
                        st.error("Failed to load leg data")
    
    # DISPLAY LEG DATA RIGHT HERE - outside the loop, always visible
    if st.session_state.selected_leg_data:
        st.divider()
        st.subheader(f"📊 LEG DATA: {st.session_state.selected_leg_name}")
        
        leg_data = st.session_state.selected_leg_data
        
        # Unwrap the data if needed
        if isinstance(leg_data, dict):
            if "response" in leg_data:
                leg_data = leg_data["response"]
            elif "data" in leg_data:
                leg_data = leg_data["data"]
        
        # Display the leg data
        if leg_data:
            # Basic match info
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 HOME TEAM")
                home_team = leg_data.get("homeTeam", {})
                st.write(f"**Name:** {home_team.get('name', 'N/A')}")
                st.write(f"**ID:** {home_team.get('id', 'N/A')}")
            
            with col2:
                st.markdown("### ✈️ AWAY TEAM")
                away_team = leg_data.get("awayTeam", {})
                st.write(f"**Name:** {away_team.get('name', 'N/A')}")
                st.write(f"**ID:** {away_team.get('id', 'N/A')}")
            
            # League info
            st.markdown("### 🏆 LEAGUE")
            league = leg_data.get("league", {})
            st.write(f"**Name:** {league.get('name', 'N/A')}")
            st.write(f"**Country:** {league.get('country', 'N/A')}")
            
            # Status and scores
            st.markdown("### 📅 MATCH STATUS")
            status = leg_data.get("status", {})
            st.write(f"**Status:** {status.get('long', 'N/A')}")
            if status.get('elapsed'):
                st.write(f"**Elapsed:** {status['elapsed']} minutes")
            
            scores = leg_data.get("scores", {})
            if scores:
                st.markdown("### ⚽ SCORES")
                st.write(f"**Home:** {scores.get('home', 0)}")
                st.write(f"**Away:** {scores.get('away', 0)}")
            
            # Venue
            venue = leg_data.get("venue", {})
            if venue:
                st.markdown("### 🏟️ VENUE")
                st.write(f"**Name:** {venue.get('name', 'N/A')}")
                st.write(f"**City:** {venue.get('city', 'N/A')}")
                if venue.get('capacity'):
                    st.write(f"**Capacity:** {venue['capacity']}")
            
            # Show all other data in expanders
            other_keys = [k for k in leg_data.keys() if k not in ['homeTeam', 'awayTeam', 'league', 'status', 'scores', 'venue']]
            if other_keys:
                with st.expander("📄 Additional Data"):
                    for key in other_keys:
                        st.markdown(f"**{key}:**")
                        st.json(leg_data[key])
            
            # Raw JSON
            with st.expander("🔍 Raw JSON Response"):
                st.json(st.session_state.selected_leg_data)
            
            # Close button
            if st.button("❌ Close Leg Data", use_container_width=True):
                st.session_state.selected_leg_data = None
                st.session_state.selected_leg_name = ""
                st.rerun()
        else:
            st.warning("No leg data available")

else:
    st.info("👈 Click 'FETCH MATCHES' to load matches")

st.divider()
st.caption(f"Match Oracle | Free Tier | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
