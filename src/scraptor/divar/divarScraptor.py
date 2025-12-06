# frameworks:
from playwright.sync_api import sync_playwright




# librarys:
import time
import os
import json 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PROD import PRODUCT



# moduals:
from unsetProxy import unsetProxy
from setTimeout import setTimeoutTo





run = True


if run:
    def run():
        with sync_playwright() as p:
            # Launch browser
            browser = p.firefox.launch(
                headless=False
                )
            
            # Create a new page
            page = browser.new_page()

            setTimeoutTo(page)

            page.goto("https://divar.ir/s/tehran")


            def search(p, page=page):
                page.get_by_placeholder("جستجو در همهٔ آگهی‌ها").fill(p)


            search(PRODUCT)
            
            time.sleep(10)
            # Close browser
            browser.close()

if __name__ == "__main__":
    run()