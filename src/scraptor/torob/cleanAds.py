import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from InitDAC import InitDAC


def getAds(page, amount, email, password):
    InitDAC()
    
    # Find div where class starts with "browse_leftContainer__"
    div = page.locator('div[class^="browse_leftContainer__"]')
    page.locator('div[class^="ProductImageSlider_wrapper__"]').evaluate_all('elements => elements.forEach(el => el.remove())')

    # Get ALL cards HTML from that div
    cards = div.locator('div[class^="ProductCard_desktop_card__"]')
    
    # Get the HTML of the entire cards container (first 'amount' cards)
    all_cards_html = ""
    for i in range(min(amount, cards.count())):
        all_cards_html += cards.nth(i).inner_html() + "\n\n"

    
    return all_cards_html

    