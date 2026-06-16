# streamlit_app.py - SINGLE FILE, CORRECT HIGHLIGHTLY ENDPOINTS
import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Match Oracle", page_icon="⚽", layout="wide")

# ========== SESSION STATE ==========
if "all_matches" not in st.session_state:
    st.session_state.all_matches = None
if "leg_data_cache" not in st.session_state:
    st.session_state.leg_data_cache = {}
if "selected_match" not in st.session_state:
    st.session_state.selected_match = None

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")

# Correct base URL from docs
BASE_URL = "https://soccer.highlightly.net"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "football-highlights-api.p.rapidapi.com",
}

# ========== API FUNCTIONS ==========

def api_get(path, params=None):
    """Generic GET. Returns (data, error_string)."""
    url = f"{BASE_URL}/{path}"
    try:
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=15)
        if r.status_code == 200:
            return r.json(), None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def unwrap(data):
    """Pull list/dict payload out of wrapper shapes."""
    if data is None:
        return None
    if isinstance(data, dict):
        # Try common wrapper keys first
        for key in ("data", "response", "groups"):
            if key in data:
                return data[key]
        return data
    return data  # already a list or primitive


def extract_team(match, side):
    """Handles homeTeam/awayTeam and teams.home/teams.away shapes."""
    key_direct = "homeTeam" if side == "home" else "awayTeam"
    return (
        match.get(key_direct)
        or match.get("teams", {}).get(side, {})
        or {}
    )


def extract_league(match):
    """Handles league and competition field names."""
    return match.get("league") or match.get("competition") or {}


def extract_score(match):
    """Handles scores/score/state shapes."""
    scores = match.get("scores") or match.get("score") or {}
    if isinstance(scores, dict):
        return scores.get("home"), scores.get("away")
    # some APIs nest inside state
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


def fetch_matches_by_date(date_str):
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
    data, err = api_get(f"matches/{match_id}")
    if err:
        return {"error": err}
    return data


def fetch_h2h(team_id_one, team_id_two):
    return api_get("head-2-head", params={
        "teamIdOne": team_id_one,
        "teamIdTwo": team_id_two,
    })


def fetch_standings(league_id, season):
    """Standings requires BOTH leagueId AND season."""
    return api_get("standings", params={
        "leagueId": league_id,
        "season": season,
    })


def fetch_last_five(team_id):
    """Correct endpoint: /last-five-games?teamId=X"""
    return api_get("last-five-games", params={"teamId": team_id})


def fetch_team_stats(team_id):
    """Correct endpoint: /teams/statistics/{id}?fromDate=YYYY-MM-DD"""
    # Season start — Jan 1 of current year is a safe fromDate
    from_date = f"{datetime.now().year}-01-01"
    return api_get(f"teams/statistics/{team_id}", params={"fromDate": from_date})


# ========== SIDEBAR ==========
with st.sidebar:
    st.header("Settings")

    date = st.date_input("Match Date", datetime.now())
    date_str = date.strftime("%Y-%m-%d")
    # Derive season from selected date
    selected_season = date.year if date.month >= 7 else date.year - 1

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
        if st.button("← Back to matches", use_container_width=True):
            st.session_state.selected_match = None
            st.rerun()

# ========== SEASON STATS VIEW ==========
if st.session_state.selected_match:
    sel = st.session_state.selected_match
    home_name  = sel["home_name"]
    away_name  = sel["away_name"]
    home_id    = sel["home_id"]
    away_id    = sel["away_id"]
    league_id  = sel["league_id"]
    league_name = sel["league_name"]
    season     = sel.get("season", selected_season)

    st.title("Season Stats")
    st.subheader(f"{home_name}  vs  {away_name}")
    st.caption(f"{league_name}  ·  Season {season}")

    if st.button("← Back to matches"):
        st.session_state.selected_match = None
        st.rerun()

    st.divider()

    # ──────────────────────────────────────────
    # H2H
    # ──────────────────────────────────────────
    st.header("Head to Head")

    if not home_id or not away_id:
        st.warning("Team IDs unavailable — cannot fetch H2H.")
    else:
        h2h_raw, h2h_err = fetch_h2h(home_id, away_id)
        if h2h_err:
            st.error(f"H2H failed: {h2h_err}")
        else:
            matches_list = h2h_raw if isinstance(h2h_raw, list) else []
            if not matches_list:
                st.info("No H2H history returned for these teams.")
            else:
                home_wins = away_wins = draws = 0
                rows = []
                for m in matches_list:
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

        with st.expander("Raw H2H"):
            st.json(h2h_raw if h2h_raw else {"note": "no response"})

    st.divider()

    # ──────────────────────────────────────────
    # STANDINGS
    # ──────────────────────────────────────────
    st.header("League Standings")

    if not league_id:
        st.info("No league ID — cannot fetch standings.")
    else:
        standings_raw, standings_err = fetch_standings(league_id, season)
        if standings_err:
            st.error(f"Standings failed: {standings_err}")
        else:
            # Response shape: {"groups": [...], "league": {...}}
            groups = standings_raw.get("groups", []) if isinstance(standings_raw, dict) else []
            table_rows = []
            if groups:
                # flatten all groups into one list
                for group in groups:
                    entries = group.get("standings", group.get("table", []))
                    if isinstance(entries, list):
                        table_rows.extend(entries)

            def find_in_table(rows, name, tid):
                for row in rows:
                    team = row.get("team", {})
                    if team.get("id") == tid or team.get("name") == name:
                        return row
                return None

            if table_rows:
                c1, c2 = st.columns(2)
                for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
                    with col:
                        st.subheader(tname)
                        row = find_in_table(table_rows, tname, tid)
                        if row:
                            st.write(f"**Position:** {row.get('position', 'N/A')}")
                            st.write(f"**Points:** {row.get('points', 'N/A')}")
                            played = row.get("played") or row.get("all", {}).get("played", "N/A")
                            won    = row.get("won")    or row.get("all", {}).get("win", "N/A")
                            drawn  = row.get("drawn")  or row.get("all", {}).get("draw", "N/A")
                            lost   = row.get("lost")   or row.get("all", {}).get("lose", "N/A")
                            st.write(f"Played: {played}  |  W {won}  D {drawn}  L {lost}")
                            gf = row.get("goalsFor",   row.get("goals", {}).get("for", "N/A"))
                            ga = row.get("goalsAgainst", row.get("goals", {}).get("against", "N/A"))
                            st.write(f"Goals: {gf} for / {ga} against")
                            form = row.get("form")
                            if form:
                                st.write(f"Form: {form}")
                        else:
                            st.write("Not found in standings.")
            else:
                st.info("Standings returned but no table entries found — see raw response.")

        with st.expander("Raw standings"):
            st.json(standings_raw if standings_raw else {"note": "no response"})

    st.divider()

    # ──────────────────────────────────────────
    # LAST FIVE GAMES
    # ──────────────────────────────────────────
    st.header("Last 5 Finished Games")

    c1, c2 = st.columns(2)
    for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
        with col:
            st.subheader(tname)
            if not tid:
                st.warning("No team ID.")
            else:
                last5_raw, last5_err = fetch_last_five(tid)
                if last5_err:
                    st.error(f"Failed: {last5_err}")
                elif not last5_raw:
                    st.info("No data returned.")
                else:
                    games = last5_raw if isinstance(last5_raw, list) else []
                    if not games:
                        st.info("No finished games found.")
                    else:
                        for m in games:
                            mh = extract_team(m, "home").get("name", "?")
                            ma = extract_team(m, "away").get("name", "?")
                            sh, sa = extract_score(m)
                            date_val = m.get("date", "")[:10]
                            score_str = f"{sh} - {sa}" if sh is not None else "vs"
                            # Highlight if this team won
                            result = ""
                            if sh is not None and sa is not None:
                                if (mh == tname and sh > sa) or (ma == tname and sa > sh):
                                    result = " ✅"
                                elif sh == sa:
                                    result = " ➖"
                                else:
                                    result = " ❌"
                            st.write(f"{date_val}  {mh} **{score_str}** {ma}{result}")

            with st.expander(f"Raw — {tname}"):
                st.json(last5_raw if "last5_raw" in dir() and last5_raw else {"note": "no response"})

    st.divider()

    # ──────────────────────────────────────────
    # TEAM SEASON STATISTICS
    # ──────────────────────────────────────────
    st.header("Team Season Statistics")

    c1, c2 = st.columns(2)
    for col, tname, tid in [(c1, home_name, home_id), (c2, away_name, away_id)]:
        with col:
            st.subheader(tname)
            if not tid:
                st.warning("No team ID.")
            else:
                stats_raw, stats_err = fetch_team_stats(tid)
                if stats_err:
                    st.error(f"Failed: {stats_err}")
                elif not stats_raw:
                    st.info("No stats returned.")
                else:
                    # Response is a list of per-league/season objects
                    stats_list = stats_raw if isinstance(stats_raw, list) else [stats_raw]
                    # Find the entry for the current league if possible
                    entry = next(
                        (s for s in stats_list if s.get("leagueId") == league_id),
                        stats_list[0] if stats_list else None
                    )
                    if entry:
                        st.write(f"**League:** {entry.get('leagueName', 'N/A')}  |  **Season:** {entry.get('season', 'N/A')}")
                        for scope in ("total", "home", "away"):
                            section = entry.get(scope, {})
                            if section:
                                st.write(f"**{scope.capitalize()}:**")
                                played = section.get("played", "N/A")
                                wins   = section.get("wins",   "N/A")
                                draws  = section.get("draws",  "N/A")
                                loses  = section.get("loses",  "N/A")
                                gf     = section.get("goalsScored",   section.get("goalsFor", "N/A"))
                                ga     = section.get("goalsConceded", section.get("goalsAgainst", "N/A"))
                                st.write(f"P {played}  W {wins}  D {draws}  L {loses}  |  GF {gf}  GA {ga}")
                    else:
                        st.info("No matching season entry — see raw response.")

                with st.expander(f"Raw stats — {tname}"):
                    st.json(stats_raw if stats_raw else {"note": "no response"})

    st.stop()


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

        with st.expander(f"{idx+1}. {home} vs {away}  —  {league}", expanded=False):
            status_obj = match.get("status") or match.get("state") or {}
            status_str = status_obj.get("long", status_obj.get("description", "Scheduled")) if isinstance(status_obj, dict) else str(status_obj)
            st.write(f"**Match ID:** {match_id}  |  **Status:** {status_str}")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("FETCH LEG DATA", key=f"leg_{match_id}_{idx}", use_container_width=True):
                    with st.spinner("Fetching..."):
                        leg = fetch_match_detail(match_id)
                        if leg:
                            st.session_state.leg_data_cache[match_id] = leg
                            st.success("Fetched")
                            st.rerun()
                        else:
                            st.error("Failed")

            with col_b:
                if st.button("VIEW SEASON STATS", key=f"stats_{match_id}_{idx}", use_container_width=True):
                    st.session_state.selected_match = {
                        "home_id":     home_id,
                        "away_id":     away_id,
                        "home_name":   home,
                        "away_name":   away,
                        "league_id":   league_id,
                        "league_name": league,
                        "match_id":    match_id,
                        "season":      selected_season,
                    }
                    st.rerun()

            with col_c:
                if st.button("RAW MATCH DATA", key=f"raw_{match_id}_{idx}", use_container_width=True):
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
                            st.write(f"{lg.get('name', 'N/A')}  —  {lg.get('country', 'N/A')}")

                        st_obj = actual.get("status") or actual.get("state") or {}
                        if isinstance(st_obj, dict) and (st_obj.get("long") or st_obj.get("description")):
                            st.markdown("**STATUS**")
                            st.write(st_obj.get("long") or st_obj.get("description", ""))

                        sh, sa = extract_score(actual)
                        if sh is not None:
                            st.markdown("**SCORES**")
                            st.write(f"Home: {sh}  —  Away: {sa}")

                        venue = actual.get("venue") or {}
                        if isinstance(venue, dict) and (venue.get("name") or venue.get("city")):
                            st.markdown("**VENUE**")
                            st.write(f"{venue.get('name', 'N/A')}  —  {venue.get('city', 'N/A')}")

                        with st.expander("Full leg data (raw)"):
                            st.json(leg_data)
                    else:
                        st.warning("No valid data structure in response.")
                        st.json(leg_data)

else:
    st.info("Click 'FETCH MATCHES' in the sidebar to load matches.")

st.divider()
st.caption(f"Match Oracle  ·  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
