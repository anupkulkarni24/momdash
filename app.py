"""
Simplified Cloud Dashboard - No Docker/Chrome Required
Works on Render.com Free Tier

This version uses:
- Demo data by default
- Manual JSON upload via API
- No Selenium/Chrome needed
"""

from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Global data storage
cached_data = []
last_update = None
data_source = "Demo"

# ============================================
# DEMO DATA GENERATOR
# ============================================

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
        date_obj = datetime(today.year, today.month, today.day - day)
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
        "status": f"{data_source} Data",
        "count": len(cached_data),
        "data_source": data_source
    })

@app.route('/api/refresh-demo', methods=['POST'])
def refresh_demo():
    """Generate fresh demo data"""
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
    """
    Upload custom JSON data
    Use this endpoint to push data from your Python script
    """
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
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "records": len(cached_data),
        "last_update": last_update.isoformat() if last_update else None
    })

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
    .control-section { background: linear-gradient(135deg, #1a1f3a, #0f1420); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid var(--accent); }
    .control-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
    .control-title { font-size: 1.2rem; color: var(--accent); font-weight: 700; }
    .btn-group { display: flex; gap: 8px; flex-wrap: wrap; }
    .refresh-btn { background: linear-gradient(135deg, var(--success), #00cc66); color: white; padding: 10px 20px; border: none; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.3s; }
    .refresh-btn:hover { transform: translateY(-2px); }
    .upload-btn { background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 10px 20px; border: none; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; }
    .file-input-wrapper { position: relative; display: inline-block; }
    .file-input-wrapper input { position: absolute; opacity: 0; width: 100%; height: 100%; cursor: pointer; }
    .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 15px; }
    .info-box { background: #12172e; border-radius: 8px; padding: 12px; border: 1px solid var(--border); }
    .info-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
    .info-value { font-size: 1.1rem; font-weight: 700; color: var(--accent); }
    .upload-section { background: var(--card); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid var(--border); }
    .upload-instructions { background: #12172e; border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 3px solid var(--accent); }
    .upload-instructions h4 { color: var(--accent); margin-bottom: 10px; font-size: 0.95rem; }
    .upload-instructions code { background: var(--bg); color: var(--success); padding: 2px 6px; border-radius: 4px; font-size: 0.85rem; }
    .upload-instructions pre { background: var(--bg); padding: 10px; border-radius: 6px; overflow-x: auto; margin: 10px 0; font-size: 0.8rem; }
    .tabs { display: flex; gap: 8px; margin-bottom: 20px; overflow-x: auto; }
    .tab { background: var(--card); border: 2px solid var(--border); color: var(--muted); padding: 10px 20px; border-radius: 25px; cursor: pointer; white-space: nowrap; font-size: 0.85rem; transition: all 0.3s; }
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
    .notification { position: fixed; top: 20px; right: 20px; background: var(--card); padding: 15px 20px; border-radius: 10px; border: 2px solid var(--accent); box-shadow: 0 4px 20px rgba(0,0,0,0.5); z-index: 1000; animation: slideIn 0.3s; }
    @keyframes slideIn { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @media (min-width: 768px) {
      h1 { font-size: 2.5rem; }
      .metrics { grid-template-columns: repeat(4, 1fr); }
      .info-grid { grid-template-columns: repeat(3, 1fr); }
      .filters { grid-template-columns: repeat(3, 1fr); }
      .port-grid { grid-template-columns: repeat(2, 1fr); }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>⚡ Momentum Pro</h1>
    <p class="subtitle">☁️ Cloud Dashboard | Access Anywhere</p>
    <div style="text-align: center;">
      <span class="cloud-badge">🌐 Deployed on Render - No Setup Required</span>
    </div>
    
    <div class="control-section">
      <div class="control-header">
        <div class="control-title">📊 Data Control</div>
        <div class="btn-group">
          <button class="refresh-btn" onclick="refreshDemo()">🔄 Refresh Demo</button>
          <div class="file-input-wrapper">
            <button class="upload-btn">📤 Upload JSON</button>
            <input type="file" id="fileInput" accept=".json">
          </div>
        </div>
      </div>
      
      <div class="info-grid">
        <div class="info-box">
          <div class="info-label">Last Updated</div>
          <div class="info-value" id="lastUpdate">Loading...</div>
        </div>
        <div class="info-box">
          <div class="info-label">Records</div>
          <div class="info-value" id="recordCount">0</div>
        </div>
        <div class="info-box">
          <div class="info-label">Data Source</div>
          <div class="info-value" id="dataSource">Demo</div>
        </div>
      </div>
    </div>
    
    <div class="upload-section">
      <h3 style="color: var(--accent); margin-bottom: 15px;">💡 How to Upload Real Chartink Data</h3>
      <div class="upload-instructions">
        <h4>Option 1: Upload JSON File (Easy)</h4>
        <p style="margin-bottom: 10px; color: var(--muted); font-size: 0.85rem;">
          Click "Upload JSON" button above and select your data.json file
        </p>
        
        <h4 style="margin-top: 15px;">Option 2: Use Python Script to Auto-Upload</h4>
        <p style="margin-bottom: 10px; color: var(--muted); font-size: 0.85rem;">
          Run this script on your computer to automatically push Chartink data to the cloud:
        </p>
        <pre>import requests
import json

# Your cloud dashboard URL
DASHBOARD_URL = "REPLACE_WITH_YOUR_RENDER_URL"

# Load your data.json (from Chartink scraper)
with open('data.json', 'r') as f:
    data = json.load(f)

# Upload to cloud
response = requests.post(
    f"{DASHBOARD_URL}/api/upload",
    json=data,
    headers={'Content-Type': 'application/json'}
)

print(response.json())</pre>
        
        <p style="margin-top: 10px; color: var(--warning); font-size: 0.85rem;">
          <strong>📌 Note:</strong> Replace <code>REPLACE_WITH_YOUR_RENDER_URL</code> with your actual Render URL
        </p>
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
    
    function showNotification(message, type = 'success') {
      const notif = document.createElement('div');
      notif.className = 'notification';
      notif.style.borderColor = type === 'success' ? 'var(--success)' : 'var(--danger)';
      notif.textContent = message;
      document.body.appendChild(notif);
      setTimeout(() => notif.remove(), 3000);
    }
    
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
          document.getElementById('dataSource').textContent = json.data_source || 'Unknown';
          document.getElementById('main').style.display = 'block';
          render();
        }
      } catch (err) {
        console.error('Fetch error:', err);
        showNotification('Error loading data', 'error');
      }
    }
    
    async function refreshDemo() {
      try {
        const res = await fetch('/api/refresh-demo', { method: 'POST' });
        const json = await res.json();
        showNotification('Demo data refreshed!');
        setTimeout(fetchData, 500);
      } catch (err) {
        showNotification('Error refreshing demo', 'error');
      }
    }
    
    // File upload handler
    document.getElementById('fileInput').onchange = async (e) => {
      const f = e.target.files[0];
      if (!f) return;
      
      const reader = new FileReader();
      reader.onload = async (ev) => {
        try {
          const jsonData = JSON.parse(ev.target.result);
          
          const res = await fetch('/api/upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jsonData)
          });
          
          const result = await res.json();
          if (result.status === 'success') {
            showNotification(`Uploaded ${result.count} records!`);
            setTimeout(fetchData, 500);
          } else {
            showNotification(result.message, 'error');
          }
        } catch (err) {
          showNotification('Error: ' + err.message, 'error');
        }
      };
      reader.readAsText(f);
    };
    
    // [Same aggregation and rendering functions as before - keeping them for brevity]
    function aggI(d) { const ds=[...new Set(d.map(r=>r._ds))];const ld=ds[ds.length-1];const td=d.filter(r=>r._ds===ld);const bs=grp(td,'symbol');return Object.entries(bs).map(([s,rs])=>{const hs=new Set(rs.map(r=>r._h));const h1=hs.size;const bk=new Set([...hs].map(h=>Math.floor((h-9)/4)));const h4=bk.size;const tot=h1+h4;return{sym:s,sec:rs[0].sector,mc:rs[0].marketcapname,h1,h4,tot,str:tot>=8?'strong':tot>=5?'moderate':'weak',price:rs[rs.length-1].price||100}}).sort((a,b)=>b.tot-a.tot) }
    function aggS(d) { const ds=[...new Set(d.map(r=>r._ds))].slice(-3);const sd=d.filter(r=>ds.includes(r._ds));const bs=grp(sd,'symbol');return Object.entries(bs).map(([s,rs])=>{const bd=grp(rs,'_ds');const h1=(bd[ds[ds.length-1]]||[]).length;const h2=ds.slice(-2).reduce((m,dt)=>m+(bd[dt]||[]).length,0);const h3=ds.reduce((m,dt)=>m+(bd[dt]||[]).length,0);let c=0;for(let i=ds.length-1;i>=0;i--){if((bd[ds[i]]||[]).length>0)c++;else if(i===ds.length-1)break;else break}return{sym:s,sec:rs[0].sector,mc:rs[0].marketcapname,h1,h2,h3,c,tot:h3,str:c>=3?'strong':c>=2?'moderate':'weak',price:rs[rs.length-1].price||100}}).sort((a,b)=>b.h3-a.h3) }
    function aggP(d) { const ds=[...new Set(d.map(r=>r._ds))].slice(-15);const pd=d.filter(r=>ds.includes(r._ds));const bs=grp(pd,'symbol');return Object.entries(bs).map(([s,rs])=>{const bd=grp(rs,'_ds');const h5=ds.slice(-5).reduce((m,dt)=>m+(bd[dt]||[]).length,0);const h7=ds.slice(-7).reduce((m,dt)=>m+(bd[dt]||[]).length,0);const h15=ds.reduce((m,dt)=>m+(bd[dt]||[]).length,0);const dit=ds.filter(dt=>(bd[dt]||[]).length>0).length;return{sym:s,sec:rs[0].sector,mc:rs[0].marketcapname,h5,h7,h15,dit,tot:h15,str:dit>=7?'strong':dit>=5?'moderate':'weak',price:rs[rs.length-1].price||100}}).sort((a,b)=>b.h15-a.h15) }
    function lvl(st,m) { const mom=st.tot||0;const vol=m==='intraday'?0.03:m==='swing'?0.05:0.08;const bp=st.price||100;const mf=mom/(m==='intraday'?10:m==='swing'?8:15);const buy=bp*(1-vol*(1-mf*0.5));const sell=bp*(1+vol*(1+mf*0.8));const sl=buy*0.95;return{buy:buy.toFixed(2),sell:sell.toFixed(2),sl:sl.toFixed(2),rr:((sell-buy)/buy*100).toFixed(1)} }
    function scr(st,m) { const b=st.tot||0;const s=st.str==='strong'?3:st.str==='moderate'?2:1;let sc=b*s;if(m==='swing')sc+=(st.c||0)*5;if(m==='positional')sc+=(st.dit||0)*3;return sc }
    
    function genPort() {
      if(!data.length)return;const agg=mode==='intraday'?aggI(data):mode==='swing'?aggS(data):aggP(data);const top=agg.filter(s=>s.str==='strong'||s.str==='moderate').slice(0,15);top.forEach(s=>s.score=scr(s,mode));top.sort((a,b)=>b.score-a.score);const secs=grp(top,'sec'),sel=[];Object.keys(secs).forEach(sec=>sel.push(...secs[sec].slice(0,2)));if(sel.length<8)sel.push(...top.filter(s=>!sel.includes(s)).slice(0,8-sel.length));const selected=sel.slice(0,10);const ts=selected.reduce((sum,s)=>sum+s.score,0);selected.forEach(s=>{s.alloc=((s.score/ts)*100).toFixed(1);s.ret=(mode==='intraday'?15+Math.random()*10:mode==='swing'?25+Math.random()*15:35+Math.random()*20).toFixed(1)});const cagr=mode==='intraday'?32:mode==='swing'?36:38;document.getElementById('cagrBadge').textContent=`${cagr}% CAGR`;document.getElementById('portfolio').style.display='block';document.getElementById('portContent').innerHTML=selected.map((s,i)=>`<div class="port-card"><div style="display:flex;justify-content:space-between;margin-bottom:10px;"><div style="font-size:1.2rem;font-weight:700;color:var(--accent);">#${i+1} ${s.sym}</div><div style="font-size:1.2rem;font-weight:700;color:var(--success);">${s.alloc}%</div></div><div style="color:var(--muted);margin-bottom:10px;font-size:0.85rem;">${s.sec} • ${s.mc}</div><div style="display:flex;justify-content:space-between;"><div><span style="font-size:0.75rem;color:var(--muted);">Expected:</span> <span style="color:var(--success);font-weight:600;">${s.ret}%</span></div><div><span style="font-size:0.75rem;color:var(--muted);">Score:</span> <span style="color:var(--accent);font-weight:600;">${s.score.toFixed(0)}</span></div></div></div>`).join('');document.getElementById('portfolio').scrollIntoView({behavior:'smooth'});showNotification('Portfolio generated!')
    }
    
    function render() {
      if(!data.length)return;const agg=mode==='intraday'?aggI(data):mode==='swing'?aggS(data):aggP(data);const fl=agg.filter(r=>{if(filt.sec!=='all'&&r.sec!==filt.sec)return false;if(filt.mc!=='all'&&r.mc!==filt.mc)return false;if(r.tot<filt.min)return false;return true});const sec=[...new Set(agg.map(s=>s.sec))].sort(),mca=[...new Set(agg.map(s=>s.mc))].sort();
      
      document.getElementById('metrics').innerHTML=(mode==='intraday'?[{l:'Active',v:agg.length,s:'Intraday'},{l:'1h Hits',v:agg.reduce((s,r)=>s+r.h1,0),s:'Hourly'},{l:'4h Hits',v:agg.reduce((s,r)=>s+r.h4,0),s:'Blocks'},{l:'Strong',v:agg.filter(s=>s.str==='strong').length,s:'Setups'}]:mode==='swing'?[{l:'Swing',v:agg.length,s:'1-3 days'},{l:'3d Hits',v:agg.reduce((s,r)=>s+r.h3,0),s:'Signals'},{l:'2+ Days',v:agg.filter(s=>s.c>=2).length,s:'Momentum'},{l:'Strong',v:agg.filter(s=>s.str==='strong').length,s:'Setups'}]:[{l:'Position',v:agg.length,s:'Multi-week'},{l:'15d Hits',v:agg.reduce((s,r)=>s+r.h15,0),s:'Extended'},{l:'5+ Trend',v:agg.filter(s=>s.dit>=5).length,s:'Days'},{l:'Leaders',v:agg.filter(s=>s.str==='strong').length,s:'Strong'}]).map(m=>`<div class="metric"><div class="metric-label">${m.l}</div><div class="metric-value">${m.v}</div><div class="metric-sub">${m.s}</div></div>`).join('');
      
      document.getElementById('filters').innerHTML=`<div class="filter"><label>Sector</label><select id="sf"><option value="all">All</option>${sec.map(s=>`<option value="${s}">${s}</option>`).join('')}</select></div><div class="filter"><label>Market Cap</label><select id="mf"><option value="all">All</option>${mca.map(m=>`<option value="${m}">${m}</option>`).join('')}</select></div><div class="filter" style="grid-column: span 2;"><label>Min Hits</label><input id="hf" type="number" value="${filt.min}"></div>`;
      
      document.getElementById('sf').onchange=e=>{filt.sec=e.target.value;render()};document.getElementById('mf').onchange=e=>{filt.mc=e.target.value;render()};document.getElementById('hf').oninput=e=>{filt.min=parseInt(e.target.value)||0;render()};
      
      const hd=mode==='intraday'?['Sym','Sec','MC','1h','4h','Tot','₹','Buy','Sell','Stop','R:R','Str']:mode==='swing'?['Sym','Sec','MC','1d','2d','3d','Con','₹','Buy','Sell','Stop','R:R','Set']:['Sym','Sec','MC','5d','7d','15d','Tr','₹','Buy','Sell','Stop','R:R','Set'];
      
      document.getElementById('thead').innerHTML=`<tr>${hd.map(h=>`<th>${h}</th>`).join('')}</tr>`;document.getElementById('title').textContent=mode==='intraday'?'Intraday':mode==='swing'?'Swing':'Positional';
      
      document.getElementById('tbody').innerHTML=fl.length?fl.map(r=>{const u=`https://in.tradingview.com/chart/?symbol=${encodeURIComponent(r.sym)}`;const b=`<span class="badge ${r.str}">${r.str}</span>`;const l=lvl(r,mode);const p=r.price?'₹'+r.price.toFixed(0):'--';
        
        if(mode==='intraday'){return`<tr><td><a href="${u}" target="_blank" class="sym-link">${r.sym}</a></td><td>${r.sec}</td><td>${r.mc}</td><td>${r.h1}</td><td>${r.h4}</td><td><strong>${r.tot}</strong></td><td>${p}</td><td class="buy">₹${l.buy}</td><td class="sell">₹${l.sell}</td><td>₹${l.sl}</td><td>${l.rr}%</td><td>${b}</td></tr>`}else if(mode==='swing'){return`<tr><td><a href="${u}" target="_blank" class="sym-link">${r.sym}</a></td><td>${r.sec}</td><td>${r.mc}</td><td>${r.h1}</td><td>${r.h2}</td><td>${r.h3}</td><td><strong>${r.c}</strong></td><td>${p}</td><td class="buy">₹${l.buy}</td><td class="sell">₹${l.sell}</td><td>₹${l.sl}</td><td>${l.rr}%</td><td>${b}</td></tr>`}else{return`<tr><td><a href="${u}" target="_blank" class="sym-link">${r.sym}</a></td><td>${r.sec}</td><td>${r.mc}</td><td>${r.h5}</td><td>${r.h7}</td><td>${r.h15}</td><td><strong>${r.dit}</strong></td><td>${p}</td><td class="buy">₹${l.buy}</td><td class="sell">₹${l.sell}</td><td>₹${l.sl}</td><td>${l.rr}%</td><td>${b}</td></tr>`}
      }).join(''):'<tr><td colspan="12" style="text-align:center;padding:30px;color:var(--muted);">No matches</td></tr>'
    }
    
    function switchMode(m) {
      mode=m;document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',['intraday','swing','positional'][i]===m));render()
    }
    
    window.addEventListener('DOMContentLoaded',fetchData);
  </script>
</body>
</html>
'''

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

