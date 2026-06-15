# streamlit_app.py - CLEAN WORKING VERSION
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

def extract_odds(match):
    """Extract odds from match data"""
    home_odds = 2.00
    draw_odds = 3.25
    away_odds = 3.50
    
    # Try to find real odds
    if "odds" in match:
        for odd in match["odds"]:
            if odd.get("market") == "full_time_result":
                for outcome in odd.get("outcomes", []):
                    name = outcome.get("name", "").lower()
                    price = outcome.get("price", 0)
                    if price > 0:
                        if "home" in name:
                            home_odds = price
                        elif "draw" in name:
                            draw_odds = price
                        elif "away" in name:
                            away_odds = price
    
    return home_odds, draw_odds, away_odds

def fetch_matches(date_str):
    """Fetch matches from API"""
    url = f"https://highlightly.net/api/football/matches?date={date_str}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            st.error(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# Sidebar
with st.sidebar:
    st.header("Settings")
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")
    show_real_odds_only = st.checkbox("Show only matches with real odds")
    
    if st.button("FETCH MATCHES", type="primary"):
        with st.spinner("Loading..."):
            matches = fetch_matches(date_str)
            st.session_state.all_matches = matches
            st.rerun()
    
    if st.session_state.all_matches:
        st.write(f"Matches loaded: {len(st.session_state.all_matches)}")

# Main content
if st.session_state.all_matches:
    matches = st.session_state.all_matches
    
    # Apply filters
    if league_filter:
        matches = [m for m in matches if league_filter.lower() in m.get("league", {}).get("name", "").lower()]
    
    filtered_matches = []
    for match in matches:
        home_odds, draw_odds, away_odds = extract_odds(match)
        has_real_odds = home_odds != 2.00
        
        if show_real_odds_only and not has_real_odds:
            continue
        
        filtered_matches.append(match)
    
    st.subheader(f"Matches: {len(filtered_matches)}")
    
    # Display matches
    for idx, match in enumerate(filtered_matches):
        home = match.get("homeTeam", {}).get("name", "Home")
        away = match.get("awayTeam", {}).get("name", "Away")
        league = match.get("league", {}).get("name", "Unknown")
        match_id = match.get("id", idx)
        
        home_odds, draw_odds, away_odds = extract_odds(match)
        
        # Determine prediction
        if home_odds < away_odds:
            selection = home
            odds = home_odds
        else:
            selection = away
            odds = away_odds
        
        edge = (1/odds - 1/3.5) * 100
        
        if edge > 8:
            verdict = "✅ APPROVED"
            color = "green"
        elif edge > 3:
            verdict = "⚠️ CAUTION"
            color = "orange"
        else:
            verdict = "❌ REJECTED"
            color = "red"
        
        with st.expander(f"{verdict} | {idx+1}. {home} vs {away} - {league}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**ODDS**")
                st.metric(home, f"{home_odds:.2f}")
                st.metric("Draw", f"{draw_odds:.2f}")
                st.metric(away, f"{away_odds:.2f}")
            
            with col2:
                st.markdown("**PREDICTION**")
                st.markdown(f"<h3 style='color:{color}'>{verdict}</h3>", unsafe_allow_html=True)
                st.write(f"Selection: {selection}")
                st.write(f"Odds: {odds:.2f}")
                st.write(f"Edge: {edge:.1f}%")
            
            with col3:
                st.markdown("**METRICS**")
                prob = (1/odds) * 100
                st.metric("Model Prob", f"{prob:.1f}%")
                st.metric("Fair Odds", f"{odds:.2f}")
            
            # Details button
            btn_key = f"btn_{match_id}_{idx}"
            if st.button("View Details", key=btn_key):
                st.session_state.selected_match = match
                st.rerun()
    
    # Show selected match details
    if st.session_state.selected_match:
        st.markdown("---")
        st.subheader("Match Details")
        st.json(st.session_state.selected_match)
        
        if st.button("Close Details"):
            st.session_state.selected_match = None
            st.rerun()

else:
    st.info("Click 'FETCH MATCHES' in the sidebar to load matches")

# Footer
st.markdown("---")
st.caption(f"Match Oracle | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
