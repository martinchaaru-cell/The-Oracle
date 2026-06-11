import React, { useState } from 'react';

function Settings() {
    const [aiThreshold, setAiThreshold] = useState(60);
    const [baseStake, setBaseStake] = useState(10);
    const [maxStake, setMaxStake] = useState(100);

    const handleSave = () => {
        alert('Settings saved successfully!');
    };

    return (
        <div className="settings">
            <h1 className="gold-header">⚙️ Settings</h1>
            
            <div className="settings-section">
                <h2>AI Intelligence Settings</h2>
                <div className="setting-item">
                    <label>AI Consensus Threshold (%)</label>
                    <input 
                        type="range" 
                        min="0" 
                        max="100" 
                        value={aiThreshold}
                        onChange={(e) => setAiThreshold(e.target.value)}
                    />
                    <span>{aiThreshold}%</span>
                </div>
                <div className="setting-item">
                    <label>
                        <input type="checkbox" defaultChecked /> Enable DeepSeek
                    </label>
                </div>
                <div className="setting-item">
                    <label>
                        <input type="checkbox" defaultChecked /> Enable Claude
                    </label>
                </div>
                <div className="setting-item">
                    <label>
                        <input type="checkbox" defaultChecked /> Enable Gemini
                    </label>
                </div>
                <div className="setting-item">
                    <label>
                        <input type="checkbox" defaultChecked /> Enable GPT
                    </label>
                </div>
            </div>

            <div className="settings-section">
                <h2>Stake Management</h2>
                <div className="setting-item">
                    <label>Base Stake (€)</label>
                    <input 
                        type="number" 
                        value={baseStake}
                        onChange={(e) => setBaseStake(e.target.value)}
                        min="0"
                        max="1000"
                    />
                </div>
                <div className="setting-item">
                    <label>Maximum Stake (€)</label>
                    <input 
                        type="number" 
                        value={maxStake}
                        onChange={(e) => setMaxStake(e.target.value)}
                        min="0"
                        max="10000"
                    />
                </div>
            </div>

            <button onClick={handleSave} className="save-btn">Save Settings</button>
        </div>
    );
}

export default Settings;
