import os
import time
import csv
import json
import ctypes
import urllib.parse
from bs4 import BeautifulSoup
from seleniumbase import Driver
from wikihow.tor_manager import tor

# Base Paths
BASE_DISCOVERY_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery"
EXTRACTION_DIR = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\extraction"
MAIN_BROWSER_PROFILE = r"c:\Users\Admin\Documents\WikiHow Project\data\browser_session"

# Config
BATCH_SIZE_BEFORE_ROTATION = 30
WAIT_BETWEEN_PAGES = 4

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
        proxy = tor.get_selenium_proxy()
        print(f"[SYSTEM] Initializing Extraction Driver with Native Profile (Proxy: {proxy})")
        # Headless False so user can login if needed
        _driver = Driver(uc=True, headless=False, user_data_dir=MAIN_BROWSER_PROFILE, proxy=proxy)
        print("[SYSTEM] Driver Ready.")
    return _driver

def notify_user_login():
    """Pops up a dialog to let the user log in if session is expired."""
    title = "WikiHow Extraction - Login Required"
    msg = (
        "WikiHow login required or session expired!\n\n"
        "Please log in to WikiHow in the browser window.\n"
        "Once you are logged in, click:\n"
        "  [Yes]    - Continue with extraction\n"
        "  [Cancel] - Exit the script"
    )
    # MB_YESNOCANCEL | MB_ICONWARNING | MB_SYSTEMMODAL | MB_TOPMOST
    res = ctypes.windll.user32.MessageBoxW(0, msg, title, 0x00000003 | 0x00000030 | 0x00040000 | 0x00001000)
    return res == 6 # IDYES

def check_login_state(driver):
    """Detects if we are currently logged out."""
    try:
        page_source = driver.page_source.lower()
        if "log in" in page_source and "log out" not in page_source:
            print("  [WARN] Not logged in detected.")
            if notify_user_login():
                print("  [OK] User confirmed login. Resuming...")
                return True
            else:
                print("  [EXIT] User cancelled.")
                exit(0)
    except:
        pass
    return True

def parse_history_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    revisions = []
    
    # Standard MediaWiki history selector
    history_list = soup.select_one("ul#pagehistory")
    if not history_list:
        # Fallback to broader list check
        rows = soup.find_all("li", {"data-mw-revid": True})
    else:
        rows = history_list.find_all('li', recursive=False)
        
    for li in rows:
        try:
            rev_id = li.get('data-mw-revid', 'unknown')
            ts_link = li.select_one("a.mw-changeslist-date")
            timestamp = ts_link.get_text() if ts_link else ""
            user_link = li.select_one("a.mw-userlink")
            user = user_link.get_text() if user_link else "Anonymous"
            is_anon = "mw-anonuserlink" in (user_link.get('class', []) if user_link else [])
            delta_node = li.select_one("span.mw-plusminus-pos, span.mw-plusminus-neg, span.mw-plusminus-null")
            size_delta = delta_node.get_text() if delta_node else "0"
            comment_node = li.select_one("span.comment")
            comment = comment_node.get_text() if comment_node else ""
            
            revisions.append({
                "revision_id": rev_id, "timestamp": timestamp, "user": user,
                "is_anon": is_anon, "size_delta": size_delta, "comment": comment
            })
        except: pass
    return revisions

def process_category(continuum, category):
    slug = category.replace(" ", "_").lower()
    discovery_csv = os.path.join(BASE_DISCOVERY_DIR, continuum, slug, "discovery_report.csv")
    output_dir = os.path.join(EXTRACTION_DIR, continuum, slug)
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(discovery_csv): return

    with open(discovery_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        articles = list(reader)

    print(f"\n>>> CONTINUUM: {continuum} | CATEGORY: {category} ({len(articles)} arts)")
    
    driver = get_driver()
    processed_count = 0

    for art in articles:
        url = art['URL']
        title = art['Real WikiHow Title']
        
        # Clean URL
        if "/url?q=" in url:
            url = urllib.parse.unquote(url.split("/url?q=")[1].split("&")[0])
            
        safe_title = "".join([c if c.isalnum() else "_" for c in title])[:50]
        out_csv = os.path.join(output_dir, f"{safe_title}_history.csv")
        
        if os.path.exists(out_csv):
            print(f"  [EXIST] {title}")
            continue

        history_url = url + ("&" if "?" in url else "?") + "action=history"
        print(f"  Extracting: {title}...")
        
        try:
            driver.get(history_url)
            time.sleep(WAIT_BETWEEN_PAGES)
            
            # Check for Login/Block
            check_login_state(driver)
            if "blocked" in driver.title.lower():
                print("  [BLOCK] Rotating Tor IP...")
                tor.rotate_ip()
                time.sleep(5)
                driver.get(history_url)
                time.sleep(WAIT_BETWEEN_PAGES)

            revisions = parse_history_page(driver.page_source)
            if revisions:
                with open(out_csv, 'w', newline='', encoding='utf-8') as f_out:
                    writer = csv.DictWriter(f_out, fieldnames=["revision_id", "timestamp", "user", "is_anon", "size_delta", "comment"])
                    writer.writeheader()
                    writer.writerows(revisions)
                print(f"    -> {len(revisions)} revisions.")
            else:
                print("    [!] No revisions found.")

            processed_count += 1
            if processed_count % BATCH_SIZE_BEFORE_ROTATION == 0:
                print("  [SYSTEM] Batch rotation cooldown...")
                tor.rotate_ip()
                time.sleep(5)

        except Exception as e:
            print(f"  [ERR] {title}: {e}")

def main():
    manifest_path = r"c:\Users\Admin\Documents\WikiHow Project\data\mapped_spaces.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    for continuum, data in manifest.items():
        sorted_cats = sorted(data['cats'].items(), key=lambda x: x[1])
        for cat, score in sorted_cats:
            process_category(continuum, cat)

if __name__ == "__main__":
    main()
