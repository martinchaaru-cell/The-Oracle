<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Match Oracle - Football Intelligence</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            height: 100vh;
            overflow: hidden;
        }
        .dashboard { display: flex; height: 100vh; }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #0f0f1a 0%, #0a0a0f 100%);
            border-right: 1px solid #2a2a3a;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            flex-shrink: 0;
        }
        .logo { padding: 24px 20px; border-bottom: 1px solid #2a2a3a; margin-bottom: 20px; }
        .logo h1 { font-size: 22px; background: linear-gradient(135deg, #f59e0b, #ea580c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .logo p { font-size: 11px; color: #6b7280; margin-top: 4px; }
        
        .nav-item {
            padding: 12px 20px;
            margin: 4px 12px;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s;
        }
        .nav-item:hover { background: #1a1a2e; }
        .nav-item.active { background: linear-gradient(90deg, #f59e0b20 0%, #1a1a2e 100%); border-left: 3px solid #f59e0b; color: #f59e0b; }
        .nav-icon { font-size: 20px; width: 28px; }
        
        /* Main Content */
        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .header {
            background: #0f0f1a;
            border-bottom: 1px solid #2a2a3a;
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-title { font-size: 18px; font-weight: 600; }
        .header-badge { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 20px; padding: 6px 14px; font-size: 12px; }
        .header-badge span { color: #f59e0b; font-weight: 600; }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            padding: 20px 24px;
        }
        .stat-card {
            background: #0f0f1a;
            border: 1px solid #2a2a3a;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        .stat-value { font-size: 32px; font-weight: 700; color: #f59e0b; }
        .stat-label { font-size: 11px; color: #6b7280; margin-top: 6px; }
        .stat-card.approved .stat-value { color: #22c55e; }
        .stat-card.rejected .stat-value { color: #ef4444; }
        .stat-card.caution .stat-value { color: #eab308; }
        
        /* Content Area */
        .content-area { flex: 1; overflow-y: auto; padding: 0 24px 24px; }
        
        /* League Tabs */
        .league-tabs {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid #2a2a3a;
        }
        .league-tab {
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-radius: 24px;
            padding: 8px 20px;
            font-size: 13px;
            cursor: pointer;
        }
        .league-tab.active { background: #f59e0b; color: #000; border-color: #f59e0b; }
        
        /* Match Cards */
        .match-card {
            background: #0f0f1a;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            margin-bottom: 12px;
            overflow: hidden;
        }
        .match-card:hover { border-color: #f59e0b; }
        .match-header {
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            cursor: pointer;
            flex-wrap: wrap;
        }
        .match-teams { flex: 2; min-width: 180px; }
        .match-teams .teams { font-size: 15px; font-weight: 600; }
        .match-teams .vs { color: #6b7280; margin: 0 8px; }
        .match-teams .meta { font-size: 11px; color: #6b7280; margin-top: 4px; }
        
        .match-odds { display: flex; gap: 8px; }
        .odd-box {
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-radius: 8px;
            padding: 6px 12px;
            text-align: center;
            min-width: 55px;
        }
        .odd-box .odd-label { font-size: 9px; color: #6b7280; }
        .odd-box .odd-value { font-size: 14px; font-weight: 600; color: #f59e0b; }
        
        .match-verdict {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }
        .verdict-APPROVED { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
        .verdict-CAUTION { background: rgba(234,179,8,0.15); color: #eab308; border: 1px solid rgba(234,179,8,0.3); }
        .verdict-REJECTED { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
        
        .match-prob { text-align: center; min-width: 70px; }
        .match-prob .prob-value { font-size: 16px; font-weight: 700; color: #f59e0b; }
        .match-prob .prob-label { font-size: 9px; color: #6b7280; }
        
        /* Match Detail Panel - THIS IS WHERE LEG DATA GOES */
        .match-detail {
            display: none;
            background: #0a0a0a;
            border-top: 1px solid #2a2a3a;
            padding: 20px;
        }
        .match-detail.show { display: block; }
        
        .detail-tabs {
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            border-bottom: 1px solid #2a2a3a;
            padding-bottom: 8px;
        }
        .detail-tab {
            cursor: pointer;
            padding: 8px 16px;
            font-size: 12px;
            color: #6b7280;
            border-radius: 8px;
        }
        .detail-tab.active { background: #f59e0b; color: #000; font-weight: 600; }
        .detail-content { display: none; }
        .detail-content.active { display: block; }
        
        .info-panel {
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .info-title { font-size: 12px; font-weight: 700; color: #f59e0b; margin-bottom: 12px; }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2a2a4a; }
        .info-label { color: #6b7280; }
        .info-value.good { color: #22c55e; }
        .info-value.bad { color: #ef4444; }
        
        .league-selector { padding: 0 20px 20px; }
        .league-group { margin-bottom: 16px; }
        .league-group-title { font-size: 11px; font-weight: 600; color: #6b7280; margin-bottom: 10px; }
        .league-checkbox {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            cursor: pointer;
        }
        .league-checkbox input { width: 16px; height: 16px; accent-color: #f59e0b; }
        
        .btn-primary {
            background: #f59e0b;
            color: #000;
            border: none;
            padding: 12px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 16px;
        }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .console-log {
            background: #0f0f1a;
            border-top: 1px solid #2a2a3a;
            padding: 8px 20px;
            font-family: monospace;
            font-size: 11px;
            max-height: 100px;
            overflow-y: auto;
        }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #6b7280; }
        .empty-state-icon { font-size: 48px; margin-bottom: 16px; }
        .loading { display: flex; justify-content: center; padding: 60px; }
        .spinner { width: 40px; height: 40px; border: 3px solid #2a2a4a; border-top-color: #f59e0b; border-radius: 50%; animation: spin 0.6s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="logo">
                <h1>⚽ MATCH ORACLE</h1>
                <p>35 Modules Active</p>
            </div>

            <div class="nav-item active" onclick="switchPage('dashboard')">
                <span class="nav-icon">📊</span><span>Dashboard</span>
            </div>
            <div class="nav-item" onclick="switchPage('history')">
                <span class="nav-icon">📜</span><span>History</span>
            </div>

            <div style="flex: 1;"></div>

            <div class="league-selector">
                <div class="league-group-title">📅 Match Date</div>
                <input type="date" id="matchDate" style="width:100%; padding:10px; background:#1a1a2e; border:1px solid #2a2a4a; border-radius:8px; color:#e0e0e0; margin-bottom:16px;">
                
                <div class="league-group-title">🏆 Select Leagues</div>
                <div id="leagueList"></div>
                
                <button id="runScanBtn" class="btn-primary" onclick="runOracle()">🚀 Run Match Oracle</button>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="header">
                <div class="header-title" id="pageTitle">Dashboard</div>
                <div class="header-badge"><span id="moduleCount">35</span> MODULES ACTIVE</div>
            </div>

            <div class="stats-grid" id="statsGrid">
                <div class="stat-card"><div class="stat-value" id="totalScanned">0</div><div class="stat-label">SCANNED</div></div>
                <div class="stat-card approved"><div class="stat-value" id="totalApproved">0</div><div class="stat-label">APPROVED</div></div>
                <div class="stat-card rejected"><div class="stat-value" id="totalRejected">0</div><div class="stat-label">REJECTED</div></div>
                <div class="stat-card caution"><div class="stat-value" id="totalCaution">0</div><div class="stat-label">CAUTION</div></div>
            </div>

            <div class="content-area" id="contentArea">
                <div class="empty-state">
                    <div class="empty-state-icon">🔮</div>
                    <h3>No scan results</h3>
                    <p>Select leagues from the sidebar and click <strong>Run Match Oracle</strong></p>
                </div>
            </div>

            <div class="console-log" id="logBox">Ready. Select leagues and click "Run Match Oracle".</div>
        </div>
    </div>

    <script>
        // ============================================================
        // FRONTEND WITH PROPER LEG DATA ROUTING
        // ============================================================
        
        const BACKEND_URL = window.location.origin;
        let scanResults = null;
        let activeTab = null;
        let scanRunning = false;
        let statusInterval = null;
        
        // League data
        const LEAGUES = {
            "PREMIER_LEAGUE": { name: "Premier League", id: 39 },
            "LA_LIGA": { name: "La Liga", id: 140 },
            "BUNDESLIGA": { name: "Bundesliga", id: 78 },
            "SERIE_A": { name: "Serie A", id: 135 },
            "LIGUE_1": { name: "Ligue 1", id: 61 },
            "EREDIVISIE": { name: "Eredivisie", id: 88 },
            "PRIMEIRA_LIGA": { name: "Primeira Liga", id: 94 },
        };
        
        let selectedLeagues = new Set(['PREMIER_LEAGUE', 'LA_LIGA', 'BUNDESLIGA', 'SERIE_A', 'LIGUE_1']);
        
        function init() {
            document.getElementById('matchDate').value = new Date().toISOString().split('T')[0];
            renderLeagueList();
            loadStatus();
            startStatusPolling();
        }
        
        function renderLeagueList() {
            const container = document.getElementById('leagueList');
            if (!container) return;
            let html = '<div class="league-group">';
            for (const [key, league] of Object.entries(LEAGUES)) {
                const isChecked = selectedLeagues.has(key);
                html += `
                    <div class="league-checkbox" onclick="toggleLeague('${key}')">
                        <input type="checkbox" ${isChecked ? 'checked' : ''} onclick="event.stopPropagation(); toggleLeague('${key}')">
                        <label>${league.name}</label>
                    </div>
                `;
            }
            html += '</div>';
            container.innerHTML = html;
        }
        
        function toggleLeague(key) {
            if (selectedLeagues.has(key)) {
                selectedLeagues.delete(key);
            } else {
                selectedLeagues.add(key);
            }
            renderLeagueList();
        }
        
        function switchPage(page) {
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            if (event && event.target) {
                event.target.closest('.nav-item').classList.add('active');
            }
            document.getElementById('pageTitle').innerText = page === 'dashboard' ? 'Dashboard' : 'Match History';
            document.getElementById('statsGrid').style.display = page === 'dashboard' ? 'grid' : 'none';
            if (page === 'history') loadHistory();
        }
        
        async function runOracle() {
            if (scanRunning) return;
            if (selectedLeagues.size === 0) {
                log('⚠️ Please select at least one league');
                return;
            }
            
            const leagues = Array.from(selectedLeagues);
            const date = document.getElementById('matchDate').value;
            
            scanRunning = true;
            const btn = document.getElementById('runScanBtn');
            btn.textContent = '⏳ Running...';
            btn.disabled = true;
            log(`🚀 Starting scan for ${leagues.length} leagues on ${date}...`);
            
            try {
                const resp = await fetch(`${BACKEND_URL}/api/scan`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ leagues, season: 2026, target_date: date })
                });
                const data = await resp.json();
                if (data.status === 'started') {
                    log('✅ Scan started. Waiting for results...');
                } else {
                    log('❌ Failed: ' + (data.error || 'Unknown'));
                    scanRunning = false;
                    btn.textContent = '🚀 Run Match Oracle';
                    btn.disabled = false;
                }
            } catch (e) {
                log('❌ Error: ' + e.message);
                scanRunning = false;
                btn.textContent = '🚀 Run Match Oracle';
                btn.disabled = false;
            }
        }
        
        function startStatusPolling() {
            if (statusInterval) clearInterval(statusInterval);
            statusInterval = setInterval(loadStatus, 2000);
        }
        
        async function loadStatus() {
            try {
                const resp = await fetch(`${BACKEND_URL}/api/status`);
                const data = await resp.json();
                
                if (data.log && data.log.length) {
                    const last = data.log[data.log.length - 1];
                    const logBox = document.getElementById('logBox');
                    if (logBox && !logBox.innerHTML.includes(last)) {
                        logBox.innerHTML += '\n' + last;
                        logBox.scrollTop = logBox.scrollHeight;
                    }
                }
                
                if (data.results && data.results.leagues && data.results.leagues.length) {
                    scanResults = data.results;
                    if (!activeTab && scanResults.leagues.length) activeTab = scanResults.leagues[0].league;
                    renderResults();
                    if (!data.running) {
                        clearInterval(statusInterval);
                        scanRunning = false;
                        const btn = document.getElementById('runScanBtn');
                        if (btn) {
                            btn.textContent = '🚀 Run Match Oracle';
                            btn.disabled = false;
                        }
                    }
                }
            } catch (e) {
                console.error('Poll error:', e);
            }
        }
        
        function renderResults() {
            if (!scanResults) return;
            
            const totals = scanResults.totals || {};
            document.getElementById('totalScanned').innerText = totals.total || 0;
            document.getElementById('totalApproved').innerText = totals.approved || 0;
            document.getElementById('totalRejected').innerText = totals.rejected || 0;
            document.getElementById('totalCaution').innerText = totals.caution || 0;
            
            const leagues = scanResults.leagues || [];
            const container = document.getElementById('contentArea');
            if (!container) return;
            
            let html = '<div class="league-tabs">';
            for (const league of leagues) {
                html += `<div class="league-tab ${activeTab === league.league ? 'active' : ''}" onclick="switchLeagueTab('${league.league.replace(/'/g, "\\'")}')">${league.league} (${league.matches.length})</div>`;
            }
            html += '</div>';
            
            const activeLeague = leagues.find(l => l.league === activeTab);
            if (activeLeague) {
                for (let i = 0; i < activeLeague.matches.length; i++) {
                    html += renderMatchCard(activeLeague.matches[i], i);
                }
            }
            container.innerHTML = html;
        }
        
        function renderMatchCard(m, idx) {
            const status = m.final_status || 'PENDING';
            const verClass = `verdict-${status}`;
            const oracle = m.oracle || {};
            const prob = oracle.model_prob ? (oracle.model_prob * 100).toFixed(1) + '%' : '—';
            const edge = oracle.edge ? (oracle.edge * 100).toFixed(1) + '%' : '—';
            const home = m.match ? m.match.split(' vs ')[0] : '?';
            const away = m.match ? m.match.split(' vs ')[1] : '?';
            
            return `
                <div class="match-card">
                    <div class="match-header" onclick="toggleDetail(${idx})">
                        <div class="match-teams">
                            <div class="teams">${escapeHtml(home)}<span class="vs">vs</span>${escapeHtml(away)}</div>
                            <div class="meta">${m.match_date || ''} · ${m.selection || 'Unknown'}</div>
                        </div>
                        <div class="match-odds">
                            <div class="odd-box"><div class="odd-label">H</div><div class="odd-value">${m.home_odds || '-'}</div></div>
                            <div class="odd-box"><div class="odd-label">D</div><div class="odd-value">${m.draw_odds || '-'}</div></div>
                            <div class="odd-box"><div class="odd-label">A</div><div class="odd-value">${m.away_odds || '-'}</div></div>
                        </div>
                        <div class="match-verdict ${verClass}">${status}</div>
                        <div class="match-prob"><div class="prob-value">${prob}</div><div class="prob-label">PROB</div></div>
                        <div class="match-prob"><div class="prob-value">${edge}</div><div class="prob-label">EDGE</div></div>
                    </div>
                    <div class="match-detail" id="detail-${idx}">
                        ${renderLegData(m)}
                    </div>
                </div>
            `;
        }
        
        function renderLegData(m) {
            // Extract all leg data from the match object
            const oracle = m.oracle || {};
            const m3 = m.m3_probability || {};
            const m4 = m.m4_prefilter || {};
            const m5 = m.m5_forensics || {};
            const m8 = m.m8_dual || {};
            const m9 = m.m9_underdog || {};
            const m11 = m.m11_master || {};
            const status = m.final_status || 'PENDING';
            
            return `
                <div class="detail-tabs">
                    <div class="detail-tab active" onclick="switchDetailTab(this, 'oracle')">Oracle (M11)</div>
                    <div class="detail-tab" onclick="switchDetailTab(this, 'probability')">Probability (M3)</div>
                    <div class="detail-tab" onclick="switchDetailTab(this, 'prefilter')">Pre-Filter (M4)</div>
                    <div class="detail-tab" onclick="switchDetailTab(this, 'analysis')">Analysis (M8/M9)</div>
                    <div class="detail-tab" onclick="switchDetailTab(this, 'notes')">Notes & Risk</div>
                </div>
                
                <!-- Oracle Tab -->
                <div class="detail-content active" id="oracle-tab">
                    <div class="info-panel">
                        <div class="info-title">🔮 M11 Master Aggregation - Final Verdict</div>
                        <div class="info-row"><span class="info-label">Verdict</span><span class="info-value ${status === 'APPROVED' ? 'good' : status === 'REJECTED' ? 'bad' : ''}">${status}</span></div>
                        <div class="info-row"><span class="info-label">Confidence</span><span class="info-value">${m.final_confidence || 'LOW'}</span></div>
                        <div class="info-row"><span class="info-label">Selection</span><span class="info-value">${m.selection || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Odds</span><span class="info-value">${m.odds || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Model Probability</span><span class="info-value">${(oracle.model_prob * 100 || 0).toFixed(1)}%</span></div>
                        <div class="info-row"><span class="info-label">Edge</span><span class="info-value ${oracle.edge > 0 ? 'good' : 'bad'}">${(oracle.edge * 100 || 0).toFixed(1)}%</span></div>
                        <div class="info-row"><span class="info-label">Failure Score (M5)</span><span class="info-value ${oracle.failure_score < 4.5 ? 'good' : 'bad'}">${oracle.failure_score || 0}</span></div>
                        <div class="info-row"><span class="info-label">Pre-Filter (M4)</span><span class="info-value ${oracle.pre_filter_passed ? 'good' : 'bad'}">${oracle.pre_filter_passed ? 'PASSED' : 'FAILED'}</span></div>
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">📊 M11 Master Metrics</div>
                        <div class="info-row"><span class="info-label">Weighted Score</span><span class="info-value">${m11.weighted_score || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Clean Weighted Score</span><span class="info-value">${m11.clean_weighted_score || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Conflict Detected</span><span class="info-value ${m11.conflict_detected ? 'bad' : 'good'}">${m11.conflict_detected ? 'YES' : 'NO'}</span></div>
                        <div class="info-row"><span class="info-label">Reliability Score</span><span class="info-value">${m11.reliability_score || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Stake Multiplier</span><span class="info-value">${m11.final_stake_multiplier || '-'}x</span></div>
                    </div>
                </div>
                
                <!-- Probability Tab -->
                <div class="detail-content" id="probability-tab">
                    <div class="info-panel">
                        <div class="info-title">📊 M3 Probability Engine</div>
                        <div class="info-row"><span class="info-label">Home Win Implied</span><span class="info-value">${m3.home_implied || '-'}%</span></div>
                        <div class="info-row"><span class="info-label">Draw Implied</span><span class="info-value">${m3.draw_implied || '-'}%</span></div>
                        <div class="info-row"><span class="info-label">Away Win Implied</span><span class="info-value">${m3.away_implied || '-'}%</span></div>
                        <div class="info-row"><span class="info-label">Bookmaker Margin</span><span class="info-value">${m3.bookmaker_margin || '-'}%</span></div>
                        <div class="info-row"><span class="info-label">Model Home Probability</span><span class="info-value">${m3.model_home_prob || '-'}%</span></div>
                        <div class="info-row"><span class="info-label">Edge Percentage</span><span class="info-value ${oracle.edge > 0 ? 'good' : 'bad'}">${m3.edge_pct || '-'}%</span></div>
                    </div>
                </div>
                
                <!-- Pre-Filter Tab -->
                <div class="detail-content" id="prefilter-tab">
                    <div class="info-panel">
                        <div class="info-title">🚪 M4 Asymmetric Pre-Filter (8-Point Gate)</div>
                        <div class="info-row"><span class="info-label">Passed</span><span class="info-value ${m4.passed ? 'good' : 'bad'}">${m4.passed ? 'PASSED' : 'FAILED'}</span></div>
                        <div class="info-row"><span class="info-label">Checks Passed</span><span class="info-value">${m4.checks_passed || 0}/8</span></div>
                        ${(m4.details || []).map(d => `
                            <div class="info-row"><span class="info-label">${d.check}</span><span class="info-value ${d.result === 'PASS' ? 'good' : 'bad'}">${d.result}</span></div>
                        `).join('')}
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">🔬 M5 Forensic Checks</div>
                        <div class="info-row"><span class="info-label">Failure Score</span><span class="info-value ${m5.failure_score <= 4.5 ? 'good' : 'bad'}">${m5.failure_score || 0} / ${m5.threshold || 4.5}</span></div>
                        <div class="info-row"><span class="info-label">Passed</span><span class="info-value ${m5.passed ? 'good' : 'bad'}">${m5.passed ? 'YES' : 'NO'}</span></div>
                    </div>
                </div>
                
                <!-- Analysis Tab -->
                <div class="detail-content" id="analysis-tab">
                    <div class="info-panel">
                        <div class="info-title">🔄 M8 Dual Pattern Engine</div>
                        <div class="info-row"><span class="info-label">Dual Risk Level</span><span class="info-value">${m8.dual_risk_level || 'UNKNOWN'}</span></div>
                        <div class="info-row"><span class="info-label">Clean Risk Score</span><span class="info-value">${m8.clean_risk_score || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Conflict Detected</span><span class="info-value ${m8.conflict_detected ? 'bad' : 'good'}">${m8.conflict_detected ? 'YES' : 'NO'}</span></div>
                        <div class="info-row"><span class="info-label">Conflict Severity</span><span class="info-value">${m8.conflict_severity || 'NONE'}</span></div>
                        <div class="info-row"><span class="info-label">Underdog Threat</span><span class="info-value">${m8.underdog_threat || 'NONE'}</span></div>
                        <div class="info-row"><span class="info-label">Patterns Reliable</span><span class="info-value">${m8.patterns_reliable ? 'YES' : 'NO'}</span></div>
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">⚠️ M9 Underdog Scanner</div>
                        <div class="info-row"><span class="info-label">Threat Level</span><span class="info-value">${m9.threat_level || 'NONE'}</span></div>
                        <div class="info-row"><span class="info-label">Clean Threat Level</span><span class="info-value">${m9.clean_threat_level || 'NONE'}</span></div>
                        <div class="info-row"><span class="info-label">Recommendation</span><span class="info-value">${m9.recommendation || 'NONE'}</span></div>
                        <div class="info-row"><span class="info-label">Pattern Count</span><span class="info-value">${m9.pattern_count || 0}</span></div>
                        <div class="info-row"><span class="info-label">Underdog Edge</span><span class="info-value">${m9.underdog_edge || 0}</span></div>
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">🏆 M10 Season Tally Matrix</div>
                        <div class="info-row"><span class="info-label">Matrix Useful</span><span class="info-value">${m10?.matrix_useful ? 'YES' : 'NO'}</span></div>
                        <div class="info-row"><span class="info-label">Combined Risk Flag</span><span class="info-value">${m10?.combined_risk_flag || 'NONE'}</span></div>
                        <div class="info-row"><span class="info-label">Bilateral Prediction</span><span class="info-value">${m10?.bilateral_prediction || 'UNKNOWN'}</span></div>
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">📜 M26 Match Context</div>
                        <div class="info-row"><span class="info-label">Context Label</span><span class="info-value">${m26?.context_label || 'UNKNOWN'}</span></div>
                        <div class="info-row"><span class="info-label">Match Importance</span><span class="info-value">${m26?.match_importance || '-'}</span></div>
                        <div class="info-row"><span class="info-label">Dead Rubber</span><span class="info-value">${m26?.is_dead_rubber ? 'YES' : 'NO'}</span></div>
                        <div class="info-row"><span class="info-label">Rivalry/Derby</span><span class="info-value">${m26?.is_rivalry || m26?.is_derby ? 'YES' : 'NO'}</span></div>
                        <div class="info-row"><span class="info-label">Six Pointer</span><span class="info-value">${m26?.is_six_pointer ? 'YES' : 'NO'}</span></div>
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">🤝 M27 H2H Analysis</div>
                        <div class="info-row"><span class="info-label">H2H Score</span><span class="info-value">${m27?.h2h_score || 0}</span></div>
                        <div class="info-row"><span class="info-label">H2H Label</span><span class="info-value">${m27?.h2h_label || 'UNKNOWN'}</span></div>
                        <div class="info-row"><span class="info-label">Draw Boost Factor</span><span class="info-value">${m27?.draw_boost_factor || '1.00'}x</span></div>
                        <div class="info-row"><span class="info-label">Draw Rate</span><span class="info-value">${((m27?.draw_rate || 0) * 100).toFixed(0)}%</span></div>
                    </div>
                </div>
                
                <!-- Notes Tab -->
                <div class="detail-content" id="notes-tab">
                    <div class="info-panel">
                        <div class="info-title">📝 M11 Decision Notes</div>
                        ${(m.decision_notes || []).map(n => `<div class="info-row"><span class="info-label">•</span><span class="info-value">${n}</span></div>`).join('') || '<div class="info-row"><span class="info-label">No notes available</span></div>'}
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">⚠️ Risk Flags</div>
                        ${(m.risk_flags || []).map(f => `<div class="info-row"><span class="info-label">⚠️</span><span class="info-value bad">${f}</span></div>`).join('') || '<div class="info-row"><span class="info-label">No risk flags</span></div>'}
                    </div>
                    
                    <div class="info-panel">
                        <div class="info-title">🔧 Module Output Logs (Last 10)</div>
                        ${(m.check_log || []).slice(-10).map(log => `<div class="info-row"><span class="info-label">•</span><span class="info-value" style="font-family:monospace; font-size:10px;">${log}</span></div>`).join('') || '<div class="info-row"><span class="info-label">No logs available</span></div>'}
                    </div>
                </div>
            `;
        }
        
        async function loadHistory() {
            const container = document.getElementById('contentArea');
            container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
            
            try {
                const resp = await fetch(`${BACKEND_URL}/api/history`);
                const data = await resp.json();
                
                if (data.history && data.history.length) {
                    let html = '<div class="league-tabs"><div class="league-tab active">Recent Matches</div></div>';
                    for (let i = 0; i < data.history.length; i++) {
                        const h = data.history[i];
                        const verClass = `verdict-${h.verdict || 'PENDING'}`;
                        html += `
                            <div class="match-card">
                                <div class="match-header" onclick="toggleDetail(${i})">
                                    <div class="match-teams">
                                        <div class="teams">${escapeHtml(h.home)}<span class="vs">vs</span>${escapeHtml(h.away)}</div>
                                        <div class="meta">${h.league || 'Unknown'} | ${h.date || ''}</div>
                                    </div>
                                    <div class="match-verdict ${verClass}">${h.verdict || 'PENDING'}</div>
                                    <div class="match-prob"><div class="prob-value">${((h.edge || 0) * 100).toFixed(1)}%</div><div class="prob-label">EDGE</div></div>
                                </div>
                            </div>
                        `;
                    }
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📜</div><h3>No history yet</h3><p>Run scans to see results here</p></div>';
                }
            } catch (e) {
                container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">❌</div><h3>Error</h3><p>${e.message}</p></div>`;
            }
        }
        
        function switchLeagueTab(league) { activeTab = league; renderResults(); }
        function toggleDetail(idx) { document.getElementById(`detail-${idx}`)?.classList.toggle('show'); }
        function switchDetailTab(el, tabName) {
            const parent = el.closest('.match-detail');
            if (!parent) return;
            parent.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
            parent.querySelectorAll('.detail-content').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            document.getElementById(`${tabName}-tab`)?.classList.add('active');
        }
        function escapeHtml(text) { if (!text) return ''; return text.replace(/[&<>]/g, function(m) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}[m]; }); }
        function log(msg) {
            const logBox = document.getElementById('logBox');
            if (!logBox) return;
            const ts = new Date().toLocaleTimeString();
            logBox.innerHTML += `\n[${ts}] ${msg}`;
            logBox.scrollTop = logBox.scrollHeight;
        }
        
        init();
    </script>
</body>
</html>
