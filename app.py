import streamlit as st
import base64
import os

# --- 1. إعدادات الصفحة (يجب أن تكون أول سطر في الكود) ---
st.set_page_config(page_title="Alabtal AI Dictionary", layout="wide")

# --- 2. دالة جلب الصور بأمان (تمنع توقف السكريبت) ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except:
            return ""
    return ""

# --- 3. تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #1e3a8a, #0f172a);
        color: white;
    }
    .main-header { text-align: center; padding: 10px; }
    .logo-img { width: 180px; margin-bottom: 10px; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: #ef4444;
        color: white;
        font-weight: bold;
        height: 45px;
        border: none;
    }
    /* إخفاء القوائم الجانبية لتجنب التشتت */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. نظام التنقل (Session State) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    # عرض اللوجو
    logo_data = get_base64('logo_animated.gif')
    if logo_data:
        st.markdown(f'<div class="main-header"><img src="data:image/gif;base64,{logo_data}" class="logo-img"></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center;'>قاموس الأبطال للغة الإنجليزية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>اختر صفك الدراسي لتبدأ</p>", unsafe_allow_html=True)

    # شبكة الصفوف
    col1, col2, col3 = st.columns(3)
    grades = [
        ("Grade 1", "cover_g1.jpg"), ("Grade 2", "cover_g2.jpg"), ("Grade 3", "cover_g3.jpg"),
        ("Grade 4", "cover_g4.jpg"), ("Grade 5", "cover_g5.jpg"), ("Grade 6", "cover_g6.jpg")
    ]

    for i, (name, img_path) in enumerate(grades):
        with [col1, col2, col3][i % 3]:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.info(f"كتاب {name}") # بديل في حال عدم وجود الصورة
            
            if st.button(f"دخول {name}", key=name):
                st.session_state.grade = name.replace(" ", "").lower()
                st.session_state.page = 'select_term'
                st.rerun()

# --- صفحة اختيار الترم ---
elif st.session_state.page == 'select_term':
    st.markdown(f"<h2 style='text-align:center;'>📚 منهج {st.session_state.grade.upper()}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    # الترم الأول
    with c1:
        t1_img = f"cover_{st.session_state.grade}_t1.jpg"
        if os.path.exists(t1_img): st.image(t1_img, use_container_width=True)
        if st.button("الترم الأول", key="t1"):
            st.session_state.term, st.session_state.page = "t1", "search"
            st.rerun()

    # الترم الثاني
    with c2:
        t2_img = f"cover_{st.session_state.grade}_t2.png"
        if os.path.exists(t2_img): st.image(t2_img, use_container_width=True)
        if st.button("الترم الثاني", key="t2"):
            st.session_state.term, st.session_state.page = "t2", "search"
            st.rerun()
    
    st.write("---")
    if st.button("🔙 العودة للرئيسية"):
        st.session_state.page = 'home'
        st.rerun()

# --- صفحة البحث ---
elif st.session_state.page == 'search':
    st.markdown(f"<h3 style='text-align:center;'>🔍 محرك بحث {st.session_state.grade.upper()} - {st.session_state.term.upper()}</h3>", unsafe_allow_html=True)
    
    query = st.text_input("اكتب الكلمة بالإنجليزية:")
    if query:
        st.write(f"جاري البحث عن: {query}")
        
    if st.button("🔙 تغيير الصف"):
        st.session_state.page = 'home'
        st.rerun()
