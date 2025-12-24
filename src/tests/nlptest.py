# nlptest.py
# Lightweight category classification using TF-IDF (char ngrams)
# Works with Persian + English + unknown products

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------
# Text normalization
# --------------------------------------------------
def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("ي", "ی").replace("ك", "ک")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# --------------------------------------------------
# Category definitions (DOMAIN KNOWLEDGE LIVES HERE)
# --------------------------------------------------
CATEGORIES = {
    "املاک": """
    خانه آپارتمان ویلا زمین ملک
    اجاره رهن فروش مسکونی اداری تجاری
    """,

    "وسایل نقلیه": """
    خودرو ماشین اتومبیل موتور سیکلت
    وانت کامیون پلاک
    """,

    "کالای دیجیتال": """
    موبایل گوشی تلفن همراه اسمارتفون
    اندروید آیفون
    لپ تاپ نوت بوک کامپیوتر
    تبلت
    سامسونگ شیائومی پوکو ردمی هواوی
    ram حافظه باتری پردازنده نمایشگر
    pro max ultra plus
    """,

    "خانه و آشپزخانه": """
    مبل مبلمان تخت میز صندلی
    یخچال فریزر گاز لباسشویی
    آشپزخانه
    """,

    "خدمات": """
    خدمات تعمیر نظافت آموزش
    طراحی برنامه نویسی
    """,

    "وسایل شخصی": """
    لباس کفش کیف ساعت
    عینک زیورآلات
    """,

    "سرگرمی و فراغت": """
    دوچرخه ساز موسیقی
    کتاب بلیط کنسرت
    """,

    "اجتماعی": """
    گم شده پیدا شد
    کمک خیریه
    """,

    "تجهیزات و صنعتی": """
    ابزار دستگاه صنعتی
    کارگاهی دریل کمپرسور
    """,

    "استخدام و کاریابی": """
    استخدام شغل کار
    تمام وقت پاره وقت
    برنامه نویس مهندس
    """
}

# --------------------------------------------------
# Prepare vectorizer
# --------------------------------------------------
labels = list(CATEGORIES.keys())
texts = [normalize(t) for t in CATEGORIES.values()]

vectorizer = TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(3, 5)
)

category_vectors = vectorizer.fit_transform(texts)

# --------------------------------------------------
# Rule overrides (cheap but powerful)
# --------------------------------------------------
def rule_override(text: str):
    t = text.lower()
    if "استخدام" in t:
        return "استخدام و کاریابی"
    if "اجاره" in t or "رهن" in t:
        return "املاک"
    if "گم شده" in t:
        return "اجتماعی"
    return None

# --------------------------------------------------
# Classifier
# --------------------------------------------------
def classify(text: str):
    text_norm = normalize(text)

    rule = rule_override(text_norm)
    if rule:
        return rule, 1.0

    vec = vectorizer.transform([text_norm])
    sims = cosine_similarity(vec, category_vectors)[0]

    idx = sims.argmax()
    return labels[idx], float(sims[idx])

# --------------------------------------------------
# Tests
# --------------------------------------------------
if __name__ == "__main__":
    tests = [
        "Poco x3 pro",
        "پوکو x3 پرو سالم",
        "اجاره آپارتمان ۷۵ متری",
        "استخدام برنامه نویس اندروید",
        "دریل صنعتی سه فاز",
        "Dell precision 5540",
        "هودی مردانه سایز لارج",
        "ماشین لباس شویی"
    ]

    for t in tests:
        print(t, "=>", classify(t))
