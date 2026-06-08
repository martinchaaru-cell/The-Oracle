// app/page.tsx
"use client";

import { useEffect, useState } from "react";
import { Calendar, TrendingUp, DollarSign, Award, AlertCircle, Zap, Clock, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { api } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import toast from "react-hot-toast";

interface DashboardData {
  bankroll: {
    current: number;
    peak: number;
    drawdownPct: number;
    stakeMultiplier: number;
    healthLabel: string;
    pauseRecommended: boolean;
  };
  todayStats: {
    totalLegs: number;
    approved: number;
    rejected: number;
    caution: number;
    totalStake: number;
    potentialReturn: number;
  };
  topPicks: Array<{
    legId: string;
    match: string;
    selection: string;
    odds: number;
    modelProb: number;
    edge: number;
    confidence: string;
    homeTeam: string;
    awayTeam: string;
    league: string;
    kickoff: string;
  }>;
  legsByLeague: Array<{ league: string; count: number }>;
  performance: {
    accuracy: number;
    roi: number;
    calibrationGrade: string;
  };
  recentOddsMoves: Array<{
    match: string;
    selection: string;
    oldOdds: number;
    newOdds: number;
    movePct: number;
  }>;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const { isConnected, lastMessage } = useWebSocket("wss://the-oracle-backend.up.railway.app/ws");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === "odds_update") {
        toast.success(`Odds moved: ${lastMessage.data.match} - ${lastMessage.data.selection}`);
        fetchDashboardData();
      }
      setLastUpdate(new Date());
    }
  }, [lastMessage]);

  const fetchDashboardData = async () => {
    try {
      const response = await api.getDashboard();
      setData(response);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const triggerScan = async () => {
    try {
      toast.loading("Scanning today's fixtures...");
      await api.scanDate(new Date().toISOString().split("T")[0]);
      toast.success("Scan complete! Refreshing data...");
      fetchDashboardData();
    } catch (error) {
      toast.error("Scan failed");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  const pieColors = ["#3b82f6", "#ef4444", "#f59e0b"];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time oracle intelligence
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4" />
            <span className={isConnected ? "text-green-500" : "text-red-500"}>
              {isConnected ? "Live" : "Disconnected"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>Last update: {lastUpdate.toLocaleTimeString()}</span>
          </div>
          <Button onClick={triggerScan} className="gap-2">
            <Zap className="h-4 w-4" />
            Scan Today
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-blue-900/20 to-blue-900/5 border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Bankroll</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${data?.bankroll.current.toFixed(2)}</div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-muted-foreground">Peak: ${data?.bankroll.peak.toFixed(2)}</span>
              {data?.bankroll.drawdownPct > 0 && (
                <Badge variant={data.bankroll.drawdownPct > 0.15 ? "destructive" : "warning"}>
                  {data.bankroll.drawdownPct > 0.15 ? "⚠️" : "🔻"} {(data.bankroll.drawdownPct * 100).toFixed(1)}% drawdown
                </Badge>
              )}
            </div>
            <div className="mt-3">
              <div className="flex justify-between text-xs mb-1">
                <span>Stake Multiplier</span>
                <span>{((data?.bankroll.stakeMultiplier || 1) * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full transition-all"
                  style={{ width: `${((data?.bankroll.stakeMultiplier || 1) * 100)}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Today's Legs</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.todayStats.totalLegs || 0}</div>
            <div className="flex gap-3 mt-2 text-sm">
              <span className="text-green-500">✅ {data?.todayStats.approved || 0}</span>
              <span className="text-yellow-500">⚠️ {data?.todayStats.caution || 0}</span>
              <span className="text-red-500">❌ {data?.todayStats.rejected || 0}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Staked</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${data?.todayStats.totalStake?.toFixed(2) || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Potential Return: ${data?.todayStats.potentialReturn?.toFixed(2) || 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${
                data?.performance.calibrationGrade === "A" ? "text-green-500" :
                data?.performance.calibrationGrade === "B" ? "text-blue-500" :
                data?.performance.calibrationGrade === "C" ? "text-yellow-500" :
                "text-red-500"
              }`}>
                {data?.performance.calibrationGrade || "?"}
              </span>
              <span className="text-sm text-muted-foreground">Grade</span>
            </div>
            <div className="flex justify-between mt-2 text-sm">
              <span>📊 {((data?.performance.accuracy || 0) * 100).toFixed(0)}%</span>
              <span>💰 {((data?.performance.roi || 0) * 100).toFixed(0)}% ROI</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Legs by League</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data?.legsByLeague || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="league" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px" }}
                  labelStyle={{ color: "#e2e8f0" }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: "Approved", value: data?.todayStats.approved || 0 },
                    { name: "Rejected", value: data?.todayStats.rejected || 0 },
                    { name: "Caution", value: data?.todayStats.caution || 0 },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieColors.map((color, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px" }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
                <span className="text-sm">Approved</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-sm">Rejected</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="text-sm">Caution</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Picks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Top Picks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {data?.topPicks.map((pick, idx) => (
              <div
                key={pick.legId}
                className="flex items-center justify-between p-4 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer"
                onClick={() => window.location.href = `/legs?leg=${pick.legId}`}
              >
                <div className="flex items-center gap-4">
                  <span className="text-2xl font-bold text-primary">#{idx + 1}</span>
                  <div>
                    <div className="font-medium">{pick.match}</div>
                    <div className="text-sm text-muted-foreground">
                      {pick.selection} @ {pick.odds.toFixed(2)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Model Prob</div>
                    <div className="font-medium">{(pick.modelProb * 100).toFixed(0)}%</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Edge</div>
                    <div className="font-medium text-green-500">+{(pick.edge * 100).toFixed(1)}%</div>
                  </div>
                  <Badge variant={pick.confidence === "HIGH" ? "default" : "secondary"}>
                    {pick.confidence}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
