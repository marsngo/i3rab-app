# engine.py
import json
import random
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from config import API_KEYS

# --- النص التوجيهي للنظام ---
SYSTEM_PROMPT = """
أنت خبير ونحوي متخصص في اللغة العربية والإعراب التفصيلي، ومكلف بتحليل النصوص والنصوص القرآنية بدقة عالية.
قم بتحليل النص المدخل وإعرابه مفردات وجلماً، مع توضيح الصرف والجذور والأوزان بدقة متناهية.
"""

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

# --- دالة اكتشاف النماذج المتاحة ديناميكياً ---
def get_working_models(client) -> List[str]:
    """
    تستعلم من Google API عن جميع النماذج المتاحة فعلياً والحية للحساب
    """
    try:
        available_models = []
        for m in client.models.list():
            # نختار النماذج التي تدعم توليد النصوص فقط وتجنب نماذج الصور أو الصوت
            if "generateContent" in getattr(m, 'supported_generation_methods', []) or hasattr(m, 'name'):
                name = m.name.replace("models/", "")
                if "flash" in name and "embed" not in name:
                    available_models.append(name)
        
        # إذا وجد نماذج نضع نماذج flash في البداية لأنها الأسرع والأعلى في الحصة المجانية
        if available_models:
            return sorted(available_models, key=lambda x: ("flash" not in x, x))
    except Exception:
        pass
    
    # القائمة الاحتياطية المباشرة في حال تعذر الاستعلام
    return ["gemini-2.5-flash", "gemini-2.0-flash"]

# --- دالة التدوير والاحتياط الذكي العامة ---
def generate_content_with_fallback(prompt: str) -> str:
    valid_keys = [k for k in API_KEYS if k and k.strip()]
    if not valid_keys:
        raise Exception("لم يتم العثور على أي مفتاح API صالح. يرجى إضافته في Streamlit Secrets أو config.py")

    last_error = None

    for api_key in valid_keys:
        client = genai.Client(api_key=api_key)
        models_to_try = get_working_models(client)
        
        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_error = e
                continue

    raise Exception(f"تعذر الاتصال بجميع النماذج والمفاتيح المتاحة. الخطأ الأخير: {last_error}")

# --- دالة تحليل النص النحوي (الإعراب) ---
def analyze_arabic_text(text: str) -> Optional[TextAnalysisResponse]:
    valid_keys = [k for k in API_KEYS if k and k.strip()]
    if not valid_keys:
        return None

    last_error = None
    prompt = f"{SYSTEM_PROMPT}\n\nالنص المراد تحليله وإعرابه:\n{text}"

    for api_key in valid_keys:
        client = genai.Client(api_key=api_key)
        models_to_try = get_working_models(client)
        
        for model in models_to_try:
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
