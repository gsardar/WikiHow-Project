import os
import time
from bs4 import BeautifulSoup
from seleniumbase import Driver
from wikihow.tor_manager import tor

MAIN_BROWSER_PROFILE = r"f:\Users\Admin\Documents\WikiHow Project\data\browser_session"

def fetch_summaries(title):
    print(f"\n[SYSTEM] Fetching history for '{title}'...")
    proxy = tor.get_selenium_proxy()
    driver = Driver(uc=True, headless=False, user_data_dir=MAIN_BROWSER_PROFILE, proxy=proxy)
    
    url = f"https://www.wikihow.com/index.php?title={title.replace(' ', '_')}&action=history&limit=50"
    
    try:
        driver.get(url)
        time.sleep(5) 
        html = driver.page_source
        with open(r"f:\Users\Admin\Documents\WikiHow Project\scratch\ApplyMakeupHistory.html", "w", encoding="utf-8") as f:
            f.write(html)
        return html
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_summaries("Apply Makeup")
