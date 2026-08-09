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

# --- 1. نماذج الإعراب (Parsing Models) ---
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

# --- 2. نماذج البلاغة والعروض (Rhetoric & Meter Models) ---
class ImageryAnalysis(BaseModel):
    phrase: str = Field(description="التركيب البلاغي أو الصورة من البيت")
    image_type: str = Field(description="نوع الصورة: استعارة مكنية/تصريحية، تشبيه تام/مؤكد/مجمل/بليغ، كناية")
    explanation: str = Field(description="شرح الصورة البلاغية وأركانها وسر جمالها")

class RhetoricalDevisor(BaseModel):
    device_type: str = Field(description="المحسن البديعي: طباق، جناس، تصريع، مقابلة...")
    words: str = Field(description="الكلمات التي تحقق فيها المحسن")
    impact: str = Field(description="الأثر الفني للمحسن البديعي")

class ProsodyAnalysis(BaseModel):
    meter_name: str = Field(description="اسم البحر الشعري (مثال: البحر الطويل، الخفيف...)")
    taftilahs: str = Field(description="التفاعيل العروضية للبيت (مثل: فعولن مفاعيلن...)")
    scansion_code: str = Field(description="التقطيع العروضي بالرموز (///o //o ///o...)")
    rhyme_and_rawi: str = Field(description="تحديد القافية وحرف الروي مع حركته")

class RhetoricMeterResponse(BaseModel):
    verse: str
    imagery: List[ImageryAnalysis]
    rhetorical_devices: List[RhetoricalDevisor]
    prosody: ProsodyAnalysis

# --- دالة اكتشاف النماذج المتاحة ديناميكياً ---
def get_working_models(client) -> List[str]:
    try:
        available_models = []
        for m in client.models.list():
            if "generateContent" in getattr(m, 'supported_generation_methods', []) or hasattr(m, 'name'):
                name = m.name.replace("models/", "")
                if "flash" in name and "embed" not in name:
                    available_models.append(name)
        if available_models:
            return sorted(available_models, key=lambda x: ("flash" not in x, x))
    except Exception:
        pass
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

# --- دالة التحليل البلاغي والعروضي المضافة ---
def analyze_rhetoric_and_meter(text: str) -> Optional[RhetoricMeterResponse]:
    valid_keys = [k for k in API_KEYS if k and k.strip()]
    if not valid_keys:
        return None

    prompt = f"""
    أنت خبير في البلاغة العربية والعروض. قم بتقديم تحليل بلاغي وعروضي دقيق للبيت الشعري التالي:
    "{text}"
    تنبيه: أخرج التحليل بدقة عالية دون كتابة أي أسئلة أو مجاملات تفاعلية في النهاية.
    """

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
                        'response_schema': RhetoricMeterResponse,
                    }
                )
                return RhetoricMeterResponse.model_validate_json(response.text)
            except Exception as e:
                continue

    return None

# --- 3. نماذج مُمرّن الإعراب التفاعلي (Quiz Models) ---
class QuizOption(BaseModel):
    option_text: str = Field(description="نص الخيار الإعرابي (مثال: فاعل مرفوع وعلامة رفعه الضمة)")
    is_correct: bool = Field(description="هل هذا الخيار هو الإجابة الصحيحة؟")
    explanation: str = Field(description="توضيح مختصر لسبب صحة أو خطأ هذا الخيار")

class QuizQuestion(BaseModel):
    sentence: str = Field(description="الجملة أو البيت الشعري الحاوي على الكلمة المستهدفة")
    target_word: str = Field(description="الكلمة المحددة للإعراب")
    question_text: str = Field(description="صياغة السؤال (مثال: ما الإعراب الصحيح لكلمة '...' في الجملة؟)")
    options: List[QuizOption] = Field(description="قائمة بـ 4 خيارات إعرابية (واحد منها فقط صحيح)")
    hint: str = Field(description="تلميح نحوي ذكي للمساعدة دون إعطاء الإجابة مباشرة")

# --- دالة توليد سؤال إعرابي تفاعلي ---
def generate_grammar_quiz(grade: str, branch: str) -> Optional[QuizQuestion]:
    valid_keys = [k for k in API_KEYS if k and k.strip()]
    if not valid_keys:
        return None

    prompt = f"""
    قم بصياغة سؤال إعرابي تفاعلي مبتكر ومناسب لطلاب {grade} ({branch}) بناءً على الشواهد والأبيات المقررة في كتاب اللغة العربية السوري.
    اختر جملة أو بيتاً شعرياً، وحدد كلمة واحدة مميزة فيه، وضع 4 خيارات إعرابية دقيقة (خيار واحد صحيح و 3 خيارات خاطئة لكنها منطقية للتمويه).
    تنبيه: أخرج النتيجة بتنسيق JSON المطابق للنموذج فقط وتوقف فوراً دون أية أسئلة أو مقدمات.
    """

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
                        'response_schema': QuizQuestion,
                    }
                )
                return QuizQuestion.model_validate_json(response.text)
            except Exception as e:
                continue

    return None
