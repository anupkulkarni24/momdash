from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import random
import threading
import time

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

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Momentum Dashboard Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #0a0e27 0%, #050814 100%); color: #e4e9f7; min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; font-size: 2rem; margin-bottom: 30px; background: linear-gradient(135deg, #00d4ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .card { background: #1a1f3a; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #2a2f4a; }
        .btn { background: linear-gradient(135deg, #00d4ff, #0099cc); color: white; padding: 12px 24px; border: none; border-radius: 25px; cursor: pointer; font-weight: 600; margin: 5px; }
        .btn:hover { transform: translateY(-2px); }
        .info { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .info-box { background: #12172e; padding: 15px; border-radius: 8px; }
        .info-label { font-size: 0.8rem; color: #8b92b0; text-transform: uppercase; }
        .info-value { font-size: 1.5rem; color: #00d4ff; font-weight: 700; margin-top: 5px; }
        .success { color: #00ff88; }
        #fileInput { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Momentum Dashboard Pro</h1>
        <div class="card">
            <h2 style="margin-bottom: 15px;">📊 Data Control</h2>
            <button class="btn" onclick="document.getElementById('fileInput').click()">📤 Upload JSON</button>
            <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
            <input type="file" id="fileInput" accept=".json" onchange="uploadFile(event)">
            <div class="info">
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
                    <div class="info-value" id="dataSource">Demo</div>
                </div>
            </div>
        </div>
        <div class="card">
            <p class="success">✅ Dashboard is live and ready!</p>
            <p style="margin-top: 10px; color: #8b92b0;">Upload your JSON file to see your data visualized.</p>
        </div>
    </div>
    <script>
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const json = await res.json();
                document.getElementById('lastUpdate').textContent = new Date(json.last_update).toLocaleTimeString();
                document.getElementById('recordCount').textContent = json.count;
                document.getElementById('dataSource').textContent = json.data_source;
            } catch (err) {
                console.error(err);
            }
        }
        
        async function uploadFile(event) {
            const file = event.target.files[0];
            if (!file) return;
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
                    alert(result.message || 'Upload successful!');
                    loadData();
                } catch (err) {
                    alert('Error: ' + err.message);
                }
            };
            reader.readAsText(file);
        }
        
        async function refreshData() {
            const res = await fetch('/api/refresh-demo', { method: 'POST' });
            const json = await res.json();
            alert(json.message);
            loadData();
        }
        
        window.onload = loadData;
    </script>
</body>
</html>
    """)

@app.route('/api/data')
def get_data():
    return jsonify({
        "data": cached_data,
        "last_update": last_update.isoformat() if last_update else None,
        "status": scraping_status,
        "count": len(cached_data),
        "data_source": data_source
    })

@app.route('/api/refresh-demo', methods=['POST'])
def refresh_demo():
    global cached_data, last_update, data_source
    cached_data = generate_demo_data()
    last_update = datetime.now()
    data_source = "Demo"
    return jsonify({
        "status": "success",
        "message": "Demo data refreshed",
        "count": len(cached_data)
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    global cached_data, last_update, data_source
    try:
        data = request.get_json()
        if data and isinstance(data, list) and len(data) > 0:
            cached_data = data
            last_update = datetime.now()
            data_source = "Uploaded"
            return jsonify({
                "status": "success",
                "message": f"Uploaded {len(data)} records",
                "count": len(cached_data)
            })
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
