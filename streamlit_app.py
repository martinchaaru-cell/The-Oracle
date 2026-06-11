<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Match Oracle - Football Intelligence</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #0a0a0a 0%, #0f0f0f 100%);
      color: #e0e0e0;
      height: 100vh;
      overflow: hidden;
    }
    
    .app {
      display: flex;
      height: 100vh;
    }
    
    /* Sidebar - Black/Dark theme */
    .sidebar {
      width: 280px;
      background: #0a0a0a;
      border-right: 1px solid #2a2a2a;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      padding: 20px;
      gap: 20px;
      flex-shrink: 0;
    }
    
    .logo {
      font-size: 1.5rem;
      font-weight: 800;
      background: linear-gradient(135deg, #FFD700, #FFA500);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 5px;
    }
    
    .logo span {
      font-size: 0.7rem;
      color: #B8860B;
      font-weight: normal;
      display: block;
    }
    
    .section-title {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      color: #FFD700;
      margin-bottom: 10px;
      letter-spacing: 1px;
    }
    
    select, input {
      width: 100%;
      padding: 10px 12px;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 8px;
      color: #e0e0e0;
      font-size: 0.8rem;
      margin-bottom: 8px;
    }
    
    select:focus, input:focus {
      outline: none;
      border-color: #FFD700;
    }
    
    button {
      background: linear-gradient(135deg, #FFD700, #FFA500);
      color: #000;
      font-weight: bold;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 0.85rem;
      width: 100%;
    }
    
    button:hover {
      opacity: 0.9;
      transform: translateY(-1px);
    }
    
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
    
    /* Quick leagues */
    .quick-leagues {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }
    
    .league-btn {
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 20px;
      padding: 5px 12px;
      font-size: 0.7rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .league-btn:hover {
      background: #FFD700;
      color: #000;
      border-color: #FFD700;
    }
    
    .league-btn.active {
      background: #FFD700;
      color: #000;
      border-color: #FFD700;
    }
    
    /* Main content */
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    
    .main-header {
      background: #0a0a0a;
      border-bottom: 1px solid #2a2a2a;
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .header-title {
      font-size: 1.3rem;
      font-weight: 700;
      background: linear-gradient(135deg, #FFD700, #FFA500);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .header-subtitle {
      font-size: 0.7rem;
      color: #B8860B;
    }
    
    /* Summary cards */
    .summary-bar {
      background: #0a0a0a;
      border-bottom: 1px solid #2a2a2a;
      padding: 12px 24px;
      display: flex;
      gap: 16px;
    }
    
    .summary-card {
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      padding: 12px 20px;
      min-width: 100px;
      text-align: center;
    }
    
    .summary-card .value {
      font-size: 1.8rem;
      font-weight: 700;
      color: #FFD700;
    }
    
    .summary-card .label {
      font-size: 0.7rem;
      color: #888;
      text-transform: uppercase;
      margin-top: 4px;
    }
    
    .summary-card.approved .value { color: #00FF88; }
    .summary-card.rejected .value { color: #FF4444; }
    .summary-card.caution .value { color: #FFA500; }
    
    /* Content area */
    .content-area {
      flex: 1;
      overflow-y: auto;
      padding: 20px 24px;
    }
    
    /* League tabs */
    .league-tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    
    .league-tab {
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 20px;
      padding: 6px 16px;
      font-size: 0.75rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .league-tab:hover {
      background: #2a2a2a;
    }
    
    .league-tab.active {
      background: #FFD700;
      color: #000;
      border-color: #FFD700;
    }
    
    /* Match card */
    .match-card {
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      margin-bottom: 8px;
      overflow: hidden;
    }
    
    .match-card:hover {
      border-color: #FFD700;
    }
    
    .match-row {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      gap: 16px;
      cursor: pointer;
    }
    
    .match-row:hover {
      background: rgba(255, 215, 0, 0.05);
    }
    
    .match-teams {
      flex: 2;
      min-width: 0;
    }
    
    .match-teams .teams {
      font-size: 0.85rem;
      font-weight: 600;
    }
    
    .match-teams .meta {
      font-size: 0.65rem;
      color: #666;
      margin-top: 2px;
    }
    
    .match-odds {
      display: flex;
      gap: 6px;
    }
    
    .odd-box {
      background: #0a0a0a;
      border: 1px solid #2a2a2a;
      border-radius: 6px;
      padding: 4px 8px;
      text-align: center;
      min-width: 50px;
    }
    
    .odd-label {
      font-size: 0.55rem;
      color: #666;
    }
    
    .odd-value {
      font-size: 0.8rem;
      font-weight: 600;
      color: #FFD700;
    }
    
    .verdict-badge {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.65rem;
      font-weight: 600;
      min-width: 80px;
      text-align: center;
    }
    
    .verdict-APPROVED {
      background: rgba(0, 255, 136, 0.15);
      color: #00FF88;
      border: 1px solid rgba(0, 255, 136, 0.3);
    }
    
    .verdict-REJECTED {
      background: rgba(255, 68, 68, 0.15);
      color: #FF4444;
      border: 1px solid rgba(255, 68, 68, 0.3);
    }
    
    .verdict-CAUTION {
      background: rgba(255, 165, 0, 0.15);
      color: #FFA500;
      border: 1px solid rgba(255, 165, 0, 0.3);
    }
    
    .match-prob, .match-edge {
      text-align: center;
      min-width: 60px;
    }
    
    .prob-label, .edge-label {
      font-size: 0.55rem;
      color: #666;
    }
    
    .match-prob .value {
      font-size: 0.8rem;
      font-weight: 600;
      color: #FFD700;
    }
    
    .match-edge .value {
      font-size: 0.8rem;
      font-weight: 600;
    }
    
    .match-edge .positive { color: #00FF88; }
    .match-edge .negative { color: #FF4444; }
    
    /* Detail panel */
    .match-detail {
      display: none;
      background: #0f0f0f;
      border-top: 1px solid #2a2a2a;
      padding: 16px;
    }
    
    .match-detail.show {
      display: block;
    }
    
    .detail-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
      border-bottom: 1px solid #2a2a2a;
      padding-bottom: 8px;
    }
    
    .detail-tab {
      padding: 6px 16px;
      font-size: 0.75rem;
      cursor: pointer;
      border-radius: 6px;
      transition: all 0.2s;
    }
    
    .detail-tab:hover {
      background: #2a2a2a;
    }
    
    .detail-tab.active {
      background: #FFD700;
      color: #000;
    }
    
    .detail-content {
      display: none;
    }
    
    .detail-content.active {
      display: block;
    }
    
    .detail-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 12px;
    }
    
    .detail-item {
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 8px;
      padding: 12px;
    }
    
    .detail-item .label {
      font-size: 0.6rem;
      color: #FFD700;
      text-transform: uppercase;
      margin-bottom: 4px;
    }
    
    .detail-item .value {
      font-size: 0.8rem;
      font-weight: 600;
    }
    
    .risk-flags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    
    .risk-flag {
      background: rgba(255, 68, 68, 0.15);
      border: 1px solid rgba(255, 68, 68, 0.3);
      color: #FF4444;
      border-radius: 4px;
      padding: 3px 8px;
      font-size: 0.65rem;
    }
    
    .console-box {
      background: #0a0a0a;
      border-top: 1px solid #2a2a2a;
      padding: 8px 16px;
      font-family: monospace;
      font-size: 0.65rem;
      max-height: 100px;
      overflow-y: auto;
      color: #888;
    }
    
    .empty-state {
      text-align: center;
      padding: 60px;
      color: #666;
    }
    
    .empty-state h3 {
      font-size: 1.1rem;
      margin-bottom: 8px;
      color: #888;
    }
    
    .spinner {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 2px solid #2a2a2a;
      border-top-color: #FFD700;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
      margin-right: 8px;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
<div class="app">
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="logo">
      MATCH ORACLE
      <span>Football Intelligence</span>
    </div>
    
    <div class="section">
      <div class="section-title">Match Date</div>
      <input type="date" id="matchDate" value="2026-06-11">
    </div>
    
    <div class="section">
      <div class="section-title">Season</div>
      <input type="number" id="season" value="2026">
    </div>
    
    <div class="section">
      <div class="section-title">Quick Leagues</div>
      <div class="quick-leagues" id="quickLeagues"></div>
    </div>
    
    <div class="section">
      <div class="section-title">API Keys (Optional)</div>
      <input type="password" id="apiKey" placeholder="API-Football Key">
      <input type="password" id="oddsKey" placeholder="Odds API Key">
    </div>
    
    <div style="margin-top: auto">
      <button id="runBtn" onclick="runScan()">▶ RUN MATCH ORACLE</button>
    </div>
  </div>

  <!-- Main Content -->
  <div class="main">
    <div class="main-header">
      <div>
        <div class="header-title">SCAN RESULTS</div>
        <div class="header-subtitle" id="scanDate">No scan yet</div>
      </div>
      <div class="header-subtitle" id="liveClock">--:--:-- GMT+3</div>
    </div>

    <div class="summary-bar" id="summaryBar">
      <div class="summary-card">
        <div class="value" id="totalScanned">0</div>
        <div class="label">Scanned</div>
      </div>
      <div class="summary-card approved">
        <div class="value" id="totalApproved">0</div>
        <div class="label">Approved</div>
      </div>
      <div class="summary-card rejected">
        <div class="value" id="totalRejected">0</div>
        <div class="label">Rejected</div>
      </div>
      <div class="summary-card caution">
        <div class="value" id="totalCaution">0</div>
        <div class="label">Caution</div>
      </div>
    </div>

    <div class="content-area" id="contentArea">
      <div class="empty-state">
        <div style="font-size: 48px; margin-bottom: 16px;">🎯</div>
        <h3>Ready to scan</h3>
        <p>Select leagues and click RUN MATCH ORACLE</p>
      </div>
    </div>

    <div class="console-box" id="logBox">Ready. Select leagues and click RUN MATCH ORACLE.</div>
  </div>
</div>

<script>
  // Live clock
  function updateClock() {
    const now = new Date();
    const options = { timeZone: 'Africa/Nairobi', hour12: false };
    const timeStr = now.toLocaleTimeString('en-US', options);
    document.getElementById('liveClock').innerHTML = timeStr + ' GMT+3';
  }
  setInterval(updateClock, 1000);
  updateClock();

  // League data
  const LEAGUES = [
    { key: "PREMIER_LEAGUE", name: "Premier League", id: 39, country: "England" },
    { key: "LA_LIGA", name: "La Liga", id: 140, country: "Spain" },
    { key: "BUNDESLIGA", name: "Bundesliga", id: 78, country: "Germany" },
    { key: "SERIE_A", name: "Serie A", id: 135, country: "Italy" },
    { key: "LIGUE_1", name: "Ligue 1", id: 61, country: "France" },
    { key: "EREDIVISIE", name: "Eredivisie", id: 88, country: "Netherlands" }
  ];

  let selectedLeagues = new Set();
  let scanResults = null;
  let activeTab = null;
  let scanRunning = false;
  let statusInterval = null;

  function renderQuickLeagues() {
    const container = document.getElementById('quickLeagues');
    container.innerHTML = LEAGUES.map(l => 
      `<div class="league-btn ${selectedLeagues.has(l.key) ? 'active' : ''}" onclick="toggleLeague('${l.key}')">${l.name}</div>`
    ).join('');
  }

  function toggleLeague(key) {
    if (selectedLeagues.has(key)) {
      selectedLeagues.delete(key);
    } else {
      selectedLeagues.add(key);
    }
    renderQuickLeagues();
  }

  async function runScan() {
    if (scanRunning) return;
    if (selectedLeagues.size === 0) {
      alert('Please select at least one league');
      return;
    }

    const leagues = Array.from(selectedLeagues);
    const date = document.getElementById('matchDate').value;
    const season = parseInt(document.getElementById('season').value);
    const apiKey = document.getElementById('apiKey').value;
    const oddsKey = document.getElementById('oddsKey').value;

    scanRunning = true;
    document.getElementById('runBtn').textContent = '⏳ RUNNING...';
    document.getElementById('runBtn').disabled = true;
    log('🚀 Starting scan...');

    try {
      const resp = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          leagues, 
          season, 
          target_date: date,
          football_key: apiKey,
          odds_key: oddsKey
        })
      });
      const data = await resp.json();
      if (data.status === 'started') {
        log('✅ Scan started. Waiting for results...');
        startPolling();
      } else {
        log('❌ Failed: ' + (data.error || 'Unknown'));
      }
    } catch (e) {
      log('❌ Error: ' + e.message);
    }
  }

  function startPolling() {
    if (statusInterval) clearInterval(statusInterval);
    statusInterval = setInterval(async () => {
      try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        
        // Update logs
        if (data.log && data.log.length > 0) {
          const logBox = document.getElementById('logBox');
          const last = data.log[data.log.length - 1];
          if (!logBox.innerHTML.includes(last)) {
            logBox.innerHTML = data.log.slice(-50).join('\n');
            logBox.scrollTop = logBox.scrollHeight;
          }
        }
        
        // Update results
        if (data.results && data.results.leagues && data.results.leagues.length > 0) {
          scanResults = data.results;
          if (!activeTab && scanResults.leagues[0]) activeTab = scanResults.leagues[0].league;
          renderResults();
        }
        
        if (!data.running) {
          clearInterval(statusInterval);
          scanRunning = false;
          document.getElementById('runBtn').textContent = '▶ RUN MATCH ORACLE';
          document.getElementById('runBtn').disabled = false;
        }
      } catch (e) {
        console.error('Poll error:', e);
      }
    }, 2000);
  }

  function renderResults() {
    if (!scanResults) return;
    
    const totals = scanResults.totals || {};
    document.getElementById('totalScanned').textContent = totals.total || 0;
    document.getElementById('totalApproved').textContent = totals.approved || 0;
    document.getElementById('totalRejected').textContent = totals.rejected || 0;
    document.getElementById('totalCaution').textContent = totals.caution || 0;
    document.getElementById('scanDate').textContent = scanResults.date_fetched || 'Scan complete';

    const leagues = scanResults.leagues || [];
    const container = document.getElementById('contentArea');
    
    let html = '<div class="league-tabs">';
    for (const league of leagues) {
      const isActive = activeTab === league.league;
      html += `<div class="league-tab ${isActive ? 'active' : ''}" onclick="switchTab('${league.league}')">${league.league} <span style="opacity:0.6">(${league.matches.length})</span></div>`;
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
    const verdictClass = status.includes('APPROVED') ? 'APPROVED' : status.includes('CAUTION') ? 'CAUTION' : 'REJECTED';
    const prob = m.oracle?.model_prob ? (m.oracle.model_prob * 100).toFixed(1) + '%' : '—';
    const edge = m.oracle?.edge ? (m.oracle.edge * 100).toFixed(1) + '%' : '—';
    const edgeClass = m.oracle?.edge > 0 ? 'positive' : (m.oracle?.edge < 0 ? 'negative' : '');
    const home = m.match ? m.match.split(' vs ')[0] : '?';
    const away = m.match ? m.match.split(' vs ')[1] : '?';
    
    return `
      <div class="match-card">
        <div class="match-row" onclick="toggleDetail(${idx})">
          <div class="match-teams">
            <div class="teams">${home} <span style="color:#666;">vs</span> ${away}</div>
            <div class="meta">${m.match_date || ''} · ${m.selection || '?'}</div>
          </div>
          <div class="match-odds">
            <div class="odd-box"><div class="odd-label">H</div><div class="odd-value">${m.home_odds || '?'}</div></div>
            <div class="odd-box"><div class="odd-label">D</div><div class="odd-value">${m.draw_odds || '?'}</div></div>
            <div class="odd-box"><div class="odd-label">A</div><div class="odd-value">${m.away_odds || '?'}</div></div>
          </div>
          <div class="verdict-badge verdict-${verdictClass}">${status}</div>
          <div class="match-prob"><div class="prob-label">PROB</div><div class="value">${prob}</div></div>
          <div class="match-edge"><div class="edge-label">EDGE</div><div class="value ${edgeClass}">${edge}</div></div>
        </div>
        <div class="match-detail" id="detail-${idx}">
          <div class="detail-tabs">
            <div class="detail-tab active" onclick="switchDetailTab(${idx}, 'leg')">Leg Data</div>
            <div class="detail-tab" onclick="switchDetailTab(${idx}, 'forensic')">Forensic Report</div>
          </div>
          <div class="detail-content active" id="leg-${idx}">
            <div class="detail-grid">
              <div class="detail-item"><div class="label">Match</div><div class="value">${m.match}</div></div>
              <div class="detail-item"><div class="label">Selection</div><div class="value">${m.selection || '—'}</div></div>
              <div class="detail-item"><div class="label">Odds</div><div class="value">${m.odds || '—'}</div></div>
              <div class="detail-item"><div class="label">Model Probability</div><div class="value">${prob}</div></div>
              <div class="detail-item"><div class="label">Edge</div><div class="value ${edgeClass}">${edge}</div></div>
              <div class="detail-item"><div class="label">Pre-Filter</div><div class="value">${m.oracle?.pre_filter_passed ? 'PASSED' : 'FAILED'} (${m.oracle?.pre_filter_checks || 0}/8)</div></div>
              <div class="detail-item"><div class="label">Dual Risk</div><div class="value">${m.oracle?.dual_risk_level || '—'}</div></div>
            </div>
          </div>
          <div class="detail-content" id="forensic-${idx}">
            <div class="detail-grid">
              <div class="detail-item" style="grid-column:1/-1">
                <div class="label">Risk Flags</div>
                <div class="risk-flags">${(m.risk_flags || []).map(f => `<span class="risk-flag">${f}</span>`).join('') || 'None'}</div>
              </div>
              <div class="detail-item" style="grid-column:1/-1">
                <div class="label">Decision Notes</div>
                <div class="value" style="font-size:0.7rem;">${(m.decision_notes || []).map(n => `• ${n}`).join('<br>') || 'None'}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  function switchTab(league) {
    activeTab = league;
    renderResults();
  }

  function toggleDetail(idx) {
    const el = document.getElementById('detail-' + idx);
    if (el) el.classList.toggle('show');
  }

  function switchDetailTab(idx, tab) {
    const parent = document.getElementById('detail-' + idx);
    if (!parent) return;
    parent.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
    parent.querySelectorAll('.detail-content').forEach(c => c.classList.remove('active'));
    if (tab === 'leg') {
      parent.querySelector('.detail-tab:first-child').classList.add('active');
      document.getElementById('leg-' + idx).classList.add('active');
    } else {
      parent.querySelector('.detail-tab:last-child').classList.add('active');
      document.getElementById('forensic-' + idx).classList.add('active');
    }
  }

  function log(msg) {
    const logBox = document.getElementById('logBox');
    const ts = new Date().toLocaleTimeString();
    logBox.innerHTML = `[${ts}] ${msg}\n` + logBox.innerHTML;
    if (logBox.innerHTML.split('\n').length > 100) {
      logBox.innerHTML = logBox.innerHTML.split('\n').slice(0, 100).join('\n');
    }
  }

  renderQuickLeagues();
  startPolling();
</script>
</body>
</html>
