import sys
import os
import time

# Add project root to path
BASE_DIR = r"C:\Users\Admin\Documents\WikiHow Project"
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from wikihow.tor_manager import TorManager

def test_bootstrap():
    print("--- TOR LEGACY RESTORATION TEST ---")
    tm = TorManager()
    
    # Force a fresh start
    success = tm.connect(use_bridges=True)
    
    if success is True:
        print("\n[SUCCESS] Tor successfully bootstrapped to 100% using legacy parameters!")
        status = tm.get_status()
        print(f"Connected IP: {status['current_ip']}")
        print(f"Control Port: {status['control_port']}")
    else:
        print(f"\n[FAILED] Bootstrap failed: {success}")
        
    # Keep log open for a few seconds to see any late warnings
    time.sleep(5)

if __name__ == "__main__":
    test_bootstrap()
