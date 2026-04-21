import os
import json
import psutil
import logging
import argparse
from datetime import datetime
from process_manager import PID_FILE, force_kill_chrome

# Logging setup
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIFECYCLE_LOG = os.path.join(BASE_DIR, "data", "process_lifecycle.json")

def load_lifecycle():
    if os.path.exists(LIFECYCLE_LOG):
        with open(LIFECYCLE_LOG, "r") as f:
            return json.load(f)
    return {"history": [], "active": {}}

def save_lifecycle(data):
    os.makedirs(os.path.dirname(LIFECYCLE_LOG), exist_ok=True)
    with open(LIFECYCLE_LOG, "w") as f:
        json.dump(data, f, indent=2)

def status_check():
    """Verify all active PIDs and update their status."""
    data = load_lifecycle()
    new_active = {}
    
    # Also check the old active_pids.json for migration
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            old_pids = json.load(f)
            for name, p_list in old_pids.items():
                if isinstance(p_list, int): p_list = [p_list]
                for pid in p_list:
                    if str(pid) not in data["active"]:
                        data["active"][str(pid)] = {
                            "name": name,
                            "start_time": "Unknown (Migrated)",
                            "status": "RUNNING"
                        }

    processed_any = False
    for pid_str, info in list(data["active"].items()):
        pid = int(pid_str)
        if psutil.pid_exists(pid):
            new_active[pid_str] = info
        else:
            # It died externally
            info["status"] = "CLOSED"
            info["end_time"] = datetime.now().isoformat()
            data["history"].append(info)
            processed_any = True
            logger.info(f"Process {info['name']} (PID {pid}) marked as CLOSED.")

    data["active"] = new_active
    save_lifecycle(data)
    
    # Display Status
    print("\n--- Current Process Status ---")
    if not new_active:
        print("No active processes tracked.")
    for pid, info in new_active.items():
        print(f"[{info['status']}] {info['name']} (PID: {pid}) - Started: {info['start_time']}")
    print("------------------------------\n")

def sweep():
    """Kill all tracked active processes and tag them as FORCE_KILLED."""
    data = load_lifecycle()
    pids_to_kill = list(data["active"].keys())
    
    for pid_str in pids_to_kill:
        pid = int(pid_str)
        info = data["active"].pop(pid_str)
        if psutil.pid_exists(pid):
            try:
                p = psutil.Process(pid)
                p.kill()
                info["status"] = "FORCE_KILLED"
                logger.info(f"Terminated {info['name']} (PID {pid})")
            except Exception as e:
                info["status"] = f"KILL_FAILED ({e})"
        else:
            info["status"] = "ALREADY_DEAD"
            
        info["end_time"] = datetime.now().isoformat()
        data["history"].append(info)

    save_lifecycle(data)
    print("Sweep complete. All tracked processes handled.")
    
    # Run the nuclear option too if requested
    print("Performing global cleanup of any remaining chrome orphans...")
    force_kill_chrome()

def main():
    parser = argparse.ArgumentParser(description="WikiHow Project Service Control Helper")
    parser.add_argument("--status", action="store_true", help="Show status of all tracked processes")
    parser.add_argument("--sweep", action="store_true", help="Force kill and log all active processes")
    
    args = parser.parse_args()
    
    if args.status:
        status_check()
    elif args.sweep:
        sweep()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
