import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Configuration for Semantic Expansion
EXPANSION_CONFIG = {
    "domestic": {
        "seeds": ["Category:Gardening", "Category:Baking", "Category:Laundry", "Category:Baby Care"],
        "exclude": ["Professional", "Commercial", "Industrial", "Career", "Business"]
    },
    "occupational": {
        "seeds": ["Category:Software Engineering", "Category:Mechanical Engineering", "Category:Nursing", "Category:Business Management"],
        "exclude": ["Hobby", "Personal", "Family"]
    },
    "entertainment": {
        "seeds": ["Category:Knitting", "Category:Photography", "Category:DIY", "Category:PC Gaming"],
        "exclude": ["Professional", "Commercial"]
    },
    "policy": {
        "seeds": ["Category:Law Enforcement", "Category:Foreign Policy", "Category:Public Policy"],
        "exclude": ["Personal", "Opinion"]
    }
}

def get_related_topics(seed_page, session, depth=1):
    """
    Uses the 'parse' API loophole to find related categories and sub-topics.
    """
    print(f"  Expanding Seed: {seed_page}...")
    params = {
        "action": "parse",
        "page": seed_page,
        "prop": "categories|links",
        "format": "json"
    }
    
    related = set()
    try:
        resp = session.get(BASE_URL, params=params, timeout=10)
        data = resp.json().get("parse", {})
        
        # 1. Look for linked categories (Subcategories)
        links = data.get("links", [])
        for l in links:
            if l.get("ns") == 14: # Category Namespace
                cat_name = l.get("*", "")
                if cat_name:
                    related.add(f"Category:{cat_name}")
        
        # 2. Look for assigned categories (Related)
        categories = data.get("categories", [])
        for c in categories:
            cat_name = c.get("*", "")
            if cat_name:
                related.add(f"Category:{cat_name}")
                
    except Exception as e:
        print(f"    Expansion Error for {seed_page}: {e}")
        
    return list(related)

def run_discovery_loop(continuum_key):
    config = EXPANSION_CONFIG.get(continuum_key)
    if not config: return []
    
    discovered_cats = set()
    all_seeds = config["seeds"]
    
    print(f"\n--- Starting Discovery Loop for {continuum_key.upper()} ---")
    
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        
        for seed in all_seeds:
            discovered_cats.add(seed)
            # One level of recursion to find siblings/children
            related = get_related_topics(seed, session)
            for r in related:
                # Semantic Filter: Exclude keywords from the 'exclude' list
                if any(excl.lower() in r.lower() for excl in config["exclude"]):
                    print(f"    [FILTERED] {r} (Excluded keyword found)")
                    continue
                discovered_cats.add(r)
                
    return [c.replace("Category:", "") for c in discovered_cats]

def main():
    final_mapping = {}
    for key in EXPANSION_CONFIG.keys():
        expanded_set = run_discovery_loop(key)
        final_mapping[key] = {
            "title": key.capitalize() + " Continuum (Expanded)",
            "cats": expanded_set
        }
        print(f"Discovery Complete for {key}: Found {len(expanded_set)} categories.")

    with open('data/mapped_spaces_expanded.json', 'w') as f:
        json.dump(final_mapping, f, indent=2)
    print("\nSUCCESS: Expanded mapping saved to 'data/mapped_spaces_expanded.json'")

if __name__ == "__main__":
    main()
