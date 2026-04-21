import os
import csv
import time
import argparse
import json
from bs4 import BeautifulSoup
from wikihow.scraper_engine import ScraperEngine
from wikihow.tor_manager import tor

class UniversalDiscovery:
    def __init__(self, use_tor=False, use_cookies=False, headless=False):
        self.engine = ScraperEngine(use_tor=use_tor, use_cookies=use_cookies, headless=headless)
        self.seen_urls = set()

    def search_wikihow(self, query, max_results=45):
        """Native WikiHow Search Scraper."""
        print(f"  [WIKIHOW] Searching: {query}")
        results = []
        start = 0
        
        driver = self.engine.get_driver()
        
        while start < max_results:
            url = f"https://www.wikihow.com/wikiHowTo?search={query.replace(' ', '+')}&start={start}"
            driver.get(url)
            self.engine.handle_popups()
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            links = soup.select("a.result_link")
            
            if not links:
                break
                
            for a in links:
                link_url = a.get("href")
                if link_url and "wikihow.com" in link_url:
                    if link_url not in self.seen_urls:
                        title_div = a.select_one("div.result_title")
                        title = title_div.text.strip() if title_div else "Unknown"
                        results.append({"url": link_url, "title": title, "source": "wikihow"})
                        self.seen_urls.add(link_url)
            
            # Check for next button (though we use start param)
            if not soup.select_one("a.button.next"):
                break
            
            start += 15
            
        print(f"    [WIKIHOW] Found {len(results)} items.")
        return results

    def search_google(self, query, max_pages=3):
        """Google Discovery (minimal implementation for Universal tool)."""
        print(f"  [GOOGLE] Searching: {query}")
        results = []
        driver = self.engine.get_driver()
        
        # HL=EN to force English
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:wikihow.com&hl=en"
        driver.get(search_url)
        self.engine.handle_popups()
        
        for page in range(1, max_pages + 1):
            time.sleep(3)
            # Check for Captcha
            if "sorry/index" in driver.current_url:
                if not self.engine.solve_captcha_manual():
                    break
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for h3 in soup.find_all('h3'):
                link_node = h3.parent
                while link_node and link_node.name != 'a':
                    link_node = link_node.parent
                
                if link_node and link_node.name == 'a':
                    url = link_node.get('href')
                    if url and "wikihow.com" in url:
                        if url not in self.seen_urls:
                            results.append({"url": url, "title": h3.text.strip(), "source": "google"})
                            self.seen_urls.add(url)
            
            # Next page
            next_btn = driver.find_elements("css selector", "#pnnext")
            if next_btn:
                next_btn[0].click()
            else:
                break
                
        print(f"    [GOOGLE] Found {len(results)} items.")
        return results

    def run_discovery(self, category, continuum, output_file):
        print(f"\n--- Universal Discovery: {category} ({continuum}) ---")
        
        # 1. Native WikiHow Search
        res_wh = self.search_wikihow(category)
        
        # 2. Google Search (Broad)
        res_gg = self.search_google(category)
        
        all_results = res_wh + res_gg
        
        # Save to CSV
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        file_exists = os.path.isfile(output_file)
        
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Continuum", "Query", "Title", "URL", "Source"])
            
            for item in all_results:
                writer.writerow([continuum, category, item["title"], item["url"], item["source"]])
        
        print(f"  [DONE] Total {len(all_results)} new items saved to {output_file}")

    def cleanup(self):
        self.engine.destroy_driver()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal WikiHow Discovery Tool")
    parser.add_argument("--category", required=True, help="Category name to search")
    parser.add_argument("--continuum", required=True, help="Continuum name (domestic/occupational)")
    parser.add_argument("--tor", action="store_true", help="Use Tor IP rotation")
    parser.add_argument("--cookies", action="store_true", help="Use native browser session")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    
    args = parser.parse_args()
    
    # Path inside V1 data
    output_dir = rf"c:\Users\Admin\Documents\WikiHow Project\data\DataVersions\v1\data1\discovery\{args.continuum}\{args.category.replace(' ', '_').lower()}"
    output_file = os.path.join(output_dir, "discovery_report_universal.csv")
    
    discovery = UniversalDiscovery(use_tor=args.tor, use_cookies=args.cookies, headless=args.headless)
    try:
        discovery.run_discovery(args.category, args.continuum, output_file)
    finally:
        discovery.cleanup()
