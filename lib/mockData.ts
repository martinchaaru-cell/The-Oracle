// lib/mockData.ts

export const mockDashboardData = {
  bankroll: {
    current: 12450.00,
    peak: 13200.00,
    drawdownPct: 0.057,
    stakeMultiplier: 0.85,
    healthLabel: "CAUTION",
    pauseRecommended: false
  },
  todayStats: {
    totalLegs: 47,
    approved: 12,
    rejected: 28,
    caution: 7,
    totalStake: 847.50,
    potentialReturn: 2150.25
  },
  topPicks: [
    {
      legId: "leg_001",
      match: "Arsenal vs Chelsea",
      selection: "Arsenal",
      odds: 2.10,
      modelProb: 0.62,
      edge: 0.081,
      confidence: "HIGH",
      homeTeam: "Arsenal",
      awayTeam: "Chelsea",
      league: "Premier League",
      leagueTier: 1,
      kickoff: new Date().toISOString(),
      homeOdds: 2.10,
      drawOdds: 3.40,
      awayOdds: 3.20,
      selectionOdds: 2.10,
      status: "APPROVED"
    },
    {
      legId: "leg_002",
      match: "Bayern Munich vs Dortmund",
      selection: "Bayern Munich",
      odds: 1.75,
      modelProb: 0.58,
      edge: 0.067,
      confidence: "HIGH",
      homeTeam: "Bayern Munich",
      awayTeam: "Dortmund",
      league: "Bundesliga",
      leagueTier: 1,
      kickoff: new Date().toISOString(),
      homeOdds: 1.75,
      drawOdds: 3.80,
      awayOdds: 4.20,
      selectionOdds: 1.75,
      status: "APPROVED"
    },
    {
      legId: "leg_003",
      match: "Inter Milan vs Juventus",
      selection: "Inter Milan",
      odds: 2.05,
      modelProb: 0.55,
      edge: 0.042,
      confidence: "MEDIUM",
      homeTeam: "Inter Milan",
      awayTeam: "Juventus",
      league: "Serie A",
      leagueTier: 1,
      kickoff: new Date().toISOString(),
      homeOdds: 2.05,
      drawOdds: 3.30,
      awayOdds: 3.60,
      selectionOdds: 2.05,
      status: "APPROVED"
    }
  ],
  legsByLeague: [
    { league: "Premier League", count: 12 },
    { league: "La Liga", count: 10 },
    { league: "Bundesliga", count: 8 },
    { league: "Serie A", count: 8 },
    { league: "Ligue 1", count: 6 },
    { league: "Eredivisie", count: 3 }
  ],
  performance: {
    accuracy: 0.58,
    roi: 0.124,
    calibrationGrade: "B"
  },
  recentOddsMoves: [
    { match: "Arsenal vs Chelsea", selection: "Arsenal", oldOdds: 2.30, newOdds: 2.10, movePct: -8.7 },
    { match: "Liverpool vs Everton", selection: "Liverpool", oldOdds: 1.85, newOdds: 1.75, movePct: -5.4 },
    { match: "Real Madrid vs Barcelona", selection: "Real Madrid", oldOdds: 2.15, newOdds: 2.25, movePct: 4.7 }
  ]
};

export const mockAllLegs = [
  {
    legId: "leg_001",
    matchId: "arsenal_chelsea",
    country: "England",
    league: "Premier League",
    leagueId: 39,
    leagueTier: 1,
    kickoff: new Date().toISOString(),
    homeTeam: "Arsenal",
    awayTeam: "Chelsea",
    homeOdds: 2.10,
    drawOdds: 3.40,
    awayOdds: 3.20,
    selection: "Arsenal",
    selectionOdds: 2.10,
    modelProb: 0.62,
    edge: 0.081,
    status: "APPROVED",
    confidence: "HIGH"
  },
  {
    legId: "leg_002",
    matchId: "man_city_liverpool",
    country: "England",
    league: "Premier League",
    leagueId: 39,
    leagueTier: 1,
    kickoff: new Date().toISOString(),
    homeTeam: "Man City",
    awayTeam: "Liverpool",
    homeOdds: 1.95,
    drawOdds: 3.60,
    awayOdds: 3.80,
    selection: "Man City",
    selectionOdds: 1.95,
    modelProb: 0.54,
    edge: 0.022,
    status: "CAUTION",
    confidence: "MEDIUM"
  },
  {
    legId: "leg_003",
    matchId: "real_madrid_barcelona",
    country: "Spain",
    league: "La Liga",
    leagueId: 140,
    leagueTier: 1,
    kickoff: new Date().toISOString(),
    homeTeam: "Real Madrid",
    awayTeam: "Barcelona",
    homeOdds: 2.25,
    drawOdds: 3.50,
    awayOdds: 2.90,
    selection: "Real Madrid",
    selectionOdds: 2.25,
    modelProb: 0.48,
    edge: -0.017,
    status: "REJECTED",
    confidence: "LOW"
  },
  {
    legId: "leg_004",
    matchId: "bayern_dortmund",
    country: "Germany",
    league: "Bundesliga",
    leagueId: 78,
    leagueTier: 1,
    kickoff: new Date().toISOString(),
    homeTeam: "Bayern Munich",
    awayTeam: "Dortmund",
    homeOdds: 1.75,
    drawOdds: 3.80,
    awayOdds: 4.20,
    selection: "Bayern Munich",
    selectionOdds: 1.75,
    modelProb: 0.58,
    edge: 0.067,
    status: "APPROVED",
    confidence: "HIGH"
  },
  {
    legId: "leg_005",
    matchId: "inter_juventus",
    country: "Italy",
    league: "Serie A",
    leagueId: 135,
    leagueTier: 1,
    kickoff: new Date().toISOString(),
    homeTeam: "Inter Milan",
    awayTeam: "Juventus",
    homeOdds: 2.05,
    drawOdds: 3.30,
    awayOdds: 3.60,
    selection: "Inter Milan",
    selectionOdds: 2.05,
    modelProb: 0.55,
    edge: 0.042,
    status: "APPROVED",
    confidence: "MEDIUM"
  },
  {
    legId: "leg_006",
    matchId: "psg_marseille",
    country: "France",
    league: "Ligue 1",
    leagueId: 61,
    leagueTier: 1,
    kickoff: new Date().toISOString(),
    homeTeam: "PSG",
    awayTeam: "Marseille",
    homeOdds: 1.55,
    drawOdds: 4.00,
    awayOdds: 5.50,
    selection: "PSG",
    selectionOdds: 1.55,
    modelProb: 0.68,
    edge: 0.113,
    status: "APPROVED",
    confidence: "HIGH"
  }
];

export const mockPortfolio = {
  top_picks: mockDashboardData.topPicks,
  ultra_safe_acca: [
    {
      parlayId: 1,
      tier: "ULTRA_SAFE",
      legs: [
        { match: "Arsenal vs Chelsea", selection: "Arsenal", odds: 2.10, confidence: "HIGH", league: "Premier League" },
        { match: "Bayern vs Dortmund", selection: "Bayern", odds: 1.75, confidence: "HIGH", league: "Bundesliga" }
      ],
      totalOdds: 3.68,
      combinedProb: 0.36,
      riskScore: 0.72,
      riskLevel: "SAFE"
    }
  ],
  balanced: [],
  aggressive: []
};

export const mockBankroll = {
  current: 12450,
  peak: 13200,
  drawdownPct: 0.057,
  stakeMultiplier: 0.85,
  healthLabel: "CAUTION",
  pauseRecommended: false,
  singles: [
    { match: "Arsenal vs Chelsea", selection: "Arsenal", odds: 2.10, stake: 127.50, potentialReturn: 267.75, confidence: "HIGH" },
    { match: "Bayern vs Dortmund", selection: "Bayern", odds: 1.75, stake: 150.00, potentialReturn: 262.50, confidence: "HIGH" },
    { match: "Inter vs Juventus", selection: "Inter", odds: 2.05, stake: 100.00, potentialReturn: 205.00, confidence: "MEDIUM" }
  ],
  ultraSafeAcca: {
    legs: ["Arsenal", "Bayern"],
    combinedOdds: 3.68,
    stake: 50.00,
    potentialReturn: 184.00
  },
  valueAcca: null,
  history: [
    { date: "2025-06-01", bankroll: 10000, profit: 0 },
    { date: "2025-06-02", bankroll: 10250, profit: 250 },
    { date: "2025-06-03", bankroll: 10500, profit: 250 },
    { date: "2025-06-04", bankroll: 10300, profit: -200 },
    { date: "2025-06-05", bankroll: 10800, profit: 500 },
    { date: "2025-06-06", bankroll: 11200, profit: 400 },
    { date: "2025-06-07", bankroll: 11800, profit: 600 },
    { date: "2025-06-08", bankroll: 12450, profit: 650 }
  ]
};

export const mockPerformance = {
  calibrationGrade: "B",
  brierScore: 0.187,
  ece: 0.094,
  overallAccuracy: 0.58,
  highConfAccuracy: 0.68,
  mediumConfAccuracy: 0.52,
  lowConfAccuracy: 0.48,
  overallRoi: 0.124,
  byLeague: [
    { league: "Premier League", total: 45, correct: 28, accuracy: 0.622, roi: 0.152 },
    { league: "La Liga", total: 38, correct: 22, accuracy: 0.579, roi: 0.098 },
    { league: "Bundesliga", total: 32, correct: 19, accuracy: 0.594, roi: 0.112 },
    { league: "Serie A", total: 35, correct: 18, accuracy: 0.514, roi: 0.045 },
    { league: "Ligue 1", total: 28, correct: 17, accuracy: 0.607, roi: 0.134 }
  ],
  history: [
    { date: "Jun 1", accuracy: 0.52, roi: 0.03 },
    { date: "Jun 2", accuracy: 0.55, roi: 0.05 },
    { date: "Jun 3", accuracy: 0.58, roi: 0.07 },
    { date: "Jun 4", accuracy: 0.54, roi: 0.04 },
    { date: "Jun 5", accuracy: 0.60, roi: 0.09 },
    { date: "Jun 6", accuracy: 0.62, roi: 0.11 },
    { date: "Jun 7", accuracy: 0.59, roi: 0.12 },
    { date: "Jun 8", accuracy: 0.58, roi: 0.12 }
  ]
};
