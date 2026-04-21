from seleniumbase import Driver
import os
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(base_dir, "..", "data", "browser_session")

def debug_api():
    url = "https://www.wikihow.com/api.php?action=query&meta=siteinfo&format=json"
    print(f"Opening: {url}")
    
    driver = Driver(uc=True, headless=False, user_data_dir=USER_DATA_DIR)
    try:
        driver.get(url)
        time.sleep(10) # Let it load and see if any challenges appear
        print("Page Title:", driver.get_title())
        print("Page Source Snippet:", driver.page_source[:500])
        print("Body Text Snippet:", driver.get_text("body")[:500])
        input("Review the browser window and press ENTER to close...")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_api()
