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
                # استخراج الصفحة كصورة
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                # استخراج الجمل
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

# --- 3. التصميم الجمالي (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #0f172a; color: white; }
    .stButton>button { width: 100%; border-radius: 15px; background: linear-gradient(135deg, #ef4444, #b91c1c); color: white; font-weight: bold; height: 3.5em; border: none; box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-size: 1.1rem; }
    .stButton>button:hover { transform: scale(1.03); transition: 0.3s; background: #ef4444; }
    .section-header { border-right: 5px solid #ef4444; padding-right: 15px; margin: 25px 0; color: #f1f5f9; }
    .search-box { background: #1e293b; padding: 30px; border-radius: 20px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# --- 4. منطق التنقل ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'grade' not in st.session_state: st.session_state.grade = None

# --- 5. بوابة الدخول (اختيار الصف الدراسي) ---
if st.session_state.page == 'gate':
    st.markdown("<h1 style='text-align:center; font-size: 3rem;'>🦸‍♂️ سلسلة كتب الأبطال</h1>", unsafe_allow_html=True)
    logo = get_base64('logo.png')
    if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="220"></div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;'>اختر الصف الدراسي للبدء:</h2>", unsafe_allow_html=True)
    col_p4, col_p5, col_p6 = st.columns(3)
    
    with col_p4:
        if st.button("Primary 4 📚"): st.warning("قريباً إن شاء الله")
    with col_p5:
        if st.button("Primary 5 ⭐"):
            st.session_state.grade = "Primary 5"
            st.session_state.page = 'select_term'
            st.rerun()
    with col_p6:
        if st.button("Primary 6 📖"): st.warning("قريباً إن شاء الله")

# --- 6. اختيار الترم ---
elif st.session_state.page == 'select_term':
    st.markdown(f"<h1 style='text-align:center;'>قاموس الأبطال - {st.session_state.grade}</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>اختر الترم الدراسي:</h3>", unsafe_allow_html=True)
    
    t1, t2 = st.columns(2)
    with t1:
        if st.button("الترم الأول (First Term) ❄️"):
            st.session_state.term = "Term 1"
            st.session_state.page = 'main_app'
            st.rerun()
    with t2:
        if st.button("الترم الثاني (Second Term) 🌸"):
            st.session_state.term = "Term 2"
            st.session_state.page = 'main_app'
            st.rerun()
    
    if st.button("🔙 العودة لاختيار الصف"):
        st.session_state.page = 'gate'; st.rerun()

# --- 7. التطبيق الرئيسي (البحث والغلاف) ---
elif st.session_state.page == 'main_app':
    st.markdown(f"<h2 style='text-align:center;'>{st.session_state.grade} - {st.session_state.term}</h2>", unsafe_allow_html=True)
    
    # عرض الغلاف المناسب
    cover_img = 'cover1.jpg' if st.session_state.term == "Term 1" else 'cover2.jpg'
    cover = get_base64(cover_img)
    if cover:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{cover}" width="350" style="border-radius:20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
    with col_s2:
        st.markdown("<div class='search-box'>", unsafe_allow_html=True)
        query = st.text_input("🔍 ابحث عن أي كلمة بالإنجليزية:", placeholder="مثلاً: Beach, Hello, Egypt...").strip()
        if query:
            st.session_state.search_word = query
            st.session_state.page = 'results'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    if st.button("🔙 تغيير الصف أو الترم"):
        st.session_state.page = 'gate'; st.rerun()

# --- 8. صفحة عرض النتائج ---
elif st.session_state.page == 'results':
    word = st.session_state.search_word
    st.markdown(f"<h1 style='text-align:center;'>🔍 نتائج الأبطال للكلمة: {word}</h1>", unsafe_allow_html=True)
    
    sentences, pages = advanced_search('book.pdf', word)
    
    # النطق
    st.markdown(f"<h3 class='section-header'>🔊 اسمع نطق الكلمة</h3>", unsafe_allow_html=True)
    st.audio(speak(word))
    
    # عرض الجمل
    if sentences:
        st.markdown("<h3 class='section-header'>📝 جمل من الكتاب</h3>", unsafe_allow_html=True)
        for s in sentences[:8]:
            st.markdown(f"<div style='background:#1e293b; padding:15px; border-radius:15px; margin-bottom:10px; border-right:5px solid #ef4444;'>📄 {s['display']}</div>", unsafe_allow_html=True)
    
    # عرض الصفحات
    if pages:
        st.markdown("<h3 class='section-header'>📖 شاهد الكلمة داخل الكتاب</h3>", unsafe_allow_html=True)
        for p in pages:
            st.image(p['image'], caption=f"صفحة رقم {p['num']}", use_container_width=True)
            
    if st.button("🔙 العودة للبحث"):
        st.session_state.page = 'main_app'; st.rerun()

# --- 9. التذييل (Footer) ---
st.write("---")
p_img = get_base64('personal_photo.jpg')
if p_img:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{p_img}" style="width:110px; border-radius:50%; border:3px solid #ef4444;"></div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-weight:bold; color:#f8fafc;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#94a3b8; font-size:0.9rem;'>سلسلة كتب الأبطال التعليمية © 2026</div>", unsafe_allow_html=True)
