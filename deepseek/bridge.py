"""
DeepSeek Bare Bridge (v1.1 - Premium Minimal Hub)
Dedicated ONLY to DeepSeek Chat Automation.
"""

import os
import json
import time
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from seleniumbase import Driver
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.logging import RichHandler

# Config
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_DATA_DIR = os.path.join(ROOT_DIR, "data", "browser_session")
DEEPSEEK_ROOT = "https://chat.deepseek.com"
PORT = 8002

# Configuration Loaders
SELECTORS_FILE = os.path.join(os.path.dirname(__file__), "selectors.json")

def load_config():
    try:
        with open(SELECTORS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load selectors: {e}")
        return {
            "SEL_TEXTAREA": "textarea#chat-input",
            "SEL_SEND_BTN": "div[role='button']",
            "SEL_RESPONSE": "div.ds-markdown--block",
            "DISABLED_CLASS": "ds-icon-button--disabled"
        }

_driver = None
_lock = threading.Lock()

# Premium Console Setup
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, show_time=True, show_path=False)]
)
logger = logging.getLogger("bridge")

def get_driver():
    global _driver
    if _driver is None:
        with console.status("[bold blue]Initializing browser engine...", spinner="dots"):
            _driver = Driver(uc=False, headless=False, user_data_dir=USER_DATA_DIR)
            _driver.get(DEEPSEEK_ROOT)
    return _driver

def send_prompt(prompt: str, file_path: str = None) -> str:
    config = load_config()
    driver = get_driver()
    try:
        # Start fresh for stability
        driver.get(DEEPSEEK_ROOT)
        time.sleep(4)
        
        # 1. Handle File Upload
        if file_path and os.path.exists(file_path):
            abs_path = os.path.abspath(file_path)
            logger.info(f"File uploaded: {os.path.basename(abs_path)}")
            driver.find_element("css selector", "input[type='file']").send_keys(abs_path)
            time.sleep(3)
            with console.status("[blue]DeepSeek parsing file...", spinner="arc"):
                for _ in range(60):
                    btn = driver.find_element("css selector", config["SEL_SEND_BTN"])
                    if config["DISABLED_CLASS"] not in (btn.get_attribute("class") or ""):
                        break
                    time.sleep(1)
        
        # 2. Inject Prompt
        textarea = driver.find_element("css selector", config["SEL_TEXTAREA"])
        inject_script = """
        const el = arguments[0];
        const val = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(el, val);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        """
        driver.execute_script(inject_script, textarea, prompt)
        time.sleep(1)
        
        # 3. Click Send
        btn = driver.find_element("css selector", config["SEL_SEND_BTN"])
        driver.execute_script("arguments[0].click();", btn)
        
        # 4. Wait for response
        logger.info("DeepSeek generating response...")
        last_text = ""
        stable_count = 0
        
        with console.status("[bold green]DeepSeek is thinking...", spinner="simpleDots"):
            for _ in range(120):
                try:
                    # Get all response blocks and take the latest one
                    elements = driver.find_elements("css selector", config["SEL_RESPONSE"])
                    if elements:
                        curr = elements[-1].text.strip()
                        if len(curr) > 10:
                            if curr == last_text: stable_count += 1
                            else: stable_count = 0; last_text = curr
                            if stable_count >= 4: return curr
                except: pass
                time.sleep(2)
        return last_text
    except Exception as e:
        logger.error(f"Bridge error: {e}")
        return f"ERROR: {e}"

class BridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to use professional logger instead of standard stderr
        logger.info(f"Request: {self.path}")

    def _send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        if self.path == "/ask":
            with _lock: res = send_prompt(payload.get("prompt"), payload.get("file_path"))
            self._send_json(200, {"response": res})
        elif self.path == "/new":
            with _lock: get_driver().get(DEEPSEEK_ROOT)
            self._send_json(200, {"status": "ok"})
        elif self.path == "/inspect":
            # Experimental Mid-Run Recorder
            with _lock:
                driver = get_driver()
                logger.info("Starting Inspector Mode...")
                script = """
                const findSelector = (el) => {
                  if (el.id) return '#' + el.id;
                  if (el.className) return '.' + el.className.split(' ').join('.');
                  return el.tagName.toLowerCase();
                };
                window.onclick = (e) => {
                  const sel = findSelector(e.target);
                  console.log('RECORDED_SELECTOR:', sel);
                  alert('Selector: ' + sel);
                  window.onclick = null;
                };
                """
                driver.execute_script(script)
            self._send_json(200, {"status": "recording_started", "info": "Click an element in the browser to see its selector."})
        else: self._send_json(404, {"error": "Not Found"})

def main():
    console.print(Panel(
        "[bold blue]DeepSeek Automation Hub[/bold blue]\n"
        "[dim]Status: Listening on http://127.0.0.1:8002[/dim]",
        border_style="blue",
        title="[bold white]Bridge Server v1.1[/bold white]"
    ))
    get_driver()
    server = HTTPServer(("127.0.0.1", 8002), BridgeHandler)
    try: server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[dim]Shutting down bridge...[/dim]")
    finally:
        if _driver: _driver.quit()

if __name__ == "__main__":
    main()
