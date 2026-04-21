# -*- coding: utf-8 -*-
import sys, io, re, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
filter_test.py
==============
Tests the Lexical Bounding Filter by listing articles in 10 categories
and checking how many pass the keyword filter.
"""

# Define keywords for Domestic Continuum
KEYWORDS = {
    "Babies and Infants": ["baby", "babies", "infant", "newborn", "diaper", "nursery", "bottle", "crawl", "stroller", "toddler"],
    "Baking": ["bake", "baking", "cake", "bread", "cookie", "oven", "flour", "dough", "yeast", "pastry", "muffin", "pie"],
    "Home Decor": ["decorate", "decoration", "furniture", "room", "wallpaper", "curtain", "rug", "interior", "pillow", "shelf", "paint"],
    "Laundry": ["laundry", "wash", "dry", "clothes", "stain", "detergent", "fabric", "iron", "bleach", "fold"],
    "Gardening": ["garden", "gardening", "plant", "soil", "grow", "flower", "vegetable", "seed", "weed", "lawn", "prune"],
    "Personal Finance": ["money", "budget", "save", "invest", "debt", "credit", "bank", "tax", "retirement", "expense", "loan", "mortgage"],
    "Home Improvement": ["repair", "install", "renovate", "renovation", "build", "wall", "floor", "door", "window", "roof", "tile"],
    "Appliance Repair": ["repair", "fix", "washer", "dryer", "fridge", "refrigerator", "microwave", "oven", "dishwasher", "stove", "vacuum"],
    "Plumbing": ["pipe", "leak", "faucet", "drain", "toilet", "clog", "plumb", "plumbing", "sink", "shower", "water"],
    "Electrical Wiring": ["wire", "wiring", "outlet", "switch", "circuit", "light", "electrical", "breaker", "cord", "voltage", "fuse"],
}

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "WikiHowGenderResearch/1.0 (filter-test)"

def get_articles(category, limit=50):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": limit,
        "cmtype": "page",
        "format": "json"
    }
    try:
        r = requests.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        r.raise_for_status()
        return r.json().get("query", {}).get("categorymembers", [])
    except Exception as e:
        print(f"Error fetching {category}: {e}")
        return []

def passes_filter(title, keywords):
    t = title.lower()
    for kw in keywords:
        if kw in t:
            return True
    return False

print("=" * 80)
print(f"{'Category':<25} | {'Total':>5} | {'Passed':>6} | {'Filtered':>8} | {'% Kept':>7}")
print("-" * 80)

total_before = 0
total_after = 0

for cat, kws in KEYWORDS.items():
    articles = get_articles(cat)
    before = len(articles)
    passed = [a for a in articles if passes_filter(a["title"], kws)]
    after = len(passed)
    
    total_before += before
    total_after += after
    
    perc = (after / before * 100) if before > 0 else 0
    filtered = before - after
    
    print(f"{cat:<25} | {before:>5} | {after:>6} | {filtered:>8} | {perc:>6.1f}%")
    
    # Show examples of filtered out articles if any
    if filtered > 0:
        dropped = [a["title"] for a in articles if a not in passed][:3]
        print(f"  Dropped: {', '.join(dropped)}")

print("-" * 80)
final_perc = (total_after / total_before * 100) if total_before > 0 else 0
print(f"{'TOTAL':<25} | {total_before:>5} | {total_after:>6} | {total_before - total_after:>8} | {final_perc:>6.1f}%")
print("=" * 80)
