import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.AiAnalysor.Mods.Message import SendGetMessage


def getAds(page, amount, email, password, prod):
    
    # Try multiple strategies to get complete product cards
    
    all_cards_html = ""
    
    # Strategy 1: Get complete product cards with <a> tags
    try:
        cards = page.locator('a[href*="/p/"]')
        for i in range(min(amount, cards.count())):
            card_html = cards.nth(i).evaluate('(element) => element.outerHTML')
            all_cards_html += card_html + "\n\n"
    except:
        pass
    
    # Strategy 2: If first strategy didn't work, get product cards by data-testid and find their parent containers
    if not all_cards_html.strip():
        try:
            cards = page.locator('[data-testid="product-card"]')
            for i in range(min(amount, cards.count())):
                card_html = cards.nth(i).evaluate('''
                    (element) => {
                        // Try to find the parent <a> tag or return the card itself
                        let parent = element.closest('a');
                        return parent ? parent.outerHTML : element.outerHTML;
                    }
                ''')
                all_cards_html += card_html + "\n\n"
        except:
            pass
    
    # Strategy 3: Last resort - get whatever product containers we can find
    if not all_cards_html.strip():
        try:
            cards = page.locator('div[class*="ProductCard"]')
            for i in range(min(amount, cards.count())):
                card_html = cards.nth(i).evaluate('(element) => element.outerHTML')
                all_cards_html += card_html + "\n\n"
        except:
            pass
    
    # Send the HTML to be processed and get back the filtered cards
    if all_cards_html.strip():
        tempcards = SendGetMessage(all_cards_html, email, password, page, prod) 
        all_cards_html = tempcards
    else:
        all_cards_html = """
{
    "error": "no product cards found"
}"""
    
    return all_cards_html