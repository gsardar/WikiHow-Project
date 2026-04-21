import os
import requests
from seleniumbase import Driver

# Re-use the existing user data dir
USER_DATA_DIR = os.path.join(os.getcwd(), "data", "browser_session")

def test_api_with_cookies():
    print("Starting browser to grab cookies...")
    driver = Driver(uc=True, headless=True, user_data_dir=USER_DATA_DIR)
    try:
        driver.get("https://www.wikihow.com")
        cookies = driver.get_cookies()
        user_agent = driver.execute_script("return navigator.userAgent")
        
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "application/json"
        }
        
        # Test a simple query
        test_url = "https://www.wikihow.com/api.php?action=query&meta=siteinfo&format=json"
        print(f"Testing API at: {test_url}")
        
        resp = session.get(test_url, headers=headers)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Successfully accessed API with browser session!")
            print(resp.text[:200])
        else:
            print(f"Failed with 500. Response snippet: {resp.text[:200]}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    test_api_with_cookies()
