from seleniumbase import Driver
import os
import sys

# Define a persistent user data directory in the project
base_dir = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(base_dir, "..", "data", "browser_session")

def setup_session():
    print("=" * 60)
    print("WIKIHOW SESSION SETUP")
    print("=" * 60)
    print(f"User Data Directory: {USER_DATA_DIR}")
    print("\nStarting browser... Please log in to WikiHow in the opened window.")
    
    # Initialize Driver with UC mode and persistent user data
    # We don't use headless here because the user needs to interact with the UI
    driver = Driver(uc=True, user_data_dir=USER_DATA_DIR)
    
    try:
        driver.get("https://www.wikihow.com/Special:UserLogin")
        
        print("\n" + "!" * 60)
        print("ACTION REQUIRED: Please log in to your WikiHow account in the browser.")
        print("Once you are logged in and ready, come back here.")
        print("!" * 60)
        
        input("\nPress ENTER in this terminal once you have finished logging in...")
        
        print("\nSaving session and closing browser...")
    finally:
        driver.quit()
        print("\nSession saved successfully. You can now run the data collection script.")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(USER_DATA_DIR), exist_ok=True)
    setup_session()
