import streamlit as st
import requests

st.set_page_config(page_title="Highlightly Sports API Tester", page_icon="🏈", layout="wide")

# Get API key from secrets
HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("🏈 Highlightly Sports API Tester")

if not HIGHLIGHTLY_KEY:
    st.error("❌ HIGHLIGHTLY_API_KEY not found in secrets")
    st.stop()

# ============================================
# CORRECT API CONFIGURATION
# ============================================

BASE_URL = "https://sports.highlightly.net"
HEADERS = {"x-rapidapi-key": HIGHLIGHTLY_KEY}

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

# Test the countries endpoint
status, data = make_request("/football/countries", {"name": "France"})

if status == 200:
    st.success("✅ API Connection Successful!")
    
    # Handle different response formats
    if isinstance(data, list):
        # Response is a list
        st.write(f"Found {len(data)} countries")
        for country in data:
            if country.get("name") == "France":
                st.write(f"Found: {country.get('name')} ({country.get('code')})")
                if country.get("logo"):
                    st.image(country["logo"], width=50)
    elif isinstance(data, dict):
        # Response is a single object
        st.write(f"Found: {data.get('name', 'Unknown')} ({data.get('code', 'N/A')})")
        if data.get("logo"):
            st.image(data["logo"], width=50)
    else:
        st.write(f"Response type: {type(data)}")
        st.json(data)
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
                    st.write("Response:", data)
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
            
            if status == 200:
                # Handle different response structures
                leagues = []
                if isinstance(data, dict) and "data" in data:
                    leagues = data["data"]
                elif isinstance(data, list):
                    leagues = data
                else:
                    st.write("Unexpected response format:", type(data))
                    st.json(data)
                    leagues = []
                
                if leagues:
                    st.success(f"Found {len(leagues)} leagues")
                    for league in leagues[:20]:
                        with st.expander(f"🏆 {league.get('name', 'Unknown')}"):
                            st.write(f"**ID:** {league.get('id')}")
                            st.write(f"**Country:** {league.get('country', {}).get('name', 'Unknown')}")
                            seasons = [s.get("season") for s in league.get("seasons", [])]
                            if seasons:
                                st.write(f"**Seasons:** {', '.join(map(str, seasons[-5:]))}")
                else:
                    st.info("No leagues found")
            else:
                st.error(f"Failed to fetch leagues (Status: {status})")

# Tab 3: Teams
with tab3:
    team_search = st.text_input("Search team", placeholder="e.g., Vikingur Gota, Manchester United")
    
    if st.button("Search Teams"):
        params = {"limit": 50}
        if team_search:
            params["name"] = team_search
        
        with st.spinner("Searching..."):
            status, data = make_request("/football/teams", params)
            
            if status == 200:
                # Handle different response structures
                teams = []
                if isinstance(data, dict) and "data" in data:
                    teams = data["data"]
                elif isinstance(data, list):
                    teams = data
                else:
                    st.write("Unexpected response format:", type(data))
                    st.json(data)
                    teams = []
                
                if teams:
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
                    st.info(f"No teams found for '{team_search}'")
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
            
            if status == 200:
                # Handle different response structures
                matches = []
                if isinstance(data, dict) and "data" in data:
                    matches = data["data"]
                elif isinstance(data, list):
                    matches = data
                else:
                    st.write("Unexpected response format:", type(data))
                    matches = []
                
                if matches:
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
                    st.info(f"No matches found for {match_date}")
            else:
                st.info(f"Failed to fetch matches (Status: {status})")

# Tab 5: Head-to-Head (Bonus)
st.subheader("🎯 Head-to-Head Search")

col1, col2 = st.columns(2)
with col1:
    team1 = st.text_input("Team 1", placeholder="Vikingur Gota")
with col2:
    team2 = st.text_input("Team 2", placeholder="07 Vestur")

if st.button("Get H2H Data") and team1 and team2:
    # First find team IDs
    with st.spinner("Finding teams..."):
        status, teams_data = make_request("/football/teams", {"name": team1, "limit": 5})
        
        if status == 200:
            teams = teams_data.get("data", []) if isinstance(teams_data, dict) else teams_data
            if teams:
                team1_id = teams[0]["id"]
                team1_name = teams[0]["name"]
                st.success(f"Found Team 1: {team1_name} (ID: {team1_id})")
            else:
                st.error(f"Team '{team1}' not found")
                st.stop()
        else:
            st.error(f"Failed to find team '{team1}'")
            st.stop()
    
    with st.spinner("Finding second team..."):
        status, teams_data = make_request("/football/teams", {"name": team2, "limit": 5})
        
        if status == 200:
            teams = teams_data.get("data", []) if isinstance(teams_data, dict) else teams_data
            if teams:
                team2_id = teams[0]["id"]
                team2_name = teams[0]["name"]
                st.success(f"Found Team 2: {team2_name} (ID: {team2_id})")
            else:
                st.error(f"Team '{team2}' not found")
                st.stop()
        else:
            st.error(f"Failed to find team '{team2}'")
            st.stop()
    
    # Get H2H data
    with st.spinner("Fetching head-to-head data..."):
        params = {"teamIdOne": team1_id, "teamIdTwo": team2_id}
        status, h2h_data = make_request("/football/head-2-head", params)
        
        if status == 200:
            matches = h2h_data if isinstance(h2h_data, list) else h2h_data.get("data", [])
            st.success(f"Found {len(matches)} historical matches")
            
            for match in matches[:10]:
                date = match.get("date", "Unknown")[:10]
                home = match.get("homeTeam", {}).get("name", "?")
                away = match.get("awayTeam", {}).get("name", "?")
                score = match.get("state", {}).get("score", {}).get("current", "0-0")
                st.write(f"📅 {date}: {home} {score} {away}")
        else:
            st.error(f"Failed to fetch H2H data (Status: {status})")

# Footer
st.divider()
st.caption(f"API Base URL: {BASE_URL} | Free Tier: 100 requests/day")
