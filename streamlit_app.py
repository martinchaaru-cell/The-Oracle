# streamlit_app.py - DEBUGGABLE VERSION
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Initialize session state
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "selected_leg_data" not in st.session_state:
    st.session_state.selected_leg_data = None
if "api_debug" not in st.session_state:
    st.session_state.api_debug = {}

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
API_HOST = "sports.highlightly.net"

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def debug_api_call(url, headers, params=None):
    """Make API call and return full debug info"""
    result = {
        "url": url,
        "headers": headers,
        "params": params,
        "status_code": None,
        "response_text": None,
        "response_json": None,
        "error": None
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        result["status_code"] = response.status_code
        result["response_text"] = response.text[:1000]
        
        if response.status_code == 200:
            try:
                result["response_json"] = response.json()
            except:
                result["error"] = "Could not parse JSON"
        else:
            result["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def fetch_matches_with_debug(date_str):
    """Fetch matches with full debug output"""
    url = "https://sports.highlightly.net/football/matches"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    params = {"date": date_str}
    
    result = debug_api_call(url, headers, params)
    st.session_state.api_debug["matches_list"] = result
    
    if result["status_code"] == 200 and result["response_json"]:
        data = result["response_json"]
        if isinstance(data, dict):
            if "response" in data:
                return data["response"]
            elif "data" in data:
                return data["data"]
        elif isinstance(data, list):
            return data
    return []

def fetch_match_leg_with_debug(match_id):
    """Fetch individual match leg data with full debug output"""
    url = f"https://sports.highlightly.net/football/matches/{match_id}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    result = debug_api_call(url, headers)
    st.session_state.api_debug["match_leg"] = result
    return result["response_json"] if result["status_code"] == 200 else None

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    league_filter = st.text_input("League contains", placeholder="Premier, Serie")
    
    # Debug toggle
    show_debug = st.checkbox("🔍 Show API Debug Info", value=True)
    
    if st.button("🚀 FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            matches = fetch_matches_with_debug(date_str)
            if matches:
                st.session_state.all_matches = matches
                st.success(f"✅ Loaded {len(matches)} matches!")
            else:
                st.session_state.all_matches = []
                st.error("No matches found")
            st.rerun()
    
    if st.session_state.all_matches:
        st.info(f"📊 {len(st.session_state.all_matches)} matches")

# Main content
if st.session_state.all_matches:
    matches = st.session_state.all_matches
    
    # Apply filter
    if league_filter:
        matches = [m for m in matches if league_filter.lower() in str(m.get("league", {}).get("name", "")).lower()]
    
    st.subheader(f"📋 MATCHES ({len(matches)})")
    
    for idx, match in enumerate(matches):
        home = match.get("homeTeam", {}).get("name", "Home")
        away = match.get("awayTeam", {}).get("name", "Away")
        league = match.get("league", {}).get("name", "Unknown")
        match_id = match.get("id")
        
        with st.expander(f"{idx+1}. {home} vs {away} - {league}"):
            st.write(f"**Match ID:** {match_id}")
            st.write(f"**Status:** {match.get('status', {}).get('long', 'Scheduled')}")
            
            # The button - each match has its own unique key
            button_key = f"leg_btn_{match_id}_{idx}"
            
            if st.button("📊 FETCH THIS MATCH'S LEG DATA", key=button_key, use_container_width=True):
                st.write("🔄 Fetching leg data from API...")
                
                # Fetch the leg data
                leg_data = fetch_match_leg_with_debug(match_id)
                
                if leg_data:
                    st.session_state.selected_leg_data = leg_data
                    st.session_state.selected_leg_name = f"{home} vs {away}"
                    st.success(f"✅ Successfully fetched leg data for {home} vs {away}!")
                else:
                    st.error(f"❌ Failed to fetch leg data for match {match_id}")
                    st.session_state.selected_leg_data = None
                
                st.rerun()
    
    # Display selected leg data
    if st.session_state.selected_leg_data:
        st.divider()
        st.subheader(f"📊 LEG DATA: {st.session_state.selected_leg_name}")
        
        leg_data = st.session_state.selected_leg_data
        
        # Try to extract odds from the leg data
        st.write("**Attempting to extract odds from leg data...**")
        
        # Search for odds in the response
        odds_found = []
        
        def search_for_odds(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if "odd" in key.lower() or "price" in key.lower():
                        odds_found.append({"path": f"{path}.{key}", "value": value})
                    elif key == "outcomes" and isinstance(value, list):
                        for outcome in value:
                            if isinstance(outcome, dict):
                                name = outcome.get("name", "")
                                price = outcome.get("price", 0)
                                if price:
                                    odds_found.append({"type": "outcome", "name": name, "price": price})
                    else:
                        search_for_odds(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_for_odds(item, f"{path}[{i}]")
        
        search_for_odds(leg_data)
        
        if odds_found:
            st.success(f"✅ Found {len(odds_found)} odds in the API response!")
            st.write("**Extracted odds:**")
            for odd in odds_found:
                st.code(str(odd))
        else:
            st.warning("⚠️ No odds found in the API response")
            st.write("The API returned data but it doesn't contain odds. Here's what was returned:")
        
        # Show the raw response
        with st.expander("📄 RAW API RESPONSE (Full Leg Data)", expanded=True):
            st.json(leg_data)
        
        if st.button("❌ Clear Leg Data"):
            st.session_state.selected_leg_data = None
            st.rerun()

else:
    st.info("👈 Click 'FETCH MATCHES' to load matches")

# Show API debug info
if show_debug and st.session_state.get("api_debug"):
    st.divider()
    st.subheader("🔍 API DEBUG INFO")
    
    if "matches_list" in st.session_state.api_debug:
        with st.expander("Matches List API Call", expanded=True):
            debug = st.session_state.api_debug["matches_list"]
            st.write(f"**URL:** {debug['url']}")
            st.write(f"**Status Code:** {debug['status_code']}")
            if debug.get("error"):
                st.error(f"Error: {debug['error']}")
            if debug.get("response_text"):
                st.write("**Response Preview:**")
                st.code(debug["response_text"][:500])
    
    if "match_leg" in st.session_state.api_debug:
        with st.expander("Match Leg API Call (Last Attempt)", expanded=True):
            debug = st.session_state.api_debug["match_leg"]
            st.write(f"**URL:** {debug['url']}")
            st.write(f"**Status Code:** {debug['status_code']}")
            if debug.get("error"):
                st.error(f"Error: {debug['error']}")
            if debug.get("response_text"):
                st.write("**Response Preview:**")
                st.code(debug["response_text"][:500])

st.divider()
st.caption(f"Match Oracle Debug Mode | {datetime.now()}")
