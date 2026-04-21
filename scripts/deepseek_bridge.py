"""
DeepSeek Universal Bridge Server (v3.1 - Deterministic Context Hub)
Drives a single Selenium instance with adaptive XPaths and Window Tagging for focus.
"""

import sys
import os
import json
import time
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Local imports
try:
    from process_manager import cleanup_pids, track_active_driver
except ImportError:
    from scripts.process_manager import cleanup_pids, track_active_driver

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from seleniumbase import Driver

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    handlers=[logging.FileHandler("data/deepseek_bridge.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Config
USER_DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "browser_session")
SESSION_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "session_config.json")
DEEPSEEK_ROOT  = "https://chat.deepseek.com"
PORT           = 8002

_driver    = None
_lock      = threading.Lock()
_chat_url  = None
_contexts  = {"wikihow": "CONTEXT_WIKIHOW", "deepseek": "CONTEXT_DEEPSEEK"}

# ─── DOM FINGERPRINTS (Updated per deepseek fix.txt) ──────────────────────────
XP_NEW_CHAT_TEXTAREA       = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/textarea"
XP_NEW_CHAT_SEND_BTN       = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[2]/div"
XP_NEW_CHAT_UPLOAD_BTN     = "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div[1]"
XP_THREAD_RESPONSE         = "/html/body/div[1]/div/div/div[2]/div[3]/div/div[3]/div[1]/div/div[2]/div[1]"

DISABLED_CLASS = "ds-icon-button--disabled"

def _load_chat_url() -> str:
    global _chat_url
    if _chat_url: return _chat_url
    if os.path.exists(SESSION_CONFIG):
        try:
            with open(SESSION_CONFIG) as f:
                config = json.load(f)
            saved = config.get("deepseek_chat_url", "")
            if saved and saved.startswith("https://chat.deepseek.com"):
                _chat_url = saved
                return _chat_url
        except: pass
    _chat_url = DEEPSEEK_ROOT
    return _chat_url

def _tag_current_handle(name: str):
    driver = get_driver()
    logger.info(f"Tagging current window handle as '{name}'...")
    driver.execute_script(f"window.name = '{name}';")

def _find_and_tag_by_url():
    """Scans all handles to find and tag WikiHow/DeepSeek if they already exist."""
    driver = get_driver()
    handles = driver.window_handles
    found = {"wikihow": False, "deepseek": False}
    for handle in handles:
        try:
            driver.switch_to.window(handle)
            url = driver.current_url.lower()
            if "wikihow.com" in url and not found["wikihow"]:
                _tag_current_handle(_contexts["wikihow"])
                found["wikihow"] = True
            elif "deepseek.com" in url and not found["deepseek"]:
                _tag_current_handle(_contexts["deepseek"])
                found["deepseek"] = True
        except: pass
    return found

def ensure_context(purpose: str):
    """Guarantees focus on the named context, re-tagging or re-opening as needed."""
    driver = get_driver()
    tag = _contexts.get(purpose)
    
    # 1. Try to switch by Name (Deterministic)
    try:
        driver.switch_to.window(tag)
        return
    except:
        pass
    
    # 2. If name switch failed, perform full scan and registry sync
    logger.info(f"Context: {purpose} (STALE/MISSING) -> Performing recovery scan...")
    status = _find_and_tag_by_url()
    
    # 3. If still missing, ONLY THEN re-open
    if not status.get(purpose):
        logger.info(f"Context: {purpose} (NOT FOUND) -> Spawning new window...")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        if purpose == "wikihow": driver.get("https://www.wikihow.com")
        else: driver.get(_load_chat_url())
        _tag_current_handle(tag)
    else:
        # Switch to the one we just tagged
        driver.switch_to.window(tag)

def get_driver():
    global _driver
    if _driver is None:
        logger.info("Initializing Deterministic Context Hub...")
        cleanup_pids()
        # uC=False is more stable for authenticated browser sessions on DeepSeek
        _driver = Driver(uc=False, headless=False, user_data_dir=USER_DATA_DIR)
        
        # Open and tag contexts immediately to prevent future phantom windows
        _driver.get(_load_chat_url())
        _tag_current_handle(_contexts["deepseek"])
        
        _driver.execute_script("window.open('https://www.wikihow.com', '_blank');")
        _driver.switch_to.window(_driver.window_handles[-1])
        _tag_current_handle(_contexts["wikihow"])
        
        # Land back on DeepSeek
        _driver.switch_to.window(_contexts["deepseek"])
    return _driver

def _get_adaptive_paths():
    """Placeholder for legacy compatibility, now pointing to robust Turn 0 paths."""
    return {
        "textarea": XP_NEW_CHAT_TEXTAREA,
        "send_btn": XP_NEW_CHAT_SEND_BTN,
        "file_in": "//input[@type='file']",
        "upload_btn": XP_NEW_CHAT_UPLOAD_BTN
    }

def send_prompt(prompt: str, file_path: str = None) -> str:
    ensure_context("deepseek")
    driver = get_driver()
    try:
        paths = _get_adaptive_paths()
        
        # 1. Reset to New Chat for every 'ask' to ensure Turn 0 stability as requested
        driver.get(DEEPSEEK_ROOT)
        time.sleep(5)
        
        # 2. Upload
        if file_path and os.path.exists(file_path):
            abs_path = os.path.abspath(file_path)
            logger.info(f"Hub: Uploading file {abs_path}...")
            try:
                driver.find_element("css selector", paths["file_in"]).send_keys(abs_path)
            except:
                driver.find_element("xpath", paths["upload_btn"]).send_keys(abs_path)
            
            # Handshake: Wait for Send button to enable (STRICT)
            logger.info("Hub: Waiting for parsing (STRICT handshake)...")
            time.sleep(3)
            for _ in range(90):
                # Error Check
                status_elements = driver.find_elements("xpath", "/html/body/div[1]/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]")
                if status_elements:
                    text = status_elements[0].text.lower()
                    if "no text extracted" in text:
                        logger.error("Hub: DeepSeek ERROR - No text extracted.")
                        return "ERROR: DeepSeek failed to extract text from file."

                # Preparation Check
                btn = driver.find_element("xpath", paths["send_btn"])
                if DISABLED_CLASS not in (btn.get_attribute("class") or ""):
                    logger.info("Hub: Handshake COMPLETE (Send button enabled).")
                    time.sleep(2) # Buffer for React
                    break
                time.sleep(1)
        
        # 3. Inject Prompt via React-safe JS
        logger.info("Hub: Injecting prompt...")
        textarea = driver.find_element("xpath", paths["textarea"])
        inject_script = """
        const el = arguments[0];
        const val = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(el, val);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        """
        driver.execute_script(inject_script, textarea, prompt)
        time.sleep(1)
        
        # 4. Dispatch
        send_path = paths["send_btn"]
        if driver.find_elements("xpath", send_path + "/div[1]"): send_path += "/div[1]"
        
        try:
            driver.click(send_path)
        except:
             # Final fallback: JS click
             btn = driver.find_element("xpath", send_path)
             driver.execute_script("arguments[0].click();", btn)
        
        logger.info("Hub: Message DISPATCHED. Waiting for generation...")
        
        # 5. Extract (Poll for completion via stabilization)
        logger.info("Hub: Waiting for generation stabilization...")
        last_text = ""
        stable_count = 0
        final_content = ""
        
        for turn_wait in range(120):
            try:
                curr = driver.find_element("xpath", XP_THREAD_RESPONSE).text.strip()
                if len(curr) > 20:
                    if curr == last_text: stable_count += 1
                    else: stable_count = 0; last_text = curr
                    
                    if stable_count >= 4:
                        logger.info("Hub: Generation stabilized.")
                        final_content = curr
                        break
            except: pass
            time.sleep(2)
            
        return final_content if final_content else last_text
        
    except Exception as e:
        logger.error(f"Hub Failure: {e}")
        return f"ERROR: {e}"

class BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): logger.info(f"HTTP: {format % args}")
    def _send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/status": self._send_json(200, {"status": "running"})
        else: self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        payload = json.loads(body) if body else {}
        
        try:
            if self.path == "/navigate":
                url = payload.get("url")
                with _lock:
                    ensure_context("wikihow")
                    get_driver().get(url)
                self._send_json(200, {"status": "ok"})
            elif self.path == "/screenshot":
                path = payload.get("path")
                ensure_context("wikihow")
                driver = get_driver()
                os.makedirs(os.path.dirname(path), exist_ok=True)
                orig = driver.get_window_size()
                w = driver.execute_script("return document.body.parentNode.scrollWidth")
                h = driver.execute_script("return document.body.parentNode.scrollHeight")
                driver.set_window_size(w, h)
                time.sleep(1)
                driver.save_screenshot(path)
                driver.set_window_size(orig['width'], orig['height'])
                self._send_json(200, {"status": "ok"})
            elif self.path == "/ask":
                prompt = payload.get("prompt")
                file_p = payload.get("file_path")
                with _lock: res = send_prompt(prompt, file_p)
                self._send_json(200, {"response": res})
            elif self.path == "/new_chat":
                with _lock:
                    ensure_context("deepseek")
                    get_driver().get(DEEPSEEK_ROOT)
                self._send_json(200, {"status": "ok"})
            else: self._send_json(404, {"error": "Endpoint Not Found"})
        except Exception as e:
            import traceback
            logger.error(f"Hub 500 Error: {e}")
            logger.error(traceback.format_exc())
            self._send_json(500, {"error": str(e), "traceback": traceback.format_exc()})

def main():
    get_driver()
    server = HTTPServer(("127.0.0.1", PORT), BridgeHandler)
    logger.info(f"Hub Server Active at http://127.0.0.1:{PORT}")
    try: server.serve_forever()
    except: pass
    finally:
        if _driver: _driver.quit()

if __name__ == "__main__":
    main()
