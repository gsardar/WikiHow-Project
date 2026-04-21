import sys
import os
sys.path.append(os.getcwd())
from wikihow.api import _get_driver, USER_DATA_DIR
import time

def test_profile_persistence():
    print(f"Opening SeleniumBase with User Data Dir: {USER_DATA_DIR}")
    driver = _get_driver()
    
    # Visit a page that might have session data (e.g., login or user page)
    driver.get("https://www.wikihow.com/User:Whimaway")
    print(f"Page Title: {driver.title}")
    
    # Check if we are 'logged in' or if any cookies exist
    cookies = driver.get_cookies()
    print(f"Total Cookies Found: {len(cookies)}")
    
    # Take a screenshot to verify local rendering
    driver.save_screenshot("data/verification_screenshot.png")
    print("Screenshot saved to data/verification_screenshot.png")
    
    # Don't quit immediately so the subagent/user can see if possible
    time.sleep(5)

if __name__ == "__main__":
    test_profile_persistence()
