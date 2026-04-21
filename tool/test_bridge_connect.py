from wikihow.tor_manager import tor

def test():
    print("=== Tor Bridge Connection Test ===")
    success = tor.connect(use_bridges=True)
    
    if success == True:
        status = tor.get_status()
        print("\n[VERIFIED] Connection established through bridges!")
        print(f"Status: {status['status']}")
        print(f"Tor IP: {status['current_ip']}")
        print(f"Proxy:  {tor.get_selenium_proxy()}")
    else:
        print(f"\n[FAILED] Could not establish bridge connection: {success}")

if __name__ == "__main__":
    test()
