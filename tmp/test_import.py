import sys
import os
sys.path.append(os.getcwd())
try:
    print("Attempting to import _get_driver from wikihow.api...")
    from wikihow.api import _get_driver
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
