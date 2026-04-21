# -*- coding: utf-8 -*-
import sys, io, re, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
cat_finder.py
=============
Broader category search for the missing pieces.
"""

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "WikiHowGenderResearch/1.0 (cat-finder)"

SEARCH_TERMS = ["Personal Finance", "Appliance Repair", "Finance", "Appliances"]

for term in SEARCH_TERMS:
    print(f"\nSearching for '{term}':")
    params = {
        "action": "query",
        "list": "allcategories",
        "acprefix": term,
        "aclimit": 20,
        "format": "json"
    }
    r = requests.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT})
    results = r.json().get("query", {}).get("allcategories", [])
    for res in results:
        print(f"  - {res['*']}")

print("\n--- Listing members of high-level categories ---")
# Let's check "Category:Home and Garden" or "Category:Home Maintenance"
for cat in ["Home and Garden", "Home Maintenance", "Personal Finance"]:
    print(f"\nSub-categories of '{cat}':")
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{cat}",
        "cmtype": "subcat",
        "cmlimit": 50,
        "format": "json"
    }
    r = requests.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT})
    results = r.json().get("query", {}).get("categorymembers", [])
    for res in results:
        print(f"  - {res['title']}")
