import streamlit as st
import base64
import os
import fitz  # PyMuPDF
from gtts import gTTS
import io

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Alabtal AI Dictionary", layout="wide")

# --- 2. دالة تحويل الصوت (النطق) ---
def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

# --- 3. دالة جلب الصور بأمان ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except: return ""
    return ""

# --- 4. محرك البحث والقص من الـ PDF ---
def search_and_extract(pdf_path, word):
    results = []
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.search_for(word)
        
        for inst in text_instances:
            # قص منطقة الكلمة والجملة المحيطة بها (سياق الكلمة)
            clip = fitz.Rect(inst.x0 - 50, inst.y0 - 40, inst.x1 + 500, inst.y1 + 150)
            pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            
            # محاولة استخراج الجملة المكتوبة للنطق (تبسيطاً سننطق الكلمة أو السياق المتاح)
            results.append({"image": img_data, "text": word})
            if len(results) >= 5: break 
    return results

# --- 5. تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    .stTextInput input { background-color: white !important; color: black !important; border-radius: 10px; font-weight: bold; }
    .result-card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.2); }
    .stButton>button { width: 100%; border-radius: 10px; background: #ef4444; color: white; font-weight: bold; height: 45px; border: none; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- التنقل بين الصفحات (نفس الهيكل السابق المنظم) ---
if st.session_state.page == 'home':
    # (كود الصفحة الرئيسية - عرض الصفوف 1-6 بنفس الترتيب اليدوي لضمان الدقة)
    st.markdown("<h1 style='text-align: center; font-family: Cairo;'>قاموس الأبطال للغة الإنجليزية</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for i, g in enumerate(["g1", "g2", "g3"]):
        with [col1, col2, col3][i]:
            if os.path.exists(f"cover_{g}.jpg"): st.image(f"cover_{g}.jpg", use_container_width=True)
            if st.button(f"الصف {i+1}", key=g):
                st.session_state.grade_id, st.session_state.page = g, 'select_term'; st.rerun()
    col4, col5, col6 = st.columns(3)
    for i, g in enumerate(["g4", "g5", "g6"]):
        with [col4, col5, col6][i]:
            if os.path.exists(f"cover_{g}.jpg"): st.image(f"cover_{g}.jpg", use_container_width=True)
            if st.button(f"الصف {i+4}", key=g):
                st.session_state.grade_id, st.session_state.page = g, 'select_term'; st.rerun()

elif st.session_state.page == 'select_term':
    st.markdown("<h1 style='text-align:center; font-family: Cairo;'>📚 اختر الترم الدراسي</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    gid = st.session_state.grade_id
    with col1:
        if os.path.exists(f"cover_{gid}_t1.jpg"): st.image(f"cover_{gid}_t1.jpg", use_container_width=True)
        if st.button("الترم الأول"): st.session_state.term, st.session_state.page = "t1", "search"; st.rerun()
    with col2:
        if os.path.exists(f"cover_{gid}_t2.jpg"): st.image(f"cover_{gid}_t2.jpg", use_container_width=True)
        if st.button("الترم الثاني"): st.session_state.term, st.session_state.page = "t2", "search"; st.rerun()

# --- صفحة البحث (جوهر القاموس) ---
elif st.session_state.page == 'search':
    st.markdown(f"<h2 style='text-align:center;'>🔍 قاموس {st.session_state.grade_id.upper()}</h2>", unsafe_allow_html=True)
    
    query = st.text_input("اكتب الكلمة الإنجليزية (مثلاً: Apple):")
    
    if query:
        # 1. نطق الكلمة الأساسية
        st.markdown(f"### 🔊 نطق الكلمة: {query}")
        audio_bytes = speak(query)
        st.audio(audio_bytes, format='audio/mp3')
        
        st.write("---")
        
        # 2. البحث عن مقتطفات من الكتاب
        pdf_file = f"{st.session_state.grade_id}_{st.session_state.term}.pdf"
        with st.spinner('بطلنا يبحث في صفحات الكتاب...'):
            results = search_and_extract(pdf_file, query)
            
            if results:
                st.subheader("📖 مقتطفات من المنهج:")
                for res in results:
                    with st.container():
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        col_img, col_audio = st.columns([3, 1])
                        with col_img:
                            st.image(res['image'], caption="سياق الكلمة من الكتاب")
                        with col_audio:
                            st.write("🔊 اسمع النطق")
                            st.audio(audio_bytes, format='audio/mp3') # نطق الكلمة المرتبطة بالمقتطف
                        st.markdown('</div>', unsafe_allow_html=True)
            elif results is None:
                st.error(f"عذراً، ملف المنهج {pdf_file} غير موجود.")
            else:
                st.warning("لم نجد الكلمة داخل هذا الكتاب، جرب كلمة أخرى.")

    if st.button("🔙 العودة للرئيسية"): st.session_state.page = 'home'; st.rerun()
