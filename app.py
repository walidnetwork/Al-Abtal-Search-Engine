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

def play_magic_sound():
    magic_audio = '<iframe src="https://www.zapsplat.com/wp-content/uploads/2015/sound-effects-61905/zapsplat_multimedia_notification_chime_bell_001_61908.mp3" allow="autoplay" style="display:none"></iframe>'
    st.markdown(magic_audio, unsafe_allow_html=True)

# --- 3. تصميم CSS المضبط (النيون + الأعمدة) ---
logo_base64 = get_base64('logo.png')

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Orbitron:wght@700&display=swap');
    
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
    }}

    /* إجبار 3 أعمدة بجانب بعضها حتى في الموبايل */
    [data-testid="column"] {{
        width: 32% !important;
        flex: 1 1 32% !important;
        min-width: 32% !important;
    }}

    .main-title {{
        font-family: 'Cairo', sans-serif;
        font-size: clamp(1.5rem, 5vw, 3rem);
        color: #fff;
        text-shadow: 0 0 15px #00d4ff;
        text-align: center;
        margin-bottom: 5px;
    }}

    /* إعادة تأثير النيون المضيء للأزرار */
    .stButton>button {{
        width: 100% !important;
        background: rgba(0, 212, 255, 0.05) !important;
        border: 2px solid #00d4ff !important;
        color: #00d4ff !important;
        border-radius: 12px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: clamp(0.6rem, 2vw, 0.9rem) !important;
        height: 55px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        transition: 0.3s all ease-in-out;
    }}

    .stButton>button:hover {{
        background: #00d4ff !important;
        color: #000 !important;
        box-shadow: 0 0 30px #00d4ff !important;
        transform: scale(1.05);
    }}

    .center-logo-img {{
        width: 100%;
        max-width: 250px;
        animation: pulseAndGlow 3s infinite ease-in-out;
        margin: 0 auto 20px auto;
        display: block;
    }}

    @keyframes pulseAndGlow {{
        0% {{ transform: scale(1); filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4)); }}
        50% {{ transform: scale(1.05); filter: drop-shadow(0 0 25px rgba(239, 68, 68, 0.8)); }}
        100% {{ transform: scale(1); filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4)); }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. واجهة الاختيار (لوجو + 3 أعمدة تحته) ---
if 'step' not in st.session_state: st.session_state.step = 'select_grade'

if st.session_state.step == 'select_grade':
    st.markdown('<h1 class="main-title">محرك بحث الأبطال</h1>', unsafe_allow_html=True)
    
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="center-logo-img">', unsafe_allow_html=True)

    # إنشاء 3 أعمدة (كل عمود به صفين)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("GRADE 1"): play_magic_sound(); st.session_state.grade = 1; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 2"): play_magic_sound(); st.session_state.grade = 2; st.session_state.step = 'select_term'; st.rerun()
    
    with col2:
        if st.button("GRADE 3"): play_magic_sound(); st.session_state.grade = 3; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 4"): play_magic_sound(); st.session_state.grade = 4; st.session_state.step = 'select_term'; st.rerun()

    with col3:
        if st.button("GRADE 5"): play_magic_sound(); st.session_state.grade = 5; st.session_state.step = 'select_term'; st.rerun()
        if st.button("GRADE 6"): play_magic_sound(); st.session_state.grade = 6; st.session_state.step = 'select_term'; st.rerun()

# --- باقي الأجزاء المستقرة (ترم وبحث وتذييل) ---
elif st.session_state.step == 'select_term':
    g = st.session_state.grade
    st.markdown(f'<h2 style="text-align:center; color:#00d4ff;">Grade {g}</h2>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        img1 = get_base64(f"cover_g{g}_t1.jpg")
        if img1: st.image(f"data:image/jpeg;base64,{img1}", use_container_width=True)
        if st.button("TERM 1"): st.session_state.term = 1; st.session_state.step = 'search'; st.rerun()
    with c2:
        img2 = get_base64(f"cover_g{g}_t2.jpg")
        if img2: st.image(f"data:image/jpeg;base64,{img2}", use_container_width=True)
        if st.button("TERM 2"): st.session_state.term = 2; st.session_state.step = 'search'; st.rerun()
    if st.button("🔙 BACK"): st.session_state.step = 'select_grade'; st.rerun()

elif st.session_state.step == 'search':
    g, t = st.session_state.grade, st.session_state.term
    pdf_file = f"g{g}_t{t}.pdf"
    st.markdown(f'<h3 style="text-align:center;">Grade {g} - Term {t}</h3>', unsafe_allow_html=True)
    word = st.text_input("🔍 Search Word...", placeholder="Type...").strip()
    if word:
        st.audio(speak_clean(word))
        sentences, pages = advanced_search(pdf_file, word)
        if sentences:
            for i, s in enumerate(sentences[:10]):
                st.markdown(f'<div style="background:rgba(30,41,59,0.5); border-left:5px solid #00d4ff; padding:10px; border-radius:10px; margin:5px 0; direction:ltr; text-align:left;">{s["display"]}</div>', unsafe_allow_html=True)
                if st.button(f"🔊 Listen", key=f"v_{i}"): st.audio(speak_clean(s['raw']))
        if pages:
            for p in pages: st.image(p['image'], use_container_width=True)
    if st.button("🔙 BACK"): st.session_state.step = 'select_term'; st.rerun()

# التذييل مع الحقوق والرابط
st.markdown("""
    <div style="text-align:center; margin-top:40px; padding-bottom: 20px;">
        <p style="color:#64748b; font-size:0.8rem; margin-bottom:10px;">Created by Mr. Walid Elhagary</p>
        <a href="https://linktr.ee/ALABTAL.books" target="_blank" style="text-decoration:none; color:#00d4ff; border:1px solid #00d4ff; padding:8px 20px; border-radius:15px; font-size:0.8rem;">
            🔗 منصات الأبطال التعليمية
        </a>
    </div>
""", unsafe_allow_html=True)
