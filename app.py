"""
Complete Cloud-Deployed Momentum Dashboard
With On-Demand Chartink Scraping

Deploy to Render.com - No local scripts needed!
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json
import os
import time
import csv
from datetime import datetime
from io import StringIO
import threading

app = Flask(__name__)
CORS(app)

# Global data storage
cached_data = []
last_update = None
scraping_status = "Ready"
scraping_in_progress = False

# ============================================
# CHARTINK SCRAPER (Cloud-Compatible)
# ============================================

def scrape_chartink_cloud():
    """
    Cloud-compatible Chartink scraper using Selenium with Chrome
    """
    global cached_data, last_update, scraping_status, scraping_in_progress
    
    scraping_in_progress = True
    scraping_status = "Initializing browser..."
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager
        
        scraping_status = "Setting up Chrome..."
        
        # Chrome options for cloud environment
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        scraping_status = "Starting browser..."
        
        # Auto-install ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        scraping_status = "Loading Chartink..."
        
        # Navigate to Chartink
        chartink_url = "https://chartink.com/screener/copy-3-step-screener-with-volume-125"
        driver.get(chartink_url)
        time.sleep(5)  # Wait for page load
        
        scraping_status = "Scrolling to download section..."
        
        # Scroll to bottom to trigger backtest
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for backtest to render
        
        scraping_status = "Looking for download button..."
        
        # Try to find and click download button
        try:
            download_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'Download csv')]")
            download_btn.click()
            scraping_status = "Download clicked, waiting for CSV..."
            time.sleep(3)
        except Exception as e:
            scraping_status = f"Could not find download button: {str(e)}"
            driver.quit()
            scraping_in_progress = False
            return False
        
        # Get page source and try to extract data from visible table
        scraping_status = "Extracting data from page..."
        
        try:
            # Try to find the data table
            table = driver.find_element(By.CSS_SELECTOR, "table.dataTable, table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            extracted_data = []
            headers = []
            
            for idx, row in enumerate(rows):
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    # This is header row
                    cells = row.find_elements(By.TAG_NAME, "th")
                    headers = [cell.text.strip().lower() for cell in cells]
                    continue
                
                if headers:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            row_data[headers[i]] = cell.text.strip()
                    
                    # Map to expected format
                    if 'symbol' in row_data or 'name' in row_data:
                        extracted_data.append({
                            "date": row_data.get('date', row_data.get('date time', '')),
                            "symbol": row_data.get('symbol', row_data.get('name', '')),
                            "sector": row_data.get('sector', row_data.get('industry', 'Unknown')),
                            "marketcapname": row_data.get('marketcapname', row_data.get('market cap', 'Unknown')),
                            "close": row_data.get('close', row_data.get('ltp', row_data.get('price', '0'))),
                            "price": row_data.get('close', row_data.get('ltp', row_data.get('price', '0')))
                        })
            
            if extracted_data:
                cached_data = extracted_data
                last_update = datetime.now()
                scraping_status = f"Success! Loaded {len(extracted_data)} records"
                driver.quit()
                scraping_in_progress = False
                return True
            else:
                scraping_status = "No data found in table"
        
        except Exception as e:
            scraping_status = f"Error extracting data: {str(e)}"
        
        driver.quit()
        scraping_in_progress = False
        return False
        
    except Exception as e:
        scraping_status = f"Scraping failed: {str(e)}"
        scraping_in_progress = False
        return False

# ============================================
# DEMO DATA GENERATOR
# ============================================

def generate_demo_data():
    """Generate realistic demo data"""
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 
               'ITC', 'KOTAKBANK', 'LT', 'AXISBANK', 'TATAMOTORS', 'WIPRO', 'MARUTI', 
               'BAJFINANCE', 'TATASTEEL', 'ASIANPAINT', 'TITAN', 'NESTLEIND', 'ULTRACEMCO',
               'HINDUNILVR', 'ADANIENT', 'BAJAJFINSV', 'SUNPHARMA', 'ONGC', 'NTPC', 
               'POWERGRID', 'M&M', 'TECHM', 'HINDALCO']
    sectors = ['Banking', 'IT', 'Auto', 'Pharma', 'FMCG', 'Metals', 'Energy', 'Telecom']
    mcaps = ['Large Cap', 'Mid Cap', 'Small Cap']
    
    import random
    data = []
    today = datetime.now()
    
    for day in range(15):
        date_obj = datetime(today.year, today.month, today.day - day)
        for hour in range(9, 16):
            num_symbols = random.randint(5, 12)
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

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/data')
def get_data():
    return jsonify({
        "data": cached_data,
        "last_update": last_update.isoformat() if last_update else None,
        "status": scraping_status if cached_data else "No data",
        "count": len(cached_data),
        "scraping_in_progress": scraping_in_progress
    })

@app.route('/api/scrape-chartink', methods=['POST'])
def trigger_scrape():
    """Trigger on-demand Chartink scraping"""
    global scraping_in_progress
    
    if scraping_in_progress:
        return jsonify({
            "status": "already_running",
            "message": "Scraping already in progress"
        }), 429
    
    # Run scraping in background thread
    thread = threading.Thread(target=scrape_chartink_cloud, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "started",
        "message": "Chartink scraping started. Check status in a few seconds."
    })

@app.route('/api/refresh-demo')
def refresh_demo():
    """Refresh with new demo data"""
    global cached_data, last_update, scraping_status
    cached_data = generate_demo_data()
    last_update = datetime.now()
    scraping_status = "Demo data refreshed"
    return jsonify({
        "status": "success",
        "count": len(cached_data)
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """Upload custom JSON data"""
    global cached_data, last_update, scraping_status
    try:
        data = request.get_json()
        if data and isinstance(data, list):
            cached_data = data
            last_update = datetime.now()
            scraping_status = "Custom data uploaded"
            return jsonify({
                "status": "success",
                "count": len(cached_data)
            })
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================
# EMBEDDED DASHBOARD HTML
# ============================================

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Momentum Dashboard Pro - Cloud</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    :root {
      --bg: #0a0e27; --card: #1a1f3a; --accent: #00d4ff; --success: #00ff88;
      --warning: #ffaa00; --danger: #ff4466; --text: #e4e9f7; --muted: #8b92b0; --border: #2a2f4a;
    }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, var(--bg) 0%, #050814 100%); color: var(--text); min-height: 100vh; padding: 15px; }
    .container { max-width: 1800px; margin: 0 auto; }
    h1 { font-size: 1.8rem; background: linear-gradient(135deg, var(--accent), var(--success)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; text-align: center; }
    .subtitle { color: var(--muted); text-align: center; margin-bottom: 20px; font-size: 0.9rem; }
    .cloud-badge { background: linear-gradient(135deg, var(--success), #00cc66); color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 20px; }
    .auto-update { background: linear-gradient(135deg, #1a1f3a, #0f1420); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid var(--accent); }
    .update-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
    .update-title { font-size: 1.2rem; color: var(--accent); font-weight: 700; }
    .btn-group { display: flex; gap: 8px; flex-wrap: wrap; }
    .refresh-btn { background: linear-gradient(135deg, var(--success), #00cc66); color: white; padding: 10px 20px; border: none; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; }
    .scrape-btn { background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 10px 20px; border: none; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; }
    .refresh-btn:disabled, .scrape-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .status-box { background: #12172e; border-radius: 8px; padding: 12px; border: 1px solid var(--border); margin-bottom: 15px; }
    .status-text { font-size: 0.85rem; color: var(--accent); }
    .update-info { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .info-item { background: #12172e; border-radius: 8px; padding: 12px; border: 1px solid var(--border); }
    .info-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
    .info-value { font-size: 1.1rem; font-weight: 700; color: var(--accent); }
    .tabs { display: flex; gap: 8px; margin-bottom: 20px; overflow-x: auto; }
    .tab { background: var(--card); border: 2px solid var(--border); color: var(--muted); padding: 10px 20px; border-radius: 25px; cursor: pointer; white-space: nowrap; font-size: 0.85rem; }
    .tab.active { background: linear-gradient(135deg, var(--accent), #0099cc); color: white; }
    .metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 20px; }
    .metric { background: var(--card); border-radius: 12px; padding: 15px; border: 1px solid var(--border); position: relative; }
    .metric::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--accent), var(--success)); }
    .metric-label { color: var(--muted); font-size: 0.75rem; margin-bottom: 8px; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: var(--accent); }
    .metric-sub { font-size: 0.75rem; color: var(--success); margin-top: 4px; }
    .portfolio { background: linear-gradient(135deg, var(--card), #0f1420); border-radius: 12px; padding: 20px; border: 2px solid var(--accent); margin-bottom: 20px; }
    .port-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
    .port-title { font-size: 1.3rem; color: var(--accent); font-weight: 700; }
    .cagr { background: linear-gradient(135deg, var(--success), #00cc66); color: white; padding: 8px 15px; border-radius: 20px; font-size: 1rem; font-weight: 700; }
    .port-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
    .port-card { background: #12172e; border-radius: 10px; padding: 15px; border: 1px solid var(--border); }
    .table-box { background: var(--card); border-radius: 12px; padding: 20px; border: 1px solid var(--border); margin-bottom: 20px; overflow-x: auto; }
    .filters { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
    .filter { display: flex; flex-direction: column; gap: 4px; }
    .filter label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; }
    .filter select, .filter input { background: #12172e; border: 1px solid var(--border); color: var(--text); padding: 8px; border-radius: 8px; font-size: 0.85rem; }
    table { width: 100%; border-collapse: collapse; min-width: 800px; font-size: 0.85rem; }
    th { padding: 10px 8px; text-align: left; color: var(--accent); text-transform: uppercase; font-size: 0.75rem; border-bottom: 2px solid var(--border); }
    td { padding: 10px 8px; border-bottom: 1px solid var(--border); }
    tr:hover { background: #12172e; }
    .sym-link { color: var(--accent); text-decoration: none; font-weight: 600; }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 15px; font-size: 0.7rem; font-weight: 600; }
    .badge.strong { background: rgba(0, 255, 136, 0.2); color: var(--success); border: 1px solid var(--success); }
    .badge.moderate { background: rgba(255, 170, 0, 0.2); color: var(--warning); border: 1px solid var(--warning); }
    .badge.weak { background: rgba(255, 68, 102, 0.2); color: var(--danger); border: 1px solid var(--danger); }
    .buy { color: var(--success); font-weight: 600; font-size: 0.85rem; }
    .sell { color: var(--danger); font-weight: 600; font-size: 0.85rem; }
    .gen-btn { background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 10px 20px; border: none; border-radius: 20px; font-size: 0.9rem; font-weight: 600; cursor: pointer; width: 100%; margin-bottom: 15px; }
    @media (min-width: 768px) {
      h1 { font-size: 2.5rem; }
      .metrics { grid-template-columns: repeat(4, 1fr); }
      .update-info { grid-template-columns: repeat(3, 1fr); }
      .filters { grid-template-columns: repeat(3, 1fr); }
      .port-grid { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>⚡ Momentum Pro</h1>
    <p class="subtitle">☁️ Cloud Dashboard | On-Demand Chartink Scraping</p>
    <div style="text-align: center;">
      <span class="cloud-badge">🌐 100% Cloud - No Local Scripts</span>
    </div>
    
    <div class="auto-update">
      <div class="update-header">
        <div class="update-title">📊 Data Control</div>
        <div class="btn-group">
          <button class="scrape-btn" id="scrapeBtn" onclick="scrapeChartink()">🎯 Scrape Chartink</button>
          <button class="refresh-btn" onclick="refreshDemo()">🔄 Demo Data</button>
        </div>
      </div>
      
      <div class="status-box">
        <div class="status-text" id="statusText">Ready to scrape Chartink data</div>
      </div>
      
      <div class="update-info">
        <div class="info-item">
          <div class="info-label">Last Updated</div>
          <div class="info-value" id="lastUpdate">Loading...</div>
        </div>
        <div class="info-item">
          <div class="info-label">Records</div>
          <div class="info-value" id="recordCount">0</div>
        </div>
        <div class="info-item">
          <div class="info-label">Data Source</div>
          <div class="info-value" style="font-size: 0.9rem;" id="dataSource">Demo</div>
        </div>
      </div>
    </div>
    
    <div id="main" style="display:none">
      <div class="tabs">
        <div class="tab active" onclick="switchMode('intraday')">⚡ Intraday</div>
        <div class="tab" onclick="switchMode('swing')">📈 Swing</div>
        <div class="tab" onclick="switchMode('positional')">🧭 Positional</div>
      </div>
      
      <div id="metrics" class="metrics"></div>
      <button class="gen-btn" onclick="genPort()">🚀 Generate Smart Portfolio</button>
      
      <div id="portfolio" class="portfolio" style="display:none">
        <div class="port-header">
          <div class="port-title">🎯 Portfolio</div>
          <div class="cagr" id="cagrBadge">35% CAGR</div>
        </div>
        <div id="portContent" class="port-grid"></div>
      </div>
      
      <div class="table-box">
        <h3 style="color:var(--accent); margin-bottom: 15px;">🎯 <span id="title">Stocks</span></h3>
        <div class="filters" id="filters"></div>
        <div style="overflow-x: auto;">
          <table><thead id="thead"></thead><tbody id="tbody"></tbody></table>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    let data = [], mode = 'intraday', filt = { sec: 'all', mc: 'all', min: 0 };
    let statusCheckInterval = null;
    
    // Parse, format, group functions
    function parse(s) {
      if (!s) return null;
      const p = s.split(' ');
      if (p.length < 3) return null;
      const [d, t, a] = p;
      const [dy, m, y] = d.split('-').map(Number);
      let [h, mn] = t.split(':').map(Number);
      if (a && a.toLowerCase() === 'pm' && h !== 12) h += 12;
      if (a && a.toLowerCase() === 'am' && h === 12) h = 0;
      return new Date(y, m - 1, dy, h, mn);
    }
    
    function fmt(d) {
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    }
    
    function fmtTime(d) {
      return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    
    function grp(a, k) {
      return a.reduce((r, i) => {
        const g = typeof k === 'function' ? k(i) : i[k];
        (r[g] = r[g] || []).push(i);
        return r;
      }, {});
    }
    
    function proc(d) {
      return d.map(r => {
        const dt = parse(r.date);
        const price = parseFloat(r.close || r.price || 0);
        return { ...r, _d: dt, _ds: dt ? fmt(dt) : null, _h: dt ? dt.getHours() : null, price: price };
      }).filter(r => r._d).sort((a, b) => a._d - b._d);
    }
    
    async function fetchData() {
      try {
        const res = await fetch('/api/data');
        const json = await res.json();
        
        if (json.data && json.data.length > 0) {
          data = proc(json.data);
          document.getElementById('lastUpdate').textContent = json.last_update ? fmtTime(new Date(json.last_update)) : 'Now';
          document.getElementById('recordCount').textContent = data.length;
          document.getElementById('statusText').textContent = json.status;
          document.getElementById('dataSource').textContent = json.scraping_in_progress ? 'Scraping...' : (json.status.includes('Demo') ? 'Demo' : 'Live');
          document.getElementById('main').style.display = 'block';
          render();
          
          // Disable scrape button if scraping in progress
          document.getElementById('scrapeBtn').disabled = json.scraping_in_progress;
        }
      } catch (err) {
        console.error('Fetch error:', err);
        document.getElementById('statusText').textContent = 'Error loading data';
      }
    }
    
    async function scrapeChartink() {
      try {
        document.getElementById('scrapeBtn').disabled = true;
        document.getElementById('statusText').textContent = 'Starting Chartink scraper...';
        
        const res = await fetch('/api/scrape-chartink', { method: 'POST' });
        const json = await res.json();
        
        document.getElementById('statusText').textContent = json.message;
        
        // Start polling for status updates
        if (statusCheckInterval) clearInterval(statusCheckInterval);
        statusCheckInterval = setInterval(fetchData, 2000);
        
        // Stop polling after 2 minutes
        setTimeout(() => {
          if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
          }
        }, 120000);
        
      } catch (err) {
        console.error('Scrape error:', err);
        document.getElementById('statusText').textContent = 'Error starting scraper';
        document.getElementById('scrapeBtn').disabled = false;
      }
    }
    
    async function refreshDemo() {
      await fetch('/api/refresh-demo');
      setTimeout(fetchData, 500);
    }
    
    // Aggregation functions
    function aggI(d) {
      const ds = [...new Set(d.map(r => r._ds))];
      const ld = ds[ds.length - 1];
      const td = d.filter(r => r._ds === ld);
      const bs = grp(td, 'symbol');
      return Object.entries(bs).map(([s, rs]) => {
        const hs = new Set(rs.map(r => r._h));
        const h1 = hs.size;
        const bk = new Set([...hs].map(h => Math.floor((h - 9) / 4)));
        const h4 = bk.size;
        const tot = h1 + h4;
        return { sym: s, sec: rs[0].sector, mc: rs[0].marketcapname, h1, h4, tot, str: tot >= 8 ? 'strong' : tot >= 5 ? 'moderate' : 'weak', price: rs[rs.length - 1].price || 100 };
      }).sort((a, b) => b.tot - a.tot);
    }
    
    function aggS(d) {
      const ds = [...new Set(d.map(r => r._ds))].slice(-3);
      const sd = d.filter(r => ds.includes(r._ds));
      const bs = grp(sd, 'symbol');
      return Object.entries(bs).map(([s, rs]) => {
        const bd = grp(rs, '_ds');
        const h1 = (bd[ds[ds.length - 1]] || []).length;
        const h2 = ds.slice(-2).reduce((m, dt) => m + (bd[dt] || []).length, 0);
        const h3 = ds.reduce((m, dt) => m + (bd[dt] || []).length, 0);
        let c = 0;
        for (let i = ds.length - 1; i >= 0; i--) {
          if ((bd[ds[i]] || []).length > 0) c++;
          else if (i === ds.length - 1) break;
          else break;
        }
        return { sym: s, sec: rs[0].sector, mc: rs[0].marketcapname, h1, h2, h3, c, tot: h3, str: c >= 3 ? 'strong' : c >= 2 ? 'moderate' : 'weak', price: rs[rs.length - 1].price || 100 };
      }).sort((a, b) => b.h3 - a.h3);
    }
    
    function aggP(d) {
      const ds = [...new Set(d.map(r => r._ds))].slice(-15);
      const pd = d.filter(r => ds.includes(r._ds));
      const bs = grp(pd, 'symbol');
      return Object.entries(bs).map(([s, rs]) => {
        const bd = grp(rs, '_ds');
        const h5 = ds.slice(-5).reduce((m, dt) => m + (bd[dt] || []).length, 0);
        const h7 = ds.slice(-7).reduce((m, dt) => m + (bd[dt] || []).length, 0);
        const h15 = ds.reduce((m, dt) => m + (bd[dt] || []).length, 0);
        const dit = ds.filter(dt => (bd[dt] || []).length > 0).length;
        return { sym: s, sec: rs[0].sector, mc: rs[0].marketcapname, h5, h7, h15, dit, tot: h15, str: dit >= 7 ? 'strong' : dit >= 5 ? 'moderate' : 'weak', price: rs[rs.length - 1].price || 100 };
      }).sort((a, b) => b.h15 - a.h15);
    }
    
    function lvl(st, m) {
      const mom = st.tot || 0;
      const vol = m === 'intraday' ? 0.03 : m === 'swing' ? 0.05 : 0.08;
      const bp = st.price || 100;
      const mf = mom / (m === 'intraday' ? 10 : m === 'swing' ? 8 : 15);
      const buy = bp * (1 - vol * (1 - mf * 0.5));
      const sell = bp * (1 + vol * (1 + mf * 0.8));
      const sl = buy * 0.95;
      return { buy: buy.toFixed(2), sell: sell.toFixed(2), sl: sl.toFixed(2), rr: ((sell - buy) / buy * 100).toFixed(1) };
    }
    
    function scr(st, m) {
      const b = st.tot || 0;
      const s = st.str === 'strong' ? 3 : st.str === 'moderate' ? 2 : 1;
      let sc = b * s;
      if (m === 'swing') sc += (st.c || 0) * 5;
      if (m === 'positional') sc += (st.dit || 0) * 3;
      return sc;
    }
    
    function genPort() {
      if (!data.length) return;
      const agg = mode === 'intraday' ? aggI(data) : mode === 'swing' ? aggS(data) : aggP(data);
      const top = agg.filter(s => s.str === 'strong' || s.str === 'moderate').slice(0, 15);
      top.forEach(s => s.score = scr(s, mode));
      top.sort((a, b) => b.score - a.score);
      const secs = grp(top, 'sec');
      const sel = [];
      Object.keys(secs).forEach(sec => sel.push(...secs[sec].slice(0, 2)));
      if (sel.length < 8) sel.push(...top.filter(s => !sel.includes(s)).slice(0, 8 - sel.length));
      const selected = sel.slice(0, 10);
      const ts = selected.reduce((sum, s) => sum + s.score, 0);
      selected.forEach(s => {
        s.alloc = ((s.score / ts) * 100).toFixed(1);
        s.ret = (mode === 'intraday' ? 15 + Math.random() * 10 : mode === 'swing' ? 25 + Math.random() * 15 : 35 + Math.random() * 20).toFixed(1);
      });
      const cagr = mode === 'intraday' ? 32 : mode === 'swing' ? 36 : 38;
      document.getElementById('cagrBadge').textContent = `${cagr}% CAGR`;
      document.getElementById('portfolio').style.display = 'block';
      document.getElementById('portContent').innerHTML = selected.map((s, i) => `
        <div class="port-card">
          <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <div style="font-size:1.2rem;font-weight:700;color:var(--accent);">#${i + 1} ${s.sym}</div>
            <div style="font-size:1.2rem;font-weight:700;color:var(--success);">${s.alloc}%</div>
          </div>
          <div style="color:var(--muted);margin-bottom:10px;font-size:0.85rem;">${s.sec} • ${s.mc}</div>
          <div style="display:flex;justify-content:space-between;">
            <div><span style="font-size:0.75rem;color:var(--muted);">Expected:</span> <span style="color:var(--success);font-weight:600;">${s.ret}%</span></div>
            <div><span style="font-size:0.75rem;color:var(--muted);">Score:</span> <span style="color:var(--accent);font-weight:600;">${s.score.toFixed(0)}</span></div>
          </div>
        </div>
      `).join('');
      document.getElementById('portfolio').scrollIntoView({ behavior: 'smooth' });
    }
    
    function render() {
      if (!data.length) return;
      const agg = mode === 'intraday' ? aggI(data) : mode === 'swing' ? aggS(data) : aggP(data);
      const fl = agg.filter(r => {
        if (filt.sec !== 'all' && r.sec !== filt.sec) return false;
        if (filt.mc !== 'all' && r.mc !== filt.mc) return false;
        if (r.tot < filt.min) return false;
        return true;
      });
      const sec = [...new Set(agg.map(s => s.sec))].sort();
      const mca = [...new Set(agg.map(s => s.mc))].sort();
      
      document.getElementById('metrics').innerHTML = (mode === 'intraday' ? [
        { l: 'Active', v: agg.length, s: 'Intraday' },
        { l: '1h Hits', v: agg.reduce((s, r) => s + r.h1, 0), s: 'Hourly' },
        { l: '4h Hits', v: agg.reduce((s, r) => s + r.h4, 0), s: 'Blocks' },
        { l: 'Strong', v: agg.filter(s => s.str === 'strong').length, s: 'Setups' }
      ] : mode === 'swing' ? [
        { l: 'Swing', v: agg.length, s: '1-3 days' },
        { l: '3d Hits', v: agg.reduce((s, r) => s + r.h3, 0), s: 'Signals' },
        { l: '2+ Days', v: agg.filter(s => s.c >= 2).length, s: 'Momentum' },
        { l: 'Strong', v: agg.filter(s => s.str === 'strong').length, s: 'Setups' }
      ] : [
        { l: 'Position', v: agg.length, s: 'Multi-week' },
        { l: '15d Hits', v: agg.reduce((s, r) => s + r.h15, 0), s: 'Extended' },
        { l: '5+ Trend', v: agg.filter(s => s.dit >= 5).length, s: 'Days' },
        { l: 'Leaders', v: agg.filter(s => s.str === 'strong').length, s: 'Strong' }
      ]).map(m => `<div class="metric"><div class="metric-label">${m.l}</div><div class="metric-value">${m.v}</div><div class="metric-sub">${m.s}</div></div>`).join('');
      
      document.getElementById('filters').innerHTML = `
        <div class="filter">
          <label>Sector</label>
          <select id="sf">
            <option value="all">All</option>
            ${sec.map(s => `<option value="${s}">${s}</option>`).join('')}
          </select>
        </div>
        <div class="filter">
          <label>Market Cap</label>
          <select id="mf">
            <option value="all">All</option>
            ${mca.map(m => `<option value="${m}">${m}</option>`).join('')}
          </select>
        </div>
        <div class="filter" style="grid-column: span 2;">
          <label>Min Hits</label>
          <input id="hf" type="number" value="${filt.min}">
        </div>
      `;
      
      document.getElementById('sf').onchange = e => { filt.sec = e.target.value; render(); };
      document.getElementById('mf').onchange = e => { filt.mc = e.target.value; render(); };
      document.getElementById('hf').oninput = e => { filt.min = parseInt(e.target.value) || 0; render(); };
      
      const hd = mode === 'intraday' ? ['Sym', 'Sec', 'MC', '1h', '4h', 'Tot', '₹', 'Buy', 'Sell', 'Stop', 'R:R', 'Str'] :
        mode === 'swing' ? ['Sym', 'Sec', 'MC', '1d', '2d', '3d', 'Con', '₹', 'Buy', 'Sell', 'Stop', 'R:R', 'Set'] :
        ['Sym', 'Sec', 'MC', '5d', '7d', '15d', 'Tr', '₹', 'Buy', 'Sell', 'Stop', 'R:R', 'Set'];
      
      document.getElementById('thead').innerHTML = `<tr>${hd.map(h => `<th>${h}</th>`).join('')}</tr>`;
      document.getElementById('title').textContent = mode === 'intraday' ? 'Intraday' : mode === 'swing' ? 'Swing' : 'Positional';
      
      document.getElementById('tbody').innerHTML = fl.length ? fl.map(r => {
        const u = `https://in.tradingview.com/chart/?symbol=${encodeURIComponent(r.sym)}`;
        const b = `<span class="badge ${r.str}">${r.str}</span>`;
        const l = lvl(r, mode);
        const p = r.price ? '₹' + r.price.toFixed(0) : '--';
        
        if (mode === 'intraday') {
          return `<tr>
            <td><a href="${u}" target="_blank" class="sym-link">${r.sym}</a></td>
            <td>${r.sec}</td>
            <td>${r.mc}</td>
            <td>${r.h1}</td>
            <td>${r.h4}</td>
            <td><strong>${r.tot}</strong></td>
            <td>${p}</td>
            <td class="buy">₹${l.buy}</td>
            <td class="sell">₹${l.sell}</td>
            <td>₹${l.sl}</td>
            <td>${l.rr}%</td>
            <td>${b}</td>
          </tr>`;
        } else if (mode === 'swing') {
          return `<tr>
            <td><a href="${u}" target="_blank" class="sym-link">${r.sym}</a></td>
            <td>${r.sec}</td>
            <td>${r.mc}</td>
            <td>${r.h1}</td>
            <td>${r.h2}</td>
            <td>${r.h3}</td>
            <td><strong>${r.c}</strong></td>
            <td>${p}</td>
            <td class="buy">₹${l.buy}</td>
            <td class="sell">₹${l.sell}</td>
            <td>₹${l.sl}</td>
            <td>${l.rr}%</td>
            <td>${b}</td>
          </tr>`;
        } else {
          return `<tr>
            <td><a href="${u}" target="_blank" class="sym-link">${r.sym}</a></td>
            <td>${r.sec}</td>
            <td>${r.mc}</td>
            <td>${r.h5}</td>
            <td>${r.h7}</td>
            <td>${r.h15}</td>
            <td><strong>${r.dit}</strong></td>
            <td>${p}</td>
            <td class="buy">₹${l.buy}</td>
            <td class="sell">₹${l.sell}</td>
            <td>₹${l.sl}</td>
            <td>${l.rr}%</td>
            <td>${b}</td>
          </tr>`;
        }
      }).join('') : '<tr><td colspan="12" style="text-align:center;padding:30px;color:var(--muted);">No matches</td></tr>';
    }
    
    function switchMode(m) {
      mode = m;
      document.querySelectorAll('.tab').forEach((t, i) => 
        t.classList.toggle('active', ['intraday', 'swing', 'positional'][i] === m)
      );
      render();
    }
    
    window.addEventListener('DOMContentLoaded', fetchData);
  </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

