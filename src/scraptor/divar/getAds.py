import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.AiAnalysor.Mods.Message import SendGetMessage

def getAds(page, amount, email, password, prod):
    
    # Try multiple strategies to get complete product cards
    
    all_cards_html = ""
    loaded_count = 0
    max_scroll_attempts = 10
    scroll_attempt = 0
    
    # First, try to get initial cards
    initial_cards = page.locator('article.kt-post-card')
    initial_count = initial_cards.count()
    loaded_count = initial_count
    
    # If we already have enough cards, proceed
    if loaded_count >= amount:
        for i in range(min(amount, initial_count)):
            try:
                card = initial_cards.nth(i)
                # Get the parent <a> tag that contains the entire card
                card_html = card.evaluate('''
                    (element) => {
                        // Try to find the closest parent <a> tag
                        let parent = element.closest('a');
                        if (parent) {
                            return parent.outerHTML;
                        }
                        // If no parent <a>, try to find the <a> inside
                        let link = element.querySelector('a');
                        return link ? link.outerHTML : element.outerHTML;
                    }
                ''')
                all_cards_html += card_html + "\n\n"
            except:
                pass
    
    # If not enough cards, scroll to load more
    else:
        while loaded_count < amount and scroll_attempt < max_scroll_attempts:
            # First, collect current cards
            current_cards = page.locator('article.kt-post-card')
            current_count = current_cards.count()
            
            # If no new cards loaded after scroll, break
            if current_count <= loaded_count:
                scroll_attempt += 1
            else:
                loaded_count = current_count
                scroll_attempt = 0
            
            # Scroll down to load more content
            try:
                # Scroll to the bottom of the page
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                
                # Wait for new content to load (adjust timeout as needed)
                page.wait_for_timeout(2000)
                
                # Check for loading indicators and wait if present
                loading_selectors = [
                    '[class*="loading"]', 
                    '[class*="progress"]',
                    '[class*="skeleton"]',
                    '[aria-label*="loading"]'
                ]
                
                for selector in loading_selectors:
                    try:
                        if page.locator(selector).first.is_visible(timeout=1000):
                            page.wait_for_timeout(1000)
                    except:
                        pass
                        
            except Exception as e:
                print(f"Error during scroll: {e}")
                break
        
        # After scrolling, collect all cards up to the requested amount
        final_cards = page.locator('article.kt-post-card')
        final_count = final_cards.count()
        
        # Alternative strategy: try different selectors if article.kt-post-card doesn't work
        if final_count == 0:
            # Try other possible selectors
            selectors_to_try = [
                'article[class*="post-card"]',
                'div[class*="post-card"]',
                'a[class*="post-card"]',
                'div[class*="ProductCard"]',
                'a[href*="/v/"]'
            ]
            
            for selector in selectors_to_try:
                try:
                    final_cards = page.locator(selector)
                    final_count = final_cards.count()
                    if final_count > 0:
                        break
                except:
                    continue
        
        # Collect the cards
        for i in range(min(amount, final_count)):
            try:
                card = final_cards.nth(i)
                # Get the full card HTML with its link
                card_html = card.evaluate('''
                    (element) => {
                        // If element is already an <a> tag, return it
                        if (element.tagName.toLowerCase() === 'a') {
                            return element.outerHTML;
                        }
                        
                        // Try to find parent <a> tag
                        let parent = element.closest('a');
                        if (parent) {
                            return parent.outerHTML;
                        }
                        
                        // Try to find child <a> tag
                        let childLink = element.querySelector('a');
                        if (childLink) {
                            return childLink.outerHTML;
                        }
                        
                        // Fallback: return the element itself
                        return element.outerHTML;
                    }
                ''')
                all_cards_html += card_html + "\n\n"
            except Exception as e:
                print(f"Error extracting card {i}: {e}")
                continue
    
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