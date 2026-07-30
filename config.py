# config.py
import os

PRIMARY_KEY = os.getenv("GEMINI_API_KEY", "")

# قائمة المفاتيح المتاحة (يفضل إضافة مفاتيح من حسابات Google مجانية أخرى هنا لزيادة السعة)
API_KEYS = [
    PRIMARY_KEY,
    # "مفتاح_مجاني_ثاني_من_حساب_آخر",
]

# قائمة النماذج المجانية المستقرة والفعالة (بدون نماذج الـ Pro غير المتاحة مجاناً)
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-002",
]
