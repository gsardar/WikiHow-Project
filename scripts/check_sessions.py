"""
WikiHow Session Checker
Verifies that the persisted SeleniumBase browser profile has active login sessions
for WikiHow and DeepSeek. Prints the login status and instructs the user if not logged in.
"""
import sys
import os
sys.path.append(os.getcwd())

from wikihow.api import _get_driver
import time

CHECKS = {
    "WikiHow": {
        "url": "https://www.wikihow.com/Special:UserLogin",
        "logged_in_url_fragment": "Special:UserLogin",  # If redirected AWAY from login page, we're logged in
        "logged_in_indicator": "Log Out",               # Text present when logged in
        "logged_out_indicator": "Log In",
    },
    "DeepSeek": {
        "url": "https://chat.deepseek.com",
        "logged_in_indicator": "New chat",              # Present on chat page when authenticated
        "logged_out_indicator": "Sign In",
    },
}

def check_session(driver, name: str, info: dict) -> bool:
    print(f"\n🔍 Checking {name}...")
    driver.get(info["url"])
    time.sleep(3)

    page_text = driver.get_text("body")

    if info.get("logged_in_indicator") and info["logged_in_indicator"] in page_text:
        print(f"  ✅ {name}: LOGGED IN (found '{info['logged_in_indicator']}')")
        return True
    elif info.get("logged_out_indicator") and info["logged_out_indicator"] in page_text:
        print(f"  ❌ {name}: NOT LOGGED IN (found '{info['logged_out_indicator']}')")
        return False
    else:
        print(f"  ⚠️  {name}: AMBIGUOUS — could not determine login state.")
        print(f"       Current URL: {driver.current_url}")
        return False

def main():
    print("="*50)
    print("WikiHow Project — Browser Session Validator")
    print("="*50)

    driver = _get_driver()
    results = {}
    for name, info in CHECKS.items():
        results[name] = check_session(driver, name, info)

    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    all_ok = True
    for name, ok in results.items():
        status = "✅ Logged In" if ok else "❌ NOT logged in — Please log in manually."
        print(f"  {name}: {status}")
        if not ok:
            all_ok = False

    if not all_ok:
        print("""
ACTION REQUIRED:
  1. Run this script with headless=False to see the browser window.
  2. Log in manually to the failed services.
  3. Re-run this script to confirm — the session will be saved in:
       data/browser_session/
""")
    else:
        print("\n✅ All sessions active. Ready to scrape.\n")

if __name__ == "__main__":
    main()
