# frameworks:
from playwright.sync_api import sync_playwright




# librarys:
import time
import os
import json 
import sys

# Make sure project root (src) is on sys.path so absolute imports work from anywhere
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from scraptor.PROD import PRODUCT



# modules:
from scraptor.unsetProxy import unsetProxy
from scraptor.torob.search import search
from scraptor.torob.cleanAds import getAds
from scraptor.setTimeout import setTimeoutTo




run = True


if run:
    def run(product: str | None = None):
        """
        Run the Torob scraptor.

        - When product is provided, it will be used as the search term.
        - When product is None, it falls back to the global PRODUCT constant.
        """
        search_term = product or PRODUCT

        unsetProxy(log=False)
        with sync_playwright() as p:
            # Launch browser in headless mode for web usage
            browser = p.firefox.launch(
                headless=True,
                # proxy={"server": "direct://"},
                # args=["--no-proxy-server"]
            )

            # Create a new page
            page = browser.new_page()

            setTimeoutTo(page)

            page.set_default_timeout(60000)

            page.goto("https://torob.com")

            search(page, search_term, onlyStocks=True)

            gottenads = getAds(page, 20, "your5dad6666@gmail.com", "yasin.11A", search_term)

            browser.close()

            # Resolve json/ path relative to project root (same as Divar)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            json_dir = os.path.join(project_root, "json")
            json_path = os.path.join(json_dir, "torob.json")
            os.makedirs(json_dir, exist_ok=True)

            gottenads = json.loads(gottenads)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(gottenads, f, indent=4, ensure_ascii=False)

            print(f"Saved {len(gottenads)} ads to {json_path}")

            pass
if run:
    if __name__ == "__main__":
        run()
