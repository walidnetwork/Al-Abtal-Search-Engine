import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة والتصميم السريع ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: #0f172a; color: white;
    }
    /* تصغير الأزرار لتناسب العرض الجانبي */
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #ef4444;
        color: white; font-weight: bold; font-size: 0.85rem; height: 2.5em; border: None;
    }
    .sentence-box {
        background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 8px;
        border-right: 5px solid #ef4444; font-size: 1.4rem; color: #ffffff !important;
    }
    .word-highlight { color: #ff4b4b; font-weight: bold; }

    /* تنسيق كارت الأيقونة */
    .icon-box {
        text-align: center;
        padding: 5px;
        border-radius: 10px;
        background-color: #1e293b;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }
    .icon-img { width: 80px; height: auto; border-radius: 5px; margin-bottom: 5px; }

    /* زر الفيسبوك المزدوج */
    .fb-split-btn {
        display: inline-flex; align-items: center; text-decoration: none;
        border-radius: 5px; overflow: hidden; font-family: Arial, sans-serif;
        font-weight: bold; margin-top: 15px;
    }
    .fb-left { background-color: #4b4b4b; color: white; padding: 8px 12px; display: flex; align-items: center; gap: 5px; font-size: 0.8rem; }
    .fb-right { background-color: #0078d4; color: white; padding: 8px 15px; font-size: 0.9rem; }
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

# --- 3. التنقل ---
if 'step' not in st.session_state: st.session_state.step = 'select_grade'

# --- 4. واجهة الأيقونات (واجهة واحدة بدون سكرول) ---
if st.session_state.step == 'select_grade':
    logo = get_base64('logo.png')
    if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="120"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>ALABTAL DICTIONARY</h3>", unsafe_allow_html=True)
    
    # توزيع الأيقونات في شبكة 3 أعمدة
    cols = st.columns(3)
    for i in range(1, 7):
        with cols[(i-1) % 3]:
            st.markdown(f'<div class="icon-box">', unsafe_allow_html=True)
            img_b64 = get_base64(f"cover_g{i}.jpg")
            if img_b64:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="icon-img">', unsafe_allow_html=True)
            if st.button(f"G {i}", key=f"g_{i}"):
                st.session_state.grade = i; st.session_state.step = 'select_term'; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- 5. واجهة الترم ---
elif st.session_state.step == 'select_term':
    g = st.session_state.grade
    st.markdown(f"<h3 style='text-align:center;'>الصف {g}</h3>", unsafe_allow_html=True)
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
    word = st.text_input("Search:", placeholder="Type here...").strip()
    if word:
        st.audio(speak_clean(word))
        sentences, pages = advanced_search(pdf_file, word)
        for i, s in enumerate(sentences[:10]):
            st.markdown(f"<div class='sentence-box'>📄 {s['display']}</div>", unsafe_allow_html=True)
            if st.button(f"🔊 Listen", key=f"v_{i}"): st.audio(speak_clean(s['raw']))
        for p in pages: st.image(p['image'], use_container_width=True)
    if st.button("🔙 عودة"): st.session_state.step = 'select_term'; st.rerun()

# --- 7. التذييل ---
st.write("---")
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='color:#94a3b8; font-size:0.8rem;'>Created by Mr. Walid Elhagary</div>
    <a href="https://www.facebook.com/share/15fGv6mC8C/" target="_blank" class="fb-split-btn">
        <div class="fb-left">FACEBOOK</div>
        <div class="fb-right">FOLLOW US</div>
    </a>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
