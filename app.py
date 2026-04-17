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
    if not os.path.exists(pdf_path):
        return [], []
    
    try:
        doc = fitz.open(pdf_path)
        word_pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            if word_pattern.search(text):
                # استخراج الجمل
                lines = text.split('\n')
                for line in lines:
                    clean_line = re.sub(r'[^a-zA-Z0-9\s,.\'!?]', '', line).strip()
                    if word_pattern.search(clean_line) and len(clean_line) > len(word):
                        display_text = re.sub(word_pattern, f"<b style='color:#ef4444;'>{word}</b>", clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({
                                "display": display_text,
                                "raw": clean_line,
                                "page": page_num + 1
                            })
                
                # استخراج الصفحة كصورة
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                full_pages.append({"num": page_num + 1, "image": img_data})
        doc.close()
    except Exception as e:
        print(f"Error: {e}")
        
    return extracted_sentences, full_pages

# --- 3. واجهة المستخدم والتصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: #1e293b; color: white;
    }
    .main-title { color: #f8fafc; text-align: center; font-size: 3rem; }
    .stButton>button { width: 100%; border-radius: 12px; background: #ef4444; color: white; font-weight: bold; }
    .section-header { border-right: 5px solid #ef4444; padding-right: 15px; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 4. منطق التنقل ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- 5. الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.markdown("<h1 class='main-title'>🦸‍♂️ قاموس الأبطال</h1>", unsafe_allow_html=True)
    logo = get_base64('logo.png')
    if logo:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="200"></div>', unsafe_allow_html=True)
    
    search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
    with search_col2:
        query = st.text_input("🔍 ابحث عن كلمة", placeholder="ادخل الكلمة هنا...").strip()
        if query:
            st.session_state.search_word = query
            st.session_state.page = 'results'
            st.rerun()

# --- 6. صفحة النتائج ---
elif st.session_state.page == 'results':
    word = st.session_state.search_word
    st.markdown(f"<h2 style='text-align:center;'>نتائج البحث عن: {word}</h2>", unsafe_allow_html=True)
    
    sentences, pages = advanced_search('book.pdf', word)
    
    # نطق الكلمة
    st.markdown(f"<h3 class='section-header'>🔊 نطق الكلمة</h3>", unsafe_allow_html=True)
    st.audio(speak(word))
    
    if sentences:
        st.markdown("<h3 class='section-header'>📝 الجمل التعليمية</h3>", unsafe_allow_html=True)
        for s in sentences[:5]:
            st.markdown(f"<div style='background:#334155; padding:10px; border-radius:10px; margin-bottom:5px;'>📄 {s['display']}</div>", unsafe_allow_html=True)
    
    if pages:
        st.markdown("<h3 class='section-header'>📖 صفحات الكتاب</h3>", unsafe_allow_html=True)
        for p in pages:
            st.image(p['image'], caption=f"صفحة {p['num']}", use_container_width=True)
            
    if st.button("🔙 عودة للرئيسية"):
        st.session_state.page = 'home'
        st.rerun()

# --- 7. التذييل (Footer) ---
st.write("---")
p_img = get_base64('personal_photo.jpg')
if p_img:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{p_img}" style="width:100px; border-radius:50%; border:2px solid #ef4444;"></div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
