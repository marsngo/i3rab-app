from pydantic import BaseModel, Field
from typing import List, Optional

class WordMorphology(BaseModel):
    root: str = Field(description="جذر الكلمة، مثل: كتب")
    weight: str = Field(description="الوزن الصرفي، مثل: فَاعِل")
    word_type: str = Field(description="نوع الكلمة: اسم، فعل، حرف، مشتق...")
    derivation_details: Optional[str] = Field(None, description="تفاصيل الإعلال أو الإبدال أو الزيادة إن وجد")

class WordParsing(BaseModel):
    irab: str = Field(description="الإعراب التفصيلي للكلمة")
    reason: str = Field(description="التعليل النحوي أو سبب الإعراب بناء على القواعد")

class WordAnalysis(BaseModel):
    word: str = Field(description="الكلمة كما وردت")
    diacritization: str = Field(description="الكلمة بعد الضبط بالشكل التام")
    pos: str = Field(description="القسم: اسم / فعل / حرف")
    parsing: WordParsing
    morphology: WordMorphology

class SentenceParsing(BaseModel):
    sub_sentence: str = Field(description="الجملة الفرعية أو المركبة")
    irab_location: str = Field(description="محل الجملة من الإعراب (مثلاً: في محل رفع خبر)")

class QuranReference(BaseModel):
    surah: str = Field(description="اسم السورة")
    ayah: int = Field(description="رقم الآية")

class ComprehensiveAnalysis(BaseModel):
    sentence: str = Field(description="الجملة الأصلية مضبوطة بالشكل")
    is_quranic: bool = Field(description="هل الجملة آية قرآنية؟")
    quran_reference: Optional[QuranReference] = None
    words_analysis: List[WordAnalysis]
    sentences_analysis: List[SentenceParsing]
    references: List[str] = Field(description="المراجع التراثية المعتمد عليها في الإعراب")