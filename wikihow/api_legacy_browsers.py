"""
WikiHow API Client (LEGACY BROWSER ARCHIVE)
This file contains the original Selenium-based logic for article history 
and user profile scraping. 

[CAUTION]: These functions may trigger chromedriver crashes on some systems.
For the stable version, use wikihow/api.py.
"""
import time
import os
from bs4 import BeautifulSoup
from seleniumbase import Driver
import urllib.parse
import re

# Original User Resolution Logic (Browser-Based)
def legacy_get_profile_gender(username, driver):
    """Original Selenium-based profile scraper."""
    profile_url = f"https://www.wikihow.com/User:{username.replace(' ', '_')}"
    user_info = {"username": username, "real_name": "unknown", "location": "unknown", "gender": "unknown"}
    
    try:
        driver.get(profile_url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        header = soup.select_one("#hp_top_right")
        if header:
            rows = header.select("p.hp_top_row")
            if rows:
                b_tags = rows[0].find_all("b")
                if len(b_tags) >= 1: user_info["real_name"] = b_tags[0].get_text().strip()
                if len(b_tags) >= 2: user_info["location"] = b_tags[1].get_text().strip()
                
        # Bio Content
        bio_elem = soup.select_one("#bodyContent")
        if bio_elem: user_info["bio"] = bio_elem.get_text().strip()
        
        return user_info
    except Exception as e:
        print(f"Legacy Scraping Error: {e}")
        return user_info

# Original History Scraping Logic (Browser-Based)
def legacy_get_revisions(title, driver, limit=50):
    """Original Selenium-based history scraper."""
    slug = title.replace(" ", "_")
    url = f"https://www.wikihow.com/index.php?title={slug}&action=history&limit={limit}"
    
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        history_list = soup.select("ul#pagehistory li")
        results = []
        for li in history_list:
            user_link = li.select_one(".mw-userlink")
            if user_link:
                results.append({
                    "user": user_link.get_text().strip(),
                    "timestamp": li.select_one(".mw-changeslist-date").get_text().strip()
                })
        return results
    except Exception as e:
        print(f"Legacy History Error: {e}")
        return []
