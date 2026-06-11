import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Dashboard() {
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchMatches();
    }, []);

    const fetchMatches = async () => {
        try {
            const response = await axios.get('/api/matches');
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

    const getVerdictIcon = (verdict) => {
        switch(verdict) {
            case 'APPROVED': return '✅';
            case 'REJECTED': return '🚫';
            default: return '⚠️';
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
                                {getVerdictIcon(match.verdict)} {match.verdict}
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

export default Dashboard;
