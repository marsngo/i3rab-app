# config.py
import os

# جلب المفتاح الرئيسي من متغيرات البيئة (Streamlit Secrets أو .env)
PRIMARY_KEY = os.getenv("GEMINI_API_KEY", "")

# قائمة المفاتيح المتاحة للتنقل والتدوير
API_KEYS = [
    PRIMARY_KEY,
]

# قائمة النماذج المتاحة للتنقل التلقائي عند انشغال النموذج أو استنفاد الحصة
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
