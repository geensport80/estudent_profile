import streamlit as st
import os

# 🌟 1. บังคับพับ Sidebar ตั้งแต่เริ่มโหลดหน้าเว็บ 
st.set_page_config(
    page_title="APDI Login", 
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# ==========================================
# 🌟 CSS Theme (ฟอนต์ Kanit + ซ่อนเมนูด้านซ้ายเด็ดขาด)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], [class*="st-"], .stApp, h1, h2, h3, h4, h5, h6, p, label, button, input {
        font-family: 'Kanit', sans-serif !important;
    }

    /* 🌟 2. โค้ดซ่อน Sidebar แบบขั้นเด็ดขาด (บังคับลบพื้นที่ออก) */
    [data-testid="stSidebar"] { 
        display: none !important; 
        min-width: 0px !important;
        max-width: 0px !important;
    }
    [data-testid="collapsedControl"] { 
        display: none !important; 
    }
    
    .stApp {
        background-color: #F4F7FC; 
    }
    
    div.stTextInput > div > div > input {
        background-color: #CDEADE !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 15px 20px !important;
        color: #2C3E50 !important;
        font-weight: 500 !important;
    }
    
    button[kind="primary"] {
        background: linear-gradient(90deg, #3B82F6 0%, #4FACFE 100%) !important;
        border-radius: 30px !important;
        border: none !important;
        padding: 12px !important;
        font-weight: 500 !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3) !important;
        margin-top: 15px !important;
    }
    
    .login-title {
        color: #3B82F6;
        text-align: center;
        font-weight: 600;
        font-size: 38px;
        margin-bottom: 5px;
    }
    .login-subtitle {
        color: #6B7280;
        text-align: center;
        font-weight: 300;
        font-size: 14px;
        margin-bottom: 30px;
    }
    
    img {
        border-radius: 15px; 
    }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col_space_l, col_img, col_form, col_space_r = st.columns([1.5, 3, 3, 1.5], gap="large")
    
    with col_img:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # ค้นหาไฟล์โลโก้ (ดักไว้ทั้งแบบ .png และ .jpg ป้องกัน Error)
        if os.path.exists("new-logo-apdi.png"):
            st.image("new-logo-apdi.png", use_container_width=True)
        elif os.path.exists("new-logo-apdi_white_small.jpg"):
            st.image("new-logo-apdi_white_small.jpg", use_container_width=True)
        else:
            st.error("หารูปโลโก้ไม่พบ")
        
    with col_form:
        st.markdown("<div class='login-title'>Welcome</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-subtitle'>Login into your account to continue</div>", unsafe_allow_html=True)
        
        username = st.text_input(" ", placeholder="Email / Username (e.g. T001)", label_visibility="collapsed")
        password = st.text_input(" ", placeholder="Password", type="password", label_visibility="collapsed")
        
        st.markdown("<p style='text-align:right; color:#6B7280; font-size:12px;'>forgot your password?</p>", unsafe_allow_html=True)
        
        if st.button("LOG IN", type="primary", use_container_width=True):
            u = username.strip().upper() 
            p = password.strip()
            
            if u == "T001" and p == "1234":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'teacher'
                st.session_state['user_id'] = u
                st.switch_page("pages/2_Teacher_Panel.py") 
                
            elif u == "686101400062" and p == "1234":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'student'
                st.session_state['user_id'] = u
                st.switch_page("pages/1_My_Profile.py") 
                
            else:
                st.error("รหัสไม่ถูกต้อง!")