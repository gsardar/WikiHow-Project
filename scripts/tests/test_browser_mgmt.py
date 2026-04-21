import os
import sys
import time
import logging

# Ensure project root is in path
sys.path.append(os.getcwd())

from wikihow import api
from wikihow.process_manager import cleanup_pids, MGMT_LOG

def test_browser_workflow():
    print("\n--- Phase 1: Cleanup Stale Sessions ---")
    # Clean up anything left over from previous crashes
    cleanup_pids(force_all=True)
    
    print("\n--- Phase 2: Start New Browser Session ---")
    # Start with direct connection for faster test
    driver = api._get_driver(no_tor=True)
    
    print("\n--- Phase 3: Verify Tab Switching & Safety ---")
    print("Switching to DeepSeek tab...")
    api.switch_to_tab("deepseek")
    print(f"Current URL: {driver.current_url}")
    
    print("SIMULATION: Spawning 3 unauthorized tabs...")
    for i in range(3):
        driver.execute_script(f"window.open('https://www.google.com/search?q={i}', '_blank');")
    
    print(f"Total handles currently open (should be 5): {len(driver.window_handles)}")
    
    print("Switching back to WikiHow tab (should trigger auto-cleanup)...")
    api.switch_to_tab("wikihow")
    print(f"Current URL: {driver.current_url}")
    print(f"Total handles after cleanup (should be 2): {len(driver.window_handles)}")
    
    print("\n--- Phase 4: Body Snippet & Status Verification ---")
    try:
        data = api.get_category_members("Gardening", limit=2)
        print(f"Fetched {len(data)} members. Check logs for body snippet.")
    except Exception as e:
        print(f"Data fetch failed: {e}")
    
    print("\n--- Phase 5: Final Cleanup ---")
    print("Closing browser and cleaning up PIDs...")
    cleanup_pids()
    
    print("\n--- Phase 6: Log Verification ---")
    msg = "No log found."
    if os.path.exists(MGMT_LOG):
        with open(MGMT_LOG, "r") as f:
            lines = f.readlines()
            msg = "".join(lines[-15:]) # Last 15 lines
    
    print("\nRecent Browser Management Logs:")
    print("-" * 50)
    print(msg)
    print("-" * 50)

if __name__ == "__main__":
    test_browser_workflow()
