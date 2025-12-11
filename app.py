"""
COMPLETE app.py for Render Deployment
This is the FULL version with the complete dashboard UI

Save this as app.py and deploy to Render
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import random
import threading

app = Flask(__name__)
CORS(app)

# Global data storage
cached_data = []
last_update = None
data_source = "Demo"
scraping_status = "Ready"
scraping_in_progress = False

def generate_demo_data():
    """Generate realistic demo data"""
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 
               'ITC', 'KOTAKBANK', 'LT', 'AXISBANK', 'TATAMOTORS', 'WIPRO', 'MARUTI', 
               'BAJFINANCE', 'TATASTEEL', 'ASIANPAINT', 'TITAN', 'NESTLEIND', 'ULTRACEMCO',
               'HINDUNILVR', 'ADANIENT', 'BAJAJFINSV', 'SUNPHARMA', 'ONGC', 'NTPC', 
               'POWERGRID', 'M&M', 'TECHM', 'HINDALCO', 'HCLTECH', 'DRREDDY', 'CIPLA',
               'HEROMOTOCO', 'EICHERMOT', 'GRASIM', 'JSWSTEEL', 'INDUSINDBK', 'VEDL']
    sectors = ['Banking', 'IT', 'Auto', 'Pharma', 'FMCG', 'Metals', 'Energy', 'Telecom', 'Infrastructure']
    mcaps = ['Large Cap', 'Mid Cap', 'Small Cap']
    
    data = []
    today = datetime.now()
    
    for day in range(15):
        date_obj = today - timedelta(days=day)
        for hour in range(9, 16):
            num_symbols = random.randint(8, 15)
            selected_symbols = random.sample(symbols, num_symbols)
            for symbol in selected_symbols:
                price = random.uniform(100, 3000)
                data.append({
                    "date": f"{date_obj.day:02d}-{date_obj.month:02d}-{date_obj.year} {hour:02d}:{random.randint(0, 59):02d} {'PM' if hour >= 12 else 'AM'}",
                    "symbol": symbol,
                    "sector": random.choice(sectors),
                    "marketcapname": random.choice(mcaps),
                    "close": f"{price:.2f}",
                    "price": f"{price:.2f}"
                })
    return data

# Initialize with demo data
cached_data = generate_demo_data()
last_update = datetime.now()

# API ENDPOINTS
@app.route('/')
def index():
    # Return full dashboard HTML (embedded in string)
    return render_template_string(FULL_DASHBOARD_HTML)

@app.route('/api/data')
def get_data():
    return jsonify({
        "data": cached_data,
        "last_update": last_update.isoformat() if last_update else None,
        "status": scraping_status,
        "count": len(cached_data),
        "data_source": data_source,
        "scraping_in_progress": scraping_in_progress
    })

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
            "message": "Invalid data format. Expected non-empty JSON array"
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
        "last_update": last_update.isoformat() if last_update else None,
        "data_source": data_source
    })

# Full Dashboard HTML (keeping it simple but functional)
FULL_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Momentum Dashboard Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0a0e27; --card: #1a1f3a; --accent: #00d4ff; --success: #00ff88;
            --text: #e4e9f7; --muted: #8b92b0; --border: #2a2f4a;
        }
        body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, var(--bg) 0%, #050814 100%); color: var(--text); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, var(--accent), var(--success)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { text-align: center; color: var(--muted); margin-bottom: 30px; }
        .card { background: var(--card); border-radius: 12px; padding: 25px; margin-bottom: 20px; border: 1px solid var(--border); }
        .btn { background: linear-gradient(135deg, var(--accent), #0099cc); color: white; padding: 12px 24px; border: none; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); }
        .btn-upload { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .info-box { background: #12172e; padding: 15px; border-radius: 8px; border: 1px solid var(--border); }
        .info-label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; margin-bottom: 5px; }
        .info-value { font-size: 1.5rem; color: var(--accent); font-weight: 700; }
        .success-msg { color: var(--success); padding: 15px; background: rgba(0, 255, 136, 0.1); border-radius: 8px; margin-top: 15px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }
        th { background: #12172e; color: var(--accent); font-size: 0.85rem; text-transform: uppercase; }
        tr:hover { background: #12172e; }
        #fileInput { display: none; }
        .notification { position: fixed; top: 20px; right: 20px; background: var(--card); padding: 15px 20px; border-radius: 10px; border: 2px solid var(--success); box-shadow: 0 4px 20px rgba(0,0,0,0.5); z-index: 1000; animation: slideIn 0.3s; }
        @keyframes slideIn { from { transform: translateX(400px); } to { transform: translateX(0); } }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .info-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Momentum Dashboard Pro</h1>
        <p class="subtitle">Cloud-Deployed | Real-Time Data Updates</p>
        
        <div class="card">
            <h2 style="margin-bottom: 20px; color: var(--accent);">📊 Data Control Panel</h2>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button class="btn btn-upload" onclick="document.getElementById('fileInput').click()">📤 Upload JSON</button>
                <button class="btn" onclick="refreshDemo()">🔄 Refresh Demo</button>
            </div>
            <input type="file" id="fileInput" accept=".json" onchange="uploadFile(event)">
            
            <div class="info-grid">
                <div class="info-box">
                    <div class="info-label">Last Updated</div>
                    <div class="info-value" id="lastUpdate">Loading...</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Total Records</div>
                    <div class="info-value" id="recordCount">0</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Data Source</div>
                    <div class="info-value" id="dataSource" style="font-size: 1.1rem;">Loading...</div>
                </div>
            </div>
            
            <div class="success-msg" id="successMsg" style="display: none;">
                ✅ <span id="successText"></span>
            </div>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 15px; color: var(--accent);">📋 Data Preview</h2>
            <div style="overflow-x: auto;">
                <table id="dataTable">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Sector</th>
                            <th>Market Cap</th>
                            <th>Price</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">Loading data...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        function showNotification(message, isError = false) {
            const notif = document.createElement('div');
            notif.className = 'notification';
            notif.style.borderColor = isError ? '#ff4466' : '#00ff88';
            notif.textContent = message;
            document.body.appendChild(notif);
            setTimeout(() => notif.remove(), 4000);
        }
        
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const json = await res.json();
                
                const lastUpdateDate = new Date(json.last_update);
                document.getElementById('lastUpdate').textContent = lastUpdateDate.toLocaleTimeString();
                document.getElementById('recordCount').textContent = json.count;
                document.getElementById('dataSource').textContent = json.data_source || 'Demo';
                
                // Display first 10 records in table
                const tbody = document.getElementById('tableBody');
                if (json.data && json.data.length > 0) {
                    const rows = json.data.slice(0, 10).map(row => `
                        <tr>
                            <td><strong>${row.symbol || 'N/A'}</strong></td>
                            <td>${row.sector || 'N/A'}</td>
                            <td>${row.marketcapname || 'N/A'}</td>
                            <td>₹${parseFloat(row.price || row.close || 0).toFixed(2)}</td>
                            <td>${row.date || 'N/A'}</td>
                        </tr>
                    `).join('');
                    tbody.innerHTML = rows;
                } else {
                    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--muted);">No data available</td></tr>';
                }
                
                console.log('Data loaded:', json.count, 'records');
            } catch (err) {
                console.error('Load error:', err);
                document.getElementById('tableBody').innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: #ff4466;">Error loading data</td></tr>';
            }
        }
        
        async function uploadFile(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            showNotification('Uploading file...');
            
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    
                    console.log('Uploading', data.length, 'records...');
                    
                    const res = await fetch('/api/upload', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await res.json();
                    
                    if (result.status === 'success') {
                        showNotification('✅ Upload successful! ' + result.count + ' records');
                        document.getElementById('successMsg').style.display = 'block';
                        document.getElementById('successText').textContent = result.message;
                        setTimeout(() => loadData(), 500);
                    } else {
                        showNotification('❌ ' + result.message, true);
                    }
                } catch (err) {
                    showNotification('❌ Error: ' + err.message, true);
                    console.error('Upload error:', err);
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
        
        // Load data on page load and refresh every 30 seconds
        window.addEventListener('DOMContentLoaded', () => {
            loadData();
            setInterval(loadData, 30000);
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
