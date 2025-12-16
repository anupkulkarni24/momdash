<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Momentum Dashboard Enhanced Trading Signals</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --bg: #0b1020;
      --bg-card: #111729;
      --bg-alt: #151b30;
      --accent: #38bdf8;
      --accent-soft: rgba(56,189,248,0.12);
      --text: #e5e7eb;
      --muted: #9ca3af;
      --danger: #f97373;
      --success: #22c55e;
      --warning: #facc15;
      --border: #1f2937;
      --radius-lg: 14px;
      --radius-sm: 8px;
      --shadow-soft: 0 18px 40px rgba(0,0,0,0.45);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #111827 0, #020617 55%);
      color: var(--text);
      min-height: 100vh;
    }

    .page {
      max-width: 1600px;
      margin: 0 auto;
      padding: 20px 16px 40px;
    }

    header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 18px;
    }

    .title-block h1 {
      margin: 0;
      font-size: 1.8rem;
      letter-spacing: 0.03em;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .tag-pill {
      font-size: 0.7rem;
      padding: 3px 9px;
      border-radius: 999px;
      border: 1px solid var(--accent-soft);
      color: var(--accent);
      background: rgba(15,23,42,0.8);
    }

    .subtitle {
      margin: 4px 0 0;
      font-size: 0.86rem;
      color: var(--muted);
      max-width: 640px;
    }

    /* Market Cap Quick Filter Buttons */
    .mcap-filters {
      display: flex;
      gap: 8px;
      margin-top: 12px;
      flex-wrap: wrap;
    }

    .mcap-btn {
      padding: 8px 16px;
      border-radius: 20px;
      border: 2px solid var(--border);
      background: rgba(15,23,42,0.9);
      color: var(--muted);
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      transition: all 0.3s;
    }

    .mcap-btn:hover {
      border-color: var(--accent);
      color: var(--accent);
      transform: translateY(-2px);
    }

    .mcap-btn.active {
      background: linear-gradient(135deg, var(--accent), #6366f1);
      border-color: var(--accent);
      color: white;
      box-shadow: 0 4px 15px rgba(56,189,248,0.4);
    }

    /* Tabs */
    .tabs {
      display: inline-flex;
      margin-top: 14px;
      border-radius: 999px;
      padding: 3px;
      background: rgba(15,23,42,0.9);
      border: 1px solid rgba(30,64,175,0.7);
    }

    .tab-btn {
      border: none;
      background: transparent;
      color: var(--muted);
      padding: 6px 16px;
      border-radius: 999px;
      font-size: 0.83rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.18s ease;
      white-space: nowrap;
    }

    .tab-btn span.icon {
      font-size: 0.9rem;
    }

    .tab-btn.active {
      background: linear-gradient(135deg, #38bdf8, #6366f1);
      color: white;
      box-shadow: 0 0 0 1px rgba(15,23,42,0.7);
    }

    .tab-btn:not(.active):hover {
      background: rgba(30,64,175,0.55);
      color: #e5e7eb;
    }

    /* Layout */
    .grid {
      display: grid;
      grid-template-columns: minmax(0,2.5fr) minmax(0,1fr);
      gap: 14px;
      margin-top: 18px;
    }

    @media (max-width: 1100px) {
      .grid {
        grid-template-columns: minmax(0,1fr);
      }
    }

    .card {
      background: linear-gradient(145deg, var(--bg-card), #020617);
      border-radius: var(--radius-lg);
      border: 1px solid var(--border);
      padding: 14px 14px 12px;
      box-shadow: var(--shadow-soft);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 10px;
      margin-bottom: 10px;
    }

    .card-title {
      font-size: 0.96rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .card-title .dot {
      width: 6px;
      height: 6px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 10px rgba(56,189,248,0.9);
    }

    .card-subtitle {
      font-size: 0.78rem;
      color: var(--muted);
    }

    /* Summary badges */
    .summary-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 8px;
      margin-bottom: 10px;
    }

    .summary-pill {
      border-radius: var(--radius-sm);
      background: radial-gradient(circle at top left, rgba(56,189,248,0.2), rgba(15,23,42,0.95));
      border: 1px solid rgba(148,163,184,0.6);
      padding: 6px 8px;
    }

    .summary-label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.09em;
      color: #cbd5f5;
      margin-bottom: 4px;
    }

    .summary-value {
      font-size: 0.98rem;
      font-weight: 600;
    }

    .summary-hint {
      font-size: 0.72rem;
      color: var(--muted);
    }

    /* Filters */
    .filters {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }

    .filter {
      display: flex;
      flex-direction: column;
      gap: 3px;
      min-width: 150px;
      flex: 1 1 150px;
    }

    .filter label {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .filter select,
    .filter input[type="number"],
    .filter input[type="text"] {
      background: rgba(15,23,42,0.9);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 0.78rem;
    }

    /* Table */
    .table-wrapper {
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      overflow-y: auto;
      overflow-x: auto;
      max-height: 600px;
      max-width: 100%;
    }

    table {
      width: 100%;
      min-width: 900px;
      border-collapse: collapse;
      font-size: 0.8rem;
    }

    thead {
      background: linear-gradient(to right, rgba(15,23,42,0.95), rgba(30,64,175,0.7));
      position: sticky;
      top: 0;
      z-index: 1;
    }

    th, td {
      padding: 8px 10px;
      text-align: left;
      border-bottom: 1px solid rgba(31,41,55,0.9);
      white-space: nowrap;
    }

    th {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #cbd5f5;
      cursor: pointer;
      user-select: none;
    }

    th:hover {
      background: rgba(30,64,175,0.4);
    }

    th .sort-indicator {
      font-size: 0.7rem;
      margin-left: 4px;
      opacity: 0.8;
    }

    tbody tr:nth-child(even) {
      background: rgba(15,23,42,0.75);
    }

    tbody tr:hover {
      background: rgba(30,64,175,0.55);
    }

    .symbol-link {
      color: #e5e7eb;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.9rem;
    }

    .symbol-link:hover {
      color: var(--accent);
      text-decoration: underline;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 0.7rem;
      font-weight: 600;
    }

    .pill-green {
      background: rgba(16,185,129,0.16);
      color: #6ee7b7;
      border: 1px solid rgba(16,185,129,0.6);
    }
    .pill-yellow {
      background: rgba(234,179,8,0.18);
      color: #facc15;
      border: 1px solid rgba(234,179,8,0.6);
    }
    .pill-blue {
      background: rgba(59,130,246,0.2);
      color: #bfdbfe;
      border: 1px solid rgba(59,130,246,0.7);
    }
    .pill-red {
      background: rgba(248,113,113,0.18);
      color: #fecaca;
      border: 1px solid rgba(248,113,113,0.65);
    }

    /* Trading Levels Styling */
    .price-cell {
      font-weight: 700;
      color: var(--accent);
      font-size: 0.95rem;
    }

    .sl-cell {
      color: var(--danger);
      font-weight: 600;
    }

    .target-cell {
      color: var(--success);
      font-weight: 600;
    }

    .rr-cell {
      font-weight: 600;
    }

    .rr-good {
      color: var(--success);
    }

    .rr-medium {
      color: var(--warning);
    }

    .rr-poor {
      color: var(--danger);
    }

    /* Show All Button */
    .show-all-btn {
      margin: 10px 0;
      padding: 10px 20px;
      background: linear-gradient(135deg, var(--accent), #6366f1);
      color: white;
      border: none;
      border-radius: 25px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s;
    }

    .show-all-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 20px rgba(56,189,248,0.4);
    }

    .status-banner {
      margin-top: 10px;
      font-size: 0.8rem;
      color: var(--muted);
      padding: 10px;
      background: rgba(15,23,42,0.6);
      border-radius: 8px;
      border-left: 3px solid var(--accent);
    }

    .status-banner span {
      color: var(--accent);
      font-weight: 500;
    }

    .side-card {
      margin-bottom: 10px;
    }

    .chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 6px;
    }

    .chip {
      border-radius: 999px;
      border: 1px solid rgba(148,163,184,0.7);
      padding: 4px 11px;
      font-size: 0.74rem;
      cursor: pointer;
      background: radial-gradient(circle at top left, rgba(59,130,246,0.25), rgba(15,23,42,0.95));
      color: #e0f2fe;
      box-shadow: 0 8px 18px rgba(15,23,42,0.7);
      transition: transform 0.12s ease, box-shadow 0.12s ease;
    }

    .chip:hover {
      transform: translateY(-1px);
      box-shadow: 0 10px 22px rgba(15,23,42,0.9);
    }

    .chip strong {
      color: #f9fafb;
      font-weight: 600;
    }

    .help-box {
      font-size: 0.77rem;
      color: var(--muted);
      border-radius: var(--radius-sm);
      border: 1px dashed rgba(148,163,184,0.7);
      padding: 8px 10px;
      background: rgba(15,23,42,0.9);
    }

    .help-box ul {
      padding-left: 18px;
      margin: 6px 0 0;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      margin-top: 15px;
      padding: 10px;
    }

    .pagination button {
      padding: 8px 16px;
      background: rgba(15,23,42,0.9);
      border: 1px solid var(--border);
      color: var(--text);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
    }

    .pagination button:hover:not(:disabled) {
      background: var(--accent);
      border-color: var(--accent);
    }

    .pagination button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .pagination span {
      color: var(--muted);
      font-size: 0.85rem;
    }
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="title-block">
        <h1>
          ⚡ Momentum Dashboard Pro
          <span class="tag-pill">Enhanced Trading Signals</span>
        </h1>
        <p class="subtitle">
          Cloud-hosted with auto-updates, trading levels (Entry/SL/Target), and complete signal analysis
        </p>
        
        <!-- Market Cap Quick Filters -->
        <div class="mcap-filters">
          <button class="mcap-btn active" data-mcap="all">🌟 All Caps</button>
          <button class="mcap-btn" data-mcap="Large Cap">🏢 Large Cap</button>
          <button class="mcap-btn" data-mcap="Mid Cap">🏭 Mid Cap</button>
          <button class="mcap-btn" data-mcap="Small Cap">🚀 Small Cap</button>
        </div>
        
        <div class="tabs" id="modeTabs">
          <button class="tab-btn active" data-mode="intraday">
            <span class="icon">⚡</span> Intraday (1h / 4h)
          </button>
          <button class="tab-btn" data-mode="swing">
            <span class="icon">📈</span> Swing (1–3 days)
          </button>
          <button class="tab-btn" data-mode="positional">
            <span class="icon">🧭</span> Positional (5–15 days)
          </button>
        </div>
      </div>
    </header>

    <div class="status-banner" id="statusBanner">
      <span>●</span> Loading data from cloud...
    </div>

    <div class="grid">
      <!-- Main area -->
      <div>
        <div class="card" id="mainCard">
          <div class="card-header">
            <div>
              <div class="card-title">
                <span class="dot"></span>
                <span id="mainCardTitle">Intraday Momentum Radar (1h / 4h)</span>
              </div>
              <div class="card-subtitle" id="mainCardSubtitle">
                Complete trading signals with entry, stop loss, and target levels calculated automatically
              </div>
            </div>
          </div>

          <div class="summary-row" id="summaryRow">
            <!-- Summary cards injected by JS -->
          </div>

          <div class="filters" id="filtersRow">
            <!-- Filters injected by JS -->
          </div>

          <div class="table-wrapper">
            <table>
              <thead id="tableHead">
                <!-- Head injected by JS -->
              </thead>
              <tbody id="tableBody">
                <tr><td colspan="12" style="text-align: center; padding: 40px;">Loading signals...</td></tr>
              </tbody>
            </table>
          </div>

          <div class="pagination" id="pagination">
            <button id="prevBtn">← Previous</button>
            <span id="pageInfo">Page 1 of 1</span>
            <button id="nextBtn">Next →</button>
            <button id="showAllBtn" class="show-all-btn">Show All Signals</button>
          </div>
        </div>
      </div>

      <!-- Side area -->
      <div>
        <div class="card side-card">
          <div class="card-header">
            <div class="card-title">
              <span class="dot"></span>
              <span id="sideTitle">Quick Stats</span>
            </div>
          </div>
          <div id="sideContent">
            <div class="chip-row" id="chipRow">
              <!-- Stats injected -->
            </div>
          </div>
        </div>

        <div class="help-box" id="helpBox">
          <strong>📊 Trading Levels Explained</strong>
          <ul>
            <li><strong style="color: var(--accent)">Entry:</strong> Current market price</li>
            <li><strong style="color: var(--danger)">Stop Loss:</strong> Risk management level (2-5% below entry)</li>
            <li><strong style="color: var(--success)">Target:</strong> Profit booking level (based on R:R ratio)</li>
            <li><strong>R:R Ratio:</strong> Risk-Reward ratio (Good: 2+, Medium: 1.5-2, Poor: <1.5)</li>
          </ul>
          <br>
          <strong>🎯 How to Use</strong>
          <ul>
            <li>Filter by market cap using buttons at top</li>
            <li>Choose your trading timeframe (Intraday/Swing/Positional)</li>
            <li>Sort columns by clicking headers</li>
            <li>Click symbol to open TradingView chart</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <script>
    // ======== Utility functions ========
    function parseCustomDate(str) {
      if (!str) return null;
      const parts = str.split(" ");
      if (parts.length < 3) return null;
      const [datePart, timePart, ampmRaw] = parts;
      const [d, m, y] = datePart.split("-").map(Number);
      let [h, min] = timePart.split(":").map(Number);
      const ampm = (ampmRaw || '').toLowerCase();
      if (ampm === "pm" && h !== 12) h += 12;
      if (ampm === "am" && h === 12) h = 0;
      return new Date(y, m - 1, d, h, min);
    }

    function formatDateOnly(date) {
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, "0");
      const d = String(date.getDate()).padStart(2, "0");
      return `${y}-${m}-${d}`;
    }

    function getUnique(arr) {
      return Array.from(new Set(arr));
    }

    function groupBy(arr, keyFn) {
      const map = new Map();
      for (const item of arr) {
        const key = keyFn(item);
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(item);
      }
      return map;
    }

    // Calculate trading levels
    function calculateTradingLevels(price, mode) {
      const p = parseFloat(price);
      let slPercent, targetMultiplier;
      
      if (mode === 'intraday') {
        slPercent = 0.02; // 2% SL for intraday
        targetMultiplier = 2; // 1:2 R:R
      } else if (mode === 'swing') {
        slPercent = 0.03; // 3% SL for swing
        targetMultiplier = 2.5; // 1:2.5 R:R
      } else {
        slPercent = 0.05; // 5% SL for positional
        targetMultiplier = 3; // 1:3 R:R
      }
      
      const sl = p * (1 - slPercent);
      const risk = p - sl;
      const target = p + (risk * targetMultiplier);
      const rr = (target - p) / (p - sl);
      
      return {
        entry: p.toFixed(2),
        sl: sl.toFixed(2),
        target: target.toFixed(2),
        rr: rr.toFixed(2)
      };
    }

    // ======== Global state ========
    const state = {
      raw: [],
      dates: [],
      mode: "intraday",
      selectedMcap: "all",
      currentPage: 1,
      itemsPerPage: 50,
      showAll: false,
      aggregates: {
        intraday: [],
        swing: [],
        positional: []
      },
      filters: {
        sector: "all",
        marketcap: "all",
        min_hits: 0,
        min_swing_days: 0,
        min_days_in_trend: 0
      },
      sort: {
        field: null,
        direction: "desc"
      }
    };

    // ======== Aggregation logic ========
    function preprocessRaw(json) {
      const rows = [];
      for (const r of json) {
        const dt = parseCustomDate(r.date);
        if (!dt) continue;
        const date_only = formatDateOnly(dt);
        const hour = dt.getHours();
        
        // Extract price from various possible fields
        let price = r.close || r.Close || r.ltp || r.LTP || r.price || r.Price || r['last price'] || r['Last Price'] || '0';
        if (typeof price === 'string') {
          price = price.replace(/[₹,\s]/g, '').trim();
        }
        
        rows.push({
          ...r,
          _dt: dt,
          _dateOnly: date_only,
          _hour: hour,
          symbol: r.symbol || r.Symbol || 'N/A',
          sector: r.sector || r.Sector || 'Other',
          marketcapname: r.marketcapname || r.marketCapName || r['Market Cap'] || 'Unknown',
          price: price
        });
      }
      rows.sort((a, b) => a._dt - b._dt);
      state.raw = rows;
      state.dates = getUnique(rows.map(r => r._dateOnly));
    }

    function aggregateIntraday() {
      const rows = state.raw;
      if (!rows.length) return [];
      const lastDate = state.dates[state.dates.length - 1];
      const subset = rows.filter(r => r._dateOnly === lastDate);
      const bySymbol = groupBy(subset, r => r.symbol);

      const result = [];
      for (const [symbol, list] of bySymbol.entries()) {
        const hours = getUnique(list.map(r => r._hour));
        const hits_1h = hours.length;
        const buckets = new Set();
        for (const h of hours) {
          const bucket = Math.floor((h - 9) / 4);
          buckets.add(bucket);
        }
        const hits_4h = buckets.size;
        const sample = list[list.length - 1]; // Get latest
        result.push({
          symbol,
          sector: sample.sector,
          marketcapname: sample.marketcapname,
          price: sample.price,
          hits_1h,
          hits_4h,
          total_hits: hits_1h + hits_4h
        });
      }
      return result.sort((a, b) => b.total_hits - a.total_hits);
    }

    function aggregateSwing(daysBack = 3) {
      const rows = state.raw;
      if (!rows.length) return [];
      const uniqueDates = state.dates;
      const lastDates = uniqueDates.slice(-daysBack);
      if (!lastDates.length) return [];

      const bySymbol = groupBy(
        rows.filter(r => lastDates.includes(r._dateOnly)),
        r => r.symbol
      );

      const last = lastDates[lastDates.length - 1];
      const result = [];

      for (const [symbol, list] of bySymbol.entries()) {
        const sample = list[list.length - 1];
        const byDate = groupBy(list, r => r._dateOnly);
        const hits_1d = (byDate.get(last) || []).length;
        const lastTwo = lastDates.slice(-2);
        const hits_2d = lastTwo.reduce((acc, d) => acc + ((byDate.get(d) || []).length), 0);
        const hits_3d = lastDates.reduce((acc, d) => acc + ((byDate.get(d) || []).length), 0);

        let consec = 0;
        for (let i = lastDates.length - 1; i >= 0; i--) {
          const d = lastDates[i];
          const count = (byDate.get(d) || []).length;
          if (count > 0) consec += 1;
          else break;
        }

        result.push({
          symbol,
          sector: sample.sector,
          marketcapname: sample.marketcapname,
          price: sample.price,
          hits_1d,
          hits_2d,
          hits_3d,
          consec_days: consec
        });
      }

      return result.sort((a, b) => b.hits_3d - a.hits_3d);
    }

    function aggregatePositional() {
      const rows = state.raw;
      if (!rows.length) return [];
      const uniqueDates = state.dates;
      if (!uniqueDates.length) return [];

      const last15 = uniqueDates.slice(-15);
      const bySymbol = groupBy(
        rows.filter(r => last15.includes(r._dateOnly)),
        r => r.symbol
      );

      const result = [];
      for (const [symbol, list] of bySymbol.entries()) {
        const sample = list[list.length - 1];
        const byDate = groupBy(list, r => r._dateOnly);
        const hits_5dDates = last15.slice(-5);
        const hits_7dDates = last15.slice(-7);
        const hits_5d = hits_5dDates.reduce((acc, d) => acc + ((byDate.get(d) || []).length), 0);
        const hits_7d = hits_7dDates.reduce((acc, d) => acc + ((byDate.get(d) || []).length), 0);
        const hits_15d = last15.reduce((acc, d) => acc + ((byDate.get(d) || []).length), 0);

        const lastForTrend = last15.slice(-10);
        let daysInTrend = 0;
        for (const d of lastForTrend) {
          if ((byDate.get(d) || []).length > 0) daysInTrend++;
        }

        result.push({
          symbol,
          sector: sample.sector,
          marketcapname: sample.marketcapname,
          price: sample.price,
          hits_5d,
          hits_7d,
          hits_15d,
          days_in_trend: daysInTrend
        });
      }

      return result.sort((a, b) => b.hits_15d - a.hits_15d);
    }

    function recomputeAggregates() {
      state.aggregates.intraday = aggregateIntraday();
      state.aggregates.swing = aggregateSwing(3);
      state.aggregates.positional = aggregatePositional();
    }

    // ======== Filtering ========
    function filteredAggregates(mode) {
      let agg = state.aggregates[mode] || [];
      const { sector, marketcap, min_hits, min_swing_days, min_days_in_
