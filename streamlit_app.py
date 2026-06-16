# streamlit_app.py - SINGLE FILE, ALL FIXES APPLIED
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# ========== SESSION STATE ==========
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "leg_data_cache" not in st.session_state:
    st.session_state.leg_data_cache = {}
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
API_HOST = "sports.highlightly.net"
BASE_URL = "https://sports.highlightly.net/football"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}

# ========== API FUNCTIONS ==========

def fetch_matches_by_date(date_str):
    try:
        r = requests.get(
            f"{BASE_URL}/matches",
            headers=HEADERS,
            params={"date": date_str},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                return data.get("response") or data.get("data") or []
            elif isinstance(data, list):
                return data
        return []
    except Exception as e:
        st.error(f"Error fetching matches: {e}")
        return []


def fetch_match_leg_data(match_id):
    try:
        r = requests.get(
            f"{BASE_URL}/matches/{match_id}",
            headers=HEADERS,
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
        return {"error": f"API returned status {r.status_code}", "status_code": r.status_code}
    except Exception as e:
        return {"error": str(e)}


def fetch_h2h(team_id_one, team_id_two):
    try:
        r = requests.get(
            f"{BASE_URL}/head-2-head",
            headers=HEADERS,
            params={"teamIdOne": team_id_one, "teamIdTwo": team_id_two},
            timeout=15
        )
        if r.status_code == 200:
            return r.json(), None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def fetch_standings(league_id):
    try:
        r = requests.get(
            f"{BASE_URL}/standings",
            headers=HEADERS,
            params={"leagueId": league_id},
            timeout=15
        )
        if r.status_code == 200:
            return r.json(), None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def fetch_team_recent(team_id):
    try:
        r = requests.get(
            f"{BASE_URL}/matches",
            headers=HEADERS,
            params={"teamId": team_id, "limit": 5},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data, None
            if isinstance(data, dict):
                return data.get("response") or data.get("data") or [], None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def fetch_team_stats(team_id, league_id):
    try:
        r = requests.get(
            f"{BASE_URL}/teams/{team_id}/statistics",
            headers=HEADERS,
            params={"league": league_id},
            timeout=15
        )
        if r.status_code == 200:
            return r.json(), None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


# ========== HELPERS ==========

def unwrap(data):
    """Pull the useful payload out of wrapper shapes."""
    if data is None:
        return None
    if isinstance(data, dict):
        return data.get("response") or data.get("data") or data
    if isinstance(data, list):
        return data
    return data


def extract_team(match, side):
    """
    Safely extract team dict from a match object.
    Handles both homeTeam/awayTeam and teams.home/teams.away shapes.
    side: 'home' or 'away'
    """
    key_direct = "homeTeam" if side == "home" else "awayTeam"
    key_nested = side  # 'home' or 'away' inside 'teams'
    return (
        match.get(key_direct)
        or match.get("teams", {}).get(key_nested, {})
        or {}
    )


def extract_league(match):
    """Handles both 'league' and 'competition' shapes."""
    return match.get("league") or match.get("competition") or {}


# ========== SIDEBAR ==========
with st.sidebar:
    st.header("Settings")

    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")

    league_filter = st.text_input("League contains", placeholder="Premier, Serie, La Liga")

    if st.button("FETCH MATCHES", type="primary", use_container_width=True):
        with st.spinner("Fetching matches..."):
            matches = fetch_matches_by_date(date_str)
            if matches:
                st.session_state.all_matches = matches
                st.session_state.leg_data_cache = {}
                st.session_state.selected_match = None
                st.success(f"Loaded {len(matches)} matches")
            else:
                st.session_state.all_matches = []
                st.warning("No matches found")
            st.rerun()

    if st.session_state.all_matches:
        st.info(f"{len(st.session_state.all_matches)} matches loaded")

    if st.session_state.selected_match:
        if st.button("Back to matches", use_container_width=True):
            st.session_state.selected_match = None
            st.rerun()

# ========== SEASON STATS VIEW ==========
if st.session_state.selected_match:
    selected = st.session_state.selected_match
    home_name = selected["home_name"]
    away_name = selected["away_name"]
    home_id   = selected["home_id"]
    away_id   = selected["away_id"]
    league_id = selected["league_id"]
    league_name = selected["league_name"]

    st.title("Season Stats")
    st.subheader(f"{home_name} vs {away_name}")
    st.caption(f"{league_name}")

    if st.button("← Back to matches"):
        st.session_state.selected_match = None
        st.rerun()

    st.divider()

    # ---- H2H ----
    st.header("Head to Head")

    if not home_id or not away_id:
        st.warning("Team IDs unavailable — cannot fetch H2H. Check raw match data below.")
    else:
        h2h_raw, h2h_err = fetch_h2h(home_id, away_id)
        if h2h_err:
            st.error(f"H2H request failed: {h2h_err}")
        else:
            h2h_payload = unwrap(h2h_raw)
            matches_list = h2h_payload if isinstance(h2h_payload, list) else (
                h2h_payload.get("matches", []) if isinstance(h2h_payload, dict) else []
            )
            if not matches_list:
                st.info("No H2H history returned by this API for these teams.")
            else:
                home_wins = away_wins = draws = 0
                rows = []
                for m in matches_list:
                    mh_team = extract_team(m, "home")
                    ma_team = extract_team(m, "away")
                    mh = mh_team.get("name", "?")
                    ma = ma_team.get("name", "?")
                    scores = m.get("scores") or m.get("score") or {}
                    sh = scores.get("home") if isinstance(scores, dict) else None
                    sa = scores.get("away") if isinstance(scores, dict) else None
                    date_val = m.get("date") or m.get("fixture", {}).get("date", "")

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
                        "Score": f"{sh} - {sa}" if sh is not None else "N/A"
                    })

                c1, c2, c3 = st.columns(3)
                c1.metric(f"{home_name} wins", home_wins)
                c2.metric("Draws", draws)
                c3.metric(f"{away_name} wins", away_wins)
                st.table(rows)

        with st.expander("Raw H2H response"):
            st.json(h2h_raw if h2h_raw is not None else {"note": "no response"})

    st.divider()

    # ---- STANDINGS ----
    st.header("League Standings")

    if not league_id:
        st.info("No league ID available for this fixture — cannot fetch standings.")
    else:
        standings_raw, standings_err = fetch_standings(league_id)
        if standings_err:
            st.error(f"Standings request failed: {standings_err}")
        else:
            standings_payload = unwrap(standings_raw)
            table_rows = standings_payload

            if isinstance(table_rows, dict):
                table_rows = (
                    table_rows.get("standings")
                    or table_rows.get("table")
                    or table_rows.get("response")
                    or []
                )
            if isinstance(table_rows, list) and table_rows and isinstance(table_rows[0], list):
                table_rows = table_rows[0]

            def find_team_in_table(rows, name, tid):
                for row in rows:
                    team = row.get("team", row)
                    if team.get("id") == tid or team.get("name") == name:
                        return row
                return None

            if isinstance(table_rows, list) and table_rows:
                c1, c2 = st.columns(2)
                for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
                    with col:
                        st.subheader(tname)
                        row = find_team_in_table(table_rows, tname, tid)
                        if row:
                            st.write(f"Position: {row.get('position', row.get('rank', 'N/A'))}")
                            st.write(f"Points: {row.get('points', 'N/A')}")
                            all_s = row.get("all", row)
                            st.write(f"Played: {all_s.get('played', row.get('played', 'N/A'))}")
                            st.write(f"Won:    {all_s.get('win', row.get('win', 'N/A'))}")
                            st.write(f"Drawn:  {all_s.get('draw', row.get('draw', 'N/A'))}")
                            st.write(f"Lost:   {all_s.get('lose', row.get('lose', 'N/A'))}")
                            form = row.get("form")
                            if form:
                                st.write(f"Form: {form}")
                        else:
                            st.write("Not found in standings table.")
            else:
                st.info("Standings returned in an unexpected shape — see raw response.")

        with st.expander("Raw standings response"):
            st.json(standings_raw if standings_raw is not None else {"note": "no response"})

    st.divider()

    # ---- RECENT FORM ----
    st.header("Recent Matches (last 5)")

    c1, c2 = st.columns(2)
    for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
        with col:
            st.subheader(tname)
            if not tid:
                st.warning("No team ID — cannot fetch recent matches.")
            else:
                recent_raw, recent_err = fetch_team_recent(tid)
                if recent_err:
                    st.error(f"Request failed: {recent_err}")
                elif not recent_raw:
                    st.info("No recent matches returned.")
                else:
                    recent_list = recent_raw if isinstance(recent_raw, list) else recent_raw.get("matches", [])
                    if not recent_list:
                        st.info("No recent matches found.")
                    else:
                        for m in recent_list[:5]:
                            mh = extract_team(m, "home").get("name", "?")
                            ma = extract_team(m, "away").get("name", "?")
                            scores = m.get("scores") or m.get("score") or {}
                            sh = scores.get("home", "-") if isinstance(scores, dict) else "-"
                            sa = scores.get("away", "-") if isinstance(scores, dict) else "-"
                            st.write(f"{mh} {sh} : {sa} {ma}")

            with st.expander(f"Raw recent — {tname}"):
                data_to_show = recent_raw if 'recent_raw' in dir() and recent_raw else {"note": "no response"}
                st.json(data_to_show)

    st.divider()

    # ---- TEAM SEASON STATS ----
    st.header("Team Season Statistics")

    c1, c2 = st.columns(2)
    for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
        with col:
            st.subheader(tname)
            if not tid or not league_id:
                st.warning("Missing team ID or league ID.")
            else:
                stats_raw, stats_err = fetch_team_stats(tid, league_id)
                if stats_err:
                    st.error(f"Request failed: {stats_err}")
                elif not stats_raw:
                    st.info("No stats returned.")
                else:
                    payload = unwrap(stats_raw)
                    if isinstance(payload, dict):
                        fixtures = payload.get("fixtures") or payload.get("matches") or {}
                        goals = payload.get("goals") or {}
                        form = payload.get("form")

                        if fixtures:
                            st.write("**Fixtures:**")
                            played = fixtures.get("played") or {}
                            wins   = fixtures.get("wins")   or {}
                            draws  = fixtures.get("draws")  or {}
                            loses  = fixtures.get("loses")  or {}
                            st.write(f"Played: {played.get('total', played) if isinstance(played, dict) else played}")
                            st.write(f"Wins:   {wins.get('total', wins) if isinstance(wins, dict) else wins}")
                            st.write(f"Draws:  {draws.get('total', draws) if isinstance(draws, dict) else draws}")
                            st.write(f"Losses: {loses.get('total', loses) if isinstance(loses, dict) else loses}")
                        if goals:
                            st.write("**Goals for:**")
                            gf = goals.get("for") or {}
                            st.write(f"Total: {gf.get('total', {}).get('total', 'N/A') if isinstance(gf.get('total'), dict) else gf.get('total', 'N/A')}")
                        if form:
                            st.write(f"**Form:** {form}")
                        if not fixtures and not goals and not form:
                            st.info("Stats returned but no recognisable fields — see raw response.")
                    else:
                        st.info("Unexpected stats shape — see raw response.")

                with st.expander(f"Raw stats — {tname}"):
                    st.json(stats_raw if stats_raw else {"note": "no response"})

    st.stop()  # Don't render matches list below when in stats view

# ========== MATCHES LIST ==========
st.title("⚽ MATCH ORACLE - LIVE MATCHES")

if st.session_state.all_matches:
    matches = st.session_state.all_matches

    if league_filter:
        matches = [
            m for m in matches
            if league_filter.lower() in extract_league(m).get("name", "").lower()
        ]

    st.subheader(f"MATCHES ({len(matches)})")

    for idx, match in enumerate(matches):
        home_team_obj = extract_team(match, "home")
        away_team_obj = extract_team(match, "away")
        league_obj    = extract_league(match)

        home      = home_team_obj.get("name", "Home")
        away      = away_team_obj.get("name", "Away")
        home_id   = home_team_obj.get("id")
        away_id   = away_team_obj.get("id")
        league    = league_obj.get("name", "Unknown")
        league_id = league_obj.get("id")
        match_id  = match.get("id")

        if not match_id:
            continue

        with st.expander(f"{idx+1}. {home} vs {away} - {league}", expanded=False):
            st.write(f"**Match ID:** {match_id}")
            status_obj = match.get("status") or {}
            st.write(f"**Status:** {status_obj.get('long', 'Scheduled') if isinstance(status_obj, dict) else status_obj}")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("FETCH LEG DATA", key=f"leg_{match_id}_{idx}", use_container_width=True):
                    with st.spinner("Fetching..."):
                        leg_data = fetch_match_leg_data(match_id)
                        if leg_data:
                            st.session_state.leg_data_cache[match_id] = leg_data
                            st.success("Fetched")
                            st.rerun()
                        else:
                            st.error("Failed")

            with col_b:
                if st.button("VIEW SEASON STATS", key=f"stats_{match_id}_{idx}", use_container_width=True):
                    st.session_state.selected_match = {
                        "home_id": home_id,
                        "away_id": away_id,
                        "home_name": home,
                        "away_name": away,
                        "league_id": league_id,
                        "league_name": league,
                        "match_id": match_id,
                    }
                    st.rerun()

            with col_c:
                if st.button("RAW DATA", key=f"raw_{match_id}_{idx}", use_container_width=True):
                    st.json(match)

            # Leg data display
            if match_id in st.session_state.leg_data_cache:
                st.divider()
                st.subheader("LEG DATA")
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
                            st.markdown("**HOME TEAM**")
                            ht = extract_team(actual, "home")
                            st.write(f"Name: {ht.get('name', 'N/A')}")
                            st.write(f"ID: {ht.get('id', 'N/A')}")
                        with c2:
                            st.markdown("**AWAY TEAM**")
                            at = extract_team(actual, "away")
                            st.write(f"Name: {at.get('name', 'N/A')}")
                            st.write(f"ID: {at.get('id', 'N/A')}")

                        lg = extract_league(actual)
                        if lg.get("name"):
                            st.markdown("**LEAGUE**")
                            st.write(f"Name: {lg.get('name', 'N/A')}")
                            st.write(f"Country: {lg.get('country', 'N/A')}")

                        st_obj = actual.get("status") or {}
                        if isinstance(st_obj, dict) and (st_obj.get("long") or st_obj.get("short")):
                            st.markdown("**STATUS**")
                            st.write(f"{st_obj.get('long', '')}  ({st_obj.get('short', '')})")

                        scores = actual.get("scores") or actual.get("score") or {}
                        if isinstance(scores, dict) and (scores.get("home") is not None):
                            st.markdown("**SCORES**")
                            st.write(f"Home: {scores.get('home')}  Away: {scores.get('away')}")

                        venue = actual.get("venue") or {}
                        if isinstance(venue, dict) and (venue.get("name") or venue.get("city")):
                            st.markdown("**VENUE**")
                            st.write(f"{venue.get('name', 'N/A')} — {venue.get('city', 'N/A')}")

                        with st.expander("Raw API Response"):
                            st.json(leg_data)
                    else:
                        st.warning("No valid data structure in response")
                        st.json(leg_data)

else:
    st.title("⚽ MATCH ORACLE - LIVE MATCHES")
    st.info("Click 'FETCH MATCHES' in the sidebar to load matches")

st.divider()
st.caption(f"Match Oracle | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
