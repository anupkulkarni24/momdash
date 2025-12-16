"""
Complete Flask App for Cloud Momentum Dashboard
Works with autoupload.py to receive and display data

DEPLOY INSTRUCTIONS:
1. Save this as app.py
2. Create requirements.txt with: flask, flask-cors
3. Deploy to Render
4. Update autoupload.py with your Render URL
5. Run autoupload.py on your computer

Your Render URL will be: https://YOUR-APP-NAME.onrender.com
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Global storage for uploaded data
cached_data = []
last_update = None

@app.route('/')
def index():
    """Serve the HTML dashboard"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Dashboard Setup Required</h1>
        <p>Please create index.html with your momentum dashboard HTML</p>
        <p>The dashboard HTML should be saved as 'index.html' next to app.py</p>
        """, 404

@app.route('/data.json')
def serve_data():
    """Serve data as data.json for the dashboard JavaScript"""
    return jsonify(cached_data)

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """
    Endpoint for autoupload.py script
    Receives JSON array from CSV conversion
    """
    global cached_data, last_update
    
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            print("❌ Invalid data format received")
            return jsonify({
                "status": "error",
                "message": "Expected JSON array"
            }), 400
        
        cached_data = data
        last_update = datetime.now()
        
        print(f"✅ Uploaded {len(data)} records at {last_update.strftime('%H:%M:%S')}")
        
        return jsonify({
            "status": "success",
            "count": len(data),
            "message": f"Successfully uploaded {len(data)} records"
        })
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
