"""
Match Oracle - Streamlit Frontend
Supports both direct Highlightly API and Backend API
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import json

# ============================================
# CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Match Oracle - Football Intelligence",
    page_icon="🔮",
    layout="wide"
)

# Get API keys from secrets
HIGHLIGHTLY_KEY = st.secrets.get("HIGHLIGHTLY_API_KEY", "")
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://oracle-backend-1-vryo.onrender.com")

# League configuration
LEAGUES = [
    {"key": "PREMIER_LEAGUE", "name": "Premier League", "id": 39, "country": "England"},
    {"key": "LA_LIGA", "name": "La Liga", "id": 140, "country": "Spain"},
    {"key": "BUNDESLIGA", "name": "Bundesliga", "id": 78, "country": "Germany"},
    {"key": "SERIE_A", "name": "Serie A", "id": 135, "country": "Italy"},
    {"key": "LIGUE_1", "name": "Ligue 1", "id": 61, "country": "France"},
    {"key": "EREDIVISIE", "name": "Eredivisie", "id": 88, "country": "Netherlands"},
    {"key": "PRIMEIRA_LIGA", "name": "Primeira Liga", "id": 94, "country": "Portugal"},
    {"key": "BRAZIL_SERIE_A", "name": "Brasileirão", "id": 71, "country": "Brazil"},
    {"key": "J1_LEAGUE", "name": "J1 League", "id": 292, "country": "Japan"},
]

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "mode" not in st.session_state:
    st.session_state.mode = "backend"  # "backend" or "highlightly"
if "scan_results" not in st.session_state:
    st.session_state.scan_results = None
if "highlightly_matches" not in st.session_state:
    st.session_state.highlightly_matches = None
if "scan_running" not in st.session_state:
    st.session_state.scan_running = False
if "selected_league_ids" not in st.session_state:
    st.session_state.selected_league_ids = []

# ============================================
# HIGHLIGHTLY API FUNCTIONS
# ============================================

class HighlightlyClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://sports.highlightly.net"
        self.headers = {"x-rapidapi-key": api_key}
    
    def get_matches(self, date=None, league_id=None, limit=100):
        url = f"{self.base_url}/football/matches"
        params = {"limit": limit}
        if date:
            params["date"] = date
        if league_id:
            params["leagueId"] = league_id
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", []) if isinstance(data, dict) else data
        except Exception as e:
            st.error(f"Highlightly API error: {e}")
        return []
    
    def get_team_info(self, team_id):
        url = f"{self.base_url}/football/teams/{team_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data[0] if isinstance(data, list) and data else None
        except Exception as e:
            st.error(f"Error fetching team info: {e}")
        return None
    
    def get_head_to_head(self, team_id_1, team_id_2):
        url = f"{self.base_url}/football/head-2-head"
        params = {"teamIdOne": team_id_1, "teamIdTwo": team_id_2}
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else data.get("data", [])
        except Exception as e:
            st.error(f"Error fetching H2H: {e}")
        return []


# ============================================
# BACKEND API FUNCTIONS
# ============================================

def backend_start_scan(leagues, date):
    """Start scan on backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/scan",
            json={
                "leagues": leagues,
                "target_date": date.strftime("%Y-%m-%d"),
                "season": 2026
            },
            timeout=10
        )
        return response.status_code == 200 and response.json().get("status") == "started"
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return False

def backend_get_status():
    """Get scan status from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/status", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        pass
    return None

def backend_upload_matches(content):
    """Upload custom matches to backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/upload",
            json={"content": content, "league": "Custom"},
            timeout=10
        )
        return response.status_code == 200 and response.json().get("status") == "started"
    except Exception as e:
        st.error(f"Upload error: {e}")
        return False


# ============================================
# UI COMPONENTS
# ============================================

# Header
st.title("🔮 Match Oracle - Football Intelligence")

# Mode selector
col_mode1, col_mode2, col_mode3 = st.columns([1, 2, 1])
with col_mode1:
    mode = st.radio(
        "API Mode",
        ["Backend (Full Pipeline)", "Highlightly (Raw Data)"],
        horizontal=True,
        index=0 if st.session_state.mode == "backend" else 1
    )
    st.session_state.mode = "backend" if "Backend" in mode else "highlightly"

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    if st.session_state.mode == "backend":
        st.info(f"🔗 Backend: {BACKEND_URL}")
        backend_status = backend_get_status()
        if backend_status:
            st.success(f"✅ Backend Online")
        else:
            st.warning("⚠️ Backend may be starting up...")
    
    st.subheader("📅 Match Date")
    match_date = st.date_input("Date", datetime.now())
    
    st.subheader("🏆 Select Leagues")
    selected_leagues = []
    for league in LEAGUES:
        if st.checkbox(league["name"], key=f"league_{league['key']}"):
            selected_leagues.append(league["key"])
            if league["id"] not in st.session_state.selected_league_ids:
                st.session_state.selected_league_ids.append(league["id"])
    
    st.session_state.selected_league_ids = [
        l["id"] for l in LEAGUES if l["key"] in selected_leagues
    ]
    
    # Run button
    if selected_leagues:
        if st.button("🚀 Run Scan", type="primary", use_container_width=True):
            if st.session_state.mode == "backend":
                if backend_start_scan(selected_leagues, match_date):
                    st.session_state.scan_running = True
                    st.session_state.scan_results = None
                    st.success("Scan started!")
                    st.rerun()
                else:
                    st.error("Failed to start scan")
            else:
                st.session_state.scan_running = True
                st.rerun()
    
    # Upload section
    st.divider()
    st.subheader("📤 Upload Matches")
    upload_text = st.text_area(
        "CSV Format: Home,Away,Selection,HomeOdds,DrawOdds,AwayOdds,League",
        height=120,
        placeholder="Manchester City,Arsenal,Man City,1.85,3.40,4.20,Premier League"
    )
    
    if st.button("🔍 Scan Upload", use_container_width=True):
        if upload_text.strip():
            if st.session_state.mode == "backend":
                if backend_upload_matches(upload_text):
                    st.session_state.scan_running = True
                    st.success("Upload scan started!")
                    st.rerun()
            else:
                st.info("Upload scanning is only available in Backend mode")
    
    # API Status
    st.divider()
    if st.session_state.mode == "highlightly":
        if HIGHLIGHTLY_KEY:
            st.success("✅ Highlightly API Key loaded")
        else:
            st.error("❌ Highlightly API Key missing")


# ============================================
# MAIN CONTENT - HIGHLIGHTLY MODE
# ============================================

if st.session_state.mode == "highlightly":
    st.subheader("🏟️ Raw Match Data from Highlightly API")
    
    if st.session_state.scan_running and not st.session_state.highlightly_matches:
        with st.spinner("Fetching matches from Highlightly..."):
            client = HighlightlyClient(HIGHLIGHTLY_KEY)
            all_matches = []
            
            progress_bar = st.progress(0)
            for i, league_id in enumerate(st.session_state.selected_league_ids):
                matches = client.get_matches(
                    date=match_date.strftime("%Y-%m-%d"),
                    league_id=league_id,
                    limit=50
                )
                all_matches.extend(matches)
                progress_bar.progress((i + 1) / max(len(st.session_state.selected_league_ids), 1))
            
            st.session_state.highlightly_matches = all_matches
            st.session_state.scan_running = False
    
    # Display matches
    if st.session_state.highlightly_matches:
        matches = st.session_state.highlightly_matches
        st.success(f"✅ Found {len(matches)} matches on {match_date}")
        
        # Search filter
        search = st.text_input("🔍 Filter matches", placeholder="Team name...")
        
        filtered = matches
        if search:
            filtered = [m for m in matches if 
                       search.lower() in m.get("homeTeam", {}).get("name", "").lower() or
                       search.lower() in m.get("awayTeam", {}).get("name", "").lower()]
        
        for match in filtered[:30]:
            home = match.get("homeTeam", {}).get("name", "?")
            away = match.get("awayTeam", {}).get("name", "?")
            league = match.get("league", {}).get("name", "?")
            state = match.get("state", {}).get("description", "Unknown")
            score = match.get("state", {}).get("score", {}).get("current", "vs")
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 3, 2, 1])
                with col1:
                    st.markdown(f"**{home}**")
                with col2:
                    st.markdown(f"`{score}`")
                with col3:
                    st.markdown(f"**{away}**")
                with col4:
                    st.caption(f"{league}")
                with col5:
                    status_color = "🟢" if state == "Not started" else "🟡" if state == "In progress" else "⚫"
                    st.caption(f"{status_color} {state}")
                
                # Expandable details
                with st.expander("📊 Match Details"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Home Team Info**")
                        home_id = match.get("homeTeam", {}).get("id")
                        if home_id:
                            team_info = client.get_team_info(home_id)
                            if team_info:
                                st.write(f"Name: {team_info.get('name')}")
                                st.write(f"ID: {team_info.get('id')}")
                    
                    with col_b:
                        st.markdown("**Away Team Info**")
                        away_id = match.get("awayTeam", {}).get("id")
                        if away_id:
                            team_info = client.get_team_info(away_id)
                            if team_info:
                                st.write(f"Name: {team_info.get('name')}")
                                st.write(f"ID: {team_info.get('id')}")
                    
                    # Show CSV format for easy upload to backend
                    st.markdown("**📋 Copy to Backend (CSV format):**")
                    csv_line = f"{home},{away},{home},2.00,3.25,3.50,{league}"
                    st.code(csv_line, language="csv")
                
                st.divider()
        
        if len(matches) > 30:
            st.info(f"Showing 30 of {len(matches)} matches")
        
        # Action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Refresh"):
                st.session_state.highlightly_matches = None
                st.session_state.scan_running = True
                st.rerun()
        
        with col_b:
            csv_export = "\n".join([
                f"{m.get('homeTeam', {}).get('name', '')},{m.get('awayTeam', {}).get('name', '')},{m.get('homeTeam', {}).get('name', '')},2.00,3.25,3.50,{m.get('league', {}).get('name', '')}"
                for m in matches[:50]
            ])
            st.download_button(
                "📥 Export to CSV",
                csv_export,
                file_name=f"matches_{match_date}.csv",
                mime="text/csv"
            )


# ============================================
# MAIN CONTENT - BACKEND MODE
# ============================================

else:
    # Poll for results in backend mode
    if st.session_state.scan_running:
        status = backend_get_status()
        
        if status:
            # Show log
            if status.get("log"):
                with st.expander("📋 Scan Log"):
                    for log_entry in status["log"][-20:]:
                        st.code(log_entry, language="text")
            
            # Check if complete
            if not status.get("running", True):
                st.session_state.scan_running = False
                st.session_state.scan_results = status.get("results", {})
                st.success("✅ Scan complete!")
                st.rerun()
            else:
                st.info("⏳ Scan in progress...")
                st.caption("Refreshing in 3 seconds...")
                import time
                time.sleep(3)
                st.rerun()
    
    # Display backend results
    if st.session_state.scan_results:
        results = st.session_state.scan_results
        totals = results.get("totals", {})
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Scanned", totals.get("total", 0))
        with col2:
            st.metric("✅ Approved", totals.get("approved", 0), delta=None, delta_color="normal")
        with col3:
            st.metric("⚠️ Caution", totals.get("caution", 0))
        with col4:
            st.metric("❌ Rejected", totals.get("rejected", 0))
        
        st.divider()
        
        # Display matches by league
        leagues_data = results.get("leagues", [])
        
        if leagues_data:
            league_tabs = st.tabs([l.get("league", "Unknown") for l in leagues_data])
            
            for tab, league_data in zip(league_tabs, leagues_data):
                with tab:
                    matches = league_data.get("matches", [])
                    st.write(f"**{len(matches)} matches**")
                    
                    for match in matches:
                        home = match.get("match", "").split(" vs ")[0] if " vs " in match.get("match", "") else "?"
                        away = match.get("match", "").split(" vs ")[1] if " vs " in match.get("match", "") else "?"
                        status = match.get("final_status", "PENDING")
                        
                        # Status color
                        if status == "APPROVED":
                            status_badge = "🟢 APPROVED"
                        elif status == "CAUTION":
                            status_badge = "🟡 CAUTION"
                        elif status == "REJECTED":
                            status_badge = "🔴 REJECTED"
                        else:
                            status_badge = "⚪ PENDING"
                        
                        with st.expander(f"{home} vs {away} - {status_badge}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📊 Match Info**")
                                st.write(f"Date: {match.get('match_date', 'N/A')}")
                                st.write(f"Kickoff: {match.get('kickoff_time', 'N/A')}")
                                st.write(f"Selection: {match.get('selection', 'N/A')} @ {match.get('odds', 'N/A')}")
                                
                                st.markdown("**🎲 Odds**")
                                st.write(f"Home: {match.get('home_odds', '-')}")
                                st.write(f"Draw: {match.get('draw_odds', '-')}")
                                st.write(f"Away: {match.get('away_odds', '-')}")
                            
                            with col2:
                                st.markdown("**🔮 Oracle Verdict**")
                                oracle = match.get("oracle", {})
                                st.write(f"Model Prob: {oracle.get('model_prob', 0)*100:.1f}%")
                                st.write(f"Edge: {oracle.get('edge', 0)*100:.1f}%")
                                st.write(f"Failure Score: {oracle.get('failure_score', 0)}")
                                st.write(f"Pre-filter: {'✅ PASS' if oracle.get('pre_filter_passed') else '❌ FAIL'}")
                            
                            # Forensic report tabs
                            tab1, tab2, tab3, tab4 = st.tabs(["🏆 M4 Pre-filter", "🔄 M8 Dual Pattern", "⚠️ M9 Underdog", "📝 Decision Notes"])
                            
                            with tab1:
                                m4 = match.get("m4_prefilter", {})
                                st.write(f"Passed: {m4.get('passed', False)}")
                                st.write(f"Checks Passed: {m4.get('checks_passed', 0)}/8")
                                for detail in m4.get("details", []):
                                    result = "✅" if detail.get("result") == "PASS" else "❌" if detail.get("result") == "FAIL" else "⚠️"
                                    st.write(f"{result} {detail.get('check')}: {detail.get('detail', '')[:80]}")
                            
                            with tab2:
                                m8 = match.get("m8_dual", {})
                                st.write(f"Dual Risk Level: {m8.get('dual_risk_level', 'UNKNOWN')}")
                                st.write(f"Clean Risk Score: {m8.get('clean_risk_score', '-')}")
                                st.write(f"Conflict Detected: {'⚠️ YES' if m8.get('conflict_detected') else '✅ NO'}")
                                st.write(f"Underdog Threat: {m8.get('underdog_threat', 'NONE')}")
                            
                            with tab3:
                                m9 = match.get("m9_underdog", {})
                                st.write(f"Threat Level: {m9.get('threat_level', 'NONE')}")
                                st.write(f"Recommendation: {m9.get('recommendation', 'NONE')}")
                                st.write(f"Underdog Edge: {m9.get('underdog_edge', 0)}")
                            
                            with tab4:
                                for note in match.get("decision_notes", []):
                                    st.caption(f"• {note}")
                                
                                risk_flags = match.get("risk_flags", [])
                                if risk_flags:
                                    st.markdown("**⚠️ Risk Flags**")
                                    for flag in risk_flags:
                                        st.error(flag)
        else:
            st.info("No results yet. Select leagues and click 'Run Scan'")
    
    else:
        st.info("👈 Select leagues from the sidebar and click 'Run Scan' to get started")


# ============================================
# FOOTER
# ============================================

st.divider()
st.caption(f"🔮 Match Oracle | Mode: {st.session_state.mode.upper()} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
