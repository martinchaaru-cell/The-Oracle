import React from 'react';

function Performance() {
    return (
        <div className="performance">
            <h1 className="gold-header">📈 Performance Analytics</h1>
            
            <div className="metrics-grid">
                <div className="metric-card">
                    <div className="metric-value">0</div>
                    <div className="metric-label">Total Bets</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">0%</div>
                    <div className="metric-label">Win Rate</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">0%</div>
                    <div className="metric-label">ROI</div>
                </div>
                <div className="metric-card">
                    <div className="metric-value">€0</div>
                    <div className="metric-label">Profit/Loss</div>
                </div>
            </div>

            <div className="coming-soon">
                <h3>📊 Detailed Analytics Coming Soon</h3>
                <p>Track your betting performance, view historical data, and analyze system accuracy.</p>
            </div>
        </div>
    );
}

export default Performance;
