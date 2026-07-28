import json
import re
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODEL_NAME
from prompts.system_prompts import SYSTEM_PARSING_PROMPT
from schemas.syntax_schema import ComprehensiveAnalysis

# تهيئة عميل Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def clean_json_string(text: str) -> str:
    """استخراج نص JSON النقي في حال وجود أي وسوم زائدة"""
    text = text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def analyze_arabic_text(text: str) -> ComprehensiveAnalysis:
    """
    دالة تحليل النص وإعرابه باستخدام Gemini API
    """
    prompt = f"{SYSTEM_PARSING_PROMPT}\n\nقم بإعراب وتحليل النص التالي مع الضبط الشامل والاستشهاد بالمراجع:\n{text}"

    try:
        # إرسال الطلب مع تحديد صيغة المخرجات المباشرة JSON
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComprehensiveAnalysis,
                temperature=0.1,
            ),
        )

        raw_text = response.text
        cleaned_json = clean_json_string(raw_text)
        
        # تحويل النتيجة إلى Pydantic Object
        parsed_data = ComprehensiveAnalysis.model_validate_json(cleaned_json)
        return parsed_data

    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بـ Gemini API: {e}")
        return None