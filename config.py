import os

# يقرأ المفتاح من متغيرات البيئة السرية، وفي حال عدم وجوده يرجع نصاً فارغاً
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

MODEL_NAME = "gemini-1.5-flash"
