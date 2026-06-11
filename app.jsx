import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

// Dashboard Component
function Dashboard() {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchMatches();
    }, []);

    const fetchMatches = async () => {
        try {
            const response = await axios.get(`${API_URL}/matches`);
            setMatches(response.data.data);
        } catch (error) {
            console.error('Error fetching matches:', error);
        } finally {
            setLoading(false);
        }
    };

    const getVerdictClass = (verdict) => {
        switch(verdict) {
            case 'APPROVED': return 'verdict-approved';
            case 'REJECTED': return 'verdict-rejected';
            default: return 'verdict-caution';
        }
    };

    if (loading) return <div className="loading">Loading matches...</div>;

    return (
        <div className="dashboard">
            <div className="header">
                <h1 className="gold-header">🎯 Match Oracle</h1>
                <p className="gold-subheader">Forensic Betting Intelligence | AI-Powered Match Analysis</p>
            </div>

            <div className="matches-table">
                <div className="table-header">
                    <div className="col-match">Match</div>
                    <div className="col-odds">H</div>
                    <div className="col-odds">D</div>
                    <div className="col-odds">A</div>
                    <div className="col-verdict">Verdict</div>
                    <div className="col-action"></div>
                </div>

                {matches.map(match => (
                    <div key={match.id} className="match-row">
                        <div className="col-match">
                            <div className="match-teams">{match.home} vs {match.away}</div>
                            <div className="match-meta">{match.date} · {match.venue.split(' ')[0]}</div>
                        </div>
                        <div className="col-odds">{match.homeOdds}</div>
                        <div className="col-odds">{match.drawOdds}</div>
                        <div className="col-odds">{match.awayOdds}</div>
                        <div className="col-verdict">
                            <span className={`verdict-badge ${getVerdictClass(match.verdict)}`}>
                                {match.verdict === 'REJECTED' ? '🚫' : match.verdict === 'APPROVED' ? '✅' : '⚠️'} {match.verdict}
                            </span>
                            <div className="confidence-bar">
                                <div className="confidence-label">{match.confidence}%</div>
                                <div className="confidence-track">
                                    <div className="confidence-fill" style={{ width: `${match.confidence}%` }}></div>
                                </div>
                            </div>
                        </div>
                        <div className="col-action">
                            <button onClick={() => navigate(`/forensic/${match.id}`)} className="analyze-btn">
                                Analyze
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// Forensic Report Component
function ForensicReport() {
    const { matchId } = useParams();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchForensicReport();
    }, [matchId]);

    const fetchForensicReport = async () => {
        try {
            const response = await axios.get(`${API_URL}/forensic/${matchId}`);
            setReport(response.data.data);
        } catch (error) {
            console.error('Error fetching report:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Loading forensic report...</div>;
    if (!report) return <div className="error">Report not found</div>;

    const modules = report.modules;

    return (
        <div className="forensic-report">
            <button onClick={() => navigate('/')} className="back-btn">← Back to Dashboard</button>
            
            <div className="report-header">
                <h1 className="gold-header">🔬 Forensic Report: {report.home} vs {report.away}</h1>
                <p className="gold-subheader">{report.league} | {report.venue} | {report.date}</p>
            </div>

            {/* Module 0 */}
            <div className="module">
                <h2 className="module-header">MODULE 0: {modules.m0.name}</h2>
                <div className="module-content">
                    {modules.m0.checks.map((check, idx) => (
                        <div key={idx} className="check-item">✅ {check.name}: {check.value}</div>
                    ))}
                    <div className="verdict-pass">Verdict: ✅ {modules.m0.status}</div>
                </div>
            </div>

            {/* Module 1 */}
            <div className="module">
                <h2 className="module-header">MODULE 1: {modules.m1.name}</h2>
                <div className="module-content">
                    <div className="two-columns">
                        <div>
                            <h3>{report.home}</h3>
                            <p>Games: {modules.m1.homeMetrics.games} | W-D-L: {modules.m1.homeMetrics.wins}-{modules.m1.homeMetrics.draws}-{modules.m1.homeMetrics.losses}</p>
                            <p>PPG: {modules.m1.homeMetrics.ppg}</p>
                            <p>Recent Form: {modules.m1.homeMetrics.recentForm}</p>
                        </div>
                        <div>
                            <h3>{report.away}</h3>
                            <p>Games: {modules.m1.awayMetrics.games} | W-D-L: {modules.m1.awayMetrics.wins}-{modules.m1.awayMetrics.draws}-{modules.m1.awayMetrics.losses}</p>
                            <p>PPG: {modules.m1.awayMetrics.ppg}</p>
                            <p>Recent Form: {modules.m1.awayMetrics.recentForm}</p>
                        </div>
                    </div>
                    <div className="verdict-pass">Verdict: ✅ {modules.m1.status}</div>
                </div>
            </div>

            {/* Module 3 */}
            <div className="module">
                <h2 className="module-header">MODULE 3: {modules.m3.name}</h2>
                <div className="module-content">
                    <div className="odds-analysis">
                        <div>Home: {modules.m3.oddsAnalysis.homeOdds} (Implied {modules.m3.oddsAnalysis.homeImplied}% | Model {modules.m3.oddsAnalysis.homeModel}%)</div>
                        <div>Draw: {modules.m3.oddsAnalysis.drawOdds} (Implied {modules.m3.oddsAnalysis.drawImplied}% | Model {modules.m3.oddsAnalysis.drawModel}%)</div>
                        <div>Away: {modules.m3.oddsAnalysis.awayOdds} (Implied {modules.m3.oddsAnalysis.awayImplied}% | Model {modules.m3.oddsAnalysis.awayModel}%)</div>
                        <div className="edge-warning">Edge: {modules.m3.oddsAnalysis.edge}% (NEGATIVE)</div>
                    </div>
                </div>
            </div>

            {/* Module 4 */}
            <div className="module">
                <h2 className="module-header">MODULE 4: {modules.m4.name}</h2>
                <div className="module-content">
                    {modules.m4.checks.map((check, idx) => (
                        <div key={idx} className="check-item">
                            {check.passed ? '✅' : '❌'} {check.name}: {check.value} (+{check.points} pts)
                        </div>
                    ))}
                    <div className="verdict-pass">Passed: {modules.m4.passed}/{modules.m4.total} → ✅ PASS</div>
                </div>
            </div>

            {/* Module 5 */}
            <div className="module">
                <h2 className="module-header">MODULE 5: {modules.m5.name}</h2>
                <div className="module-content">
                    {modules.m5.failures.map((failure, idx) => (
                        <div key={idx} className="warning-item">⚠️ {failure.name}: +{failure.points} pts</div>
                    ))}
                    <div>TOTAL: {modules.m5.total} / {modules.m5.threshold} → ✅ PASS</div>
                </div>
            </div>

            {/* Module 6 */}
            <div className="module">
                <h2 className="module-header">MODULE 6: {modules.m6.name}</h2>
                <div className="module-content">
                    {modules.m6.injuries.map((injury, idx) => (
                        <div key={idx} className="warning-item">⚠️ {injury.team}: {injury.player} ({injury.position}) - {injury.status}</div>
                    ))}
                </div>
            </div>

            {/* Module 7 */}
            <div className="module">
                <h2 className="module-header">MODULE 7: {modules.m7.name}</h2>
                <div className="module-content">
                    {modules.m7.ais.map((ai, idx) => (
                        <div key={idx} className="ai-item">
                            <strong>{ai.provider}:</strong> {ai.verdict} - {ai.reasoning}
                        </div>
                    ))}
                    <div className="info">Consensus: {modules.m7.consensus} (Agreement: {modules.m7.agreement}%)</div>
                </div>
            </div>

            {/* Module 8 */}
            <div className="module">
                <h2 className="module-header">MODULE 8: {modules.m8.name}</h2>
                <div className="module-content">
                    <div>H2H all-time: {report.home} DOMINANT ({modules.m8.h2hAllTime.home}% vs {modules.m8.h2hAllTime.away}%)</div>
                    <div>Current season: {report.home} DOMINANT ({modules.m8.currentSeason.home}% vs {modules.m8.currentSeason.away}%)</div>
                    <div className={`severity-${modules.m8.severity.toLowerCase()}`}>Conflict severity: {modules.m8.severity}</div>
                </div>
            </div>

            {/* Final Verdict */}
            <div className="final-verdict">
                <h2>FINAL VERDICT</h2>
                <div className="verdict-reject">{report.finalVerdict}</div>
                <div className="stake">Recommended Stake: €{report.finalStake}</div>
                <div className="reason">{report.finalReason}</div>
            </div>
        </div>
    );
}

// Main App Component
function App() {
    return (
        <Router>
            <div className="app">
                <div className="sidebar">
                    <h2>🎯 Match Oracle</h2>
                    <hr />
                    <Link to="/" className="nav-link">📊 Dashboard</Link>
                    <Link to="/performance" className="nav-link">📈 Performance</Link>
                    <Link to="/settings" className="nav-link">⚙️ Settings</Link>
                    <hr />
                    <div className="system-status">
                        <h3>System Status</h3>
                        <p>✅ AI Engine: Active</p>
                        <p>✅ Data Feed: Connected</p>
                        <p>🕐 {new Date().toLocaleTimeString()} GMT+3</p>
                    </div>
                </div>
                
                <div className="main-content">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/forensic/:matchId" element={<ForensicReport />} />
                        <Route path="/performance" element={<div>Performance Page</div>} />
                        <Route path="/settings" element={<div>Settings Page</div>} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;
