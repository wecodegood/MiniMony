from playwright.sync_api import sync_playwright
import time



with sync_playwright() as p:
    
    browser = p.firefox.launch(headless=False)

    page = browser.new_page()

    page.goto("https://divar.ir/s/iran?map_interaction=search_this_area_disabled", wait_until="domcontentloaded")



    # for i in range(1000):

    #     page.keyboard.press("PageDown")

        
    time.sleep(10000000)



    pass

