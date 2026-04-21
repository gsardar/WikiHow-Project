# -*- coding: utf-8 -*-
import sys, io, re, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
filter_test_v2.py
=================
Tests the Lexical Bounding Filter with expanded keywords and corrected category names.
"""

# Map internal keys to actual WikiHow category names and robust keywords
DOMESTIC_MAP = {
    "Babies and Infants": {
        "cat": "Babies and Infants",
        "kw": ["baby", "babies", "infant", "newborn", "diaper", "nursery", "bottle", "crawl", "stroller", "toddler", "crib", "child", "kid", "parent", "pregnancy", "prenatal", "breastfeeding", "birth", "pacifier", "teething"]
    },
    "Baking": {
        "cat": "Baking",
        "kw": ["bake", "baking", "cake", "bread", "cookie", "oven", "flour", "dough", "yeast", "pastry", "muffin", "pie", "knead", "whisk", "sugar", "chocolate", "frosting", "cupcake", "brownie", "doughnut"]
    },
    "Home Decorating": {
        "cat": "Home Decorating",
        "kw": ["decorate", "decoration", "furniture", "room", "wallpaper", "curtain", "rug", "interior", "pillow", "shelf", "paint", "accent", "lighting", "frame", "hanging", "art", "carpet", "mirror", "vase", "blind"]
    },
    "Laundry": {
        "cat": "Laundry",
        "kw": ["laundry", "wash", "dry", "clothes", "stain", "detergent", "fabric", "iron", "bleach", "fold", "hamper", "machine", "linen", "silk", "wool", "wrinkle", "dryer", "washer", "sock", "lint"]
    },
    "Gardening": {
        "cat": "Gardening",
        "kw": ["garden", "gardening", "plant", "soil", "grow", "flower", "vegetable", "seed", "weed", "lawn", "prune", "sprinkler", "mulch", "fertilizer", "tree", "shrub", "herb", "grass", "mow", "rose"]
    },
    "Personal Finance": {
        "cat": "Finance and Business",
        "kw": ["money", "budget", "save", "invest", "debt", "credit", "bank", "tax", "retirement", "expense", "loan", "mortgage", "cash", "income", "wallet", "card", "billing", "check", "stock", "interest"]
    },
    "Home Improvements": {
        "cat": "Home Improvements",
        "kw": ["repair", "install", "renovate", "renovation", "build", "wall", "floor", "door", "window", "roof", "tile", "siding", "gutter", "deck", "patio", "fence", "attic", "stairs", "drywall", "insulation"]
    },
    "Appliance Repair": {
        "cat": "Home Appliances",
        "kw": ["repair", "fix", "washer", "dryer", "fridge", "refrigerator", "microwave", "oven", "dishwasher", "stove", "vacuum", "freezer", "toaster", "blender", "kettle", "heater", "cool", "appliance"]
    },
    "Plumbing": {
        "cat": "Plumbing",
        "kw": ["pipe", "leak", "faucet", "drain", "toilet", "clog", "plumb", "plumbing", "sink", "shower", "water", "hose", "septic", "heater", "valve", "trap", "sump", "p-trap", "tank"]
    },
    "Electrical Wiring": {
        "cat": "Electrical Wiring and Safety Switches",
        "kw": ["wire", "wiring", "outlet", "switch", "circuit", "light", "electrical", "breaker", "cord", "voltage", "fuse", "bulb", "terminal", "cable", "fixture", "ground", "panel", "spark"]
    },
}

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "WikiHowGenderResearch/1.0 (filter-test-v2)"

def get_articles(category, limit=50):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": limit,
        "cmtype": "page",
        "format": "json"
    }
    r = requests.get(BASE_URL, params=params, headers={"User-Agent": USER_AGENT})
    return r.json().get("query", {}).get("categorymembers", [])

def passes_filter(title, keywords):
    t = title.lower()
    for kw in keywords:
        if kw in t:
            return True
    return False

print("=" * 90)
print(f"{'Key':<20} | {'Cat Name':<28} | {'Total':>5} | {'Passed':>6} | {'% Kept':>7}")
print("-" * 90)

total_before = 0
total_after = 0

for key, data in DOMESTIC_MAP.items():
    articles = get_articles(data["cat"])
    before = len(articles)
    passed = [a for a in articles if passes_filter(a["title"], data["kw"])]
    after = len(passed)
    
    total_before += before
    total_after += after
    
    perc = (after / before * 100) if before > 0 else 0
    print(f"{key:<20} | {data['cat'][:28]:<28} | {before:>5} | {after:>6} | {perc:>6.1f}%")
    
    if before > after:
        dropped = [a["title"] for a in articles if a not in passed][:3]
        print(f"  Dropped: {', '.join(dropped)}")

print("-" * 90)
final_perc = (total_after / total_before * 100) if total_before > 0 else 0
print(f"{'TOTAL':<20} | {'':<28} | {total_before:>5} | {total_after:>6} | {final_perc:>6.1f}%")
print("=" * 90)
