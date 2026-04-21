import os
import time
import requests
import ctypes
from seleniumbase import Driver
from wikihow.tor_manager import tor
from bs4 import BeautifulSoup

class ScraperEngine:
    def __init__(self, use_tor=False, use_cookies=False, headless=False):
        self.use_tor = use_tor
        self.use_cookies = use_cookies
        self.headless = headless
        self.driver = None
        self.profile_path = r"c:\Users\Admin\Documents\WikiHow Project\data\browser_session"
        
    def get_driver(self):
        if self.driver:
            try:
                _ = self.driver.current_url
                return self.driver
            except:
                try: self.driver.quit()
                except: pass
                self.driver = None

        proxy = None
        if self.use_tor:
            proxy = tor.get_selenium_proxy()
            print(f"  [ENGINE] Routing via Tor Proxy: {proxy}")

        user_data_dir = None
        if self.use_cookies:
            user_data_dir = self.profile_path
            print(f"  [ENGINE] Loading Native Cookies: {user_data_dir}")

        self.driver = Driver(uc=True, headless=self.headless, user_data_dir=user_data_dir, proxy=proxy)
        return self.driver

    def destroy_driver(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
            self.driver = None

    def get_with_requests(self, url, timeout=15):
        proxies = None
        if self.use_tor:
            proxies = tor.get_requests_proxies()
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        return response

    def handle_popups(self):
        """Standard shield for Google Consent and WikiHow Modals."""
        if not self.driver: return
        
        url = self.driver.current_url.lower()
        # 1. Google Consent
        if "google" in url:
            try:
                # Try common Google Accept selectors
                selectors = ["button#L2AGLb", "button[aria-label='Accept all']"]
                for sel in selectors:
                    btns = self.driver.find_elements("css selector", sel)
                    if btns:
                        btns[0].click()
                        time.sleep(1)
            except: pass

        # 2. WikiHow Newsletter/Join Popups
        if "wikihow.com" in url:
            try:
                # Common WikiHow modal close buttons
                modal_close = self.driver.find_elements("css selector", ".modal-header .close, .optin_control_close")
                if modal_close:
                    modal_close[0].click()
                    print("  [SHIELD] Blocked WikiHow Popup.")
            except: pass

    def solve_captcha_manual(self):
        """Interruption for manual captcha solving."""
        print("  [ENGINE] CAPTCHA detected - waiting for manual intervention...")
        title = "Scriver Engine - CAPTCHA"
        msg = "Solve CAPTCHA in browser, then click OK to resume.\nClick Cancel to stop."
        res = ctypes.windll.user32.MessageBoxW(0, msg, title, 1 | 0x30 | 0x40000 | 0x1000)
        return res == 1 # IDOK
