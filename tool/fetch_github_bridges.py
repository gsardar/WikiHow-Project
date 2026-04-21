import requests
import os

BRIDGE_URL = "https://raw.githubusercontent.com/scriptzteam/Tor-Bridges-Collector/main/bridges-obfs4"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tor_bridges.txt")

def fetch_bridges():
    print(f"--- Fetching Stealth Bridges (By-Pass Mode) ---")
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        r = requests.get(BRIDGE_URL, timeout=15)
        if r.status_code == 200:
            lines = r.text.splitlines()
            bridges = [line.strip() for line in lines if line.strip().startswith("obfs4")]
            
            if not bridges:
                print("[ERROR] No bridges found.")
                return False

            # HEURISTIC: Institutional firewalls usually allow Port 443, 80, 8080, 8443.
            # We also prioritize iat-mode=1/2 which randomizes packet timing for DPI bypass.
            stealth_bridges = []
            
            # Tier 1: Randomized Timing + Standard Ports
            for b in bridges:
                if ("iat-mode=1" in b or "iat-mode=2" in b) and any(port in b for port in [":443 ", ":80 ", ":8443 "]):
                    stealth_bridges.append(b)

            # Tier 2: Just Randomized Timing
            if len(stealth_bridges) < 10:
                for b in bridges:
                    if ("iat-mode=1" in b or "iat-mode=2" in b) and b not in stealth_bridges:
                        stealth_bridges.append(b)
            
            # Tier 3: Just Standard Ports
            if len(stealth_bridges) < 15:
                for b in bridges:
                    if any(port in b for port in [":443 ", ":80 ", ":8443 "]) and b not in stealth_bridges:
                        stealth_bridges.append(b)

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                # Use a small diverse set (max 15) for faster bootstrap
                for b in stealth_bridges[:15]:
                    f.write(f"Bridge {b}\n")
            
            print(f"[SUCCESS] Saved {len(stealth_bridges[:15])} high-stealth bridges (iat-mode prioritized) to {OUTPUT_FILE}")
            return True
        else:
            print(f"[ERROR] Failed download. Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"[CRITICAL] Bridge fetch failed: {e}")
        return False

if __name__ == "__main__":
    fetch_bridges()
