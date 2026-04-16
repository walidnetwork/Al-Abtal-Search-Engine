import streamlit as st
import time
import base64

# --- إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="Alabtal AI Dictionary", layout="centered", initial_sidebar_state="collapsed")

# --- دالة تحويل الموارد لعملها برمجياً (Base64) ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# --- تحسين الواجهة بـ CSS لكسر البهتان ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #ef4444, #b91c1c);
        color: white;
        font-weight: bold;
        border: none;
        height: 45px;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0px 5px 15px rgba(239, 68, 68, 0.5);
    }
    img {
        border-radius: 15px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# إدارة حالة التطبيق (Stages)
if 'stage' not in st.session_state:
    st.session_state.stage = 'splash'

# --- 1. شاشة الترحيب (Splash Screen) ---
if st.session_state.stage == 'splash':
    placeholder = st.empty()
    with placeholder.container():
        logo_b64 = get_base64('logo_animated.gif')
        audio_b64 = get_base64('start_theme.wav')
        
        st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; height: 70vh; flex-direction: column; text-align: center;">
                <img src="data:image/gif;base64,{logo_b64}" width="250">
                <audio autoplay><source src="data:audio/wav;base64,{audio_b64}" type="audio/wav"></audio>
                <h2 style="font-family: Cairo; margin-top: 25px; color: #f8fafc;">مرحباً بك يا بطل في عالم الأبطال</h2>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(4) # وقت عرض اللوجو
    st.session_state.stage = 'select_grade'
    st.rerun()

# --- 2. واجهة اختيار الصف الدراسي ---
elif st.session_state.stage == 'select_grade':
    st.markdown("<h1 style='text-align: center;'>🦸‍♂️ اختر صفك الدراسي</h1>", unsafe_allow_html=True)
    
    # توزيع الصفوف في شبكة (Grid)
    col1, col2, col3 = st.columns(3)
    grades = [("G1", "cover_g1.jpg"), ("G2", "cover_g2.jpg"), ("G3", "cover_g3.jpg"), 
              ("G4", "cover_g4.jpg"), ("G5", "cover_g5.jpg"), ("G6", "cover_g6.jpg")]
    
    for i, (g_name, g_img) in enumerate(grades):
        with [col1, col2, col3][i % 3]:
            st.image(g_img, use_container_width=True)
            if st.button(f"الصف {g_name[-1]}", key=f"btn_{g_name}"):
                st.session_state.grade = g_name
                st.session_state.stage = 'select_term'
                st.rerun()

# --- 3. واجهة اختيار الترم الدراسي ---
elif st.session_state.stage == 'select_term':
    st.markdown(f"<h1 style='text-align: center;'>📚 {st.session_state.grade} - اختر الترم</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(f"cover_{st.session_state.grade.lower()}_t1.jpg")
        if st.button("الترم الأول", key="t1"):
            st.session_state.term = "T1"
            st.session_state.stage = 'search_mode'
            st.rerun()
    with col2:
        # ملاحظة: الترم الثاني بصيغة PNG حسب ملفاتك المرفوعة
        st.image(f"cover_{st.session_state.grade.lower()}_t2.png")
        if st.button("الترم الثاني", key="t2"):
            st.session_state.term = "T2"
            st.session_state.stage = 'search_mode'
            st.rerun()

# --- 4. واجهة البحث النهائية ---
elif st.session_state.stage == 'search_mode':
    # عرض غلاف الترم في الأعلى
    current_cover = f"cover_{st.session_state.grade.lower()}_t1.jpg" if st.session_state.term == "T1" else f"cover_{st.session_state.grade.lower()}_t2.png"
    
    st.markdown(f"<div style='text-align: center;'><img src='data:image/png;base64,{get_base64(current_cover)}' width='120'></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>منهج {st.session_state.grade} - {st.session_state.term}</p>", unsafe_allow_html=True)
    
    st.title("🔍 ابحث عن الكلمة")
    
    # محرك البحث (يربط بملف الـ PDF المخصص لهذا الصف والترم)
    query = st.text_input("اكتب الكلمة بالإنجليزية (مثلاً: Apple):")
    
    if query:
        st.success(f"جاري البحث عن '{query}' في قاموس الأبطال...")
        # هنا سنضيف منطق البحث عن الكلمة في الـ PDF لاحقاً
        
    if st.button("🔙 العودة لاختيار الصفوف"):
        st.session_state.stage = 'select_grade'
        st.rerun()
