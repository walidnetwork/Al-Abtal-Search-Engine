import streamlit as st
import fitz  # PyMuPDF
from gtts import gTTS
import io
from PIL import Image
import re
import os

# 1. إعدادات الواجهة
st.set_page_config(page_title="قاموس الأبطال الشامل", page_icon="🦸‍♂️", layout="centered")

# 2. تصميم الواجهة (CSS)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0f2fe 0%, #fefce8 100%); }
    .main-title { color: #1e40af; font-family: 'Arial Black', sans-serif; font-size: 38px; text-shadow: 2px 2px #ffffff; text-align: center; }
    .grade-header { color: #f59e0b; font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 10px; }
    .sentence-box { 
        background-color: #ffffff; padding: 25px; border-radius: 20px; 
        border: 3px solid #3b82f6; margin-bottom: 15px;
        box-shadow: 0px 5px 15px rgba(59, 130, 246, 0.1);
        color: #1e3a8a !important; font-size: 24px; font-weight: bold; text-align: center;
    }
    .highlight { color: #ffffff; background-color: #ef4444; padding: 2px 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

def display_hero_logo():
    possible_paths = ["assets/logo.png", "assets/logo.png.png"]
    found_path = next((p for p in possible_paths if os.path.exists(p)), None)
    if found_path:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image(found_path, width=180)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    display_hero_logo()
    st.markdown('<div class="main-title">قاموس الأبطال</div>', unsafe_allow_html=True)
    code = st.text_input("ادخل كود التفعيل:", type="password")
    if st.button("انطلق الآن! 🚀", use_container_width=True):
        if code == "HERO2026":
            st.session_state.logged_in = True
            st.rerun()
else:
    display_hero_logo()
    st.markdown('<div class="main-title">مدرسة الأبطال الذكية</div>', unsafe_allow_html=True)
    
    # --- إضافة لوحة اختيار الصف الدراسي ---
    st.markdown('<div class="grade-header">اختر صفك الدراسي يا بطل:</div>', unsafe_allow_html=True)
    grade_option = st.selectbox("", 
                                ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6"],
                                index=0)
    
    # تحديد مسار الملف بناءً على الاختيار
    grade_map = {
        "Grade 1": "g1_t1.pdf", "Grade 2": "g2_t1.pdf", "Grade 3": "g3_t1.pdf",
        "Grade 4": "g4_t1.pdf", "Grade 5": "g5_t1.pdf", "Grade 6": "g6_t1.pdf"
    }
    selected_pdf = grade_map[grade_option]
    
    st.divider()
    
    search_query = st.text_input(f"🔍 ابحث عن كلمة في منهج ({grade_option}):", placeholder="اكتب الكلمة هنا...").strip()

    if search_query:
        # نطق الكلمة
        tts_word = gTTS(text=search_query, lang='en')
        word_fp = io.BytesIO()
        tts_word.write_to_fp(word_fp)
        st.audio(word_fp)

        pdf_path = f"data/{selected_pdf}"
        
        if os.path.exists(pdf_path):
            try:
                doc = fitz.open(pdf_path)
                best_page_num = None
                found_sentences = []
                search_pattern = r'\b' + re.escape(search_query) + r'\b'
                
                for page_num, page in enumerate(doc):
                    if page_num < 5: continue # تخطي المقدمة
                    text = page.get_text("text").replace('\n', ' ')
                    if re.search(search_pattern, text, re.IGNORECASE):
                        if best_page_num is None: best_page_num = page_num
                        raw = re.findall(r'([^.!?]*' + re.escape(search_query) + r'[^.!?]*[.!?]?)', text, re.IGNORECASE)
                        for s in raw:
                            if 3 <= len(s.split()) <= 15:
                                found_sentences.append(s.strip())

                if best_page_num is not None:
                    st.markdown(f"<h4 style='color:#1e40af;'>🖼️ لقطة من كتاب {grade_option}:</h4>", unsafe_allow_html=True)
                    page_img = doc.load_page(best_page_num)
                    pix = page_img.get_pixmap(matrix=fitz.Matrix(2, 2)) 
                    img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    st.image(img_data, use_container_width=True)

                if found_sentences:
                    st.markdown("<h4 style='color:#1e40af;'>📝 اسمع جمل الأبطال:</h4>", unsafe_allow_html=True)
                    for s in list(dict.fromkeys(found_sentences))[:3]:
                        pattern = re.compile(re.escape(search_query), re.IGNORECASE)
                        highlighted = pattern.sub(f'<span class="highlight">{search_query}</span>', s)
                        st.markdown(f'<div class="sentence-box">{highlighted}</div>', unsafe_allow_html=True)
                        
                        tts_sent = gTTS(text=s, lang='en', slow=True) 
                        sent_fp = io.BytesIO()
                        tts_sent.write_to_fp(sent_fp)
                        st.audio(sent_fp)
                        st.divider()
                else:
                    st.info(f"الكلمة موجودة في الكتاب، لكن لم أجد لها جملة كاملة في {grade_option}.")
            except:
                st.error("حدث خطأ أثناء قراءة الملف.")
        else:
            st.warning(f"⚠️ عذراً يا بطل، ملف المنهج ({selected_pdf}) غير موجود حالياً في مجلد data.")