# -*- coding: utf-8 -*-
import sys, io, re, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
list_cats.py
============
Searches for the correct names of the 4 missing categories on WikiHow.
"""

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "WikiHowGenderResearch/1.0 (cat-search)"

SEARCH_TERMS = [
    "Personal Finance",
    "Home Improvement",
    "Appliance Repair",
    "Electrical Wiring"
]

def search_category(term):
    params = {
        "action": "query",
        "list": "allcategories",
        "acprefix": term,
        "aclimit": 10,
        "format": "json"
    }
    r = requests.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT})
    return r.json().get("query", {}).get("allcategories", [])

for term in SEARCH_TERMS:
    print(f"\nSearching for '{term}':")
    results = search_category(term)
    for res in results:
        print(f"  - {res['*']}")
