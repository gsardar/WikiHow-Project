import subprocess
import time
import os
import socket
import logging
import signal
import sys

# Configuration
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tool", "tor-ip-changer")
TOR_EXE = os.path.join(BASE_DIR, "tor", "tor.exe")
OBFS4_EXE = os.path.join(BASE_DIR, "tor", "obfs4proxy.exe")
BRIDGES_FILE = os.path.join(BASE_DIR, "tor", "bridges.txt")
DATA_DIR = os.path.join(BASE_DIR, "Data", "tor_service")
LOG_FILE = os.path.join(DATA_DIR, "service.log")
TOR_LOG = os.path.join(DATA_DIR, "tor.log")
TORRC_PATH = os.path.join(DATA_DIR, "torrc")

SOCKS_PORT = 9050
CONTROL_PORT = 15000
USE_BRIDGES = False # Set to True if in a restrictive network

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

import threading

class TorService:
    def __init__(self, interval=0):
        self.process = None
        self.interval = interval
        self.stop_event = threading.Event()

    def generate_torrc(self):
        logging.info(f"Generating torrc at {TORRC_PATH}")
        lines = [
            f"SocksPort {SOCKS_PORT}",
            f"ControlPort {CONTROL_PORT}",
            f"DataDirectory {DATA_DIR}",
            f"Log notice file {TOR_LOG}",
            f"GeoIPFile {os.path.join(BASE_DIR, 'tor', 'geoip')}",
            f"GeoIPv6File {os.path.join(BASE_DIR, 'tor', 'geoip6')}",
        ]

        if USE_BRIDGES and os.path.exists(BRIDGES_FILE):
            logging.info("Adding bridges and PT configuration to torrc.")
            # Use double backslashes for Windows paths in torrc
            pt_path = OBFS4_EXE.replace("\\", "\\\\")
            lines.append(f"ClientTransportPlugin obfs4 exec \"{pt_path}\"")
            lines.append("UseBridges 1")
            with open(BRIDGES_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("obfs4 "):
                        lines.append(f"Bridge {line}")
        else:
            logging.warning("Bridges file not found. Tor will attempt direct connection.")

        with open(TORRC_PATH, "w") as f:
            f.write("\n".join(lines))
        return TORRC_PATH

    def start(self):
        if self.is_running():
            logging.info("Tor service is already running.")
            return

        logging.info("Starting Tor service...")
        self.generate_torrc()

        cmd = [
            TOR_EXE,
            "-f", TORRC_PATH
        ]

        # Start process as detached on Windows
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Save PID
        with open(os.path.join(DATA_DIR, "tor.pid"), "w") as f:
            f.write(str(self.process.pid))
            
        logging.info(f"Tor started with PID {self.process.pid}. Socks: {SOCKS_PORT}, Control: {CONTROL_PORT}")

        # Start auto-rotator if interval is set
        if self.interval > 0:
            threading.Thread(target=self._auto_rotate_loop, daemon=True).start()
            logging.info(f"Auto-rotation enabled every {self.interval} seconds.")

    def _auto_rotate_loop(self):
        while not self.stop_event.is_set():
            time.sleep(self.interval)
            logging.info("Auto-rotation triggered by interval.")
            self.rotate()

    def stop(self):
        self.stop_event.set()
        pid_file = os.path.join(DATA_DIR, "tor.pid")
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                pid = int(f.read())
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True)
                else:
                    os.kill(pid, signal.SIGTERM)
                logging.info(f"Stopped Tor process {pid}.")
            except Exception:
                logging.info("Process already stopped.")
            os.remove(pid_file)
        
        # Also stop any manager processes if running
        manager_pid_file = os.path.join(DATA_DIR, "manager.pid")
        if os.path.exists(manager_pid_file):
            with open(manager_pid_file, "r") as f:
                mpid = int(f.read())
            try:
                if os.name == 'nt':
                     subprocess.run(['taskkill', '/F', '/T', '/PID', str(mpid)], capture_output=True)
            except: pass
            os.remove(manager_pid_file)

    def verify(self):
        logging.info("Verifying Tor connectivity...")
        proxies = {
            'http': f'socks5h://127.0.0.1:{SOCKS_PORT}',
            'https': f'socks5h://127.0.0.1:{SOCKS_PORT}'
        }
        try:
            r = requests.get("https://checkip.amazonaws.com", proxies=proxies, timeout=15)
            ip = r.text.strip()
            logging.info(f"Verification Success! Current IP: {ip}")
            return True, ip
        except Exception as e:
            logging.error(f"Verification Failed: {e}")
            return False, str(e)

    def rotate(self):
        logging.info("Requesting New Identity (IP Rotate)...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", CONTROL_PORT))
                s.send(b'AUTHENTICATE ""\r\n')
                response = s.recv(1024)
                if b"250 OK" not in response:
                    logging.error(f"Authentication failed: {response}")
                    return False
                
                s.send(b"SIGNAL NEWNYM\r\n")
                response = s.recv(1024)
                if b"250 OK" in response:
                    logging.info("New Identity requested successfully.")
                    # Optional: verify after rotate
                    return True
                else:
                    logging.error(f"SIGNAL NEWNYM failed: {response}")
                    return False
        except Exception as e:
            logging.error(f"Could not connect to Control Port: {e}")
            return False

    def is_running(self):
        pid_file = os.path.join(DATA_DIR, "tor.pid")
        if not os.path.exists(pid_file):
            return False
        with open(pid_file, "r") as f:
            try:
                pid = int(f.read())
            except: return False
        
        if os.name == 'nt':
            output = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True).stdout
            return str(pid) in output
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

if __name__ == "__main__":
    import requests
    import argparse
    
    parser = argparse.ArgumentParser(description="Tor Service Manager")
    parser.add_argument("command", choices=["start", "stop", "rotate", "status", "verify"])
    parser.add_argument("--interval", type=int, default=0, help="Rotation interval in seconds")
    
    args = parser.parse_args()
    service = TorService(interval=args.interval)
    
    if args.command == "start":
        # If interval is set, we need the manager to stay running.
        # Otherwise it just starts Tor and exits.
        if args.interval > 0:
            # Save manager PID
            with open(os.path.join(DATA_DIR, "manager.pid"), "w") as f:
                f.write(str(os.getpid()))
            service.start()
            while not service.stop_event.is_set():
                time.sleep(1)
        else:
            service.start()
    elif args.command == "stop":
        service.stop()
    elif args.command == "rotate":
        service.rotate()
    elif args.command == "verify":
        success, result = service.verify()
        if success: print(f"Success: {result}")
        else: print(f"Failed: {result}")
    elif args.command == "status":
        if service.is_running():
            print("Status: Running")
            if os.path.exists(TOR_LOG):
                with open(TOR_LOG, "r") as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        if "Bootstrapped" in line:
                            print(f"Bootstrap: {line.strip().split('Bootstrapped ')[1]}")
                            break
        else:
            print("Status: Stopped")
    else:
        print(f"Unknown command: {cmd}")
