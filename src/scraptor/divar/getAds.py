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
    return int(digits_only) if digits_only else None


def _extract_relevant_products(all_cards_html: str, target_product: str) -> list[dict]:
    """Parse HTML and return all relevant products based on target product."""
    soup = BeautifulSoup(all_cards_html, "html.parser")
    products = []

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

        # Price
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

        # Robust image extraction: prefer <picture> images, then img with divarcdn, then data-* attrs
        def _normalize_url(url: str) -> str:
            if not url:
                return ""
            url = url.strip().strip('"\'')
            if url.startswith("//"):
                return "https:" + url
            if url.startswith("/"):
                return "https://divar.ir" + url
            return url

        def _extract_image(el):
            if not el:
                return ""
            # picture > img
            pic_img = el.select_one("picture img[src]")
            if pic_img:
                val = pic_img.get("src") or pic_img.get("srcset")
                if val:
                    if "," in val:
                        first = [p.strip() for p in val.split(',') if p.strip()][0].split()[0]
                        return _normalize_url(first)
                    return _normalize_url(val)

            # img with divarcdn
            img_el = el.select_one("img[src*='divarcdn.com']")
            if img_el:
                val = img_el.get("src") or img_el.get("data-src") or img_el.get("srcset")
                if val:
                    if "," in val:
                        first = [p.strip() for p in val.split(',') if p.strip()][0].split()[0]
                        return _normalize_url(first)
                    return _normalize_url(val)

            # any slide img
            slide_img = el.select_one(".kt-post-card__photo img[src]")
            if slide_img:
                val = slide_img.get("src") or slide_img.get("data-src") or slide_img.get("srcset")
                if val:
                    if "," in val:
                        first = [p.strip() for p in val.split(',') if p.strip()][0].split()[0]
                        return _normalize_url(first)
                    return _normalize_url(val)

            # data-* attributes
            for attr in ("data-image", "data-src", "data-bg", "data-original"):
                candidate = el.get(attr)
                if candidate:
                    return _normalize_url(candidate)

            return ""

        image_url = _extract_image(article)

        # Simple relevance check
        if target_product.lower() in name.lower():
            products.append({
                "name": name,
                "price": price,
                "link": href,
                "image": image_url
            })

    return products


def getAds(page, amount, email, password, target_product):
    """Collect Divar ads and return the cheapest relevant ad."""
    all_cards_html = ""
    cards = page.locator("article.kt-post-card")
    for i in range(min(amount, cards.count())):
        try:
            card_html = cards.nth(i).evaluate(
                "(el) => el.outerHTML"
            )
            all_cards_html += card_html + "\n\n"
        except Exception:
            continue

    if not all_cards_html.strip():
        return json.dumps({"error": "no product cards found"}, ensure_ascii=False, indent=4)

    products = _extract_relevant_products(all_cards_html, target_product)
    if not products:
        return json.dumps({"error": "no matching ads after hard filtering"}, ensure_ascii=False, indent=4)

    cheapest = min(products, key=lambda x: x["price"])
    return json.dumps(cheapest, ensure_ascii=False)
