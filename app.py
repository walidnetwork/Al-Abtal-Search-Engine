import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الهوية ---
st.set_page_config(
    page_title="ALABTAL SEARCH ENGINE", 
    page_icon="logo.png",
    layout="wide" # ضروري جداً للتوزيع العرضي
)

# --- 2. دوال البحث والنطق المستقرة (بدون أي تعديل في المنطق) ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

@st.cache_data(show_spinner=False)
def speak_clean(text):
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

# --- 3. التصميم المحدث للضبط والسنترة (CSS) ---
logo_base64 = get_base64('logo.png')

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Orbitron:wght@700&display=swap');
    
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
    }}

    .main-title {{
        font-family: 'Cairo', sans-serif;
        font-size: clamp(2rem, 5vw, 3.5rem);
        color: #fff;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);
        text-align: center;
        margin: 20px 0 40px 0;
    }}

    /* تصميم الأزرار النيون */
    .stButton>button {{
        width: 100% !important;
        background: rgba(0, 212, 255, 0.03) !important;
        border: 2px solid #00d4ff !important;
        color: #00d4ff !important;
        border-radius: 12px !important;
        font-family: 'Orbitron', sans-serif !important;
        height: 55px !important;
        margin-bottom: 15px !important;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        background: #00d4ff !important;
        color: #000 !important;
        box-shadow: 0 0 25px #00d4ff;
    }}

    .center-logo-img {{
        width: 100%;
        max-width: 280px;
        filter: drop-shadow(0 0 15px rgba(239, 68, 68, 0.5));
    }}

    .word-highlight {{ color: #00d4ff; font-weight: bold; }}
    .sentence-box {{
        background: rgba(30, 41, 59, 0.5);
        border-left: 5px solid #00d4ff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: left;
        direction: ltr;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. منطق التنقل والواجهة ---
if 'step' not in st.session_state: st.session_state.step = 'select_grade'

if st.session_state.step == 'select_grade':
    st.markdown('<h1 class="main-title">محرك بحث الأبطال</h1>', unsafe_allow_html=True)
    
    # توزيع الأعمدة لضمان السنترة (1:1:1) مع مسافات جانبية خفيفة
    _, col_left, col_mid, col_right, _ = st.columns([0.2, 1, 1.5, 1, 0.2])
    
    with col_left:
        st.write("<br><br>", unsafe_allow_html=True)
        if st.button("GRADE 1"): st.session_state.grade = 1; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 2"): st.session_state.grade = 2; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 3"): st.session_state.grade = 3; st.session_state.step = 'select_term'; st.rerun()

    with col_mid:
        if logo_base64:
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" class="center-logo-img"></div>', unsafe_allow_html=True)

    with col_right:
        st.write("<br><br>", unsafe_allow_html=True)
        if st.button("GRADE 4"): st.session_state.grade = 4; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 5"): st.session_state.grade = 5; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 6"): st.session_state.grade = 6; st.session_state.step = 'select_term'; st.rerun()

elif st.session_state.step == 'select_term':
    g = st.session_state.grade
    st.markdown(f'<h2 style="text-align:center; color:#00d4ff;">Grade {g}</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        img1 = get_base64(f"cover_g{g}_t1.jpg")
        if img1: st.image(f"data:image/jpeg;base64,{img1}", use_container_width=True)
        if st.button("TERM 1"): st.session_state.term = 1; st.session_state.step = 'search'; st.rerun()
    with col2:
        img2 = get_base64(f"cover_g{g}_t2.jpg")
        if img2: st.image(f"data:image/jpeg;base64,{img2}", use_container_width=True)
        if st.button("TERM 2"): st.session_state.term = 2; st.session_state.step = 'search'; st.rerun()
    if st.button("🔙 BACK"): st.session_state.step = 'select_grade'; st.rerun()

elif st.session_state.step == 'search':
    g, t = st.session_state.grade, st.session_state.term
    pdf_file = f"g{g}_t{t}.pdf"
    st.markdown(f'<h3 style="text-align:center;">Grade {g} - Term {t}</h3>', unsafe_allow_html=True)
    word = st.text_input("🔍 Search Word...", placeholder="Type here...").strip()
    
    if word:
        st.audio(speak_clean(word))
        sentences, pages = advanced_search(pdf_file, word)
        if sentences:
            for i, s in enumerate(sentences[:10]):
                st.markdown(f'<div class="sentence-box">{s["display"]}</div>', unsafe_allow_html=True)
                if st.button(f"🔊 Listen", key=f"v_{i}"): st.audio(speak_clean(s['raw']))
        if pages:
            for p in pages: st.image(p['image'], use_container_width=True)
    
    if st.button("🔙 BACK"): st.session_state.step = 'select_term'; st.rerun()

# --- 5. التذييل (Footer) ---
st.markdown("""
    <div style="text-align:center; margin-top:50px; padding-top:20px; border-top:1px solid #1e293b;">
        <a href="https://linktr.ee/ALABTAL.books" target="_blank" style="text-decoration:none;">
            <button style="background:transparent; border:1px solid #00d4ff; color:#00d4ff; padding:8px 25px; border-radius:20px; cursor:pointer;">
                🔗 جميع منصات الأبطال التعليمية
            </button>
        </a>
        <p style="color:#64748b; font-size:0.8rem; margin-top:10px;">Created by Mr. Walid Elhagary</p>
    </div>
""", unsafe_allow_html=True)
