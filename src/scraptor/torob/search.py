def search(page, thing, onlyStocks=True):
    page.get_by_placeholder("نام کالا را وارد کنید").fill(thing)
    page.keyboard.press("Enter")
    
    # Use timeout instead of networkidle
    page.wait_for_timeout(5000)  # Wait 5 seconds

    
    # if onlyStocks:
    #     url = page.url
    #     page.goto(url + " &available=true&stock_status=new")
    #     page.wait_for_timeout(5000)  # Wait 5 seconds
    # else:
    #     url = page.url
    #     page.goto(url + " &available=true")