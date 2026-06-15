# streamlit_app.py - CORRECT API INTEGRATION
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Initialize session state
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
API_HOST = "sports.highlightly.net"  # The correct host

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def fetch_matches(date_str):
    """Fetch matches using the correct API format"""
    # Correct URL format from documentation
    url = f"https://sports.highlightly.net/football/matches"
    
    # BOTH headers are required
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    params = {"date": date_str}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # The API returns data directly
            if isinstance(data, dict):
                # Check common response formats
                if "response" in data:
                    return data["response"]
                elif "data" in data:
                    return data["data"]
                elif "matches" in data:
                    return data["matches"]
                else:
                    # If it's a dict but not wrapped, try to extract list values
                    for value in data.values():
                        if isinstance(value, list):
                            return value
                    return [data] if data else []
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            st.error(f"API Error {response.status_code}: {response.text[:200]}")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def fetch_match_details(match_id):
    """Fetch details for a specific match"""
    url = f"https://sports.highlightly.net/football/matches/{match_id}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def extract_real_odds(match):
    """Extract REAL odds from the API response"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Look for odds in the response
    # Method 1: Check for odds array directly
    if "odds" in match:
        odds_data = match["odds"]
        if isinstance(odds_data, list):
            for odd_item in odds_data:
                # Look for match odds market
                if odd_item.get("market") == "Full Time Result" or odd_item.get("name") == "Match Odds":
                    outcomes = odd_item.get("outcomes", [])
                    for outcome in outcomes:
                        outcome_name = outcome.get("name", "").lower()
                        price = outcome.get("price", 0)
                        if price > 0:
                            if "home" in outcome_name:
                                home_odds = price
                            elif "draw" in outcome_name:
                                draw_odds = price
                            elif "away" in outcome_name:
                                away_odds = price
    
    # Method 2: Check bookmakers array
    if home_odds is None and "bookmakers" in match:
        for bookmaker in match["bookmakers"]:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h" or market.get("market") == "Full Time Result":
                    for outcome in market.get("outcomes", []):
                        outcome_name = outcome.get("name", "").lower()
                        price = outcome.get("price", 0)
                        if price > 0:
                            if "home" in outcome_name:
                                home_odds = price
                            elif "draw" in outcome_name:
                                draw_odds = price
                            elif "away" in outcome_name:
                                away_odds = price
    
    return home_odds, draw_odds, away_odds

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")
    
    if st.button("FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches from Highlightly API..."):
            matches = fetch_matches(date_str)
            if matches and len(matches) > 0:
                st.session_state.all_matches = matches
                st.success(f"✅ Loaded {len(matches)} matches!")
            else:
                st.session_state.all_matches = []
                st.warning(f"No matches found for {date_str}")
            st.rerun()
    
    if st.session_state.all_matches:
        st.write(f"📊 {len(st.session_state.all_matches)} matches loaded")

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
    
    st.subheader(f"📋 MATCHES: {len(matches)}")
    
    if len(matches) == 0:
        st.warning("No matches match your filter")
    else:
        for idx, match in enumerate(matches):
            # Extract basic match info
            home_team = match.get("homeTeam", {})
            away_team = match.get("awayTeam", {})
            league = match.get("league", {})
            match_id = match.get("id")
            status = match.get("status", {}).get("long", "Scheduled")
            
            home_name = home_team.get("name", "Home")
            away_name = away_team.get("name", "Away")
            league_name = league.get("name", "Unknown")
            
            # Extract REAL odds (not hardcoded)
            home_odds, draw_odds, away_odds = extract_real_odds(match)
            
            # Check if we have real odds
            has_real_odds = home_odds is not None
            
            # Use defaults only for display if no real odds
            display_home = home_odds if home_odds else 2.00
            display_draw = draw_odds if draw_odds else 3.25
            display_away = away_odds if away_odds else 3.50
            
            # Calculate prediction based on real odds if available
            if home_odds and away_odds:
                if home_odds < away_odds:
                    selection = home_name
                    odds = home_odds
                else:
                    selection = away_name
                    odds = away_odds
                edge = ((1/odds) - 0.33) * 100 if odds > 0 else 0
            else:
                selection = "N/A"
                odds = 0
                edge = 0
            
            if has_real_odds and edge > 8:
                verdict = "✅ APPROVED"
                color = "green"
            elif has_real_odds and edge > 3:
                verdict = "⚠️ CAUTION"
                color = "orange"
            elif has_real_odds:
                verdict = "❌ REJECTED"
                color = "red"
            else:
                verdict = "📊 NO ODDS"
                color = "gray"
            
            with st.expander(f"{verdict} | {idx+1}. {home_name} vs {away_name} - {league_name}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🎲 ODDS**")
                    if has_real_odds:
                        st.success("Real odds from bookmakers")
                    else:
                        st.warning("No odds available for this match")
                    st.metric(home_name, f"{display_home:.2f}")
                    st.metric("Draw", f"{display_draw:.2f}")
                    st.metric(away_name, f"{display_away:.2f}")
                
                with col2:
                    st.markdown("**🔮 PREDICTION**")
                    if has_real_odds:
                        st.markdown(f"<h3 style='color:{color}'>{verdict}</h3>", unsafe_allow_html=True)
                        st.write(f"**Selection:** {selection}")
                        st.write(f"**Odds:** {odds:.2f}")
                        st.write(f"**Edge:** {edge:.1f}%")
                    else:
                        st.write("Cannot predict - no odds data")
                
                with col3:
                    st.markdown("**📊 MATCH INFO**")
                    st.write(f"🏆 {league_name}")
                    st.write(f"📅 Status: {status}")
                    st.write(f"🆔 ID: {match_id}")
                    if match.get("venue", {}).get("name"):
                        st.write(f"🏟️ Venue: {match['venue']['name']}")
                    
                    # View Details button
                    if st.button("View Full Match Details", key=f"details_{match_id}_{idx}"):
                        with st.spinner("Fetching match details..."):
                            details = fetch_match_details(match_id)
                            if details:
                                st.session_state.selected_match = details
                                st.success("Details loaded!")
                            else:
                                st.error("Could not fetch details")
                            st.rerun()
        
        # Show selected match details
        if st.session_state.selected_match:
            st.divider()
            st.subheader("📊 FULL MATCH DETAILS")
            st.json(st.session_state.selected_match)
            if st.button("Close Details"):
                st.session_state.selected_match = None
                st.rerun()

else:
    st.info("👈 Click 'FETCH MATCHES' in the sidebar to load matches")
    
    with st.expander("📖 API Information"):
        st.markdown("""
        **API Configuration:**
        - Base URL: `https://sports.highlightly.net/football/`
        - Headers Required:
          - `x-rapidapi-key`: Your API key
          - `x-rapidapi-host`: sports.highlightly.net
        
        **Endpoints:**
        - Matches: `/football/matches?date=YYYY-MM-DD`
        - Match Details: `/football/matches/{match_id}`
        """)

st.divider()
st.caption(f"Match Oracle | Highlightly Sports API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
