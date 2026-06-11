import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function Sidebar() {
    const [time, setTime] = useState('');

    useEffect(() => {
        const timer = setInterval(() => {
            const now = new Date();
            setTime(now.toLocaleTimeString('en-US', { timeZone: 'Africa/Nairobi' }));
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    return (
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
                <p>🕐 {time} GMT+3</p>
            </div>
            <hr />
            <div className="version-info">
                <p>Version: 2.0.0</p>
                <p>Last Update: June 2026</p>
            </div>
        </div>
    );
}

export default Sidebar;
