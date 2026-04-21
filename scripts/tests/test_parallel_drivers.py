import sys
import os
import time
import multiprocessing
from wikihow import api

def run_worker(worker_id):
    print(f"--- Worker {worker_id} Starting ---")
    try:
        # Each worker initializes its own driver with a UNIQUE profile
        # This is what our api.py now supports via worker_id
        driver = api._get_driver(no_tor=True, worker_id=worker_id)
        
        url = "https://www.wikihow.com/Main-Page"
        print(f"Worker {worker_id} loading {url}...")
        driver.get(url)
        time.sleep(5)
        
        cookie_count = len(driver.get_cookies())
        print(f"Worker {worker_id} SUCCESS. Cookies: {cookie_count}. Handles: {len(driver.window_handles)}")
        
        # Keep open for a bit for user to see
        time.sleep(5)
        
    except Exception as e:
        print(f"Worker {worker_id} FAILED: {e}")
    finally:
        # Note: We don't cleanup globally here so other worker stays alive
        pass

def test_parallel_drivers():
    print("Testing Parallel Browser Instances with Unique Sandboxed Profiles...")
    p1 = multiprocessing.Process(target=run_worker, args=(1,))
    p2 = multiprocessing.Process(target=run_worker, args=(2,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    print("\nParallel Test Complete.")

if __name__ == "__main__":
    test_parallel_drivers()
