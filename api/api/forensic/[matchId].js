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
                    { name: "Odds present", value: "2.15/4.30/7.52", result: "PASS" }
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
            }
        }
    }
};

export default async function handler(req, res) {
    const { matchId } = req.query;
    
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    const data = FORENSIC_DATA[matchId];
    if (data) {
        res.status(200).json({ success: true, data });
    } else {
        res.status(404).json({ success: false, error: "Forensic data not found" });
    }
}
