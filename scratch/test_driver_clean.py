
from seleniumbase import Driver
import os
import time

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

print("Starting driver test (NO PROFILE, NO PROXY)...")
try:
    driver = Driver(uc=True, headless=True, agent=ua)
    print("Driver initialized successfully.")
    driver.get("https://www.google.com")
    print(f"Page title: {driver.title}")
    driver.quit()
except Exception as e:
    print(f"Driver init failed: {e}")
