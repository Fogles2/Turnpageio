#!/usr/bin/env python3
"""
Pinterest Image Scraper using Playwright

This script uses Playwright to search Pinterest for images and capture screenshots
to avoid 403 errors. Images are saved with meaningful filenames including timestamps
and keywords.

Usage:
    python pinterest_scraper.py --keywords "keyword1,keyword2" --count 10
"""

import argparse
import asyncio
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from playwright.async_api import async_playwright, Page, Browser


class PinterestScraper:
    """Pinterest image scraper using Playwright for browser automation."""
    
    def __init__(
        self,
        output_dir: str = "pinterest_images",
        rate_limit: float = 2.0,
        headless: bool = True
    ):
        """
        Initialize the Pinterest scraper.
        
        Args:
            output_dir: Directory to save downloaded images
            rate_limit: Delay between requests in seconds (default: 2.0)
            headless: Run browser in headless mode (default: True)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.rate_limit = rate_limit
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def setup(self):
        """Setup the browser and page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await context.new_page()
        
    async def cleanup(self):
        """Cleanup browser resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
            
    async def search_pinterest(self, keywords: str) -> None:
        """
        Search Pinterest for the given keywords.
        
        Args:
            keywords: Search keywords
        """
        search_url = f"https://www.pinterest.com/search/pins/?q={keywords.replace(' ', '%20')}"
        print(f"Searching Pinterest for: {keywords}")
        
        try:
            await self.page.goto(search_url, wait_until='networkidle', timeout=30000)
            # Wait for images to load
            await self.page.wait_for_selector('img', timeout=10000)
            await asyncio.sleep(2)  # Additional wait for dynamic content
        except Exception as e:
            print(f"Error navigating to Pinterest: {e}")
            raise
            
    async def scroll_and_load_images(self, scroll_count: int = 3) -> None:
        """
        Scroll the page to load more images.
        
        Args:
            scroll_count: Number of times to scroll down
        """
        for i in range(scroll_count):
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(1)
            print(f"Scrolled {i + 1}/{scroll_count} times")
            
    async def capture_image_screenshots(
        self,
        keywords: str,
        max_images: int = 10
    ) -> List[str]:
        """
        Capture screenshots of Pinterest images.
        
        Args:
            keywords: Keywords for filename generation
            max_images: Maximum number of images to capture
            
        Returns:
            List of saved image paths
        """
        saved_images = []
        
        # Find all image elements
        try:
            # Wait for images to be present
            await self.page.wait_for_selector('img[src*="pinimg"]', timeout=10000)
            
            # Get all Pinterest image elements
            images = await self.page.query_selector_all('img[src*="pinimg"]')
            
            print(f"Found {len(images)} image elements")
            
            # Limit to max_images
            images = images[:max_images]
            
            for idx, img_element in enumerate(images):
                try:
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    keyword_slug = keywords.replace(" ", "_").replace(",", "_")[:50]
                    filename = f"{keyword_slug}_{timestamp}_{idx + 1}.png"
                    filepath = self.output_dir / filename
                    
                    # Scroll element into view
                    await img_element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    
                    # Take screenshot of the image element
                    await img_element.screenshot(path=str(filepath))
                    
                    saved_images.append(str(filepath))
                    print(f"Saved: {filename}")
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit)
                    
                except Exception as e:
                    print(f"Error capturing image {idx + 1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding images: {e}")
            
        return saved_images
        
    async def scrape(
        self,
        keywords: str,
        max_images: int = 10,
        scroll_count: int = 3
    ) -> List[str]:
        """
        Main scraping method.
        
        Args:
            keywords: Search keywords
            max_images: Maximum number of images to capture
            scroll_count: Number of times to scroll for loading more images
            
        Returns:
            List of saved image paths
        """
        try:
            await self.setup()
            
            # Search for keywords
            await self.search_pinterest(keywords)
            
            # Scroll to load more images
            await self.scroll_and_load_images(scroll_count)
            
            # Capture screenshots
            saved_images = await self.capture_image_screenshots(keywords, max_images)
            
            print(f"\nSuccessfully captured {len(saved_images)} images")
            return saved_images
            
        finally:
            await self.cleanup()


async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Pinterest Image Scraper using Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pinterest_scraper.py --keywords "nature,mountains" --count 10
  python pinterest_scraper.py --keywords "design inspiration" --count 5 --output images/
  python pinterest_scraper.py --keywords "food photography" --count 20 --headless false
        """
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        required=True,
        help='Search keywords (comma-separated or space-separated)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Maximum number of images to capture (default: 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='pinterest_images',
        help='Output directory for images (default: pinterest_images)'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=2.0,
        help='Rate limit delay in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--headless',
        type=str,
        default='true',
        choices=['true', 'false'],
        help='Run browser in headless mode (default: true)'
    )
    parser.add_argument(
        '--scroll-count',
        type=int,
        default=3,
        help='Number of times to scroll down for loading more images (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = PinterestScraper(
        output_dir=args.output,
        rate_limit=args.rate_limit,
        headless=(args.headless.lower() == 'true')
    )
    
    # Run scraping
    start_time = time.time()
    saved_images = await scraper.scrape(
        keywords=args.keywords,
        max_images=args.count,
        scroll_count=args.scroll_count
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'=' * 60}")
    print(f"Scraping completed in {elapsed_time:.2f} seconds")
    print(f"Total images saved: {len(saved_images)}")
    print(f"Output directory: {args.output}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
