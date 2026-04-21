import requests
import json
import time

BASE_URL = "https://www.wikihow.com/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def test_module(name, params):
    params.update({"format": "json"})
    try:
        start = time.time()
        r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        latency = time.time() - start
        
        status = r.status_code
        try:
            data = r.json()
            is_valid_json = True
            error = data.get("error", {}).get("info", "None")
        except:
            is_valid_json = False
            error = "Invalid JSON"
            
        print(f"[{status}] {name: <20} | Latency: {latency: >5.2f}s | JSON: {is_valid_json: <5} | Error: {error}")
        return {"status": status, "module": name, "latency": latency, "json": is_valid_json, "error": error}
    except Exception as e:
        print(f"[ERR] {name: <20} | Error: {str(e)[:50]}")
        return {"status": "ERROR", "module": name, "error": str(e)}

def run_audit():
    print(f"{'='*80}")
    print(f"WikiHow API Audit - {time.ctime()}")
    print(f"{'='*80}\n")
    
    audit_cases = [
        ("Base Connection", {"action": "query", "meta": "siteinfo"}),
        ("Simple Info", {"action": "query", "prop": "info", "titles": "Gardening"}),
        ("Cat Members (Small)", {"action": "query", "list": "categorymembers", "cmtitle": "Category:Gardening", "cmlimit": 1}),
        ("Cat Members (Large)", {"action": "query", "list": "categorymembers", "cmtitle": "Category:Gardening", "cmlimit": 50}),
        ("Generator Cat", {"action": "query", "generator": "categorymembers", "gcmtitle": "Category:Gardening"}),
        ("Search (List)", {"action": "query", "list": "search", "srsearch": "Gardening"}),
        ("Revisions", {"action": "query", "prop": "revisions", "titles": "Gardening", "rvlimit": 5}),
        ("Parse Action", {"action": "parse", "page": "Gardening", "prop": "text"}),
        ("User Info", {"action": "query", "list": "users", "ususers": "Admin"}),
        ("Namespace Check", {"action": "query", "meta": "siteinfo", "siprop": "namespaces"}),
        ("Recent Changes", {"action": "query", "list": "recentchanges", "rclimit": 5}),
        ("All Pages", {"action": "query", "list": "allpages", "aplimit": 5}),
    ]
    
    results = []
    for name, params in audit_cases:
        results.append(test_module(name, params))
        time.sleep(1) # Polite delay
        
    print(f"\n{'='*80}")
    summary = {
        "total": len(results),
        "success_200": len([r for r in results if r.get("status") == 200]),
        "failed_500": len([r for r in results if r.get("status") == 500]),
        "errors": len([r for r in results if r.get("status") in (404, 403, "ERROR")])
    }
    print(f"Audit Summary: {summary}")
    
    with open("data/logs/api_audit.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"Detailed results saved to data/logs/api_audit.json")

if __name__ == "__main__":
    run_audit()
