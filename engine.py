# engine.py
import json
import random
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from config import API_KEYS, AVAILABLE_MODELS
from prompts.system_prompts import SYSTEM_PROMPT

# --- نماذج البيانات (Pydantic Models) ---
class ParsingInfo(BaseModel):
    irab: str = Field(description="الإعراب التفصيلي للكلمة")
    reason: str = Field(description="التعليل النحوي وسبب الحركة")

class MorphologyInfo(BaseModel):
    root: str = Field(description="الجذر الثلاثي للكلمة")
    weight: str = Field(description="الوزن الصرفي")
    word_type: str = Field(description="جامد (ذات/معنى) أم مشتق وأنواعه")
    derivation_details: Optional[str] = Field(None, description="تفاصيل المشتق أو مصدر الفعل")

class WordAnalysis(BaseModel):
    word: str = Field(description="الكلمة كما وردت في النص")
    diacritization: str = Field(description="الكلمة مع التشكيل الكامل")
    pos: str = Field(description="اسم، فعل، حرف")
    parsing: ParsingInfo
    morphology: MorphologyInfo

class SentenceAnalysis(BaseModel):
    sub_sentence: str = Field(description="الجملة الفرعية أو الشبه جملة")
    irab_location: str = Field(description="المحل الإعرابي للجملة (في محل رفع/نصب/لا محل لها...)")

class QuranReference(BaseModel):
    surah: str = Field(description="اسم السورة")
    ayah: int = Field(description="رقم الآية")

class TextAnalysisResponse(BaseModel):
    original_text: str
    is_quranic: bool
    quran_reference: Optional[QuranReference] = None
    words_analysis: List[WordAnalysis]
    sentences_analysis: List[SentenceAnalysis]
    references: List[str]

# --- دالة التدوير والاحتياط الذكي العامة ---
def generate_content_with_fallback(prompt: str) -> str:
    """
    تستدعي نماذج Gemini المتاحة بالتتابع مع تدوير المفاتيح.
    إذا فشل نموذج بـ 404 أو 429، تنتقل تلقائياً للنموذج أو المفتاح التالي.
    """
    # تصفية المفاتيح الفعالة
    valid_keys = [k for k in API_KEYS if k.strip()]
    if not valid_keys:
        raise Exception("لم يتم العثور على أي مفتاح API صالح في ملف config.py")

    last_error = None

    # تجربة المفاتيح والنماذج
    for api_key in valid_keys:
        client = genai.Client(api_key=api_key)
        for model in AVAILABLE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_error = e
                # الانتقال للنموذج أو المفتاح التالي صامتاً
                continue

    raise Exception(f"تعذر الاتصال بجميع النماذج والمفاتيح المتاحة. الخطأ الأخير: {last_error}")

# --- دالة تحليل النص النحوي (الإعراب) ---
def analyze_arabic_text(text: str) -> Optional[TextAnalysisResponse]:
    """
    تحليل النص النحوي باستخدام النظام الاحتياطي للحصول على نتيجة Structured JSON
    """
    valid_keys = [k for k in API_KEYS if k.strip()]
    if not valid_keys:
        return None

    last_error = None
    prompt = f"{SYSTEM_PROMPT}\n\nالنص المراد تحليله وإعرابه:\n{text}"

    for api_key in valid_keys:
        client = genai.Client(api_key=api_key)
        for model in AVAILABLE_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': TextAnalysisResponse,
                    }
                )
                return TextAnalysisResponse.model_validate_json(response.text)
            except Exception as e:
                last_error = e
                continue

    print(f"Error in analyze_arabic_text: {last_error}")
    return None
