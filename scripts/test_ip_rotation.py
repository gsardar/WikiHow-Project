import requests
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from wikihow.tor_manager import tor
from stem.control import Controller
from stem import Signal

def get_ip(proxies):
    try:
        return requests.get("https://api.ipify.org", proxies=proxies, timeout=10).text.strip()
    except Exception as e:
        return f"ERROR: {e}"

print("=== IP ROTATION TEST ===")
tor._detect_ports()

if not tor.is_connected:
    print("Tor not connected. Please open Tor Browser first.")
    sys.exit(1)

proxies = tor.get_requests_proxies()
ip_before = get_ip(proxies)
print(f"IP before rotation : {ip_before}")
print(f"Control port       : {tor.control_port}")

# Try cookie auth (required by Tor Browser)
TOR_COOKIE = r"C:\Users\Admin\Desktop\Portable\Tor Browser\Browser\TorBrowser\Data\Tor\control_auth_cookie"

print("\nAttempting NEWNYM signal via cookie auth...")
try:
    with Controller.from_port(port=9151) as c:
        c.authenticate(cookie_file=TOR_COOKIE)
        print("  [OK] Authenticated with cookie")
        c.signal(Signal.NEWNYM)
        print("  [OK] NEWNYM signal sent")

    import time; time.sleep(5)
    ip_after = get_ip(proxies)
    print(f"IP after rotation  : {ip_after}")

    if ip_before != ip_after:
        print("\nSUCCESS: IP changed!")
    else:
        print("\nNOTE: IP is the same (Tor may reuse circuits; try again)")
except Exception as e:
    print(f"  [FAIL] {e}")
    print("\nTrying blank authenticate (fallback)...")
    try:
        with Controller.from_port(port=9151) as c:
            c.authenticate()
            c.signal(Signal.NEWNYM)
            import time; time.sleep(5)
            ip_after = get_ip(proxies)
            print(f"IP after rotation  : {ip_after}")
    except Exception as e2:
        print(f"  [FAIL] fallback also failed: {e2}")
