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

# --- 3. التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] { 
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; 
        background-color: #0f172a; color: white; 
    }
    .stButton>button { 
        width: 100%; border-radius: 15px; background: linear-gradient(135deg, #ef4444, #b91c1c); 
        color: white; font-weight: bold; height: 3.5em; border: none; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); 
    }
    .section-header { border-right: 5px solid #ef4444; padding-right: 15px; margin: 25px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 4. منطق التنقل والحالة ---
if 'page' not in st.session_state: st.session_state.page = 'gate'
if 'grade' not in st.session_state: st.session_state.grade = None
if 'term' not in st.session_state: st.session_state.term = None

# --- 5. بوابة الدخول (اختيار الصف الدراسي) ---
if st.session_state.page == 'gate':
    st.markdown("<h1 style='text-align:center;'>🦸‍♂️ مرحباً بك في عالم الأبطال</h1>", unsafe_allow_html=True)
    logo = get_base64('logo.png')
    if logo: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo}" width="180"></div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;'>اختر الصف الدراسي:</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.button("Primary 4 (Soon)")
    with c2:
        # هنا تظهر صورة غلاف رابعة أو خامسة إذا أردت، لكننا وضعنا الأزرار أولاً
        if st.button("Primary 5 ⭐"):
            st.session_state.grade = "Primary 5"
            st.session_state.page = 'select_term'
            st.rerun()
    with c3: 
        st.button("Primary 6 (Soon)")

# --- 6. اختيار الترم (مع ظهور صور الأغلفة) ---
elif st.session_state.page == 'select_term':
    st.markdown(f"<h1 style='text-align:center;'>قاموس الأبطال - {st.session_state.grade}</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>اختر الترم الدراسي:</h3>", unsafe_allow_html=True)
    
    t1, t2 = st.columns(2)
    with t1:
        # عرض غلاف الترم الأول
        cov1 = get_base64('cover1.jpg')
        if cov1: st.image(f"data:image/jpeg;base64,{cov1}", use_container_width=True)
        if st.button("الترم الأول (Term 1)"):
            st.session_state.term = "Term 1"
            st.session_state.page = 'app'
            st.rerun()
            
    with t2:
        # عرض غلاف الترم الثاني
        cov2 = get_base64('cover2.jpg')
        if cov2: st.image(f"data:image/jpeg;base64,{cov2}", use_container_width=True)
        if st.button("الترم الثاني (Term 2)"):
            st.session_state.term = "Term 2"
            st.session_state.page = 'app'
            st.rerun()
            
    if st.button("🔙 العودة لاختيار الصف"):
        st.session_state.page = 'gate'; st.session_state.grade = None; st.rerun()

# --- 7. التطبيق الرئيسي (البحث) ---
elif st.session_state.page == 'app':
    st.markdown(f"<h2 style='text-align:center;'>{st.session_state.grade} - {st.session_state.term}</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        query = st.text_input("🔍 ابحث عن كلمة داخل الكتاب:").strip()
        if query:
            st.session_state.search_word = query
            st.session_state.page = 'results'
            st.rerun()
    
    if st.button("🔙 تغيير الإعدادات"):
        st.session_state.page = 'gate'; st.rerun()

# --- 8. صفحة النتائج ---
elif st.session_state.page == 'results':
    word = st.session_state.search_word
    sentences, pages = advanced_search('book.pdf', word)
    
    st.markdown(f"<h3 class='section-header'>🔊 نطق الكلمة: {word}</h3>", unsafe_allow_html=True)
    st.audio(speak(word))
    
    if sentences:
        st.markdown("<h3 class='section-header'>📝 جمل من الكتاب</h3>", unsafe_allow_html=True)
        for s in sentences[:8]:
            st.markdown(f"<div style='background:#1e293b; padding:15px; border-radius:10px; margin-bottom:10px; border-right:4px solid #ef4444;'>📄 {s['display']}</div>", unsafe_allow_html=True)
    
    if pages:
        st.markdown("<h3 class='section-header'>📖 صفحات من الكتاب</h3>", unsafe_allow_html=True)
        for p in pages:
            st.image(p['image'], caption=f"صفحة {p['num']}", use_container_width=True)
            
    if st.button("🔙 عودة للبحث"):
        st.session_state.page = 'app'; st.rerun()

# --- 9. التذييل ---
st.write("---")
p_img = get_base64('personal_photo.jpg')
if p_img:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/jpeg;base64,{p_img}" style="width:100px; border-radius:50%; border:2px solid #ef4444;"></div>', unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
