# pages/1_Season_Stats.py - H2H AND SEASON STATS
import streamlit as st
import requests

st.set_page_config(page_title="Season Stats - Match Oracle", page_icon="📊", layout="wide")

API_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
API_HOST = "sports.highlightly.net"
BASE_URL = "https://sports.highlightly.net/football"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}


def api_get(path, params=None):
    """Generic GET against the Highlightly football API. Returns (data, error)."""
    url = f"{BASE_URL}/{path}"
    try:
        r = requests.get(url, headers=HEADERS, params=params or {}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data, None
        return None, f"HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)


def unwrap(data):
    """Pull the useful payload out of a {response: ...} / {data: ...} / list wrapper."""
    if data is None:
        return None
    if isinstance(data, dict):
        if "response" in data:
            return data["response"]
        if "data" in data:
            return data["data"]
        return data
    if isinstance(data, list):
        return data
    return data


# ---- Read context passed from the matches page ----
home_team = st.session_state.get("stats_home_team")
away_team = st.session_state.get("stats_away_team")
match_id = st.session_state.get("stats_match_id")
league_id = st.session_state.get("stats_league_id")
league_name = st.session_state.get("stats_league_name", "Unknown league")

if not home_team or not away_team:
    st.warning("No match selected. Go back to the matches list and choose a fixture first.")
    if st.button("Back to matches"):
        st.switch_page("streamlit_app.py")
    st.stop()

if st.button("Back to matches"):
    st.switch_page("streamlit_app.py")

st.title("Season Stats")
st.subheader(f"{home_team['name']} vs {away_team['name']}")
st.caption(f"{league_name} | Match ID: {match_id}")

st.divider()

# ================= H2H =================
st.header("Head to head")

h2h_data, h2h_err = api_get(
    "head-2-head",
    params={"teamIdOne": home_team.get("id"), "teamIdTwo": away_team.get("id")},
)

h2h_payload = unwrap(h2h_data)

if h2h_err:
    st.error(f"H2H request failed: {h2h_err}")
elif not h2h_payload:
    st.info(
        "No H2H data returned. This endpoint path may not match Highlightly's actual "
        "head-to-head route for your plan - check the API docs for the correct path "
        "(e.g. /football/head-2-head, /football/h2h, or similar)."
    )
else:
    matches_list = h2h_payload if isinstance(h2h_payload, list) else h2h_payload.get("matches", [])

    if not matches_list:
        st.info("H2H endpoint responded but returned no match history for these teams.")
    else:
        home_wins = away_wins = draws = 0
        rows = []
        for m in matches_list:
            mh = m.get("homeTeam", {}).get("name", "?")
            ma = m.get("awayTeam", {}).get("name", "?")
            sh = m.get("scores", {}).get("home")
            sa = m.get("scores", {}).get("away")
            date = m.get("date") or m.get("status", {}).get("date", "")

            if sh is not None and sa is not None:
                if sh == sa:
                    draws += 1
                elif (mh == home_team["name"] and sh > sa) or (ma == home_team["name"] and sa > sh):
                    home_wins += 1
                else:
                    away_wins += 1

            rows.append({"Date": date, "Home": mh, "Away": ma, "Score": f"{sh} - {sa}" if sh is not None else "N/A"})

        col1, col2, col3 = st.columns(3)
        col1.metric(f"{home_team['name']} wins", home_wins)
        col2.metric("Draws", draws)
        col3.metric(f"{away_team['name']} wins", away_wins)

        st.table(rows)

with st.expander("Raw H2H response"):
    st.json(h2h_data if h2h_data is not None else {"note": "no response"})

st.divider()

# ================= SEASON FORM / STANDINGS =================
st.header("Season form")

if not league_id:
    st.info("No league ID available for this fixture, cannot fetch standings.")
else:
    standings_data, standings_err = api_get(
        "standings",
        params={"leagueId": league_id},
    )
    standings_payload = unwrap(standings_data)

    if standings_err:
        st.error(f"Standings request failed: {standings_err}")
    elif not standings_payload:
        st.info(
            "No standings data returned. This endpoint path may not match Highlightly's "
            "actual standings route for your plan - check the API docs for the correct path "
            "(e.g. /football/standings)."
        )
    else:
        # Try to flatten standings table, structure varies by provider
        table_rows = standings_payload
        if isinstance(table_rows, dict):
            table_rows = table_rows.get("standings") or table_rows.get("table") or []

        if isinstance(table_rows, list) and table_rows and isinstance(table_rows[0], list):
            # some providers nest groups: [[team1, team2, ...]]
            table_rows = table_rows[0]

        def find_team_row(rows, team_name, team_id):
            for row in rows:
                team = row.get("team", row)
                if team.get("id") == team_id or team.get("name") == team_name:
                    return row
            return None

        if isinstance(table_rows, list):
            home_row = find_team_row(table_rows, home_team["name"], home_team.get("id"))
            away_row = find_team_row(table_rows, away_team["name"], away_team.get("id"))

            col1, col2 = st.columns(2)
            for col, team, row in [(col1, home_team, home_row), (col2, away_team, away_row)]:
                with col:
                    st.subheader(team["name"])
                    if row:
                        st.write(f"Position: {row.get('position', row.get('rank', 'N/A'))}")
                        st.write(f"Points: {row.get('points', 'N/A')}")
                        all_stats = row.get("all", row)
                        st.write(f"Played: {all_stats.get('played', row.get('played', 'N/A'))}")
                        st.write(f"Won: {all_stats.get('win', row.get('win', 'N/A'))}")
                        st.write(f"Drawn: {all_stats.get('draw', row.get('draw', 'N/A'))}")
                        st.write(f"Lost: {all_stats.get('lose', row.get('lose', 'N/A'))}")
                        form = row.get("form")
                        if form:
                            st.write(f"Form: {form}")
                    else:
                        st.write("Not found in standings table")
        else:
            st.info("Standings data returned in an unexpected shape - see raw response below.")

    with st.expander("Raw standings response"):
        st.json(standings_data if standings_data is not None else {"note": "no response"})

st.divider()

# ================= RECENT FORM (last N matches per team) =================
st.header("Recent matches")

col1, col2 = st.columns(2)

for col, team in [(col1, home_team), (col2, away_team)]:
    with col:
        st.subheader(team["name"])
        recent_data, recent_err = api_get(
            "matches",
            params={"teamId": team.get("id"), "limit": 5},
        )
        recent_payload = unwrap(recent_data)

        if recent_err:
            st.error(f"Request failed: {recent_err}")
        elif not recent_payload:
            st.info("No recent match data returned for this team.")
        else:
            recent_list = recent_payload if isinstance(recent_payload, list) else recent_payload.get("matches", [])
            if not recent_list:
                st.info("No recent matches found.")
            else:
                for m in recent_list[:5]:
                    mh = m.get("homeTeam", {}).get("name", "?")
                    ma = m.get("awayTeam", {}).get("name", "?")
                    sh = m.get("scores", {}).get("home")
                    sa = m.get("scores", {}).get("away")
                    st.write(f"{mh} {sh if sh is not None else '-'} : {sa if sa is not None else '-'} {ma}")

        with st.expander(f"Raw recent matches - {team['name']}"):
            st.json(recent_data if recent_data is not None else {"note": "no response"})
