# streamlit_app.py - FIXED to display all matches properly
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
# DYNAMIC API CALLS
# ============================================================

@st.cache_data(ttl=60)
def fetch_matches_direct(date: str, league_id: int = None) -> list:
    """Fetch matches directly from Highlightly API"""
    url = f"{HIGHLIGHTLY_URL}/football/matches"
    params = {"date": date, "limit": 200}
    if league_id:
        params["leagueId"] = league_id
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", []) if isinstance(data, dict) else data
            return matches
        else:
            st.error(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


@st.cache_data(ttl=300)
def fetch_all_leagues() -> dict:
    """Fetch all leagues and organize by country"""
    url = f"{HIGHLIGHTLY_URL}/football/leagues"
    params = {"limit": 500}
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            leagues = data.get("data", []) if isinstance(data, dict) else data
            
            # Organize by country
            leagues_by_country = {}
            for league in leagues:
                country = league.get("country", {}).get("name", "Other")
                if country not in leagues_by_country:
                    leagues_by_country[country] = []
                leagues_by_country[country].append({
                    "id": league.get("id"),
                    "name": league.get("name"),
                    "logo": league.get("logo")
                })
            
            return leagues_by_country
    except Exception as e:
        st.error(f"Error fetching leagues: {e}")
    
    return {}


def extract_match_details(match: dict) -> dict:
    """Extract all relevant details from a match"""
    home_team = match.get("homeTeam", {})
    away_team = match.get("awayTeam", {})
    league = match.get("league", {})
    state = match.get("state", {})
    score = state.get("score", {})
    
    # Extract odds
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
    
    # Determine favorite
    if home_odds < away_odds:
        favorite = home_team.get("name", "?")
        fav_odds = home_odds
        selection = favorite
    else:
        favorite = away_team.get("name", "?")
        fav_odds = away_odds
        selection = favorite
    
    # Simple oracle calculation
    model_prob = 1.0 / fav_odds if fav_odds > 1.0 else 0.5
    edge = model_prob - (1.0 / fav_odds) if fav_odds > 1.0 else 0
    
    if edge > 0.08 and fav_odds < 2.50:
        verdict = "APPROVED"
        confidence = "HIGH"
    elif edge > 0.03:
        verdict = "CAUTION"
        confidence = "MEDIUM"
    else:
        verdict = "REJECTED"
        confidence = "LOW"
    
    return {
        "match_id": match.get("id"),
        "home_team": home_team.get("name", "?"),
        "away_team": away_team.get("name", "?"),
        "league": league.get("name", "Unknown"),
        "league_id": league.get("id"),
        "status": state.get("description", "Unknown"),
        "score": score.get("current", "0-0"),
        "date": match.get("date", ""),
        "home_odds": home_odds,
        "draw_odds": draw_odds,
        "away_odds": away_odds,
        "favorite": favorite,
        "fav_odds": fav_odds,
        "selection": selection,
        "model_prob": model_prob,
        "edge": edge,
        "verdict": verdict,
        "confidence": confidence,
        "csv_line": f"{home_team.get('name', '?')},{away_team.get('name', '?')},{selection},{home_odds},{draw_odds},{away_odds},{league.get('name', 'Unknown')}"
    }


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
    
    # Fetch method
    fetch_method = st.radio(
        "Fetch Method",
        ["All Matches", "By League"],
        help="'All Matches' fetches everything. 'By League' lets you select specific leagues."
    )
    
    if fetch_method == "By League":
        st.divider()
        if st.button("🔄 Load Leagues", use_container_width=True):
            with st.spinner("Loading leagues..."):
                leagues_by_country = fetch_all_leagues()
                st.session_state.leagues_by_country = leagues_by_country
                st.success(f"✅ Loaded leagues from {len(leagues_by_country)} countries")
                st.rerun()
        
        if st.session_state.get("leagues_by_country"):
            st.subheader("Select Leagues")
            selected_league_ids = []
            for country, leagues in st.session_state.leagues_by_country.items():
                with st.expander(f"🌍 {country} ({len(leagues)})"):
                    for league in leagues:
                        if st.checkbox(league["name"], key=f"league_{league['id']}"):
                            selected_league_ids.append(league["id"])
            st.session_state.selected_league_ids = selected_league_ids
    
    st.divider()
    
    # Fetch button
    if st.button("🔍 Fetch Matches", type="primary", use_container_width=True):
        with st.spinner("Fetching matches from Highlightly..."):
            if fetch_method == "By League" and st.session_state.get("selected_league_ids"):
                all_matches = []
                for league_id in st.session_state.selected_league_ids:
                    matches = fetch_matches_direct(date_str, league_id)
                    all_matches.extend(matches)
                    st.info(f"League {league_id}: {len(matches)} matches")
            else:
                # Fetch all matches (no league filter)
                all_matches = fetch_matches_direct(date_str)
            
            if all_matches:
                processed = [extract_match_details(m) for m in all_matches]
                st.session_state.matches = processed
                st.success(f"✅ Found {len(processed)} matches on {date_str}")
                st.balloons()
            else:
                st.warning(f"No matches found on {date_str}")
            
            st.rerun()


# ============================================================
# DISPLAY MATCHES
# ============================================================

if st.session_state.get("matches"):
    matches = st.session_state.matches
    
    # Summary metrics
    approved = sum(1 for m in matches if m["verdict"] == "APPROVED")
    caution = sum(1 for m in matches if m["verdict"] == "CAUTION")
    rejected = sum(1 for m in matches if m["verdict"] == "REJECTED")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Total", len(matches))
    with col2:
        st.metric("✅ Approved", approved, delta=f"{approved/len(matches)*100:.0f}%")
    with col3:
        st.metric("⚠️ Caution", caution)
    with col4:
        st.metric("❌ Rejected", rejected)
    with col5:
        st.metric("🎯 Avg Edge", f"{sum(m['edge'] for m in matches)/len(matches)*100:.1f}%")
    
    st.divider()
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        leagues = sorted(set(m["league"] for m in matches))
        selected_leagues = st.multiselect("Filter by League", leagues, default=leagues[:5] if len(leagues) > 5 else leagues)
    with col2:
        verdicts = ["APPROVED", "CAUTION", "REJECTED"]
        selected_verdicts = st.multiselect("Filter by Verdict", verdicts, default=verdicts)
    
    # Filter matches
    filtered = [m for m in matches if m["league"] in selected_leagues and m["verdict"] in selected_verdicts]
    
    if not filtered:
        st.info("No matches match the selected filters")
    else:
        st.caption(f"Showing {len(filtered)} of {len(matches)} matches")
        
        # Group by league
        matches_by_league = {}
        for match in filtered:
            league = match["league"]
            if league not in matches_by_league:
                matches_by_league[league] = []
            matches_by_league[league].append(match)
        
        for league, league_matches in matches_by_league.items():
            with st.expander(f"🏆 {league} ({len(league_matches)} matches)", expanded=True):
                for match in league_matches:
                    # Determine verdict color
                    if match["verdict"] == "APPROVED":
                        verdict_color = "green"
                    elif match["verdict"] == "CAUTION":
                        verdict_color = "orange"
                    else:
                        verdict_color = "red"
                    
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"**{match['home_team']}** vs **{match['away_team']}**")
                        st.caption(f"ID: {match['match_id']}")
                    
                    with col2:
                        st.markdown(f"Odds:")
                        st.markdown(f"🏠 {match['home_odds']} | 🤝 {match['draw_odds']} | ✈️ {match['away_odds']}")
                    
                    with col3:
                        st.markdown(f"**Oracle:**")
                        st.markdown(f"<span style='color:{verdict_color}; font-weight:bold'>{match['verdict']}</span>", unsafe_allow_html=True)
                        st.caption(f"Edge: {match['edge']*100:.1f}% | Prob: {match['model_prob']*100:.1f}%")
                    
                    with col4:
                        st.markdown(f"**Selection:** {match['selection']}")
                        st.markdown(f"@ {match['fav_odds']:.2f}")
                        st.caption(f"Status: {match['status']}")
                    
                    # CSV for backend
                    st.code(f"📋 {match['csv_line']}", language="csv")
                    st.divider()

else:
    st.info("👈 Select date and click 'Fetch Matches' to see today's fixtures")

# Footer
st.divider()
st.caption(f"🔮 Match Oracle | Data from Highlightly API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
