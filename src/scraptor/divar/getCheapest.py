import json
import re
import asyncio
from typing import Dict, Any, List
from playwright.async_api import async_playwright
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# NLP MODEL (ONCE)
# =========================
_MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# =========================
# TEXT NORMALIZATION
# =========================
def _normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# =========================
# STRONG TOKENS
# =========================
def _strong_tokens(text: str) -> set[str]:
    tokens = _normalize(text).split()
    out = set()
    for t in tokens:
        if any(ch.isdigit() for ch in t):
            out.add(t)
        elif len(t) >= 2:  # include short tokens for soft match
            out.add(t)
    return out

# =========================
# BRAND+MODEL CHECK (SOFTER)
# =========================
def _has_brand_model_soft(query: str, candidate: str) -> bool:
    q = _normalize(query)
    c = _normalize(candidate)

    q_tokens = q.split()
    brand_tokens = [t for t in q_tokens if not any(ch.isdigit() for ch in t)]
    model_tokens = [t for t in q_tokens if any(ch.isdigit() for ch in t)]

    brand_present = any(bt in c for bt in brand_tokens)
    model_present = any(mt in c for mt in model_tokens)

    # Soft: accept if either brand or model present
    return brand_present or model_present

# =========================
# SEMANTIC SIMILARITY
# =========================
def _semantic_similarity(a: str, b: str) -> float:
    vecs = _MODEL.encode([_normalize(a), _normalize(b)])
    return float(cosine_similarity([vecs[0]], [vecs[1]])[0][0])

# =========================
# TOKEN PENALTY
# =========================
def _token_penalty(query: str, candidate: str) -> float:
    q_tokens = _strong_tokens(query)
    c_text = _normalize(candidate)
    if not q_tokens:
        return 0.0
    missing = sum(1 for t in q_tokens if t not in c_text)
    return missing / len(q_tokens)

# =========================
# PRICE PARSER (PERSIAN)
# =========================
def _extract_price(text: str) -> int | None:
    if not text:
        return None
    persian_map = {
        '۰':'0','۱':'1','۲':'2','۳':'3','۴':'4',
        '۵':'5','۶':'6','۷':'7','۸':'8','۹':'9',
        '٠':'0','١':'1','٢':'2','٣':'3','٤':'4',
        '٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'
    }
    digits = ""
    for ch in text:
        if ch in persian_map:
            digits += persian_map[ch]
        elif ch.isdigit():
            digits += ch
    try:
        return int(digits) if digits else None
    except ValueError:
        return None

# =========================
# GET CHEAPEST AD (SOFTER + FALLBACK)
# =========================
async def getCheapestAdd(url: str, target_product: str, headless: bool = True) -> Dict[str, Any]:
    products: List[Dict[str, Any]] = []

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0"
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('a.kt-post-card__action', timeout=10000)
            cards = await page.locator('a.kt-post-card__action').all()

            for card in cards:
                try:
                    title_el = card.locator('h2.kt-post-card__title')
                    if await title_el.count() == 0:
                        continue
                    title = (await title_el.first.inner_text()).strip()
                    descs = await card.locator('div.kt-post-card__description').all()

                    price = None
                    for d in descs:
                        txt = await d.inner_text()
                        price = _extract_price(txt)
                        if price:
                            break

                    link = await card.get_attribute('href')
                    if link and not link.startswith("http"):
                        link = "https://divar.ir" + link

                    img_el = card.locator("img")
                    image = ""
                    if await img_el.count() > 0:
                        image = (await img_el.first.get_attribute("data-src")
                                 or await img_el.first.get_attribute("src") or "")

                    products.append({
                        "name": title,
                        "price": price,
                        "link": link or "",
                        "image": image
                    })
                except Exception:
                    continue
        finally:
            await browser.close()

    # Phase 1: Soft brand+model filter
    filtered = [p for p in products if _has_brand_model_soft(target_product, p["name"])]
    if not filtered:
        filtered = products  # fallback to all

    # Phase 2: NLP scoring
    scored = []
    for p in filtered:
        semantic = _semantic_similarity(target_product, p["name"])
        penalty = _token_penalty(target_product, p["name"])
        score = semantic - (penalty * 0.2)
        scored.append({**p, "score": score})

    # Phase 3: If nothing scored well, fallback to max semantic similarity only
    if not scored:
        fallback = [
            {**p, "score": _semantic_similarity(target_product, p["name"])}
            for p in products
        ]
        if fallback:
            best = max(fallback, key=lambda x: x["score"])
            best.pop("score", None)
            return best
        else:
            return {"error": "no products found even in fallback", "mode": "soft"}

    # Phase 4: Choose best by score then cheapest
    best = min(
        scored,
        key=lambda x: (-(x["score"]), x["price"] if x["price"] is not None else float("inf"))
    )
    best.pop("score", None)
    return best

# =========================
# SYNC WRAPPER
# =========================
def extract_cheapest_product_playwright(url: str, target_product: str, headless: bool = True) -> Dict[str, Any]:
    return asyncio.run(getCheapestAdd(url, target_product, headless))

# =========================
# EXAMPLE USAGE
# =========================
if __name__ == "__main__":
    url = "https://divar.ir/s/tehran/mobile-phones?q=iphone+16+pro"
    result = extract_cheapest_product_playwright(url, "iPhone 16 Pro", headless=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
