import asyncio
from playwright.async_api import async_playwright

# In Message.py - Change to sync version
def SendGetMessage(message, email, password, page):
    from ..initMods.GetLastResponse import GetLastResponse
    from ..initMods.Loginer import LoginToDeepSeek
    from ..initMods.initMessages import customeInitMessage

    LoginToDeepSeek(email, password, page)

    customeInitMessage(
        page,
        """you are a ai assistant made to format big html tags, into simple json files, the html tag is a tag from a simple online shop, that have a few cards in it, you should format that html card, into json, the formatting should look like this
        {
            name: NAMEOFTHETCARD
            price: PRICEOFTHATCARD
            link: LINKOFTHATCARD
            image: PICTUREOFTHATCARD
        }

        POINTS: 
            - DO NOT answer with anything BUT json.
            - ONLY give json:
                -meaning:
                    if you HAVE the html files --> give me the json,
                    if you dont hve the html files --> return this -->:
                        {
                            "no html provided"
                        }
                
        """
    )
    
    page.get_by_placeholder("Message DeepSeek").fill(message)
    page.keyboard.press("Enter")
    response = GetLastResponse(page)
    
    return response

# For sync code, use this wrapper:
def SendGetMessageSync(message, email, password):
    return asyncio.run(SendGetMessage(message, email, password))