# config.py
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# قائمة النماذج المتاحة مرتبة حسب الأولوية والسرعة
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
