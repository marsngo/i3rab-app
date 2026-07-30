import streamlit as st
import json
from engine import analyze_arabic_text
from lesson_generator import create_formatted_lesson_docx
from config import GEMINI_API_KEY, MODEL_NAME
from google import genai
from prompts.system_prompts import LESSON_GENERATOR_PROMPT
from prompts.syrian_curriculum import SYRIAN_CURRICULUM_PROMPT, SYRIAN_EXAM_PROMPT

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="المعرّب الذكي | المنصة التعليمية المتكاملة",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. بيانات دروس المنهاج السوري ---
SYRIAN_BAC_LESSONS = [
    "المفعول المطلق والمفعول لأجله",
    "المفعول فيه (الظرف)",
    "الحال والأحكام المتعلقة بها",
    "التمييز وأنواعه",
    "الاستثناء وأحكامه",
    "المنادى وأحكام إعرابه",
    "أسلوب الشرط (النتائج والأدوات)",
    "أسلوب التعجب وأحكامه",
    "أسلوب المدح والذم",
    "أحكام العدد والمعدود",
    "قواعد الإعلال (بالقلب وبالحذف)",
    "قواعد الإبدال",
    "المشتقات وإعمالها (اسم الفاعل، المفعول، المشبهة)",
    "العروض: البحر البسيط والكامل والخفيف",
    "درس آخر (كتابة يدوية)..."
]

SYRIAN_9TH_LESSONS = [
    "الأفعال الخمسة وإعرابها",
    "الأفعال الناقصة والأفعال التامة",
    "المفعول به والمفعول فيه",
    "المفعول لأجله والمفعول المطلق",
    "المبتدأ والخبر ونواسخهما",
    "المنادى وأنواعه",
    "النعت (الصفة) والعطف",
    "التوكيد والبدل",
    "الاسم الجامد والاسم المشتق",
    "الميزان الصرفي والصحيح والمعتل",
    "العروض: البحر الطويل والرجز",
    "درس آخر (كتابة يدوية)..."
]

# --- 3. تنسيق الـ CSS المحسّن بالكامل ---
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

/* تنسيق الأبيات العمودية (الصدر والعجز) */
.poem-box {
    background-color: #1e293b;
    border-right: 5px solid #2563eb;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 30px;
    direction: rtl;
}

.poem-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    gap: 20px;
    border-bottom: 1px dashed #334155;
    padding-bottom: 8px;
}

.poem-row:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.hemistich-first {
    flex: 1;
    text-align: right;
    font-size: 1.25rem;
    font-weight: 700;
    color: #f8fafc;
}

.hemistich-second {
    flex: 1;
    text-align: left;
    font-size: 1.25rem;
    font-weight: 700;
    color: #38bdf8;
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

# --- 4. الهيدر الرئيسي ---
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
                st.error("حدث خطأ أثناء معالجة النص. يرجى التحقق من الاتصال والمفتاح.")
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
        grade = st.selectbox("المرحلة الدراسية:", ["الثالث الثانوي (البكالوريا)", "الصف التاسع الإعدادي"])
    with col_branch:
        branch = st.selectbox("الفرع (للبكالوريا):", ["العلمي", "الأدبي"]) if grade == "الثالث الثانوي (البكالوريا)" else "عام"

    # --- الخدمة الأولى: شرح الدرس ---
    if sub_mode == "📖 شرح درس وتطبيقاته من المنهاج":
        lessons_list = SYRIAN_BAC_LESSONS if grade == "الثالث الثانوي (البكالوريا)" else SYRIAN_9TH_LESSONS
        selected_lesson = st.selectbox("اختر الدرس المقرر من القائمة:", lessons_list)
        
        topic = st.text_input("اكتب اسم الدرس المطلوب:") if selected_lesson == "درس آخر (كتابة يدوية)..." else selected_lesson
            
        if st.button("عرض الشرح والشواهد الامتحانية 📚", key="btn_syria_explain"):
            if not topic.strip():
                st.warning("يرجى اختيار أو كتابة اسم الدرس.")
            else:
                with st.spinner("جاري استخراج شرح الدرس والشواهد المعتمدة من كتاب الوزارة..."):
                    try:
                        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                        query = f"{SYRIAN_CURRICULUM_PROMPT}\n\nالمرحلة: {grade} ({branch})\nاسم الدرس: {topic}\n\nيرجى تقديم شرح مفصل وشامل يتضمن: القاعدة، الشواهد من قصائد الكتاب، أمثلة معربة، وطريقة السؤال الصادرة في الامتحان الوزاري وكيفية الإجابة عليها."
                        response = gemini_client.models.generate_content(
                            model=MODEL_NAME,
                            contents=query,
                        )
                        st.markdown(f"<div style='direction: rtl; text-align: right;'>{response.text}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")

    # --- الخدمة الثانية: الاختبار والتصحيح التلقائي الشامل ---
    else:
        st.markdown("### 📝 ورقة امتحانية تفاعلية شاملة (تطابق الامتحان النهائي)")
        
        if st.button("توليد نموذج امتحاني شامل 🎲", key="btn_gen_exam"):
            with st.spinner("جاري صياغة ورقة الاختبار والقصيدة بالعمودين الشعرية..."):
                try:
                    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                    exam_query = f"{SYRIAN_EXAM_PROMPT}\n\nقم بصياغة نموذج امتحاني لطلاب {grade} ({branch}). أخرج النتيجة بتنسيق JSON فقط."
                    
                    response = gemini_client.models.generate_content(
                        model=MODEL_NAME,
                        contents=exam_query,
                    )
                    
                    raw_text = response.text.replace("```json", "").replace("```", "").strip()
                    exam_data = json.loads(raw_text)
                    
                    st.session_state["exam_data"] = exam_data
                    st.session_state["confirmed_answers"] = {}
                except Exception as e:
                    st.error("حدث خطأ أثناء توليد الاختبار. يرجى الضغط على زر التوليد مرة أخرى.")

        if "exam_data" in st.session_state:
            exam_data = st.session_state["exam_data"]
            
            # 1. عرض الأبيات العمودية
            poem_html = "<div class='poem-box'><h4 style='color: #38bdf8; margin-bottom: 16px; font-weight: 800;'>📜 النص الشعري المقرر للشهادة:</h4>"
            poem_lines = exam_data.get('poem', [])
            
            if isinstance(poem_lines, list):
                for verse in poem_lines:
                    first_part = verse.get('first', '') if isinstance(verse, dict) else str(verse)
                    second_part = verse.get('second', '') if isinstance(verse, dict) else ""
                    poem_html += f"""
                    <div class="poem-row">
                        <span class="hemistich-first">{first_part}</span>
                        <span class="hemistich-second">{second_part}</span>
                    </div>
                    """
            poem_html += "</div>"
            st.markdown(poem_html, unsafe_allow_html=True)
            
            st.markdown("<h3 style='direction: rtl; text-align: right;'>✍️ الأسئلة والإجابات المطلوبة:</h3>", unsafe_allow_html=True)
            
            # 2. عرض كل سؤال فرعي بحقل وزر تثبيت مستقلين
            current_section = ""
            for q in exam_data.get("questions", []):
                q_id = q["id"]
                section_title = q.get("section", "أسئلة ورقة الامتحان")
                
                if section_title != current_section:
                    current_section = section_title
                    st.markdown(f"<h4 style='color: #facc15; direction: rtl; text-align: right; margin-top: 25px;'>📌 {current_section}</h4>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="direction: rtl; text-align: right; font-size: 1.15rem; font-weight: 700; color: #93c5fd; margin-bottom: 8px; margin-top: 10px;">
                    س {q_id}: {q['text']}
                </div>
                """, unsafe_allow_html=True)
                
                is_essay = "التعبير" in section_title or "الموضوع" in q['text']
                height_val = 180 if is_essay else 90
                
                ans = st.text_area(
                    f"إجابتك على السؤال ({q_id}):",
                    key=f"input_q_{q_id}",
                    placeholder="اكتب الموضوع بالكامل هنا..." if is_essay else "اكتب الإجابة المفصلة لهذا السؤال هنا...",
                    height=height_val
                )
                
                if st.button(f"تأكيد إجابة السؤال ({q_id}) ✅", key=f"btn_confirm_{q_id}"):
                    if "confirmed_answers" not in st.session_state:
                        st.session_state["confirmed_answers"] = {}
                    st.session_state["confirmed_answers"][q_id] = ans
                    st.success(f"تم حفظ إجابة السؤال {q_id} بنجاح!")
                
                if q_id in st.session_state.get("confirmed_answers", {}):
                    st.markdown(f"<div style='direction: rtl; text-align: right; color: #4ade80; font-weight: 700; margin-top: 5px;'>📌 الإجابة المثبتة للسؤال ({q_id}): {st.session_state['confirmed_answers'][q_id]}</div>", unsafe_allow_html=True)
                    
                st.markdown("<hr style='border: 1px dashed #334155; margin: 15px 0;'>", unsafe_allow_html=True)
            
            # 3. زر التصحيح الشامل
            if st.button("⚖️ تصحيح نموذج الامتحان وإظهار العلامة الكلية والموضوع", key="btn_grade_all"):
                all_answers_summary = ""
                for q in exam_data.get("questions", []):
                    q_id = q["id"]
                    final_ans = st.session_state.get("confirmed_answers", {}).get(q_id, st.session_state.get(f"input_q_{q_id}", "لم يجب"))
                    all_answers_summary += f"السؤال {q_id} ({q.get('section', '')}): {q['text']}\nإجابة الطالب:\n{final_ans}\n\n"
                
                with st.spinner("جاري تقييم الورقة وموضوع التعبير حسب سلم التصحيح الوزاري..."):
                    try:
                        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                        eval_prompt = f"""
                        أنت مصحح وزاري معتمد لمادة اللغة العربية في سوريا.
                        المنهاج: {grade} ({branch})
                        النص الشعري:
                        {exam_data.get('poem', '')}
                        
                        الأسئلة وإجابات الطالب:
                        {all_answers_summary}
                        
                        قم بتقديم تقرير تصحيح رسمي يحتوي على:
                        1. العلامة الكلية المقدرة.
                        2. تقييم مفصل لسؤال الموضوع الأدبي/الاجباري.
                        3. تصحيح بقية الأسئلة سؤالاً بسؤال مع توضيح الأخطاء والإجابة السليمة.
                        4. نصائح توجيهية نهائية.
                        """
                        
                        response = gemini_client.models.generate_content(
                            model=MODEL_NAME,
                            contents=eval_prompt,
                        )
                        
                        st.markdown("<h2 style='direction: rtl; text-align: right;'>📊 نتيجة التصحيح وتقييم الامتحان:</h2>", unsafe_allow_html=True)
                        st.markdown(f"<div style='direction: rtl; text-align: right;'>{response.text}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء إجراء التصحيح: {e}")

# --- 5. التوقيع ---
st.markdown("""
<div class='footer-container'>
    <p>تصميم وتطوير: <b>مهيدي الخالدي</b> | <a href='mailto:alkhaldimhedy@gmail.com'>alkhaldimhedy@gmail.com</a></p>
    <p>جميع الحقوق محفوظة © 2026 | الإصدار: <b>v1.1.0</b></p>
</div>
""", unsafe_allow_html=True)
