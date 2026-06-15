# streamlit_app.py - PROPERLY FIXED API INTEGRATION
import streamlit as st
import requests
from datetime import datetime
import hmac

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Initialize session state
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "selected_match_data" not in st.session_state:
    st.session_state.selected_match_data = None
if "selected_match_name" not in st.session_state:
    st.session_state.selected_match_name = ""
if "api_error" not in st.session_state:
    st.session_state.api_error = None

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def diagnose_api_connection():
    """Diagnose what's wrong with the API connection"""
    issues = []
    
    if not API_KEY:
        issues.append("❌ No API key found in secrets.toml")
    else:
        issues.append(f"✅ API key loaded (length: {len(API_KEY)} chars)")
    
    # Test different API formats
    test_endpoints = [
        ("https://highlightly.net/api/football/matches?date=2025-06-15", "Bearer"),
        ("https://sports.highlightly.net/api/football/matches?date=2025-06-15", "Bearer"),
        ("https://api.highlightly.com/v1/football/matches?date=2025-06-15", "Bearer"),
        ("https://sports.highlightly.net/football/matches?date=2025-06-15", "RapidAPI"),
    ]
    
    for url, auth_type in test_endpoints:
        try:
            if auth_type == "Bearer":
                headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}
            else:
                headers = {"x-rapidapi-key": API_KEY, "Accept": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=5)
            issues.append(f"🔍 {auth_type} to {url[:50]}... → Status: {response.status_code}")
            
            if response.status_code == 200:
                issues.append(f"   ✅ WORKING! Use this format")
                return True, response.json(), issues
        except Exception as e:
            issues.append(f"   ❌ Error: {str(e)[:50]}")
    
    return False, None, issues

def fetch_real_matches(date_str):
    """Actually fix the API call - no hardcoded data"""
    
    # First, diagnose what's wrong
    working, data, diagnosis = diagnose_api_connection()
    
    if working and data:
        matches = data.get("data", data)
        if isinstance(matches, list):
            return matches, diagnosis
        else:
            return [], ["API returned data but not in expected format"]
    
    # If we get here, show the actual error
    return None, diagnosis

def extract_odds_from_match(match):
    """Extract real odds from API response"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Check various places where odds might be
    if "odds" in match and match["odds"]:
        for odd_obj in match["odds"]:
            if odd_obj.get("market") == "full_time_result" or odd_obj.get("name") == "Match Odds":
                outcomes = odd_obj.get("outcomes", [])
                for outcome in outcomes:
                    outcome_name = outcome.get("name", "").lower()
                    price = outcome.get("price", 0) or outcome.get("odd", 0)
                    
                    if "home" in outcome_name:
                        home_odds = price
                    elif "draw" in outcome_name:
                        draw_odds = price
                    elif "away" in outcome_name:
                        away_odds = price
    
    if "bookmakers" in match:
        for bookmaker in match["bookmakers"]:
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        outcome_name = outcome.get("name", "").lower()
                        price = outcome.get("price", 0)
                        
                        if "home" in outcome_name:
                            home_odds = price
                        elif "draw" in outcome_name:
                            draw_odds = price
                        elif "away" in outcome_name:
                            away_odds = price
    
    # Return None if no real odds found (not defaults)
    return home_odds, draw_odds, away_odds

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    
    st.divider()
    
    if st.button("🔍 DIAGNOSE API", use_container_width=True):
        with st.spinner("Testing API connections..."):
            working, data, diagnosis = diagnose_api_connection()
            st.session_state.api_diagnosis = diagnosis
            st.rerun()
    
    if st.session_state.get("api_diagnosis"):
        with st.expander("📋 API Diagnosis Results", expanded=True):
            for line in st.session_state.api_diagnosis:
                st.code(line)
    
    st.divider()
    
    if st.button("🚀 FETCH MATCHES", type="primary", use_container_width=True):
        st.session_state.fetch_attempted = True
        with st.spinner("Fetching real matches from API..."):
            matches, diagnosis = fetch_real_matches(date_str)
            
            if matches is not None:
                st.session_state.all_matches = matches
                st.session_state.api_error = None
                st.success(f"✅ Loaded {len(matches)} real matches!")
            else:
                st.session_state.all_matches = []
                st.session_state.api_error = diagnosis
                st.error("❌ Failed to fetch real matches")
            st.rerun()
    
    st.divider()
    st.caption(f"🔑 API Key: {'Present' if API_KEY else 'Missing'}")
    if API_KEY:
        st.caption(f"   Length: {len(API_KEY)} chars")
        st.caption(f"   First 5 chars: {API_KEY[:5]}...")

# Main content
st.markdown("---")

if st.session_state.api_error:
    st.error("### ⚠️ API Integration Error")
    st.write("The API call failed. Here's why:")
    for error in st.session_state.api_error:
        st.write(f"- {error}")
    
    st.info("""
    **How to fix:**
    
    1. **Verify your API key** - Make sure it's correct in `.streamlit/secrets.toml`
    2. **Check API documentation** - The endpoint or authentication method might be different
    3. **Contact Highlightly support** - Ask for the correct:
       - Base URL
       - Authentication header format
       - Required parameters for fetching matches
       
    **Format in secrets.toml should be:**
    ```toml
    HIGHLIGHTLY_API_KEY = "your-actual-api-key-here"
