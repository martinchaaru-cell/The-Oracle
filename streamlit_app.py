# app_match.py - MINIMAL WORKING VERSION
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", layout="wide")

# Get API key
API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

# Debug: Show if API key exists
st.write(f"API Key Status: {'✅ Loaded' if API_KEY else '❌ Missing'}")

if not API_KEY:
    st.error("Add HIGHLIGHTLY_API_KEY to Streamlit secrets")
    st.stop()

# Date selection
date = st.date_input("Select Date", datetime(2026, 6, 15))
date_str = date.strftime("%Y-%m-%d")

# Fetch button
if st.button("GET MATCHES", type="primary"):
    st.write("Fetching matches...")
    
    url = f"https://sports.highlightly.net/football/matches?date={date_str}&limit=100"
    headers = {"x-rapidapi-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        st.write(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", []) if isinstance(data, dict) else data
            st.success(f"✅ FOUND {len(matches)} MATCHES!")
            
            # Store in session state
            st.session_state.matches = matches
        else:
            st.error(f"API Error: {response.status_code}")
            st.code(response.text[:500])
    except Exception as e:
        st.error(f"Error: {e}")

# Display matches
if st.session_state.get("matches"):
    matches = st.session_state.matches
    
    st.subheader(f"📋 MATCHES ({len(matches)})")
    
    for i, match in enumerate(matches):
        home = match.get("homeTeam", {}).get("name", "Unknown")
        away = match.get("awayTeam", {}).get("name", "Unknown")
        league = match.get("league", {}).get("name", "Unknown")
        
        # Create a card for each match
        with st.container():
            st.markdown(f"### {i+1}. {home} vs {away}")
            st.write(f"**League:** {league}")
            st.write(f"**Match ID:** {match.get('id')}")
            st.divider()
        
        # Show first 20 matches only
        if i >= 19:
            st.info(f"... and {len(matches) - 20} more matches")
            break

else:
    st.info("Click 'GET MATCHES' to fetch today's fixtures")
