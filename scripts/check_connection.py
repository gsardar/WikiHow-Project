import requests
from wikihow import api

def check_connection():
    # 1. Start browser once to sync cookies
    driver = api._get_driver()
    api.sync_browser_cookies()
    
    # 2. Test static request using those cookies
    url = "https://www.wikihow.com/User:Gourav_4"
    r = requests.get(url, cookies=api._SESSION_COOKIES)
    
    print(f"Server Response Code: {r.status_code}")
    if "Gourav 4" in r.text:
        print("SUCCESS: Engine is correctly connected to 'Gourav 4'!")
    else:
        print("FAILED: Session not detected.")

if __name__ == "__main__":
    check_connection()
