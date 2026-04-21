from seleniumbase import Driver
import os
import time
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(base_dir, "..", "data", "browser_session")

def test_session():
    driver = Driver(uc=True, headless=False, user_data_dir=USER_DATA_DIR)
    try:
        # Check main page for login indicators
        print("Checking main page...")
        driver.get("https://www.wikihow.com/Main-Page")
        time.sleep(5)
        # Often login is indicated by a 'Log Out' link or a username
        page_text = driver.get_text("body").lower()
        is_logged_in = "log out" in page_text
        print(f"Is Logged In (detected by 'log out' presence): {is_logged_in}")
        
        # Check API
        api_url = "https://www.wikihow.com/api.php?action=query&meta=siteinfo&format=json"
        print(f"Checking API: {api_url}")
        driver.get(api_url)
        time.sleep(5)
        content = driver.get_text("body").strip()
        print(f"API Response (first 100 chars): {content[:100]}")
        
        if "500" in content and "error" in content.lower():
            print("!!! API still returns 500 error.")
        else:
            try:
                # Try to parse as JSON
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != -1:
                    json.loads(content[start:end])
                    print("--- API is working and returning valid JSON.")
                else:
                    print("--- API response is not JSON, but doesn't look like a 500 error page.")
            except Exception as e:
                print(f"--- Failed to parse as JSON: {e}")
                
    finally:
        driver.quit()

if __name__ == "__main__":
    test_session()
