# streamlit_app.py - WITH PROPER ERROR HANDLING
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Initialize session state
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None

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
            return {"error": f"API returned status {response.status_code}", "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e)}

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
    
    # Track which match's leg data to show
    if "leg_data_cache" not in st.session_state:
        st.session_state.leg_data_cache = {}
    
    for idx, match in enumerate(matches):
        home = match.get("homeTeam", {}).get("name", "Home")
        away = match.get("awayTeam", {}).get("name", "Away")
        league = match.get("league", {}).get("name", "Unknown")
        match_id = match.get("id")
        
        # Ensure match_id is valid
        if not match_id:
            continue
            
        expander_key = f"expander_{match_id}_{idx}"
        
        with st.expander(f"{idx+1}. {home} vs {away} - {league}", expanded=False):
            st.write(f"**Match ID:** {match_id}")
            st.write(f"**Status:** {match.get('status', {}).get('long', 'Scheduled')}")
            
            # Button to fetch leg data
            button_key = f"fetch_leg_{match_id}_{idx}"
            
            if st.button("📊 FETCH LEG DATA", key=button_key, use_container_width=True):
                with st.spinner("Fetching leg data from API..."):
                    leg_data = fetch_match_leg_data(match_id)
                    if leg_data:
                        st.session_state.leg_data_cache[match_id] = leg_data
                        st.success("✅ Leg data fetched successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to fetch leg data")
            
            # Display leg data if it exists in cache
            if match_id in st.session_state.leg_data_cache:
                st.divider()
                st.subheader("📊 LEG DATA")
                
                leg_data = st.session_state.leg_data_cache[match_id]
                
                # Check if leg_data is valid
                if leg_data and isinstance(leg_data, dict):
                    # Check for error in response
                    if "error" in leg_data:
                        st.error(f"API Error: {leg_data['error']}")
                        if "status_code" in leg_data:
                            st.write(f"Status Code: {leg_data['status_code']}")
                    else:
                        # Unwrap the data
                        actual_data = leg_data
                        if "response" in leg_data:
                            actual_data = leg_data["response"]
                        elif "data" in leg_data:
                            actual_data = leg_data["data"]
                        
                        # Check if actual_data is valid
                        if actual_data and isinstance(actual_data, dict):
                            # Teams
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**🏠 HOME TEAM**")
                                home_team = actual_data.get("homeTeam", {})
                                if home_team:
                                    st.write(f"Name: {home_team.get('name', 'N/A')}")
                                    st.write(f"ID: {home_team.get('id', 'N/A')}")
                                else:
                                    st.write("No home team data")
                            
                            with col2:
                                st.markdown("**✈️ AWAY TEAM**")
                                away_team = actual_data.get("awayTeam", {})
                                if away_team:
                                    st.write(f"Name: {away_team.get('name', 'N/A')}")
                                    st.write(f"ID: {away_team.get('id', 'N/A')}")
                                else:
                                    st.write("No away team data")
                            
                            # League
                            league_info = actual_data.get("league", {})
                            if league_info:
                                st.markdown("**🏆 LEAGUE**")
                                st.write(f"Name: {league_info.get('name', 'N/A')}")
                                st.write(f"Country: {league_info.get('country', 'N/A')}")
                            
                            # Status
                            status = actual_data.get("status", {})
                            if status:
                                st.markdown("**📅 STATUS**")
                                st.write(f"Long: {status.get('long', 'N/A')}")
                                st.write(f"Short: {status.get('short', 'N/A')}")
                            
                            # Scores
                            scores = actual_data.get("scores", {})
                            if scores and isinstance(scores, dict):
                                st.markdown("**⚽ SCORES**")
                                st.write(f"Home: {scores.get('home', 0)}")
                                st.write(f"Away: {scores.get('away', 0)}")
                            
                            # Venue
                            venue = actual_data.get("venue", {})
                            if venue:
                                st.markdown("**🏟️ VENUE**")
                                st.write(f"Name: {venue.get('name', 'N/A')}")
                                st.write(f"City: {venue.get('city', 'N/A')}")
                            
                            # Show raw response in expander
                            with st.expander("Raw API Response"):
                                st.json(leg_data)
                        else:
                            st.warning("No valid data in API response")
                            st.write("Raw response:")
                            st.json(leg_data)
                else:
                    st.error("Invalid leg data received")
                    st.write("Raw response:")
                    st.json(leg_data)

else:
    st.info("👈 Click 'FETCH MATCHES' to load matches")
    
    with st.expander("📖 How to use"):
        st.markdown("""
        1. **FETCH MATCHES** - Load all matches for selected date
        2. **Expand any match** - Click on a match to see details
        3. **FETCH LEG DATA** - Click button to load complete match data
        4. **View leg data** - Data appears right below the button
        """)

st.divider()
st.caption(f"Match Oracle | Free Tier | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
