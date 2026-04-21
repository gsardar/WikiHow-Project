import os
import time
import json
import csv
import urllib.parse
import requests
import ctypes
from seleniumbase import Driver
from wikihow.tor_manager import tor
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "discovery")
# Isolated profile - completely separate from the main browser_session data
GOOGLE_PROFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "google_scrape_session")
MAX_PAGES = 100

_google_driver = None

def _get_google_driver():
    """Returns a persistent browser instance. Reuses existing if healthy."""
    global _google_driver
    
    if _google_driver:
        try:
            # Check if responsive
            _ = _google_driver.current_url
            return _google_driver
        except:
            print("  [SYSTEM] Persistent driver became unresponsive. Reinitializing...")
            try: _google_driver.quit()
            except: pass
            _google_driver = None

    if _google_driver is None:
        os.makedirs(GOOGLE_PROFILE, exist_ok=True)
        proxy = tor.get_selenium_proxy()
        print(f"Initializing Persistent Google Scrape Driver...")
        if proxy:
            print(f"  [NETWORK] Routing via Proxy: {proxy}")
        _google_driver = Driver(uc=True, headless=False, user_data_dir=GOOGLE_PROFILE,
                                agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                proxy=proxy)
        print("  Persistent Driver Ready.")
    return _google_driver

def _rotate_in_place(driver):
    """Rotates Tor IP and cleans browser state WITHOUT restarting the instance."""
    print("    [TOR] Rotating identity (NEWNYM)...")
    success, msg = tor.rotate_ip()
    print(f"    [TOR] {msg}")
    
    print("    [CLEAN] Clearing browser cookies and cache...")
    try:
        driver.delete_all_cookies()
        try:
            # Deep clean via CDP
            driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        except:
            pass # fallback if CDP fails
        print("    [CLEAN] Success.")
    except Exception as e:
        print(f"    [CLEAN] Error: {e}")
    
    print("    [COOLDOWN] Waiting 10s for new circuit stabilization...")
    time.sleep(10)


def resolve_real_title(url):
    """Visits the page to extract the actual H1 title."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, proxies=tor.get_requests_proxies(), timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            h1 = soup.select_one("h1")
            return h1.get_text().strip() if h1 else "Not Found"
    except:
        pass
    return "Error Resolving"

def init_csv(csv_path):
    """Forcefully creates the CSV and folder if missing, then writes header."""
    folder = os.path.dirname(csv_path)
    if not os.path.exists(folder): os.makedirs(folder)
    
    headers = ["Continuum", "Query", "Google Title", "Real WikiHow Title", "URL"]
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
    print(f"  [INIT] Created report at {csv_path}")

def _handle_google_consent(driver):
    """Auto-clicks through Google's 'Before you continue' consent/terms page."""
    url  = driver.current_url.lower()
    page = driver.page_source.lower()
    
    # Only act if we are on a Google-related domain
    if "google" not in url:
        return
        
    if "consent.google" in url or "before you continue" in page or "cookie" in url:
        print("    [CONSENT] Google consent page detected - auto-accepting...")
        accept_selectors = [
            "button#L2AGLb",
            "button[aria-label='Accept all']",
            "button[jsname='b3VHJd']",
            "form[action*='consent'] button",
            "div#introAgreeButton",
            "button.tHlp8d",
        ]
        for sel in accept_selectors:
            try:
                btn = driver.find_element("css selector", sel)
                btn.click()
                print("    [CONSENT] Accepted.")
                time.sleep(2)
                return
            except:
                continue
        # Last resort: any button with accept/agree text
        try:
            buttons = driver.find_elements("tag name", "button")
            for btn in buttons:
                txt = btn.text.lower()
                # Added French keywords: "accepter", "j'accepte", "tout accepter"
                if any(w in txt for w in ["accept", "agree", "accept all", "accepter", "j'accepte", "tout accepter"]):
                    btn.click()
                    print(f"    [CONSENT] Clicked '{btn.text}'")
                    time.sleep(2)
                    return
        except:
            pass
        print("    [CONSENT] Could not find accept button - continuing anyway.")

def append_to_csv(csv_path, continuum, query, item):
    """Appends a single result to the discovery report immediately."""
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            continuum,
            query,
            item["google_title"],
            item["real_title"],
            item["url"]
        ])

def perform_harvest(driver, query, continuum, csv_path, seen_urls):
    """Stage 1: Harvest Google Results. Stage 2: Resolve Real Titles & Append Real-Time."""
    print(f"\n--- Harvesting Query: {query} ---")
    # Added &hl=en to force English results even when rotating through non-English Tor nodes
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=en"
    driver.get(search_url)
    time.sleep(5)
    
    page = 1
    total_new = 0

    while page <= MAX_PAGES:
        print(f"  Scanning Page {page}...")
        
        # 1. Handle Google Terms/Consent
        _handle_google_consent(driver)
        
        # 2. CAPTCHA Detection - manual dialog
        if "sorry/index" in driver.current_url or "recaptcha" in driver.page_source.lower():
            print("    [CAPTCHA] Google wall detected - waiting for user action...")
            title = "WikiHow Scraper - CAPTCHA Detected"
            msg = (
                "Google CAPTCHA detected!\n\n"
                "Solve it in the browser window, then click:\n"
                "  [Yes]    - I solved it, continue scraping\n"
                "  [No]     - Rotate IP and retry automatically\n"
                "  [Cancel] - Exit the script"
            )
            # MB_YESNOCANCEL | MB_ICONWARNING | MB_SYSTEMMODAL | MB_TOPMOST
            res = ctypes.windll.user32.MessageBoxW(0, msg, title, 0x00000003 | 0x00000030 | 0x00040000 | 0x00001000)
            if res == 6:  # IDYES - user solved it
                print("    [OK] User solved CAPTCHA - retrying scan...")
                time.sleep(1)
                continue # RE-SCAN the page
            elif res == 7:  # IDNO - rotate IP
                _rotate_in_place(driver)
                return "RESTART_REQUIRED"
            else:  # IDCANCEL - exit
                print("    [EXIT] User requested termination via dialog.")
                exit(0)
            
        # 3. Harvest Results
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        found_on_page = 0
        for h3 in soup.find_all('h3'):
            link_node = h3.parent
            while link_node and link_node.name != 'a':
                link_node = link_node.parent
            
            if link_node and link_node.name == 'a':
                url = link_node.get('href')
                if url and "wikihow.com" in url:
                    if url in seen_urls:
                        continue
                        
                    google_title = h3.get_text().strip()
                    print(f"    Found: {google_title[:40]}... -> Resolving and Writing...")
                    real_title = resolve_real_title(url)
                    
                    item = {
                        "google_title": google_title,
                        "real_title": real_title,
                        "url": url
                    }
                    
                    append_to_csv(csv_path, continuum, query, item)
                    seen_urls.add(url)
                    found_on_page += 1
                    total_new += 1
        
        # Stuck Check: If Page 1 shows 0 results, it's likely a hidden block or unhandled consent
        # Trigger on any Google domain if we are stuck on Page 1 with no results
        if page == 1 and found_on_page == 0 and "google" in driver.current_url:
            print(f"    [STUCK] 0 links found on Page 1 (URL: {driver.current_url}).")
            title = "WikiHow Scraper - Potential Block"
            msg = (
                "0 articles found on Page 1. This usually means Google is blocking you or "
                "waiting for a terms acceptance.\n\n"
                "Check the browser window. If you fix it, click:\n"
                "  [Yes]    - I fixed it, retry/continue\n"
                "  [No]     - Rotate IP and retry\n"
                "  [Cancel] - Exit"
            )
            res = ctypes.windll.user32.MessageBoxW(0, msg, title, 0x00000003 | 0x00000030 | 0x00040000 | 0x00001000)
            if res == 6: # IDYES
                print("    [RETRY] Retrying current page scan...")
                continue
            elif res == 7: # IDNO
                _rotate_in_place(driver)
                return "RESTART_REQUIRED"
            elif res == 2: # IDCANCEL
                exit(0)
        
        print(f"    Extracted {found_on_page} new links on page {page}.")
        
        # Pagination
        next_btn = soup.select_one("#pnnext")
        if next_btn:
            page += 1
            try:
                driver.execute_script("arguments[0].click();", driver.find_element("css selector", "#pnnext"))
            except:
                break
            time.sleep(2)
        else:
            break
            
    return total_new

def generate_queries(category, continuum):
    """Generates a 3-pronged search strategy for a given category."""
    queries = [
        f"site:wikihow.com Category:{category}", 
        f"site:wikihow.com \"{category}\""
    ]
    if continuum == "domestic":
        queries.append(f"site:wikihow.com \"how to\" {category}")
    elif continuum == "occupational":
        queries.append(f"site:wikihow.com career in {category}")
    elif continuum == "entertainment":
        queries.append(f"site:wikihow.com {category} as a hobby")
    elif continuum == "policy":
        queries.append(f"site:wikihow.com impact of {category}")
    else:
        queries.append(f"site:wikihow.com \"{category}\" tips")
    return queries

def main():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    
    # Unified mapping file using the new Scored Dictionary structure
    mapped_file = os.path.join(DATA_DIR, "..", "mapped_spaces.json")
    with open(mapped_file, 'r', encoding='utf-8') as f:
        mapped_data = json.load(f)
        
    # Tor Status Check
    status = tor.get_status()
    print(f"\n[SYSTEM] Tor Connectivity: {status['status']}")
    if status['status'] == "CALIBRATED":
        print(f"         IP: {status['current_ip']} (Mode: {status['mode']})")
    else:
        print(f"         WARNING: Stealth Mode (Tor) is not active. Running standard session.")

    # Set to a continuum name to resume from that point, or None to process all
    START_FROM = "occupational"
    reached_start = (START_FROM is None)

    for continuum, details in mapped_data.items():
        if not reached_start:
            if continuum == START_FROM:
                reached_start = True
            else:
                print(f"[SKIP] Continuum '{continuum}' - resuming from '{START_FROM}'")
                continue

        print(f"\n==========================================")
        print(f"STARTING SWEEP: {continuum.upper()}")
        print(f"==========================================")
        
        sorted_cats = sorted(details['cats'].items(), key=lambda item: item[1])
        
        for category, score in sorted_cats:
            slug = category.replace(" ", "_").lower()
            csv_path = os.path.join(DATA_DIR, continuum, slug, "discovery_report.csv")
            
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 1000:
                print(f"[CHECKPOINT] Skipping '{category}' (Score: {score}) - already processed.")
                continue

            print(f"\nProcessing Category: {category} (Score: {score})")
            init_csv(csv_path)
            
            queries = generate_queries(category, continuum)
            seen_urls = set()

            for q in queries:
                captcha_retries = 0
                MAX_CAPTCHA_RETRIES = 3
                while True: # Retry loop for rotation/block handling
                    driver = _get_google_driver()
                    try:
                        res = perform_harvest(driver, q, continuum, csv_path, seen_urls)
                        
                        # Handle 0-result fallback
                        if res == 0:
                            print(f"    [WARN] Query '{q}' returned 0 results.")
                            title = "WikiHow Scraper - No Results"
                            msg = f"Query '{q}' returned 0 results.\n\nIs Google blocking or did you solve it?\n[Yes] Done with this query\n[No] Rotate and Retry\n[Cancel] Exit"
                            mres = ctypes.windll.user32.MessageBoxW(0, msg, title, 3 | 0x30 | 0x40000 | 0x1000)
                            if mres == 7: # No -> Rotate
                                _rotate_in_place(driver)
                                res = "RESTART_REQUIRED"
                            elif mres == 2: # Cancel
                                exit(0)

                        if res == "RESTART_REQUIRED":
                            captcha_retries += 1
                            if captcha_retries >= MAX_CAPTCHA_RETRIES:
                                print(f"  [SKIP] Query '{q[:50]}' hit block {MAX_CAPTCHA_RETRIES}x — skipping.")
                                break
                            # Driver handles rotation in-place now; just continue the while loop
                            continue 
                        
                        # Successful query: just continue to next query
                        break
                    except Exception as e:
                        print(f"  CRITICAL ERROR on query '{q}': {e}")
                        break
                
            # Category transition: Keep the driver alive
            print(f"  [DONE] Category '{category}' completed. Continuing with browser open...")
        
    print("\n[COMPLETE] Discovery finished.")
    if _google_driver:
        print("Closing persistent driver...")
        try: _google_driver.quit()
        except: pass

if __name__ == "__main__":
    main()
