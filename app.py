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
    .stApp { background: linear-gradient(to bottom, #1e3a8a, #0f172a); color: white; }
    label { color: #f1f5f9 !important; font-weight: bold !important; font-family: 'Cairo', sans-serif; font-size: 1.2rem !important; }
    .stTextInput input { 
        background-color: white !important; 
        color: black !important; 
        border-radius: 10px !important; 
        height: 45px !important;
        font-weight: bold !important;
    }
    .main-header { text-align: center; padding: 10px; }
    .logo-img { width: 180px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 10px; background: #ef4444; color: white; font-weight: bold; height: 50px; border: none; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- الصفحة الرئيسية (بترتيب إجباري 1-6) ---
if st.session_state.page == 'home':
    logo_data = get_base64('logo_animated.gif')
    if logo_data:
        st.markdown(f'<div class="main-header"><img src="data:image/gif;base64,{logo_data}" class="logo-img"></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; font-family: Cairo;'>قاموس الأبطال للغة الإنجليزية</h1>", unsafe_allow_html=True)

    # الترتيب اليدوي لضمان عدم اللخبطة
    # السطر الأول: الصفوف 1، 2، 3
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if os.path.exists("cover_g1.jpg"): st.image("cover_g1.jpg", use_container_width=True)
        if st.button("دخول الصف الأول", key="g1"):
            st.session_state.grade_id, st.session_state.page = "g1", "select_term"; st.rerun()

    with col2:
        if os.path.exists("cover_g2.jpg"): st.image("cover_g2.jpg", use_container_width=True)
        if st.button("دخول الصف الثاني", key="g2"):
            st.session_state.grade_id, st.session_state.page = "g2", "select_term"; st.rerun()

    with col3:
        if os.path.exists("cover_g3.jpg"): st.image("cover_g3.jpg", use_container_width=True)
        if st.button("دخول الصف الثالث", key="g3"):
            st.session_state.grade_id, st.session_state.page = "g3", "select_term"; st.rerun()

    # السطر الثاني: الصفوف 4، 5، 6
    col4, col5, col6 = st.columns(3)

    with col4:
        if os.path.exists("cover_g4.jpg"): st.image("cover_g4.jpg", use_container_width=True)
        if st.button("دخول الصف الرابع", key="g4"):
            st.session_state.grade_id, st.session_state.page = "g4", "select_term"; st.rerun()

    with col5:
        if os.path.exists("cover_g5.jpg"): st.image("cover_g5.jpg", use_container_width=True)
        if st.button("دخول الصف الخامس", key="g5"):
            st.session_state.grade_id, st.session_state.page = "g5", "select_term"; st.rerun()

    with col6:
        if os.path.exists("cover_g6.jpg"): st.image("cover_g6.jpg", use_container_width=True)
        if st.button("دخول الصف السادس", key="g6"):
            st.session_state.grade_id, st.session_state.page = "g6", "select_term"; st.rerun()

# --- صفحة اختيار الترم ---
elif st.session_state.page == 'select_term':
    st.markdown("<h1 style='text-align:center; font-family: Cairo;'>📚 اختر الترم الدراسي</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    gid = st.session_state.grade_id
    
    with col1:
        t1 = f"cover_{gid}_t1.jpg"
        if os.path.exists(t1): st.image(t1, caption="الترم الأول", use_container_width=True)
        if st.button("تصفح الترم الأول"):
            st.session_state.term, st.session_state.page = "الترم الأول", "search"; st.rerun()

    with col2:
        t2 = f"cover_{gid}_t2.jpg"
        if os.path.exists(t2): st.image(t2, caption="الترم الثاني", use_container_width=True)
        if st.button("تصفح الترم الثاني"):
            st.session_state.term, st.session_state.page = "الترم الثاني", "search"; st.rerun()
    
    if st.button("🔙 العودة لاختيار الصف"):
        st.session_state.page = 'home'; st.rerun()

# --- صفحة البحث ---
elif st.session_state.page == 'search':
    st.markdown("<h2 style='text-align:center; font-family: Cairo;'>🔍 محرك بحث الأبطال</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>الصف: {st.session_state.grade_id.upper()} | {st.session_state.term}</p>", unsafe_allow_html=True)
    user_query = st.text_input("أدخل الكلمة الإنجليزية التي تبحث عنها هنا:")
    if st.button("🔙 العودة للرئيسية"):
        st.session_state.page = 'home'; st.rerun()
