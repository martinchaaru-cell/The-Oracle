# streamlit_app.py - WORKING WITH CORRECT API ENDPOINTS
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

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def fetch_countries():
    """Fetch available countries"""
    url = "https://sports.highlightly.net/football/countries"
    headers = {"x-rapidapi-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_leagues_by_country(country_code):
    """Fetch leagues for a specific country"""
    url = f"https://sports.highlightly.net/football/leagues/country/{country_code}"
    headers = {"x-rapidapi-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_matches_by_date(date_str):
    """Fetch matches using the correct Highlightly endpoint"""
    # Try the correct endpoint format from your working example
    url = f"https://sports.highlightly.net/football/matches"
    headers = {"x-rapidapi-key": API_KEY}
    params = {"date": date_str}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Handle different response formats
            if isinstance(data, dict):
                if "data" in data:
                    return data["data"]
                elif "response" in data:
                    return data["response"]
                elif "matches" in data:
                    return data["matches"]
                else:
                    # If data is a dict but not in expected format, try to extract values
                    return list(data.values()) if data else []
            elif isinstance(data, list):
                return data
        else:
            st.error(f"API Error {response.status_code}: {response.text[:100]}")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def fetch_match_details(match_id):
    """Fetch details for a specific match"""
    url = f"https://sports.highlightly.net/football/matches/{match_id}"
    headers = {"x-rapidapi-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def extract_odds_from_match(match):
    """Extract odds from match data"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Check various locations for odds
    if "odds" in match:
        for odd in match.get("odds", []):
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
    
    if "bookmakers" in match:
        for bookmaker in match.get("bookmakers", []):
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
    
    # Return None if no real odds found
    return home_odds, draw_odds, away_odds

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")
    show_only_real_odds = st.checkbox("Show only matches with real odds")
    
    if st.button("FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            matches = fetch_matches_by_date(date_str)
            if matches:
                st.session_state.all_matches = matches
                st.success(f"✅ Loaded {len(matches)} matches!")
            else:
                st.session_state.all_matches = []
                st.warning(f"No matches found for {date_str}")
            st.rerun()
    
    st.divider()
    
    # Test countries endpoint (working from your screenshot)
    if st.button("Test API Connection", use_container_width=True):
        with st.spinner("Testing..."):
            countries = fetch_countries()
            if countries:
                st.success(f"✅ API Working! Found {len(countries)} countries")
                st.json(countries[:3])
            else:
                st.error("API connection failed")
    
    if st.session_state.all_matches:
        st.write(f"📊 {len(st.session_state.all_matches)} matches loaded")

# Main content
if st.session_state.all_matches:
    matches = st.session_state.all_matches
    
    # Apply league filter
    if league_filter:
        matches = [m for m in matches if league_filter.lower() in str(m.get("league", {}).get("name", "")).lower()]
    
    # Filter by real odds if needed
    if show_only_real_odds:
        real_odds_matches = []
        for match in matches:
            h, d, a = extract_odds_from_match(match)
            if h is not None:
                real_odds_matches.append(match)
        matches = real_odds_matches
    
    st.subheader(f"📋 MATCHES FOUND: {len(matches)}")
    
    if len(matches) == 0:
        st.warning("No matches match your filters")
    else:
        for idx, match in enumerate(matches):
            # Extract basic info
            home = match.get("homeTeam", {}).get("name", "Home")
            away = match.get("awayTeam", {}).get("name", "Away")
            league = match.get("league", {}).get("name", "Unknown")
            match_id = match.get("id", idx)
            status = match.get("status", {}).get("long", "Scheduled")
            
            # Extract odds
            home_odds, draw_odds, away_odds = extract_odds_from_match(match)
            
            # Determine if we have real odds
            has_real_odds = home_odds is not None
            
            if not has_real_odds:
                home_odds, draw_odds, away_odds = 2.00, 3.25, 3.50
            
            # Calculate prediction
            if home_odds < away_odds:
                selection = home
                odds = home_odds
                fav = "HOME"
            else:
                selection = away
                odds = away_odds
                fav = "AWAY"
            
            # Calculate edge (simplified)
            implied_prob = 1/odds if odds > 0 else 0.33
            fair_prob = 0.45  # Baseline
            edge = (implied_prob - fair_prob) * 100
            
            if edge > 5 and has_real_odds:
                verdict = "✅ APPROVED"
                color = "green"
            elif edge > 0:
                verdict = "⚠️ CAUTION"
                color = "orange"
            else:
                verdict = "❌ REJECTED"
                color = "red"
            
            with st.expander(f"{verdict} | {idx+1}. {home} vs {away} - {league}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🎲 ODDS**")
                    st.metric(home, f"{home_odds:.2f}")
                    st.metric("Draw", f"{draw_odds:.2f}")
                    st.metric(away, f"{away_odds:.2f}")
                    if not has_real_odds:
                        st.caption("⚠️ No real odds available")
                    else:
                        st.caption("✅ Real odds from bookmakers")
                
                with col2:
                    st.markdown("**🔮 PREDICTION**")
                    st.markdown(f"<h3 style='color:{color}'>{verdict}</h3>", unsafe_allow_html=True)
                    st.write(f"**Selection:** {selection}")
                    st.write(f"**Odds:** {odds:.2f}")
                    st.write(f"**Edge:** {edge:.1f}%")
                    st.write(f"**Favorite:** {fav}")
                
                with col3:
                    st.markdown("**📊 MATCH INFO**")
                    st.write(f"🏆 {league}")
                    st.write(f"📅 Status: {status}")
                    st.write(f"🆔 ID: {match_id}")
                    
                    # Details button
                    if st.button("View Details", key=f"details_{match_id}_{idx}"):
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
            st.subheader("📊 MATCH DETAILS")
            st.json(st.session_state.selected_match)
            
            if st.button("Close Details"):
                st.session_state.selected_match = None
                st.rerun()

else:
    st.info("👈 Click 'FETCH MATCHES' in the sidebar to load matches")
    
    # Show example of working API
    with st.expander("📖 API Info"):
        st.markdown("""
        **Working API Endpoints:**
        - Countries: `https://sports.highlightly.net/football/countries`
        - Matches: `https://sports.highlightly.net/football/matches?date=YYYY-MM-DD`
        
        **Authentication:** `x-rapidapi-key` header with your API key
        """)

# Footer
st.divider()
st.caption(f"Match Oracle | API: Highlightly Sports | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
