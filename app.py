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
    layout="wide"
)

# --- 2. دوال البحث والنطق المستقرة ---
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

# --- 3. تصميم CSS المضبط للتقريب والتوسيط ---
logo_base64 = get_base64('logo.png')

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Orbitron:wght@700&display=swap');
    
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
    }}

    .main-title {{
        font-family: 'Cairo', sans-serif;
        font-size: 3rem;
        color: #fff;
        text-shadow: 0 0 15px #00d4ff;
        text-align: center;
        margin-bottom: 20px;
    }}

    /* تصميم الأزرار - قمنا بتقليل العرض ليقترب من اللوجو */
    .stButton>button {{
        width: 140px !important;
        background: rgba(0, 212, 255, 0.03) !important;
        border: 2px solid #00d4ff !important;
        color: #00d4ff !important;
        border-radius: 10px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.9rem !important;
        height: 50px !important;
        margin-bottom: 10px !important;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        background: #00d4ff !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00d4ff;
    }}

    /* تقريب الأزرار من المركز */
    [data-testid="column"]:nth-child(2) {{ text-align: right !important; }}
    [data-testid="column"]:nth-child(4) {{ text-align: left !important; }}

    .center-logo-img {{
        width: 100%;
        max-width: 260px;
        filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4));
    }}
    
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
    
    # استخدام توزيع أعمدة يضغط العناصر للمركز
    _, col_left, col_mid, col_right, _ = st.columns([0.5, 0.8, 1.2, 0.8, 0.5])
    
    with col_left:
        st.write("<br><br>", unsafe_allow_html=True)
        if st.button("GRADE 1"): st.session_state.grade = 1; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 2"): st.session_state.grade = 2; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 3"): st.session_state.grade = 3; st.session_state.step = 'select_term'; st.rerun()

    with col_mid:
        if logo_base64:
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_base64}" class="center-logo-
