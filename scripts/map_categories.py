import requests
import json

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

spaces = {
    "domestic": {
        "title": "Domestic & Household Management Continuum",
        "kws": ["Baby Care", "Elder Care", "Interior Decoration", "Baking", "Laundry", "Household Finances", "Gardening", "Assembling Furniture", "Appliance Repair", "Plumbing"]
    },
    "occupational": {
        "title": "Occupational & Professional Fields Continuum",
        "kws": ["Early Childhood Education", "Nursing", "Social Work", "Human Resources", "Arts", "Business Management", "Physics", "Software Engineering", "Mechanical Engineering", "Construction", "Machinery"]
    },
    "entertainment": {
        "title": "Entertainment & Leisure Continuum",
        "kws": ["Knitting", "Dancing", "Poetry", "Social Media", "Photography", "Sports", "Board Games", "PC Gaming", "Game Development", "Hacking", "DIY"]
    },
    "policy": {
        "title": "Public Policy & Governance Continuum",
        "kws": ["Maternal Health", "Education Policy", "Welfare", "Sanitation", "Urban Planning", "Taxation", "Foreign Policy", "Law Enforcement", "Military Strategy", "Geopolitics", "Policy"]
    }
}

def fuzzy_match(kw, cats):
    # Try exact match first
    for c in cats:
        if kw.lower() == c.lower():
            return c
            
    # Try exact match with simple variations
    for c in cats:
        if kw.lower() + "s" == c.lower() or kw.lower() == c.lower() + "s":
            return c
            
    # Try contains
    matches = [c for c in cats if kw.lower() in c.lower()]
    if matches:
        return sorted(matches, key=len)[0]
        
    return None

def fetch_category_matches(kw, session):
    print(f"Scraping for categories related to '{kw}'...")
    # Try direct category page first
    url = f"https://www.wikihow.com/Category:{kw.replace(' ', '-')}"
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"  Found direct match for '{kw}'")
            return [kw]
        
        # Fallback to search page
        search_url = f"https://www.wikihow.com/Special:Search"
        params = {
            "search": f"Category:{kw}",
            "fulltext": "1",
            "ns14": "1" # Category namespace
        }
        resp = session.get(search_url, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"  Scraping Error: Status {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        # WikiHow search results for categories
        results = soup.select('ul.mw-search-results li a')
        matches = []
        for r in results:
            title = r.get_text()
            if title.startswith("Category:"):
                matches.append(title.replace("Category:", ""))
        
        print(f"  Found {len(matches)} potential matches via search.")
        return matches
    except Exception as e:
        print(f"  Error scraping for '{kw}': {e}")
        return []

def main():
    print("Initializing category mapping...")
    all_mapped_cats = set() # To avoid duplicates
    
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        # Try to use Tor if available, otherwise fallback to direct
        try:
            session.proxies.update({
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            })
            # Test proxy
            session.get("https://google.com", timeout=2)
            print("Using Tor proxy for mapping.")
        except:
            print("Tor proxy not responsive. Using direct connection.")
            session.proxies = {}

        print("\nMapping research keywords to WikiHow categories:")
        final_spaces = {}
        
        for key, space in spaces.items():
            print(f"\n--- {space['title']} ---")
            mapped_cats = set()
            for kw in space["kws"]:
                # Fetch matches for this specific keyword
                cats = fetch_category_matches(kw, session)
                match = fuzzy_match(kw, cats)
                
                if not match and len(kw.split()) > 1:
                    # Try fallback to first word
                    fallback = kw.split()[0]
                    cats_fallback = fetch_category_matches(fallback, session)
                    match = fuzzy_match(fallback, cats_fallback)
                
                if match:
                    print(f"  RESULT: '{kw}' -> '{match}'")
                    mapped_cats.add(match)
                else:
                    print(f"  RESULT: '{kw}' -> NO MATCH FOUND")
            
            final_spaces[key] = {
                "title": space["title"],
                "cats": list(mapped_cats)
            }
        
    with open('data/mapped_spaces.json', 'w') as f:
        json.dump(final_spaces, f, indent=2)

if __name__ == "__main__":
    main()
