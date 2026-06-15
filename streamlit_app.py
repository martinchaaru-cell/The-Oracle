# streamlit_app.py - AUTO-DISPLAYS ALL LEG DATA
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
            st.error(f"API returned status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
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
        st.error(f"Error fetching matches: {str(e)}")
        return []

def display_any_data(data, depth=0):
    """Recursively display any data structure"""
    if data is None:
        st.write("No data available")
        return
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                st.markdown(f"**{key.upper()}**")
                display_any_data(value, depth + 1)
            else:
                st.write(f"**{key}:** {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                st.markdown(f"**Item {i+1}**")
                display_any_data(item, depth + 1)
            else:
                st.write(f"**Item {i+1}:** {item}")
    else:
        st.write(str(data))

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
                        st.session_state.selected_leg_data = leg_data
                        st.session_state.selected_leg_name = f"{home} vs {away}"
                        st.success(f"✅ Leg data loaded successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to load leg data")
    
    # Display selected leg data prominently
    if st.session_state.selected_leg_data:
        st.divider()
        st.subheader(f"📊 LEG DATA: {st.session_state.selected_leg_name}")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Formatted View", "🔍 Raw JSON", "ℹ️ Info"])
        
        with tab1:
            st.markdown("### Leg Data Contents")
            leg_data = st.session_state.selected_leg_data
            
            # Check if data is wrapped in 'response' or 'data'
            if isinstance(leg_data, dict):
                if "response" in leg_data:
                    leg_data = leg_data["response"]
                elif "data" in leg_data:
                    leg_data = leg_data["data"]
            
            # Display the data in a readable format
            if isinstance(leg_data, dict):
                # Extract key information if it exists
                if "homeTeam" in leg_data:
                    st.markdown("#### 🏠 Home Team")
                    st.write(f"Name: {leg_data['homeTeam'].get('name', 'N/A')}")
                    st.write(f"ID: {leg_data['homeTeam'].get('id', 'N/A')}")
                
                if "awayTeam" in leg_data:
                    st.markdown("#### ✈️ Away Team")
                    st.write(f"Name: {leg_data['awayTeam'].get('name', 'N/A')}")
                    st.write(f"ID: {leg_data['awayTeam'].get('id', 'N/A')}")
                
                if "league" in leg_data:
                    st.markdown("#### 🏆 League")
                    st.write(f"Name: {leg_data['league'].get('name', 'N/A')}")
                    st.write(f"Country: {leg_data['league'].get('country', 'N/A')}")
                
                if "status" in leg_data:
                    st.markdown("#### 📅 Status")
                    st.write(f"Long: {leg_data['status'].get('long', 'N/A')}")
                    st.write(f"Short: {leg_data['status'].get('short', 'N/A')}")
                    if leg_data['status'].get('elapsed'):
                        st.write(f"Elapsed: {leg_data['status']['elapsed']} min")
                
                if "scores" in leg_data and leg_data["scores"]:
                    st.markdown("#### ⚽ Scores")
                    scores = leg_data["scores"]
                    st.write(f"Home: {scores.get('home', 0)} - Away: {scores.get('away', 0)}")
                
                if "venue" in leg_data and leg_data["venue"]:
                    st.markdown("#### 🏟️ Venue")
                    venue = leg_data["venue"]
                    st.write(f"Name: {venue.get('name', 'N/A')}")
                    st.write(f"City: {venue.get('city', 'N/A')}")
                    if venue.get('capacity'):
                        st.write(f"Capacity: {venue['capacity']}")
                
                # If none of the above, display all keys
                if not any(key in leg_data for key in ["homeTeam", "awayTeam", "league", "status"]):
                    st.markdown("#### All Available Data")
                    for key, value in leg_data.items():
                        if not isinstance(value, (dict, list)):
                            st.write(f"**{key}:** {value}")
                        else:
                            with st.expander(f"{key}"):
                                st.json(value)
            
            elif isinstance(leg_data, list):
                st.write(f"Array with {len(leg_data)} items")
                for i, item in enumerate(leg_data[:5]):  # Show first 5
                    st.write(f"**Item {i+1}:**")
                    st.json(item)
            else:
                st.write(leg_data)
        
        with tab2:
            st.json(st.session_state.selected_leg_data)
        
        with tab3:
            st.markdown("""
            **About Leg Data:**
            - Leg data contains all available information about a specific match
            - Free tier includes: teams, league, status, scores, venue
            - Odds require paid tier upgrade
            - Click 'Fetch Leg Data' on any match to see its details
            """)
        
        if st.button("❌ Clear Leg Data", use_container_width=True):
            st.session_state.selected_leg_data = None
            st.session_state.selected_leg_name = ""
            st.rerun()

else:
    st.info("👈 Click 'FETCH MATCHES' to load matches")
    
    with st.expander("📖 How to use"):
        st.markdown("""
        1. **Click 'FETCH MATCHES'** - Loads all matches for selected date
        2. **Expand any match** - Click on a match to see basic info
        3. **Click 'FETCH LEG DATA'** - Loads complete details for that match
        4. **View leg data** - See teams, league, status, scores, venue, and more
        """)

st.divider()
st.caption(f"Match Oracle | Free Tier | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
