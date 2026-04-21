# -*- coding: utf-8 -*-
import sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE_URL = "https://www.wikihow.com/api.php"

for cat in ["Laundry", "Personal Finance", "Money Management", "Appliances"]:
    params = {"action": "query", "titles": f"Category:{cat}", "format": "json"}
    r = requests.get(BASE_URL, params=params)
    exists = "-1" not in r.json().get("query", {}).get("pages", {})
    print(f"Category:{cat} exists: {exists}")
