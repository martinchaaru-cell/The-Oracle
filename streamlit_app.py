"""DEBUG VERSION - Shows all errors"""
import sys
import traceback

# Catch all errors and display them
try:
    import streamlit as st
    import requests
    import pandas as pd
    from datetime import datetime, timedelta
    import os
    
    # Page config MUST be the first Streamlit command
    st.set_page_config(
        page_title="Highlightly API Tester",
        page_icon="🏈",
        layout="wide"
    )
    
    # Display that app is loading
    st.write("🚀 App is loading...")
    
    # ============================================
    # GET API KEY
    # ============================================
    
    def get_api_key():
        """Get API key from various sources"""
        # Try Streamlit secrets
        try:
            if "HIGHLIGHTLY_API_KEY" in st.secrets:
                return st.secrets["HIGHLIGHTLY_API_KEY"]
        except:
            pass
        
        # Try environment variables
        env_key = os.environ.get("HIGHLIGHTLY_API_KEY")
        if env_key:
            return env_key
        
        return None
    
    # Show loading status
    st.write("🔑 Checking API key...")
    
    HIGHLIGHTLY_KEY = get_api_key()
    
    # Sidebar
    with st.sidebar:
        st.header("🔑 API Status")
        
        if HIGHLIGHTLY_KEY:
            st.success("✅ API Key Loaded")
            masked = f"{HIGHLIGHTLY_KEY[:8]}...{HIGHLIGHTLY_KEY[-4:]}"
            st.code(masked, language="text")
        else:
            st.error("❌ API Key Not Found")
            st.info("""
            **Add your API key:**
            1. Go to Settings → Secrets
            2. Add: `HIGHLIGHTLY_API_KEY = "your-key"`
            3. Rerun the app
            """)
    
    # API Configuration
    HIGHLIGHTLY_HOST = "sport-highlights-api.p.rapidapi.com"
    HEADERS = {
        "x-rapidapi-host": HIGHLIGHTLY_HOST,
        "x-rapidapi-key": HIGHLIGHTLY_KEY
    }
    BASE_URL = f"https://{HIGHLIGHTLY_HOST}"
    
    def make_request(endpoint: str, params: dict = None):
        """Make API request"""
        if not HIGHLIGHTLY_KEY:
            return None
        
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {e}")
            return None
    
    # Main UI
    st.title("🏈 Highlightly Sports API Tester")
    
    # Test connection button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Test Connection"):
            with st.spinner("Testing..."):
                result = make_request("/football/countries", {"limit": 1})
                if result:
                    st.success("✅ API Connected Successfully!")
                    st.json(result)
                else:
                    st.error("❌ Connection Failed")
    
    with col2:
        if HIGHLIGHTLY_KEY:
            st.info(f"API Key: {HIGHLIGHTLY_KEY[:10]}...")
    
    # Simple test section
    st.header("Quick Test")
    
    test_option = st.selectbox(
        "Select test:",
        ["Countries", "Leagues", "Teams", "Matches"]
    )
    
    if test_option == "Countries":
        if st.button("Fetch Countries"):
            with st.spinner("Fetching..."):
                data = make_request("/football/countries")
                if data and "data" in data:
                    st.success(f"Found {len(data['data'])} countries")
                    st.dataframe(pd.DataFrame(data["data"]))
    
    elif test_option == "Leagues":
        league_name = st.text_input("League name (optional)")
        if st.button("Fetch Leagues"):
            with st.spinner("Fetching..."):
                params = {"limit": 20}
                if league_name:
                    params["leagueName"] = league_name
                data = make_request("/football/leagues", params)
                if data and "data" in data:
                    st.success(f"Found {len(data['data'])} leagues")
                    for league in data["data"][:10]:
                        st.write(f"- {league.get('name')} (ID: {league.get('id')})")
    
    elif test_option == "Teams":
        team_name = st.text_input("Team name", placeholder="Vikingur")
        if st.button("Search Teams") and team_name:
            with st.spinner("Searching..."):
                data = make_request("/football/teams", {"name": team_name, "limit": 20})
                if data and "data" in data:
                    st.success(f"Found {len(data['data'])} teams")
                    for team in data["data"]:
                        st.write(f"- {team.get('name')} (ID: {team.get('id')})")
    
    elif test_option == "Matches":
        match_date = st.date_input("Date", datetime.now())
        if st.button("Fetch Matches"):
            with st.spinner("Fetching..."):
                data = make_request("/football/matches", {"date": match_date.strftime("%Y-%m-%d"), "limit": 20})
                if data and "data" in data:
                    st.success(f"Found {len(data['data'])} matches")
                    for match in data["data"][:10]:
                        home = match.get("homeTeam", {}).get("name", "?")
                        away = match.get("awayTeam", {}).get("name", "?")
                        st.write(f"- {home} vs {away}")
    
    st.divider()
    st.caption("Debug mode - If you see this, the app is running!")
    
except Exception as e:
    # Display any error that occurs
    st.error(f"❌ App Error: {str(e)}")
    st.code(traceback.format_exc())
