# streamlit_app.py - CLEAN WORKING VERSION
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

# Sidebar
with st.sidebar:
    st.header("Settings")
    date = st.date_input("Match Date", datetime(2026, 6, 15))
    date_str = date.strftime("%Y-%m-%d")
    
    if st.button("FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            url = f"https://sports.highlightly.net/football/matches?date={date_str}&limit=200"
            headers = {"x-rapidapi-key": API_KEY}
            
            try:
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    matches = data.get("data", []) if isinstance(data, dict) else data
                    st.session_state.matches = matches
                    st.success(f"✅ Found {len(matches)} matches!")
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

# Main content
if st.session_state.get("matches"):
    matches = st.session_state.matches
    
    st.subheader(f"📋 ALL {len(matches)} MATCHES")
    
    for idx, match in enumerate(matches):
        # Extract data
        home = match.get("homeTeam", {}).get("name", "?")
        away = match.get("awayTeam", {}).get("name", "?")
        league = match.get("league", {}).get("name", "?")
        match_id = match.get("id")
        
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
        
        # Calculate verdict
        if home_odds < away_odds:
            selection = home
            odds = home_odds
        else:
            selection = away
            odds = away_odds
        
        model_prob = 1.0 / odds if odds > 1.0 else 0.5
        edge = model_prob - (1.0 / odds) if odds > 1.0 else 0
        
        if edge > 0.08 and odds < 2.50:
            verdict = "APPROVED"
            color = "green"
        elif edge > 0.03:
            verdict = "CAUTION"
            color = "orange"
        else:
            verdict = "REJECTED"
            color = "red"
        
        # Display match card
        with st.expander(f"{idx+1}. {home} vs {away} - {league}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Odds**")
                st.write(f"🏠 {home}: {home_odds}")
                st.write(f"🤝 Draw: {draw_odds}")
                st.write(f"✈️ {away}: {away_odds}")
            
            with col2:
                st.markdown("**Oracle Verdict**")
                st.markdown(f"<span style='color:{color}; font-weight:bold'>{verdict}</span>", unsafe_allow_html=True)
                st.write(f"Selection: {selection}")
                st.write(f"Odds: {odds:.2f}")
            
            with col3:
                st.markdown("**Metrics**")
                st.write(f"Edge: {edge*100:.1f}%")
                st.write(f"Model Prob: {model_prob*100:.1f}%")
            
            # CSV line
            csv_line = f"{home},{away},{selection},{home_odds},{draw_odds},{away_odds},{league}"
            st.code(csv_line, language="csv")
        
        # Show only first 50 matches to avoid performance issues
        if idx >= 49:
            st.info(f"... and {len(matches) - 50} more matches")
            break

else:
    st.info("👈 Click 'FETCH MATCHES' to get today's fixtures")

st.divider()
st.caption(f"Match Oracle | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
