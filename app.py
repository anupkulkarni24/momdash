"""
ENHANCED app.py for Render Deployment
Complete dashboard with Intraday/Swing/Positional + Portfolio Tracking

Save this as app.py and deploy to Render
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Global data storage
cached_data = []
portfolio_data = []
last_update = None
data_source = "Demo"
scraping_status = "Ready"

def categorize_strategy(row):
    """Categorize stock into Intraday/Swing/Positional based on price action"""
    try:
        price = float(str(row.get('price', 0)).replace(',', '').replace('₹', ''))
        
        # Simple strategy logic (customize as needed)
        volatility = random.random()  # In real case, calculate from historical data
        
        if volatility > 0.7:
            return "Intraday"
        elif volatility > 0.4:
            return "Swing"
        else:
            return "Positional"
    except:
        return "Swing"  # Default

def generate_demo_data():
    """Generate realistic demo data with strategies"""
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 
               'ITC', 'KOTAKBANK', 'LT', 'AXISBANK', 'TATAMOTORS', 'WIPRO', 'MARUTI', 
               'BAJFINANCE', 'TATASTEEL', 'ASIANPAINT', 'TITAN', 'NESTLEIND', 'ULTRACEMCO']
    sectors = ['Banking', 'IT', 'Auto', 'Pharma', 'FMCG', 'Metals', 'Energy']
    mcaps = ['Large Cap', 'Mid Cap', 'Small Cap']
    strategies = ['Intraday', 'Swing', 'Positional']
    
    data = []
    today = datetime.now()
    
    for day in range(10):
        date_obj = today - timedelta(days=day)
        for hour in range(9, 16):
            num_symbols = random.randint(5, 10)
            selected_symbols = random.sample(symbols, num_symbols)
            for symbol in selected_symbols:
                price = random.uniform(100, 3000)
                data.append({
                    "date": f"{date_obj.day:02d}-{date_obj.month:02d}-{date_obj.year} {hour:02d}:{random.randint(0, 59):02d}",
                    "symbol": symbol,
                    "sector": random.choice(sectors),
                    "marketcapname": random.choice(mcaps),
                    "close": f"{price:.2f}",
                    "price": f"{price:.2f}",
                    "strategy": random.choice(strategies),
                    "volume": random.randint(100000, 10000000),
                    "change_pct": round(random.uniform(-5, 5), 2)
                })
    return data

# Initialize with demo data
cached_data = generate_demo_data()
last_update = datetime.now()

# API ENDPOINTS
@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/data')
def get_data():
    # Add strategy categorization to data
    enriched_data = []
    for row in cached_data:
        if 'strategy' not in row:
            row['strategy'] = categorize_strategy(row)
        enriched_data.append(row)
    
    return jsonify({
        "data": enriched_data,
        "portfolio": portfolio_data,
        "last_update": last_update.isoformat() if last_update else None,
        "status": scraping_status,
        "count": len(enriched_data),
        "data_source": data_source
    })

@app.route('/api/portfolio', methods=['GET', 'POST', 'DELETE'])
def manage_portfolio():
    global portfolio_data
    
    if request.method == 'GET':
        return jsonify({"portfolio": portfolio_data})
    
    elif request.method == 'POST':
        trade = request.get_json()
        trade['id'] = len(portfolio_data) + 1
        trade['timestamp'] = datetime.now().isoformat()
        portfolio_data.append(trade)
        return jsonify({"status": "success", "trade": trade})
    
    elif request.method == 'DELETE':
        trade_id = request.args.get('id', type=int)
        portfolio_data = [t for t in portfolio_data if t.get('id') != trade_id]
        return jsonify({"status": "success"})

@app.route('/api/refresh-demo', methods=['POST'])
def refresh_demo():
    global cached_data, last_update, data_source, scraping_status
    cached_data = generate_demo_data()
    last_update = datetime.now()
    data_source = "Demo"
    scraping_status = "Demo data refreshed"
    return jsonify({
        "status": "success",
        "message": "Demo data refreshed",
        "count": len(cached_data)
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    global cached_data, last_update, data_source, scraping_status
    try:
        data = request.get_json()
        if data and isinstance(data, list) and len(data) > 0:
            # Add strategy categorization during upload
            for row in data:
                if 'strategy' not in row:
                    row['strategy'] = categorize_strategy(row)
            
            cached_data = data
            last_update = datetime.now()
            data_source = "Uploaded (Real Data)"
            scraping_status = f"Uploaded {len(data)} records successfully"
            return jsonify({
                "status": "success",
                "message": f"Uploaded {len(data)} records",
                "count": len(cached_data)
            })
        return jsonify({
            "status": "error", 
            "message": "Invalid data format"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "records": len(cached_data),
        "portfolio_trades": len(portfolio_data),
        "last_update": last_update.isoformat() if last_update else None,
        "data_source": data_source
    })

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Momentum Dashboard Pro - Portfolio Edition</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0a0e27; --card: #1a1f3a; --accent: #00d4ff; --success: #00ff88;
            --warning: #ffa500; --danger: #ff4466; --text: #e4e9f7; --muted: #8b92b0; --border: #2a2f4a;
        }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, var(--bg) 0%, #050814 100%); 
            color: var(--text); min-height: 100vh; padding: 20px; 
        }
        .container { max-width: 1600px; margin: 0 auto; }
        h1 { 
            text-align: center; font-size: 2.5rem; margin-bottom: 10px; 
            background: linear-gradient(135deg, var(--accent), var(--success)); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        }
        .subtitle { text-align: center; color: var(--muted); margin-bottom: 30px; }
        .card { 
            background: var(--card); border-radius: 12px; padding: 25px; 
            margin-bottom: 20px; border: 1px solid var(--border); 
        }
        .btn { 
            background: linear-gradient(135deg, var(--accent), #0099cc); 
            color: white; padding: 12px 24px; border: none; border-radius: 25px; 
            cursor: pointer; font-weight: 600; margin: 5px; transition: all 0.3s; 
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3); }
        .btn-upload { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
        .btn-success { background: linear-gradient(135deg, #00ff88, #00cc70); }
        .btn-danger { background: linear-gradient(135deg, #ff4466, #cc3355); }
        .info-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 15px; margin-top: 20px; 
        }
        .info-box { 
            background: #12172e; padding: 15px; border-radius: 8px; 
            border: 1px solid var(--border); text-align: center;
        }
        .info-label { 
            font-size: 0.75rem; color: var(--muted); 
            text-transform: uppercase; margin-bottom: 5px; 
        }
        .info-value { font-size: 1.8rem; color: var(--accent); font-weight: 700; }
        .tabs { 
            display: flex; gap: 10px; margin-bottom: 20px; 
            border-bottom: 2px solid var(--border); padding-bottom: 10px;
        }
        .tab { 
            padding: 10px 20px; border-radius: 8px 8px 0 0; 
            cursor: pointer; transition: all 0.3s; background: #12172e;
        }
        .tab.active { 
            background: linear-gradient(135deg, var(--accent), #0099cc); 
            color: white; font-weight: 600;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }
        th { 
            background: #12172e; color: var(--accent); 
            font-size: 0.85rem; text-transform: uppercase; 
        }
        tr:hover { background: #12172e; }
        .badge { 
            padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; 
            font-weight: 600; display: inline-block;
        }
        .badge-intraday { background: #ff4466; color: white; }
        .badge-swing { background: #ffa500; color: white; }
        .badge-positional { background: #00ff88; color: #0a0e27; }
        .modal { 
            display: none; position: fixed; top: 0; left: 0; 
            width: 100%; height: 100%; background: rgba(0,0,0,0.8); 
            z-index: 1000; align-items: center; justify-content: center;
        }
        .modal.active { display: flex; }
        .modal-content { 
            background: var(--card); padding: 30px; border-radius: 15px; 
            max-width: 500px; width: 90%; border: 2px solid var(--accent);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; margin-bottom: 8px; 
            color: var(--muted); font-weight: 600; 
        }
        .form-group input, .form-group select { 
            width: 100%; padding: 12px; border-radius: 8px; 
            border: 1px solid var(--border); background: #12172e; 
            color: var(--text); font-size: 1rem;
        }
        .notification { 
            position: fixed; top: 20px; right: 20px; 
            background: var(--card); padding: 15px 20px; border-radius: 10px; 
            border: 2px solid var(--success); box-shadow: 0 4px 20px rgba(0,0,0,0.5); 
            z-index: 1000; animation: slideIn 0.3s; 
        }
        @keyframes slideIn { from { transform: translateX(400px); } to { transform: translateX(0); } }
        #fileInput { display: none; }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .info-grid { grid-template-columns: 1fr 1fr; }
            .tabs { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Momentum Dashboard Pro</h1>
        <p class="subtitle">Strategy-Based Trading | Portfolio Tracking</p>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: var(--accent);">📊 Data Control Panel</h2>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn btn-upload" onclick="document.getElementById('fileInput').click()">📤 Upload JSON</button>
                <button class="btn" onclick="refreshDemo()">🔄 Refresh Demo</button>
                <button class="btn btn-success" onclick="openAddTradeModal()">➕ Add Trade</button>
            </div>
            <input type="file" id="fileInput" accept=".json" onchange="uploadFile(event)">
            
            <div class="info-grid">
                <div class="info-box">
                    <div class="info-label">Last Updated</div>
                    <div class="info-value" id="lastUpdate" style="font-size: 1.2rem;">--:--</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Total Signals</div>
                    <div class="info-value" id="recordCount">0</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Portfolio Trades</div>
                    <div class="info-value" id="portfolioCount">0</div>
                </div>
                <div class="info-box">
                    <div class="info-label">P&L</div>
                    <div class="info-value" id="totalPnL" style="font-size: 1.3rem;">₹0</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Data Source</div>
                    <div class="info-value" id="dataSource" style="font-size: 0.9rem;">Demo</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('all')">All Signals</div>
                <div class="tab" onclick="switchTab('intraday')">🔴 Intraday</div>
                <div class="tab" onclick="switchTab('swing')">🟠 Swing</div>
                <div class="tab" onclick="switchTab('positional')">🟢 Positional</div>
                <div class="tab" onclick="switchTab('portfolio')">💼 Portfolio</div>
            </div>
            
            <div id="tab-all" class="tab-content active">
                <h3 style="color: var(--accent); margin-bottom: 15px;">All Trading Signals</h3>
                <div style="overflow-x: auto;">
                    <table id="allTable">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Strategy</th>
                                <th>Sector</th>
                                <th>Market Cap</th>
                                <th>Price</th>
                                <th>Change %</th>
                                <th>Date</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="allTableBody">
                            <tr><td colspan="8" style="text-align: center; padding: 40px;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="tab-intraday" class="tab-content">
                <h3 style="color: #ff4466; margin-bottom: 15px;">🔴 Intraday Signals</h3>
                <div style="overflow-x: auto;">
                    <table><thead><tr><th>Symbol</th><th>Price</th><th>Change %</th><th>Date</th><th>Action</th></tr></thead>
                    <tbody id="intradayTableBody"></tbody></table>
                </div>
            </div>
            
            <div id="tab-swing" class="tab-content">
                <h3 style="color: #ffa500; margin-bottom: 15px;">🟠 Swing Signals</h3>
                <div style="overflow-x: auto;">
                    <table><thead><tr><th>Symbol</th><th>Price</th><th>Change %</th><th>Date</th><th>Action</th></tr></thead>
                    <tbody id="swingTableBody"></tbody></table>
                </div>
            </div>
            
            <div id="tab-positional" class="tab-content">
                <h3 style="color: #00ff88; margin-bottom: 15px;">🟢 Positional Signals</h3>
                <div style="overflow-x: auto;">
                    <table><thead><tr><th>Symbol</th><th>Price</th><th>Change %</th><th>Date</th><th>Action</th></tr></thead>
                    <tbody id="positionalTableBody"></tbody></table>
                </div>
            </div>
            
            <div id="tab-portfolio" class="tab-content">
                <h3 style="color: var(--accent); margin-bottom: 15px;">💼 My Portfolio</h3>
                <div style="overflow-x: auto;">
                    <table><thead><tr><th>Symbol</th><th>Type</th><th>Buy Price</th><th>Qty</th><th>Current Price</th><th>P&L</th><th>Date</th><th>Action</th></tr></thead>
                    <tbody id="portfolioTableBody"></tbody></table>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Add Trade Modal -->
    <div id="addTradeModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px; color: var(--accent);">➕ Add Trade</h2>
            <form onsubmit="addTrade(event)">
                <div class="form-group">
                    <label>Symbol</label>
                    <input type="text" id="tradeSymbol" required>
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <select id="tradeType" required>
                        <option value="buy">Buy</option>
                        <option value="sell">Sell</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Price</label>
                    <input type="number" step="0.01" id="tradePrice" required>
                </div>
                <div class="form-group">
                    <label>Quantity</label>
                    <input type="number" id="tradeQty" required>
                </div>
                <div class="form-group">
                    <label>Strategy</label>
                    <select id="tradeStrategy">
                        <option value="Intraday">Intraday</option>
                        <option value="Swing">Swing</option>
                        <option value="Positional">Positional</option>
                    </select>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 30px;">
                    <button type="submit" class="btn btn-success" style="flex: 1;">Add Trade</button>
                    <button type="button" class="btn btn-danger" onclick="closeAddTradeModal()" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        let allData = [];
        let portfolioData = [];
        
        function showNotification(message, isError = false) {
            const notif = document.createElement('div');
            notif.className = 'notification';
            notif.style.borderColor = isError ? '#ff4466' : '#00ff88';
            notif.textContent = message;
            document.body.appendChild(notif);
            setTimeout(() => notif.remove(), 4000);
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }
        
        function openAddTradeModal() {
            document.getElementById('addTradeModal').classList.add('active');
        }
        
        function closeAddTradeModal() {
            document.getElementById('addTradeModal').classList.remove('active');
        }
        
        async function addTrade(event) {
            event.preventDefault();
            const trade = {
                symbol: document.getElementById('tradeSymbol').value,
                type: document.getElementById('tradeType').value,
                price: parseFloat(document.getElementById('tradePrice').value),
                qty: parseInt(document.getElementById('tradeQty').value),
                strategy: document.getElementById('tradeStrategy').value
            };
            
            try {
                const res = await fetch('/api/portfolio', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(trade)
                });
                const result = await res.json();
                showNotification('✅ Trade added successfully!');
                closeAddTradeModal();
                loadData();
            } catch (err) {
                showNotification('❌ Error adding trade', true);
            }
        }
        
        async function deleteTrade(id) {
            if (!confirm('Delete this trade?')) return;
            try {
                await fetch(`/api/portfolio?id=${id}`, {method: 'DELETE'});
                showNotification('✅ Trade deleted');
                loadData();
            } catch (err) {
                showNotification('❌ Error deleting trade', true);
            }
        }
        
        function addToPortfolio(symbol, price, strategy) {
            document.getElementById('tradeSymbol').value = symbol;
            document.getElementById('tradePrice').value = price;
            document.getElementById('tradeStrategy').value = strategy;
            openAddTradeModal();
        }
        
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const json = await res.json();
                
                allData = json.data || [];
                portfolioData = json.portfolio || [];
                
                // Update stats
                const lastUpdateDate = new Date(json.last_update);
                document.getElementById('lastUpdate').textContent = lastUpdateDate.toLocaleTimeString();
                document.getElementById('recordCount').textContent = json.count;
                document.getElementById('portfolioCount').textContent = portfolioData.length;
                document.getElementById('dataSource').textContent = json.data_source || 'Demo';
                
                // Calculate P&L
                let totalPnL = 0;
                portfolioData.forEach(trade => {
                    if (trade.type === 'buy') {
                        const currentPrice = parseFloat(trade.price) * 1.02; // Mock 2% gain
                        totalPnL += (currentPrice - trade.price) * trade.qty;
                    }
                });
                const pnlEl = document.getElementById('totalPnL');
                pnlEl.textContent = `₹${totalPnL.toFixed(0)}`;
                pnlEl.style.color = totalPnL >= 0 ? '#00ff88' : '#ff4466';
                
                // Render tables
                renderAllTable();
                renderStrategyTable('intraday', 'Intraday');
                renderStrategyTable('swing', 'Swing');
                renderStrategyTable('positional', 'Positional');
                renderPortfolioTable();
                
            } catch (err) {
                console.error('Load error:', err);
            }
        }
        
        function renderAllTable() {
            const tbody = document.getElementById('allTableBody');
            if (!allData || allData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No data</td></tr>';
                return;
            }
            
            const uniqueSymbols = new Map();
            allData.forEach(row => {
                if (!uniqueSymbols.has(row.symbol)) uniqueSymbols.set(row.symbol, row);
            });
            
            const rows = Array.from(uniqueSymbols.values()).slice(0, 20).map(row => {
                const price = parseFloat(row.price || 0);
                const change = row.change_pct || 0;
                const strategyBadge = `<span class="badge badge-${row.strategy?.toLowerCase() || 'swing'}">${row.strategy || 'Swing'}</span>`;
                
                return `<tr>
                    <td><strong>${row.symbol}</strong></td>
                    <td>${strategyBadge}</td>
                    <td>${row.sector || 'N/A'}</td>
                    <td>${row.marketcapname || 'N/A'}</td>
                    <td><strong style="color: var(--accent);">₹${price.toFixed(2)}</strong></td>
                    <td style="color: ${change >= 0 ? '#00ff88' : '#ff4466'}">${change >= 0 ? '+' : ''}${change}%</td>
                    <td style="font-size: 0.85rem;">${row.date || 'N/A'}</td>
                    <td><button class="btn" style="padding: 6px 12px; font-size: 0.8rem;" onclick="addToPortfolio('${row.symbol}', ${price}, '${row.strategy}')">Add</button></td>
                </tr>`;
            }).join('');
            
            tbody.innerHTML = rows;
        }
        
        function renderStrategyTable(strategy, strategyName) {
            const tbody = document.getElementById(strategy + 'TableBody');
            const filtered = allData.filter(r => r.strategy === strategyName);
            
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No signals</td></tr>';
                return;
            }
            
            const uniqueSymbols = new Map();
            filtered.forEach(row => {
                if (!uniqueSymbols.has(row.symbol)) uniqueSymbols.set(row.symbol, row);
            });
            
            const rows = Array.from(uniqueSymbols.values()).slice(0, 15).map(row => {
                const price = parseFloat(row.price || 0);
                const change = row.change_pct || 0;
                
                return `<tr>
                    <td><strong>${row.symbol}</strong></td>
                    <td><strong style="color: var(--accent);">₹${price.toFixed(2)}</strong></td>
                    <td style="color: ${change >= 0 ? '#00ff88' : '#ff4466'}">${change >= 0 ? '+' : ''}${change}%</td>
                    <td style="font-size: 0.85rem;">${row.date || 'N/A'}</td>
                    <td><button class="btn" style="padding: 6px 12px; font-size: 0.8rem;" onclick="addToPortfolio('${row.symbol}', ${price}, '${strategyName}')">Add</button></td>
                </tr>`;
            }).join('');
            
            tbody.innerHTML = rows;
        }
        
        function renderPortfolioTable() {
            const tbody = document.getElementById('portfolioTableBody');
            
            if (portfolioData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No trades yet</td></tr>';
                return;
            }
            
            const rows = portfolioData.map(trade => {
                const currentPrice = trade.price * 1.02; // Mock current price
                const pnl = (currentPrice - trade.price) * trade.qty;
                const pnlColor = pnl >= 0 ? '#00ff88' : '#ff4466';
                
                return `<tr>
                    <td><strong>${trade.symbol}</strong></td>
                    <td><span class="badge badge-${trade.type === 'buy' ? 'positional' : 'intraday'}">${trade.type.toUpperCase()}</span></td>
                    <td>₹${trade.price.toFixed(2)}</td>
                    <td>${trade.qty}</td>
                    <td>₹${currentPrice.toFixed(2)}</td>
                    <td style="color: ${pnlColor}; font-weight: 700;">${pnl >= 0 ? '+' : ''}₹${pnl.toFixed(2)}</td>
                    <td style="font-size: 0.85rem;">${new Date(trade.timestamp).toLocaleDateString()}</td>
                    <td><button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8rem;" onclick="deleteTrade(${trade.id})">×</button></td>
                </tr>`;
            }).join('');
            
            tbody.innerHTML = rows;
        }
        
        async function uploadFile(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            showNotification('Uploading file...');
            
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    const res = await fetch('/api/upload', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await res.json();
                    
                    if (result.status === 'success') {
                        showNotification('✅ Upload successful! ' + result.count + ' records');
                        setTimeout(() => loadData(), 500);
                    } else {
                        showNotification('❌ ' + result.message, true);
                    }
                } catch (err) {
                    showNotification('❌ Error: ' + err.message, true);
                }
            };
            reader.readAsText(file);
            event.target.value = '';
        }
        
        async function refreshDemo() {
            try {
                const res = await fetch('/api/refresh-demo', { method: 'POST' });
                const json = await res.json();
                showNotification(json.message);
                setTimeout(() => loadData(), 500);
            } catch (err) {
                showNotification('Error refreshing demo', true);
            }
        }
        
        // Auto-refresh every 30 seconds
        window.addEventListener('DOMContentLoaded', () => {
            loadData();
            setInterval(loadData, 30000);
        });
        
        // Close modal on outside click
        document.getElementById('addTradeModal').addEventListener('click', (e) => {
            if (e.target.id === 'addTradeModal') closeAddTradeModal();
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
