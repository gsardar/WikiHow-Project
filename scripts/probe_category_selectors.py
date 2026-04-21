import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

# Test pagination via 'start' parameter (standard MediaWiki pattern)
base = "https://www.wikihow.com/wikiHowTo?search=Accounting+and+Finance&type=category"

all_urls = set()
for start in range(0, 45, 15):
    url = f"{base}&start={start}" if start > 0 else base
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a.result_link")
    hrefs = [a.get("href","") for a in links if a.get("href","")]
    new = [h for h in hrefs if h not in all_urls]
    all_urls.update(hrefs)
    print(f"start={start:3d} -> {len(links)} links, {len(new)} new | HTTP {r.status_code}")
    if not links:
        break

print(f"\nTotal unique articles found: {len(all_urls)}")
for u in sorted(all_urls)[:5]:
    print(f"  {u}")
