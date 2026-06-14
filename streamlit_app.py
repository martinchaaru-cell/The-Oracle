import streamlit as st
import requests

st.set_page_config(page_title="Highlightly API Tester", page_icon="🏈", layout="wide")

# Get API key from secrets
HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("🏈 Highlightly Sports API Tester")

if not HIGHLIGHTLY_KEY:
    st.error("❌ HIGHLIGHTLY_API_KEY not found in secrets")
    st.stop()

# ============================================
# CORRECT API CONFIGURATION
# ============================================

# Use the DIRECT API URL (not the RapidAPI proxy)
BASE_URL = "https://sports.highlightly.net"

# Headers - only the API key is needed for direct access
HEADERS = {
    "x-rapidapi-key": HIGHLIGHTLY_KEY
}

def make_request(endpoint: str, params: dict = None):
    """Make request to Highlightly API"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        return response.status_code, response.json() if response.status_code == 200 else None
    except Exception as e:
        return 500, str(e)

# Test the connection
st.subheader("🔌 Testing API Connection")

# Test the countries endpoint (same as demo)
status, data = make_request("/football/countries", {"name": "France"})

if status == 200:
    st.success("✅ API Connection Successful!")
    st.write(f"Found: {data.get('name')} ({data.get('code')})")
    if data.get("logo"):
        st.image(data["logo"], width=50)
else:
    st.error(f"❌ API Connection Failed (Status: {status})")
    st.stop()

# ============================================
# Main App
# ============================================

st.header("📊 Available Endpoints")

tab1, tab2, tab3, tab4 = st.tabs(["🌍 Countries", "⚽ Leagues", "🏟️ Teams", "📅 Matches"])

# Tab 1: Countries
with tab1:
    country_search = st.text_input("Search country by name", placeholder="e.g., France, England")
    
    if st.button("Search Countries"):
        params = {}
        if country_search:
            params["name"] = country_search
        
        with st.spinner("Searching..."):
            status, data = make_request("/football/countries", params)
            
            if status == 200:
                if isinstance(data, list):
                    st.success(f"Found {len(data)} countries")
                    for country in data:
                        st.write(f"- {country.get('name')} ({country.get('code')})")
                elif isinstance(data, dict):
                    st.success(f"Found: {data.get('name')}")
                    st.json(data)
            else:
                st.error(f"Failed: Status {status}")

# Tab 2: Leagues
with tab2:
    league_search = st.text_input("Search league", placeholder="e.g., Premier League")
    country_code = st.text_input("Filter by country code (optional)", placeholder="GB, FR, DE")
    
    if st.button("Search Leagues"):
        params = {"limit": 50}
        if league_search:
            params["leagueName"] = league_search
        if country_code:
            params["countryCode"] = country_code
        
        with st.spinner("Searching..."):
            status, data = make_request("/football/leagues", params)
            
            if status == 200 and data and "data" in data:
                leagues = data["data"]
                st.success(f"Found {len(leagues)} leagues")
                
                for league in leagues[:20]:
                    with st.expander(f"🏆 {league.get('name', 'Unknown')}"):
                        st.write(f"**ID:** {league.get('id')}")
                        st.write(f"**Country:** {league.get('country', {}).get('name', 'Unknown')}")
                        seasons = [s.get("season") for s in league.get("seasons", [])]
                        st.write(f"**Seasons:** {', '.join(map(str, seasons[-5:]))}")
            else:
                st.error(f"Failed to fetch leagues (Status: {status})")

# Tab 3: Teams
with tab3:
    team_search = st.text_input("Search team", placeholder="e.g., Vikingur Gota, Manchester United")
    
    if st.button("Search Teams"):
        params = {"name": team_search, "limit": 50} if team_search else {"limit": 50}
        
        with st.spinner("Searching..."):
            status, data = make_request("/football/teams", params)
            
            if status == 200 and data and "data" in data:
                teams = data["data"]
                st.success(f"Found {len(teams)} teams")
                
                for team in teams:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if team.get("logo"):
                            st.image(team["logo"], width=40)
                        else:
                            st.write("🏟️")
                    with col2:
                        st.markdown(f"**{team.get('name', 'Unknown')}**")
                        st.caption(f"ID: `{team.get('id')}` | Type: {team.get('type', 'club')}")
                    st.divider()
            else:
                st.error(f"Failed to fetch teams (Status: {status})")

# Tab 4: Matches
with tab4:
    from datetime import datetime, timedelta
    
    date_option = st.radio("Date", ["Today", "Tomorrow", "Pick date"], horizontal=True)
    
    if date_option == "Today":
        match_date = datetime.now().strftime("%Y-%m-%d")
    elif date_option == "Tomorrow":
        match_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        match_date = st.date_input("Select date", datetime.now()).strftime("%Y-%m-%d")
    
    if st.button("Fetch Matches"):
        params = {"date": match_date, "limit": 100}
        
        with st.spinner(f"Fetching matches for {match_date}..."):
            status, data = make_request("/football/matches", params)
            
            if status == 200 and data and "data" in data:
                matches = data["data"]
                st.success(f"✅ Found {len(matches)} matches on {match_date}")
                
                for match in matches[:20]:
                    home = match.get("homeTeam", {}).get("name", "?")
                    away = match.get("awayTeam", {}).get("name", "?")
                    league = match.get("league", {}).get("name", "?")
                    state = match.get("state", {}).get("description", "Unknown")
                    score = match.get("state", {}).get("score", {}).get("current", "vs")
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 3, 2])
                    with col1:
                        st.write(home)
                    with col2:
                        st.write(score)
                    with col3:
                        st.write(away)
                    with col4:
                        st.caption(f"{league[:20]} | {state}")
                    st.divider()
            else:
                st.info(f"No matches found for {match_date} (Status: {status})")

# Footer
st.divider()
st.caption(f"API Base URL: {BASE_URL} | Status: Connected")
