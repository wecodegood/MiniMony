# frameworks:
from playwright.sync_api import sync_playwright

# libraries:
import time
import os
import json
import sys

# Ensure project root is on sys.path so we can import scraptor as a top-level package
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now we can import scraptor modules as top-level
from scraptor.PROD import PRODUCT
from scraptor.unsetProxy import unsetProxy
from scraptor.torob.search import search
from scraptor.torob.cleanAds import getAds
from scraptor.setTimeout import setTimeoutTo


def run(product: str | None = None):
    """
    Run the Torob scraptor.

    - When product is provided, it will be used as the search term.
    - When product is None, it falls back to the global PRODUCT constant.
    """
    search_term = product or PRODUCT

    unsetProxy(log=False)
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        setTimeoutTo(page)
        page.set_default_timeout(60000)
        page.goto("https://torob.com")
        search(page, search_term, onlyStocks=True)
        gottenads = getAds(page, 20, search_term)
        browser.close()

    # Save ads to JSON relative to project root
    json_dir = os.path.join(PROJECT_ROOT, "json")
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, "torob.json")

    # Ensure we return parsed data rather than writing to disk
    try:
        gottenads = json.loads(gottenads)
    except Exception:
        # If getAds already returned a Python object
        pass

    print(f"Scraped {len(gottenads) if isinstance(gottenads, list) else 1} ads from Torob")
    return gottenads


if __name__ == "__main__":
    run()
