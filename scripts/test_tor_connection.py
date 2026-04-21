import requests
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from wikihow.tor_manager import tor

print("=== TOR MANAGER TEST ===")
status = tor.get_status()
print(f"Status     : {status['status']}")
print(f"Proxy Port : {status['proxy_port']}")
print(f"Mode       : {status['mode']}")
print(f"Current IP : {status['current_ip']}")

if status["status"] == "CALIBRATED":
    print("\n[OK] Tor is live. Testing proxied request...")
    proxies = tor.get_requests_proxies()
    r = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
    print(f"External IP via Tor: {r.text.strip()}")
    print("SUCCESS: Pipeline is connected and ready for the research sweep!")
else:
    print("\n[INFO] Tor Browser not detected on ports 9050/9150.")
    print("Attempting to launch Tor Browser...")
    result = tor.connect()
    if result is True:
        print(f"SUCCESS: Connected! IP: {tor.active_ip}")
    else:
        print(f"FAILED: {result}")
        print("\nHint: Please open the Tor Browser manually and let it connect, then re-run this test.")
