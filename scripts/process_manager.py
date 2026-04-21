import os
import json
import psutil
import logging

# Define storage for active PIDs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PID_FILE = os.path.join(BASE_DIR, "data", "active_pids.json")

logger = logging.getLogger(__name__)

def track_pid(name, pid):
    """Save a PID and its associated name to the tracking file."""
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    try:
        pids = {}
        if os.path.exists(PID_FILE):
            with open(PID_FILE, "r") as f:
                pids = json.load(f)
        
        # If it's a list (already exists), append; otherwise make it a list
        if name not in pids: pids[name] = []
        if isinstance(pids[name], int): pids[name] = [pids[name]]
        
        if pid not in pids[name]:
            pids[name].append(pid)
            
        with open(PID_FILE, "w") as f:
            json.dump(pids, f, indent=2)
        logger.info(f"Tracking PID for {name}: {pid}")
    except Exception as e:
        logger.error(f"Error tracking PID: {e}")

def track_active_driver(name, driver):
    """Automatically discover the ChromeDriver PID and all its Chrome children."""
    try:
        parent_pid = driver.service.process.pid
        track_pid(f"{name}_driver", parent_pid)
        
        # Find all chrome children
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            track_pid(f"{name}_chrome", child.pid)
    except Exception as e:
        logger.error(f"Failed to track active driver {name}: {e}")

def cleanup_pids():
    """Kill all PIDs recorded in the tracking file and clear the file."""
    if not os.path.exists(PID_FILE):
        return

    try:
        with open(PID_FILE, "r") as f:
            pids = json.load(f)
        
        for name, p_list in pids.items():
            # Handle both single int and list of ints
            if isinstance(p_list, int): p_list = [p_list]
            
            for pid in p_list:
                if psutil.pid_exists(pid):
                    try:
                        p = psutil.Process(pid)
                        p.kill()
                        logger.info(f"Cleaned up stale process {name} (PID {pid})")
                    except Exception as e:
                        logger.warning(f"Failed to kill {name} ({pid}): {e}")
        
        # Clear the file after cleanup
        with open(PID_FILE, "w") as f:
            json.dump({}, f)
    except Exception as e:
        logger.error(f"Error in cleanup_pids: {e}")

def force_kill_chrome():
    """Nuclear option: kill any chromedriver.exe or chrome.exe process."""
    logger.info("Performing force-kill of all chrome/chromedriver instances...")
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in ['chrome.exe', 'chromedriver.exe', 'google chrome']:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == "__main__":
    # Test cleanup
    logging.basicConfig(level=logging.INFO)
    cleanup_pids()
    force_kill_chrome()
