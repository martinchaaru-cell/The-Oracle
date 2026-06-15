# streamlit_app.py - With Demo Mode for Off-Season
import streamlit as st
import requests
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Match Oracle", page_icon="🔮", layout="wide")

HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
HIGHLIGHTLY_URL = "https://sports.highlightly.net"

# Demo matches for off-season display
DEMO_MATCHES = {
    "International Friendly": [
        {"home": "Germany", "away": "France", "time": "20:45", "home_odds": 2.10, "draw_odds": 3.30, "away_odds": 3.40},
        {"home": "England", "away": "Spain", "time": "20:00", "home_odds": 2.30, "draw_odds": 3.20, "away_odds": 3.10},
        {"home": "Italy", "away": "Netherlands", "time": "19:45", "home_odds": 2.05, "draw_odds": 3.25, "away_odds": 3.60},
        {"home": "Brazil", "away": "Argentina", "time": "21:00", "home_odds": 2.15, "draw_odds": 3.10, "away_odds": 3.40},
        {"home": "Portugal", "away": "Belgium", "time": "19:30", "home_odds": 2.25, "draw_odds": 3.15, "away_odds": 3.25},
    ],
    "Club Friendly": [
        {"home": "Real Madrid", "away": "AC Milan", "time": "18:00", "home_odds": 1.85, "draw_odds": 3.60, "away_odds": 4.00},
        {"home": "Bayern Munich", "away": "Tottenham", "time": "17:30", "home_odds": 1.75, "draw_odds": 3.80, "away_odds": 4.20},
        {"home": "Barcelona", "away": "Arsenal", "time": "20:00", "home_odds": 1.90, "draw_odds": 3.50, "away_odds": 3.80},
        {"home": "Manchester City", "away": "Chelsea", "time": "19:00", "home_odds": 1.70, "draw_odds": 3.80, "away_odds": 4.50},
        {"home": "PSG", "away": "Inter Milan", "time": "20:30", "home_odds": 1.80, "draw_odds": 3.70, "away_odds": 4.00},
    ],
    "World Cup Qualifiers": [
        {"home": "USA", "away": "Mexico", "time": "02:00", "home_odds": 2.20, "draw_odds": 3.10, "away_odds": 3.30},
        {"home": "Japan", "away": "South Korea", "time": "11:00", "home_odds": 2.15, "draw_odds": 3.05, "away_odds": 3.50},
        {"home": "Australia", "away": "Saudi Arabia", "time": "10:30", "home_odds": 1.95, "draw_odds": 3.20, "away_odds": 4.00},
        {"home": "Egypt", "away": "Senegal", "time": "19:00", "home_odds": 2.25, "draw_odds": 3.00, "away_odds": 3.30},
        {"home": "Morocco", "away": "Tunisia", "time": "20:00", "home_odds": 2.10, "draw_odds": 3.10, "away_odds": 3.60},
    ]
}

def fetch_real_matches(date: str, league_id: int) -> list:
    """Try to fetch real matches from API"""
    if not HIGHLIGHTLY_KEY:
        return []
    
    url = f"{HIGHLIGHTLY_URL}/football/matches"
    params = {"leagueId": league_id, "date": date, "limit": 50}
    headers = {"x-rapidapi-key": HIGHLIGHTLY_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", []) if isinstance(data, dict) else data
    except:
        pass
    return []

def get_demo_matches_for_date(date: str) -> dict:
    """Return demo matches - all matches are always available in demo mode"""
    # Use the date to seed the selection (same matches for same date)
    random.seed(date)
    
    all_demo_matches = []
    for league, matches in DEMO_MATCHES.items():
        for match in matches:
            all_demo_matches.append({
                "league": league,
                "home": match["home"],
                "away": match["away"],
                "time": match["time"],
                "home_odds": match["home_odds"],
                "draw_odds": match["draw_odds"],
                "away_odds": match["away_odds"],
            })
    
    # Return a subset (not all) for variety
    random.shuffle(all_demo_matches)
    return all_demo_matches[:12]  # Return up to 12 matches

def process_match_oracle(match: dict) -> dict:
    """Simple oracle logic for demo matches"""
    home_odds = match["home_odds"]
    away_odds = match["away_odds"]
    
    if home_odds < away_odds:
        selection = match["home"]
        odds = home_odds
        fav_is_home = True
    else:
        selection = match["away"]
        odds = away_odds
        fav_is_home = False
    
    model_prob = 1.0 / odds if odds > 1.0 else 0.5
    edge = model_prob - (1.0 / odds) if odds > 1.0 else 0
    
    if edge > 0.08 and odds < 2.50:
        verdict = "APPROVED"
        confidence = "HIGH"
    elif edge > 0.03:
        verdict = "CAUTION"
        confidence = "MEDIUM"
    else:
        verdict = "REJECTED"
        confidence = "LOW"
    
    return {
        "match": f"{match['home']} vs {match['away']}",
        "selection": selection,
        "odds": odds,
        "home_odds": match["home_odds"],
        "draw_odds": match["draw_odds"],
        "away_odds": match["away_odds"],
        "final_status": verdict,
        "final_confidence": confidence,
        "oracle": {
            "model_prob": round(model_prob, 4),
            "edge": round(edge, 4),
            "pre_filter_passed": edge > 0.03,
            "failure_score": round((1 - model_prob) * 10, 2),
        },
        "m3_probability": {
            "home_implied": round(1/match["home_odds"]*100, 1),
            "draw_implied": round(1/match["draw_odds"]*100, 1),
            "away_implied": round(1/match["away_odds"]*100, 1),
        },
        "decision_notes": [f"Edge: {edge*100:.1f}%", f"Model prob: {model_prob*100:.1f}%"],
    }

st.title("🔮 Match Oracle - Football Intelligence")

# Check if API key exists (for real data)
api_available = bool(HIGHLIGHTLY_KEY)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Data source selector
    data_source = st.radio(
        "Data Source",
        ["Demo Mode (Off-Season)", "Real API (if available)"],
        index=0,
        help="Demo mode shows sample matches since leagues are on summer break"
    )
    
    st.divider()
    
    match_date = st.date_input("📅 Match Date", datetime.now())
    date_str = match_date.strftime("%Y-%m-%d")
    
    st.divider()
    
    if st.button("🔍 Fetch Matches", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            if data_source == "Real API (if available)" and api_available:
                # Try real API first
                st.info("Attempting to fetch real matches from Highlightly...")
                # Try a league that might have matches (international)
                test_leagues = [1, 2, 3]  # International league IDs
                real_matches = []
                for league_id in test_leagues:
                    matches = fetch_real_matches(date_str, league_id)
                    real_matches.extend(matches)
                
                if real_matches:
                    st.session_state.matches = real_matches
                    st.success(f"✅ Found {len(real_matches)} real matches!")
                else:
                    st.warning("No real matches found. Using demo mode instead.")
                    st.session_state.matches = get_demo_matches_for_date(date_str)
                    st.info(f"📋 Showing {len(st.session_state.matches)} demo matches")
            else:
                # Use demo mode
                st.session_state.matches = get_demo_matches_for_date(date_str)
                st.success(f"✅ Demo mode: {len(st.session_state.matches)} matches ready")
            
            st.session_state.fetch_triggered = True
            st.rerun()

# Main content
if st.session_state.get("fetch_triggered", False):
    st.session_state.fetch_triggered = False
    st.rerun()

if st.session_state.get("matches"):
    matches = st.session_state.matches
    st.subheader(f"📋 Matches ({len(matches)})")
    
    # Stats summary
    processed = [process_match_oracle(m) for m in matches]
    approved = sum(1 for p in processed if p["final_status"] == "APPROVED")
    caution = sum(1 for p in processed if p["final_status"] == "CAUTION")
    rejected = sum(1 for p in processed if p["final_status"] == "REJECTED")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total", len(matches))
    with col2:
        st.metric("✅ Approved", approved, delta=f"{approved/len(matches)*100:.0f}%")
    with col3:
        st.metric("⚠️ Caution", caution)
    with col4:
        st.metric("❌ Rejected", rejected)
    
    st.divider()
    
    # Display matches by league/time
    for idx, match in enumerate(matches):
        oracle_result = process_match_oracle(match)
        
        with st.expander(f"⚽ {oracle_result['match']} - {match.get('league', 'Match')} - {oracle_result['final_status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Match Info**")
                st.write(f"Home: {match['home']} @ {match['home_odds']}")
                st.write(f"Draw: @ {match['draw_odds']}")
                st.write(f"Away: {match['away']} @ {match['away_odds']}")
                st.write(f"Kickoff: {match.get('time', 'TBD')}")
            
            with col2:
                st.markdown("**🔮 Oracle Verdict**")
                st.write(f"Verdict: {oracle_result['final_status']}")
                st.write(f"Confidence: {oracle_result['final_confidence']}")
                st.write(f"Selection: {oracle_result['selection']} @ {oracle_result['odds']}")
                st.write(f"Edge: {oracle_result['oracle']['edge']*100:.1f}%")
                st.write(f"Model Prob: {oracle_result['oracle']['model_prob']*100:.1f}%")
            
            st.divider()
            
            st.markdown("**📝 Decision Notes**")
            for note in oracle_result['decision_notes']:
                st.write(f"• {note}")
            
            # CSV for backend
            csv_line = f"{match['home']},{match['away']},{oracle_result['selection']},{match['home_odds']},{match['draw_odds']},{match['away_odds']},{match.get('league', 'Demo')}"
            st.code(f"📋 Copy to Backend: {csv_line}", language="csv")
else:
    st.info("👈 Select data source and click 'Fetch Matches' to see matches")
    
    # Show what's available in demo mode
    with st.expander("📺 Demo Mode Preview (Current Off-Season)"):
        st.markdown("""
        Since major leagues are on summer break (June-July), Demo Mode shows sample matches including:
        - **International Friendlies** (Germany vs France, England vs Spain)
        - **Club Friendlies** (Real Madrid vs AC Milan, Bayern vs Tottenham)
        - **World Cup Qualifiers** (USA vs Mexico, Japan vs South Korea)
        
        These matches are for demonstration purposes and show how the Oracle works.
        When the season starts (August), real matches will appear automatically.
        """)

st.divider()
st.caption(f"🔮 Match Oracle | {'Demo Mode - Off Season' if data_source == 'Demo Mode (Off-Season)' else 'Real API Mode'} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
