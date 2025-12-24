import json
import re
from bs4 import BeautifulSoup

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================
# NLP MODEL (LOAD ONCE)
# =========================
_MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


# =========================
# NORMALIZATION
# =========================
def _normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# STRONG TOKENS (IDENTITY)
# =========================
def _strong_tokens(text: str) -> set[str]:
    tokens = _normalize(text).split()
    out = set()

    for t in tokens:
        if any(ch.isdigit() for ch in t):
            out.add(t)
        elif len(t) >= 3:
            out.add(t)

    return out


# =========================
# EXACT MATCH CHECK
# =========================
def _exact_identity_match(query: str, title: str) -> bool:
    q = _normalize(query)
    t = _normalize(title)

    return q in t or t in q


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
# PRICE PARSER
# =========================
def _persian_to_int(price_text: str) -> int | None:
    if not price_text:
        return None

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    mapping = {ord(p): str(i) for i, p in enumerate(persian_digits)}
    normalized = price_text.translate(mapping)

    digits = "".join(ch for ch in normalized if ch.isdigit())
    if not digits:
        return None

    try:
        return int(digits)
    except ValueError:
        return None


# =========================
# CORE LOGIC
# =========================
def _extract_best_product_from_html(
    all_cards_html: str,
    user_query: str,
) -> str:
    soup = BeautifulSoup(all_cards_html, "html.parser")
    candidates = []

    for anchor in soup.select('a[href^="/p/"]'):
        name_el = anchor.select_one(
            'h2[class*="ProductCard_desktop_product-name"]'
        )
        if not name_el:
            continue

        name = " ".join(name_el.get_text(strip=True).split())
        href = anchor.get("href") or ""

        price_el = anchor.select_one(
            'div[class*="ProductCard_desktop_product-price-text"]'
        )
        price = None
        if price_el:
            price = _persian_to_int(
                " ".join(price_el.get_text(strip=True).split())
            )

        img_el = anchor.select_one("img")
        image_url = img_el.get("src") if img_el else ""

        candidates.append(
            {
                "name": name,
                "price": price,
                "link": href,
                "image": image_url,
            }
        )

    if not candidates:
        return json.dumps(
            {"error": "no products found"},
            ensure_ascii=False,
            indent=4,
        )

    # =========================
    # PHASE 1: IDENTITY CHECK
    # =========================
    exact_matches = [
        c for c in candidates
        if _exact_identity_match(user_query, c["name"])
    ]

    strict_mode = bool(exact_matches)

    scored = []

    for c in candidates:
        semantic = _semantic_similarity(user_query, c["name"])
        penalty = _token_penalty(user_query, c["name"])

        if strict_mode:
            final_score = semantic - (penalty * 0.4)
            threshold = 0.45
        else:
            final_score = semantic - (penalty * 0.15)
            threshold = 0.35

        if final_score < threshold:
            continue

        scored.append(
            {
                **c,
                "score": final_score,
            }
        )

    if not scored:
        return json.dumps(
            {
                "error": "no sufficiently relevant product found",
                "mode": "strict" if strict_mode else "soft",
            },
            ensure_ascii=False,
            indent=4,
        )

    # Rank: relevance first, then price
    best = max(
        scored,
        key=lambda r: (
            r["score"],
            -(r["price"] or float("inf")),
        ),
    )

    best.pop("score", None)

    return json.dumps(best, ensure_ascii=False, indent=4)


# =========================
# PUBLIC ENTRY (PLAYWRIGHT)
# =========================
def getAds(page, amount: int, user_query: str) -> str:
    all_cards_html = ""

    try:
        cards = page.locator('a[href^="/p/"]')
        for i in range(min(amount, cards.count())):
            all_cards_html += cards.nth(i).evaluate(
                "(el) => el.outerHTML"
            ) + "\n"
    except Exception:
        pass

    if not all_cards_html.strip():
        try:
            cards = page.locator('div[class*="ProductCard"]')
            for i in range(min(amount, cards.count())):
                all_cards_html += cards.nth(i).evaluate(
                    "(el) => el.outerHTML"
                ) + "\n"
        except Exception:
            pass

    if not all_cards_html.strip():
        return json.dumps(
            {"error": "failed to collect ads"},
            ensure_ascii=False,
            indent=4,
        )

    return _extract_best_product_from_html(
        all_cards_html,
        user_query,
    )
