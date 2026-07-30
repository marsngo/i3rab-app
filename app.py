import streamlit as st
import json
import os
from engine import analyze_arabic_text, generate_content_with_fallback
from lesson_generator import create_formatted_lesson_docx
from prompts.system_prompts import LESSON_GENERATOR_PROMPT
from prompts.syrian_curriculum import SYRIAN_CURRICULUM_PROMPT, SYRIAN_EXAM_PROMPT
from syrian_data import SYRIAN_9TH_CURRICULUM, SYRIAN_BAC_CURRICULUM

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="المعرّب الذكي | المنصة التعليمية المتكاملة",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. تنسيق الـ CSS المحسّن بالكامل ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

* {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
}

.stApp {
    background-color: #0f172a !important;
    color: #f8fafc !important;
}

#MainMenu, header, footer {
    visibility: hidden;
    height: 0px;
}

label, .stRadio label, p, .stSelectbox label {
    color: #f8fafc !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
}

div[role="radiogroup"] label {
    background-color: #1e293b !important;
    padding: 8px 16px !important;
    border-radius: 10px !important;
    border: 1px solid #3b82f6 !important;
    margin-left: 10px !important;
}

textarea, input[type="text"], div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
}

.stButton>button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #ffffff !important;
    font-size: 1.2rem !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 10px 24px !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
}

.card-box {
    background-color: #1e293b;
    border: 2px solid #3b82f6;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.card-header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #1e40af;
    padding-bottom: 10px;
    margin-bottom: 14px;
}

.word-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #38bdf8;
}

.word-pos {
    background: #2563eb;
    color: #ffffff;
    font-size: 0.85rem;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 700;
}

.section-label {
    color: #93c5fd;
    font-weight: 700;
}

.morpho-box {
    margin-top: 12px;
    padding: 12px;
    background: #0f172a;
    border-radius: 10px;
    border: 1px solid #334155;
}

.morpho-item {
    color: #4ade80;
    margin-bottom: 4px;
    font-size: 0.95rem;
}

.morpho-item-details {
    color: #facc15;
    margin-bottom: 4px;
    font-size: 0.95rem;
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

# --- 3. الهيدر الرئيسي ---
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 style='font-size: 2.5rem; color: #38bdf8; font-weight: 800;'>📖 المِعْرَبُ الذَّكِيّ</h1>
    <p style='font-size: 1.1rem; color: #cbd5e1;'>المنصة الذكية المتقدمة للتحليل النحوي ومنهاج اللغة العربية للشهادات السورية</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 تحليل النص والإعراب", "📚 تحضير درس للمعلم (.docx)", "🎓 منهاج التاسع والبكالوريا (سوريا)"])

# === التبويب الأول: الإعراب ===
with tab1:
    input_text = st.text_area(
        "أدخل الجملة أو الآية القرآنية:",
        placeholder="مثال: لَوْ أَنْزَلْنَا هَذَا الْقُرْآنَ عَلَى جَبَلٍ",
        value="لَوْ أَنْزَلْنَا هَذَا الْقُرْآنَ عَلَى جَبَلٍ",
        height=100
    )
    
    if st.button("أعرب وحلّل النص ⚡", key="btn_parse"):
        if not input_text.strip():
            st.error("رجاءً أدخل نصاً للتحليل.")
        else:
            with st.spinner("جاري التحليل واستخراج إعراب جميع الكلمات..."):
                result = analyze_arabic_text(input_text)
                
            if not result:
                st.error("حدث خطأ أثناء معالجة النص. يرجى التحقق من المفتاح أو الاتصال.")
            else:
                st.markdown("### 🔤 تحليل المفردات والصرف لجميع الكلمات")
                words = result.words_analysis
                cols = st.columns(2)
                
                for index, item in enumerate(words):
                    col = cols[index % 2]
                    with col:
                        details_html = f"<div class='morpho-item-details'>⚙️ {item.morphology.derivation_details}</div>" if item.morphology.derivation_details else ""
                        card_html = f"""<div class="card-box"><div class="card-header-flex"><span class="word-title">{item.diacritization}</span><span class="word-pos">{item.pos}</span></div><div style="margin-bottom: 10px; font-size: 1rem; line-height: 1.7;"><span class="section-label">📌 الإعراب:</span> {item.parsing.irab}</div><div style="margin-bottom: 10px; font-size: 1rem; line-height: 1.7;"><span class="section-label">💡 التعليل النحوي:</span> {item.parsing.reason}</div><div class="morpho-box"><div class="morpho-item">🌱 <b>الجذر:</b> {item.morphology.root}</div><div class="morpho-item">⚖️ <b>الوزن:</b> {item.morphology.weight}</div><div class="morpho-item">🔍 <b>النوع:</b> {item.morphology.word_type}</div>{details_html}</div></div>"""
                        st.markdown(card_html, unsafe_allow_html=True)
                
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

# === التبويب الثاني: تحضير الدرس ===
with tab2:
    lesson_topic = st.text_input(
        "عنوان أو موضوع الدرس النحوي/الصرفي:",
        placeholder="مثال: أحكام المفعول لأجله مع الشواهد والأمثلة"
    )
    
    if st.button("توليد خطة الدرس والتصدير إلى Word 📄", key="btn_lesson"):
        if not lesson_topic.strip():
            st.warning("يرجى كتابة عنوان الدرس أولاً.")
        else:
            with st.spinner("جاري صياغة خطة الدرس..."):
                try:
                    prompt = f"{LESSON_GENERATOR_PROMPT}\n\nقم بإعداد خطة درس متكاملة ومفصلة حول موضوع: {lesson_topic}"
                    lesson_content = generate_content_with_fallback(prompt)
                    
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

# === التبويب الثالث: المنهاج السوري (تاسع وبكالوريا) ===
with tab3:
    st.markdown("## 🎓 دليل وتدريبات المنهاج السوري")
    
    sub_mode = st.radio(
        "اختر الخدمة المطلوبة:",
        ["📖 شرح درس وتطبيقاته من المنهاج", "📝 نموذج امتحاني وتصحيح تلقائي"],
        horizontal=True
    )
    
    st.markdown("---")
    
    col_grade, col_branch = st.columns(2)
    with col_grade:
        grade = st.selectbox("المرحلة الدراسية:", ["الصف التاسع الإعدادي", "الثالث الثانوي (البكالوريا)"])
    with col_branch:
        branch = st.selectbox("الفرع (للبكالوريا):", ["العلمي", "الأدبي"]) if grade == "الثالث الثانوي (البكالوريا)" else "عام"

    # دالة مساعدة لجلب النص المفرغ تلقائياً من الكتاب
    def get_extracted_lesson_text(lesson_title):
        json_path = os.path.join("data", "grade9_texts.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    extracted_data = json.load(f)
                for key, val in extracted_data.items():
                    if lesson_title in key or key in lesson_title:
                        return val.get("raw_text", "")
            except Exception:
                pass
        return None

    # الخدمة الأولى: شرح الدرس
    if sub_mode == "📖 شرح درس وتطبيقاته من المنهاج":
        curriculum_data = SYRIAN_9TH_CURRICULUM if grade == "الصف التاسع الإعدادي" else SYRIAN_BAC_CURRICULUM
        
        col_unit, col_lesson = st.columns(2)
        with col_unit:
            selected_unit = st.selectbox("اختر الوحدة / القسم من الكتاب:", list(curriculum_data.keys()))
        with col_lesson:
            lessons_in_unit = curriculum_data[selected_unit]
            selected_lesson = st.selectbox("اختر الدرس المطلوب الشرح عنه:", lessons_in_unit)
            
        if st.button("عرض الشرح والشواهد الامتحانية 📚", key="btn_syria_explain"):
            with st.spinner("جاري استخراج شرح الدرس والشواهد المعتمدة..."):
                try:
                    original_text = get_extracted_lesson_text(selected_lesson) if grade == "الصف التاسع الإعدادي" else None
                    context_prompt = ""
                    if original_text:
                        context_prompt = f"\n\nملاحظة هامّة: استخدم النص المعتمد حرفياً من كتاب الوزارة السوري الآتي ولا تخمّن أبياتاً خارجية:\n'''\n{original_text}\n'''"

                    query = f"{SYRIAN_CURRICULUM_PROMPT}\n\nالمرحلة: {grade} ({branch})\nالوحدة: {selected_unit}\nالدرس/القصيدة: {selected_lesson}{context_prompt}\n\nقدم شرحاً شاملاً للدرس يتضمن: القاعدة التفصيلية، الشواهد من أسطر/قصائد الكتاب، الإعراب النموذجي للكلمات الرئيسية، وطريقة السؤال الصادرة في الامتحان الوزاري وكيفية الإجابة عليه."
                    
                    response_text = generate_content_with_fallback(query)
                    st.markdown(f"<div style='direction: rtl; text-align: right;'>{response_text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

    # الخدمة الثانية: الاختبار والنموذج الامتحاني الشامل
    else:
        st.markdown("### 📝 ورقة امتحانية تفاعلية شاملة (تطابق الامتحان النهائي)")
        
        if st.button("توليد نموذج امتحاني شامل 🎲", key="btn_gen_exam"):
            with st.spinner("جاري صياغة ورقة الاختبار والقصيدة..."):
                try:
                    exam_query = f"{SYRIAN_EXAM_PROMPT}\n\nقم بصياغة نموذج امتحاني لطلاب {grade} ({branch}). أخرج النتيجة بتنسيق JSON فقط."
                    response_text = generate_content_with_fallback(exam_query)
                    
                   raw_text = response_text.replace("```json", "").replace("```", "").strip()
