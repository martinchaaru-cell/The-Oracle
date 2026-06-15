# streamlit_app.py - PROPER ODDS EXTRACTION WITH CORRECTED API
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def extract_odds_from_match(match):
    """Properly extract odds from Highlightly API response"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Method 1: Check bookmakers array
    bookmakers = match.get("bookmakers", [])
    for bookmaker in bookmakers:
        markets = bookmaker.get("markets", [])
        for market in markets:
            if market.get("key") == "h2h" or market.get("market") == "Full Time Result":
                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    name = outcome.get("name", "").lower()
                    price = outcome.get("price", 0)
                    if price > 0:
                        if name == "home" or name == match.get("homeTeam", {}).get("name", "").lower():
                            home_odds = price
                        elif name == "draw":
                            draw_odds = price
                        elif name == "away" or name == match.get("awayTeam", {}).get("name", "").lower():
                            away_odds = price
                break  # Found h2h market
    
    # Method 2: Check direct odds field
    if home_odds is None:
        odds_data = match.get("odds", [])
        for odd in odds_data:
            if odd.get("market") == "Full Time Result":
                for value in odd.get("values", []):
                    val = value.get("value", "")
                    if val == "Home":
                        home_odds = value.get("odd", 2.00)
                    elif val == "Draw":
                        draw_odds = value.get("odd", 3.25)
                    elif val == "Away":
                        away_odds = value.get("odd", 3.50)
    
    # Default values if no odds found
    if home_odds is None:
        home_odds = 2.00
    if draw_odds is None:
        draw_odds = 3.25
    if away_odds is None:
        away_odds = 3.50
    
    return home_odds, draw_odds, away_odds

def fetch_match_details(match_id):
    """Fetch detailed data for a specific match"""
    # CORRECTED: Using proper API endpoint
    url = f"https://highlightly.net/api/football/matches/{match_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch match details: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        st.error(f"Error fetching match details: {e}")
        return None

def fetch_matches_by_date(date_str):
    """Fetch matches for a specific date using corrected API"""
    # CORRECTED: Using proper API endpoint
    url = "https://highlightly.net/api/football/matches"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    params = {
        "date": date_str
    }
    
    try:
        st.info(f"Fetching from: {url} with date: {date_str}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("❌ Authentication failed! Please check your API key.")
            st.info("Make sure you're using the correct API key format in your secrets.toml file")
            return None
        elif response.status_code == 404:
            st.error(f"❌ No matches found for date: {date_str}")
            return None
        else:
            st.error(f"API Error {response.status_code}: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timeout - API took too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Connection error - Cannot reach the API server")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

def fetch_available_leagues():
    """Fetch all available leagues"""
    url = "https://highlightly.net/api/football/leagues"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching leagues: {e}")
        return None

def display_match_details(match_data):
    """Display detailed match information"""
    if not match_data:
        return
    
    # Handle different response structures
    match = match_data.get("data", match_data)
    
    st.subheader("📊 MATCH DETAILS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Competition Info**")
        st.write(f"League: {match.get('league', {}).get('name', 'N/A')}")
        st.write(f"Season: {match.get('season', {}).get('name', 'N/A')}")
        st.write(f"Round: {match.get('round', {}).get('name', 'N/A')}")
        
    with col2:
        st.markdown("**📅 Match Info**")
        st.write(f"Status: {match.get('state', {}).get('description', 'N/A')}")
        st.write(f"Venue: {match.get('venue', {}).get('name', 'N/A')}")
        if match.get('starting_at'):
            st.write(f"Kickoff: {match.get('starting_at')}")
    
    # Scores if match is live or finished
    scores = match.get("scores", {})
    if scores:
        st.markdown("**⚽ Current Score**")
        st.write(f"Home: {scores.get('home', 0)} - Away: {scores.get('away', 0)}")
    
    # Head to head stats if available
    h2h = match.get("head_to_head", {})
    if h2h:
        st.markdown("**📈 Head to Head**")
        st.json(h2h)
    
    # Recent form
    form = match.get("form", {})
    if form:
        st.markdown("**📊 Recent Form**")
        col1, col2 = st.columns(2)
        with col1:
            home_form = form.get('home', {}).get('form', 'N/A')
            st.write(f"Home Team Form: {home_form}")
        with col2:
            away_form = form.get('away', {}).get('form', 'N/A')
            st.write(f"Away Team Form: {away_form}")

# Sidebar
with st.sidebar:
    st.header("Settings")
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    # League filter
    st.subheader("Filter by League")
    league_filter = st.text_input("League name contains", placeholder="e.g., Premier, Serie, World")
    
    # Show odds type
    show_only_real_odds = st.checkbox("Show only matches with real odds", value=False)
    
    # Option to fetch leagues
    if st.button("📋 SHOW AVAILABLE LEAGUES", use_container_width=True):
        with st.spinner("Fetching leagues..."):
            leagues_data = fetch_available_leagues()
            if leagues_data:
                st.session_state.leagues = leagues_data
                st.success("✅ Leagues loaded!")
                st.rerun()
    
    # Display leagues if available
    if st.session_state.get("leagues"):
        with st.expander("Available Leagues"):
            leagues = st.session_state.leagues.get("data", st.session_state.leagues)
            if isinstance(leagues, list):
                for league in leagues[:20]:  # Show first 20
                    st.caption(f"• {league.get('name', 'Unknown')}")
    
    st.divider()
    
    if st.button("FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            data = fetch_matches_by_date(date_str)
            
            if data:
                matches = data.get("data", []) if isinstance(data, dict) else data
                if matches:
                    st.session_state.all_matches = matches
                    st.session_state.raw_matches = matches
                    st.session_state.selected_match = None
                    st.success(f"✅ Found {len(matches)} matches!")
                    st.rerun()
                else:
                    st.warning(f"No matches found on {date_str}")
            else:
                st.error("Failed to fetch matches. Check API key and try again.")

# Main content
if st.session_state.get("all_matches"):
    all_matches = st.session_state.all_matches
    
    # Apply filters
    filtered = all_matches.copy()
    
    if league_filter:
        filtered = [m for m in filtered if league_filter.lower() in m.get("league", {}).get("name", "").lower()]
    
    if show_only_real_odds:
        filtered_with_odds = []
        for match in filtered:
            home_odds, draw_odds, away_odds = extract_odds_from_match(match)
            if home_odds != 2.00 or draw_odds != 3.25 or away_odds != 3.50:
                filtered_with_odds.append(match)
        filtered = filtered_with_odds
    
    st.subheader(f"📋 {len(filtered)} MATCHES")
    
    # Debug option
    if filtered and st.checkbox("Show raw API data for debugging"):
        st.json(filtered[0])
    
    # Store selected match details in session state
    if "selected_match_data" not in st.session_state:
        st.session_state.selected_match_data = None
    
    # Display matches in a compact grid
    for idx, match in enumerate(filtered):
        # Extract basic data
        home = match.get("homeTeam", {}).get("name", "?")
        away = match.get("awayTeam", {}).get("name", "?")
        league = match.get("league", {}).get("name", "?")
        match_id = match.get("id")
        status = match.get("state", {}).get("description", "Scheduled")
        
        # EXTRACT REAL ODDS
        home_odds, draw_odds, away_odds = extract_odds_from_match(match)
        
        # Determine if odds are real or default
        has_real_odds = home_odds != 2.00 or draw_odds != 3.25 or away_odds != 3.50
        
        # Calculate oracle verdict
        if home_odds < away_odds:
            selection = home
            odds = home_odds
            fav = "Home"
        else:
            selection = away
            odds = away_odds
            fav = "Away"
        
        model_prob = 1.0 / odds if odds > 1.0 else 0.5
        edge = model_prob - (1.0 / odds) if odds > 1.0 else 0
        
        if edge > 0.08 and odds < 2.50:
            verdict = "APPROVED"
            color = "green"
            verdict_icon = "✅"
        elif edge > 0.03:
            verdict = "CAUTION"
            color = "orange"
            verdict_icon = "⚠️"
        else:
            verdict = "REJECTED"
            color = "red"
            verdict_icon = "❌"
        
        # Create columns for each match row
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            st.markdown(f"**{idx+1}. {home} vs {away}**")
            st.caption(f"{league} | {status}")
        
        with col2:
            st.markdown(f"🎲 **Odds:** {home_odds:.2f} | {draw_odds:.2f} | {away_odds:.2f}")
            if not has_real_odds:
                st.caption("⚠️ Default odds (no bookmaker data)")
        
        with col3:
            st.markdown(f"<span style='color:{color}'>**{verdict_icon} {verdict}**</span>", unsafe_allow_html=True)
            st.caption(f"Selection: {selection} ({odds:.2f})")
        
        with col4:
            st.metric("Edge", f"{edge*100:.1f}%", delta_color="normal")
        
        with col5:
            # Button to fetch and display match details
            button_key = f"details_btn_{match_id}_{idx}"
            if st.button("📊 Details", key=button_key, use_container_width=True):
                with st.spinner(f"Fetching details for {home} vs {away}..."):
                    details = fetch_match_details(match_id)
                    if details:
                        st.session_state.selected_match_data = details
                        st.session_state.selected_match_name = f"{home} vs {away}"
                        st.rerun()
        
        # Add divider between matches
        st.divider()
        
        # Limit display for performance
        if idx >= 99:
            remaining = len(filtered) - 100
            if remaining > 0:
                st.info(f"... and {remaining} more matches")
            break
    
    # Display selected match details in an expandable section
    if st.session_state.get("selected_match_data"):
        with st.expander(f"📋 Match Details: {st.session_state.selected_match_name}", expanded=True):
            display_match_details(st.session_state.selected_match_data)
            
            # Add close button
            if st.button("Close Details", key="close_details"):
                st.session_state.selected_match_data = None
                st.rerun()

elif st.session_state.get("all_matches") is not None:
    if len(st.session_state.all_matches) == 0:
        st.warning(f"No matches found on {date_str}")
    else:
        st.info("👈 Click 'FETCH MATCHES' to load matches")
else:
    st.info("👈 Click 'FETCH MATCHES' to get today's fixtures")

# Footer
st.divider()
st.caption(f"Match Oracle | Data from Highlightly API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Debug info in sidebar
with st.sidebar:
    st.divider()
    st.caption("Debug Info:")
    if st.session_state.get("all_matches"):
        st.caption(f"📊 Total matches: {len(st.session_state.all_matches)}")
    if st.session_state.get("selected_match_data"):
        st.caption("✅ Match details loaded")
    st.caption(f"🔑 API Key loaded: {'Yes' if API_KEY else 'No'}")
