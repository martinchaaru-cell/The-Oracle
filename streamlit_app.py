import streamlit as st
import requests
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Match Oracle - Football Intelligence", page_icon="🔮", layout="wide")

# ============================================
# CONFIGURATION
# ============================================

HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")

# API Configuration
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

def send_to_backend(match_data, league_name):
    """Send a match to the backend for processing"""
    # Format as CSV line that backend expects
    csv_line = f"{match_data['home_team']},{match_data['away_team']},{match_data['home_team']},2.00,3.25,3.50,{league_name}"
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            json={"content": csv_line, "league": "Custom"},
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Backend error: {e}")
        return False

def get_backend_results():
    """Get results from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ============================================
# SESSION STATE
# ============================================

if "processed_matches" not in st.session_state:
    st.session_state.processed_matches = []
if "backend_results" not in st.session_state:
    st.session_state.backend_results = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# ============================================
# UI
# ============================================

st.title("🔮 Match Oracle - Football Intelligence")

# Connection status
col1, col2, col3 = st.columns(3)
with col1:
    if HIGHLIGHTLY_KEY:
        st.success("✅ Highlightly API Connected")
    else:
        st.error("❌ Highlightly API Key Missing")
with col2:
    try:
        health = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if health.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Unavailable")
    except:
        st.warning("⚠️ Backend Unavailable")
with col3:
    st.info(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

# ============================================
# SIDEBAR - League Selection
# ============================================

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Date picker
    match_date = st.date_input("Match Date", datetime.now())
    
    # Pre-defined leagues (from Highlightly)
    st.subheader("🏆 Select Leagues")
    
    # Load leagues from Highlightly
    if st.button("🔄 Load Leagues"):
        with st.spinner("Loading leagues from Highlightly..."):
            status, data = make_request("/football/leagues", {"limit": 100})
            if status == 200:
                leagues = data.get("data", []) if isinstance(data, dict) else data
                st.session_state.available_leagues = leagues
                st.success(f"Loaded {len(leagues)} leagues")
            else:
                st.error("Failed to load leagues")
    
    # League selection
    if "available_leagues" in st.session_state:
        leagues = st.session_state.available_leagues
        
        # Search filter
        search = st.text_input("🔍 Search", placeholder="Premier, La Liga...")
        
        filtered = leagues
        if search:
            search_lower = search.lower()
            filtered = [l for l in leagues if search_lower in l.get("name", "").lower()]
        
        # Select leagues
        selected_leagues = []
        for league in filtered[:30]:  # Limit display
            if st.checkbox(f"{league.get('name', 'Unknown')}", key=f"league_{league.get('id')}"):
                selected_leagues.append(league)
        
        st.session_state.selected_leagues = selected_leagues
    else:
        # Fallback hardcoded leagues
        st.info("Click 'Load Leagues' first")
        fallback_leagues = [
            {"id": 39, "name": "Premier League"},
            {"id": 140, "name": "La Liga"},
            {"id": 78, "name": "Bundesliga"},
            {"id": 135, "name": "Serie A"},
            {"id": 61, "name": "Ligue 1"},
        ]
        selected_leagues = []
        for league in fallback_leagues:
            if st.checkbox(f"{league['name']}", key=f"fallback_{league['id']}"):
                selected_leagues.append(league)
        st.session_state.selected_leagues = selected_leagues
    
    # Action buttons
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        fetch_btn = st.button("🔍 Fetch Matches", type="primary", use_container_width=True)
    with col_b:
        process_btn = st.button("⚙️ Process with Backend", use_container_width=True)

# ============================================
# MAIN CONTENT
# ============================================

# Fetch matches from Highlightly
if fetch_btn and st.session_state.get("selected_leagues"):
    with st.spinner("Fetching matches from Highlightly..."):
        all_matches = []
        
        for league in st.session_state.selected_leagues:
            league_id = league.get("id")
            league_name = league.get("name")
            
            status, data = make_request("/football/matches", {
                "date": match_date.strftime("%Y-%m-%d"),
                "leagueId": league_id,
                "limit": 50
            })
            
            if status == 200:
                matches = data.get("data", []) if isinstance(data, dict) else data
                for match in matches:
                    all_matches.append({
                        "home_team": match.get("homeTeam", {}).get("name", "?"),
                        "away_team": match.get("awayTeam", {}).get("name", "?"),
                        "league_id": league_id,
                        "league_name": league_name,
                        "match_id": match.get("id"),
                        "date": match_date.strftime("%Y-%m-%d"),
                        "state": match.get("state", {}).get("description", "Unknown"),
                        "score": match.get("state", {}).get("score", {}).get("current", "vs"),
                    })
        
        st.session_state.fetched_matches = all_matches
        st.success(f"✅ Fetched {len(all_matches)} matches")

# Process matches with backend
if process_btn and st.session_state.get("fetched_matches"):
    st.session_state.processing = True
    st.session_state.processed_matches = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, match in enumerate(st.session_state.fetched_matches):
        status_text.text(f"Processing {i+1}/{len(st.session_state.fetched_matches)}: {match['home_team']} vs {match['away_team']}")
        
        if send_to_backend(match, match['league_name']):
            st.session_state.processed_matches.append(match)
        
        progress_bar.progress((i + 1) / len(st.session_state.fetched_matches))
        time.sleep(0.5)  # Rate limiting
    
    status_text.text("Waiting for backend to process...")
    time.sleep(3)  # Give backend time to process
    
    # Get results
    backend_status = get_backend_results()
    if backend_status and backend_status.get("results"):
        st.session_state.backend_results = backend_status["results"]
    
    st.session_state.processing = False
    st.success(f"✅ Processed {len(st.session_state.processed_matches)} matches")
    st.rerun()

# ============================================
# DISPLAY RESULTS
# ============================================

if st.session_state.get("fetched_matches"):
    st.subheader(f"📋 Matches Found ({len(st.session_state.fetched_matches)})")
    
    for match in st.session_state.fetched_matches:
        with st.expander(f"{match['home_team']} vs {match['away_team']} - {match['league_name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Match Info**")
                st.write(f"Date: {match['date']}")
                st.write(f"Status: {match['state']}")
                st.write(f"Score: {match['score']}")
                
                # CSV format for manual upload
                csv_line = f"{match['home_team']},{match['away_team']},{match['home_team']},2.00,3.25,3.50,{match['league_name']}"
                st.code(f"📋 CSV: {csv_line}", language="csv")
            
            with col2:
                # Check if this match has been processed by backend
                processed_ids = [m.get("match_id") for m in st.session_state.get("processed_matches", [])]
                if match.get("match_id") in processed_ids:
                    st.success("✅ Sent to Backend")
                else:
                    if st.button(f"Send to Backend", key=f"send_{match['match_id']}"):
                        if send_to_backend(match, match['league_name']):
                            st.success("Sent! Check results in a moment")
                            st.rerun()

# ============================================
# DISPLAY BACKEND RESULTS
# ============================================

if st.session_state.backend_results:
    st.subheader("🔮 Oracle Verdicts")
    
    results = st.session_state.backend_results
    totals = results.get("totals", {})
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total", totals.get("total", 0))
    with col2:
        st.metric("✅ Approved", totals.get("approved", 0))
    with col3:
        st.metric("⚠️ Caution", totals.get("caution", 0))
    with col4:
        st.metric("❌ Rejected", totals.get("rejected", 0))
    
    # Display verdicts by league
    for league_data in results.get("leagues", []):
        st.markdown(f"### 🏆 {league_data.get('league', 'Unknown')}")
        
        for match in league_data.get("matches", []):
            home = match.get("match", "").split(" vs ")[0] if " vs " in match.get("match", "") else "?"
            away = match.get("match", "").split(" vs ")[1] if " vs " in match.get("match", "") else "?"
            verdict = match.get("final_status", "PENDING")
            
            if verdict == "APPROVED":
                st.success(f"🟢 {home} vs {away} - {verdict}")
            elif verdict == "CAUTION":
                st.warning(f"🟡 {home} vs {away} - {verdict}")
            elif verdict == "REJECTED":
                st.error(f"🔴 {home} vs {away} - {verdict}")
            else:
                st.info(f"⚪ {home} vs {away} - {verdict}")

# ============================================
# DIRECT HIGHLIGHTLY TEST (Optional)
# ============================================

with st.expander("🔧 Direct Highlightly API Test"):
    st.write("Test the Highlightly API connection directly")
    
    test_endpoint = st.selectbox("Endpoint", ["Countries", "Leagues", "Teams"])
    
    if st.button("Test"):
        if test_endpoint == "Countries":
            status, data = make_request("/football/countries", {"limit": 10})
            if status == 200:
                st.json(data)
        elif test_endpoint == "Leagues":
            status, data = make_request("/football/leagues", {"limit": 10})
            if status == 200:
                st.json(data)
        else:
            status, data = make_request("/football/teams", {"limit": 10})
            if status == 200:
                st.json(data)

# ============================================
# FOOTER
# ============================================

st.divider()
st.caption(f"🔮 Match Oracle | Highlightly API + Backend | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
