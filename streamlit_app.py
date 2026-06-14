import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="🔮", layout="wide")

HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")

st.title("🔮 Match Oracle - Football Intelligence")
st.info("⚠️ Using Highlightly Mode (Backend temporarily unavailable)")

# Simple league selection (hardcoded but works)
LEAGUES = [
    {"name": "Premier League", "id": 39},
    {"name": "La Liga", "id": 140},
    {"name": "Bundesliga", "id": 78},
    {"name": "Serie A", "id": 135},
    {"name": "Ligue 1", "id": 61},
]

with st.sidebar:
    st.header("Settings")
    match_date = st.date_input("Match Date", datetime.now())
    
    selected_leagues = []
    for league in LEAGUES:
        if st.checkbox(league["name"]):
            selected_leagues.append(league["id"])
    
    if st.button("Fetch Matches", type="primary"):
        if selected_leagues and HIGHLIGHTLY_KEY:
            st.session_state.fetch = True
            st.session_state.selected_ids = selected_leagues
            st.session_state.date = match_date

# Fetch and display matches
if st.session_state.get("fetch"):
    with st.spinner("Fetching matches..."):
        all_matches = []
        
        for league_id in st.session_state.selected_ids:
            url = "https://sports.highlightly.net/football/matches"
            params = {
                "date": st.session_state.date.strftime("%Y-%m-%d"),
                "leagueId": league_id,
                "limit": 50
            }
            headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                matches = data.get("data", [])
                all_matches.extend(matches)
        
        st.session_state.matches = all_matches
        st.session_state.fetch = False

# Display results
if st.session_state.get("matches"):
    matches = st.session_state.matches
    st.success(f"✅ Found {len(matches)} matches")
    
    for match in matches:
        home = match.get("homeTeam", {}).get("name", "?")
        away = match.get("awayTeam", {}).get("name", "?")
        league = match.get("league", {}).get("name", "?")
        
        with st.expander(f"{home} vs {away} - {league}"):
            st.write("To get forensic reports, upload to backend:")
            csv_line = f"{home},{away},{home},2.00,3.25,3.50,{league}"
            st.code(csv_line, language="csv")
            
            # Option to send to backend
            if st.button(f"Send to Backend", key=match.get("id")):
                upload_response = requests.post(
                    f"{BACKEND_URL}/api/upload",
                    json={"content": csv_line, "league": "Custom"}
                )
                if upload_response.status_code == 200:
                    st.success("Sent to backend! Check Backend mode for results")
                else:
                    st.error(f"Failed: {upload_response.status_code}")
