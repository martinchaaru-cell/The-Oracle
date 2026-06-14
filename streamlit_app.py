"""
Match Oracle - Streamlit Frontend (Dynamic Leagues)
Fetches leagues dynamically from Highlightly API
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# ============================================
# CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🔮",
    layout="wide"
)

# Get API keys from secrets
HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")

# ============================================
# SESSION STATE
# ============================================

if "mode" not in st.session_state:
    st.session_state.mode = "backend"
if "scan_results" not in st.session_state:
    st.session_state.scan_results = None
if "scan_running" not in st.session_state:
    st.session_state.scan_running = False
if "available_leagues" not in st.session_state:
    st.session_state.available_leagues = []
if "leagues_loaded" not in st.session_state:
    st.session_state.leagues_loaded = False
if "selected_leagues" not in st.session_state:
    st.session_state.selected_leagues = []

# ============================================
# HIGHLIGHTLY CLIENT
# ============================================

class HighlightlyClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://sports.highlightly.net"
        self.headers = {"x-rapidapi-key": api_key}
        self.cache = {}
    
    def _request(self, endpoint, params=None):
        """Make API request with caching"""
        cache_key = f"{endpoint}_{str(params)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = data
                return data
        except Exception as e:
            st.error(f"API error: {e}")
        return None
    
    def get_countries(self):
        """Get all supported countries"""
        data = self._request("/football/countries")
        if data and isinstance(data, list):
            return data
        return []
    
    def get_leagues(self, country_code=None, season=None):
        """Get leagues dynamically - can filter by country"""
        params = {"limit": 200}
        if country_code:
            params["countryCode"] = country_code
        if season:
            params["season"] = season
        
        data = self._request("/football/leagues", params)
        
        if data and isinstance(data, dict):
            return data.get("data", [])
        elif data and isinstance(data, list):
            return data
        return []
    
    def get_league_by_id(self, league_id):
        """Get specific league by ID"""
        data = self._request(f"/football/leagues/{league_id}")
        if data and isinstance(data, list) and data:
            return data[0]
        return None
    
    def get_matches(self, date=None, league_id=None, limit=100):
        """Get matches for a specific date/league"""
        params = {"limit": limit}
        if date:
            params["date"] = date
        if league_id:
            params["leagueId"] = league_id
        
        data = self._request("/football/matches", params)
        
        if data and isinstance(data, dict):
            return data.get("data", [])
        elif data and isinstance(data, list):
            return data
        return []
    
    def get_team_info(self, team_id):
        """Get team information"""
        data = self._request(f"/football/teams/{team_id}")
        if data and isinstance(data, list) and data:
            return data[0]
        return None
    
    def search_leagues(self, query):
        """Search leagues by name"""
        all_leagues = self.get_leagues()
        if not all_leagues:
            return []
        
        query_lower = query.lower()
        return [
            l for l in all_leagues 
            if query_lower in l.get("name", "").lower() or
               query_lower in l.get("country", {}).get("name", "").lower()
        ]


# ============================================
# BACKEND FUNCTIONS
# ============================================

def backend_start_scan(leagues, date):
    """Start scan on backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/scan",
            json={
                "leagues": [l["key"] for l in leagues],
                "target_date": date.strftime("%Y-%m-%d"),
                "season": datetime.now().year
            },
            timeout=10
        )
        return response.status_code == 200 and response.json().get("status") == "started"
    except Exception as e:
        st.error(f"Backend error: {e}")
        return False

def backend_get_status():
    """Get scan status from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


# ============================================
# INITIALIZE CLIENT AND LOAD LEAGUES
# ============================================

if HIGHLIGHTLY_KEY and not st.session_state.leagues_loaded:
    with st.spinner("Loading leagues from Highlightly API..."):
        client = HighlightlyClient(HIGHLIGHTLY_KEY)
        
        # Fetch all leagues
        all_leagues = client.get_leagues()
        
        if all_leagues:
            # Process leagues: extract useful info
            processed_leagues = []
            for league in all_leagues:
                country = league.get("country", {})
                processed_leagues.append({
                    "id": league.get("id"),
                    "name": league.get("name"),
                    "country": country.get("name", "Unknown"),
                    "country_code": country.get("code", ""),
                    "logo": league.get("logo"),
                    "seasons": [s.get("season") for s in league.get("seasons", [])],
                    "key": league.get("name", "").upper().replace(" ", "_")
                })
            
            # Sort by country then name
            processed_leagues.sort(key=lambda x: (x["country"], x["name"]))
            
            st.session_state.available_leagues = processed_leagues
            st.session_state.leagues_loaded = True
            
            # Also store client for reuse
            st.session_state.highlightly_client = client

# ============================================
# UI - HEADER
# ============================================

st.title("🔮 Match Oracle - Football Intelligence")

# Mode selector
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    mode = st.radio(
        "API Mode",
        ["Backend (Full Pipeline)", "Highlightly (Raw Data)"],
        horizontal=True,
        index=0 if st.session_state.mode == "backend" else 1
    )
    st.session_state.mode = "backend" if "Backend" in mode else "highlightly"

# ============================================
# UI - SIDEBAR
# ============================================

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Backend status
    if st.session_state.mode == "backend":
        st.info(f"🔗 Backend: {BACKEND_URL}")
        backend_status = backend_get_status()
        if backend_status:
            st.success("✅ Backend Online")
        else:
            st.warning("⚠️ Backend may be starting...")
    
    # Date picker
    st.subheader("📅 Match Date")
    match_date = st.date_input("Date", datetime.now())
    
    # Dynamic League Selection
    st.subheader("🏆 Select Leagues")
    
    if st.session_state.leagues_loaded:
        leagues = st.session_state.available_leagues
        
        # Search filter for leagues
        search_term = st.text_input("🔍 Search leagues", placeholder="Premier, La Liga, Bundesliga...")
        
        filtered_leagues = leagues
        if search_term:
            search_lower = search_term.lower()
            filtered_leagues = [
                l for l in leagues 
                if search_lower in l["name"].lower() or search_lower in l["country"].lower()
            ]
        
        # Show league count
        st.caption(f"Showing {len(filtered_leagues)} of {len(leagues)} leagues")
        
        # Group by country for better organization
        countries = {}
        for league in filtered_leagues:
            country = league["country"]
            if country not in countries:
                countries[country] = []
            countries[country].append(league)
        
        # Select/deselect all buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✅ Select All", use_container_width=True):
                st.session_state.selected_leagues = filtered_leagues.copy()
                st.rerun()
        with col_b:
            if st.button("❌ Deselect All", use_container_width=True):
                st.session_state.selected_leagues = []
                st.rerun()
        
        st.divider()
        
        # Display leagues by country
        for country in sorted(countries.keys()):
            with st.expander(f"🌍 {country} ({len(countries[country])})"):
                for league in countries[country]:
                    league_key = f"{country}_{league['name']}"
                    checked = league in st.session_state.selected_leagues
                    if st.checkbox(
                        f"{league['name']}",
                        value=checked,
                        key=league_key
                    ):
                        if league not in st.session_state.selected_leagues:
                            st.session_state.selected_leagues.append(league)
                    else:
                        if league in st.session_state.selected_leagues:
                            st.session_state.selected_leagues.remove(league)
    else:
        st.error("Failed to load leagues. Check your Highlightly API key.")
        
        # Manual fallback input
        st.subheader("📝 Manual League Entry")
        manual_league_id = st.number_input("League ID", value=39, step=1)
        manual_league_name = st.text_input("League Name", value="Premier League")
        
        if st.button("Add League"):
            st.session_state.selected_leagues.append({
                "id": manual_league_id,
                "name": manual_league_name,
                "country": "Manual",
                "key": manual_league_name.upper().replace(" ", "_")
            })
            st.rerun()
    
    # Run button
    st.divider()
    if st.session_state.selected_leagues:
        if st.button("🚀 Run Scan", type="primary", use_container_width=True):
            if st.session_state.mode == "backend":
                if backend_start_scan(st.session_state.selected_leagues, match_date):
                    st.session_state.scan_running = True
                    st.session_state.scan_results = None
                    st.success("Scan started!")
                    st.rerun()
                else:
                    st.error("Failed to start scan")
            else:
                st.session_state.scan_running = True
                st.rerun()
    else:
        st.info("Select at least one league")
    
    # Upload section
    st.divider()
    st.subheader("📤 Upload Matches")
    upload_text = st.text_area(
        "CSV Format",
        height=100,
        placeholder="Home,Away,Selection,HomeOdds,DrawOdds,AwayOdds,League"
    )
    if st.button("🔍 Scan Upload", use_container_width=True):
        if upload_text.strip() and st.session_state.mode == "backend":
            # Handle upload
            pass

# ============================================
# MAIN CONTENT - HIGHLIGHTLY MODE
# ============================================

if st.session_state.mode == "highlightly":
    st.subheader("🏟️ Matches from Highlightly API")
    
    if st.session_state.scan_running:
        with st.spinner("Fetching matches..."):
            client = st.session_state.get("highlightly_client")
            if not client:
                client = HighlightlyClient(HIGHLIGHTLY_KEY)
            
            all_matches = []
            league_ids = [l["id"] for l in st.session_state.selected_leagues]
            
            progress_bar = st.progress(0)
            for i, league_id in enumerate(league_ids):
                matches = client.get_matches(
                    date=match_date.strftime("%Y-%m-%d"),
                    league_id=league_id,
                    limit=50
                )
                all_matches.extend(matches)
                progress_bar.progress((i + 1) / max(len(league_ids), 1))
            
            st.session_state.highlightly_matches = all_matches
            st.session_state.scan_running = False
    
    if st.session_state.get("highlightly_matches"):
        matches = st.session_state.highlightly_matches
        st.success(f"✅ Found {len(matches)} matches on {match_date}")
        
        for match in matches[:50]:
            home = match.get("homeTeam", {}).get("name", "?")
            away = match.get("awayTeam", {}).get("name", "?")
            league = match.get("league", {}).get("name", "?")
            score = match.get("state", {}).get("score", {}).get("current", "vs")
            
            with st.expander(f"{home} vs {away} - {league}"):
                st.write(f"Score: {score}")
                st.write(f"Match ID: {match.get('id')}")
                
                # CSV export for backend
                csv_line = f"{home},{away},{home},2.00,3.25,3.50,{league}"
                st.code(f"📋 Copy to Backend: {csv_line}", language="csv")
    else:
        st.info("Select leagues and click 'Run Scan' to fetch matches")

# ============================================
# MAIN CONTENT - BACKEND MODE
# ============================================

else:
    # Poll for results
    if st.session_state.scan_running:
        status = backend_get_status()
        
        if status:
            if status.get("log"):
                with st.expander("📋 Scan Log"):
                    for log_entry in status["log"][-20:]:
                        st.code(log_entry, language="text")
            
            if not status.get("running", True):
                st.session_state.scan_running = False
                st.session_state.scan_results = status.get("results", {})
                st.success("✅ Scan complete!")
                st.rerun()
            else:
                st.info("⏳ Scan in progress...")
                st.caption("Refreshing in 3 seconds...")
                import time
                time.sleep(3)
                st.rerun()
    
    # Display results
    if st.session_state.scan_results:
        results = st.session_state.scan_results
        totals = results.get("totals", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Scanned", totals.get("total", 0))
        with col2:
            st.metric("✅ Approved", totals.get("approved", 0))
        with col3:
            st.metric("⚠️ Caution", totals.get("caution", 0))
        with col4:
            st.metric("❌ Rejected", totals.get("rejected", 0))
        
        st.divider()
        
        leagues_data = results.get("leagues", [])
        if leagues_data:
            for league_data in leagues_data:
                st.subheader(f"🏆 {league_data.get('league', 'Unknown')}")
                matches = league_data.get("matches", [])
                
                for match in matches:
                    home = match.get("match", "").split(" vs ")[0] if " vs " in match.get("match", "") else "?"
                    away = match.get("match", "").split(" vs ")[1] if " vs " in match.get("match", "") else "?"
                    status = match.get("final_status", "PENDING")
                    
                    if status == "APPROVED":
                        status_icon = "🟢"
                    elif status == "CAUTION":
                        status_icon = "🟡"
                    elif status == "REJECTED":
                        status_icon = "🔴"
                    else:
                        status_icon = "⚪"
                    
                    st.write(f"{status_icon} **{home}** vs **{away}** - {status}")
        else:
            st.info("No results yet")
    else:
        st.info("👈 Select leagues and click 'Run Scan' to get started")

# ============================================
# FOOTER
# ============================================

st.divider()
st.caption(f"🔮 Match Oracle | Mode: {st.session_state.mode.upper()} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
