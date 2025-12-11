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
from search import search
from cleanAds import getAds
from setTimeout import setTimeoutTo




run = True


if run:
    def run():
        unsetProxy(log=False)
        with sync_playwright() as p:
            # Launch browser
            browser = p.firefox.launch(
                headless=False,
                # proxy={"server": "direct://"},
                # args=["--no-proxy-server"]
            )
            
            # Create a new page
            page = browser.new_page()

            setTimeoutTo(page)

            page.set_default_timeout(60000) 


            page.goto("https://torob.com")


            search(page, PRODUCT, onlyStocks=True)

            # page2 = browser.new_page()
            gottenads = getAds(page, 20, "your5dad6666@gmail.com", "yasin.11A", PRODUCT)

            


            
            # time.sleep(200)
            browser.close()
            # print(gottenads)


            json_path = "json/torob.json"
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            gottenads = json.loads(gottenads)

            with open(json_path, "a") as f:
                f.truncate(0)
                json.dump(gottenads, f, indent=4, ensure_ascii=False)
            

            pass
if run:
    if __name__ == "__main__":
        run()
