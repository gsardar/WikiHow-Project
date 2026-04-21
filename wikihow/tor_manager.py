import time
import os
import subprocess
import requests
from stem import Signal
from stem.control import Controller

# Project Paths
BASE_DIR = r"C:\Users\Admin\Documents\WikiHow Project"
TOR_EXE = r"C:\Users\Admin\Desktop\Portable\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
TOR_BROWSER_EXE = r"C:\Users\Admin\Desktop\Portable\Tor Browser\Browser\firefox.exe"
TORRC_CUSTOM = os.path.join(BASE_DIR, "tool", "torrc.custom")

class TorManager:
    """
    Centralized service for managing Tor connectivity, IP rotation, 
    and proxy configuration for the WikiHow project.
    Supports automated bridge-bypass for high-security networks.
    """
    def __init__(self):
        self.proxy_port = None
        self.control_port = None
        self.active_ip = None
        self.is_connected = False
        self._process = None
        self._detect_ports()

    def _detect_ports(self):
        """Probes standard Tor ports to find an active service."""
        port_pairs = [(9050, 15000), (9050, 9051), (9150, 9151)]
        for p_port, c_port in port_pairs:
            try:
                proxies = {'http': f'socks5h://127.0.0.1:{p_port}', 'https': f'socks5h://127.0.0.1:{p_port}'}
                r = requests.get("https://api.ipify.org", proxies=proxies, timeout=5)
                if r.status_code == 200:
                    self.proxy_port = p_port
                    self.control_port = c_port
                    self.active_ip = r.text.strip()
                    self.is_connected = True
                    return
            except:
                continue
        self.is_connected = False

    def get_status(self):
        """Returns a detailed status dictionary of the Tor service."""
        self._detect_ports()
        return {
            "status": "CALIBRATED" if self.is_connected else "OFFLINE",
            "proxy_port": self.proxy_port,
            "control_port": self.control_port,
            "current_ip": self.active_ip,
            "mode": "Browser" if self.proxy_port == 9150 else "System Service" if self.proxy_port == 9050 else "None"
        }

    def connect(self):
        """
        Launches tor.exe headlessly using Tor Browser's binaries.
        No browser window is shown. Port 9050/9051 used (not 9150/9151).
        """
        self._detect_ports()
        if self.is_connected:
            print(f"[TOR] Already connected on port {self.proxy_port}. IP: {self.active_ip}")
            return True

        TOR_EXE_PATH   = r"C:\Users\Admin\Desktop\Portable\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
        TORRC_HEADLESS = os.path.join(BASE_DIR, "tool", "torrc.headless")
        os.makedirs(os.path.join(BASE_DIR, "tool", "tor_data", "headless"), exist_ok=True)

        # Kill any stale tor process
        subprocess.call("taskkill /f /im tor.exe", shell=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)

        print("[TOR] Starting headless Tor (no browser window)...")
        try:
            self._process = subprocess.Popen(
                [TOR_EXE_PATH, "-f", TORRC_HEADLESS],
                creationflags=0x08000000,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"[TOR] Headless launch failed: {e}")
            return False

        print("[TOR] Bootstrapping", end="", flush=True)
        for _ in range(30):
            time.sleep(3)
            self._detect_ports()
            if self.is_connected:
                print(f"\n[TOR] SUCCESS: Headless Tor connected. IP: {self.active_ip}")
                return True
            print(".", end="", flush=True)

        print("\n[TOR] FAILED: Bootstrap timed out.")
        return False

    def rotate_ip(self):
        """Signals Tor for a New Identity (Fresh IP)."""
        if not self.is_connected:
            return False, "Tor is not connected."
        # Try headless control port first, then Tor Browser port
        for port in [9051, 9151]:
            try:
                with Controller.from_port(port=port) as controller:
                    controller.authenticate()
                    controller.signal(Signal.NEWNYM)
                    time.sleep(5)
                    self._detect_ports()
                    return True, f"Identity Rotated. New IP: {self.active_ip}"
            except Exception:
                continue
        return False, "Could not connect to Tor control port (tried 9051, 9151)."

    def get_selenium_proxy(self):
        if not self.is_connected: return None
        return f"socks5://127.0.0.1:{self.proxy_port}"

    def get_requests_proxies(self):
        if not self.is_connected: return None
        return {
            'http': f'socks5h://127.0.0.1:{self.proxy_port}',
            'https': f'socks5h://127.0.0.1:{self.proxy_port}'
        }

tor = TorManager()
