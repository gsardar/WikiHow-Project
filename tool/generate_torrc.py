import os

BASE_DIR = r"C:\Users\Admin\Documents\WikiHow Project"
TOR_BROWSER_DIR = r"C:\Users\Admin\Desktop\Portable\Tor Browser\Browser\TorBrowser"
TOR_EXE = os.path.join(TOR_BROWSER_DIR, "Tor", "tor.exe")
LYREBIRD_PATH = os.path.join(TOR_BROWSER_DIR, "Tor", "PluggableTransports", "lyrebird.exe")
BRIDGES_FILE = os.path.join(BASE_DIR, "tool", "tor_bridges.txt")
DATA_DIR = os.path.join(BASE_DIR, "tool", "tor_data", "tordata0")
OUTPUT_TORRC = os.path.join(BASE_DIR, "tool", "torrc.custom")

def generate_torrc():
    print(f"--- Generating Modern Tor Browser torrc ---")
    
    # Ensure data dir exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(BRIDGES_FILE):
        print(f"[ERROR] Bridges file not found.")
        return False

    # Extract bridges from the high-stealth GitHub list
    with open(BRIDGES_FILE, "r") as f:
        bridges = f.read().strip()

    torrc_content = f"""
# Modern Tor Browser Integration torrc
DataDirectory {DATA_DIR}
GeoIPFile {os.path.join(TOR_BROWSER_DIR, "Data", "Tor", "geoip")}
GeoIPv6File {os.path.join(TOR_BROWSER_DIR, "Data", "Tor", "geoip6")}

# Logging
Log notice file {os.path.join(DATA_DIR, "tor.log")}

# Connection Ports
SocksPort 0.0.0.0:9050
ControlPort 15000
DNSPort 53

# Bridge Configuration
UseBridges 1
ClientTransportPlugin obfs2,obfs3,obfs4 exec {LYREBIRD_PATH}

# Performance / Stealth
AvoidDiskWrites 1
SafeLogging 0
GeoIPExcludeUnknown 1

# Injected High-Stealth Bridges
{bridges}
"""
    
    with open(OUTPUT_TORRC, "w", encoding="utf-8") as f:
        f.write(torrc_content.strip())
        
    print(f"[SUCCESS] torrc.custom generated at {OUTPUT_TORRC}")
    return True

if __name__ == "__main__":
    generate_torrc()
