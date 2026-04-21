import os
import time
import logging
from seleniumbase import Driver

# --- CONFIG ---
WORKSPACE_DIR = r"f:\Users\Admin\Documents\WikiHow Project"
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "browser_session")
TEST_IMAGE = os.path.join(WORKSPACE_DIR, "data", "Sophia_B.png")

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger(__name__)

# --- XPATHS FROM USER ---
# Upload Button
XPATH_UPLOAD_BTN = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div[1]"

# Status (1 file)
XPATH_STATUS = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]"

# Textbox
XPATH_TEXTAREA_EMPTY = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div/div[1]/textarea"
XPATH_TEXTAREA_FILE = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/textarea"

# Send Button
XPATH_SEND_BTN_FILE_TEXT = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[2]/div"

def run_test():
    logger.info("Starting DeepSeek XPath Test...")
    
    # We use UC=False because the user said they are logged in and we want to use the session.
    # UC=True often triggers challenges even if logged in. 
    # But since the user used Driver(uc=False) in their bridge, we follow that.
    driver = Driver(uc=False, headless=False, user_data_dir=USER_DATA_DIR)
    
    try:
        logger.info("Navigating to DeepSeek...")
        driver.get("https://chat.deepseek.com")
        time.sleep(5)
        
        # 1. Verify we are logged in (look for new chat or textarea)
        if not driver.find_elements("xpath", XPATH_TEXTAREA_EMPTY):
            logger.warning("Main textarea not found. You might need to log in or solve a captcha.")
            input("Please ensure you are at the chat screen, then press Enter here...")
        
        # 2. Upload File
        logger.info(f"Uploading file: {TEST_IMAGE}")
        # We find the file input (usually hidden near the upload button)
        # The user provided the XPath for the button, but we need the input for send_keys
        # Usually it's //input[@type='file']
        try:
            file_input = driver.find_element("css selector", "input[type='file']")
            file_input.send_keys(os.path.abspath(TEST_IMAGE))
        except:
            logger.info("Falling back to finding upload button and sending keys there...")
            driver.find_element("xpath", XPATH_UPLOAD_BTN).send_keys(os.path.abspath(TEST_IMAGE))

        # 3. Wait for Parsing
        logger.info("Waiting for 'parsing' status...")
        parsing_started = False
        for _ in range(30):
            try:
                status_el = driver.find_element("xpath", XPATH_STATUS)
                status_text = status_el.text.lower()
                logger.debug(f"Current status: {status_text}")
                if "parsing" in status_text:
                    logger.info("Detected 'parsing' state.")
                    parsing_started = True
                    break
            except: pass
            time.sleep(1)
        
        if parsing_started:
            logger.info("Waiting for parsing to finish...")
            for _ in range(60):
                try:
                    status_el = driver.find_element("xpath", XPATH_STATUS)
                    status_text = status_el.text.lower()
                    if "parsing" not in status_text and len(status_text) > 2:
                        logger.info(f"Parsing complete. New status: {status_text}")
                        break
                except:
                    logger.info("Status element disappeared - parsing likely finished.")
                    break
                time.sleep(1)
        else:
            logger.warning("Never detected 'parsing' state. Proceeding anyway...")

        # 4. Type Question
        logger.info("Typing question...")
        # Use the 'file uploaded' version of the textarea
        driver.type(XPATH_TEXTAREA_FILE, "what is her gender?")
        time.sleep(2)
        
        # 5. Click Send
        logger.info("Clicking send...")
        driver.click(XPATH_SEND_BTN_FILE_TEXT)
        
        # 6. Wait for Completion
        logger.info("Waiting for generation to complete...")
        XPATH_COMPLETION_INDICATOR = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[3]/div[1]/div[5]"
        XPATH_RESPONSE_CONTENT = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[1]"
        
        generation_finished = False
        for _ in range(120): # Wait up to 2 minutes
            try:
                if driver.find_elements("xpath", XPATH_COMPLETION_INDICATOR):
                    logger.info("Generation finished (indicator found).")
                    generation_finished = True
                    break
            except: pass
            time.sleep(2)
        
        if generation_finished:
            try:
                response_el = driver.find_element("xpath", XPATH_RESPONSE_CONTENT)
                response_text = response_el.text
                logger.info("--- RESPONSE START ---")
                print(response_text)
                logger.info("--- RESPONSE END ---")
            except Exception as e:
                logger.error(f"Failed to extract response content: {e}")
        else:
            logger.warning("Generation timed out or completion indicator not found.")

        # 7. CHAT 1: Send a follow-up
        logger.info("Starting Chat 1 (follow-up) test...")
        XPATH_TEXTAREA_CHAT1_NO_FILE = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[2]/div[2]/div/div/div[1]/textarea"
        XPATH_SEND_BTN_CHAT1 = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[2]/div[2]/div/div/div[2]/div[3]/div[2]/div"
        # Since we aren't uploading a file for the follow-up in this test, we use the 'NO FILE' version.
        
        logger.info("Typing follow-up question...")
        driver.type(XPATH_TEXTAREA_CHAT1_NO_FILE, "Are you sure? Review the username carefully.")
        time.sleep(2)
        
        logger.info("Clicking send (Chat 1)...")
        driver.click(XPATH_SEND_BTN_CHAT1)
        
        # 8. Wait for Completion (Chat 1)
        logger.info("Waiting for Chat 1 generation to complete...")
        XPATH_COMPLETION_INDICATOR_CHAT1 = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[4]/div[3]/div[1]/div[5]"
        XPATH_RESPONSE_CONTENT_CHAT1 = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[4]/div[1]"
        
        generation_finished_chat1 = False
        for _ in range(120):
            try:
                if driver.find_elements("xpath", XPATH_COMPLETION_INDICATOR_CHAT1):
                    logger.info("Chat 1 Generation finished.")
                    generation_finished_chat1 = True
                    break
            except: pass
            time.sleep(2)
        
        if generation_finished_chat1:
            try:
                response_el = driver.find_element("xpath", XPATH_RESPONSE_CONTENT_CHAT1)
                logger.info("--- CHAT 1 RESPONSE START ---")
                print(response_el.text)
                logger.info("--- CHAT 1 RESPONSE END ---")
            except Exception as e:
                logger.error(f"Failed to extract Chat 1 response: {e}")
                
        # Take final screenshot
        res_path = os.path.join(WORKSPACE_DIR, "data", "test_result_thread.png")
        driver.save_screenshot(res_path)
        logger.info(f"Screenshot saved to {res_path}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    run_test()
