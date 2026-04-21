
import requests
import json
import sys
from bs4 import BeautifulSoup

rev_id = sys.argv[1] if len(sys.argv) > 1 else "31106"
url = f"https://www.wikihow.com/api.php?action=compare&torelative=prev&fromrev={rev_id}&format=json"
proxies = {
    "http": "http://172.31.92.239:65482",
    "https": "http://172.31.92.239:65482"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

print(f"Fetching diff for {rev_id}...")
r = requests.get(url, headers=headers, proxies=proxies, timeout=25)
print(f"Status: {r.status_code}")
data = r.json()
if "compare" in data and "*" in data["compare"]:
    diff_html = data["compare"]["*"]
    soup = BeautifulSoup(diff_html, "html.parser")
    added = [td.get_text().strip() for td in soup.select(".diff-addedline")]
    removed = [td.get_text().strip() for td in soup.select(".diff-deletedline")]
    print(f"Added: {len(added)}")
    print(f"Removed: {len(removed)}")
    if added: print(f"Sample Added: {added[0][:100]}...")
else:
    print("No compare key or * tag found.")
    print(json.dumps(data, indent=2))
