# frameworks:
from playwright.sync_api import sync_playwright


# moduals:
from ..unsetProxy import unsetProxy


# librarys:
import time

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

        unsetProxy(log=False)

        page.set_default_timeout(60000) 


        page.goto("https://torob.com")



        
        time.sleep(10)        
        # Close browser
        browser.close()

if __name__ == "__main__":
    run()