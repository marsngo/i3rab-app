# config.py
import os

PRIMARY_KEY = os.getenv("GEMINI_API_KEY", "")

# قائمة المفاتيح (يمكنك إضافة أكثر من مفتاح مجاني لزيادة الحصة)
API_KEYS = [
    PRIMARY_KEY,
]
