import os
import time
import csv
import json
from bs4 import BeautifulSoup
from seleniumbase import Driver
from wikihow.tor_manager import tor

# Base Paths (Strict adherence to project standards)
BASE_DISCOVERY_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery"
EXTRACTION_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\extraction\pilot_v2"
# THE BROWSER DATA:
MAIN_BROWSER_PROFILE = r"c:\Users\Admin\Documents\WikiHow Project\data\browser_session"

# Pilot Config
LIMIT_ARTICLES_PER_CAT = 2
LIMIT_CATEGORIES = 2

_driver = None

def get_driver():
    global _driver
    if _driver:
        try:
            _ = _driver.current_url
            return _driver
        except:
            try: _driver.quit()
            except: pass
            _driver = None

    if _driver is None:
        # We do NOT use tor in the visual data/browser_session profile unless specifically calibrated
        # But Tor manager usually provides a proxy if it's running.
        # However, the user said "use the browser data" which implies the existing state.
        
        # Check if Tor is available for this session
        proxy = tor.get_selenium_proxy()
        print(f"  [PILOT] Initializing Driver with MAIN BROWSER DATA (Proxy: {proxy})...")
        
        # We use UC mode as usual
        _driver = Driver(uc=True, headless=False, user_data_dir=MAIN_BROWSER_PROFILE, proxy=proxy)
        print("  Driver Initialized.")
    return _driver

def parse_history_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    revisions = []
    
    # Selector check: ul#pagehistory is standard MediaWiki
    history_list = soup.select_one("ul#pagehistory")
    if not history_list:
        # Fallback for mobile or different skin
        history_list = soup.select_one(".mw-pager-body")
    
    if not history_list: return []
    
    for li in history_list.find_all('li', recursive=False):
        try:
            rev_id = li.get('data-mw-revid', 'unknown')
            ts_link = li.select_one("a.mw-changeslist-date")
            timestamp = ts_link.get_text() if ts_link else ""
            user_link = li.select_one("a.mw-userlink")
            user = user_link.get_text() if user_link else "Anonymous"
            delta_node = li.select_one("span.mw-plusminus-pos, span.mw-plusminus-neg, span.mw-plusminus-null")
            size_delta = delta_node.get_text() if delta_node else "0"
            revisions.append({
                "revision_id": rev_id, "timestamp": timestamp, 
                "user": user, "size_delta": size_delta
            })
        except: pass
    return revisions

def run_pilot():
    print("Starting Extraction Pilot (Mode: Browser Data)...")
    manifest_path = r"c:\Users\Admin\Documents\WikiHow Project\data\mapped_spaces.json"
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    continuum = "domestic"
    data = manifest[continuum]
    sorted_cats = sorted(data['cats'].items(), key=lambda x: x[1])[:LIMIT_CATEGORIES]

    os.makedirs(EXTRACTION_DIR, exist_ok=True)
    driver = get_driver()

    for cat, score in sorted_cats:
        slug = cat.replace(" ", "_").lower()
        discovery_csv = os.path.join(BASE_DISCOVERY_DIR, continuum, slug, "discovery_report.csv")
        
        if not os.path.exists(discovery_csv):
            print(f"  [MISSING] {discovery_csv}")
            continue
        
        with open(discovery_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            articles = list(reader)[:LIMIT_ARTICLES_PER_CAT]

        print(f"\n[PILOT] {cat}:")
        
        for art in articles:
            url = art['URL']
            title = art['Real WikiHow Title']
            
            # Clean up URL (sometimes has Google fragments)
            if "/url?q=" in url:
                url = url.split("/url?q=")[1].split("&")[0]
                url = urllib.parse.unquote(url)
            
            history_url = url + ("&" if "?" in url else "?") + "action=history"
            
            print(f"  Visiting: {title}")
            driver.get(history_url)
            time.sleep(5) # Allowing more time for login-state browser
            
            revisions = parse_history_page(driver.page_source)
            if not revisions:
                print("    [!] 0 revisions found. Retrying with longer wait...")
                time.sleep(5)
                revisions = parse_history_page(driver.page_source)

            print(f"    Success: {len(revisions)} revisions captured.")
            
            safe_title = "".join([c if c.isalnum() else "_" for c in title])[:30]
            out_csv = os.path.join(EXTRACTION_DIR, f"{slug}_{safe_title}.csv")
            with open(out_csv, 'w', newline='', encoding='utf-8') as fo:
                writer = csv.DictWriter(fo, fieldnames=["revision_id", "timestamp", "user", "size_delta"])
                writer.writeheader()
                writer.writerows(revisions)

    print(f"\n[PILOT COMPLETE] Data at {EXTRACTION_DIR}")
    driver.quit()

if __name__ == "__main__":
    import urllib.parse
    run_pilot()
