"""
WikiHow API Client (Ultra-Stable "Tank" Edition)
- Browser-less resolution for Genders (to avoid system crashes)
- Bio & Real Name context preserved for accuracy
- Fully authenticated via synced Gourav 4 session
"""
import os
import json
import time
import logging
import traceback
import urllib.parse
import requests
import re
from io import BytesIO
from bs4 import BeautifulSoup
from .process_manager import logger as mgmt_logger
from .tor_manager import tor


BASE_URL = "https://www.wikihow.com/api.php"
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sessions", "browser_session")
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cached_users.json")
# Global override for research nodes
GLOBAL_PROXY_OVERRIDE = "172.31.44.95:1080"

COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "session_cookies.json")



RATE_LIMIT = 2.0
_last_request_time = 0.0
_driver = None
_persistent_driver = None
_VISION_CLASSIFIER = None
_TAB_REGISTRY = {} 
_SESSION_COOKIES = {} 
USER_CACHE = {}

# --- Cache Management ---
def _load_cache():
    global USER_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                USER_CACHE = json.load(f)
        except:
            USER_CACHE = {}

def _save_cache():
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(USER_CACHE, f, indent=4)

def load_session_cookies():
    global _SESSION_COOKIES
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r") as f:
                _SESSION_COOKIES = json.load(f)
            mgmt_logger.info(f"Loaded {len(_SESSION_COOKIES)} cookies from file.")
        except:
            _SESSION_COOKIES = {}

def save_session_cookies():
    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
    with open(COOKIE_FILE, "w") as f:
        json.dump(_SESSION_COOKIES, f, indent=4)

_load_cache()
load_session_cookies()


# --- Browser Management (For Initial Mapping Only) ---
from .tor_manager import tor

# --- Browser Management (For Initial Mapping Only) ---
def _get_driver(proxy=None, forced_headless=None):
    global _driver
    if _driver is None:
        from seleniumbase import Driver
        try:
            profile_dir = USER_DATA_DIR
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            
            # Default to Headless for extraction, unless forced otherwise (for login)
            is_headless = True
            if forced_headless is not None:
                is_headless = forced_headless
                
            mode_str = "HEADLESS" if is_headless else "HEADED"
            print(f"Initializing Tank Driver ({mode_str} UC MODE, Profile: {os.path.basename(profile_dir)})...")
            
            # Use global override, then provided proxy, else None
            final_proxy = GLOBAL_PROXY_OVERRIDE or proxy 
            if final_proxy:
                print(f"  [NETWORK] Routing via Proxy: {final_proxy}")
            else:
                print("  [NETWORK] Direct Connection (No Proxy)")

                
            # Running with dynamic headless setting.
            _driver = Driver(uc=True, headless=is_headless, user_data_dir=profile_dir, agent=ua, proxy=final_proxy)
            mgmt_logger.info(f"Search Engine Started ({mode_str} UC MODE).")
            print(f"  {mode_str.capitalize()} Stealth Tank Driver Ready.")
            
        except Exception as e:
            mgmt_logger.error(f"Failed to launch browser: {e}")
            print(f"  CRITICAL: Browser Launch Failed: {e}")
    return _driver

def sync_browser_cookies():
    global _driver, _SESSION_COOKIES
    if _driver:
        try:
            print("Syncing session cookies...")
            if "wikihow.com" not in _driver.current_url:
                _driver.get("https://www.wikihow.com/Main-Page")
            raw_cookies = _driver.get_cookies()
            _SESSION_COOKIES = {c['name']: c['value'] for c in raw_cookies}
            save_session_cookies()
            mgmt_logger.info(f"Session Synced: {len(_SESSION_COOKIES)} cookies captured and saved.")
            print(f"  SUCCESS: {len(_SESSION_COOKIES)} session cookies captured.")

        except Exception as e:
            print(f"  Cookie Sync Warning: {e}")

# --- Core Scrapers (Browser-Less for Stability) ---



def get_article_details(title: str) -> dict:
    """Fetch co-authors list and expert info using Static Requests."""
    global _SESSION_COOKIES
    slug = title.replace(" ", "_")
    url = f"https://www.wikihow.com/{slug}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        mgmt_logger.info(f"Scraping Article Details: {slug}")
        r = requests.get(url, headers=headers, cookies=_SESSION_COOKIES, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        details = {
            "co_authors": [],
            "expert": None,
            "expert_title": None,
            "stats": {}
        }
        
        # Co-authors from "About This Article" or Byline
        # Try different possible selectors for co-authors
        co_author_links = soup.select("a.sp_namelink, a.coauthor_link")
        details["co_authors"] = list(set([a.get_text().strip() for a in co_author_links]))
        
        # Expert check - looks for various indicators
        # Often has .coauthor_checkstar or is inside .sp_expert
        expert_link = soup.select_one("a.coauthor_checkstar, .sp_expert a.sp_namelink")
        if expert_link:
            details["expert"] = expert_link.get_text().strip()
            # Try to find professional title (often in sibling or parent)
            parent = expert_link.find_parent(["div", "li", "span"])
            if parent:
                # Look for blurb or title text
                blurb = parent.select_one(".sp_expert_blurb, .coauthor_title")
                if blurb:
                    details["expert_title"] = blurb.get_text().strip()
                else:
                    text = parent.get_text()
                    match = re.search(r",\s*([^,.\n]*)", text)
                    if match: details["expert_title"] = match.group(1).strip()


        # Stats
        stats_list = soup.select(".footer_stats li")
        for s in stats_list:
            text = s.get_text().strip()
            if "Updated" in text: details["stats"]["last_updated"] = text.replace("Updated:", "").strip()
            if "Views" in text: details["stats"]["views"] = text.replace("Views:", "").strip().replace(",", "")
            
        return details
    except Exception as e:
        mgmt_logger.error(f"Article details fetch failed: {e}")
        return {}

def get_talk_page(title: str) -> list[dict]:
    """Fetch Talk or Discussion page threads."""
    global _SESSION_COOKIES
    slug = title.replace(" ", "_").replace("?", "%3F")
    
    # Try Discussion: first as it is the modern standard
    url = f"https://www.wikihow.com/Discussion:{slug}"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        mgmt_logger.info(f"Scraping Discussion Page: {slug}")
        r = requests.get(url, headers=headers, cookies=_SESSION_COOKIES, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        threads = []
        
        # Check for .discuss_post (Modern Layout)
        posts = soup.select(".discuss_post")
        if posts:
            for p in posts:
                author_link = p.select_one('a[href*="/User:"]')
                author = author_link.get_text().strip() if author_link else "Unknown"
                # Comment body usually inside a specific div or just the text of the post
                body = p.get_text().strip()
                # Clean up body (remove author name and "said:")
                if author in body:
                    body = body.split("said:", 1)[-1].strip()
                threads.append({"author": author, "text": body})
        
        # Fallback to MediaWiki Talk (Classic Layout)
        if not threads:
            url = f"https://www.wikihow.com/index.php?title=Talk:{slug}"
            r = requests.get(url, headers=headers, cookies=_SESSION_COOKIES, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            headers_tags = soup.select("#bodyContent h2")
            for h in headers_tags:
                topic = h.get_text().strip()
                comments = []
                curr = h.find_next_sibling()
                while curr and curr.name != "h2":
                    if curr.name in ["p", "dl", "ul"]:
                        text = curr.get_text().strip()
                        author_link = curr.select_one('a[href*="/User:"]')
                        author = author_link.get_text().strip() if author_link else "Unknown"
                        if text:
                            comments.append({"author": author, "text": text})
                    curr = curr.find_next_sibling()
                threads.append({"topic": topic, "comments": comments})
                
        return threads
    except Exception as e:
        mgmt_logger.error(f"Talk/Discussion page fetch failed: {e}")
        return []



def get_users(usernames: list, fallback_to_profile: bool = True) -> dict:
    """Fetch user gender info using Static Requests + Bio/Name Context."""
    global USER_CACHE, _SESSION_COOKIES
    results = {}
    to_resolve = []
    
    for u in usernames:
        if u in USER_CACHE: results[u] = USER_CACHE[u]
        else: to_resolve.append(u)
            
    if not to_resolve: return results
    
    headers = {"User-Agent": "Mozilla/5.0"}
    for u in to_resolve:
        profile_url = f"https://www.wikihow.com/User:{u.replace(' ', '_')}"
        info = {"username": u, "gender": "unknown", "real_name": "unknown", "bio": "", "source": "none"}
        
        try:
            # STATIC PROFILE FETCH
            r = requests.get(profile_url, headers=headers, cookies=_SESSION_COOKIES, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                
                # --- [RESTORED] Real Name Context ---
                header = soup.select_one("#hp_top_right")
                if header:
                    rows = header.select("p.hp_top_row")
                    if rows:
                        b_tags = rows[0].find_all("b")
                        if len(b_tags) >= 1: info["real_name"] = b_tags[0].get_text().strip()
                
                # --- [RESTORED] Bio Context ---
                bio_elem = soup.select_one("#bodyContent")
                if bio_elem: info["bio"] = bio_elem.get_text().strip()[:1000]

                # --- Resolve Gender (Genderize on Real Name) ---
                name_to_check = info["real_name"] if info["real_name"] != "unknown" else u
                first_name = name_to_check.split()[0]
                
                # Generic/Bot check
                if first_name.lower() in ("wikihow", "miscbot", "votebot"):
                    info["gender"] = "unknown"
                else:
                    g_res = requests.get(f"https://api.genderize.io?name={first_name}", timeout=5)
                    if g_res.status_code == 200:
                        g_data = g_res.json()
                        info["gender"] = g_data.get("gender", "unknown")
                        info["source"] = "genderize"
                
                results[u] = info
                USER_CACHE[u] = info
                mgmt_logger.info(f"Resolved {u} (Static) -> {info['gender']}")
        except:
            results[u] = info
            
    _save_cache()
    return results

def scrape_search_results(query: str, limit: int = 50) -> list[dict]:
    driver = _get_driver()
    url = f"https://www.wikihow.com/wikiHowTo?search={urllib.parse.quote(query)}"
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = []
        for link in soup.select("a.result_link"):
            results.append({"title": link.get_text().strip(), "url": link.get("href", ""), "ns": 0})
            if len(results) >= limit: break
        return results
    except: return []

def get_category_members(category: str, limit: int = 100) -> list[dict]:
    return scrape_search_results(category, limit=limit)

def get_browser_tab(purpose: str):
    # Dummy to maintain compatibility with calling scripts
    return _get_driver()

def get_revision_diff(rev_id: str) -> dict:
    """Fetch the added/removed text for a specific revision using Parallel Requests + Proxy with Retry logic."""
    global _SESSION_COOKIES
    url = f"https://www.wikihow.com/api.php?action=compare&torelative=prev&fromrev={rev_id}&format=json"
    
    # Proxy Injection
    p_string = GLOBAL_PROXY_OVERRIDE or proxy
    if p_string:
        proxies = {
            "http": f"http://{p_string}",
            "https": f"http://{p_string}"
        }
    else:
        proxies = None
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random jitter to prevent synchronized spikes
            time.sleep(1 + (attempt * 2)) 
            
            r = requests.get(url, headers=headers, cookies=_SESSION_COOKIES, proxies=proxies, timeout=25)
            
            # Block detection
            if r.status_code == 429 or "Temporarily Unavailable" in r.text or "Too many requests" in r.text:
                return {"added": ["BLOCK_DETECTED"], "removed": []}
                
            data = r.json()
            if "compare" in data and "*" in data["compare"]:
                diff_html = data["compare"]["*"]
                soup = BeautifulSoup(diff_html, "html.parser")
                added = [td.get_text().strip() for td in soup.select(".diff-addedline")]
                removed = [td.get_text().strip() for td in soup.select(".diff-deletedline")]
                
                # VALIDATION: If both are empty, it might be a silent failure or a null edit.
                # In our context (1400+ empty), it's likely a failure. We return None to trigger retry.
                if not added and not removed:
                    mgmt_logger.warning(f"  [EMPTY DIFF] Rev {rev_id} returned no lines. Retrying...")
                    continue
                    
                return {"added": added, "removed": removed}
            
            # If we get JSON but no compare key, it might be an error (e.g. rev deleted)
            if "error" in data:
                mgmt_logger.warning(f"  [API ERROR] Rev {rev_id}: {data['error'].get('info')}")
                continue

        except (requests.exceptions.SSLError, requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            mgmt_logger.warning(f"  [PROXY JITTER] Attempt {attempt+1}/{max_retries} failed for rev {rev_id}: {e}")
            continue
        except Exception as e:
            mgmt_logger.error(f"  [UNEXPECTED FAIL] Rev {rev_id}: {e}")
            break
            
    # If we get here, all retries failed
    return None # Return None to signal a failure to the extractor


def ask_deepseek(prompt: str, file_path: str = None) -> str:
    """
    Sends a prompt (and optional file) to the local DeepSeek Bridge.
    Bridge must be running (python deepseek/bridge.py)
    """
    BRIDGE_URL = "http://127.0.0.1:8002/ask"
    try:
        mgmt_logger.info(f"Relaying prompt to DeepSeek Bridge: {prompt[:50]}...")
        payload = {"prompt": prompt}
        if file_path:
            payload["file_path"] = os.path.abspath(file_path)
            
        r = requests.post(BRIDGE_URL, json=payload, timeout=600)
        if r.status_code == 200:
            return r.json().get("response", "ERROR: Empty response from bridge")
        else:
            return f"BRIDGE_HTTP_ERROR: {r.status_code} - {r.text}"
    except Exception as e:
        mgmt_logger.error(f"DeepSeek Bridge connection failed: {e}")
        return f"BRIDGE_CONNECTION_FAILED: {e}"


def get_revisions(title_slug, limit=500):
    driver = _get_driver()
    all_revisions = []
    
    # If limit is 0 or None, we fetch EVERYTHING
    infinite = (limit is None or limit == 0)
    
    # We use the BROWSER for the main history list to ensure JS/Wait/Cookies are handled perfectly.
    url = f"https://www.wikihow.com/index.php?title={title_slug}&action=history&limit=500"
    
    try:
        while infinite or len(all_revisions) < limit:
            curr_limit_str = "Infinity" if infinite else limit
            mgmt_logger.info(f"    [SCRAPE] Fetching history (Browser): {title_slug} (Total: {len(all_revisions)} / {curr_limit_str})")
            
            # POLITE PROTOCOL: Mandatory delay
            time.sleep(3)
            
            driver.get(url)
            time.sleep(2) # Additional JS wait
            
            # Block Detection
            if "Temporarily Unavailable" in driver.page_source or "Too many requests" in driver.page_source:
                print("\n[!!!] BROWSER BLOCK DETECTED. WikiHow has throttled this IP.")
                mgmt_logger.error("Browser Blocked: Too Many Requests.")
                break
                
            soup = BeautifulSoup(driver.page_source, "html.parser")

            history_list = soup.select("#pagehistory li")
            
            if not history_list:
                # Try one fallback: Friendly URL action=history
                if len(all_revisions) == 0:
                   mgmt_logger.info("    [FALLBACK] Trying friendly URL pattern...")
                   driver.get(f"https://www.wikihow.com/{title_slug}?action=history")
                   time.sleep(4)
                   soup = BeautifulSoup(driver.page_source, "html.parser")
                   history_list = soup.select("#pagehistory li")
            
            if not history_list:
                break
                
            for li in history_list:
                if not infinite and len(all_revisions) >= limit:
                    break
                    
                rev_id = li.get("data-mw-revid")
                user_link = li.select_one(".mw-userlink")
                timestamp_link = li.select_one(".mw-changeslist-date")
                size_span = li.select_one(".history-size")
                change_span = li.select_one(".mw-plusminus-pos, .mw-plusminus-neg, .mw-plusminus-null")
                summary_span = li.select_one(".comment")
                minor_span = li.select_one(".minoredit")
                
                rev_data = {
                    "id": rev_id,
                    "user": user_link.text if user_link else "Unknown",
                    "timestamp": timestamp_link.text if timestamp_link else "",
                    "anon": "mw-anonuserlink" in (user_link.get("class", []) if user_link else []),
                    "size": size_span.text if size_span else "",
                    "change": 0,
                    "summary": summary_span.text if summary_span else "",
                    "is_minor": minor_span is not None
                }
                
                if change_span:
                    try:
                        rev_data["change"] = int(re.sub(r"[^\d\-]", "", change_span.text))
                    except: pass
                    
                all_revisions.append(rev_data)
            
            # Check for pagination (mw-nextlink)
            next_link = soup.select_one(".mw-nextlink")
            if next_link and next_link.get("href"):
                if infinite or len(all_revisions) < limit:
                    url = "https://www.wikihow.com" + next_link.get("href")
                else: break
            else:
                break
                
        mgmt_logger.info(f"Scraped {len(all_revisions)} revisions for {title_slug}")
        return all_revisions
        
    except Exception as e:
        mgmt_logger.error(f"Error scraping history: {e}")
        return all_revisions




