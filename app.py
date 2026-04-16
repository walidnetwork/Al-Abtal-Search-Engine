import streamlit as st
import base64
import os
import fitz  # PyMuPDF للبحث داخل الـ PDF

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Alabtal AI Dictionary", layout="wide")

# --- 2. دالة جلب الصور ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except: return ""
    return ""

# --- 3. دالة البحث الذكي داخل الـ PDF ---
def search_in_pdf(pdf_path, word):
    results = []
    if not os.path.exists(pdf_path):
        return None
    
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.search_for(word)
        
        # إذا وجدت الكلمة، نأخذ لقطة للمنطقة المحيطة بها
        for inst in text_instances:
            # تكبير منطقة القص قليلاً لتشمل الصورة والترجمة
            clip = fitz.Rect(inst.x0 - 100, inst.y0 - 50, inst.x1 + 400, inst.y1 + 300)
            pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            results.append(img_data)
            if len(results) >= 3: break # اكتفي بأول 3 نتائج للسرعة
    return results

# --- 4. تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    label { color: white !important; font-weight: bold !important; font-family: 'Cairo'; }
    .stTextInput input { background-color: white !important; color: black !important; border-radius: 10px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 10px; background: #ef4444; color: white; font-weight: bold; height: 50px; border: none; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    logo_data = get_base64('logo_animated.gif')
    if logo_data:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/gif;base64,{logo_data}" width="180"></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; font-family: Cairo;'>قاموس الأبطال للغة الإنجليزية</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    grades = [("g1", "الصف الأول"), ("g2", "الصف الثاني"), ("g3", "الصف الثالث")]
    for i, (gid, name) in enumerate(grades):
        with [col1, col2, col3][i]:
            img = f"cover_{gid}.jpg"
            if os.path.exists(img): st.image(img, use_container_width=True)
            if st.button(f"دخول {name}", key=gid):
                st.session_state.grade_id, st.session_state.page = gid, 'select_term'; st.rerun()

    col4, col5, col6 = st.columns(3)
    grades2 = [("g4", "الصف الرابع"), ("g5", "الصف الخامس"), ("g6", "الصف السادس")]
    for i, (gid, name) in enumerate(grades2):
        with [col4, col5, col6][i]:
            img = f"cover_{gid}.jpg"
            if os.path.exists(img): st.image(img, use_container_width=True)
            if st.button(f"دخول {name}", key=gid):
                st.session_state.grade_id, st.session_state.page = gid, 'select_term'; st.rerun()

# --- صفحة اختيار الترم ---
elif st.session_state.page == 'select_term':
    st.markdown("<h1 style='text-align:center; font-family: Cairo;'>📚 اختر الترم الدراسي</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    gid = st.session_state.grade_id
    
    with col1:
        t1 = f"cover_{gid}_t1.jpg"
        if os.path.exists(t1): st.image(t1, use_container_width=True)
        if st.button("الترم الأول"):
            st.session_state.term, st.session_state.page = "t1", "search"; st.rerun()

    with col2:
        t2 = f"cover_{gid}_t2.jpg"
        if os.path.exists(t2): st.image(t2, use_container_width=True)
        if st.button("الترم الثاني"):
            st.session_state.term, st.session_state.page = "t2", "search"; st.rerun()
    
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث والنتائج ---
elif st.session_state.page == 'search':
    st.markdown("<h2 style='text-align:center;'>🔍 محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    pdf_to_search = f"{st.session_state.grade_id}_{st.session_state.term}.pdf"
    
    query = st.text_input("ادخل الكلمة (English):")
    
    if query:
        with st.spinner('بطلنا يبحث لك الآن...'):
            results = search_in_pdf(pdf_to_search, query)
            
            if results:
                st.success(f"وجدنا {len(results)} نتيجة لـ '{query}'")
                for img_bytes in results:
                    st.image(img_bytes)
            elif results is None:
                st.error(f"ملف المنهج ({pdf_to_search}) غير موجود في السيرفر.")
            else:
                st.warning("لم نجد هذه الكلمة، تأكد من كتابتها بشكل صحيح.")

    if st.button("🔙 عودة للرئيسية"): st.session_state.page = 'home'; st.rerun()
