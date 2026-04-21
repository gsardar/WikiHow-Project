import os
import time
import pandas as pd
from seleniumbase import Driver
import ctypes
import json

# -- CONFIGURATION ------------------------------------------------------------
BROWSER_DATA = r"c:\Users\Admin\Documents\WikiHow Project\data\browser_session"

# Selectors
TAG_TEXTAREA  = "textarea"
REL_FILE_INPUT = "//input[@type='file']"
XPATH_PREVIEW = "._76cd190"

# User's Pattern Fallback (from absolute path)
USER_PATTERN_TEXTBOX = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[2]/div[2]/div/div[2]/div[2]/div[3]/div[2]/div/div[1]"

# -- GLOBAL STATE --
GLOBAL_HANDLES = {"hub": None, "probe": None}

# -- CAPTCHA POPUP ------------------------------------------------------------
def handle_captcha(driver):
    try:
        if "just a moment" in driver.title.lower() or driver.find_elements("css selector", "#cf-turnstile-wrapper"):
            print("\n[GATE] CAPTCHA detected. Solve it, then click OK.")
            ctypes.windll.user32.MessageBoxW(0, "Solve CAPTCHA, then click OK.", "Handshake Alert", 0x40000 | 0x30)
            time.sleep(2)
    except: pass

# -- DOM UTILS ----------------------------------------------------------------
def click_send_button(driver):
    script = """
    function findSend() {
        // Look for the blue arrow SVG in the bottom right group
        const btns = document.querySelectorAll('div[role="button"], button');
        for (const btn of btns) {
            if (btn.querySelector('svg') && btn.offsetHeight > 20) {
                const r = btn.getBoundingClientRect();
                if (r.bottom > window.innerHeight - 300) return btn;
            }
        }
        return null;
    }
    const b = findSend();
    if (b) { b.click(); return true; }
    return false;
    """
    try: return driver.execute_script(script)
    except: return False

def clear_attachments(driver):
    try:
        driver.execute_script("document.querySelectorAll('._76cd190, .ds-icon-close, .remove-btn').forEach(el => el.click());")
        time.sleep(1)
    except: pass

# -- HANDSHAKES ---------------------------------------------------------------
def get_latest_response(driver, old_count):
    print("  [Wait] Waiting for NEW AI response...")
    last_text = ""
    for _ in range(60):
        try:
            msgs = driver.find_elements("css selector", ".ds-markdown")
            if len(msgs) > old_count:
                current_text = msgs[-1].text.strip()
                if len(current_text) > 10:
                    if any(x in current_text.lower() for x in ["cannot read", "unable to see", "no image", "no text"]):
                        return "DUD_FAILURE"
                    break
        except: pass
        time.sleep(2)
        
    print("  [Wait] Stabilizing output...")
    for _ in range(30):
        try:
            msgs = driver.find_elements("css selector", ".ds-markdown")
            if msgs:
                current_text = msgs[-1].text
                if current_text == last_text and len(current_text) > 20:
                    if not driver.find_elements("css selector", ".ds-icon-stop-circle"):
                        return current_text
                last_text = current_text
        except: pass
        time.sleep(2)
    return last_text if last_text else "Timeout"

def get_bio_context(driver):
    try:
        return driver.find_element("css selector", "#bodyContent").text[:1200].replace("\n", " ").strip()
    except: return "Context unavailable."

def switch_to_tab(driver, key, fallback_script=None):
    h = GLOBAL_HANDLES.get(key)
    if h and h in driver.window_handles:
        driver.switch_to.window(h)
        return h
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url.lower()
        if key == "hub" and "deepseek" in url:
            GLOBAL_HANDLES["hub"] = handle
            return handle
        if key == "probe" and "wikihow" in url:
            GLOBAL_HANDLES["probe"] = handle
            return handle
    if fallback_script:
        driver.execute_script(fallback_script)
        time.sleep(4)
        new_h = driver.window_handles[-1]
        GLOBAL_HANDLES[key] = new_h
        return new_h
    return None

# -- MAIN SEQUENCE ------------------------------------------------------------
def run_handshake_test():
    os.system("taskkill /F /IM chrome.exe /T 2>nul")
    time.sleep(2)
    driver = Driver(uc=True, headless=False, user_data_dir=BROWSER_DATA)
    try:
        # -- Phase 1: Establish Hub on initial window --
        print("  [Setup] Initializing Primary Hub...")
        # Use Non-Blocking JS Redirect to bypass onload hangs
        driver.execute_script("window.location.href = 'https://chat.deepseek.com';")
        GLOBAL_HANDLES["hub"] = driver.current_window_handle
        
        # Poll for ready with a refresh fallback
        for _ in range(10):
            handle_captcha(driver)
            if driver.find_elements("css selector", TAG_TEXTAREA): break
            if driver.find_elements("xpath", USER_PATTERN_TEXTBOX): break
            print("  [Setup] Interface not found. Re-checking...")
            time.sleep(5)
        else:
            print("  [Setup] [Warning] Forcing refresh...")
            driver.refresh(); time.sleep(5)
            
        print("  [Setup] [OK] Hub Ready.")

        # Phase 2: Establish Probe
        switch_to_tab(driver, "probe", "window.open('about:blank', '_blank');")
        
        test_targets = ["Sophia B", "Jr eds", "Authoring This", "Skycaptain95"]
        for u in test_targets:
            print(f"\n-- Handshake Test: {u} --")
            switch_to_tab(driver, "probe")
            driver.get(f"https://www.wikihow.com/User:{u.replace(' ', '_')}")
            time.sleep(4)
            bio_context = get_bio_context(driver)
            u_img = os.path.join(r"c:\Users\Admin\Documents\WikiHow Project\data", f"{u.replace(' ', '_')}.png")
            driver.save_screenshot(u_img)
            
            for attempt in range(2):
                switch_to_tab(driver, "hub")
                clear_attachments(driver)
                # Upload
                driver.find_element("xpath", REL_FILE_INPUT).send_keys(os.path.abspath(u_img))
                
                print("  [Handshake] Waiting for ingestion...")
                for _ in range(60):
                    if len(driver.find_elements("css selector", XPATH_PREVIEW)) > 0: break
                    time.sleep(1)
                
                old_count = len(driver.find_elements("css selector", ".ds-markdown"))
                prompt = (f"BIO: {bio_context}\n\n"
                          f"TASK: Identify gender of wikiHow user '{u}' based on context & image.\n"
                          f"FORMAT: Output ONLY JSON: {{\"username\":\"{u}\", \"gender\":\"...\", \"reasoning\":\"...\"}}")
                
                # Input
                textarea = None
                tas = driver.find_elements("css selector", TAG_TEXTAREA)
                if tas: textarea = tas[0]
                else:
                    tas = driver.find_elements("xpath", USER_PATTERN_TEXTBOX)
                    if tas: textarea = tas[0]
                
                if textarea:
                    # Nuclear Overlay Purge
                    driver.execute_script("document.querySelectorAll('[popover]').forEach(el => el.remove());")
                    
                    # React-Safe Value Injection
                    inject_script = """
                    const el = arguments[0];
                    const val = arguments[1];
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
                    setter.call(el, val);
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    """
                    driver.execute_script(inject_script, textarea, prompt)
                    print("  [Handshake] Prompt injected via state-hook. Polling for Geometric Dispatch...")
                    time.sleep(3)
                    
                    # 3. Geometric Send
                    dispatched = False
                    for _ in range(15):
                        if click_send_button(driver):
                            dispatched = True; break
                        time.sleep(1)
                    
                    if not dispatched:
                        print("  [Handshake] [Warning] Geometric dispatch failed. Using Enter fallback.")
                        textarea.send_keys("\n")
                
                # Extract
                result = get_latest_response(driver, old_count)
                if result == "DUD_FAILURE":
                    print(f"  [Retry] Dud detected. Purging...")
                    continue
                print(f"  [Result] {u}: {result}")
                break

        print("\n[DONE] Universal Master proof complete.")
        input("Press Enter to close browser...")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_handshake_test()
