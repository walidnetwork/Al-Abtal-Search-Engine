import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة والتنسيق الجمالي ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: #0f172a; color: white;
    }
    .stButton>button {
        width: 100%; border-radius: 20px; background: linear-gradient(135deg, #ef4444, #b91c1c);
        color: white; font-weight: bold; font-size: 1.2rem; height: 3.5em;
        border: 2px solid #f87171; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    .stButton>button:hover { transform: scale(1.05); transition: 0.3s; }
    .cover-card { border-radius: 20px; border: 3px solid #334155; margin-bottom: 15px; }
    .sentence-box {
        background: #1e293b; padding: 20px; border-radius: 15px; margin-bottom: 10px;
        border-right: 6px solid #ef4444; font-size: 1.3rem;
    }
    .main-title { text-align: center; color: #f8fafc; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    </style>
""", unsafe_allow_html=True)

# --- 2. دالات المساعدة (التعامل مع الملفات والنطق) ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def speak_clean(text):
    # تنظيف النص من الرموز (النجمة، الماسة، إلخ) للنطق فقط
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    tts = gTTS(text=clean_text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

def advanced_search(pdf_path, word):
    extracted_sentences = []
    full_pages = []
    if not os.path.exists(pdf_path): return [], []
    try:
        doc = fitz.open(pdf_path)
        word_pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if word_pattern.search(text):
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                lines = text.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if word_pattern.search(clean_line) and len(clean_line) > 3:
                        display_text = re.sub(word_pattern, f"<span style='color:#ef4444; font-weight:bold;'>{word}</span>", clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({"display": display_text, "raw": clean_line})
        doc.close()
    except: pass
    return extracted_sentences, full_pages

# --- 3. منطق التنقل والحالة ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'grade_num' not in st.session_state: st.session_state.grade_num = None

# --- 4. واجهة الترحيب ---
if st.session_state.step == 'welcome':
    st.markdown("<h1 class='main-title'>🦸‍♂️ مرحباً بك يا بطل في عالم الأبطال</h1>", unsafe_allow_html=True)
    logo = get_base64('logo_animated.gif') or get_base64('logo.png')
    if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{logo}" width="250"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>ALABTAL DICTIONARY</h2>", unsafe_allow_html=True)
    if st.button("🚀 ابدأ المغامرة الآن"):
        st.session_state.step = 'select_grade'; st.rerun()

# --- 5. واجهة اختيار الصف (الأغلفة العمودية) ---
elif st.session_state.step == 'select_grade':
    st.markdown("<h2 style='text-align:center;'>اختر صفك الدراسي يا بطل</h2>", unsafe_allow_html=True)
    
    for i in range(1, 7):
        col_img, col_btn = st.columns([1, 2])
        with col_img:
            img_name = f"cover_g{i}.jpg"
            img_b64 = get_base64(img_name)
            if img_b64: st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="cover-card" width="100%">', unsafe_allow_html=True)
        with col_btn:
            st.write("<br>" * 2, unsafe_allow_html=True)
            if st.button(f"دخول الصف {i} الابتدائي", key=f"btn_g{i}"):
                st.session_state.grade_num = i
                st.session_state.step = 'select_term'; st.rerun()

# --- 6. واجهة اختيار الترم ---
elif st.session_state.step == 'select_term':
    g = st.session_state.grade_num
    st.markdown(f"<h2 style='text-align:center;'>قاموس الأبطال - الصف {g}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        img_t1 = get_base64(f"cover_g{g}_t1.jpg")
        if img_t1: st.markdown(f'<img src="data:image/jpeg;base64,{img_t1}" class="cover-card" width="100%">', unsafe_allow_html=True)
        if st.button("الترم الأول"):
            st.session_state.term_num = 1; st.session_state.step = 'search'; st.rerun()
    with c2:
        img_t2 = get_base64(f"cover_g{g}_t2.jpg")
        if img_t2: st.markdown(f'<img src="data:image/jpeg;base64,{img_t2}" class="cover-card" width="100%">', unsafe_allow_html=True)
        if st.button("الترم الثاني"):
            st.session_state.term_num = 2; st.session_state.step = 'search'; st.rerun()
    
    if st.button("🔙 العودة لاختيار الصف"):
        st.session_state.step = 'select_grade'; st.rerun()

# --- 7. محرك البحث والنتائج ---
elif st.session_state.step == 'search':
    g = st.session_state.grade_num
    t = st.session_state.term_num
    st.markdown(f"<h2 style='text-align:center;'>🔍 محرك بحث الأبطال - صف {g} - ترم {t}</h2>", unsafe_allow_html=True)
    
    # تحديد ملف الـ PDF المناسب (مثال: g5_t1.pdf)
    pdf_file = f"g{g}_t{t}.pdf" 
    # ملاحظة: إذا كان لديك ملف واحد فقط حالياً، استبدل pdf_file بـ 'g1_t2.pdf' المتاح في صورك
    if not os.path.exists(pdf_file): pdf_file = "g1_t2.pdf" 

    word = st.text_input("ادخل الكلمة (English):", placeholder="اكتب الكلمة هنا...").strip()
    
    if word:
        st.markdown(f"### 🔊 نطق الكلمة: {word}")
        st.audio(speak_clean(word))
        
        sentences, pages = advanced_search(pdf_file, word)
        
        if sentences:
            st.markdown("### 📝 جمل من منهجك")
            for i, s in enumerate(sentences[:10]):
                st.markdown(f"<div class='sentence-box'>📄 {s['display']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 استمع للجملة رقم {i+1}", key=f"voice_{i}"):
                    st.audio(speak_clean(s['raw']))
        
        if pages:
            st.markdown("### 📖 صفحات من الكتاب")
            for p in pages:
                st.image(p['image'], caption=f"صفحة {p['num']}", use_container_width=True)
        
        if not sentences and not pages:
            st.warning("لم نجد هذه الكلمة في منهجك يا بطل، حاول مرة أخرى!")

    if st.button("🔙 العودة لاختيار الترم"):
        st.session_state.step = 'select_term'; st.rerun()

# --- التذييل (Footer) ---
st.write("---")
st.markdown("<div style='text-align:center; color:#94a3b8;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
