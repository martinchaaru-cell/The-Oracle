// lib/api.ts
import * as mockData from './mockData';

class ApiClient {
  // Dashboard
  async getDashboard() {
    return mockData.mockDashboardData;
  }

  // Legs
  async getAllLegs(filters?: {
    status?: string[];
    confidence?: string[];
    league?: string[];
    date?: string;
  }) {
    let legs = [...mockData.mockAllLegs];
    
    if (filters?.status && filters.status.length > 0) {
      legs = legs.filter(l => filters.status!.includes(l.status));
    }
    if (filters?.confidence && filters.confidence.length > 0) {
      legs = legs.filter(l => filters.confidence!.includes(l.confidence));
    }
    if (filters?.league && filters.league.length > 0) {
      legs = legs.filter(l => filters.league!.includes(l.league));
    }
    
    return { legs, total: legs.length, filters: {} };
  }

  async getLegForensic(legId: string) {
    // Return mock forensic data
    return {
      m4: { passed: true, checksPassed: 6, checksTotal: 8, weightedScore: 0.75, checkDetails: [] },
      m5: { failureScore: 2.5, passed: true, details: {} },
      m6: { homeScore: 82, awayScore: 65, homeKeyPlayersMissing: [], awayKeyPlayersMissing: [], homeFatigue: "LOW", awayFatigue: "MEDIUM" },
      m7: { consensus: "APPROVE", agreement: 0.78, providers: ["DeepSeek", "Claude", "Gemini"], narratives: {} },
      m8: { dualRiskLevel: "LOW", underdogThreat: "LOW", patternClashScore: 0.18, resilienceGap: 0.24, patternsReliable: true },
      m9: { underdogEdge: -0.021, threatLevel: "LOW", patternScore: 22, goldmineQualified: false },
      m10: { matrixUseful: true, bilateralPrediction: "HOME", bilateralConfidence: "HIGH", trapValueSignal: "NONE" },
      m26: { matchImportance: 0.72, contextLabel: "HIGH_STAKES", isRivalry: true, isSixPointer: false, isDeadRubber: false, homeMotivation: "HIGH", awayMotivation: "NORMAL" },
      m27: { h2hScore: 78, h2hLabel: "FAV_EDGE", gamesPlayed: 48, favWins: 29, draws: 11, undWins: 8, drawRate: 0.23, psychologicalBlock: false, drawBoostFactor: 1.0 },
      riskFlags: ["Pattern clash moderate"],
      finalStatus: "APPROVED",
      finalConfidence: "HIGH",
      weightedScore: 0.78
    };
  }

  // Portfolio
  async getPortfolio() {
    return mockData.mockPortfolio;
  }

  async getParlays() {
    return mockData.mockPortfolio;
  }

  async getBankroll() {
    return mockData.mockBankroll;
  }

  async getPerformance() {
    return mockData.mockPerformance;
  }

  // Countries & Leagues
  async getCountries() {
    return {
      countries: [
        { id: 1, name: "England", code: "ENG", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", leagues: [
          { id: 39, name: "Premier League", tier: 1, season: 2025, totalTeams: 20 },
          { id: 40, name: "Championship", tier: 2, season: 2025, totalTeams: 24 }
        ]},
        { id: 2, name: "Spain", code: "ESP", flag: "🇪🇸", leagues: [
          { id: 140, name: "La Liga", tier: 1, season: 2025, totalTeams: 20 }
        ]},
        { id: 3, name: "Germany", code: "GER", flag: "🇩🇪", leagues: [
          { id: 78, name: "Bundesliga", tier: 1, season: 2025, totalTeams: 18 }
        ]},
        { id: 4, name: "Italy", code: "ITA", flag: "🇮🇹", leagues: [
          { id: 135, name: "Serie A", tier: 1, season: 2025, totalTeams: 20 }
        ]},
        { id: 5, name: "France", code: "FRA", flag: "🇫🇷", leagues: [
          { id: 61, name: "Ligue 1", tier: 1, season: 2025, totalTeams: 18 }
        ]}
      ]
    };
  }

  // Config
  async getConfig() {
    return {
      homeWinThreshold: 0.57,
      opponentWinCap: 0.25,
      minEdge: 0.04,
      confidenceThreshold: 0.55,
      riskTolerance: 1.0,
      kellyFraction: 0.25
    };
  }

  async updateConfig(config: any) {
    console.log("Config updated (mock):", config);
    return { success: true };
  }

  async getApiBudget() {
    return {
      budget: {
        callsUsed: 47,
        callsLimit: 100,
        callsLeft: 53,
        warning: false,
        critical: false,
        emergency: false,
        exhausted: false
      }
    };
  }

  async getDatabaseStats() {
    return {
      matches: 847,
      predictions: 632,
      outcomes: 421,
      uniqueLeagues: 28,
      overallAccuracy: 0.58
    };
  }

  // Calendar
  async getCalendarEvents(startDate: string, endDate: string) {
    return {
      events: [
        { date: new Date().toISOString().split('T')[0], legCount: 47, approvedCount: 12, rejectedCount: 28, cautionCount: 7, scanned: true },
        { date: new Date(Date.now() - 86400000).toISOString().split('T')[0], legCount: 52, approvedCount: 14, rejectedCount: 30, cautionCount: 8, scanned: true }
      ]
    };
  }

  async scanDate(date: string) {
    console.log("Scanning date (mock):", date);
    return { success: true };
  }

  async scanDateRange(startDate: string, endDate: string) {
    console.log("Scanning range (mock):", startDate, endDate);
    return { success: true };
  }

  // Generic POST
  async post(endpoint: string, data?: any) {
    console.log("POST (mock):", endpoint, data);
    return { success: true };
  }
}

export const api = new ApiClient();
