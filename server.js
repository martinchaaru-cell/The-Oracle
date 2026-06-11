const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static('public'));

// ========== MATCH DATA ==========
const MATCHES = [
    {
        id: 1,
        home: "Manchester City",
        away: "Bournemouth",
        date: "2026-06-11",
        venue: "Etihad Stadium",
        league: "Premier League",
        homeOdds: 2.15,
        drawOdds: 4.30,
        awayOdds: 7.52,
        verdict: "REJECTED",
        confidence: 46.5,
        homeWinProb: 46.5,
        drawProb: 22.5,
        awayWinProb: 31.0
    },
    {
        id: 2,
        home: "Liverpool",
        away: "Sheffield United",
        date: "2026-06-11",
        venue: "Anfield",
        league: "Premier League",
        homeOdds: 2.35,
        drawOdds: 4.70,
        awayOdds: 8.22,
        verdict: "REJECTED",
        confidence: 42.5,
        homeWinProb: 42.5,
        drawProb: 21.3,
        awayWinProb: 36.2
    },
    {
        id: 3,
        home: "Arsenal",
        away: "Nottingham Forest",
        date: "2026-06-11",
        venue: "Emirates Stadium",
        league: "Premier League",
        homeOdds: 2.10,
        drawOdds: 4.20,
        awayOdds: 7.35,
        verdict: "REJECTED",
        confidence: 47.6,
        homeWinProb: 47.6,
        drawProb: 23.8,
        awayWinProb: 28.6
    },
    {
        id: 4,
        home: "Chelsea",
        away: "Burnley",
        date: "2026-06-11",
        venue: "Stamford Bridge",
        league: "Premier League",
        homeOdds: 2.55,
        drawOdds: 5.10,
        awayOdds: 8.92,
        verdict: "REJECTED",
        confidence: 39.2,
        homeWinProb: 39.2,
        drawProb: 19.6,
        awayWinProb: 41.2
    },
    {
        id: 5,
        home: "Real Madrid",
        away: "Almeria",
        date: "2026-06-11",
        venue: "Santiago Bernabeu",
        league: "La Liga",
        homeOdds: 2.05,
        drawOdds: 4.10,
        awayOdds: 7.17,
        verdict: "REJECTED",
        confidence: 48.8,
        homeWinProb: 48.8,
        drawProb: 24.4,
        awayWinProb: 26.8
    }
];

// ========== FORENSIC DATA FOR EACH MATCH ==========
const FORENSIC_DATA = {
    1: {
        matchId: 1,
        home: "Manchester City",
        away: "Bournemouth",
        league: "Premier League",
        venue: "Etihad Stadium",
        date: "June 12, 2026",
        homeOdds: 2.15,
        drawOdds: 4.30,
        awayOdds: 7.52,
        finalVerdict: "REJECTED",
        finalStake: 0.00,
        finalReason: "Negative edge detected with low confidence",
        modules: {
            m0: {
                name: "Guardrail & Data Integrity",
                status: "PASS",
                checks: [
                    { name: "Fixture Status", value: "NS (upcoming)", result: "PASS" },
                    { name: "Odds present", value: "2.15/4.30/7.52", result: "PASS" },
                    { name: "Odds bounds", value: "All >1.01, <100", result: "PASS" }
                ]
            },
            m1: {
                name: "Data Ingestion",
                status: "PASS",
                homeMetrics: {
                    games: 20, wins: 14, draws: 4, losses: 2,
                    goalsFor: 48, goalsAgainst: 18,
                    homeRecord: "8-1-1", ppg: 2.30,
                    recentForm: "W, W, D, W, W, L"
                },
                awayMetrics: {
                    games: 20, wins: 5, draws: 6, losses: 9,
                    goalsFor: 22, goalsAgainst: 31,
                    awayRecord: "2-3-5", ppg: 1.05,
                    recentForm: "L, D, L, L, W, D"
                },
                h2h: "Man City 70%, Draw 20%, Bournemouth 10%"
            },
            m3: {
                name: "Probability Engine",
                status: "WARNING",
                oddsAnalysis: {
                    homeOdds: 2.15, homeImplied: 46.5, homeModel: 42,
                    drawOdds: 4.30, drawImplied: 23.3, drawModel: 25,
                    awayOdds: 7.52, awayImplied: 13.3, awayModel: 33,
                    margin: 16.9, edge: -4.5
                }
            },
            m4: {
                name: "Asymmetric Pre-filter",
                status: "PASS",
                passed: 7,
                total: 8,
                checks: [
                    { name: "Season Win Gap", passed: true, value: "+9 wins", points: 10 },
                    { name: "Venue Win Gap", passed: true, value: "+60%", points: 10 },
                    { name: "H2H Favoured", passed: true, value: "70%", points: 10 }
                ]
            },
            m5: {
                name: "Forensic Checks",
                status: "PASS",
                total: 3.5,
                threshold: 4.5,
                failures: [
                    { name: "Negative Edge Detected", points: 2.0 },
                    { name: "Low Confidence Threshold", points: 1.5 }
                ]
            },
            m6: {
                name: "Personnel Forensics",
                status: "WARNING",
                injuries: [
                    { team: "Manchester City", player: "J. Grealish", position: "M", status: "DOUBTFUL" }
                ],
                scores: { home: 75, away: 65 }
            },
            m7: {
                name: "Quad-AI Intelligence",
                status: "CAUTION",
                consensus: "REJECT",
                agreement: 75,
                ais: [
                    { provider: "DeepSeek", verdict: "CAUTION", reasoning: "Low confidence" },
                    { provider: "Claude", verdict: "REJECT", reasoning: "Negative edge" },
                    { provider: "Gemini", verdict: "CAUTION", reasoning: "Injury concerns" },
                    { provider: "GPT", verdict: "REJECT", reasoning: "No value" }
                ]
            },
            m8: {
                name: "Dual Pattern Engine",
                status: "APPROVE",
                severity: "LOW",
                verdict: "APPROVE",
                h2hAllTime: { home: 70, away: 10 },
                currentSeason: { home: 70, away: 25 }
            },
            m9: {
                name: "Underdog Scanner",
                status: "LOW",
                underdogEdge: -8,
                threatLevel: "LOW"
            },
            m10: {
                name: "Season Tally Matrix",
                status: "MEDIUM",
                confidence: "MEDIUM",
                bilateral: { home: 45, draw: 25, away: 30 }
            }
        }
    },
    // Add similar data for other matches...
    2: { /* Liverpool data */ },
    3: { /* Arsenal data */ },
    4: { /* Chelsea data */ },
    5: { /* Real Madrid data */ }
};

// ========== LEAGUE STANDINGS ==========
const LEAGUE_STANDINGS = {
    "Premier League": [
        { pos: 1, team: "Manchester City", pts: 43, gp: 17, w: 13, d: 4, l: 0, gf: 46, ga: 10, gd: 36 },
        { pos: 2, team: "Liverpool", pts: 31, gp: 17, w: 9, d: 4, l: 4, gf: 32, ga: 14, gd: 18 },
        { pos: 3, team: "Arsenal", pts: 29, gp: 17, w: 8, d: 5, l: 4, gf: 28, ga: 13, gd: 15 },
        { pos: 4, team: "Chelsea", pts: 29, gp: 17, w: 8, d: 5, l: 4, gf: 21, ga: 12, gd: 9 }
    ],
    "La Liga": [
        { pos: 1, team: "Real Madrid", pts: 43, gp: 17, w: 13, d: 4, l: 0, gf: 46, ga: 10, gd: 36 },
        { pos: 2, team: "Barcelona", pts: 31, gp: 17, w: 9, d: 4, l: 4, gf: 32, ga: 14, gd: 18 }
    ]
};

// ========== API ROUTES ==========

// Get all matches
app.get('/api/matches', (req, res) => {
    res.json({ success: true, data: MATCHES });
});

// Get match by ID
app.get('/api/matches/:id', (req, res) => {
    const match = MATCHES.find(m => m.id === parseInt(req.params.id));
    if (match) {
        res.json({ success: true, data: match });
    } else {
        res.status(404).json({ success: false, error: "Match not found" });
    }
});

// Get forensic report for a match
app.get('/api/forensic/:matchId', (req, res) => {
    const forensic = FORENSIC_DATA[req.params.matchId];
    if (forensic) {
        res.json({ success: true, data: forensic });
    } else {
        res.status(404).json({ success: false, error: "Forensic data not found" });
    }
});

// Get league standings
app.get('/api/standings/:league', (req, res) => {
    const standings = LEAGUE_STANDINGS[req.params.league];
    if (standings) {
        res.json({ success: true, data: standings });
    } else {
        res.status(404).json({ success: false, error: "League not found" });
    }
});

// Analyze match endpoint (for AI predictions)
app.post('/api/analyze', async (req, res) => {
    const { matchId } = req.body;
    // Here you would integrate with AI services
    res.json({ 
        success: true, 
        message: "Analysis complete",
        analysis: {
            recommendation: "REJECT",
            confidence: 46.5,
            edge: -4.5
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Match Oracle Server running on port ${PORT}`);
    console.log(`📊 API available at http://localhost:${PORT}/api`);
});
