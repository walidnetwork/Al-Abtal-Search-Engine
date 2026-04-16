import streamlit as st
import base64
import os
import fitz  # PyMuPDF
from gtts import gTTS
import io
import re

# --- 1. إعدادات الصفحة والهوية ---
st.set_page_config(
    page_title="ALABTAL DICTIONARY",
    page_icon="logo_animated.gif",
    layout="wide"
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

# --- 4. محرك البحث الذكي (استخراج جمل محددة + صفحات كاملة) ---
def advanced_search(pdf_path, word):
    extracted_sentences = []
    full_pages = []
    
    if not os.path.exists(pdf_path): return None, None
    
    try:
        doc = fitz.open(pdf_path)
        # البحث عن الكلمة مع تجاهل حالة الأحرف
        word_pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        
        found_pages_indices = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            # إذا وجدت الكلمة في الصفحة
            if word_pattern.search(text):
                # تقسيم النص إلى أسطر/جمل نظيفة
                lines = text.split('\n')
                for line in lines:
                    if word_pattern.search(line) and len(line.strip()) > len(word):
                        clean_line = line.strip()
                        # تمييز الكلمة داخل الجملة لجعلها بارزة
                        highlighted_text = re.sub(word_pattern, f"<u>{word}</u>", clean_line)
                        
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({
                                "display": highlighted_text, 
                                "raw": clean_line,
                                "page": page_num + 1
                            })

                # حفظ الصفحة كاملة كصورة
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
    .sentence-card { 
        background: white; 
        color: #0f172a; 
        padding: 25px; 
        border-radius: 15px; 
        margin-bottom: 15px; 
        border-right: 10px solid #ef4444;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.4);
        text-align: left;
    }
    .sentence-text { font-size: 1.6rem; font-weight: 800; color: #1e3a8a; line-height: 1.4; }
    .sentence-text u { color: #ef4444; text-decoration: none; border-bottom: 3px solid #ef4444; }
    .page-info { color: #64748b; font-size: 0.9rem; margin-top: 10px; font-weight: bold; }
    .section-title { border-bottom: 2px solid #ef4444; padding-bottom: 10px; margin-top: 40px; font-family: 'Cairo'; }
    .stTextInput input { background-color: white !important; color: black !important; font-size: 1.2rem !important; height: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'home'

# --- التنقل (Home / Terms) ---
if st.session_state.page == 'home':
    logo = get_base64('logo_animated.gif')
    if logo: st.markdown(f'<center><img src="data:image/gif;base64,{logo}" width="200"></center>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-family: Cairo;'>قاموس الأبطال</h1>", unsafe_allow_html=True)
    for row in [["g1", "g2", "g3"], ["g4", "g5", "g6"]]:
        cols = st.columns(3)
        for i, gid in enumerate(row):
            with cols[i]:
                img = f"cover_{gid}.jpg"
                if os.path.exists(img): st.image(img, use_container_width=True)
                if st.button(f"دخول الصف {gid[1]}", key=gid):
                    st.session_state.grade_id, st.session_state.page = gid, 'select_term'; st.rerun()

elif st.session_state.page == 'select_term':
    st.markdown("<h1 style='text-align:center; font-family: Cairo;'>📚 اختر الترم الدراسي</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    gid = st.session_state.grade_id
    for i, t in enumerate(["t1", "t2"]):
        with [col1, col2][i]:
            img = f"cover_{gid}_{t}.jpg"
            if os.path.exists(img): st.image(img, use_container_width=True)
            if st.button(f"تصفح الترم {'الأول' if t=='t1' else 'الثاني'}", key=t):
                st.session_state.term, st.session_state.page = t, 'search'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث والنتائج المعدلة ---
elif st.session_state.page == 'search':
    st.markdown(f"<h2 style='text-align:center;'>🔍 محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    query = st.text_input("ادخل الكلمة (English):")
    
    if query:
        st.markdown(f"### 🔊 نطق الكلمة: {query}")
        q_audio = speak(query)
        if q_audio: st.audio(q_audio)
        
        pdf_file = f"{st.session_state.grade_id}_{st.session_state.term}.pdf"
        with st.spinner('بطلنا يحلل كتاب المدرسة...'):
            sentences, pages = advanced_search(pdf_file, query)
            
            if sentences:
                st.markdown("<h3 class='section-title'>📝 جمل من المنهج</h3>", unsafe_allow_html=True)
                for s in sentences:
                    st.markdown(f"""
                    <div class="sentence-card">
                        <p class="sentence-text">{s['display']}</p>
                        <p class="page-info">ذكرت في صفحة: {s['page']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # زر النطق مع النص المطلوب
                    st.write("🔊 استمع للجملة:")
                    s_audio = speak(s['raw'])
                    if s_audio: st.audio(s_audio)
                
                st.markdown("<h3 class='section-title'>📖 صفحات الكتاب كاملة</h3>", unsafe_allow_html=True)
                for p in pages:
                    st.markdown(f"**الصفحة رقم: {p['num']}**")
                    st.image(p['image'], use_container_width=True)
            else:
                st.warning("لم نجد نتائج دقيقة للكلمة المطلوبة.")

    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- Footer ---
st.markdown("---")
f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
with f_col2:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    p_img = get_base64('personal_photo.jpg')
    if p_img: st.markdown(f'<img src="data:image/jpeg;base64,{p_img}" style="width:100px; border-radius:50%; border:3px solid #ef4444;">', unsafe_allow_html=True)
    st.markdown("### Created by Mr. Walid")
    st.markdown("[![Facebook](https://img.shields.io/badge/Facebook-Follow%20Us-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/your-page-link)")
    st.markdown("</div>", unsafe_allow_html=True)
