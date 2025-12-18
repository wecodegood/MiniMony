# frameworks:
from playwright.sync_api import sync_playwright

# libraries:
import time
import os
import sys
import json

# Make sure project root (src) is on sys.path so absolute imports work from anywhere
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from scraptor.PROD import PRODUCT

# modules:
from scraptor.unsetProxy import unsetProxy
from scraptor.setTimeout import setTimeoutTo
from scraptor.divar.search import search
from scraptor.divar.getAds import getAds
from scraptor.divar.getCheapest import getCheapestAdd

def run(product: str | None = None):
    """
    Run the Divar scraptor.

    - When product is provided, it will be used as the search term.
    - When product is None, it falls back to the global PRODUCT constant
      to preserve CLI behaviour.
    """
    search_term = product or PRODUCT

    with sync_playwright() as p:
        # Launch browser in headless mode so it can safely run behind the web UI
        browser = p.firefox.launch(headless=True)

        # Create a new page
        page = browser.new_page()

        # Set timeout
        setTimeoutTo(page)

        # Search for the product
        search(search_term, page)

        # Wait for content to be ready (improved version)
        wait_for_content_ready(page)

        for _ in range(10):
            page.keyboard.press("PageDown")

        # Get ads (JSON string) and parse to Python object
        ads_json = getAds(page, 20, "your5dad6666@gmail.com", "yasin.11A", search_term)
        try:
            ads = json.loads(ads_json)
        except Exception:
            # Fallback: keep raw response if it wasn't valid JSON
            ads = ads_json

        # Save to JSON - FIXED PATH
        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up 2 levels to reach src folder
        project_root = os.path.dirname(os.path.dirname(script_dir))
        # Create json directory path
        json_dir = os.path.join(project_root, "json")
        json_path = os.path.join(json_dir, "divar.json")

        os.makedirs(json_dir, exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ads, f, indent=4, ensure_ascii=False)

        # Try to log a meaningful count
        count = len(ads) if isinstance(ads, list) else 1
        print(f"Saved {count} ads to {json_path}")

        time.sleep(2)
        browser.close()


def wait_for_content_ready(page, timeout=30000):
    """
    Wait until the page has actual content, not just loading animations
    """
    start_time = time.time()
    poll_interval = 500  # Check every 500ms
    
    # Define what "ready enough" means for Divar
    content_selectors = [
        "article.post-card",  # Divar ad cards
        "[data-testid='post-card']",  # Another possible selector
        ".post-list article",  # List of posts
        ".kt-post-card",  # Divar's post cards
    ]
    
    while time.time() - start_time < timeout:
        # Check each selector
        for selector in content_selectors:
            elements = page.query_selector_all(selector)
            if elements and len(elements) > 3:  # At least 4 ads loaded
                # Check if any have actual content
                for element in elements[:3]:  # Check first 3
                    text = element.inner_text().strip()
                    if text and len(text) > 30:  # Has reasonable content
                        print(f"Found {len(elements)} ads, ready to scrape!")
                        return True
        
        # Also check for pagination or results count
        results_count = page.query_selector(".post-list-header__count")
        if results_count:
            count_text = results_count.inner_text().strip()
            if any(char.isdigit() for char in count_text):
                print(f"Found results count: {count_text}")
                return True
        
        page.wait_for_timeout(poll_interval / 1000)  # Convert to seconds
    
    print("Timeout waiting for content")
    return False


if __name__ == "__main__":
    runApp = True
    defGoTo = False  # Set to True if you need initial navigation
    
    if runApp == True:
        run()