import streamlit as st
import base64
from gtts import gTTS
import io
import os
import fitz  # PyMuPDF
import re

# --- 1. إعدادات الصفحة والتصميم الجذاب للأطفال ---
st.set_page_config(page_title="Heroes Dictionary", page_icon="🦸‍♂️", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stappviewcontainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
        background-color: #0f172a;
        color: white;
    }
    
    /* تصميم الأزرار الجذاب */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(135deg, #ef4444, #b91c1c);
        color: white;
        font-weight: bold;
        font-size: 1.3rem;
        height: 3.5em;
        border: 2px solid #f87171;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        transition: 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05) translateY(-5px);
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.6);
        background: #ef4444;
    }
    
    /* تنسيق الجمل المستخرجة */
    .sentence-box {
        background: #1e293b;
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 15px;
        border-right: 8px solid #ef4444;
        font-size: 1.4rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .word-highlight {
        color: #ef4444;
        font-weight: bold;
        text-decoration: underline;
    }
    
    /* تنسيق الأغلفة */
    .cover-img {
        border-radius: 20px;
        border: 4px solid #334155;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. دالات المساعدة الذكية ---

def get_base64(bin_file):
    """تحويل الصور إلى base64 لعرضها بوضوح"""
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def speak_clean(text):
    """نطق الجملة بعد تنظيفها تماماً من الرموز (النجوم، الماسات، إلخ)"""
    # حذف أي شيء ليس حرفاً أو رقماً أو علامات ترقيم أساسية
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?\']', '', text)
    tts = gTTS(text=clean_text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

def advanced_search(pdf_path, word):
    """البحث الاحترافي داخل ملف الـ PDF"""
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
                # 1. استخراج الصفحة كصورة
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                full_pages.append({"num": page_num + 1, "image": pix.tobytes("png")})
                
                # 2. استخراج الجمل وتلوين الكلمة
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

# --- 3. إدارة التنقل بين المراحل ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'grade' not in st.session_state: st.session_state.grade = 1
if 'term' not in st.session_state: st.session_state.term = 1

# --- 4. المرحلة 1: الترحيب واللوجو ---
if st.session_state.step == 'welcome':
    st.markdown("<h1 style='text-align:center;'>🦸‍♂️ مرحباً بك يا بطل في عالم الأبطال</h1>", unsafe_allow_html=True)
    logo = get_base64('logo_animated.gif') or get_base64('logo.png')
    if logo:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{logo}" width="250"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>ALABTAL DICTIONARY</h2>", unsafe_allow_html=True)
    if st.button("🚀 هيا بنا نبدأ المغامرة"):
        st.session_state.step = 'select_grade'; st.rerun()

# --- 5. المرحلة 2: اختيار الصف الدراسي (معدلة لتظهر كل الصفوف) ---
elif st.session_state.step == 'select_grade':
    st.markdown("<h2 style='text-align:center;'>اختر صفك الدراسي يا بطل</h2>", unsafe_allow_html=True)
    
    # قائمة الصفوف الستة
    for i in range(1, 7):
        # إنشاء حاوية لكل صف عشان نفصلهم عن بعض بشكل شيك
        with st.container():
            col_img, col_btn = st.columns([1, 1.5]) # موازنة الحجم بين الصورة والزر
            
            with col_img:
                img_name = f"cover_g{i}.jpg"
                img_b64 = get_base64(img_name)
                if img_b64:
                    st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" class="cover-img" style="width:100%; max-width:200px; display:block; margin:auto;">', unsafe_allow_html=True)
                else:
                    st.info(f"صورة الصف {i}") # تنبيه لو الصورة مش موجودة على جيت هاب
            
            with col_btn:
                st.write("<br>" if not st.sidebar.checkbox("نمط الموبايل", False) else "", unsafe_allow_html=True)
                if st.button(f"دخول الصف {i} الابتدائي", key=f"grade_btn_{i}"):
                    st.session_state.grade = i
                    st.session_state.step = 'select_term'
                    st.rerun()
            
            st.markdown("<hr style='margin:10px 0; border-color:#334155;'>", unsafe_allow_html=True) # خط فاصل بسيط بين الصفوف

# --- 6. المرحلة 3: اختيار الترم ---
elif st.session_state.step == 'select_term':
    g = st.session_state.grade
    st.markdown(f"<h1 style='text-align:center;'>قاموس الأبطال - الصف {g}</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        t1_img = get_base64(f"cover_g{g}_t1.jpg")
        if t1_img: st.markdown(f'<img src="data:image/jpeg;base64,{t1_img}" class="cover-img" width="100%">', unsafe_allow_html=True)
        if st.button(f"الترم الأول - الصف {g}"):
            st.session_state.term = 1; st.session_state.step = 'search'; st.rerun()
            
    with c2:
        t2_img = get_base64(f"cover_g{g}_t2.jpg")
        if t2_img: st.markdown(f'<img src="data:image/jpeg;base64,{t2_img}" class="cover-img" width="100%">', unsafe_allow_html=True)
        if st.button(f"الترم الثاني - الصف {g}"):
            st.session_state.term = 2; st.session_state.step = 'search'; st.rerun()
    
    if st.button("🔙 عودة لاختيار الصف"):
        st.session_state.step = 'select_grade'; st.rerun()

# --- 7. المرحلة 4: محرك البحث والنتائج ---
elif st.session_state.step == 'search':
    g, t = st.session_state.grade, st.session_state.term
    st.markdown(f"<h2 style='text-align:center;'>🔍 محرك بحث الأبطال - الصف {g} - الترم {t}</h2>", unsafe_allow_html=True)
    
    # اختيار ملف الـ PDF بناءً على اختيار الطالب
    pdf_to_search = f"g{g}_t{t}.pdf"
    if not os.path.exists(pdf_to_search):
        pdf_to_search = "g1_t2.pdf" # ملف احتياطي إذا لم يتوفر الملف المحدد
    
    col_input, col_search = st.columns([4, 1])
    with col_input:
        query = st.text_input("اكتب الكلمة هنا يا بطل:", placeholder="مثلاً: Beach...").strip()
    
    if query:
        # 🔊 نطق الكلمة المبحوث عنها أولاً
        st.markdown(f"### 🔊 نطق الكلمة: {query}")
        st.audio(speak_clean(query))
        
        sentences, pages = advanced_search(pdf_to_search, query)
        
        if sentences:
            st.markdown("### 📝 جمل من كتابك")
            for i, s in enumerate(sentences[:10]):
                st.markdown(f"<div class='sentence-box'>📄 {s['display']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 استمع للجملة رقم {i+1}", key=f"audio_{i}"):
                    st.audio(speak_clean(s['raw']))
        
        if pages:
            st.markdown("### 📖 صفحات من الكتاب")
            for p in pages:
                st.image(p['image'], caption=f"صفحة رقم {p['num']}", use_container_width=True)
        
        if not sentences and not pages:
            st.warning("لم نجد هذه الكلمة في الكتاب، حاول مرة أخرى يا بطل!")

    if st.button("🔙 العودة لاختيار الترم"):
        st.session_state.step = 'select_term'; st.rerun()

# --- 8. التذييل (Footer) ---
st.write("---")
st.markdown("<div style='text-align:center; color:#94a3b8;'>Created with ❤️ by Mr. Walid Elhagary</div>", unsafe_allow_html=True)
