import streamlit as st
import base64
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Alabtal AI Dictionary", layout="wide")

# --- 2. دالة جلب الصور بأمان ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except: return ""
    return ""

# --- 3. تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #1e3a8a, #0f172a);
        color: white;
    }
    label { color: #f1f5f9 !important; font-weight: bold !important; font-family: 'Cairo', sans-serif; }
    .stTextInput input { background-color: rgba(255, 255, 255, 0.9) !important; color: #000 !important; border-radius: 10px !important; }
    .main-header { text-align: center; padding: 10px; }
    .logo-img { width: 180px; margin-bottom: 10px; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: #ef4444;
        color: white;
        font-weight: bold;
        height: 50px;
        border: none;
        font-size: 1.1rem;
    }
    .cover-box { text-align: center; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. نظام التنقل ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- الصفحة الرئيسية (اختيار الصف) ---
if st.session_state.page == 'home':
    logo_data = get_base64('logo_animated.gif')
    if logo_data:
        st.markdown(f'<div class="main-header"><img src="data:image/gif;base64,{logo_data}" class="logo-img"></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; font-family: Cairo;'>قاموس الأبطال للغة الإنجليزية</h1>", unsafe_allow_html=True)
    
    grades = [
        ("Grade 1", "cover_g1.jpg"), ("Grade 2", "cover_g2.jpg"), ("Grade 3", "cover_g3.jpg"),
        ("Grade 4", "cover_g4.jpg"), ("Grade 5", "cover_g5.jpg"), ("Grade 6", "cover_g6.jpg")
    ]

    row1 = st.columns(3)
    row2 = st.columns(3)
    all_columns = row1 + row2

    for i, (name, img_path) in enumerate(grades):
        with all_columns[i]:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            if st.button(f"دخول {name}", key=name):
                st.session_state.grade = name.replace(" ", "").lower() # تصبح g1, g2...
                st.session_state.page = 'select_term'
                st.rerun()

# --- صفحة اختيار الترم (المحدثة لإظهار الأغلفة) ---
elif st.session_state.page == 'select_term':
    st.markdown(f"<h2 style='text-align:center; font-family: Cairo;'>📚 اختر الترم الدراسي - {st.session_state.grade.upper()}</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # مصفوفة بأسماء الملفات المحتملة للترمين
    # الكود سيبحث عن cover_g1_t1.jpg أو cover_g1_t1.png وهكذا
    grade_code = st.session_state.grade # مثل g1
    
    with col1:
        st.markdown('<div class="cover-box">', unsafe_allow_html=True)
        t1_filename = f"cover_{grade_code}_t1.jpg"
        if not os.path.exists(t1_filename): t1_filename = f"cover_{grade_code}_t1.png" # تجربة png إذا لم يجد jpg
        
        if os.path.exists(t1_filename):
            st.image(t1_filename, caption="غلاف الترم الأول", use_container_width=True)
        else:
            st.warning(f"غلاف الترم الأول ({t1_filename}) غير موجود")
        
        if st.button("تصفح كلمات الترم الأول", key="btn_t1"):
            st.session_state.term, st.session_state.page = "t1", "search"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="cover-box">', unsafe_allow_html=True)
        t2_filename = f"cover_{grade_code}_t2.jpg"
        if not os.path.exists(t2_filename): t2_filename = f"cover_{grade_code}_t2.png"
        
        if os.path.exists(t2_filename):
            st.image(t2_filename, caption="غلاف الترم الثاني", use_container_width=True)
        else:
            st.warning(f"غلاف الترم الثاني ({t2_filename}) غير موجود")
            
        if st.button("تصفح كلمات الترم الثاني", key="btn_t2"):
            st.session_state.term, st.session_state.page = "t2", "search"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 العودة لاختيار الصفوف"):
        st.session_state.page = 'home'
        st.rerun()

# --- صفحة البحث ---
elif st.session_state.page == 'search':
    st.markdown(f"<h2 style='text-align:center;'>🔍 محرك بحث {st.session_state.grade.upper()} - {st.session_state.term.upper()}</h2>", unsafe_allow_html=True)
    query = st.text_input("أدخل الكلمة الإنجليزية التي تبحث عنها:")
    if st.button("🔙 تغيير الترم أو الصف"):
        st.session_state.page = 'home'
        st.rerun()
