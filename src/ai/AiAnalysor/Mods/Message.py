def SendGetMessage(page, message, email, password):
    from initMods.GetLastResponse import GetLastResponse
    from initMods.Loginer import LoginToDeepSeek

    with sync_playwright() as p:

        browser = p.firefox.launch(
            headless=True,
            # slow_mo=2000
        )

        # context saves the settings we whant to modify in the prefrencec
        # for example here i did this to make deepseek.com go dark mode because i was getting blind
        context = browser.new_context(
            color_scheme='dark'  # to make it go dark mode
            
        )
        
        page = context.new_page()


        LoginToDeepSeek(email, password, browser, page) # this is a function from a file named Loginer.py located in initMods folder




        page.get_by_placeholder("Message DeepSeek").fill(message)
        page.keyboard.press("Enter")
        response = GetLastResponse()
    return response


        
