import os
import csv
import re
import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WikiHowUserProfiler:
    def __init__(self, driver):
        self.driver = driver

    def get_user_metadata(self, username):
        url = f"https://www.wikihow.com/User:{username.replace(' ', '-')}"
        print(f"Profiling: {username} -> {url}")
        self.driver.get(url)
        
        # Wait for the main profile container to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#user_about, .userinfo_stats, .user_badge"))
            )
        except:
            print(f"  [TIMEOUT] Profile took too long to load for {username}")

        metadata = {
            "username": username,
            "url": url,
            "is_staff": False,
            "is_admin": False,
            "is_booster": False,
            "is_welcomer": False,
            "is_bot": False,
            "bio": "",
            "expertise": "",
            "edit_count_profile": "",
            "badges_raw": "",
            "extra_stats": ""
        }

        # NEW: Absolute Scraper Logic (Regex on raw text)
        full_text = self.driver.execute_script("return document.body.innerText;")
        
        # 1. Pattern Scout: Badges (Any pb-badge)
        badges = self.driver.find_elements(By.CSS_SELECTOR, ".pb-badge")
        found_badges = []
        for b in badges:
            cls = b.get_attribute("class")
            text = b.text.strip()
            found_badges.append(f"{text}({cls})")
            if "pb-staff" in cls: metadata["is_staff"] = True
            if "pb-admin" in cls: metadata["is_admin"] = True
            if "pb-nab" in cls: metadata["is_booster"] = True
            if "pb-welcome" in cls: metadata["is_welcomer"] = True
        metadata["badges_raw"] = "|".join(found_badges)
        
        if "BOT" in username.upper() or any("pb-bot" in b.lower() for b in found_badges):
            metadata["is_bot"] = True

        # 2. Regex Bio Extraction
        # Look for typical start of bio text
        bio_match = re.search(r"(Hi, I'm .*?\. .*?)(?=Questions Answered|Awards|Statistics|$)", full_text, re.DOTALL | re.IGNORECASE)
        if bio_match:
            metadata["bio"] = bio_match.group(1).strip().replace("\n", " ")
        else:
            # Fallback for staff accounts
            staff_match = re.search(r"(This is an account used by editors.*?)(?=Questions Answered|Awards|Statistics|$)", full_text, re.DOTALL | re.IGNORECASE)
            if staff_match:
                metadata["bio"] = staff_match.group(1).strip().replace("\n", " ")

        # 3. Regex Expertise extraction
        expert_match = re.search(r"Questions Answered\s*(.*?)(?=Awards|Statistics|$)", full_text, re.DOTALL | re.IGNORECASE)
        if expert_match:
            metadata["expertise"] = expert_match.group(1).strip().replace("\n", ", ")

        # 4. Regex Stats
        # Prioritize 'X contributions' then 'X edits'
        contrib_match = re.search(r"([\d,]+)\s+contributions", full_text, re.IGNORECASE)
        if contrib_match:
            metadata["edit_count_profile"] = contrib_match.group(1).replace(",", "")
        else:
            edit_match = re.search(r"([\d,]+)\s+edits", full_text, re.IGNORECASE)
            if edit_match:
                metadata["edit_count_profile"] = edit_match.group(1).replace(",", "")
        
        # Clean up extra stats (limit to meaningful words/numbers)
        stats_raw = re.findall(r"([\d,]+\s+\w+)", full_text)
        metadata["extra_stats"] = "|".join([s for s in stats_raw if len(s) < 30])

        # NEW: String Sanitizer for CSV rows
        for key in ["bio", "expertise", "extra_stats"]:
            metadata[key] = metadata[key].replace("\n", " ").replace("\r", " ").strip()

        return metadata

def run_profiler(user_list, output_file):
    profile_path = r"c:\Users\Admin\Documents\WikiHow Project\data\browser_session"
    print(f"  [PROFILER] Initializing with Native Cookies: {profile_path}")
    
    driver = Driver(uc=True, headless=False, user_data_dir=profile_path)
    profiler = WikiHowUserProfiler(driver)
    
    fieldnames = ["username", "url", "is_staff", "is_admin", "is_booster", "is_welcomer", "is_bot", "bio", "expertise", "edit_count_profile", "badges_raw", "extra_stats"]
    
    for user in user_list:
        file_exists = os.path.isfile(output_file)
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            
            try:
                data = profiler.get_user_metadata(user)
                writer.writerow(data)
                f.flush()
                print(f"Successfully profiled and FLUSHED {user}")
            except Exception as e:
                print(f"Error profiling {user}: {e}")
            time.sleep(1)

    driver.quit()

def check_for_collisions():
    """Checks for other python/chrome instances that might interfere."""
    # We use a simple message box to alert the user
    import subprocess
    try:
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq chrome.exe"', shell=True).decode()
        if "chrome.exe" in output:
            title = "Profiler Collision Warning"
            msg = "Chrome is already running! Scrapers cannot share the profile.\n\nShould I kill all Chrome processes and continue?"
            res = ctypes.windll.user32.MessageBoxW(0, msg, title, 0x00000004 | 0x00000030 | 0x00001000)
            if res == 6: # Yes
                os.system("taskkill /F /IM chrome.exe /T")
                time.sleep(2)
            else:
                print("Aborting to avoid collision.")
                exit(0)
    except:
        pass

if __name__ == "__main__":
    check_for_collisions()
    
    top_users = [
        "Seymour Edits", "Votebot", "MiscBot", "Wikivisual", "WikiHow Projects", 
        "RelatedWikihowsBot", "Wikiphoto", "Flickety", "InterwikiBot", "WRM", 
        "WikiHow Expert Review", "Anna", "Thomas_Ch", "ICanGuessItLol", "WikiHow Horizon"
    ]
    output_path = r"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\accounts\accounts_metadata.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    run_profiler(top_users, output_path)
