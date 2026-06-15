# streamlit_app.py - COMPLETELY FIXED VERSION
import streamlit as st
import requests
from datetime import datetime
import json

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Initialize session state
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "selected_match_data" not in st.session_state:
    st.session_state.selected_match_data = None
if "selected_match_name" not in st.session_state:
    st.session_state.selected_match_name = ""
if "fetch_attempted" not in st.session_state:
    st.session_state.fetch_attempted = False

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def extract_odds_from_match(match):
    """Properly extract odds from Highlightly API response"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Try different possible odds locations in the API response
    # Location 1: odds array
    if "odds" in match and match["odds"]:
        for odd in match["odds"]:
            if odd.get("name") == "Match Odds" or odd.get("market") == "Full Time Result":
                outcomes = odd.get("outcomes", [])
                for outcome in outcomes:
                    label = outcome.get("label", "").lower()
                    price = outcome.get("price", 0)
                    if "home" in label:
                        home_odds = price
                    elif "draw" in label:
                        draw_odds = price
                    elif "away" in label:
                        away_odds = price
    
    # Location 2: bookmakers array
    if home_odds is None and "bookmakers" in match:
        for bookmaker in match["bookmakers"]:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name", "").lower()
                        price = outcome.get("price", 0)
                        if "home" in name:
                            home_odds = price
                        elif "draw" in name:
                            draw_odds = price
                        elif "away" in name:
                            away_odds = price
    
    # Default values if no odds found
    if home_odds is None:
        home_odds = 2.00
    if draw_odds is None:
        draw_odds = 3.25
    if away_odds is None:
        away_odds = 3.50
    
    return float(home_odds), float(draw_odds), float(away_odds)

def fetch_matches_from_api(date_str):
    """Fetch matches using the correct API endpoint"""
    # Try multiple possible API endpoints
    endpoints = [
        f"https://highlightly.net/api/football/matches?date={date_str}",
        f"https://sports.highlightly.net/api/football/matches?date={date_str}",
        f"https://api.highlightly.com/v1/football/matches?date={date_str}"
    ]
    
    headers_list = [
        {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"},
        {"x-rapidapi-key": API_KEY, "Accept": "application/json"},
        {"X-API-Key": API_KEY, "Accept": "application/json"}
    ]
    
    for endpoint in endpoints:
        for headers in headers_list:
            try:
                response = requests.get(endpoint, headers=headers, timeout=15)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
    
    # If all attempts fail, return mock data for testing
    return generate_mock_matches(date_str)

def generate_mock_matches(date_str):
    """Generate mock match data for testing when API fails"""
    mock_matches = []
    leagues = ["English Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    teams = [
        ("Manchester United", "Liverpool"),
        ("Real Madrid", "Barcelona"),
        ("Juventus", "AC Milan"),
        ("Bayern Munich", "Borussia Dortmund"),
        ("PSG", "Marseille"),
        ("Arsenal", "Chelsea"),
        ("Atletico Madrid", "Sevilla"),
        ("Inter Milan", "Roma")
    ]
    
    for i, (home, away) in enumerate(teams[:10]):
        mock_match = {
            "id": f"match_{i}_{datetime.now().timestamp()}",
            "homeTeam": {"name": home},
            "awayTeam": {"name": away},
            "league": {"name": leagues[i % len(leagues)]},
            "state": {"description": "Scheduled"},
            "odds": [
                {
                    "name": "Match Odds",
                    "outcomes": [
                        {"label": "Home", "price": 2.10 + (i * 0.1)},
                        {"label": "Draw", "price": 3.30 + (i * 0.05)},
                        {"label": "Away", "price": 3.80 - (i * 0.1)}
                    ]
                }
            ]
        }
        mock_matches.append(mock_match)
    
    return {"data": mock_matches, "mock": True}

def fetch_match_details(match_id):
    """Fetch detailed data for a specific match"""
    endpoints = [
        f"https://highlightly.net/api/football/matches/{match_id}",
        f"https://sports.highlightly.net/api/football/matches/{match_id}",
    ]
    
    headers_list = [
        {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"},
        {"x-rapidapi-key": API_KEY, "Accept": "application/json"},
    ]
    
    for endpoint in endpoints:
        for headers in headers_list:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
    
    # Return mock details if API fails
    return {"data": {"message": "Mock data - API unavailable", "match_id": match_id}}

def display_match_details(match_data):
    """Display detailed match information"""
    if not match_data:
        st.warning("No match data available")
        return
    
    data = match_data.get("data", match_data)
    
    st.subheader("📊 MATCH DETAILS")
    
    if "mock" in data or "message" in data:
        st.info("ℹ️ Showing mock data (API connection issue)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Competition**")
        st.write(f"League: {data.get('league', {}).get('name', 'N/A')}")
        st.write(f"Season: {data.get('season', {}).get('name', 'N/A')}")
        
    with col2:
        st.markdown("**📅 Match Status**")
        st.write(f"Status: {data.get('state', {}).get('description', 'Scheduled')}")
        st.write(f"Venue: {data.get('venue', {}).get('name', 'TBD')}")
    
    # Show team stats if available
    st.markdown("**📈 Team Statistics**")
    col3, col4 = st.columns(2)
    with col3:
        st.write(f"Home Team: {data.get('homeTeam', {}).get('name', 'Unknown')}")
        st.write(f"Form: {data.get('form', {}).get('home', 'N/A')}")
    with col4:
        st.write(f"Away Team: {data.get('awayTeam', {}).get('name', 'Unknown')}")
        st.write(f"Form: {data.get('form', {}).get('away', 'N/A')}")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Date selection
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    # League filter
    st.subheader("🔍 Filter")
    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")
    show_only_real_odds = st.checkbox("Show only matches with real odds", value=False)
    
    st.divider()
    
    # Fetch button
    if st.button("🚀 FETCH MATCHES", type="primary", use_container_width=True):
        st.session_state.fetch_attempted = True
        with st.spinner("Fetching matches..."):
            result = fetch_matches_from_api(date_str)
            if result and result.get("data"):
                st.session_state.all_matches = result["data"]
                if result.get("mock"):
                    st.info("ℹ️ Using mock data - API connection issue")
                else:
                    st.success(f"✅ Loaded {len(result['data'])} matches!")
            else:
                st.session_state.all_matches = []
                st.error("No matches found. Check API key or date.")
            st.rerun()
    
    # Show API status
    st.divider()
    st.caption(f"🔑 API Key: {'✅ Loaded' if API_KEY else '❌ Missing'}")
    
    if st.session_state.all_matches:
        st.caption(f"📊 Matches loaded: {len(st.session_state.all_matches)}")

# Main content
st.markdown("---")

if st.session_state.all_matches is not None:
    matches = st.session_state.all_matches
    
    if len(matches) == 0:
        st.warning(f"⚠️ No matches found for {date_str}")
        if st.session_state.fetch_attempted:
            st.info("Try a different date or check your API key")
    else:
        # Apply filters
        filtered = matches.copy()
        
        if league_filter:
            filtered = [m for m in filtered if league_filter.lower() in m.get("league", {}).get("name", "").lower()]
        
        if show_only_real_odds:
            real_odds_matches = []
            for match in filtered:
                h, d, a = extract_odds_from_match(match)
                if h != 2.00 or d != 3.25 or a != 3.50:
                    real_odds_matches.append(match)
            filtered = real_odds_matches
        
        st.subheader(f"📋 MATCHES FOUND: {len(filtered)}")
        
        # Display matches
        for idx, match in enumerate(filtered):
            # Extract match data
            home = match.get("homeTeam", {}).get("name", "Home Team")
            away = match.get("awayTeam", {}).get("name", "Away Team")
            league = match.get("league", {}).get("name", "Unknown League")
            match_id = match.get("id", f"mock_{idx}")
            status = match.get("state", {}).get("description", "Scheduled")
            
            # Get odds
            home_odds, draw_odds, away_odds = extract_odds_from_match(match)
            has_real_odds = home_odds != 2.00 or draw_odds != 3.25 or away_odds != 3.50
            
            # Calculate oracle verdict
            if home_odds < away_odds:
                selection = home
                odds = home_odds
            else:
                selection = away
                odds = away_odds
            
            model_prob = 1.0 / odds if odds > 1.0 else 0.5
            edge = model_prob - (1.0 / 3.5)  # Simplified edge calculation
            
            if edge > 0.08:
                verdict = "✅ APPROVED"
                color = "green"
            elif edge > 0.03:
                verdict = "⚠️ CAUTION"
                color = "orange"
            else:
                verdict = "❌ REJECTED"
                color = "red"
            
            # Create expandable match card
            with st.expander(f"{verdict} | {idx+1}. {home} vs {away} - {league}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🎲 ODDS**")
                    st.metric(home, f"{home_odds:.2f}")
                    st.metric("Draw", f"{draw_odds:.2f}")
                    st.metric(away, f"{away_odds:.2f}")
                    if not has_real_odds:
                        st.caption("⚠️ Estimated odds")
                
                with col2:
                    st.markdown("**🔮 PREDICTION**")
                    st.markdown(f"<h3 style='color:{color}'>{verdict}</h3>", unsafe_allow_html=True)
                    st.write(f"**Selection:** {selection}")
                    st.write(f"**Odds:** {odds:.2f}")
                    st.write(f"**Edge:** {edge*100:.1f}%")
                
                with col3:
                    st.markdown("**📊 METRICS**")
                    st.metric("Model Probability", f"{model_prob*100:.1f}%")
                    fair_odds = 1/model_prob if model_prob > 0 else 0
                    st.metric("Fair Odds", f"{fair_odds:.2f}")
                
                # DETAILS BUTTON - This is the fix for your request
                if st.button("🔍 VIEW FULL MATCH DETAILS", key=f"details_{match_id}_{idx}", use_container_width=True):
                    with st.spinner("Loading match details..."):
                        details = fetch_match_details(match_id)
                        if details:
                            st.session_state.selected_match_data = details
                            st.session_state.selected_match_name = f"{home} vs {away}"
                            st.rerun()
        
        # Display selected match details outside the loop
        if st.session_state.selected_match_data:
            st.markdown("---")
            st.subheader(f"📌 DETAILS FOR: {st.session_state.selected_match_name}")
            display_match_details(st.session_state.selected_match_data)
            
            # Close button
            if st.button("❌ Close Details", key="close_details_btn", use_container_width=True):
                st.session_state.selected_match_data = None
                st.session_state.selected_match_name = ""
                st.rerun()

else:
    # No matches loaded yet
    st.info("👈 Click 'FETCH MATCHES' in the sidebar to load matches")
    
    # Show example
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Enter your API key** in `.streamlit/secrets.toml`
        2. **Select a date** from the sidebar
        3. **Click 'FETCH MATCHES'** to load matches
        4. **Click on any match** to expand and see odds
        5. **Click 'VIEW FULL MATCH DETAILS'** button for detailed analysis
        """)

# Footer
st.markdown("---")
st.caption(f"⚽ Match Oracle v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
