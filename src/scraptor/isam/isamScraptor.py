# frameworks:
from playwright.sync_api import sync_playwright


# moduals:


# librarys:
import time 

run = False


if run == True:
    def run():
        with sync_playwright() as p:
            # Launch browser
            browser = p.firefox.launch(
                headless=False
                )
            
            # Create a new page
            page = browser.new_page()
            
            time.sleep(10)        
            # Close browser
            browser.close()

if run == True:
    if __name__ == "__main__":
        run()