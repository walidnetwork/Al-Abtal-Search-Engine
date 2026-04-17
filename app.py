import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة - تصميم القائمة السريعة ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: #0f172a; color: white;
    }
    /* تنسيق أزرار القائمة */
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #ef4444;
        color: white; font-weight: bold; font-size: 1.1rem; height: 3em; border: None;
        text-align: center;
    }
    /* إطار قائمة الصفوف */
    .grade-item {
        background-color: #1e293b;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 15px;
        border: 1px solid #334155;
    }
    .sentence-box {
        background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 8px;
        border-right: 5px solid #ef4444; font-size: 1.4rem; color: #ffffff !important;
    }
    .word-highlight { color: #ff4b4b; font-weight: bold; }
    
    /* زر الفيسبوك المزدوج */
    .fb-split-btn {
        display: inline-flex; align-items: center; text-decoration: none;
        border-radius: 5px; overflow: hidden; font-weight: bold; margin-top: 15px;
    }
    .fb-left { background-color: #4b4b4b; color: white; padding: 10px 15px; display: flex; align-items: center; gap: 8px; font-size: 0.9rem; }
    .fb-right { background-color: #0078d4; color: white; padding: 10px 20px; font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- 2. دالات المساعدة ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

@st.cache_data(show_spinner=False)
def speak_clean(text):
    # تنظيف النص من الرموز (مثل . أو ? أو رموز غريبة) للنطق النقي
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    tts = gTTS(text=clean_text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def advanced_search(pdf_path, word):
    extracted_sentences, full_pages = [], []
    if not os.path.exists(pdf_path): return [], []
    try:
        doc = fitz.open(pdf_path)
        word_pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if word_pattern.search(text):
                pix = page.get_pixmap(matrix=fitz.Matrix(1.1, 1.1))
                full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                lines = text.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if word_pattern.search(clean_line) and len(clean_line) > 3:
                        display_text = re.sub(word_pattern, f'<span class="word-highlight">{word}</span>', clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({"display": display_text, "raw": clean_line})
        doc.close()
    except: pass
    return extracted_sentences, full_pages

# --- 3. إدارة التنقل ---
if 'step' not in st.session_state: st.session_state.step = 'select_grade'

# --- 4. واجهة قائمة الصفوف (تصميم القائمة الصغيرة السريع) ---
if st.session_state.step == 'select_grade':
    logo = get_base64('logo.png')
    if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="120"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🦸‍♂️ اختر صفك الدراسي</h2>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    # عرض الصفوف في قائمة عمودية منظمة
    for i in range(1, 7):
        # حاوية الصف: صورة صغيرة + زر
        with st.container():
            c1, c2 = st.columns([0.5, 3])
            with c1:
                img_b64 = get_base64(f"cover_g{i}.jpg")
                if img_b64:
                    st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" style="width:60px; border-radius:8px;">', unsafe_allow_html=True)
            with c2:
                if st.button(f"الصف {i} الابتدائي", key=f"g_list_{i}"):
                    st.session_state.grade = i
                    st.session_state.step = 'select_term'
                    st.rerun()

# --- 5. واجهة اختيار الترم ---
elif st.session_state.step == 'select_term':
    g = st.session_state.grade
    st.markdown(f"<h3 style='text-align:center;'>الصف {g} الابتدائي</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        img_t1 = get_base64(f"cover_g{g}_t1.jpg")
        if img_t1: st.image(f"data:image/jpeg;base64,{img_t1}", width=150)
        if st.button("الترم الأول"): st.session_state.term = 1; st.session_state.step = 'search'; st.rerun()
    with c2:
        img_t2 = get_base64(f"cover_g{g}_t2.jpg")
        if img_t2: st.image(f"data:image/jpeg;base64,{img_t2}", width=150)
        if st.button("الترم الثاني"): st.session_state.term = 2; st.session_state.step = 'search'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.step = 'select_grade'; st.rerun()

# --- 6. واجهة البحث ---
elif st.session_state.step == 'search':
    g, t = st.session_state.grade, st.session_state.term
    pdf_file = f"g{g}_t{t}.pdf"
    if not os.path.exists(pdf_file): pdf_file = "g1_t2.pdf" 
    
    word = st.text_input("ابحث عن كلمة:", placeholder="Enter word...").strip()
    if word:
        st.audio(speak_clean(word))
        sentences, pages = advanced_search(pdf_file, word)
        if sentences:
            for i, s in enumerate(sentences[:10]):
                st.markdown(f"<div class='sentence-box'>📄 {s['display']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 استمع", key=f"v_btn_{i}"): st.audio(speak_clean(s['raw']))
        if pages:
            for p in pages: st.image(p['image'], use_container_width=True)
    if st.button("🔙 عودة"): st.session_state.step = 'select_term'; st.rerun()

# --- 7. التذييل (Footer) ---
st.write("---")
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='color:#94a3b8; font-size:0.8rem;'>Created by Mr. Walid Elhagary</div>
    <a href="https://www.facebook.com/share/15fGv6mC8C/" target="_blank" class="fb-split-btn">
        <div class="fb-left">FACEBOOK</div>
        <div class="fb-right">FOLLOW OUR SERIES</div>
    </a>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
