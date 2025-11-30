import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.AiAnalysor.Mods.Message import SendGetMessage


def getAds(page, page2, amount, email, password):
    
    # Find div where class starts with "browse_leftContainer__"
    div = page.locator('div[class^="browse_leftContainer__"]')
    page.locator('div[class^="ProductImageSlider_wrapper__"]').evaluate_all('elements => elements.forEach(el => el.remove())')

    # Get ALL cards HTML from that div
    cards = div.locator('div[class^="ProductCard_desktop_card__"]')
    
    # Get the HTML of the entire cards container (first 'amount' cards)
    all_cards_html = ""
    for i in range(min(amount, cards.count())):
        all_cards_html += cards.nth(i).inner_html() + "\n\n"
    
    tempcards = SendGetMessage(all_cards_html, email, password, page) 

    all_cards_html = tempcards
    


    
    return all_cards_html

    