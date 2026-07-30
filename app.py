import streamlit as st
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

# --- 2. التنسيق (CSS) ---
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

textarea, input[type="text"] {
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
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")

    # --- الخدمة الثانية: الاختبار والتصحيح التلقائي المطور ---
    else:
        st.markdown("### 📝 ورقة امتحانية تفاعلية")
        
        if st.button("توليد نموذج امتحاني جديد 🎲", key="btn_gen_exam"):
            with st.spinner("جاري صياغة ورقة الاختبار والأسئلة الوزارية..."):
                try:
                    import json
                    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                    exam_query = f"{SYRIAN_EXAM_PROMPT}\n\nقم بصياغة نموذج امتحاني لطلاب {grade} ({branch}). أخرج النتيجة بتنسيق JSON فقط."
                    
                    response = gemini_client.models.generate_content(
                        model=MODEL_NAME,
                        contents=exam_query,
                    )
                    
                    # تنظيف النص واستخراج الـ JSON
                    raw_text = response.text.replace("```json", "").replace("```", "").strip()
                    exam_data = json.loads(raw_text)
                    
                    st.session_state["exam_data"] = exam_data
                    st.session_state["confirmed_answers"] = {}
                except Exception as e:
                    st.error("حدث خطأ أثناء توليد الاختبار. يرجى الضغط على زر التوليد مرة أخرى.")

        # عرض الورقة الامتحانية إن كانت متوفرة
        if "exam_data" in st.session_state:
            exam_data = st.session_state["exam_data"]
            
            # 1. عرض الأبيات الشعرية بأسلوب رسمي
            st.markdown(f"""
            <div style="background-color: #1e293b; border-right: 5px solid #2563eb; padding: 18px; border-radius: 10px; margin-bottom: 25px;">
                <h4 style="color: #38bdf8; margin-bottom: 10px;">📜 اقرأ الأبيات الآتية ثم أجب عن الأسئلة:</h4>
                <p style="font-size: 1.25rem; line-height: 2; white-space: pre-line; color: #f8fafc;">{exam_data.get('poem', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### ✍️ الأسئلة والإجابات:")
            
            # 2. عرض كل سؤال وحقل إجابته الخاص
            user_answers = {}
            for q in exam_data.get("questions", []):
                q_id = q["id"]
                st.markdown(f"**س {q_id}: {q['text']}**")
                
                ans = st.text_input(
                    f"إجابتك على السؤال ({q_id}):",
                    key=f"input_q_{q_id}",
                    placeholder="اكتب إجابتك هنا..."
                )
                
                # زر تأكيد الإجابة لكل سؤال
                if st.button(f"تأكيد إجابة السؤال ({q_id}) ✅", key=f"btn_confirm_{q_id}"):
                    st.session_state["confirmed_answers"][q_id] = ans
                    st.success(f"تم تثبيت إجابة السؤال {q_id} بنجاح!")
                
                if q_id in st.session_state.get("confirmed_answers", {}):
                    st.caption(f"📌 الإجابة المتبتة: {st.session_state['confirmed_answers'][q_id]}")
                    
                st.markdown("---")
            
            # 3. زر التصحيح النهائي الشامل
            if st.button("⚖️ تصحيح نموذج الامتحان وإظهار العلامة النهائية", key="btn_grade_all"):
                # تجميع كافة الإجابات المكتوبة
                all_answers_summary = ""
                for q in exam_data.get("questions", []):
                    q_id = q["id"]
                    # أخذ الإجابة المؤكدة أو المكتوبة
                    final_ans = st.session_state.get("confirmed_answers", {}).get(q_id, st.session_state.get(f"input_q_{q_id}", "لم يجب"))
                    all_answers_summary += f"السؤال {q_id}: {q['text']}\nإجابة الطالب: {final_ans}\n\n"
                
                with st.spinner("جاري تقييم الورقة حسب سلم التصحيح الوزاري الرسمية..."):
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
                        1. العلامة الكلية المقدرة (مثلاً من 60 أو من 20).
                        2. تصحيح كل سؤال على حدة مع بيان الأخطاء والجواب النموذجي المعتمد.
                        3. نصائح سريعة للطالب.
                        """
                        
                        response = gemini_client.models.generate_content(
                            model=MODEL_NAME,
                            contents=eval_prompt,
                        )
                        
                        st.markdown("## 📊 نتيجة التصحيح وتقييم الأداء:")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء إجراء التصحيح: {e}")

# --- 4. التوقيع ---
st.markdown("""
<div class='footer-container'>
    <p>تصميم وتطوير: <b>مهيدي الخالدي</b> | <a href='mailto:alkhaldimhedy@gmail.com'>alkhaldimhedy@gmail.com</a></p>
    <p>جميع الحقوق محفوظة © 2026 | الإصدار: <b>v1.1.0</b></p>
</div>
""", unsafe_allow_html=True)
