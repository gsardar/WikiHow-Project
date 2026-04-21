
from seleniumbase import Driver
import os
import time

profile_dir = "f:/Users/Admin/Documents/WikiHow Project/data/sessions/browser_session"
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
proxy = "172.31.44.95:1080"

print("Starting driver test...")
try:
    # Try with headless first to see if it's a display issue
    driver = Driver(uc=True, headless=True, user_data_dir=profile_dir, agent=ua, proxy=proxy)
    print("Driver initialized successfully (Headless).")
    driver.get("https://www.wikihow.com/Main-Page")
    print(f"Page title: {driver.title}")
    driver.quit()
except Exception as e:
    print(f"Driver init failed: {e}")
