import sys
import os
sys.path.append(os.getcwd())
import time

def open_tabs(fresh=False):
    print("DEBUG: Starting open_tabs...")
    if fresh:
        import tempfile
        import shutil
        temp_dir = tempfile.mkd_temp(prefix="wikihow_profile_")
        print(f"DEBUG: Using fresh temporary profile: {temp_dir}")
        # Note: we are not setting it here, we'll pass it to _get_driver if we refactor it
    
    print("DEBUG: Calling _get_driver(no_tor=True)...")
    try:
        from wikihow.api import _get_driver
        driver = _get_driver(no_tor=True)
    except Exception as e:
        print(f"ERROR: Failed to initialize driver: {e}")
        return

    print("DEBUG: Driver initialized. Opening tabs...")
    print("Browser is open. You can now use both tabs.")
    print("Press Ctrl+C here to close the session.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing browser...")

if __name__ == "__main__":
    open_tabs()
