import streamlit as st
import base64
import os
import fitz  # PyMuPDF
from gtts import gTTS
import io
import re

# --- 1. إعدادات الصفحة والهوية الاحترافية ---
st.set_page_config(
    page_title="ALABTAL DICTIONARY",
    page_icon="logo_animated.gif",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. دالة النطق الصوتي ---
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except: return None

# --- 3. دالة معالجة الصور (Base64) ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except: return ""
    return ""

# --- 4. محرك البحث المتطور (استخلاص جمل + صفحات كاملة) ---
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
                # استخراج الأسطر التي تحتوي على الكلمة فقط
                lines = text.split('\n')
                for line in lines:
                    clean_line = line.strip()
                    if word_pattern.search(clean_line) and len(clean_line) > len(word):
                        # تمييز الكلمة بخط عريض ولون مختلف
                        display_text = re.sub(word_pattern, f"<b style='color:#ef4444;'>{word}</b>", clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({
                                "display": display_text, 
                                "raw": clean_line,
                                "page": page_num + 1
                            })

                # حفظ الصفحة كاملة بجودة عالية
                if page_num not in found_pages_indices:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                    found_pages_indices.append(page_num)
                    
            if len(full_pages) >= 5: break # للسرعة
        return extracted_sentences, full_pages
    except: return [], []

# --- 5. هندسة الواجهة وتنسيق الألوان (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    .main-title { text-align: center; font-family: 'Cairo', sans-serif; font-size: 3rem; margin-bottom: 0; }
    label { color: white !important; font-weight: bold !important; font-family: 'Cairo'; font-size: 1.2rem !important; }
    .stTextInput input { background-color: white !important; color: black !important; font-size: 1.1rem !important; height: 50px !important; border-radius: 12px !important; }
    .sentence-card { 
        background: white; color: #0f172a; padding: 25px; border-radius: 15px; 
        margin-bottom: 10px; border-right: 10px solid #ef4444; box-shadow: 0px 6px 15px rgba(0,0,0,0.3);
    }
    .stButton>button { width: 100%; border-radius: 12px; background: #ef4444; color: white; font-weight: bold; height: 50px; border: none; font-size: 1.1rem; transition: 0.3s; }
    .stButton>button:hover { background: #b91c1c; transform: scale(1.02); }
    .section-header { border-bottom: 3px solid #ef4444; padding-bottom: 5px; margin-top: 40px; font-family: 'Cairo'; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. نظام التنقل والصفحات ---
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    logo_b64 = get_base64('logo_animated.gif')
    if logo_b64: st.markdown(f'<center><img src="data:image/gif;base64,{logo_b64}" width="220"></center>', unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>قاموس الأبطال</h1>", unsafe_allow_html=True)
    
    # عرض الصفوف 1-6 بترتيب ثابت
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
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 عودة للقائمة الرئيسية"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث والنتائج ---
elif st.session_state.page == 'search':
    st.markdown("<h2 style='text-align:center; font-family: Cairo;'>🔍 محرك بحث الأبطال</h2>", unsafe
