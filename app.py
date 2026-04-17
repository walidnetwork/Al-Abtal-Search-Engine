import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: #0f172a; color: white;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; background-color: #ef4444;
        color: white; font-weight: bold; font-size: 1.1rem; height: 3.5em; border: None;
    }
    .sentence-box {
        background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 8px;
        border-right: 5px solid #ef4444; font-size: 1.4rem; color: #ffffff !important;
    }
    .word-highlight { color: #ff4b4b; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. دالات المساعدة ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def speak(text):
    tts = gTTS(text=text, lang='en')
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

# --- 3. منطق التنقل والحالة ---
if 'page' not in st.session_state: st.session_state.page = 'select_grade'
if 'grade' not in st.session_state: st.session_state.grade = None

# --- 4. واجهة اختيار الصف ---
if st.session_state.page == 'select_grade':
    logo = get_base64('logo.png')
    if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="180"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>ALABTAL DICTIONARY</h2>", unsafe_allow_html=True)
    
    for i in range(1, 7):
        col_img, col_btn = st.columns([1, 2])
        with col_img:
            img_b64 = get_base64(f"cover_g{i}.jpg")
            if img_b64: st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" style="width:130px; border-radius:10px;">', unsafe_allow_html=True)
        with col_btn:
            st.write("<br>", unsafe_allow_html=True)
            if st.button(f"دخول الصف {i} الابتدائي", key=f"g_btn_{i}"):
                st.session_state.grade = i
                st.session_state.page = 'select_term'
                st.rerun()
        st.write("---")

# --- 5. واجهة اختيار الترم ---
elif st.session_state.page == 'select_term':
    g = st.session_state.grade
    st.markdown(f"<h2 style='text-align:center;'>الصف {g} الابتدائي</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        img_t1 = get_base64(f"cover_g{g}_t1.jpg")
        if img_t1: st.image(f"data:image/jpeg;base64,{img_t1}", width=200)
        if st.button("الترم الأول", key="t1_btn"):
            st.session_state.term = 1; st.session_state.page = 'app'; st.rerun()
    with c2:
        img_t2 = get_base64(f"cover_g{g}_t2.jpg")
        if img_t2: st.image(f"data:image/jpeg;base64,{img_t2}", width=200)
        if st.button("الترم الثاني", key="t2_btn"):
            st.session_state.term = 2; st.session_state.page = 'app'; st.rerun()
    if st.button("🔙 العودة"): st.session_state.page = 'select_grade'; st.rerun()

# --- 6. التطبيق الرئيسي (البحث) ---
elif st.session_state.page == 'app':
    g, t = st.session_state.grade, st.session_state.term
    pdf_file = f"g{g}_t{t}.pdf"
    if not os.path.exists(pdf_file): pdf_file = "book.pdf" 
    
    st.markdown(f"<h2 style='text-align:center;'>محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    word = st.text_input("ادخل الكلمة للبحث عنها:", placeholder="...").strip()
    
    if word:
        st.audio(speak(word))
        sentences, pages = advanced_search(pdf_file, word)
        if sentences:
            st.markdown("### 📝 جمل من المنهج")
            for i, s in enumerate(sentences[:10]):
                st.markdown(f"<div class='sentence-box'>📄 {s['display']}</div>", unsafe_allow_html=True)
        if pages:
            st.markdown("### 📖 صفحات من الكتاب")
            for p in pages: st.image(p['image'], use_container_width=True)
            
    if st.button("🔙 تغيير الترم"): st.session_state.page = 'select_term'; st.rerun()

# --- 7. التذييل ---
st.write("---")
st.markdown("<div style='text-align:center; color:#94a3b8;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
