CATEGORIES = {
    "املاک": "خانه آپارتمان زمین ویلا ملک اجاره فروش رهن مسکونی اداری تجاری",
    "وسایل نقلیه": "خودرو ماشین موتور سیکلت سواری وانت کامیون پلاک",
    "کالای دیجیتال": "موبایل گوشی لپ تاپ تبلت کامپیوتر دوربین کنسول هدفون",
    "خانه و آشپزخانه": "مبلمان یخچال گاز لباسشویی تخت میز صندلی آشپزخانه",
    "خدمات": "تعمیر خدمات نظافت آموزش طراحی برنامه نویسی",
    "وسایل شخصی": "لباس کفش ساعت کیف عینک زیورآلات",
    "سرگرمی و فراغت": "دوچرخه ساز موسیقی کتاب بلیط کنسرت",
    "اجتماعی": "گم شده پیدا شد خیریه کمک",
    "تجهیزات و صنعتی": "ابزار دستگاه صنعتی کارگاهی دریل کمپرسور",
    "استخدام و کاریابی": "استخدام شغل کار تمام وقت پاره وقت"
}



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

texts = list(CATEGORIES.values())
labels = list(CATEGORIES.keys())

vectorizer = TfidfVectorizer(
    ngram_range=(1,2),
    analyzer="word"
)

category_vectors = vectorizer.fit_transform(texts)

def classify(text):
    text_vec = vectorizer.transform([text])
    sims = cosine_similarity(text_vec, category_vectors)[0]
    best_idx = sims.argmax()
    return labels[best_idx], sims[best_idx]



print(classify("پوکو x3 پرو سالم"))

print(classify("اجاره آپارتمان ۷۵ متری"))

print(classify("استخدام برنامه نویس اندروید"))
