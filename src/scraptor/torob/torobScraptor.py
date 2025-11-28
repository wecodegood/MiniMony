# frameworks:
from playwright.sync_api import sync_playwright




# librarys:
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# moduals:
from unsetProxy import unsetProxy
from search import search
from cleanAds import getAds




unsetProxy(log=False)

def run():
    with sync_playwright() as p:
        # Launch browser
        browser = p.firefox.launch(
            headless=False,
            # proxy={"server": "direct://"},
            # args=["--no-proxy-server"]
        )
        
        # Create a new page
        page = browser.new_page()

        page.set_default_timeout(60000) 

        page.goto("https://torob.com")

        search(page, "dell precision 5540", onlyStocks=True)


        gottenads = getAds(page, 12)

        


        
        # time.sleep(200)
        browser.close()
        print(gottenads)

if __name__ == "__main__":
    run()