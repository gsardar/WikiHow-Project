import requests
import json

def test_api():
    title = "Bake a Cake"
    url = "https://www.wikihow.com/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "contributors|revisions",
        "rvprop": "user|comment|timestamp|size|flags",
        "rvlimit": 20
    }
    r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(f"Status Code: {r.status_code}")
        print(f"Content Start: {r.text[:500]}")


if __name__ == "__main__":
    test_api()
