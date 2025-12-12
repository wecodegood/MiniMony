import json
import re
import asyncio
from typing import Dict, Any
from playwright.async_api import async_playwright, Page

async def getCheapestAdd(
    url: str, 
    target_product: str,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Extract the cheapest product from Divar using Playwright.
    
    Args:
        url: The Divar search URL (e.g., search results page)
        target_product: The product name to search for (e.g., "Poco x3 pro")
        headless: Run browser in headless mode (faster, no GUI)
        
    Returns:
        JSON dictionary with name, price, link, and image of cheapest valid product
    """
    # Persian to Western numeral mapping
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    
    # Normalize target product for comparison
    target_normalized = target_product.lower().strip()
    
    valid_products = []
    
    async with async_playwright() as p:
        # Launch browser (Chromium is recommended for stability)[citation:4]
        browser = await p.chromium.launch(headless=headless)
        
        # Create browser context with realistic viewport[citation:4]
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        page = await context.new_page()
        
        try:
            # Navigate to the URL and wait for content[citation:1][citation:4]
            await page.goto(url, wait_until="networkidle")
            
            # Wait for product cards to load
            await page.wait_for_selector('a.kt-post-card__action', timeout=10000)
            
            # Extract all product cards using Playwright's locators[citation:1]
            product_cards = await page.locator('a.kt-post-card__action').all()
            
            for card in product_cards:
                try:
                    # Extract product name
                    title_elem = await card.locator('h2.kt-post-card__title').first
                    if not title_elem:
                        continue
                    
                    product_name = (await title_elem.inner_text()).strip()
                    
                    # Normalize product name for comparison
                    product_normalized = product_name.lower()
                    
                    # Check if this is the target product
                    if target_normalized in product_normalized or product_normalized in target_normalized:
                        is_target_product = True
                    else:
                        # Check for variations (remove spaces, special chars)
                        product_no_spaces = re.sub(r'[\s\-_]', '', product_normalized)
                        target_no_spaces = re.sub(r'[\s\-_]', '', target_normalized)
                        is_target_product = target_no_spaces in product_no_spaces or product_no_spaces in target_no_spaces
                    
                    if not is_target_product:
                        continue
                    
                    # Extract price using $$eval approach[citation:3]
                    price_text = None
                    description_elems = await card.locator('div.kt-post-card__description').all()
                    
                    for elem in description_elems:
                        text = (await elem.inner_text()).strip()
                        if 'تومان' in text or any(char.isdigit() for char in text):
                            price_text = text
                            break
                    
                    if not price_text:
                        continue
                    
                    # Extract only numeric parts and convert Persian numbers
                    price_digits = ''
                    for char in price_text:
                        if char in persian_to_english:
                            price_digits += persian_to_english[char]
                        elif char.isdigit():
                            price_digits += char
                    
                    if not price_digits:
                        continue
                    
                    try:
                        price = int(price_digits)
                    except ValueError:
                        continue
                    
                    # Extract link
                    link = await card.get_attribute('href')
                    if link and not link.startswith('http'):
                        link = f"https://divar.ir{link}"
                    
                    # Extract image
                    img_elem = await card.locator('img').first
                    image_url = ""
                    if img_elem:
                        # Try data-src first (lazy loaded), then src
                        image_url = await img_elem.get_attribute('data-src') or await img_elem.get_attribute('src') or ""
                    
                    valid_products.append({
                        'name': product_name,
                        'price': price,
                        'link': link or "",
                        'image': image_url
                    })
                    
                except Exception:
                    continue  # Skip this product if any error occurs
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return {
                "name": "",
                "price": 0,
                "link": "",
                "image": "",
                "error": str(e)
            }
        finally:
            await browser.close()
    
    # If no valid products found
    if not valid_products:
        return {
            "name": "",
            "price": 0,
            "link": "",
            "image": ""
        }
    
    # Find cheapest product
    cheapest = min(valid_products, key=lambda x: x['price'])
    
    return cheapest

# Synchronous wrapper for easier use
def extract_cheapest_product_playwright(url: str, target_product: str, headless: bool = True) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async Playwright scraper.
    """
    return asyncio.run(extract_cheapest_product_with_playwright(url, target_product, headless))

# Example usage
if __name__ == "__main__":
    # Example URL - you would use the actual Divar search URL
    divar_url = "https://divar.ir/s/tehran/mobile-phones?q=poco+x3+pro"
    
    result = extract_cheapest_product_playwright(
        url=divar_url,
        target_product="Poco x3 pro",
        headless=True  # Set to False to see the browser
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))