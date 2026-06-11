// Mock match data
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

export default async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Credentials', true);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
    res.setHeader(
        'Access-Control-Allow-Headers',
        'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
    );
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    res.status(200).json({ success: true, data: MATCHES });
}
