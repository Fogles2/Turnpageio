from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime

class PinterestScraper:
    def __init__(self):
        self.base_url = "https://pinterest.com"
        self.screenshot_dir = "pinterest_images"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def scrape_images(self, keyword, max_images=20):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to Pinterest search results
            search_url = f"{self.base_url}/search/pins/?q={keyword}"
            page.goto(search_url)
            
            # Wait for images to load
            page.wait_for_selector('[data-test-id="pinrep-image"]')
            
            images_captured = 0
            while images_captured < max_images:
                # Find all image containers
                image_elements = page.query_selector_all('[data-test-id="pinrep-image"]')
                
                for img in image_elements[images_captured:]:
                    if images_captured >= max_images:
                        break
                        
                    # Scroll element into view and wait for it to be visible
                    img.scroll_into_view_if_needed()
                    time.sleep(1)  # Allow time for image to load fully
                    
                    # Take screenshot of the image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{keyword}_{timestamp}_{images_captured}.png"
                    img.screenshot(path=os.path.join(self.screenshot_dir, filename))
                    
                    images_captured += 1
                    
                # Scroll down to load more images
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(2)  # Wait for new images to load
                
            browser.close()
            
        return self.screenshot_dir

if __name__ == "__main__":
    scraper = PinterestScraper()
    keyword = input("Enter search keyword: ")
    scraper.scrape_images(keyword)