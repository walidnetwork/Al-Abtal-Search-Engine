import streamlit as st
import base64
import os
import fitz  # PyMuPDF
from gtts import gTTS
import io
import re

# --- 1. إعدادات الصفحة والهوية (تظهر في تبويب المتصفح) ---
st.set_page_config(
    page_title="ALABTAL DICTIONARY",
    page_icon="logo_animated.gif", # سيظهر اللوجو الخاص بك هنا
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

# --- 4. المحرك الذكي للبحث والاستخلاص ---
def deep_search(pdf_path, word):
    results = []
    if not os.path.exists(pdf_path): return None
    try:
        doc = fitz.open(pdf_path)
        word_pattern = re.compile(re.escape(word), re.IGNORECASE)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for sentence in sentences:
                if word_pattern.search(sentence):
                    clean_s = sentence.replace('\n', ' ').strip()
                    inst = page.search_for(word)
                    img_data = None
                    if inst:
                        rect = inst[0]
                        clip = fitz.Rect(0, rect.y0 - 80, page.rect.width, rect.y1 + 120)
                        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(1.5, 1.5))
                        img_data = pix.tobytes("png")
                    results.append({"page": page_num + 1, "sentence": clean_s, "image": img_data})
                    if len(results) >= 8: break
            if len(results) >= 8: break
        return results
    except: return []

# --- 5. تصميم الواجهة الاحترافي (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    label { color: white !important; font-weight: bold !important; font-family: 'Cairo'; font-size: 1.2rem !important; }
    .stTextInput input { background-color: white !important; color: black !important; font-weight: bold; border-radius: 10px; }
    .result-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin-bottom: 25px; border-right: 6px solid #ef4444; }
    .sentence-text { font-size: 1.3rem; color: #fbbf24; font-weight: bold; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 10px; background: #ef4444; color: white; font-weight: bold; height: 50px; border: none; }
    .footer { text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); }
    .creator-img { width: 100px; border-radius: 50%; border: 3px solid #ef4444; cursor: pointer; transition: 0.3s; }
    .creator-img:hover { transform: scale(1.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 6. نظام التنقل ---
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    logo = get_base64('logo_animated.gif')
    if logo: st.markdown(f'<center><img src="data:image/gif;base64,{logo}" width="200"></center>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-family: Cairo;'>قاموس الأبطال</h1>", unsafe_allow_html=True)
    
    # توزيع الصفوف بترتيب 1-6
    for row in [["g1", "g2", "g3"], ["g4", "g5", "g6"]]:
        cols = st.columns(3)
        for i, gid in enumerate(row):
            with cols[i]:
                img = f"cover_{gid}.jpg"
                if os.path.exists(img): st.image(img, use_container_width=True)
                if st.button(f"دخول الصف {gid[1]}", key=gid):
                    st.session_state.grade_id, st.session_state.page = gid, 'select_term'; st.rerun()

# --- صفحة اختيار الترم ---
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
    if st.button("🔙 العودة للرئيسية"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث والنتائج ---
elif st.session_state.page == 'search':
    st.markdown(f"<h2 style='text-align:center;'>🔍 محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    query = st.text_input("ادخل الكلمة (English):", help="أدخل الكلمة ثم اضغط Enter")
    
    if query:
        # نطق الكلمة أولاً
        st.markdown(f"### 🔊 نطق الكلمة: {query}")
        q_audio = speak(query)
        if q_audio: st.audio(q_audio, format='audio/mp3')
        st.write("---")
        
        pdf_file = f"{st.session_state.grade_id}_{st.session_state.term}.pdf"
        with st.spinner('بطلنا يحلل محتوى المنهج...'):
            data = deep_search(pdf_file, query)
            if data:
                for item in data:
                    with st.container():
                        st.markdown(f'<div class="result-card"><p class="sentence-text">{item["sentence"]}</p><small>Page: {item["page"]}</small></div>', unsafe_allow_html=True)
                        c_img, c_aud = st.columns([3, 1])
                        with c_img: st.image(item['image'], caption="مقتطف من الكتاب")
                        with c_aud:
                            st.write("🔊 استمع للجملة")
                            s_audio = speak(item['sentence'])
                            if s_audio: st.audio(s_audio, format='audio/mp3')
            else: st.warning("لم نجد نتائج، تأكد من كتابة الكلمة بشكل صحيح.")

    if st.button("🔙 عودة لتغيير الترم"): st.session_state.page = 'home'; st.rerun()

# --- 7. التذييل (Footer) ومعلومات المبدع ---
st.markdown("---")
f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
with f_col2:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    # صورة المبدع (Created By)
    p_img = get_base64('personal_photo.jpg') # ارفع صورتك بهذا الاسم
    if p_img:
        st.markdown(f'<img src="data:image/jpeg;base64,{p_img}" class="creator-img" title="Created by Mr. Walid">', unsafe_allow_html=True)
    
    st.markdown("### Created by Mr. Walid")
    st.write("English Teacher & Educational Content Developer")
    
    # رابط الفيسبوك
    st.markdown("[![Facebook](https://img.shields.io/badge/Facebook-Follow%20Us-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/your-page-link)") # ضع رابط صفحتك هنا
    st.markdown("</div>", unsafe_allow_html=True)
