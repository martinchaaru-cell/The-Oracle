# streamlit_app.py - Refined with Replit Backend Integration
import streamlit as st
import requests
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# ========== CONFIGURATION ==========
# Get your Replit backend URL (from secrets or environment)
REPLIT_BACKEND_URL = st.secrets.get("REPLIT_BACKEND_URL", "https://your-replit-app.replit.app")
HIGHLIGHTLY_API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

# Highlightly API config
BASE_URL = "https://soccer.highlightly.net"
HEADERS = {
    "x-rapidapi-key": HIGHLIGHTLY_API_KEY,
    "x-rapidapi-host": "football-highlights-api.p.rapidapi.com",
}

# ========== SESSION STATE ==========
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "leg_data_cache" not in st.session_state:
    st.session_state.leg_data_cache = {}
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None
if "processed_results" not in st.session_state:
    st.session_state.processed_results = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# ========== API FUNCTIONS ==========

def api_get(path, params=None):
    """Generic GET for Highlightly API"""
    if not HIGHLIGHTLY_API_KEY:
        return None, "API key missing"
    url = f"{BASE_URL}/{path}"
    try:
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=15)
        if r.status_code == 200:
            return r.json(), None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def fetch_matches_by_date(date_str):
    """Fetch matches from Highlightly"""
    data, err = api_get("matches", params={"date": date_str})
    if err:
        st.error(f"Error fetching matches: {err}")
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("data") or data.get("response") or []
    return []


def fetch_match_detail(match_id):
    """Fetch detailed match data"""
    data, err = api_get(f"matches/{match_id}")
    if err:
        return {"error": err}
    return data


def fetch_h2h(team_id_one, team_id_two):
    """Fetch head-to-head data"""
    return api_get("head-2-head", params={
        "teamIdOne": team_id_one,
        "teamIdTwo": team_id_two,
    })


def fetch_standings(league_id, season):
    """Fetch league standings"""
    return api_get("standings", params={
        "leagueId": league_id,
        "season": season,
    })


def fetch_last_five(team_id):
    """Fetch last 5 games for a team"""
    return api_get("last-five-games", params={"teamId": team_id})


def fetch_team_stats(team_id):
    """Fetch team statistics"""
    from_date = f"{datetime.now().year}-01-01"
    return api_get(f"teams/statistics/{team_id}", params={"fromDate": from_date})


def extract_team(match, side):
    """Extract team data from match"""
    key_direct = "homeTeam" if side == "home" else "awayTeam"
    return (
        match.get(key_direct)
        or match.get("teams", {}).get(side, {})
        or {}
    )


def extract_league(match):
    """Extract league data from match"""
    return match.get("league") or match.get("competition") or {}


def extract_score(match):
    """Extract score from match"""
    scores = match.get("scores") or match.get("score") or {}
    if isinstance(scores, dict):
        return scores.get("home"), scores.get("away")
    state = match.get("state") or {}
    if isinstance(state, dict):
        score_str = state.get("score", "")
        if " - " in str(score_str):
            parts = str(score_str).split(" - ")
            try:
                return int(parts[0]), int(parts[1])
            except Exception:
                pass
    return None, None


# ========== REPLIT BACKEND FUNCTIONS ==========

def check_backend_health():
    """Check if Replit backend is online"""
    try:
        response = requests.get(f"{REPLIT_BACKEND_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def send_to_replit_backend(matches, date_str):
    """Send matches to Replit backend for processing through 35 modules"""
    if not matches:
        return None
    
    # Convert matches to CSV format that backend expects
    csv_lines = []
    for match in matches:
        home = match.get("homeTeam", {}).get("name", "")
        away = match.get("awayTeam", {}).get("name", "")
        league = match.get("league", {}).get("name", "")
        
        if home and away:
            # Extract odds from match
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
            
            # Determine selection (favorite)
            selection = home if home_odds < away_odds else away
            csv_lines.append(f"{home},{away},{selection},{home_odds},{draw_odds},{away_odds},{league}")
    
    if not csv_lines:
        return None
    
    content = "\n".join(csv_lines)
    
    try:
        # Start upload scan on Replit backend
        response = requests.post(
            f"{REPLIT_BACKEND_URL}/api/upload",
            json={"content": content, "league": "Custom"},
            timeout=30
        )
        
        if response.status_code == 200:
            # Poll for results
            time.sleep(3)
            status_response = requests.get(f"{REPLIT_BACKEND_URL}/api/upload-status", timeout=10)
            if status_response.status_code == 200:
                return status_response.json().get("results", {})
    except Exception as e:
        st.error(f"Backend error: {e}")
    
    return None


# ========== SIDEBAR ==========
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Backend status
    backend_online = check_backend_health()
    if backend_online:
        st.success("✅ Replit Backend Connected")
    else:
        st.warning("⚠️ Replit Backend Unavailable")
    
    st.divider()
    
    date = st.date_input("📅 Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    selected_season = date.year if date.month >= 7 else date.year - 1
    
    league_filter = st.text_input("🔍 Filter by League", placeholder="Premier, Serie, La Liga")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 FETCH MATCHES", type="primary", use_container_width=True):
            with st.spinner("Fetching matches..."):
                matches = fetch_matches_by_date(date_str)
                if matches:
                    st.session_state.all_matches = matches
                    st.session_state.leg_data_cache = {}
                    st.session_state.selected_match = None
                    st.session_state.processed_results = None
                    st.success(f"✅ Loaded {len(matches)} matches")
                else:
                    st.session_state.all_matches = []
                    st.warning("⚠️ No matches found")
                st.rerun()
    
    with col2:
        if st.button("⚙️ PROCESS WITH BACKEND", use_container_width=True):
            if st.session_state.all_matches:
                st.session_state.processing = True
                with st.spinner("Sending to Replit backend for full forensic analysis..."):
                    results = send_to_replit_backend(st.session_state.all_matches, date_str)
                    if results:
                        st.session_state.processed_results = results
                        st.success("✅ Processing complete!")
                        st.balloons()
                    else:
                        st.error("❌ Processing failed")
                st.session_state.processing = False
                st.rerun()
            else:
                st.warning("⚠️ Fetch matches first")
    
    st.divider()
    
    if st.session_state.all_matches:
        st.info(f"📊 {len(st.session_state.all_matches)} matches loaded")
    
    if st.session_state.processed_results:
        totals = st.session_state.processed_results.get("totals", {})
        st.success(f"✅ Approved: {totals.get('approved', 0)}")
        st.warning(f"⚠️ Caution: {totals.get('caution', 0)}")
        st.error(f"❌ Rejected: {totals.get('rejected', 0)}")
    
    if st.session_state.selected_match:
        if st.button("← Back to matches", use_container_width=True):
            st.session_state.selected_match = None
            st.rerun()


# ========== SEASON STATS VIEW ==========
if st.session_state.selected_match:
    sel = st.session_state.selected_match
    home_name = sel["home_name"]
    away_name = sel["away_name"]
    home_id = sel["home_id"]
    away_id = sel["away_id"]
    league_id = sel["league_id"]
    league_name = sel["league_name"]
    season = sel.get("season", selected_season)
    
    st.title("📊 Season Stats")
    st.subheader(f"{home_name}  vs  {away_name}")
    st.caption(f"{league_name}  ·  Season {season}")
    
    # H2H Section
    st.header("🔄 Head to Head")
    if home_id and away_id:
        h2h_raw, h2h_err = fetch_h2h(home_id, away_id)
        if not h2h_err and h2h_raw:
            matches_list = h2h_raw if isinstance(h2h_raw, list) else []
            if matches_list:
                home_wins = away_wins = draws = 0
                rows = []
                for m in matches_list[:10]:
                    mh = extract_team(m, "home").get("name", "?")
                    ma = extract_team(m, "away").get("name", "?")
                    sh, sa = extract_score(m)
                    date_val = m.get("date", "")[:10]
                    
                    if sh is not None and sa is not None:
                        if sh == sa:
                            draws += 1
                        elif (mh == home_name and sh > sa) or (ma == home_name and sa > sh):
                            home_wins += 1
                        else:
                            away_wins += 1
                    
                    rows.append({
                        "Date": date_val,
                        "Home": mh,
                        "Away": ma,
                        "Score": f"{sh} - {sa}" if sh is not None else "N/A",
                    })
                
                c1, c2, c3 = st.columns(3)
                c1.metric(f"{home_name} wins", home_wins)
                c2.metric("Draws", draws)
                c3.metric(f"{away_name} wins", away_wins)
                st.table(rows)
    
    # Standings Section
    st.header("🏆 League Standings")
    if league_id:
        standings_raw, standings_err = fetch_standings(league_id, season)
        if not standings_err and standings_raw:
            groups = standings_raw.get("groups", []) if isinstance(standings_raw, dict) else []
            table_rows = []
            for group in groups:
                entries = group.get("standings", group.get("table", []))
                if isinstance(entries, list):
                    table_rows.extend(entries)
            
            if table_rows:
                def find_team(rows, name, tid):
                    for row in rows:
                        team = row.get("team", {})
                        if team.get("id") == tid or team.get("name") == name:
                            return row
                    return None
                
                c1, c2 = st.columns(2)
                for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
                    with col:
                        st.subheader(tname)
                        row = find_team(table_rows, tname, tid)
                        if row:
                            st.write(f"**Position:** {row.get('position', 'N/A')}")
                            st.write(f"**Points:** {row.get('points', 'N/A')}")
                            played = row.get("played") or row.get("all", {}).get("played", "N/A")
                            won = row.get("won") or row.get("all", {}).get("win", "N/A")
                            drawn = row.get("drawn") or row.get("all", {}).get("draw", "N/A")
                            lost = row.get("lost") or row.get("all", {}).get("lose", "N/A")
                            st.write(f"P {played}  W {won}  D {drawn}  L {lost}")
    
    # Last 5 Games
    st.header("📈 Last 5 Games")
    for tname, tid in [(home_name, home_id), (away_name, away_id)]:
        if tid:
            st.subheader(tname)
            last5_raw, last5_err = fetch_last_five(tid)
            if not last5_err and last5_raw:
                games = last5_raw if isinstance(last5_raw, list) else []
                for m in games[:5]:
                    mh = extract_team(m, "home").get("name", "?")
                    ma = extract_team(m, "away").get("name", "?")
                    sh, sa = extract_score(m)
                    date_val = m.get("date", "")[:10]
                    score_str = f"{sh} - {sa}" if sh is not None else "vs"
                    result = ""
                    if sh is not None and sa is not None:
                        if (mh == tname and sh > sa) or (ma == tname and sa > sh):
                            result = " ✅"
                        elif sh == sa:
                            result = " ➖"
                        else:
                            result = " ❌"
                    st.write(f"{date_val}  {mh} **{score_str}** {ma}{result}")
    
    st.stop()


# ========== MATCHES LIST ==========
st.title("⚽ MATCH ORACLE - LIVE MATCHES")

if st.session_state.processed_results:
    results = st.session_state.processed_results
    
    # Show processed results summary
    totals = results.get("totals", {})
    st.subheader("📊 Oracle Verdicts")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total", totals.get("total", 0))
    c2.metric("✅ Approved", totals.get("approved", 0))
    c3.metric("⚠️ Caution", totals.get("caution", 0))
    c4.metric("❌ Rejected", totals.get("rejected", 0))
    
    st.divider()
    
    # Show verdicts by league
    for league_data in results.get("leagues", []):
        st.subheader(f"🏆 {league_data.get('league', 'Unknown')}")
        for match in league_data.get("matches", []):
            verdict = match.get("final_status", "PENDING")
            if verdict == "APPROVED":
                st.success(f"✅ {match.get('match', '?')} - {verdict}")
            elif verdict == "CAUTION":
                st.warning(f"⚠️ {match.get('match', '?')} - {verdict}")
            else:
                st.error(f"❌ {match.get('match', '?')} - {verdict}")
    
    if st.button("🔄 Clear Results"):
        st.session_state.processed_results = None
        st.rerun()
    
    st.divider()


if st.session_state.all_matches:
    matches = st.session_state.all_matches
    
    if league_filter:
        matches = [m for m in matches if league_filter.lower() in extract_league(m).get("name", "").lower()]
    
    st.subheader(f"📋 MATCHES ({len(matches)})")
    
    for idx, match in enumerate(matches):
        home_team_obj = extract_team(match, "home")
        away_team_obj = extract_team(match, "away")
        league_obj = extract_league(match)
        
        home = home_team_obj.get("name", "Home")
        away = away_team_obj.get("name", "Away")
        home_id = home_team_obj.get("id")
        away_id = away_team_obj.get("id")
        league = league_obj.get("name", "Unknown")
        league_id = league_obj.get("id")
        match_id = match.get("id")
        
        if not match_id:
            continue
        
        with st.expander(f"{idx+1}. {home} vs {away}  —  {league}", expanded=False):
            status_obj = match.get("status") or match.get("state") or {}
            status_str = status_obj.get("long", status_obj.get("description", "Scheduled")) if isinstance(status_obj, dict) else str(status_obj)
            st.write(f"**Match ID:** {match_id}  |  **Status:** {status_str}")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("📊 FETCH LEG DATA", key=f"leg_{match_id}_{idx}", use_container_width=True):
                    with st.spinner("Fetching..."):
                        leg = fetch_match_detail(match_id)
                        if leg:
                            st.session_state.leg_data_cache[match_id] = leg
                            st.success("✅ Fetched")
                            st.rerun()
                        else:
                            st.error("❌ Failed")
            
            with col_b:
                if st.button("📈 SEASON STATS", key=f"stats_{match_id}_{idx}", use_container_width=True):
                    st.session_state.selected_match = {
                        "home_id": home_id,
                        "away_id": away_id,
                        "home_name": home,
                        "away_name": away,
                        "league_id": league_id,
                        "league_name": league,
                        "match_id": match_id,
                        "season": selected_season,
                    }
                    st.rerun()
            
            with col_c:
                if st.button("📄 RAW DATA", key=f"raw_{match_id}_{idx}", use_container_width=True):
                    st.json(match)
            
            # Leg data display
            if match_id in st.session_state.leg_data_cache:
                st.divider()
                st.subheader("📋 LEG DATA")
                leg_data = st.session_state.leg_data_cache[match_id]
                
                if isinstance(leg_data, dict) and "error" in leg_data:
                    st.error(f"API Error: {leg_data['error']}")
                else:
                    actual = leg_data
                    if isinstance(leg_data, dict):
                        actual = leg_data.get("response") or leg_data.get("data") or leg_data
                    if isinstance(actual, list):
                        actual = actual[0] if actual else None
                    
                    if actual and isinstance(actual, dict):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**🏠 HOME TEAM**")
                            ht = extract_team(actual, "home")
                            st.write(f"Name: {ht.get('name', 'N/A')}")
                            st.write(f"ID: {ht.get('id', 'N/A')}")
                        with c2:
                            st.markdown("**✈️ AWAY TEAM**")
                            at = extract_team(actual, "away")
                            st.write(f"Name: {at.get('name', 'N/A')}")
                            st.write(f"ID: {at.get('id', 'N/A')}")
                        
                        lg = extract_league(actual)
                        if lg.get("name"):
                            st.markdown("**🏆 LEAGUE**")
                            st.write(f"{lg.get('name', 'N/A')}  —  {lg.get('country', 'N/A')}")
                        
                        sh, sa = extract_score(actual)
                        if sh is not None:
                            st.markdown("**📊 SCORE**")
                            st.write(f"Home: {sh}  —  Away: {sa}")
                        
                        with st.expander("📄 Full leg data (raw)"):
                            st.json(leg_data)
                    else:
                        st.warning("No valid data structure in response.")
                        st.json(leg_data)

else:
    st.info("👈 Click 'FETCH MATCHES' in the sidebar to load matches.")

st.divider()
st.caption(f"🔮 Match Oracle  ·  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
