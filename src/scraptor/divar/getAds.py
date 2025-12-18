import json

from bs4 import BeautifulSoup


def _persian_to_int(price_text: str) -> int | None:
    """Convert Divar-style Persian price text to integer toman."""
    if not price_text:
        return None

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    mapping = {ord(p): str(i) for i, p in enumerate(persian_digits)}
    normalized = price_text.translate(mapping)

    digits_only = "".join(ch for ch in normalized if ch.isdigit())
    if not digits_only:
        return None

    try:
        return int(digits_only)
    except ValueError:
        return None


def _extract_best_product_from_html(all_cards_html: str) -> str:
    """
    Parse Divar post cards HTML and return a JSON string with the
    "best" product (currently: the cheapest one).

    We support two shapes:
    - Full <article class="kt-post-card"> ... <a class="kt-post-card__action" href="/v/...">...</a>
    - Just the <a href="/v/...">...</a> fragment (what we usually capture in Playwright).
    """
    soup = BeautifulSoup(all_cards_html, "html.parser")

    products = []

    # First, try when we have full <article> wrappers (like example.html)
    for article in soup.select("article[class*='kt-post-card']"):
        link_el = article.select_one("a.kt-post-card__action[href^='/v/']")
        if not link_el:
            continue
        href = link_el.get("href") or ""

        # Product title
        name_el = article.select_one("h2[class*='kt-post-card__title']")
        if not name_el:
            continue
        name = " ".join(name_el.get_text(strip=True).split())

        # Price is usually one of the description divs containing 'تومان'
        price_el = None
        for desc in article.select("div[class*='kt-post-card__description']"):
            text = desc.get_text(strip=True)
            if "تومان" in text:
                price_el = desc
                break
        if not price_el:
            continue

        price_text = " ".join(price_el.get_text(strip=True).split())
        price = _persian_to_int(price_text)
        if price is None:
            continue

        # Thumbnail image
        img_el = article.select_one("img[src*='divarcdn.com']")
        image_url = img_el.get("src") if img_el else ""

        products.append(
            {
                "name": name,
                "price": price,
                "link": href,
                "image": image_url,
            }
        )

    # If Playwright only captured <a> fragments (no <article> around them)
    if not products:
        for link_el in soup.select("a[href^='/v/']"):
            href = link_el.get("href") or ""

            # Product title under this link
            name_el = link_el.select_one("h2[class*='kt-post-card__title']")
            if not name_el:
                continue
            name = " ".join(name_el.get_text(strip=True).split())

            # Price divs below this link
            price_el = None
            for desc in link_el.select("div[class*='kt-post-card__description']"):
                text = desc.get_text(strip=True)
                if "تومان" in text:
                    price_el = desc
                    break
            if not price_el:
                continue

            price_text = " ".join(price_el.get_text(strip=True).split())
            price = _persian_to_int(price_text)
            if price is None:
                continue

            img_el = link_el.select_one("img[src*='divarcdn.com']")
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
        return json.dumps(
            {"error": "no product cards found"},
            ensure_ascii=False,
            indent=4,
        )

    best = min(products, key=lambda p: p["price"])

    return json.dumps(best, ensure_ascii=False)


def getAds(page, amount, email, password, prod):
    """
    Collect Divar post cards HTML from the current page and
    return a JSON string describing the best product (cheapest),
    without using any AI.
    """

    # Try multiple strategies to get complete product cards
    all_cards_html = ""
    loaded_count = 0
    max_scroll_attempts = 10
    scroll_attempt = 0

    # First, try to get initial cards
    initial_cards = page.locator("article.kt-post-card")
    initial_count = initial_cards.count()
    loaded_count = initial_count

    # If we already have enough cards, proceed
    if loaded_count >= amount:
        for i in range(min(amount, initial_count)):
            try:
                card = initial_cards.nth(i)
                # Get the parent <a> tag that contains the entire card
                card_html = card.evaluate(
                    """
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
                """
                )
                all_cards_html += card_html + "\n\n"
            except Exception:
                pass

    # If not enough cards, scroll to load more
    else:
        while loaded_count < amount and scroll_attempt < max_scroll_attempts:
            # First, collect current cards
            current_cards = page.locator("article.kt-post-card")
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
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                # Wait for new content to load (adjust timeout as needed)
                page.wait_for_timeout(2000)

                # Check for loading indicators and wait if present
                loading_selectors = [
                    '[class*="loading"]',
                    '[class*="progress"]',
                    '[class*="skeleton"]',
                    '[aria-label*="loading"]',
                ]

                for selector in loading_selectors:
                    try:
                        if page.locator(selector).first.is_visible(timeout=1000):
                            page.wait_for_timeout(1000)
                    except Exception:
                        pass

            except Exception as e:
                print(f"Error during scroll: {e}")
                break

        # After scrolling, collect all cards up to the requested amount
        final_cards = page.locator("article.kt-post-card")
        final_count = final_cards.count()

        # Alternative strategy: try different selectors if article.kt-post-card doesn't work
        if final_count == 0:
            # Try other possible selectors
            selectors_to_try = [
                'article[class*="post-card"]',
                'div[class*="post-card"]',
                'a[class*="post-card"]',
                'div[class*="ProductCard"]',
                'a[href*="/v/"]',
            ]

            for selector in selectors_to_try:
                try:
                    final_cards = page.locator(selector)
                    final_count = final_cards.count()
                    if final_count > 0:
                        break
                except Exception:
                    continue

        # Collect the cards
        for i in range(min(amount, final_count)):
            try:
                card = final_cards.nth(i)
                # Get the full card HTML with its link
                card_html = card.evaluate(
                    """
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
                """
                )
                all_cards_html += card_html + "\n\n"
            except Exception as e:
                print(f"Error extracting card {i}: {e}")
                continue

    if not all_cards_html.strip():
        return json.dumps(
            {"error": "no product cards found"},
            ensure_ascii=False,
            indent=4,
        )

    # Parse collected HTML and build JSON without AI
    return _extract_best_product_from_html(all_cards_html)
