from seleniumbase import Driver
import os

d = Driver(uc=True, headless=True)
try:
    url = "https://www.wikihow.com/Category:Gardening"
    print(f"Loading {url}...")
    d.get(url)
    d.save_screenshot("data/category_debug.png")
    
    # Try multiple common selectors
    selectors = ["#mw-pages", ".category_list", ".responsive_thumb", "#bodyContent"]
    for s in selectors:
        try:
            text = d.get_text(s)[:200]
            print(f"Selector '{s}' found text: {text}")
        except:
            print(f"Selector '{s}' NOT found.")
            
    # List all links in the main content area
    links = d.find_elements("a")
    print(f"Total links found: {len(links)}")
    for link in links[:20]:
        try:
            print(f"Link: {link.get_attribute('href')} -> {link.text}")
        except:
            pass
finally:
    d.quit()
