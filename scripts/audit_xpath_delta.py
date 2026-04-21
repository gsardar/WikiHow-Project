import os
import time
from seleniumbase import Driver

def get_full_xpath(driver, element):
    return driver.execute_script("""
        function getXPath(el) {
            const parts = [];
            while (el && el.nodeType === 1) {
                let idx = 1, sib = el.previousSibling;
                while (sib) { if (sib.nodeType === 1 && sib.tagName === el.tagName) idx++; sib = sib.previousSibling; }
                parts.unshift(el.tagName.toLowerCase() + '[' + idx + ']');
                el = el.parentNode;
            }
            return '/' + parts.join('/');
        }
        return getXPath(arguments[0]);
    """, element)

def audit_delta():
    WORKSPACE_DIR = r"c:\Users\Admin\Documents\WikiHow Project"
    BROWSER_DATA = os.path.join(WORKSPACE_DIR, "data", "browser_session")
    TEMP_IMAGE = os.path.join(WORKSPACE_DIR, "data", "temp_gender_audit.png")
    
    print("Starting Structural XPath Delta Audit...")
    driver = Driver(uc=True, headless=False, user_data_dir=BROWSER_DATA)
    
    try:
        driver.get("https://chat.deepseek.com")
        time.sleep(5)
        
        # 1. Capture Base State
        print("  [Audit] Capturing State A (No File)...")
        # Selector for the Send button (usually a div with an svg inside the input area)
        send_btn = driver.find_element("css selector", "div[role='button'] svg, button svg")
        # Go up to the actual button container
        send_btn_parent = driver.execute_script("return arguments[0].closest('div[role=\"button\"], button')", send_btn)
        
        xpath_a = get_full_xpath(driver, send_btn_parent)
        print(f"  STATE A XPATH: {xpath_a}")
        
        # 2. Upload File
        print(f"  [Audit] Injecting {TEMP_IMAGE}...")
        file_input = driver.find_element("css selector", "input[type='file']")
        file_input.send_keys(os.path.abspath(TEMP_IMAGE))
        
        # 3. Wait for Thumbnail
        print("  [Audit] Waiting for thumbnail UI update...")
        for _ in range(15):
            previews = driver.find_elements("css selector", "._76cd190")
            if previews:
                print("  [Audit] Thumbnail detected.")
                break
            time.sleep(1)
            
        # 4. Capture Post-Upload State
        print("  [Audit] Capturing State B (File Uploaded)...")
        send_btn_b = driver.execute_script("return document.querySelector('div[role=\"button\"] svg, button svg').closest('div[role=\"button\"], button')")
        xpath_b = get_full_xpath(driver, send_btn_b)
        print(f"  STATE B XPATH: {xpath_b}")
        
        # 5. Final Report
        print("\n" + "="*50)
        print("FINAL DELTA REPORT:")
        print(f"State A (Empty): {xpath_a}")
        print(f"State B (File) : {xpath_b}")
        if xpath_a == xpath_b:
            print("RESULT: No structural shift detected in the Send button path.")
        else:
            print("RESULT: Structural displacement detected!")
        print("="*50 + "\n")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    audit_delta()
