# streamlit_app_new.py - COMPLETE WORKING VERSION
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# Your API key
API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

if not API_KEY:
    st.error("❌ No API key found! Add HIGHLIGHTLY_API_KEY to secrets.")
    st.stop()

st.title("⚽ Match Oracle - Live Matches")

# Date picker
col1, col2 = st.columns([1, 3])
with col1:
    match_date = st.date_input("Match Date", datetime(2026, 6, 15))
    date_str = match_date.strftime("%Y-%m-%d")

# Fetch button
if st.button("🔍 FETCH MATCHES", type="primary"):
    with st.spinner(f"Fetching matches for {date_str}..."):
        # Direct API call
        url = f"https://sports.highlightly.net/football/matches?date={date_str}&limit=200"
        headers = {"x-rapidapi-key": API_KEY}
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                matches = data.get("data", []) if isinstance(data, dict) else data
                st.session_state.matches = matches
                st.success(f"✅ Found {len(matches)} matches!")
                st.balloons()
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

# Display matches
if st.session_state.get("matches"):
    matches = st.session_state.matches
    
    st.subheader(f"📋 MATCHES ({len(matches)})")
    
    for idx, match in enumerate(matches):
        home = match.get("homeTeam", {}).get("name", "?")
        away = match.get("awayTeam", {}).get("name", "?")
        league = match.get("league", {}).get("name", "?")
        status = match.get("state", {}).get("description", "Scheduled")
        
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
        
        # Simple oracle
        if home_odds < away_odds:
            selection = home
            odds = home_odds
        else:
            selection = away
            odds = away_odds
        
        model_prob = 1.0 / odds if odds > 1.0 else 0.5
        edge = model_prob - (1.0 / odds) if odds > 1.0 else 0
        
        if edge > 0.08 and odds < 2.50:
            verdict = "✅ APPROVED"
            color = "green"
        elif edge > 0.03:
            verdict = "⚠️ CAUTION"
            color = "orange"
        else:
            verdict = "❌ REJECTED"
            color = "red"
        
        # Display match card
        with st.container():
            st.markdown(f"---")
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{home}** vs **{away}**")
                st.caption(f"{league} | {status}")
            
            with col2:
                st.markdown(f"**Odds**")
                st.write(f"🏠 {home_odds}  |  🤝 {draw_odds}  |  ✈️ {away_odds}")
            
            with col3:
                st.markdown(f"**Oracle**")
                st.markdown(f"<span style='color:{color}; font-weight:bold'>{verdict}</span>", unsafe_allow_html=True)
                st.write(f"Edge: {edge*100:.1f}%")
            
            with col4:
                st.markdown(f"**Pick**")
                st.markdown(f"**{selection}**")
                st.write(f"@{odds:.2f}")
            
            # CSV line
            csv_line = f"{home},{away},{selection},{home_odds},{draw_odds},{away_odds},{league}"
            st.code(csv_line, language="csv")
        
        if idx == 49:  # Show first 50 matches
            st.info(f"... and {len(matches) - 50} more matches")
            break

elif not st.session_state.get("matches"):
    st.info("👆 Click 'FETCH MATCHES' to see today's fixtures")

st.divider()
st.caption(f"API Key: {API_KEY[:10]}... | {datetime.now().strftime('%H:%M:%S')}")
