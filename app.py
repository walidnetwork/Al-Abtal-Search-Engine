import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re
import time # ضروري للصوت السحري

# --- 1. إعدادات الهوية ---
st.set_page_config(
    page_title="ALABTAL SEARCH ENGINE", 
    page_icon="logo.png",
    layout="wide"
)

# --- 2. دوال البحث والنطق (ثابتة تماماً) ---
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

# --- 🪄 دالة الصوت السحري ---
# ستقوم بتشغيل صوت قصير عند النقر (يتطلب ملف chime.mp3 بجانب الكود)
def play_magic_sound():
    sound_file = "chime.mp3"
    if os.path.exists(sound_file):
        # نقوم بتحميل الصوت لمرة واحدة
        with open(sound_file, "rb") as f:
            sound_bytes = f.read()
        
        # نقوم بإنشاء مشغل صوتي مؤقت
        sound_base64 = base64.b64encode(sound_bytes).decode()
        audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{sound_base64}" type="audio/mp3"></audio>'
        
        # نقوم بحقن مشغل الصوت في الصفحة وتختفي فوراً
        st.markdown(audio_html, unsafe_allow_html=True)
        # تأخير قصير جداً لضمان تشغيل الصوت قبل الـ rerun
        # time.sleep(0.1) # جرب تفعيله لو الصوت لم يعمل

# --- 3. تصميم CSS المضبط (اللوجو فوق والصفوف تحت) ---
logo_base64 = get_base64('logo.png')

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&family=Orbitron:wght@700&display=swap');
    
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
        overflow-x: hidden; /* منع التمرير الأفقي */
    }}

   .main-title {{
        text-align: center;
        margin: 20px 0;
        color: #FFFFFF !important;
        font-family: 'Orbitron', sans-serif; /* خط تكنولوجي رائع */
    }}
    .main-title .top-word {{
        display: block;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 6px;
        line-height: 1;
    }}
    .main-title .bottom-word {{
        display: block;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 3px;
        text-transform: lowercase;
        margin-top: 5px;
        opacity: 0.9;
    }}

    /* تصميم الأزرار النيون (Grade) */
    .stButton>button {{
        width: 100% !important;
        background: rgba(0, 212, 255, 0.03) !important;
        border: 2.5px solid #00d4ff !important;
        color: #00d4ff !important;
        border-radius: 12px !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: clamp(0.7rem, 2vw, 1rem) !important;
        height: clamp(50px, 8vh, 60px) !important;
        margin-bottom: 12px !important;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        background: #00d4ff !important;
        color: #000 !important;
        box-shadow: 0 0 25px #00d4ff;
        transform: translateY(-3px);
    }}

    /* محاذاة الأعمدة */
    [data-testid="column"] {{ text-align: center !important; }}

    /* حاوية اللوجو - نضمن توسيطه فوق الصفوف */
    .logo-container {{
        text-align: center;
        margin-bottom: 30px;
    }}

    .center-logo-img {{
        width: 100%;
        max-width: clamp(200px, 40vw, 280px);
        animation: pulseAndGlow 3s infinite ease-in-out;
    }}

    @keyframes pulseAndGlow {{
        0% {{ transform: scale(1); filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4)); }}
        50% {{ transform: scale(1.04); filter: drop-shadow(0 0 25px rgba(239, 68, 68, 0.7)); }}
        100% {{ transform: scale(1); filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4)); }}
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

# --- 4. واجهة الاختيار (اللوجو فوق والصفوف تحت في عمودين) ---
if 'step' not in st.session_state: st.session_state.step = 'select_grade'

if st.session_state.step == 'select_grade':
        st.markdown(f'<h1 class="main-title"><span class="top-word">ALABTAL</span><span class="bottom-word">search engine</span></h1>', unsafe_allow_html=True)
        
        if logo_base64:
            st.markdown(f'''
                <div style="text-align: center; margin-top: -40px;">
                    <img src="data:image/png;base64,{logo_base64}" style="width: 160px; margin-bottom: 10px;">
                    <p style="color: white; font-family: Cairo; font-size: 1.3rem; font-weight: bold; margin-top: -10px;">اختر صفك الدراسى</p>
                </div>
            ''', unsafe_allow_html=True)

        # الزراير في عمودين منسقين
        _, col_left, col_right, _ = st.columns([0.2, 1, 1, 0.2], gap="medium")

        with col_left:
            if st.button("GRADE 1"): play_magic_sound(); st.session_state.grade = 1; st.session_state.step = 'select_term'; st.rerun()
            if st.button("GRADE 2"): play_magic_sound(); st.session_state.grade = 2; st.session_state.step = 'select_term'; st.rerun()
            if st.button("GRADE 3"): play_magic_sound(); st.session_state.grade = 3; st.session_state.step = 'select_term'; st.rerun()

        with col_right:
            if st.button("GRADE 4"): play_magic_sound(); st.session_state.grade = 4; st.session_state.step = 'select_term'; st.rerun()
            if st.button("GRADE 5"): play_magic_sound(); st.session_state.grade = 5; st.session_state.step = 'select_term'; st.rerun()
            if st.button("GRADE 6"): play_magic_sound(); st.session_state.grade = 6; st.session_state.step = 'select_term'; st.rerun()
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
    word = st.text_input("🔍 Search Word...", placeholder="Type...").strip()
    
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
st.markdown("<div style='text-align: center; color: #FFFFFF; font-family: sans-serif; font-size: 0.85rem; margin-top: 10px; margin-bottom: -10px; opacity: 0.8;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align:center; margin-top:30px;">
        <a href="https://linktr.ee/ALABTAL.books" target="_blank" style="text-decoration:none; color:#00d4ff; border:1px solid #00d4ff; padding:5px 10px; border-radius:10px; font-size:0.7rem;">
            🔗 منصات الأبطال التعليمية
        </a>
    </div>
""", unsafe_allow_html=True)
