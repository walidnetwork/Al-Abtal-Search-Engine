import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة - تصميم مسطح وسريع جداً ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;
        background-color: #0f172a; color: white;
    }
    /* أزرار مسطحة وسريعة الاستجابة */
    .stButton>button {
        width: 100%; border-radius: 10px; background-color: #ef4444;
        color: white; font-weight: bold; font-size: 1.1rem; height: 3em;
        border: None; box-shadow: None !important;
    }
    .cover-card { 
        border-radius: 10px; border: 1px solid #334155; 
        box-shadow: None !important; 
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

@st.cache_data(show_spinner=False)
def speak_clean(text):
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    tts = gTTS(text=clean_text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

@st.cache_data(show_spinner=False)
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
                pix = page.get_pixmap(matrix=fitz.Matrix(1.1, 1.1)) # تقليل الجودة قليلاً لسرعة التحميل
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

# --- 3. إدارة التنقل - يبدأ مباشرة من اختيار الصف ---
if 'step' not in st.session_state: 
    st.session_state.step = 'select_grade'

# --- 4. واجهة اختيار الصف (الواجهة الأولى الآن) ---
if st.session_state.step == 'select_grade':
    st.markdown("<h2 style='text-align:center;'>🦸‍♂️ قاموس الأبطال - اختر صفك</h2>", unsafe_allow_html=True)
    for i in range(1, 7):
        col_img, col_btn = st.columns([1, 2])
        with col_img:
            img_b64 = get_base64(f"cover_g{i}.jpg")
            if img_b64: 
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="cover-card" style="width:140px;">', unsafe_allow_html=True)
        with col_btn:
            st.write("<br>", unsafe_allow_html=True)
            if st.button(f"دخول الصف {i} الابتدائي", key=f"g_btn_{i}"):
                st.session_state.grade = i
                st.session_state.step = 'select_term'
                st.rerun()
        st.write("---")

# --- 5. واجهة اختيار الترم ---
elif st.session_state.step == 'select_term':
    g = st.session_state.grade
    st.markdown(f"<h2 style='text-align:center;'>الصف {g} - اختر الترم</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        img_t1 = get_base64(f"cover_g{g}_t1.jpg")
        if img_t1: st.image(f"data:image/jpeg;base64,{img_t1}", width=180)
        if st.button("الترم الأول", key="t1_btn"): 
            st.session_state.term = 1; st.session_state.step = 'search'; st.rerun()
    with c2:
        img_t2 = get_base64(f"cover_g{g}_t2.jpg")
        if img_t2: st.image(f"data:image/jpeg;base64,{img_t2}", width=180)
        if st.button("الترم الثاني", key="t2_btn"): 
            st.session_state.term = 2; st.session_state.step = 'search'; st.rerun()
    
    if st.button("🔙 العودة لاختيار الصف"):
        st.session_state.step = 'select_grade'; st.rerun()

# --- 6. واجهة محرك البحث ---
elif st.session_state.step == 'search':
    g, t = st.session_state.grade, st.session_state.term
    # محاولة فتح ملف الصف والترم المختار، أو الملف الاحتياطي
    pdf_file = f"g{g}_t{t}.pdf"
    if not os.path.exists(pdf_file): pdf_file = "g1_t2.pdf" 

    word = st.text_input("ادخل الكلمة (English):", placeholder="اكتب هنا...").strip()
    if word:
        st.audio(speak_clean(word))
        sentences, pages = advanced_search(pdf_file, word)
        
        if sentences:
            st.markdown("### 📝 جمل من المنهج")
            for i, s in enumerate(sentences[:10]):
                st.markdown(f"<div class='sentence-box'>📄 {s['display']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 استمع", key=f"voice_btn_{i}"):
                    st.audio(speak_clean(s['raw']))
        
        if pages:
            st.markdown("### 📖 من داخل الكتاب")
            for p in pages: st.image(p['image'], use_container_width=True)

    if st.button("🔙 العودة لاختيار الترم"): 
        st.session_state.step = 'select_term'; st.rerun()

# --- 7. التذييل (Footer) ---
st.write("---")
st.markdown("<div style='text-align:center; color:#94a3b8; font-size:0.8rem;'>Created by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
