from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from datetime import datetime
from typing import Optional

app = FastAPI(title="Match Oracle API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Football configuration
API_FOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
API_FOOTBALL_URL = "https://v3.football.api-sports.io"

# ========== HEALTH CHECK ==========
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ========== FIXTURES ENDPOINTS ==========
@app.get("/api/fixtures/today")
async def get_todays_fixtures():
    """Get today's fixtures from API-Football"""
    if not API_FOOTBALL_KEY:
        return {"response": [], "error": "API key not configured"}
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/fixtures",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"date": today, "season": 2025}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": [], "error": f"API error: {response.status_code}"}

@app.get("/api/fixtures/league/{league_id}")
async def get_league_fixtures(league_id: int, date: Optional[str] = None):
    """Get fixtures for a specific league"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/fixtures",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"league": league_id, "date": date, "season": 2025}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

@app.get("/api/fixtures/live")
async def get_live_fixtures():
    """Get live/in-progress fixtures"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    async with httpx.AsyncClient() as client:
        # Live statuses: 1H (First Half), HT (Half Time), 2H (Second Half)
        response = await client.get(
            f"{API_FOOTBALL_URL}/fixtures",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"live": "all", "season": 2025}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

# ========== STANDINGS ENDPOINTS ==========
@app.get("/api/standings/{league_id}")
async def get_standings(league_id: int):
    """Get league standings"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/standings",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"league": league_id, "season": 2025}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

# ========== TEAM ENDPOINTS ==========
@app.get("/api/teams/{team_id}")
async def get_team_info(team_id: int):
    """Get team information"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/teams",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"id": team_id}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

@app.get("/api/teams/{team_id}/statistics")
async def get_team_statistics(team_id: int, league_id: int, season: int = 2025):
    """Get team statistics (form, goals, etc.)"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/teams/statistics",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"team": team_id, "league": league_id, "season": season}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

# ========== H2H ENDPOINTS ==========
@app.get("/api/h2h/{team1_id}/{team2_id}")
async def get_head_to_head(team1_id: int, team2_id: int, limit: int = 10):
    """Get head-to-head history between two teams"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/fixtures/headtohead",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"h2h": f"{team1_id}-{team2_id}", "last": limit}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

# ========== LEAGUE ENDPOINTS ==========
@app.get("/api/leagues")
async def get_leagues():
    """Get all available leagues"""
    if not API_FOOTBALL_KEY:
        return {"response": []}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_FOOTBALL_URL}/leagues",
            headers={"x-apisports-key": API_FOOTBALL_KEY},
            params={"season": 2025}
        )
        
        if response.status_code == 200:
            return response.json()
        return {"response": []}

# ========== FORENSIC REPORTS (Placeholder - Connect to your M4-M27) ==========
@app.get("/frontend/legs/{leg_id}/forensic")
async def get_leg_forensic(leg_id: str):
    """
    Get forensic report for a specific leg.
    This should call your M4-M27 modules.
    """
    # TODO: Connect to your actual M4-M27 modules
    # For now, return a structured placeholder
    
    return {
        "leg_id": leg_id,
        "m4": {"passed": True, "checksPassed": 6, "checksTotal": 8},
        "m5": {"failureScore": 2.5, "passed": True},
        "m6": {"homeScore": 82, "awayScore": 65},
        "m7": {"consensus": "APPROVE", "agreement": 0.78},
        "m8": {"dualRiskLevel": "LOW", "underdogThreat": "LOW"},
        "m9": {"underdogEdge": -0.021, "threatLevel": "LOW"},
        "m10": {"matrixUseful": True, "bilateralPrediction": "HOME"},
        "m26": {"matchImportance": 0.72, "isRivalry": True},
        "m27": {"h2hScore": 78, "h2hLabel": "FAV_EDGE"},
        "riskFlags": ["Pattern clash moderate"],
        "finalStatus": "APPROVED",
        "finalConfidence": "HIGH",
        "weightedScore": 0.78,
        "timestamp": datetime.now().isoformat()
    }

# ========== FRONTEND AGGREGATION ENDPOINTS ==========
@app.get("/frontend/dashboard")
async def get_dashboard_data():
    """Aggregate dashboard data"""
    fixtures = await get_todays_fixtures()
    
    return {
        "todayStats": {
            "totalLegs": len(fixtures.get("response", [])),
            "approved": 0,  # TODO: Calculate from your pipeline
            "rejected": 0,
            "caution": 0,
            "totalStaked": 847,
            "potentialReturn": 2150
        },
        "topPicks": [],  # TODO: Get from your M12 portfolio
        "legsByLeague": [],  # TODO: Calculate from fixtures
        "systemHealth": {"grade": "B", "accuracy": 0.58}
    }

@app.get("/frontend/legs")
async def get_all_legs():
    """Get all legs for display"""
    fixtures = await get_todays_fixtures()
    
    legs = []
    for fx in fixtures.get("response", [])[:20]:
        legs.append({
            "id": fx.get("fixture", {}).get("id"),
            "homeTeam": fx.get("teams", {}).get("home", {}).get("name", "?"),
            "awayTeam": fx.get("teams", {}).get("away", {}).get("name", "?"),
            "league": fx.get("league", {}).get("name", "?"),
            "kickoff": fx.get("fixture", {}).get("date", ""),
            "status": fx.get("fixture", {}).get("status", {}).get("short", "NS"),
            "selection": fx.get("teams", {}).get("home", {}).get("name", "?"),
            "selectionOdds": 2.00,
            "modelProb": 0.55,
            "edge": 0.05,
            "confidence": "MEDIUM"
        })
    
    return {"legs": legs}

@app.get("/frontend/bankroll")
async def get_bankroll():
    """Get bankroll status"""
    return {
        "current": 12450,
        "peak": 13200,
        "drawdown": 5.7,
        "history": [
            {"date": "Jun 1", "bankroll": 10000},
            {"date": "Jun 2", "bankroll": 10250},
            {"date": "Jun 3", "bankroll": 10500},
            {"date": "Jun 4", "bankroll": 10300},
            {"date": "Jun 5", "bankroll": 10800},
            {"date": "Jun 6", "bankroll": 11200},
            {"date": "Jun 7", "bankroll": 11800},
            {"date": "Jun 8", "bankroll": 12450},
        ]
    }

@app.get("/frontend/performance")
async def get_performance():
    """Get performance metrics"""
    return {
        "calibrationGrade": "B",
        "overallAccuracy": 0.58,
        "highConfAccuracy": 0.68,
        "mediumConfAccuracy": 0.52,
        "systemHealth": {"grade": "B", "accuracy": 0.58}
    }

@app.get("/frontend/parlays")
async def get_parlays():
    """Get parlay suggestions"""
    return {
        "safe": [],
        "balanced": [],
        "aggressive": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
