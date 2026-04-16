import streamlit as st
import base64
import os
import fitz  # PyMuPDF
from gtts import gTTS
import io
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="ALABTAL DICTIONARY",
    page_icon="logo_animated.gif",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. دالة النطق ---
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except: return None

# --- 3. دالة جلب الصور ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except: return ""
    return ""

# --- 4. محرك البحث ---
def advanced_search(pdf_path, word):
    extracted_sentences = []
    full_pages = []
    if not os.path.exists(pdf_path): return None, None
    try:
        doc = fitz.open(pdf_path)
        word_pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        found_pages_indices = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if word_pattern.search(text):
                lines = text.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if word_pattern.search(clean_line) and len(clean_line) > len(word):
                        display_text = re.sub(word_pattern, f"<b style='color:#ef4444;'>{word}</b>", clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({"display": display_text, "raw": clean_line, "page": page_num + 1})
                if page_num not in found_pages_indices:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                    found_pages_indices.append(page_num)
            if len(full_pages) >= 5: break
        return extracted_sentences, full_pages
    except: return [], []

# --- 5. تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    label { color: white !important; font-weight: bold !important; font-family: 'Cairo'; }
    .stTextInput input { background-color: white !important; color: black !important; font-weight: bold; border-radius: 10px; }
    .sentence-card { background: white; color: #0f172a; padding: 20px; border-radius: 15px; margin-bottom: 10px; border-right: 10px solid #ef4444; }
    .stButton>button { width: 100%; border-radius: 12px; background: #ef4444; color: white; font-weight: bold; height: 50px; border: none; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    logo_b64 = get_base64('logo_animated.gif')
    if logo_b64: st.markdown(f'<center><img src="data:image/gif;base64,{logo_b64}" width="220"></center>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-family:Cairo;'>قاموس الأبطال</h1>", unsafe_allow_html=True)
    for row_grades in [["g1", "g2", "g3"], ["g4", "g5", "g6"]]:
        cols = st.columns(3)
        for i, gid in enumerate(row_grades):
            with cols[i]:
                cover = f"cover_{gid}.jpg"
                if os.path.exists(cover): st.image(cover, use_container_width=True)
                if st.button(f"دخول الصف {gid[1]}", key=gid):
                    st.session_state.grade_id, st.session_state.page = gid, 'select_term'; st.rerun()

# --- صفحة اختيار الترم ---
elif st.session_state.page == 'select_term':
    st.markdown("<h1 style='text-align:center; font-family: Cairo;'>📚 اختر الترم الدراسي</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    gid = st.session_state.grade_id
    for i, t in enumerate(["t1", "t2"]):
        with [col1, col2][i]:
            t_cover = f"cover_{gid}_{t}.jpg"
            if os.path.exists(t_cover): st.image(t_cover, use_container_width=True)
            if st.button(f"تصفح الترم {'الأول' if t=='t1' else 'الثاني'}", key=f"btn_{t}"):
                st.session_state.term, st.session_state.page = t, 'search'; st.rerun()
    if st.button("🔙 العودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث والنتائج (التي كان بها الخطأ) ---
elif st.session_state.page == 'search':
    st.markdown("<h2 style='text-align:center; font-family: Cairo;'>🔍 محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    query = st.text_input("ادخل الكلمة (English):")
    if query:
        st.markdown(f"### 🔊 نطق الكلمة: {query}")
        q_audio = speak(query)
        if q_audio: st.audio(q_audio)
        pdf_path = f"{st.session_state.grade_id}_{st.session_state.term}.pdf"
        with st.spinner('بطلنا يبحث...'):
            sentences, pages = advanced_search(pdf_path, query)
            if sentences:
                for s in sentences:
                    st.markdown(f'<div class="sentence-card"><p style="font-size:1.4rem;">{s["display"]}</p><small>Page: {s["page"]}</small></div>', unsafe_allow_html=True)
                    s_audio = speak(s['raw'])
                    if s_audio: st.audio(s_audio)
                for p in pages:
                    st.image(p['image'], caption=f"Page {p['num']}", use_container_width=True)
            else: st.warning("لم نجد نتائج.")
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- Footer ---
st.markdown("---")
f_c1, f_c2, f_c3 = st.columns([1, 2, 1])
with f_c2:
    pers_img = get_base64('personal_photo.jpg')
    if pers_img: st.markdown(f'<center><img src="data:image/jpeg;base64,{pers_img}" style="width:110px; border-radius:50%; border:3px solid #ef4444;"></center>', unsafe_allow_html=True)
    st.markdown("<center><h3>Created by Mr. Walid</h3></center>", unsafe_allow_html=True)
