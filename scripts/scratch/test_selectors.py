import requests
import os
import json
from bs4 import BeautifulSoup


def test_url(url):
    cookies = {}
    cookie_path = r"f:\Users\Admin\Documents\WikiHow Project\data\session_cookies.json"
    if os.path.exists(cookie_path):
        with open(cookie_path, "r") as f:
            cookies = json.load(f)
            
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, cookies=cookies)

    print(f"URL: {url}")
    print(f"Status: {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    print(f"Title: {soup.title.string if soup.title else 'No Title'}")
    print(f"Content length: {len(r.text)}")
    # Check for "revisions" ul
    history = soup.select("ul#pagehistory li")
    print(f"History items: {len(history)}")
    # Check for about_article
    about = soup.select("#about_article")
    print(f"About section found: {len(about)}")

    if "About This Article" in r.text:
       print("Found 'About This Article' in text!")
       idx = r.text.find("About This Article")
       print(f"Snippet: {r.text[idx:idx+1000]}")
    else:
       print("DID NOT find 'About This Article' in text.")



if __name__ == "__main__":
    test_url("https://www.wikihow.com/Bake-a-Cake")
    test_url("https://www.wikihow.com/index.php?title=Bake-a-Cake&action=history")
    test_url("https://www.wikihow.com/index.php?title=Bake_a_Cake&action=history")

