import sys
import os
import json
import time
import logging
import urllib.request
import psutil
import socket
import argparse
import platform
import shutil
import subprocess
import asyncio
import websockets
from seleniumbase import Driver
from wikihow_scraper import PROFILES_DIR, LOGS_DIR


def find_chrome_binary():
    """Finds the system Chrome executable across macOS, Linux, and Windows."""
    system = platform.system()
    if system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chrome.app/Contents/MacOS/Chrome",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
    elif system == "Windows":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
    else:  # Linux
        for binary in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
            path = shutil.which(binary)
            if path:
                return path
    return "google-chrome"

class BrowserWatchdog:
    """
    Uniform Browser Watchdog / Self-Healing Monitor
    Launches Chrome using SeleniumBase, tracks status via CDP tab inventory,
    checks for renderer freezes, and recovers crashes automatically.
    """
    def __init__(self, profile_name, port=9099, nav_url=None):
        self.profile_name = profile_name
        self.port = port
        self.nav_url = nav_url
        self.user_data_dir = os.path.join(PROFILES_DIR, profile_name)
        self.tracker_file = os.path.join(PROFILES_DIR, f"{profile_name}_tracker.json")
        self.driver = None
        self.chrome_pid = None
        self.should_cleanup = False
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger(f"Watchdog_{self.profile_name}")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            formatter = logging.Formatter('[PID Tracker] %(asctime)s - %(message)s')
            
            # Log to package logs folder
            log_file = os.path.join(LOGS_DIR, f"watchdog_{self.profile_name}.log")
            fh = logging.FileHandler(log_file, mode="a")
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
            # Log to stdout cleanly (avoiding buffering blockages)
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.INFO)
            sh.setFormatter(formatter)
            self.logger.addHandler(sh)

    def _is_port_in_use(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', self.port)) == 0

    def _get_tabs(self):
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=1.5)
            raw = json.loads(req.read().decode("utf-8"))
            return [{
                "id": t.get("id"),
                "type": t.get("type"),
                "url": t.get("url"),
                "title": t.get("title"),
                "webSocketDebuggerUrl": t.get("webSocketDebuggerUrl")
            } for t in raw]
        except Exception:
            return None

    def _dismiss_any_alert(self, handle):
        """Best-effort: if this window/tab has a blocking native/JS dialog open, accept it."""
        try:
            self.driver.switch_to.window(handle)
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            self.logger.info(f"Dismissed a blocking alert on tab {handle}: {text!r}")
            return True
        except Exception:
            return False

    def _eval_via_cdp(self, ws_url, expression, timeout=3):
        """Runs a JS expression against a specific tab's own WebSocket - does NOT change
        which tab is visibly focused (unlike Selenium's switch_to.window + execute_script)."""
        async def evaluate():
            async with websockets.connect(ws_url, open_timeout=timeout, close_timeout=1) as ws:
                payload = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": expression}}
                await ws.send(json.dumps(payload))
                res = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout))
                if "error" in res:
                    raise RuntimeError(res["error"])
                return res.get("result", {}).get("result", {}).get("value")

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(evaluate())
        finally:
            loop.close()

    def _is_hung(self):
        """
        Health check. Two known failure modes get handled here, both discovered while
        debugging OAuth (Facebook/Google) login popups that kept getting the whole
        browser killed and relaunched (wiping every tab, including in-progress logins)
        even though only one popup tab was ever actually the problem:

        1. Probe a known-safe ANCHOR tab (the first tab from the CDP tab list, normally
           the pre-warmed nav_url tab) rather than whatever tab currently has focus - a
           stuck OAuth tab's own JS context being unresponsive doesn't mean the rest of
           the browser is dead. This is done via a direct WebSocket Runtime.evaluate call
           (like get_tab_html() below), NOT Selenium's switch_to.window()+execute_script -
           the latter visibly brings that tab to the front of the real browser window on
           every single poll (every 5s), which caused a distracting flicker between
           whatever tab the user was actually looking at (e.g. a Facebook 2FA prompt) and
           the anchor tab. The CDP WebSocket route talks to a tab without touching focus.

        2. Before giving up, actively sweep EVERY open tab for a blocking native/JS
           dialog (alert/confirm/prompt, or Chrome's own "Save password?"-style native
           prompt) and dismiss it. In Chromium, an open dialog in ANY tab blocks the
           browser's entire UI message pump, so even an unrelated tab's check can
           genuinely stall browser-wide until that dialog is cleared - this reads exactly
           like "hung" from the outside, but isn't a dead renderer at all, just a modal
           nobody answered. OAuth popups (Google/Facebook) are the most common source of
           these because of the "can't connect" / retry dialogs seen debugging this.
        """
        try:
            if not self.driver:
                return True

            # Fast path, every poll: no Selenium focus-switch, no visible flicker.
            tabs = self._get_tabs()
            if not tabs:
                return True
            anchor = next((t for t in tabs if t.get("webSocketDebuggerUrl")), None)
            if not anchor:
                return True
            try:
                self._eval_via_cdp(anchor["webSocketDebuggerUrl"], "1+1")
                return False  # healthy - never touched tab focus
            except Exception:
                pass  # fall through to the slower diagnostic path below

            # Slow path, only reached when the fast check actually failed: sweep every
            # tab for a blocking dialog via Selenium (which DOES change visible focus
            # per WebDriver's alert-handling spec) and retry once after clearing any.
            handles = self.driver.window_handles
            for h in handles:
                self._dismiss_any_alert(h)
            self._eval_via_cdp(anchor["webSocketDebuggerUrl"], "1+1")
            return False
        except Exception:
            pass
        return True

    def _write_tracker(self, status, tabs=None):
        info = {
            "profile_name": self.profile_name,
            "port": self.port,
            "user_data_dir": self.user_data_dir,
            "chrome_pid": self.chrome_pid,
            "watchdog_pid": os.getpid(),
            "status": status,
            "tabs": tabs or [],
            "last_checked": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(self.tracker_file, "w") as f:
            json.dump(info, f, indent=2)
        return info

    def get_status(self):
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, "r") as f:
                    info = json.load(f)
                pid = info.get("chrome_pid")
                if pid and psutil.pid_exists(pid):
                    tabs = self._get_tabs()
                    if tabs is None:
                        return "HUNG_OR_DEAD", info
                    return "HEALTHY", info
                else:
                    try:
                        os.remove(self.tracker_file)
                    except Exception:
                        pass
            except Exception:
                pass
        return "OFFLINE", None

    def launch_browser(self):
        self.logger.info(f"Launching Chrome on debug port {self.port} with user_data_dir={self.user_data_dir}")
        chrome_binary = find_chrome_binary()
        nav_target = self.nav_url or "https://www.wikihow.com/Main-Page"
        cmd = [
            chrome_binary,
            f"--remote-debugging-port={self.port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={self.user_data_dir}",
            "--lang=en-US",
            "--accept-lang=en-US",
            "--password-store=basic",
            "--use-mock-keychain",
            "--no-first-run",
            "--no-default-browser-check",
            nav_target
        ]
        
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.chrome_pid = proc.pid

        # Poll port until Chrome opens its CDP endpoint (up to 15s)
        connected = False
        for _ in range(15):
            time.sleep(1)
            tabs = self._get_tabs()
            if tabs is not None:
                connected = True
                break

        if not connected or not self.chrome_pid or not psutil.pid_exists(self.chrome_pid):
            self.logger.error("Failed to retrieve a live browser process PID or CDP connection.")
            self.kill_browser()
            raise RuntimeError("Launch did not produce a live browser PID or CDP connection.")

        self.logger.info(f"[OK] Chrome running on port {self.port}, PID={self.chrome_pid}")
        return self.chrome_pid

    def get_tab_html(self, tab_id):
        """Fetches page outer HTML from a specific tab ID directly via its WebSocket (no focus needed)."""
        tabs = self._get_tabs()
        if not tabs:
            return None
        
        target_tab = next((t for t in tabs if t["id"] == tab_id or tab_id in t["url"]), None)
        if not target_tab or not target_tab.get("webSocketDebuggerUrl"):
            return None
            
        async def evaluate():
            async with websockets.connect(target_tab["webSocketDebuggerUrl"]) as ws:
                payload = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "document.documentElement.outerHTML", "returnByValue": True}
                }
                await ws.send(json.dumps(payload))
                res = json.loads(await ws.recv())
                return res.get("result", {}).get("result", {}).get("value")
                
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(evaluate())
        except Exception as e:
            self.logger.error(f"Failed to fetch HTML from tab {tab_id} via WebSocket: {e}")
            return None
        finally:
            loop.close()

    def start_watchdog(self):
        status, info = self.get_status()
        if status in ["HEALTHY", "HUNG_OR_DEAD"]:
            self.logger.error(f"ABORT: Watchdog for profile '{self.profile_name}' is already running (PID: {info['chrome_pid']}).")
            sys.exit(1)

        import atexit
        atexit.register(self.cleanup)

        try:
            self.launch_browser()
            tabs = self._get_tabs() or []
            self._write_tracker("healthy", tabs)
            self.logger.info("[OK] Tracker registered. Watchdog active.")

            # Successfully initialized
            self.should_cleanup = False
            consecutive_hung = 0

            while True:
                time.sleep(5)
                tabs = self._get_tabs()
                dead = tabs is None
                hung = (not dead) and self._is_hung()

                if dead:
                    consecutive_hung = 0  # DEAD is unambiguous (port unreachable) - act immediately
                elif hung:
                    consecutive_hung += 1
                    # A single slow health check is often just a concurrent script (another
                    # attached CDP client mid-interaction, e.g. filling a login form) briefly
                    # busying the renderer - not a real hang. Require 2 consecutive failures
                    # (~5-10s apart) before declaring it dead, to avoid killing (and wiping
                    # every tab of) a browser that was only ever transiently slow.
                    self.logger.info(f"Health check slow/unresponsive ({consecutive_hung}/2) - confirming before relaunch...")
                    if consecutive_hung < 2:
                        self._write_tracker("healthy", tabs or [])
                        continue
                else:
                    consecutive_hung = 0
                    self._write_tracker("healthy", tabs)
                    continue

                consecutive_hung = 0
                reason = "DEAD (Port unreachable)" if dead else "HUNG (Renderer unresponsive, confirmed)"
                self.logger.error(f"Watchdog alert: Browser is {reason}. Relaunching...")
                self._write_tracker("relaunching")
                self.kill_browser()
                
                try:
                    self.launch_browser()
                    tabs = self._get_tabs() or []
                    self._write_tracker("healthy", tabs)
                except Exception as e:
                    self.logger.error(f"Relaunch failed: {e}. Retrying next cycle.")
                    
        except KeyboardInterrupt:
            self.logger.info("Watchdog stopped by user.")
            self.should_cleanup = True
            self.cleanup()
            sys.exit(0)

    def kill_browser(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        if self.chrome_pid and psutil.pid_exists(self.chrome_pid):
            try:
                psutil.Process(self.chrome_pid).kill()
                self.logger.info(f"Terminated browser process PID {self.chrome_pid}")
            except Exception:
                pass

    def stop(self):
        """Gracefully stops the watchdog process and shuts down its browser."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, "r") as f:
                    info = json.load(f)
                
                # Kill watchdog loop first
                watchdog_pid = info.get("watchdog_pid")
                if watchdog_pid and psutil.pid_exists(watchdog_pid) and watchdog_pid != os.getpid():
                    try:
                        psutil.Process(watchdog_pid).kill()
                        self.logger.info(f"Stopped watchdog process PID {watchdog_pid}")
                    except Exception:
                        pass
                
                # Kill browser process next
                chrome_pid = info.get("chrome_pid")
                if chrome_pid and psutil.pid_exists(chrome_pid):
                    try:
                        psutil.Process(chrome_pid).kill()
                        self.logger.info(f"Terminated browser process PID {chrome_pid}")
                    except Exception:
                        pass
                
                # Remove tracker file
                os.remove(self.tracker_file)
                print(f"Watchdog for profile '{self.profile_name}' stopped successfully.")
                return
            except Exception as e:
                print(f"Error stopping watchdog: {e}")
        print(f"No active watchdog found for profile '{self.profile_name}'.")

    def cleanup(self):
        if not self.should_cleanup:
            return
        self.logger.info("Triggering exit cleanup...")
        self.kill_browser()
        if os.path.exists(self.tracker_file):
            try:
                os.remove(self.tracker_file)
            except Exception:
                pass
        self.logger.info("Cleaned up locks and finished shutdown.")

def status_check():
    """Verify all status trackers and print their states."""
    print("\n--- Current Browser Process Status ---")
    files = [f for f in os.listdir(PROFILES_DIR) if f.endswith("_tracker.json")]
    if not files:
        print("No active processes tracked.")
        print("--------------------------------------\n")
        return
        
    for file in files:
        path = os.path.join(PROFILES_DIR, file)
        try:
            with open(path, "r") as f:
                info = json.load(f)
            pid = info.get("chrome_pid")
            prof = info.get("profile_name")
            port = info.get("port")
            status = "OFFLINE"
            if pid and psutil.pid_exists(pid):
                status = "HEALTHY"
            print(f"[{status}] Profile: {prof} (PID: {pid}) - Debug Port: {port}")
        except Exception as e:
            print(f"[ERROR] Reading tracker {file}: {e}")
    print("--------------------------------------\n")

def sweep():
    """Kill all tracked Chrome instances and delete the lock files."""
    print("Performing global cleanup of all tracked watchdogs...")
    files = [f for f in os.listdir(PROFILES_DIR) if f.endswith("_tracker.json")]
    for file in files:
        path = os.path.join(PROFILES_DIR, file)
        try:
            with open(path, "r") as f:
                info = json.load(f)
            
            # Kill watchdog first
            wpid = info.get("watchdog_pid")
            if wpid and psutil.pid_exists(wpid):
                psutil.Process(wpid).kill()
                
            # Kill browser second
            pid = info.get("chrome_pid")
            if pid and psutil.pid_exists(pid):
                psutil.Process(pid).kill()
                print(f"Terminated Chrome process PID {pid}")
            os.remove(path)
        except Exception as e:
            print(f"Failed to clean up tracker {file}: {e}")
    print("Sweep complete. All status registrations cleared.")

def main():
    parser = argparse.ArgumentParser(description="Standalone watchdog launcher & PID controller")
    parser.add_argument("action", choices=["start", "status", "sweep", "stop"])
    parser.add_argument("profile_name", nargs="?", help="Chrome profile name (required for start/stop)")
    parser.add_argument("--port", type=int, default=9099, help="CDP debug port")
    parser.add_argument("--nav", help="Optional URL to pre-warm navigate to")
    
    args = parser.parse_args()
    
    if args.action == "start":
        if not args.profile_name:
            print("Error: profile_name is required for start.")
            sys.exit(1)
        watchdog = BrowserWatchdog(args.profile_name, port=args.port, nav_url=args.nav)
        watchdog.start_watchdog()
    elif args.action == "stop":
        if not args.profile_name:
            print("Error: profile_name is required for stop.")
            sys.exit(1)
        watchdog = BrowserWatchdog(args.profile_name, port=args.port)
        watchdog.stop()
    elif args.action == "status":
        status_check()
    elif args.action == "sweep":
        sweep()

if __name__ == "__main__":
    main()
