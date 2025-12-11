# frameworks:
from playwright.sync_api import sync_playwright

# librarys:
import time
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PROD import PRODUCT

# moduals:
from unsetProxy import unsetProxy
from setTimeout import setTimeoutTo
from search import search
from getAds import getAds


run = True
defGoTo = False

if run:
    def run():
        with sync_playwright() as p:
            # Launch browser
            browser = p.firefox.launch(
                headless=False
                )
            

            
            # Create a new page
            page = browser.new_page()

            # page.evaluate("document.body.style.zoom = '0.8'")

            setTimeoutTo(page)
            if defGoTo: # divar is extrimely slow and this line of code was almost certainly useless so i did this funny thing. so the good coder will come and laugh at my code, and i will be able to learn from being a absloute bingo <-- guss that the work was :) 
                page.goto("https://divar.ir/s/iran?map_interaction=search_this_area_disabled")

            search(PRODUCT, page) # <-- baically might be our entry to the web page





            ads = getAds(page, 20, "your5dad6666@gmail.com", "yasin.11A", PRODUCT)

            json_path = "json/divar.json"
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            ads = json.loads(ads)

            with open(json_path, "a") as f:
                f.truncate(0)
                json.dump(ads, f, indent=4, ensure_ascii=False)


            time.sleep(10)
            # Close browser
            browser.close()

if __name__ == "__main__":
    run()