import requests
import json
import time
import os

BASE_URL = "https://www.wikihow.com/api.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

def test_api_module(name, params):
    headers = {"User-Agent": USER_AGENT}
    params["format"] = "json"
    
    print(f"Testing Module: {name}...")
    try:
        start = time.time()
        r = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
        duration = time.time() - start
        
        status = r.status_code
        try:
            data = r.json()
            is_json = True
            keys = list(data.keys())
        except:
            data = r.text[:200]
            is_json = False
            keys = []
            
        return {
            "name": name,
            "status": status,
            "duration": round(duration, 2),
            "is_json": is_json,
            "keys": keys,
            "params": params,
            "sample": str(data)[:300]
        }
    except Exception as e:
        return {
            "name": name,
            "status": "ERROR",
            "error": str(e)
        }

def run_audit():
    tests = [
        ("Mapping (Query:CategoryMembers)", {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Gardening",
            "cmlimit": 5
        }),
        ("History (Query:Revisions)", {
            "action": "query",
            "prop": "revisions",
            "titles": "How to Prepare Soil for a Vegetable Garden",
            "rvlimit": 5
        }),
        ("Content (Parse)", {
            "action": "parse",
            "page": "How to Prepare Soil for a Vegetable Garden",
            "prop": "text|revisions"
        }),
        ("Users (Query:Users)", {
            "action": "query",
            "list": "users",
            "ususers": "Gourav 4|Krystle",
            "usprop": "gender|editcount"
        }),
        ("SiteInfo (Query:Meta)", {
            "action": "query",
            "meta": "siteinfo"
        }),
        ("Search (Query:Search)", {
            "action": "query",
            "list": "search",
            "srsearch": "Gardening",
            "srlimit": 5
        }),
        ("CategoryList (Query:AllCategories)", {
            "action": "query",
            "list": "allcategories",
            "aclimit": 5
        })
    ]
    
    results = []
    for name, params in tests:
        res = test_api_module(name, params)
        results.append(res)
        time.sleep(2) # Modest throttle
        
    os.makedirs("data", exist_ok=True)
    with open("data/api_audit.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nAudit Complete. Saved to data/api_audit.json")
    
    # Print summary
    print("\nAPI STATUS SUMMARY:")
    for r in results:
        status_str = f"[{r['status']}]" if r['status'] == 200 else f"!! {r['status']} !!"
        print(f"{status_str} {r['name']} ({r.get('duration', 'N/A')}s)")

if __name__ == "__main__":
    run_audit()
