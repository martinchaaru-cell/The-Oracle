# streamlit_app.py - PROPER ODDS EXTRACTION
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

st.title("⚽ MATCH ORACLE - LIVE MATCHES")

def extract_odds_from_match(match):
    """Properly extract odds from Highlightly API response"""
    home_odds = None
    draw_odds = None
    away_odds = None
    
    # Method 1: Check bookmakers array
    bookmakers = match.get("bookmakers", [])
    for bookmaker in bookmakers:
        markets = bookmaker.get("markets", [])
        for market in markets:
            if market.get("key") == "h2h" or market.get("market") == "Full Time Result":
                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    name = outcome.get("name", "").lower()
                    price = outcome.get("price", 0)
                    if price > 0:
                        if name == "home" or name == match.get("homeTeam", {}).get("name", "").lower():
                            home_odds = price
                        elif name == "draw":
                            draw_odds = price
                        elif name == "away" or name == match.get("awayTeam", {}).get("name", "").lower():
                            away_odds = price
                break  # Found h2h market
    
    # Method 2: Check direct odds field
    if home_odds is None:
        odds_data = match.get("odds", [])
        for odd in odds_data:
            if odd.get("market") == "Full Time Result":
                for value in odd.get("values", []):
                    val = value.get("value", "")
                    if val == "Home":
                        home_odds = value.get("odd", 2.00)
                    elif val == "Draw":
                        draw_odds = value.get("odd", 3.25)
                    elif val == "Away":
                        away_odds = value.get("odd", 3.50)
    
    # Default values if no odds found
    if home_odds is None:
        home_odds = 2.00
    if draw_odds is None:
        draw_odds = 3.25
    if away_odds is None:
        away_odds = 3.50
    
    return home_odds, draw_odds, away_odds

# Sidebar
with st.sidebar:
    st.header("Settings")
    date = st.date_input("Match Date", datetime(2026, 6, 15))
    date_str = date.strftime("%Y-%m-%d")
    
    # League filter
    st.subheader("Filter by League")
    league_filter = st.text_input("League name contains", placeholder="e.g., Premier, Serie, World")
    
    if st.button("FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            url = f"https://sports.highlightly.net/football/matches?date={date_str}&limit=200"
            headers = {"x-rapidapi-key": API_KEY}
            
            try:
                response = requests.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    matches = data.get("data", []) if isinstance(data, dict) else data
                    st.session_state.all_matches = matches
                    st.session_state.raw_matches = matches  # Keep raw for debugging
                    st.success(f"✅ Found {len(matches)} matches!")
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

# Main content
if st.session_state.get("all_matches"):
    all_matches = st.session_state.all_matches
    
    # Apply league filter
    if league_filter:
        filtered = [m for m in all_matches if league_filter.lower() in m.get("league", {}).get("name", "").lower()]
    else:
        filtered = all_matches
    
    st.subheader(f"📋 {len(filtered)} MATCHES")
    
    # Debug: Show raw API response for first match (expandable)
    if filtered and st.checkbox("Show raw API data for debugging"):
        st.json(filtered[0])
    
    for idx, match in enumerate(filtered):
        # Extract basic data
        home = match.get("homeTeam", {}).get("name", "?")
        away = match.get("awayTeam", {}).get("name", "?")
        league = match.get("league", {}).get("name", "?")
        match_id = match.get("id")
        status = match.get("state", {}).get("description", "Scheduled")
        
        # EXTRACT REAL ODDS - NOT HARDCODED
        home_odds, draw_odds, away_odds = extract_odds_from_match(match)
        
        # Debug print to console (visible in logs)
        print(f"Match: {home} vs {away} - Odds: H={home_odds}, D={draw_odds}, A={away_odds}")
        
        # Determine if odds are real or default
        has_real_odds = home_odds != 2.00 or draw_odds != 3.25 or away_odds != 3.50
        
        # Calculate oracle verdict
        if home_odds < away_odds:
            selection = home
            odds = home_odds
            fav = "Home"
        else:
            selection = away
            odds = away_odds
            fav = "Away"
        
        model_prob = 1.0 / odds if odds > 1.0 else 0.5
        edge = model_prob - (1.0 / odds) if odds > 1.0 else 0
        
        if edge > 0.08 and odds < 2.50:
            verdict = "APPROVED"
            color = "green"
            verdict_icon = "✅"
        elif edge > 0.03:
            verdict = "CAUTION"
            color = "orange"
            verdict_icon = "⚠️"
        else:
            verdict = "REJECTED"
            color = "red"
            verdict_icon = "❌"
        
        # Display match card
        with st.expander(f"{verdict_icon} {idx+1}. {home} vs {away} - {league}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🎲 ODDS**")
                st.metric(home, f"{home_odds:.2f}" if isinstance(home_odds, float) else home_odds)
                st.metric("Draw", f"{draw_odds:.2f}" if isinstance(draw_odds, float) else draw_odds)
                st.metric(away, f"{away_odds:.2f}" if isinstance(away_odds, float) else away_odds)
                if not has_real_odds:
                    st.caption("⚠️ No odds from bookmakers - using defaults")
            
            with col2:
                st.markdown("**🔮 ORACLE**")
                st.markdown(f"<h3 style='color:{color}'>{verdict}</h3>", unsafe_allow_html=True)
                st.write(f"Selection: **{selection}**")
                st.write(f"Odds: **{odds:.2f}**")
                st.write(f"Favorite: {fav}")
            
            with col3:
                st.markdown("**📊 METRICS**")
                st.metric("Edge", f"{edge*100:.1f}%")
                st.metric("Model Prob", f"{model_prob*100:.1f}%")
                fair_odds = 1/model_prob if model_prob > 0 else 0
                st.metric("Fair Odds", f"{fair_odds:.2f}")
            
            st.divider()
            
            # Additional match info
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"🆔 Match ID: {match_id}")
                st.write(f"📅 Status: {status}")
                st.write(f"🏆 Competition: {league}")
            
            with col_b:
                # Show if odds are real
                if has_real_odds:
                    st.success("✅ Real odds from bookmakers")
                else:
                    st.warning("⚠️ No bookmaker odds available - using estimates")
            
            # CSV for backend
            csv_line = f"{home},{away},{selection},{home_odds:.2f},{draw_odds:.2f},{away_odds:.2f},{league}"
            st.code(f"📋 COPY TO BACKEND: {csv_line}", language="csv")
        
        # Limit display for performance
        if idx >= 99:
            st.info(f"... and {len(filtered) - 100} more matches")
            break

elif st.session_state.get("all_matches") is not None and len(st.session_state.all_matches) == 0:
    st.warning(f"No matches found on {date_str}")
else:
    st.info("👈 Click 'FETCH MATCHES' to get today's fixtures")

# Footer
st.divider()
st.caption(f"Match Oracle | Data from Highlightly API | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
