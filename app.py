#!/usr/bin/env python3
"""
Auto Upload to Cloud Dashboard
Run this on your computer - it will:
1. Scrape Chartink (with your browser login session)
2. Automatically upload to your cloud dashboard
3. Keep dashboard updated every 15 minutes

Replace YOUR_RENDER_URL with your actual Render URL
"""

import time
import csv
import json
import os
import shutil
import requests
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException

# ============================================
# CONFIGURATION
# ============================================

# REPLACE THIS WITH YOUR RENDER URL!
CLOUD_DASHBOARD_URL = "https://momdash-11.onrender.com"  # ⚠️ CHANGE THIS!

CHARTINK_SCREENER_URL = "https://chartink.com/screener/copy-3-step-screener-with-volume-125"
REFRESH_INTERVAL = 15 * 60  # 15 minutes in seconds
DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
CSV_NAME = "screener.csv"
CHROMEDRIVER_PATH = shutil.which("chromedriver") or ""
HEADLESS = False  # Keep False to see browser and login
DOWNLOAD_TIMEOUT = 40

# ============================================
# HELPER FUNCTIONS
# ============================================

def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def make_chrome_options(download_dir: str) -> Options:
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,900")
    
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,
    }
    opts.add_experimental_option("prefs", prefs)
    return opts

def start_driver() -> webdriver.Chrome:
    if CHROMEDRIVER_PATH:
        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    else:
        service = ChromeService()
    
    options = make_chrome_options(str(DOWNLOAD_DIR.resolve()))
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def wait_for_login(driver: webdriver.Chrome, timeout: int = 300):
    """
    Wait for user to login manually
    Checks if we're still on login page
    """
    log("⏳ Waiting for you to login to Chartink...")
    log("   Please login in the browser window")
    log("   Script will continue automatically after login")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            current_url = driver.current_url
            # If we're no longer on login page, assume logged in
            if "login" not in current_url.lower() and "chartink.com" in current_url:
                log("✓ Login detected! Continuing...")
                return True
            time.sleep(2)
        except:
            pass
    
    log("⚠️ Timeout waiting for login")
    return False

def download_chartink_csv(driver: webdriver.Chrome = None) -> Path | None:
    """
    Download CSV from Chartink using browser session
    """
    should_quit = False
    if driver is None:
        driver = start_driver()
        should_quit = True
    
    try:
        log("📊 Loading Chartink screener...")
        driver.get(CHARTINK_SCREENER_URL)
        time.sleep(5)
        
        # Check if we need to login
        if "login" in driver.current_url.lower():
            log("🔐 Login required!")
            if not wait_for_login(driver):
                log("❌ Login failed or timed out")
                return None
            
            # Go back to screener after login
            driver.get(CHARTINK_SCREENER_URL)
            time.sleep(5)
        
        log("📜 Scrolling to backtest section...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        
        # Track existing files
        before = set(DOWNLOAD_DIR.glob("*.csv"))
        
        log("🔍 Looking for download button...")
        try:
            download_btn = driver.find_element(
                By.XPATH,
                "//*[contains(normalize-space(text()), 'Download csv')]"
            )
            download_btn.click()
            log("✓ Clicked download button")
        except NoSuchElementException:
            log("⚠️ Could not find download button")
            return None
        
        # Wait for download
        log("⏳ Waiting for CSV download...")
        waited = 0
        while waited < DOWNLOAD_TIMEOUT:
            after = set(DOWNLOAD_DIR.glob("*.csv"))
            new_files = after - before
            if new_files:
                latest = sorted(new_files, key=lambda p: p.stat().st_mtime)[-1]
                dest = DOWNLOAD_DIR / CSV_NAME
                try:
                    latest.replace(dest)
                except:
                    shutil.copy2(latest, dest)
                log(f"✓ CSV downloaded: {dest}")
                return dest
            time.sleep(1)
            waited += 1
        
        log("⏰ Download timeout")
        return None
        
    except Exception as e:
        log(f"❌ Error: {e}")
        return None
    finally:
        if should_quit and driver:
            driver.quit()

def load_csv_to_json(csv_path: Path) -> list:
    """
    Convert CSV to JSON format
    """
    if not csv_path or not csv_path.exists():
        return []
    
    log(f"📄 Reading CSV: {csv_path}")
    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        normalized = []
        for r in rows:
            item = {
                "date": (
                    r.get("date")
                    or r.get("Date")
                    or r.get("Date Time")
                    or ""
                ),
                "symbol": (
                    r.get("symbol")
                    or r.get("Symbol")
                    or r.get("SYMBOL")
                    or ""
                ),
                "marketcapname": (
                    r.get("marketcapname")
                    or r.get("Marketcap")
                    or r.get("Market Cap")
                    or ""
                ),
                "sector": (
                    r.get("sector")
                    or r.get("Sector")
                    or r.get("Industry")
                    or ""
                ),
                "close": (
                    r.get("close")
                    or r.get("Close")
                    or r.get("ltp")
                    or r.get("LTP")
                    or "0"
                ),
                "price": (
                    r.get("close")
                    or r.get("Close")
                    or r.get("ltp")
                    or r.get("LTP")
                    or "0"
                )
            }
            normalized.append(item)
        
        log(f"✓ Loaded {len(normalized)} rows from CSV")
        return normalized
    except Exception as e:
        log(f"❌ Error reading CSV: {e}")
        return []

def upload_to_cloud(data: list) -> bool:
    """
    Upload data to cloud dashboard
    """
    if not data:
        log("⚠️ No data to upload")
        return False
    
    try:
        log(f"☁️ Uploading {len(data)} records to cloud...")
        
        response = requests.post(
            f"{CLOUD_DASHBOARD_URL}/api/upload",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            log(f"✅ Upload successful! {result.get('count', 0)} records on cloud")
            return True
        else:
            log(f"❌ Upload failed: HTTP {response.status_code}")
            log(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        log(f"❌ Upload error: {e}")
        return False

def update_cycle(driver: webdriver.Chrome = None) -> bool:
    """
    Complete update cycle: Download -> Convert -> Upload
    """
    log("=" * 60)
    log("🔄 Starting update cycle")
    log("=" * 60)
    
    # Download CSV
    csv_path = download_chartink_csv(driver)
    
    if not csv_path:
        log("⚠️ Using existing CSV if available...")
        csv_path = DOWNLOAD_DIR / CSV_NAME
        if not csv_path.exists():
            log("❌ No CSV available")
            return False
    
    # Convert to JSON
    data = load_csv_to_json(csv_path)
    
    if not data:
        log("❌ No data to upload")
        return False
    
    # Upload to cloud
    success = upload_to_cloud(data)
    
    if success:
        log("=" * 60)
        log("✅ Update cycle completed successfully!")
        log("   Your cloud dashboard now has the latest data")
        log("=" * 60)
    else:
        log("⚠️ Update cycle completed with errors")
    
    return success

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║           AUTO UPLOAD TO CLOUD DASHBOARD                       ║
║                                                                ║
║  This script will:                                            ║
║  1. Open Chartink in browser                                  ║
║  2. Wait for you to login (if needed)                         ║
║  3. Download backtest CSV                                     ║
║  4. Upload to your cloud dashboard                            ║
║  5. Repeat every 15 minutes                                   ║
║                                                                ║
║  Your dashboard URL:                                          ║
║  {url:<60} ║
╚════════════════════════════════════════════════════════════════╝
    """.format(url=CLOUD_DASHBOARD_URL))
    
    if "your-app-name" in CLOUD_DASHBOARD_URL:
        print("⚠️  WARNING: You need to update CLOUD_DASHBOARD_URL!")
        print("   Edit the script and replace with your actual Render URL")
        print()
        input("Press Enter to continue anyway (will fail) or Ctrl+C to exit...")
    
    # Start browser once (keeps login session)
    log("🌐 Starting browser...")
    driver = start_driver()
    
    try:
        while True:
            success = update_cycle(driver)
            
            if success:
                log(f"😴 Sleeping for {REFRESH_INTERVAL // 60} minutes...")
                log(f"   Next update at: {datetime.now().fromtimestamp(time.time() + REFRESH_INTERVAL).strftime('%H:%M:%S')}")
            else:
                log("😴 Sleeping for 5 minutes before retry...")
                time.sleep(5 * 60)
                continue
            
            time.sleep(REFRESH_INTERVAL)
            
    except KeyboardInterrupt:
        log("\n🛑 Stopped by user")
    finally:
        if driver:
            driver.quit()
        log("👋 Goodbye!")

if __name__ == "__main__":
    main()
