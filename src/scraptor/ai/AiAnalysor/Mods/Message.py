import asyncio
from playwright.async_api import async_playwright

# In Message.py - Change to sync version
def SendGetMessage(message, email, password, page, prod):
    from ..initMods.GetLastResponse import GetLastResponse
    from ..initMods.Loginer import LoginToDeepSeek
    from ..initMods.initMessages import customeInitMessage

    LoginToDeepSeek(email, password, page)
    
    page.get_by_placeholder("Message DeepSeek").fill(
        """

You are an AI assistant specialized in extracting product information from HTML and formatting it into clean JSON. Your task is to process HTML product cards from Iranian online shops and output the cheapest valid product in a specific JSON format.

REQUIRED OUTPUT FORMAT:
{
"name": "PRODUCT_NAME",
"price": PRICE_AS_NUMBER,
"link": "PRODUCT_URL",
"image": "IMAGE_URL"
}

CRITICAL RULES:

    MANDATORY FIELDS: All four fields (name, price, link, image) MUST be populated. Empty strings are NOT acceptable.

    PRICE FORMATTING:

        Always output price as a plain number (e.g., 46000000 for 46 million tomans)

        Remove all currency symbols, commas, and text

        Convert Persian numbers to Western numerals

    VALIDATION:

        Verify the product actually matches what the user is searching for

        Don't include products that merely contain keywords but aren't the actual product

        Select the cheapest valid product from the available options

    JSON STRUCTURE:

        Always use multi-line JSON format

        No code blocks or backticks

        Clean, minimal formatting without extra characters

    ERROR HANDLING:

        If no HTML is provided, return: {"no html provided"}

        If no valid products found, return empty fields with price as 0: {"name": "", "price": 0, "link": "", "image": ""}
        ----this is one error handler that you constantly break, we dont need ANOTHER PRODUCT, we need the exact PRODUCT, so. return empty, NOT ANOTHER PRODUCT

        

    PRIORITIZATION:

        Link and image URLs are ESSENTIAL - never leave them empty

        Always select the product with the lowest price among valid matches

        Clean product names by removing excessive descriptions while keeping essential specs
    

EXAMPLE OUTPUT:
{
"name": "name of the product",
"price": 49068404,
"link": "https://example.com/product/123",
"image": "https://example.com/images/product123.jpg"
}

Now process the following HTML for the product: """ + prod + "\nhtml code --> \n" + message
    )

    page.keyboard.press("Enter")
    response = GetLastResponse(page)

    return response

# For sync code, use this wrapper:
def SendGetMessageSync(message, email, password, prod):
    return asyncio.run(SendGetMessage(message, email, password, prod))

# Alternative async wrapper if you're already in async context
async def SendGetMessageAsync(message, email, password, prod):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # or True for headless
        context = await browser.new_context()
        page = await context.new_page()
        
        result = await SendGetMessage(message, email, password, page, prod)
        
        await browser.close()
        return result