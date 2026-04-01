import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_teacher_dict, import_students_from_csv, get_students_by_advisor

st.set_page_config(page_title="Teacher Panel", layout="wide")

if not st.session_state.get('logged_in') or st.session_state.get('role') != 'teacher':
    st.switch_page("app.py")

# ==========================================
# 🌟 CSS Theme (ฟอนต์ Kanit + Blue Wave & Mint Green)
# ==========================================
st.markdown("""
    <style>
    /* 1. นำเข้าฟอนต์ Kanit และ ฟอนต์ไอคอน Material กลับมาให้ชัวร์ */
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
    
    /* 2. บังคับฟอนต์ Kanit เฉพาะตัวหนังสือหลักๆ (ลดการเหวี่ยงแหที่ทำให้ไอคอนพัง) */
    html, body, h1, h2, h3, h4, h5, h6, p, label, button, input, div[data-testid="stMarkdownContainer"] {
        font-family: 'Kanit', sans-serif !important;
    }

    /* 3. 🌟 คืนค่าฟอนต์สัญลักษณ์ให้กับไอคอนส่วนหัวและปุ่มย่อขยายเมนู !important */
    .material-symbols-rounded, 
    .material-icons, 
    [data-testid="stSidebarCollapseButton"] *, 
    [data-testid="collapsedControl"] *, 
    [data-testid="stHeader"] * {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* 4. ซ่อนเมนูดั้งเดิมของ Streamlit (เฉพาะเมนู Nav) */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* 5. จัดการสีพื้นหลังและ Sidebar */
    .stApp { background-color: #F4F7FC; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4FACFE 0%, #3B82F6 100%);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] strong {
        color: #FFFFFF !important;
    }
    
    /* 6. จัดการรูปภาพโลโก้ */
    [data-testid="stSidebar"] img {
        max-width: 150px !important; 
        margin: 0 auto; 
        display: block;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    
    /* 7. ตกแต่งกล่องข้อความและปุ่ม */
    div.stTextInput > div > div > input,
    div.stNumberInput > div > div > input,
    div.stTextArea > div > div > textarea,
    div.stSelectbox > div > div > div {
        background-color: #E8F6F0 !important; 
        border-radius: 15px !important;
        border: 1px solid #D1EAE0 !important;
    }
    
    button[kind="primary"] {
        background: linear-gradient(90deg, #3B82F6 0%, #4FACFE 100%) !important;
        border-radius: 30px !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🌟 Sidebar Menu
# ==========================================
with st.sidebar:
    try:
        st.image("new-logo-apdi.png", use_container_width=False, width=160)
    except:
        st.warning("หารูปโลโก้ไม่พบ")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    role_th = "อาจารย์" if st.session_state.get('role') == 'teacher' else "นักศึกษา"
    st.markdown(f"### {st.session_state.get('user_id')}")
    st.markdown(f"**สถานะ:** {role_th}")
    st.markdown("---")
    
    st.markdown("**เมนูหลัก**")
    st.page_link("pages/2_Teacher_Panel.py", label="จัดการนักศึกษา (Teacher Panel)")
    st.page_link("pages/1_My_Profile.py", label="ดูตัวอย่างหน้าประวัติ")

    st.markdown("<br>" * 8, unsafe_allow_html=True) 
    
    if st.button("ออกจากระบบ", type="primary", use_container_width=True, key="logout_btn_teacher"):
        st.session_state.clear()
        try:
            st.switch_page("app.py")
        except:
            st.rerun()

# ==========================================
# ส่วนหน้าจอหลัก
# ==========================================
st.title("ระบบจัดการนักศึกษา (Teacher Panel)")

tab_import, tab_manage = st.tabs(["นำเข้ารายชื่อนักศึกษา (CSV)", "รายชื่อในการดูแล"])

with tab_import:
    st.subheader("ระบบนำเข้ารายชื่อนักศึกษาใหม่")
    st.markdown("#### 1. เลือกอาจารย์ที่ปรึกษาสำหรับนักศึกษากลุ่มนี้")
    teacher_options = get_teacher_dict()
    
    if not teacher_options:
        st.error("ไม่พบข้อมูลอาจารย์ในระบบ กรุณาติดต่อผู้ดูแลระบบ")
    else:
        teacher_names = list(teacher_options.values())
        selected_teacher_name = st.selectbox("ระบบจะผูกรายชื่อทั้งหมดที่จะอัปโหลด เข้ากับอาจารย์ท่านนี้:", options=teacher_names)
        selected_teacher_id = [k for k, v in teacher_options.items() if v == selected_teacher_name][0]

        st.markdown("#### 2. อัปโหลดไฟล์ CSV รายชื่อนักศึกษา")
        st.markdown("ไฟล์ต้องมีคอลัมน์ชื่อ **'รหัสประจำตัว'** และ **'ชื่อ-นามสกุล'**")
        
        uploaded_file = st.file_uploader("เลือกไฟล์ CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success("อ่านไฟล์สำเร็จ! ตัวอย่างข้อมูลที่จะนำเข้า:")
                st.dataframe(df.head()) 
                
                st.markdown("#### 3. ยืนยันการนำเข้าข้อมูล")
                if st.button("นำเข้าข้อมูลและผูกกับอาจารย์ที่เลือก", type="primary", use_container_width=True, key="import_btn"):
                    added_count = import_students_from_csv(df, selected_teacher_id)
                    if added_count > 0:
                        st.success(f"สำเร็จ! นำเข้ารายชื่อใหม่ทั้งหมด {added_count} คน และผูกกับ '{selected_teacher_name}' เรียบร้อยแล้ว!")
                    else:
                        st.warning("นำเข้า 0 คน (ข้อมูลรายชื่อเหล่านี้น่าจะมีอยู่ในระบบฐานข้อมูลแล้วครับ)")
                    
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")

with tab_manage:
    st.subheader(f"รายชื่อนักศึกษาในความดูแลของคุณ")
    current_teacher_id = st.session_state.get('user_id')
    df_advisees = get_students_by_advisor(current_teacher_id)
    
    if df_advisees.empty:
        st.info("ยังไม่มีรายชื่อนักศึกษาในความดูแลของคุณครับ (กรุณาใช้แท็บนำเข้ารายชื่อก่อน)")
    else:
        st.success(f"พบรายชื่อนักศึกษาในการดูแลทั้งหมด {len(df_advisees)} คน")
        st.dataframe(df_advisees, use_container_width=True, hide_index=True)
        
        csv = df_advisees.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="ดาวน์โหลดรายชื่อนักศึกษา (CSV)",
            data=csv,
            file_name=f"advisees_{current_teacher_id}.csv",
            mime="text/csv",
            key="download_csv_btn"
        )

        st.markdown("---")
        st.subheader("ค้นหาและเปิดดูประวัตินักศึกษา")
        
        student_choices = df_advisees['รหัสประจำตัว'].astype(str) + " : " + df_advisees['ชื่อ-นามสกุล']
        
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_student = st.selectbox("ค้นหารายชื่อนักศึกษา:", options=student_choices, label_visibility="collapsed", key="search_std_dd")
        with col_btn:
            if st.button("เปิดดูประวัติ", type="primary", use_container_width=True, key="view_profile_btn"):
                target_id = selected_student.split(" : ")[0].strip()
                st.session_state['view_student_id'] = target_id
                st.switch_page("pages/1_My_Profile.py")