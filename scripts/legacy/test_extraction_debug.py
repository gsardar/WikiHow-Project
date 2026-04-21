import os
import time
import csv
import json
from bs4 import BeautifulSoup
from seleniumbase import Driver
from wikihow.tor_manager import tor

# Base Paths
BASE_DISCOVERY_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery"
EXTRACTION_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\extraction\pilot_v3"
MAIN_BROWSER_PROFILE = r"c:\Users\Admin\Documents\WikiHow Project\data\browser_session"

LIMIT_ARTICLES = 1

def parse_history_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Debug: Save snippet of HTML to see structure
    with open(os.path.join(EXTRACTION_DIR, "debug_history.html"), "w", encoding="utf-8") as f:
        f.write(html)
        
    revisions = []
    # Trying broader selectors
    history_list = soup.select_one("#pagehistory") or soup.select_one(".mw-pager-body") or soup.select_one("ul.mw-contributions-list")
    
    if not history_list:
        print("      [DEBUG] No list found with standard selectors. Searching for any <li> with data-mw-revid...")
        rows = soup.find_all("li", {"data-mw-revid": True})
        if rows:
            print(f"      [DEBUG] Found {len(rows)} rows using data-mw-revid directly.")
        else:
            rows = []
    else:
        rows = history_list.find_all('li', recursive=False)

    for li in rows:
        try:
            rev_id = li.get('data-mw-revid', 'unknown')
            ts_link = li.select_one("a.mw-changeslist-date")
            timestamp = ts_link.get_text() if ts_link else ""
            user_link = li.select_one("a.mw-userlink")
            user = user_link.get_text() if user_link else "Anonymous"
            revisions.append({"revision_id": rev_id, "timestamp": timestamp, "user": user})
        except: pass
    return revisions

def run_debug_pilot():
    os.makedirs(EXTRACTION_DIR, exist_ok=True)
    proxy = tor.get_selenium_proxy()
    print(f"  [DEBUG] Driver with Proxy: {proxy}")
    driver = Driver(uc=True, headless=True, user_data_dir=MAIN_BROWSER_PROFILE, proxy=proxy)
    
    url = "https://www.wikihow.com/Care-for-a-Baby?action=history"
    print(f"  Visiting: {url}")
    driver.get(url)
    time.sleep(10) # Heavy wait
    
    # Click any cookie consent if present (though MAIN_PROFILE should have it)
    try:
        consent_btn = driver.find_element("css selector", "#gdpr-consent-accept")
        consent_btn.click()
        print("    Accepted GDPR consent.")
    except: pass

    revisions = parse_history_page(driver.page_source)
    print(f"  Captured {len(revisions)} revisions.")
    
    if len(revisions) == 0:
        print(f"  [CRITICAL] Still 0 revisions. Check debug_history.html in {EXTRACTION_DIR}")
    
    driver.quit()

if __name__ == "__main__":
    run_debug_pilot()
