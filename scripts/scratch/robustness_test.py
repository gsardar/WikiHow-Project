import os
import time
import logging
from seleniumbase import Driver

# --- CONFIG ---
WORKSPACE_DIR = r"f:\Users\Admin\Documents\WikiHow Project"
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "browser_session")
TARGET_FILE = os.path.join(WORKSPACE_DIR, "data", "User_ Bhoimus - wikiHow.pdf")
PROMPT_FILE = os.path.join(WORKSPACE_DIR, "instruct", "profiler_prompt.txt")

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger(__name__)

# --- XPATHS FROM "DEEPSEEK FIX.TXT" ---
# Turn 0 (Initial New Chat)
XP_TURN0_UPLOAD_BTN = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div[1]"
XP_TURN0_TEXTAREA = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/textarea"
XP_TURN0_SEND_BTN = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[2]/div"
XP_TURN0_STATUS = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]"
XP_TURN0_END = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[3]/div[1]/div[5]"

def wait_for_parsing(driver, send_btn_xpath):
    logger.info("Waiting for parsing handshake (checking send button state)...")
    time.sleep(2)
    for _ in range(60):
        try:
            send_btn = driver.find_element("xpath", send_btn_xpath)
            classes = send_btn.get_attribute("class") or ""
            # The button is disabled while parsing
            if "ds-icon-button--disabled" not in classes:
                logger.info("Parsing complete (Send button enabled).")
                return True
            time.sleep(1)
        except: pass
    return False

def run_robustness_test():
    with open(PROMPT_FILE, "r") as f:
        master_prompt = f.read()

    logger.info("Starting DeepSeek Robustness Test (NEW CHAT EVERY TURN)...")
    driver = Driver(uc=False, headless=False, user_data_dir=USER_DATA_DIR)
    
    try:
        # We start a NEW CHAT for every turn as requested by the user
        for turn in range(5):
            logger.info(f"--- TURN {turn} ---")
            
            # Navigating helps ensure we are in 'New Chat' state
            driver.get("https://chat.deepseek.com")
            time.sleep(5)
            
            # Step 1: Upload File
            try:
                # The file input is the most stable way to upload
                file_input = driver.find_element("css selector", "input[type='file']")
                file_input.send_keys(os.path.abspath(TARGET_FILE))
                logger.info("File uploaded.")
            except:
                driver.find_element("xpath", XP_TURN0_UPLOAD_BTN).send_keys(os.path.abspath(TARGET_FILE))
            
            # Step 2: Wait for Parsing
            wait_for_parsing(driver, XP_TURN0_SEND_BTN)
            
            # Step 3: Type Prompt
            textarea_xpath = XP_TURN0_TEXTAREA
            try:
                textarea = driver.wait_for_element_visible("xpath", textarea_xpath, timeout=10)
            except:
                logger.error(f"Textarea not found: {textarea_xpath}")
                continue

            # React-Safe Value Injection
            inject_script = """
            const el = arguments[0];
            const val = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            """
            driver.execute_script(inject_script, textarea, master_prompt)
            logger.info("Prompt injected.")
            time.sleep(2)
            
            # Step 4: Click Send
            send_xpath = XP_TURN0_SEND_BTN
            if driver.find_elements("xpath", send_xpath + "/div[1]"):
                send_xpath += "/div[1]"
                
            logger.info(f"Clicking send...")
            try:
                driver.click(send_xpath)
            except:
                btn = driver.find_element("xpath", send_xpath)
                driver.execute_script("arguments[0].click();", btn)
            
            # Step 5: Wait for Completion
            logger.info("Waiting for generation...")
            end_xpath = XP_TURN0_END
            for i in range(120):
                if driver.find_elements("xpath", end_xpath):
                    logger.info("Generation finished.")
                    break
                time.sleep(2)
            
            time.sleep(5) # Delay to observe result
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Closing in 30s...")
        time.sleep(30)
        driver.quit()

if __name__ == "__main__":
    run_robustness_test()
