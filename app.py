import streamlit as st
from engine import analyze_arabic_text
from lesson_generator import create_formatted_lesson_docx
from config import GEMINI_API_KEY, MODEL_NAME
from google import genai
from prompts.system_prompts import LESSON_GENERATOR_PROMPT

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="المعرّب الذكي",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. التنسيق (CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

* {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
}

.stApp {
    background-color: #1e293b !important;
    color: #f8fafc !important;
}

#MainMenu, header, footer {
    visibility: hidden;
}

/* حاوية البطاقات */
.word-cards-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 15px;
    width: 100%;
}

/* تصميم البطاقة */
.word-card {
    background: #0f172a !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.word-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1e40af;
    padding-bottom: 10px;
    margin-bottom: 12px;
}

.word-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #38bdf8 !important;
}

.word-pos {
    background: #2563eb !important;
    color: #ffffff !important;
    font-size: 0.85rem;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
}

.card-section {
    font-size: 1rem;
    line-height: 1.7;
    margin-bottom: 10px;
    color: #f8fafc !important;
}

.section-label {
    color: #93c5fd !important;
    font-weight: 700;
}

.morpho-box {
    margin-top: 12px;
    padding: 10px;
    background: #1e293b !important;
    border-radius: 10px;
    border: 1px solid #475569 !important;
}

.morpho-item {
    color: #4ade80 !important;
    margin-bottom: 4px;
}

.morpho-item.details {
    color: #facc15 !important;
}

.footer-container {
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid #334155;
    text-align: center;
    background: #0f172a;
    border-radius: 12px;
    color: #94a3b8;
}

.footer-container a {
    color: #38bdf8;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# --- 3. الهيدر ---
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 style='font-size: 2.5rem; color: #38bdf8; font-weight: 800;'>📖 المِعْرَبُ الذَّكِيّ</h1>
    <p style='font-size: 1.1rem; color: #cbd5e1;'>منصة التحليل النحوي والصرفي المتقدمة واستخراج خطط الدروس بالذكاء الاصطناعي</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 تحليل النص والإعراب", "📚 تحضير درس للمعلم (.docx)"])

with tab1:
    input_text = st.text_area(
        "أدخل الجملة أو الآية القرآنية:",
        placeholder="مثال: لَوْ جَاءَ مُعْتَذِرًا",
        height=100
    )
    
    if st.button("أعرب وحلّل النص ⚡", key="btn_parse"):
        if not input_text.strip():
            st.error("رجاءً أدخل نصاً للتحليل.")
        else:
            with st.spinner("جاري التحليل النحوي والصرفي..."):
                result = analyze_arabic_text(input_text)
                
            if not result:
                st.error("حدث خطأ أثناء معالجة النص. يرجى التحقق من الاتصال والمفتاح.")
            else:
                st.markdown("### 🔤 تحليل المفردات والصرف")
                
                # بناء الـ HTML الصحيح للبطاقات مع تنظيف الكود
                cards_html = "<div class=\"word-cards-container\">"
                for item in result.words_analysis:
                    cards_html += f"""
                    <div class="word-card">
                        <div class="word-header">
                            <span class="word-title">{item.diacritization}</span>
                            <span class="word-pos">{item.pos}</span>
                        </div>
                        <div class="card-section">
                            <span class="section-label">📌 الإعراب:</span> {item.parsing.irab}
                        </div>
                        <div class="card-section">
                            <span class="section-label">💡 التعليل النحوي:</span> {item.parsing.reason}
                        </div>
                        <div class="morpho-box">
                            <div class="morpho-item">🌱 <b>الجذر:</b> {item.morphology.root}</div>
                            <div class="morpho-item">⚖️ <b>الوزن:</b> {item.morphology.weight}</div>
                            <div class="morpho-item">🔍 <b>النوع:</b> {item.morphology.word_type}</div>
                            {f'<div class="morpho-item details">⚙️ {item.morphology.derivation_details}</div>' if item.morphology.derivation_details else ''}
                        </div>
                    </div>
                    """
                cards_html += "</div>"
                
                # إظهار البطاقات بالخاصية الصحيحة
                st.markdown(cards_html, unsafe_allow_html=True)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 🧩 إعراب الجمل")
                    if result.sentences_analysis:
                        for s in result.sentences_analysis:
                            st.markdown(f"🔹 **جملة `{s.sub_sentence}`:**\n{s.irab_location}")
                    else:
                        st.info("لا توجد جمل ذات محل إعرابي مستقل في هذا النص.")
                        
                with col2:
                    st.markdown("### 📚 المراجع والمصادر")
                    if result.is_quranic and result.quran_reference:
                        st.markdown(f"📖 **المصدر القرآني:** سورة **{result.quran_reference.surah}** - الآية **({result.quran_reference.ayah})**")
                    
                    st.markdown("**المراجع النحوية والصرفية:**")
                    for ref in result.references:
                        st.markdown(f"* {ref}")

with tab2:
    lesson_topic = st.text_input(
        "عنوان أو موضوع الدرس النحوي/الصرفي:",
        placeholder="مثال: أحكام المفعول لأجله"
    )
    
    if st.button("توليد خطة الدرس والتصدير إلى Word 📄", key="btn_lesson"):
        if not lesson_topic.strip():
            st.warning("يرجى كتابة عنوان الدرس أولاً.")
        else:
            with st.spinner("جاري صياغة خطة الدرس..."):
                try:
                    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                    prompt = f"{LESSON_GENERATOR_PROMPT}\n\nقم بإعداد خطة درس متكاملة ومفصلة حول موضوع: {lesson_topic}"
                    
                    response = gemini_client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                    )
                    
                    lesson_content = response.text
                    filename = f"درس_{lesson_topic.replace(' ', '_')}.docx"
                    file_path = create_formatted_lesson_docx(lesson_topic, lesson_content, filename)
                    
                    st.success("تم تجهيز الدرس بنجاح!")
                    
                    with open(file_path, "rb") as fp:
                        st.download_button(
                            label="📥 تحميل ملف الـ Word",
                            data=fp,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        
                    st.markdown("---")
                    st.markdown(lesson_content)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء إعداد الدرس: {e}")

# --- 4. التوقيع ---
st.markdown("""
<div class='footer-container'>
    <p>تصميم وتطوير: <b>مهيدي الخالدي</b> | <a href='mailto:alkhaldimhedy@gmail.com'>alkhaldimhedy@gmail.com</a></p>
    <p>جميع الحقوق محفوظة © 2026 | الإصدار: <b>v1.0.0</b></p>
</div>
""", unsafe_allow_html=True)
