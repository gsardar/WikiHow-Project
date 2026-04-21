"""
WikiHow Direct Category Crawler
================================
Replaces Google scraping for the discovery phase.
Uses WikiHow's own search endpoint — no Google, no CAPTCHA, no browser.

NOTE: google_discovery_v2.py is preserved untouched for the DeepSeek phase.
Output CSV format is identical so all downstream tools work unchanged.
"""

import os
import csv
import json
import time
import requests
from bs4 import BeautifulSoup
from wikihow.tor_manager import tor

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_DIR    = os.path.join(BASE_DIR, "data", "discovery")
MAPPED_FILE = os.path.join(BASE_DIR, "data", "mapped_spaces.json")

# ── Settings ──────────────────────────────────────────────────────────────────
START_FROM       = "occupational"  # Set to None to process all continuums
PAGE_SIZE        = 15              # WikiHow returns 15 results per page
DELAY            = 1.0             # Seconds between page requests
CHECKPOINT_BYTES = 1000            # Skip CSVs already > this size (already done)
MAX_EMPTY_PAGES  = 2               # Stop pagination after N consecutive empty pages

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


def _apply_proxy():
    proxies = tor.get_requests_proxies()
    if proxies:
        session.proxies.update(proxies)
        print(f"  [TOR] Routing via {proxies['https']}")
    else:
        print("  [DIRECT] Tor not active — using direct connection")


def _fetch_page(category: str, start: int) -> list[dict]:
    """Fetch one page of WikiHow search results for a category."""
    query = category.replace("_", "+").replace(" ", "+")
    url = f"https://www.wikihow.com/wikiHowTo?search={query}&type=category"
    if start > 0:
        url += f"&start={start}"

    try:
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            print(f"    [HTTP {r.status_code}]")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for a in soup.select("a.result_link"):
            href  = a.get("href", "")
            title = a.get_text(strip=True)
            # Strip view counts & metadata jammed into text
            # e.g. "How to File Taxes295,470 viewsUpdated..."
            import re
            title = re.sub(r"\s*\d[\d,]*\s*views.*", "", title).strip()
            if href and title and "/Category:" not in href:
                results.append({"title": title, "url": href})
        return results
    except Exception as e:
        print(f"    [ERROR] {e}")
        return []


def init_csv(csv_path: str):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Continuum", "Query", "Google Title", "Real WikiHow Title", "URL"])


def append_to_csv(csv_path: str, continuum: str, category: str, article: dict):
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([continuum, category, article["title"], article["title"], article["url"]])


def harvest_category(continuum: str, category: str, csv_path: str) -> int:
    seen        = set()
    total       = 0
    start       = 0
    empty_pages = 0

    print(f"\n  Querying: wikihow.com/wikiHowTo?search={category}&type=category")

    while True:
        page_num = (start // PAGE_SIZE) + 1
        print(f"    Page {page_num} (start={start})...", end=" ", flush=True)

        articles = _fetch_page(category, start)
        new_count = 0
        for art in articles:
            if art["url"] not in seen:
                seen.add(art["url"])
                append_to_csv(csv_path, continuum, category, art)
                new_count += 1
                total     += 1

        print(f"{new_count} new articles  (running total: {total})")

        if new_count == 0:
            empty_pages += 1
            if empty_pages >= MAX_EMPTY_PAGES:
                print(f"    → {MAX_EMPTY_PAGES} consecutive empty pages — stopping.")
                break
        else:
            empty_pages = 0

        if len(articles) < PAGE_SIZE:
            break  # Last page (fewer results than page size)

        start += PAGE_SIZE
        time.sleep(DELAY)

    return total


def main():
    print("=" * 58)
    print("  WikiHow Direct Category Crawler  (Google-free)")
    print("=" * 58)

    _apply_proxy()

    with open(MAPPED_FILE, "r", encoding="utf-8") as f:
        mapped_data = json.load(f)

    reached_start = (START_FROM is None)
    grand_total   = 0

    for continuum, details in mapped_data.items():
        if not reached_start:
            if continuum == START_FROM:
                reached_start = True
            else:
                print(f"[SKIP] '{continuum}'")
                continue

        print(f"\n{'='*58}")
        print(f"  CONTINUUM: {continuum.upper()}")
        print(f"{'='*58}")

        sorted_cats = sorted(details["cats"].items(), key=lambda x: x[1])

        for category, score in sorted_cats:
            slug     = category.replace(" ", "_").lower()
            csv_path = os.path.join(DATA_DIR, continuum, slug, "discovery_report.csv")

            if os.path.exists(csv_path) and os.path.getsize(csv_path) > CHECKPOINT_BYTES:
                existing = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1
                print(f"[CHECKPOINT] '{category}' — {existing} articles already. Skipping.")
                continue

            print(f"\n[Score:{score}] {category}")
            init_csv(csv_path)
            count = harvest_category(continuum, category, csv_path)
            grand_total += count
            print(f"  → Wrote {count} articles for '{category}'")
            time.sleep(DELAY)

    print(f"\n{'='*58}")
    print(f"  COMPLETE — Total new articles written: {grand_total}")
    print(f"{'='*58}")


if __name__ == "__main__":
    main()
