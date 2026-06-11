import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

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
            const response = await axios.get(`/api/forensic/${matchId}`);
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
                <p className="odds-info">Odds: H {report.homeOdds} | D {report.drawOdds} | A {report.awayOdds}</p>
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
                            <p>Goals: {modules.m1.homeMetrics.goalsFor}/{modules.m1.homeMetrics.goalsAgainst}</p>
                            <p>Home Record: {modules.m1.homeMetrics.homeRecord}</p>
                            <p>PPG: {modules.m1.homeMetrics.ppg}</p>
                            <p>Recent Form: {modules.m1.homeMetrics.recentForm}</p>
                        </div>
                        <div>
                            <h3>{report.away}</h3>
                            <p>Games: {modules.m1.awayMetrics.games} | W-D-L: {modules.m1.awayMetrics.wins}-{modules.m1.awayMetrics.draws}-{modules.m1.awayMetrics.losses}</p>
                            <p>Goals: {modules.m1.awayMetrics.goalsFor}/{modules.m1.awayMetrics.goalsAgainst}</p>
                            <p>Away Record: {modules.m1.awayMetrics.awayRecord}</p>
                            <p>PPG: {modules.m1.awayMetrics.ppg}</p>
                            <p>Recent Form: {modules.m1.awayMetrics.recentForm}</p>
                        </div>
                    </div>
                    <div className="h2h-info">H2H: {modules.m1.h2h}</div>
                    <div className="verdict-pass">Verdict: ✅ {modules.m1.status}</div>
                </div>
            </div>

            {/* Module 3 */}
            <div className="module">
                <h2 className="module-header">MODULE 3: {modules.m3.name}</h2>
                <div className="module-content">
                    <div className="odds-analysis">
                        <div className="odds-row">
                            <span>Home: {modules.m3.oddsAnalysis.homeOdds}</span>
                            <span>Implied: {modules.m3.oddsAnalysis.homeImplied}%</span>
                            <span>Model: {modules.m3.oddsAnalysis.homeModel}%</span>
                        </div>
                        <div className="odds-row">
                            <span>Draw: {modules.m3.oddsAnalysis.drawOdds}</span>
                            <span>Implied: {modules.m3.oddsAnalysis.drawImplied}%</span>
                            <span>Model: {modules.m3.oddsAnalysis.drawModel}%</span>
                        </div>
                        <div className="odds-row">
                            <span>Away: {modules.m3.oddsAnalysis.awayOdds}</span>
                            <span>Implied: {modules.m3.oddsAnalysis.awayImplied}%</span>
                            <span>Model: {modules.m3.oddsAnalysis.awayModel}%</span>
                        </div>
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

export default ForensicReport;
