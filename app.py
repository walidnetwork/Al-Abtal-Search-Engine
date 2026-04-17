import streamlit as st
import pandas as pd
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

# --- 2. دالات المساعدة ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
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
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                lines = text.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if word_pattern.search(clean_line) and len(clean_line) > 3:
                        display_text = re.sub(word_pattern, f"<b style='color:#ef4444;'>{word}</b>", clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({"display": display_text, "raw": clean_line, "page": page_num + 1})
        doc.close()
    except: pass
    return extracted_sentences, full_pages

# --- 3. التصميم (CSS) لإعادة الشكل القديم ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #1e293b; color: white; }
    .stButton>button { width: 100%; border-radius: 12px; background: #ef4444; color: white; font-weight: bold; height: 3.5em; border: none; margin-bottom: 20px; }
    .cover-img { width: 100%; border-radius: 15px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    </style>
""", unsafe_allow_html=True)

# --- 4. منطق التنقل ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'grade' not in st.session_state: st.session_state.grade = None

# --- 5. بوابة الدخول (الشكل القديم بالأغلفة) ---
if st.session_state.page == 'gate':
    st.markdown("<h1 style='text-align:center;'>قاموس الأبطال</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>ALABTAL DICTIONARY</p>", unsafe_allow_html=True)
    
    # عرض غلاف الصف الأول (مثال)
    c1 = get_base64('cover1.jpg') # تأكد من اسم ملف الغلاف لديك
    if c1: st.markdown(f'<img src="data:image/jpeg;base64,{c1}" class="cover-img">', unsafe_allow_html=True)
    if st.button("دخول الصف 1"):
        st.warning("قريباً")

    # عرض غلاف الصف الثاني
    c2 = get_base64('cover2.jpg')
    if c2: st.markdown(f'<img src="data:image/jpeg;base64,{c2}" class="cover-img">', unsafe_allow_html=True)
    if st.button("دخول الصف 2"):
        st.warning("قريباً")

    # عرض غلاف الصف الخامس (المتاح)
    c5 = get_base64('logo.png') # أو غلاف الصف الخامس
    if c5: st.markdown(f'<img src="data:image/png;base64,{c5}" class="cover-img">', unsafe_allow_html=True)
    if st.button("دخول الصف 5"):
        st.session_state.grade = "Primary 5"
        st.session_state.page = 'select_term'
        st.rerun()

# --- 6. اختيار الترم ---
elif st.session_state.page == 'select_term':
    st.markdown(f"<h2 style='text-align:center;'>قاموس {st.session_state.grade}</h2>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("الترم الأول"):
            st.session_state.term = "Term 1"; st.session_state.page = 'app'; st.rerun()
    with col_t2:
        if st.button("الترم الثاني"):
            st.session_state.term = "Term 2"; st.session_state.page = 'app'; st.rerun()
    if st.button("🔙 العودة"): st.session_state.page = 'gate'; st.rerun()

# --- 7. البحث والنتائج ---
elif st.session_state.page == 'app':
    st.markdown(f"<h2 style='text-align:center;'>بحث: {st.session_state.term}</h2>", unsafe_allow_html=True)
    query = st.text_input("🔍 ابحث عن كلمة:").strip()
    if query:
        st.session_state.search_word = query; st.session_state.page = 'results'; st.rerun()
    if st.button("🔙 تغيير"): st.session_state.page = 'gate'; st.rerun()

elif st.session_state.page == 'results':
    word = st.session_state.search_word
    sentences, pages = advanced_search('book.pdf', word)
    st.markdown(f"### نتائج البحث: {word}")
    st.audio(speak(word))
    if sentences:
        for s in sentences[:5]: st.info(s['display'])
    if pages:
        for p in pages: st.image(p['image'], use_container_width=True)
    if st.button("🔙 عودة"): st.session_state.page = 'app'; st.rerun()

# --- التذييل ---
st.write("---")
p_img = get_base64('personal_photo.jpg')
if p_img: st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{p_img}" style="width:80px; border-radius:50%; border:2px solid #ef4444;"></div>', unsafe_allow_html=True)
