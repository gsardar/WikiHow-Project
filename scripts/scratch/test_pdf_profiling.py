import os
import time
import base64
import logging
from seleniumbase import Driver

# --- CONFIG ---
WORKSPACE_DIR = r"f:\Users\Admin\Documents\WikiHow Project"
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, "data", "browser_session")
TARGET_URL = "https://www.wikihow.com/User:Zack"
TEMP_PDF = os.path.join(WORKSPACE_DIR, "data", "zack_profile.pdf")
PROMPT_FILE = os.path.join(WORKSPACE_DIR, "instruct", "profiler_prompt.txt")

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger(__name__)

# Xpaths
XP_TEXTAREA = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/textarea"
XP_SEND_BTN = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[2]/div"
XP_STATUS = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]"
XP_END = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[3]/div[1]/div[5]"

def generate_pdf(driver, output_path):
    logger.info(f"Generating PDF for {driver.current_url}...")
    # Get scroll height
    height = driver.execute_script("return document.body.parentNode.scrollHeight")
    # A bit of logic to convert pixels to inches for CDP (96 dpi)
    paper_height = (height / 96) + 1 # Add some buffer
    
    # CDP Print to PDF
    pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
        'printBackground': True,
        'paperWidth': 12, # Wide enough for WikiHow desktop
        'paperHeight': paper_height,
        'preferCSSPageSize': True
    })
    
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(pdf_data['data']))
    logger.info(f"PDF saved to {output_path}")

def wait_for_parsing(driver):
    logger.info("Waiting for PDF parsing (STRICT handshake)...")
    time.sleep(3) # Initial wait for upload to register
    for _ in range(90): # Longer timeout for PDFs
        try:
            # 1. Physical Presence Check (Fail if error text found)
            status_elements = driver.find_elements("xpath", XP_STATUS)
            if status_elements:
                text = status_elements[0].text.lower()
                if "no text extracted" in text:
                    logger.error("DeepSeek ERROR: No text extracted from PDF.")
                    return False
            
            # 2. GROUND TRUTH: Send button must be ENABLED
            send_btn = driver.find_element("xpath", XP_SEND_BTN)
            classes = send_btn.get_attribute("class") or ""
            
            # If the button is found and does NOT have the disabled class, we are ready
            if "ds-icon-button--disabled" not in classes:
                logger.info("Handshake COMPLETE: Send button is enabled.")
                time.sleep(2) # Safety buffer for React
                return True
                
        except: pass
        time.sleep(1)
    return False

def test_zack_pdf():
    with open(PROMPT_FILE, "r") as f:
        master_prompt = f.read().replace("{u}", "Zack")

    driver = Driver(headless=False, uc=False, user_data_dir=USER_DATA_DIR)
    try:
        # Step 1: Browse WikiHow
        driver.get(TARGET_URL)
        time.sleep(3)
        generate_pdf(driver, TEMP_PDF)
        
        # Step 2: Switch to DeepSeek
        driver.get("https://chat.deepseek.com")
        time.sleep(5)
        
        # Start new chat (Refresh to be safe)
        driver.get("https://chat.deepseek.com")
        time.sleep(3)
        
        # Step 3: Upload PDF
        logger.info("Uploading PDF...")
        file_input = driver.find_element("css selector", "input[type='file']")
        file_input.send_keys(os.path.abspath(TEMP_PDF))
        
        # Step 4: Handshake
        if not wait_for_parsing(driver):
             logger.error("Parsing failed or timed out.")
             return
        
        # Step 5: Inject Prompt
        logger.info("Injecting prompt...")
        textarea = driver.find_element("xpath", XP_TEXTAREA)
        inject_script = """
        const el = arguments[0];
        const val = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(el, val);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        """
        driver.execute_script(inject_script, textarea, master_prompt)
        time.sleep(2)
        
        # Step 6: Send
        send_path = XP_SEND_BTN
        if driver.find_elements("xpath", send_path + "/div[1]"):
            send_path += "/div[1]"
        driver.click(send_path)
        
        # Step 7: Wait for Completion
        logger.info("Waiting for generation...")
        for _ in range(120):
            if driver.find_elements("xpath", XP_END):
                logger.info("Generation finished.")
                break
            time.sleep(2)
        
        time.sleep(10) # Delay to view result
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_zack_pdf()
