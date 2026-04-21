import os
import time
from bs4 import BeautifulSoup
from seleniumbase import Driver
from wikihow.tor_manager import tor

MAIN_BROWSER_PROFILE = r"f:\Users\Admin\Documents\WikiHow Project\data\browser_session"

def fetch_revisions_browser(title, limit=200):
    print(f"[SYSTEM] Initializing extraction driver for {title}...")
    proxy = tor.get_selenium_proxy()
    driver = Driver(uc=True, headless=False, user_data_dir=MAIN_BROWSER_PROFILE, proxy=proxy)
    
    url = f"https://www.wikihow.com/index.php?title={title.replace(' ', '_')}&action=history&limit={limit}"
    print(f"Fetching: {url}")
    
    try:
        driver.get(url)
        time.sleep(5) # Wait for page load and any bot checks
        
        # Save a screenshot so we can debug what the browser sees
        driver.save_screenshot("f:/Users/Admin/Documents/WikiHow Project/scratch/history_test.png")
        print("Screenshot saved to scratch/history_test.png")
        
        html = driver.page_source
        
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find_all("li", {"data-mw-revid": True})
        print(f"Found {len(rows)} revisions!")
        
        if len(rows) >= 2:
            rev_curr = rows[0].get('data-mw-revid', '')
            rev_last = rows[1].get('data-mw-revid', '')
            
            diff_url = f"https://www.wikihow.com/index.php?title={title.replace(' ', '_')}&diff={rev_curr}&oldid={rev_last}"
            print(f"Trying to fetch Diff: {diff_url}")
            driver.get(diff_url)
            time.sleep(5)
            
            diff_html = driver.page_source
            diff_soup = BeautifulSoup(diff_html, 'html.parser')
            added = diff_soup.find_all('td', class_='diff-addedline')
            deleted = diff_soup.find_all('td', class_='diff-deletedline')
            
            print(f"Diff stats -> Added: {len(added)} lines | Deleted: {len(deleted)} lines")
            driver.save_screenshot("f:/Users/Admin/Documents/WikiHow Project/scratch/diff_test.png")
            print("Screenshot saved to scratch/diff_test.png")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_revisions_browser("Apply Makeup")
