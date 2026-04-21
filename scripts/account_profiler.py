import os
import csv
import json
import time
import re
import logging
import pandas as pd
from seleniumbase import Driver
from datetime import datetime
import base64

# --- CONFIG ---
WORKSPACE_DIR = r"f:\Users\Admin\Documents\WikiHow Project"
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "browser_session")
TARGET_CSV = os.path.join(WORKSPACE_DIR, "data", "upscale_test_200.csv")
OUTPUT_CSV = os.path.join(WORKSPACE_DIR, "data", "pilot_research_max_batched.csv")
PROMPT_FILE = os.path.join(WORKSPACE_DIR, "instruct", "profiler_prompt.txt")
TEMP_PDF = os.path.join(WORKSPACE_DIR, "data", "temp_profiler.pdf")

# Log setup
LOG_FILE = os.path.join(WORKSPACE_DIR, "data", "profiler_execution.log")
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

XP_NEW_CHAT_TEXTAREA_FILE  = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/textarea"
XP_NEW_CHAT_SEND_BTN       = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[2]/div"
XP_NEW_CHAT_STATUS         = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]"
XP_NEW_CHAT_UPLOAD_BTN     = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div[1]"

# Threaded Chat (Turn 1+)
XP_THREAD_RESPONSE = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[1]"
XP_THREAD_TEXTAREA = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[4]/div[1]/div/div/div[2]/div/div/div[2]/div[1]/div/textarea"
XP_THREAD_SEND_BTN = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[4]/div[1]/div/div/div[2]/div/div/div[2]/div[3]/div[2]/div"
XP_THREAD_END      = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[2]/div[2]/div[5]"
XP_TURN0_END       = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[3]/div[1]/div[5]"
XP_TURN1_END       = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[4]/div[3]/div[1]/div[5]"

class AccountProfiler:
    def __init__(self):
        with open(PROMPT_FILE, "r") as f:
            self.master_prompt = f.read()

    def wait_for_deepseek_parsing(self, driver):
        """Wait for DeepSeek to finish processing the uploaded file with a strict handshake."""
        logger.info("Waiting for DeepSeek parsing (STRICT handshake)...")
        time.sleep(3) 
        
        for _ in range(90):
            try:
                # 1. Error Detection: Check Status bar for failure message
                status_elements = driver.find_elements("xpath", XP_NEW_CHAT_STATUS)
                if status_elements:
                    text = status_elements[0].text.lower()
                    if "no text extracted" in text:
                        logger.error("DeepSeek ERROR: No text extracted from file.")
                        return False

                # 2. Preparation Check: Monitor the Send button state
                send_btn = driver.find_element("xpath", XP_NEW_CHAT_SEND_BTN)
                classes = send_btn.get_attribute("class") or ""
                
                # Handshake is complete when the button no longer has the '--disabled' class
                if "ds-icon-button--disabled" not in classes:
                    logger.info("Handshake COMPLETE: Send button is enabled.")
                    time.sleep(2) # Buffer for React state sync
                    return True
            except: pass
            time.sleep(1)
        return False

    def extract_from_deepseek(self, driver, username, file_path):
        """Perform the file upload and prompt sequence on DeepSeek."""
        logger.info(f"Uploading {username} profile to DeepSeek...")
        
        # Upload using standard input
        try:
            file_input = driver.find_element("css selector", "input[type='file']")
            file_input.send_keys(os.path.abspath(file_path))
        except:
             # Fallback if ID/CSS fails
             driver.find_element("xpath", "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div[1]").send_keys(os.path.abspath(file_path))
        
        # Wait for parsing handshake (Crucial: wait for enabled button)
        if not self.wait_for_deepseek_parsing(driver):
            logger.error(f"Image parsing timed out for {username}. Scaling back.")
            return None
        
        # Prompt (Turn 0)
        prompt = self.master_prompt.replace("{u}", username)
        
        # Inject prompt via JS to avoid React state issues or stale elements
        logger.info(f"Injecting analysis prompt for {username}...")
        try:
            textarea = driver.find_element("xpath", XP_NEW_CHAT_TEXTAREA_FILE)
            inject_script = """
            const el = arguments[0];
            const val = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            """
            driver.execute_script(inject_script, textarea, prompt)
            time.sleep(2)
        except Exception as e:
            logger.error(f"Failed to inject prompt: {e}")
            return None
        
        # Click the "New Chat" Send button
        send_path = XP_NEW_CHAT_SEND_BTN
        if driver.find_elements("xpath", send_path + "/div[1]"):
            send_path += "/div[1]"
        
        try:
            driver.click(send_path)
        except:
             # Final fallback: JS click
             btn = driver.find_element("xpath", send_path)
             driver.execute_script("arguments[0].click();", btn)
        
        # Extraction (Chat 0 only - every turn is a New Chat)
        logger.info(f"Waiting for generation for {username} (Text Stabilization)...")
        
        last_text = ""
        stable_count = 0
        final_content = ""
        
        # Wait for text to stop changing for 3 consecutive checks (Real completion)
        for i in range(120): # Up to 120 seconds
            try:
                curr_text = driver.find_element("xpath", XP_THREAD_RESPONSE).text.strip()
                if len(curr_text) > 20: 
                    if curr_text == last_text:
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_text = curr_text
                    
                    if stable_count >= 4: # Stable for ~8 seconds
                        logger.info(f"Generation stabilized for {username}.")
                        final_content = curr_text
                        break
            except: pass
            time.sleep(2)
        
        if not final_content:
             final_content = last_text # Fallback to whatever we have

        try:
            # Use regex to find { ... }
            json_match = re.search(r'(\{.*\})', final_content, re.DOTALL)
            if json_match:
                raw_json = json_match.group(1).replace("```json", "").replace("```", "")
                return json.loads(raw_json)
            else:
                logger.error(f"No JSON found for {username} in Chat 0 response.")
        except Exception as e:
            logger.error(f"Data extraction error for {username}: {e}")
            
        return None

    def run_profiler(self, batch_size=5):
        logger.info("Initializing Account Profiler (Headed Mode for Inspection)...")
        # uC=False is reportedly more stable for authenticated sessions on this site
        driver = Driver(headless=False, user_data_dir=USER_DATA_DIR, uc=False) 
        
        # Load targets
        targets = pd.read_csv(TARGET_CSV).to_dict('records')
        
        # Resume Logic: Skip users already in the output CSV
        completed_users = set()
        if os.path.exists(OUTPUT_CSV):
            try:
                out_df_existing = pd.read_csv(OUTPUT_CSV)
                completed_users = set(out_df_existing['username'].tolist())
                logger.info(f"Resuming: Found {len(completed_users)} users already processed.")
            except: pass

        results = []
        try:
            for i, target in enumerate(targets):
                if i >= batch_size: break
                u = target['username']
                url = target['profile_url']
                
                if u in completed_users:
                    logger.info(f"Skipping {u} (already processed).")
                    continue
                
                logger.info(f"--- Processing {u} ({i+1}/{len(targets)}) ---")
                
                # 1. WikiHow Navigation + PDF Generation
                driver.get(url)
                time.sleep(3)
                
                # CDP Print to PDF (Long Page capture)
                logger.info(f"Generating PDF for {u}...")
                height = driver.execute_script("return document.body.parentNode.scrollHeight")
                paper_height = (height / 96) + 1 # pixels to inches + bleed
                pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
                    'printBackground': True,
                    'paperWidth': 12,
                    'paperHeight': paper_height,
                    'preferCSSPageSize': True
                })
                with open(TEMP_PDF, "wb") as f:
                    f.write(base64.b64decode(pdf_data['data']))
                
                # 2. DeepSeek Inference
                driver.get("https://chat.deepseek.com")
                time.sleep(5)
                # Ensure fresh chat
                driver.get("https://chat.deepseek.com") 
                
                # Retry loop for the entire extraction turn
                profile_data = None
                for attempt in range(2):
                    profile_data = self.extract_from_deepseek(driver, u, TEMP_PDF)
                    if profile_data: break
                    logger.warning(f"Retry {attempt+1}/2 for {u}...")
                    driver.get("https://chat.deepseek.com") # Reset context
                    time.sleep(3)
                
                if profile_data:
                    # Merge with original target data
                    full_record = {**target, **profile_data}
                    full_record['scanned_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Atomic Save with explicit column ordering
                    df = pd.DataFrame([full_record])
                    
                    # Move 'username', 'profile_url', 'scanned_at' to front
                    cols = df.columns.tolist()
                    priority = ['username', 'profile_url', 'scanned_at']
                    # Keep AI fields next
                    ai_cols = sorted([c for c in cols if c.startswith('ai_')])
                    # Remaining
                    other_cols = sorted([c for c in cols if c not in priority and c not in ai_cols])
                    ordered_cols = priority + ai_cols + other_cols
                    
                    out_df = df[ordered_cols]
                    mode = 'a' if os.path.exists(OUTPUT_CSV) else 'w'
                    header = not os.path.exists(OUTPUT_CSV)
                    out_df.to_csv(OUTPUT_CSV, mode=mode, header=header, index=False)
                    
                    logger.info(f"Successfully profiled {u} and SAVED to CSV (Rich Schema).")
                
            logger.info(f"Batch processing complete. Results saved to {OUTPUT_CSV}")
            
        finally:
            driver.quit()

if __name__ == "__main__":
    profiler = AccountProfiler()
    # Processing the entire 50-user veteran batch
    profiler.run_profiler(batch_size=999) 
