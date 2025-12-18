import os
import json

from bs4 import BeautifulSoup


def _persian_to_int(price_text: str) -> int | None:
    """Convert Torob-style Persian price text to integer toman."""
    if not price_text:
        return None

    # Map Persian digits to Latin
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    mapping = {ord(p): str(i) for i, p in enumerate(persian_digits)}
    normalized = price_text.translate(mapping)

    # Keep only ASCII digits
    digits_only = "".join(ch for ch in normalized if ch.isdigit())
    if not digits_only:
        return None

    try:
        return int(digits_only)
    except ValueError:
        return None


def _extract_best_product_from_html(all_cards_html: str) -> str:
    """
    Parse Torob product cards HTML and return a JSON string with the
    "best" product (currently: the cheapest one).

    Output JSON shape matches the existing torob.json:
    {
        "name": "...",
        "price": 123456,
        "link": "/p/...",
        "image": "https://image.torob.com/..."
    }
    """
    soup = BeautifulSoup(all_cards_html, "html.parser")

    products = []

    # Each product is wrapped by an <a href="/p/..."> that contains a product-card div
    for anchor in soup.select('a[href^="/p/"]'):
        href = anchor.get("href") or ""

        # Product name
        name_el = anchor.select_one('h2[class*="ProductCard_desktop_product-name"]')
        if not name_el:
            continue
        name = " ".join(name_el.get_text(strip=True).split())

        # Price text
        price_el = anchor.select_one(
            'div[class*="ProductCard_desktop_product-price-text"]'
        )
        if not price_el:
            continue
        price_text = " ".join(price_el.get_text(strip=True).split())
        price = _persian_to_int(price_text)
        if price is None:
            continue

        # Image (first image inside the card)
        img_el = anchor.select_one("img[src*='image.torob.com']")
        image_url = img_el.get("src") if img_el else ""

        products.append(
            {
                "name": name,
                "price": price,
                "link": href,
                "image": image_url,
            }
        )

    if not products:
        # Fallback JSON when nothing found
        return json.dumps(
            {"error": "no product cards found"},
            ensure_ascii=False,
            indent=4,
        )

    # Choose the cheapest product
    best = min(products, key=lambda p: p["price"])

    return json.dumps(best, ensure_ascii=False)


def getAds(page, amount, email, password, prod):
    """
    Collect Torob product cards HTML from the current page and
    return a JSON string describing the best product (cheapest),
    without using any AI.
    """

    # Try multiple strategies to get complete product cards
    all_cards_html = ""

    # Strategy 1: Get complete product cards with <a> tags
    try:
        cards = page.locator('a[href*="/p/"]')
        for i in range(min(amount, cards.count())):
            card_html = cards.nth(i).evaluate("(element) => element.outerHTML")
            all_cards_html += card_html + "\n\n"
    except Exception:
        pass

    # Strategy 2: If first strategy didn't work, get product cards by data-testid and find their parent containers
    if not all_cards_html.strip():
        try:
            cards = page.locator('[data-testid="product-card"]')
            for i in range(min(amount, cards.count())):
                card_html = cards.nth(i).evaluate(
                    """
                    (element) => {
                        // Try to find the parent <a> tag or return the card itself
                        let parent = element.closest('a');
                        return parent ? parent.outerHTML : element.outerHTML;
                    }
                """
                )
                all_cards_html += card_html + "\n\n"
        except Exception:
            pass

    # Strategy 3: Last resort - get whatever product containers we can find
    if not all_cards_html.strip():
        try:
            cards = page.locator('div[class*="ProductCard"]')
            for i in range(min(amount, cards.count())):
                card_html = cards.nth(i).evaluate(
                    "(element) => element.outerHTML"
                )
                all_cards_html += card_html + "\n\n"
        except Exception:
            pass

    if not all_cards_html.strip():
        # Nothing collected at all
        return json.dumps(
            {"error": "no product cards found"},
            ensure_ascii=False,
            indent=4,
        )

    # Parse collected HTML and build JSON without AI
    return _extract_best_product_from_html(all_cards_html)
