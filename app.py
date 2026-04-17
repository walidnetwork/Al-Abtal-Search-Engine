import streamlit as st
import base64
import os
import fitz  # PyMuPDF
from gtts import gTTS
import io
import re

# --- 1. إعدادات الصفحة والهوية (المسؤول عن الأيقونة عند التنزيل) ---
st.set_page_config(
    page_title="ALABTAL DICTIONARY",
    page_icon="logo_animated.gif",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# هذا الكود الإضافي هو الذي سيحذف كلمة Streamlit من العنوان نهائياً
st.markdown("""
    <script>
        var elements = window.parent.document.querySelectorAll('title');
        if (elements.length > 0) {
            elements[0].innerText = "ALABTAL DICTIONARY";
        }
    </script>
    """, unsafe_allow_html=True)

# --- 2. دالة النطق الصافية (تتجاهل الرموز) ---
def speak(text):
    try:
        clean_text = re.sub(r'[^a-zA-Z0-9\s,.\'!?]', '', text)
        tts = gTTS(text=clean_text, lang='en')
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

# --- 4. المحرك الذكي المطور (استخلاص جمل دقيقة + صفحات كاملة) ---
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
                    clean_line = re.sub(r'[^a-zA-Z0-9\s,.\'!?]', '', line).strip()
                    if word_pattern.search(clean_line) and len(clean_line) > len(word):
                        display_text = re.sub(word_pattern, f"<b style='color:#ef4444;'>{word}</b>", clean_line)
                        if clean_line not in [s['raw'] for s in extracted_sentences]:
                            extracted_sentences.append({
                                "display": display_text, 
                                "raw": clean_line,
                                "page": page_num + 1
                            })
                if page_num not in found_pages_indices:
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                    found_pages_indices.append(page_num)
            if len(full_pages) >= 5: break
        return extracted_sentences, full_pages
    except: return [], []

# --- 5. هندسة الواجهة (CSS) مع دعم إخفاء هوية Streamlit ---
st.markdown("""
    <style>
    /* إخفاء هوية المنصة لإظهار التطبيق بشكل احترافي */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    .main-title { text-align: center; font-family: 'Cairo'; font-size: 3rem; margin-bottom: 0; }
    label { color: white !important; font-weight: bold !important; font-family: 'Cairo'; font-size: 1.2rem !important; }
    .stTextInput input { background-color: white !important; color: black !important; font-weight: bold; border-radius: 12px; height: 50px; }
    .sentence-card { 
        background: white; color: #0f172a; padding: 25px; border-radius: 15px; 
        margin-bottom: 10px; border-right: 10px solid #ef4444; box-shadow: 0px 6px 15px rgba(0,0,0,0.3);
    }
    .stButton>button { width: 100%; border-radius: 12px; background: #ef4444; color: white; font-weight: bold; height: 50px; border: none; font-size: 1.1rem; }
    .section-header { border-bottom: 3px solid #ef4444; padding-bottom: 5px; margin-top: 40px; font-family: 'Cairo'; }
    .bio-text { font-style: italic; color: #cbd5e1; font-size: 1rem; margin-top: 5px; line-height: 1.6; }
    </style>
    <script>
    function installApp() {
        alert("لبطل الأبطال: اضغط على 'الثلاث نقاط' في أعلى المتصفح (أو علامة المشاركة في الآيفون) ثم اختر 'Install' أو 'Add to Home Screen' ليظهر القاموس بجانب ألعابك وتطبيقاتك!");
    }
    </script>

    <div class="install-btn" onclick="installApp()" style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        background-color: #ef4444;
        color: white !important;
        padding: 12px 20px;
        border-radius: 50px;
        font-weight: bold;
        font-family: 'Cairo';
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        cursor: pointer;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 8px;
        border: 2px solid white;
    ">
        📲 تثبيت القاموس على موبايلك
    </div>
    
    <link rel="apple-touch-icon" href="logo_animated.gif">
    """, unsafe_allow_html=True)

# --- 6. نظام التنقل ---
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    logo_b64 = get_base64('logo_animated.gif')
    if logo_b64: st.markdown(f'<center><img src="data:image/gif;base64,{logo_b64}" width="220"></center>', unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>قاموس الأبطال</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:1.2rem;'>ALABTAL DICTIONARY</p>", unsafe_allow_html=True)
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
    if st.button("🔙 عودة للقائمة الرئيسية"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث والنتائج ---
elif st.session_state.page == 'search':
    st.markdown("<h2 style='text-align:center; font-family: Cairo;'>🔍 محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    query = st.text_input("ادخل الكلمة (English):", placeholder="ابحث هنا...")
    if query:
        st.markdown(f"### 🔊 نطق الكلمة: {query}")
        q_audio = speak(query)
        if q_audio: st.audio(q_audio)
        pdf_path = f"{st.session_state.grade_id}_{st.session_state.term}.pdf"
        
        # استخدام Spinner مخصص باسم السلسلة
        with st.spinner('ALABTAL DICTIONARY... جاري البحث'):
            sentences, pages = advanced_search(pdf_path, query)
            if sentences:
                st.markdown("<h3 class='section-header'>📝 جمل من المنهج</h3>", unsafe_allow_html=True)
                for s in sentences:
                    st.markdown(f"""
                    <div class="sentence-card">
                        <p style="font-size: 1.5rem; font-weight: bold;">{s['display']}</p>
                        <p style="color: #64748b; font-size: 0.8rem;">Page: {s['page']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("🔊 استمع للجملة:")
                    s_audio = speak(s['raw'])
                    if s_audio: st.audio(s_audio)
                st.markdown("<h3 class='section-header'>📖 صفحات الكتاب كاملة</h3>", unsafe_allow_html=True)
                for p in pages:
                    st.info(f"الصفحة رقم: {p['num']}")
                    st.image(p['image'], use_container_width=True)
            else: st.warning("لم نجد نتائج.")
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- 7. التذييل (Footer) ومعلومات المبدع ---
st.markdown("<br><br>", unsafe_allow_html=True)
f_c1, f_c2, f_c3 = st.columns([1, 2, 1])
with f_c2:
    st.markdown("<div style='text-align:center; border-top: 1px solid rgba(255,255,255,0.1); padding: 20px;'>", unsafe_allow_html=True)
    p_img = get_base64('personal_photo.jpg')
    if p_img: st.markdown(f'<img src="data:image/jpeg;base64,{p_img}" style="width:110px; border-radius:50%; border:3px solid #ef4444;">', unsafe_allow_html=True)
    st.markdown("### Created by Mr. Walid")
    st.markdown("<p class='bio-text'>مؤلف سلسلة كتب الأبطال ومدرس لغة إنجليزية متخصص في تأليف وتطوير المحتوى التعليمي.</p>", unsafe_allow_html=True)
    st.markdown("<h4>سلسلة كتب الأبطال</h4>", unsafe_allow_html=True)
    st.markdown("[![Facebook](https://img.shields.io/badge/Facebook-Follow%20Our%20Series-blue?style=for-the-badge&logo=facebook)](https://www.facebook.com/Alabtalbooks)") 
    st.markdown("</div>", unsafe_allow_html=True)
