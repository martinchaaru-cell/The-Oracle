# streamlit_app.py - FULLY DYNAMIC, NO HARDCODED LEAGUES
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Match Oracle", page_icon="🔮", layout="wide")

# ============================================================
# CONFIGURATION
# ============================================================

HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
HIGHLIGHTLY_URL = "https://sports.highlightly.net"

if not HIGHLIGHTLY_KEY:
    st.error("❌ HIGHLIGHTLY_API_KEY not found in secrets!")
    st.stop()

# ============================================================
# DYNAMIC API CALLS - NO HARDCODING
# ============================================================

@st.cache_data(ttl=300)
def fetch_all_leagues() -> list:
    """Fetch ALL leagues directly from Highlightly API - NO HARDCODING"""
    url = f"{HIGHLIGHTLY_URL}/football/leagues"
    params = {"limit": 500}  # Get as many as possible
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            leagues = data.get("data", []) if isinstance(data, dict) else data
            return leagues
        else:
            st.error(f"API returned {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching leagues: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_matches_for_league(league_id: int, date: str) -> list:
    """Fetch matches for a specific league on a specific date"""
    url = f"{HIGHLIGHTLY_URL}/football/matches"
    params = {
        "leagueId": league_id,
        "date": date,
        "limit": 100
    }
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", []) if isinstance(data, dict) else data
        return []
    except Exception as e:
        st.warning(f"Error fetching matches for league {league_id}: {e}")
        return []


def get_leagues_with_matches(date: str, all_leagues: list) -> list:
    """Check which leagues actually have matches on the given date"""
    leagues_with_matches = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, league in enumerate(all_leagues):
        status_text.text(f"Checking {league.get('name', 'Unknown')}...")
        league_id = league.get("id")
        
        if league_id:
            matches = fetch_matches_for_league(league_id, date)
            if matches:
                leagues_with_matches.append({
                    "id": league_id,
                    "name": league.get("name", "Unknown"),
                    "country": league.get("country", {}).get("name", "Unknown"),
                    "matches": matches,
                    "match_count": len(matches)
                })
        
        progress_bar.progress((i + 1) / len(all_leagues))
    
    status_text.empty()
    progress_bar.empty()
    
    return leagues_with_matches


# ============================================================
# UI
# ============================================================

st.title("🔮 Match Oracle - Football Intelligence")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Date picker
    match_date = st.date_input("📅 Match Date", datetime.now())
    date_str = match_date.strftime("%Y-%m-%d")
    
    st.divider()
    
    # Fetch leagues button
    if st.button("🔄 Load Leagues from API", type="primary", use_container_width=True):
        with st.spinner("Fetching leagues from Highlightly API..."):
            all_leagues = fetch_all_leagues()
            st.session_state.all_leagues = all_leagues
            st.session_state.leagues_loaded = True
            st.success(f"✅ Loaded {len(all_leagues)} leagues")
            st.rerun()
    
    st.divider()
    
    # Display loaded leagues status
    if st.session_state.get("leagues_loaded", False):
        st.success(f"📋 {len(st.session_state.all_leagues)} leagues available")
        
        if st.button("🔍 Find Leagues with Matches", use_container_width=True):
            with st.spinner("Checking which leagues have matches..."):
                leagues_with_matches = get_leagues_with_matches(date_str, st.session_state.all_leagues)
                st.session_state.leagues_with_matches = leagues_with_matches
                
                if leagues_with_matches:
                    st.success(f"✅ Found {len(leagues_with_matches)} leagues with matches on {date_str}")
                else:
                    st.warning(f"⚠️ No leagues have matches on {date_str}")
                st.rerun()
    else:
        st.info("👆 Click 'Load Leagues from API' to start")


# Main content area
st.subheader("📋 Matches")

# Display leagues with matches
if st.session_state.get("leagues_with_matches"):
    leagues_data = st.session_state.leagues_with_matches
    
    # Summary stats
    total_matches = sum(l["match_count"] for l in leagues_data)
    st.metric("Total Matches Found", total_matches)
    st.divider()
    
    # Display matches by league
    for league_data in leagues_data:
        with st.expander(f"🏆 {league_data['name']} - {league_data['country']} ({league_data['match_count']} matches)"):
            for match in league_data["matches"]:
                home = match.get("homeTeam", {}).get("name", "?")
                away = match.get("awayTeam", {}).get("name", "?")
                status = match.get("state", {}).get("description", "Scheduled")
                
                # Extract odds if available
                home_odds = 2.00
                draw_odds = 3.25
                away_odds = 3.50
                
                for bookmaker in match.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market.get("key") == "h2h":
                            for outcome in market.get("outcomes", []):
                                name = outcome.get("name", "").lower()
                                price = outcome.get("price", 0)
                                if name == "home" and price > 0:
                                    home_odds = price
                                elif name == "draw" and price > 0:
                                    draw_odds = price
                                elif name == "away" and price > 0:
                                    away_odds = price
                            break
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"**{home}** vs **{away}**")
                with col2:
                    st.caption(f"Odds: {home_odds} / {draw_odds} / {away_odds}")
                with col3:
                    st.caption(f"Status: {status}")
                with col4:
                    # CSV format for backend
                    csv_line = f"{home},{away},{home if home_odds < away_odds else away},{home_odds},{draw_odds},{away_odds},{league_data['name']}"
                    st.code(csv_line[:20] + "...", language="csv")
    
    # Export all matches to CSV
    all_csv_lines = []
    for league_data in leagues_data:
        for match in league_data["matches"]:
            home = match.get("homeTeam", {}).get("name", "?")
            away = match.get("awayTeam", {}).get("name", "?")
            all_csv_lines.append(f"{home},{away},{home},2.00,3.25,3.50,{league_data['name']}")
    
    if all_csv_lines:
        st.download_button(
            "📥 Export All Matches to CSV",
            "\n".join(all_csv_lines),
            file_name=f"matches_{date_str}.csv"
        )

elif not st.session_state.get("leagues_loaded", False):
    st.info("👈 Click 'Load Leagues from API' in the sidebar to fetch leagues from Highlightly")
else:
    st.info("👈 Click 'Find Leagues with Matches' to see which leagues have fixtures")


# Footer
st.divider()
st.caption(f"🔮 Match Oracle | Data directly from Highlightly API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
