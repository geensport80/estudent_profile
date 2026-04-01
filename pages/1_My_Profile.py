import streamlit as st
import pandas as pd
import sys
import os
from database import save_consultation, get_consultations_by_student, get_student_name

# 🌟 เพิ่มโค้ดส่วนนี้เพื่อเชื่อมต่อและดึงฟังก์ชันมาจากไฟล์ database.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import save_consultation

# 1. ตรวจสอบสิทธิ์ (ถ้ายังไม่ล็อกอิน ให้เตะกลับไปหน้า Login ทันที)
if not st.session_state.get('logged_in'):
    st.switch_page("app.py")

# ==========================================
# 🌟 CSS Theme (ฟอนต์ Kanit + Blue Wave & Mint Green)
# ==========================================
st.markdown("""
    <style>
    /* 1. นำเข้าฟอนต์ Kanit และ ฟอนต์ไอคอน Material กลับมาให้ชัวร์ */
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');
    
    /* 2. บังคับฟอนต์ Kanit เฉพาะตัวหนังสือหลักๆ */
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
        st.image("new-logo-apdi.png", use_container_width=True)
    except:
        st.warning("หารูปโลโก้ไม่พบ")
        
    st.markdown("---")
    
    role_th = "อาจารย์" if st.session_state.get('role') == 'teacher' else "นักศึกษา"
    st.markdown(f"### {st.session_state.get('user_id')}")
    st.markdown(f"**สถานะ:** {role_th}")
    st.markdown("---")
    
    st.markdown("**เมนูหลัก**")
    if st.session_state.get('role') == 'student':
        st.page_link("pages/1_My_Profile.py", label="ประวัติส่วนตัว (My Profile)")
    elif st.session_state.get('role') == 'teacher':
        st.page_link("pages/2_Teacher_Panel.py", label="จัดการนักศึกษา (Teacher Panel)")
        st.page_link("pages/1_My_Profile.py", label="ดูตัวอย่างหน้าประวัติ")

    st.markdown("<br>" * 10, unsafe_allow_html=True) 
    if st.button("ออกจากระบบ", type="primary", use_container_width=True):
        st.session_state.clear()
        try:
            st.switch_page("app.py")
        except:
            st.rerun()

# ==========================================
# 🌟 เช็คว่าใครกำลังดูหน้านี้อยู่? (กำหนด target_id)
# ==========================================
if st.session_state.get('role') == 'teacher':
    if 'view_student_id' in st.session_state:
        target_id = st.session_state['view_student_id']
    else:
        st.warning("⚠️ กรุณาเลือกนักศึกษาจากหน้า Teacher Panel ก่อนครับ")
        st.stop()
else:
    target_id = st.session_state.get('user_id')

# ==========================================
# ส่วนหัวของหน้าเว็บ
# ==========================================
st.title("🎓 ระบบจัดการข้อมูลประวัตินักศึกษา")
st.markdown(f"**กำลังแสดงข้อมูลประวัติของรหัส:** {target_id}") 
st.markdown("---")

# ==========================================
# 2. ตั้งค่าสถานะ โหมดแก้ไขข้อมูล (Edit Mode)
# ==========================================
for i in range(1, 6):
    if f'edit_t{i}' not in st.session_state:
        st.session_state[f'edit_t{i}'] = False

# ==========================================
# ==========================================
# 3. สร้างระบบ Tabs แบบซ่อน/แสดงตามสิทธิ์
# ==========================================
# กำหนดรายชื่อ Tabs พื้นฐานที่ทุกคน(รวมถึงนักศึกษา)มองเห็น
tab_names = [
    "📝 ข้อมูลพื้นฐาน", 
    "📚 ประวัติการศึกษา & TOEIC", 
    "🏆 รางวัล & ความประพฤติ", 
    "💼 การทำงาน & กิจกรรม", 
    "📂 อัปโหลดไฟล์"
]

# ตรวจสอบสิทธิ์: ถ้าเป็น 'teacher' หรือ 'admin' ให้เพิ่ม Tab 6 เข้าไป
is_staff = st.session_state.get('role') in ['teacher', 'admin']

if is_staff:
    tab_names.append("บันทึกการเข้าพบอาจารย์")

# สร้าง Tabs ขึ้นมาตามจำนวนที่จัดเตรียมไว้ใน list
tabs = st.tabs(tab_names)

# แตกตัวแปรเก็บไว้ใช้งาน (Tab 1 ถึง 5 มีเสมอ)
tab1, tab2, tab3, tab4, tab5 = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4]

# --- TAB 1: ข้อมูลพื้นฐาน ---
with tab1:
    d1 = not st.session_state['edit_t1']
    st.subheader("ประวัติส่วนตัว (Personal Information)")

    col_pfx, col_fname, col_lname, col_nick = st.columns([1.5, 3, 3, 1.5])
    with col_pfx:
        prefix = st.selectbox("คำนำหน้า", ["นาย", "นางสาว"], key="t1_prefix", disabled=d1)
    with col_fname:
        fname = st.text_input("ชื่อ", key="t1_fname", disabled=d1)
    with col_lname:
        lname = st.text_input("นามสกุล", key="t1_lname", disabled=d1)
    with col_nick:
        nickname = st.text_input("ชื่อเล่น", key="t1_nickname", disabled=d1)

    eng_name = st.text_input("ชื่อ-สกุล ภาษาอังกฤษ (Mr./Miss)", key="t1_eng_name", disabled=d1)

    col_adv, col_std = st.columns(2)
    with col_adv:
        st.text_input("อาจารย์ที่ปรึกษา", value="รอการดึงข้อมูลจากระบบ", disabled=True, key="t1_advisor")
    with col_std:
        st.text_input("รหัสนักศึกษา", value=target_id, disabled=True, key="t1_std_id")

    col_dob, col_age, col_nat, col_eth, col_rel = st.columns([2, 1, 1.5, 1.5, 1.5])
    with col_dob:
        dob = st.date_input("วันเดือนปีเกิด", key="t1_dob", disabled=d1)
    with col_age:
        age = st.number_input("อายุ", min_value=15, max_value=60, step=1, key="t1_age", disabled=d1)
    with col_nat:
        nationality = st.text_input("สัญชาติ", key="t1_nationality", disabled=d1)
    with col_eth:
        ethnicity = st.text_input("เชื้อชาติ", key="t1_ethnicity", disabled=d1)
    with col_rel:
        religion = st.text_input("ศาสนา", key="t1_religion", disabled=d1)

    col_home, col_tel, col_line = st.columns([2, 1.5, 1.5])
    with col_home:
        hometown = st.text_input("ภูมิลำเนา (จังหวัด)", key="t1_hometown", disabled=d1)
    with col_tel:
        tel = st.text_input("เบอร์โทรติดต่อ", key="t1_tel", disabled=d1)
    with col_line:
        line_id = st.text_input("LINE ID", key="t1_line_id", disabled=d1)

    st.markdown("---")
    st.subheader("📍 ที่อยู่ปัจจุบัน")
    
    residence_type = st.radio("ประเภทที่พักอาศัย", ["หอพักของมหาวิทยาลัย", "หอพักภายนอก", "บ้าน"], horizontal=True, key="t1_res_type", disabled=d1)
    
    if residence_type in ["หอพักของมหาวิทยาลัย", "หอพักภายนอก"]:
        col_bld, col_rm, col_fl = st.columns([2, 1, 1])
        with col_bld:
            st.text_input("อาคาร", key="t1_bldg", disabled=d1)
        with col_rm:
            st.text_input("ห้องพักเลขที่", key="t1_room", disabled=d1)
        with col_fl:
            st.text_input("ชั้น", key="t1_floor", disabled=d1)
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        st.text_input("เลขที่", key="t1_house_no", disabled=d1)
    with col_a2:
        st.text_input("หมู่ที่", key="t1_moo", disabled=d1)
    with col_a3:
        st.text_input("ซอย", key="t1_soi", disabled=d1)
    with col_a4:
        st.text_input("ถนน", key="t1_road", disabled=d1)

    col_a5, col_a6, col_a7, col_a8 = st.columns(4)
    with col_a5:
        st.text_input("ตำบล/แขวง", key="t1_subdist", disabled=d1)
    with col_a6:
        st.text_input("อำเภอ/เขต", key="t1_dist", disabled=d1)
    with col_a7:
        st.text_input("จังหวัด", key="t1_prov", disabled=d1) 
    with col_a8:
        st.text_input("รหัสไปรษณีย์", key="t1_zipcode", disabled=d1)

    st.markdown("---")
    st.subheader("👨‍👩‍👧‍👦 ข้อมูลครอบครัว")

    col_f1, col_f2, col_f3 = st.columns([2, 1.5, 1.5])
    with col_f1:
        st.text_input("ชื่อบิดา", key="t1_father_name", disabled=d1)
    with col_f2:
        st.text_input("อาชีพบิดา", key="t1_father_job", disabled=d1)
    with col_f3:
        st.text_input("เบอร์โทรติดต่อ (บิดา)", key="t1_father_tel", disabled=d1)

    col_m1, col_m2, col_m3 = st.columns([2, 1.5, 1.5])
    with col_m1:
        st.text_input("ชื่อมารดา", key="t1_mother_name", disabled=d1)
    with col_m2:
        st.text_input("อาชีพมารดา", key="t1_mother_job", disabled=d1)
    with col_m3:
        st.text_input("เบอร์โทรติดต่อ (มารดา)", key="t1_mother_tel", disabled=d1)

    col_stat, col_sib = st.columns([3, 1])
    with col_stat:
        st.radio("สถานภาพของบิดา/มารดา", ["อยู่ด้วยกัน", "แยกกันอยู่", "หม้าย/หย่าร้าง"], horizontal=True, key="t1_parent_stat", disabled=d1)
    with col_sib:
        st.number_input("จำนวนพี่น้อง (คน)", min_value=1, max_value=20, step=1, key="t1_siblings", disabled=d1)

    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        st.text_input("ผู้ปกครอง (กรณีไม่ใช่บิดา/มารดา)", key="t1_guardian_name", disabled=d1)
    with col_g2:
        st.text_input("อาชีพผู้ปกครอง", key="t1_guardian_job", disabled=d1)

    st.markdown("---")
    st.subheader("🚨 ผู้ติดต่อกรณีฉุกเฉิน")
    col_em1, col_em2 = st.columns(2)
    with col_em1:
        st.text_input("เบอร์โทรติดต่อกรณีฉุกเฉิน", key="t1_em_tel", disabled=d1)
    with col_em2:
        st.text_input("ความเกี่ยวข้องเป็น", key="t1_em_rel", disabled=d1)

    st.write("<br>", unsafe_allow_html=True)
    if not st.session_state['edit_t1']:
        if st.button("✏️ แก้ไขข้อมูลพื้นฐาน", use_container_width=True, key="btn_edit_t1"):
            st.session_state['edit_t1'] = True
            st.rerun() 
    else:
        if st.button("💾 บันทึกข้อมูลพื้นฐานเรียบร้อย", use_container_width=True, type="primary", key="btn_save_t1"):
            st.session_state['edit_t1'] = False
            st.success("บันทึกข้อมูลสำเร็จ!")
            st.rerun() 

# --- TAB 2: ประวัติการศึกษา ---
with tab2:
    d2 = not st.session_state['edit_t2']
    st.subheader("📚 ประวัติการศึกษา (มัธยมศึกษา/ปวช./ปวส.)")
    st.text_input("จบการศึกษาจากโรงเรียน", key="t2_school_name", disabled=d2)
    
    col_ed1, col_ed2, col_ed3, col_ed4 = st.columns(4)
    with col_ed1:
        st.text_input("อำเภอ", key="t2_school_dist", disabled=d2)
    with col_ed2:
        st.text_input("จังหวัด", key="t2_school_prov", disabled=d2) 
    with col_ed3:
        st.text_input("แผนการเรียน", key="t2_school_plan", disabled=d2)
    with col_ed4:
        st.text_input("เกรดเฉลี่ยสะสม", key="t2_school_gpa", disabled=d2)

    st.markdown("---")
    st.subheader("🎯 ประวัติคะแนน TOEIC SCORE")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.number_input("ปี 1 เทอม 1", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y1t1", disabled=d2)
        st.number_input("ปี 2 เทอม 1", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y2t1", disabled=d2)
        st.number_input("ปี 3 เทอม 1", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y3t1", disabled=d2)
        st.number_input("ปี 4 เทอม 1", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y4t1", disabled=d2)
    with col_t2:
        st.number_input("ปี 1 เทอม 2", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y1t2", disabled=d2)
        st.number_input("ปี 2 เทอม 2", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y2t2", disabled=d2)
        st.number_input("ปี 3 เทอม 2", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y3t2", disabled=d2)
        st.number_input("ปี 4 เทอม 2", min_value=0, max_value=990, step=5, value=0, key="t2_toeic_y4t2", disabled=d2)

    st.markdown("---")
    st.subheader("🎓 ข้อมูลการศึกษาระดับปริญญาตรี")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.text_input("วิชาเอกที่เลือกเรียน", key="t2_major", disabled=d2)
    with col_m2:
        st.text_input("วิชาโท", key="t2_minor", disabled=d2)

    st.write("<br>", unsafe_allow_html=True)
    st.markdown("**ภาระค่าใช้จ่ายในการเรียน:**")
    financial_support = st.radio("เลือกรูปแบบภาระค่าใช้จ่าย", ["ทุนส่วนตัว", "กู้ยืม กยศ.", "กู้ยืม กรอ.", "ทุนอื่นๆ"], horizontal=True, label_visibility="collapsed", key="t2_finance_type", disabled=d2)
    if financial_support == "ทุนอื่นๆ":
        st.text_input("โปรดระบุรายละเอียดทุนอื่นๆ", key="t2_finance_other", disabled=d2)

    st.write("<br>", unsafe_allow_html=True)
    if not st.session_state['edit_t2']:
        if st.button("✏️ แก้ไขประวัติการศึกษา", use_container_width=True, key="btn_edit_t2"):
            st.session_state['edit_t2'] = True
            st.rerun() 
    else:
        if st.button("💾 บันทึกประวัติการศึกษาเรียบร้อย", use_container_width=True, type="primary", key="btn_save_t2"):
            st.session_state['edit_t2'] = False
            st.success("บันทึกข้อมูลสำเร็จ!")
            st.rerun()

# --- TAB 3: รางวัล & ความประพฤติ ---
with tab3:
    d3 = not st.session_state['edit_t3']
    
    st.subheader("การบันทึกความประพฤติ")
    
    # 🌟 โซนที่ 1: ฟอร์มบันทึกข้อมูล (ซ่อนไว้ให้เฉพาะอาจารย์เห็น)
    if st.session_state.get('role') == 'teacher':
        st.markdown("**สำหรับอาจารย์ที่ปรึกษา:** บันทึกประวัติความประพฤติ")
        with st.form("conduct_form"):
            col_c1, col_c2 = st.columns([3, 1])
            with col_c1:
                st.text_input("รายละเอียดพฤติกรรม (เช่น มาสาย, ทะเลาะวิวาท)", key="t3_conduct_detail", disabled=d3)
            with col_c2:
                st.date_input("วันที่เกิดเหตุ", key="t3_conduct_date", disabled=d3)
                
            if st.form_submit_button("บันทึกความประพฤติ", disabled=d3):
                st.success("จำลองการส่งข้อมูล... (รอเชื่อมต่อฐานข้อมูล)")
                
    # 🌟 โซนที่ 2: ส่วนแสดงประวัติ (ทั้งนักศึกษาและอาจารย์จะเห็นตรงนี้เหมือนกัน)
    st.markdown("**ประวัติที่ถูกบันทึกในระบบ:**")
    
    has_conduct_record = False # เปลี่ยนเป็น True ถ้าเจอข้อมูลใน DB
    
    if has_conduct_record:
        st.error("🚨 วันที่ 15/03/2026 : เข้าเรียนสายเกิน 3 ครั้ง")
    else:
        st.info("ประวัติความประพฤติ: ปกติ ไม่มีประวัติการหักคะแนน")
    
    st.markdown("---")
    st.subheader("รางวัลเกียรติคุณ")
    df_awards = pd.DataFrame({
        "ลำดับ": [1], 
        "รายละเอียด": ["ชนะเลิศการประกวดนวัตกรรม"], 
        "วันที่": ["2023-10-15"]
    })
    edited_awards = st.data_editor(df_awards, num_rows="dynamic", use_container_width=True, key="t3_awards_editor", disabled=d3)

    st.write("<br>", unsafe_allow_html=True)
    if not st.session_state['edit_t3']:
        if st.button("แก้ไขข้อมูลรางวัลและความประพฤติ", use_container_width=True, key="btn_edit_t3"):
            st.session_state['edit_t3'] = True
            st.rerun()
    else:
        if st.button("บันทึกข้อมูลรางวัลเรียบร้อย", use_container_width=True, type="primary", key="btn_save_t3"):
            st.session_state['edit_t3'] = False
            st.success("บันทึกข้อมูลสำเร็จ!")
            st.rerun()

# --- TAB 4: การทำงาน & กิจกรรม ---
with tab4:
    d4 = not st.session_state['edit_t4']
    
    st.subheader("💼 การทำงานระหว่างเรียน")
    st.markdown("กรุณากรอกประวัติการทำงาน หรือการฝึกงาน (ถ้ามี)")
    
    df_work = pd.DataFrame({
        "ลำดับ": [1], 
        "สถานที่ทำงาน/ตำแหน่ง": ["ผู้ช่วยวิจัย (Research Assistant)"], 
        "ระยะเวลา": ["เทอม 1/2566"]
    })
    
    edited_work = st.data_editor(
        df_work, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="t4_work_editor", 
        disabled=d4
    )

    st.markdown("---")
    
    st.subheader("✨ ความสามารถพิเศษและอื่นๆ")
    df_skills = pd.DataFrame({
        "ลำดับ": [1], 
        "ทักษะ/ความสามารถ": ["ภาษาอังกฤษ (English)"], 
        "ระดับความชำนาญ": ["ปานกลาง (Intermediate)"]
    })
    
    edited_skills = st.data_editor(
        df_skills, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="t4_skills_editor", 
        disabled=d4
    )
    
    st.text_area("บันทึกอื่นๆ (ข้อความอิสระ)", key="t4_other_notes", disabled=d4)
    
    st.write("<br>", unsafe_allow_html=True)
    if not st.session_state['edit_t4']:
        if st.button("✏️ แก้ไขข้อมูลการทำงานและกิจกรรม", use_container_width=True, key="btn_edit_t4"):
            st.session_state['edit_t4'] = True
            st.rerun()
    else:
        if st.button("💾 บันทึกข้อมูลการทำงานและกิจกรรม", use_container_width=True, type="primary", key="btn_save_t4"):
            st.session_state['edit_t4'] = False
            st.success("บันทึกข้อมูลสำเร็จ!")
            st.rerun()

# --- TAB 5: อัปโหลดไฟล์ ---
with tab5:
    d5 = not st.session_state['edit_t5']
    
    st.subheader("ระบบจัดเก็บไฟล์และรูปภาพประจำปี")
    st.markdown("### รูปภาพนักศึกษา (รายปี)")
    st.markdown("กรุณาอัปโหลดภาพถ่ายเต็มตัว เห็นหน้าตาชัดเจน **ชุดเครื่องแบบสถาบัน APDI เท่านั้น**")

    placeholder_style = """
        <div style='border: 2px dashed #8BB4F9; border-radius: 15px; padding: 40px; text-align: center; color: #6B7280; background-color: #F4F7FC; margin-bottom: 10px;'>
            <span style='font-size: 24px; font-family: "Material Symbols Rounded";'>image</span><br>
            พื้นที่แสดงรูปภาพ {year}
        </div>
    """

    col_img1, col_img2 = st.columns(2, gap="large")
    with col_img1:
        st.markdown("<h4 style='color: #3B82F6;'>ปี 1</h4>", unsafe_allow_html=True)
        img_y1 = st.file_uploader("อัปโหลดรูปภาพ ปี 1", type=['png', 'jpg', 'jpeg'], key="t5_img_y1", disabled=d5)
        if img_y1 is not None:
            st.image(img_y1, use_container_width=True, caption="รูปภาพ ปี 1")
        else:
            st.markdown(placeholder_style.format(year="ปี 1"), unsafe_allow_html=True)
            
    with col_img2:
        st.markdown("<h4 style='color: #3B82F6;'>ปี 2</h4>", unsafe_allow_html=True)
        img_y2 = st.file_uploader("อัปโหลดรูปภาพ ปี 2", type=['png', 'jpg', 'jpeg'], key="t5_img_y2", disabled=d5)
        if img_y2 is not None:
            st.image(img_y2, use_container_width=True, caption="รูปภาพ ปี 2")
        else:
            st.markdown(placeholder_style.format(year="ปี 2"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_img3, col_img4 = st.columns(2, gap="large")
    with col_img3:
        st.markdown("<h4 style='color: #3B82F6;'>ปี 3</h4>", unsafe_allow_html=True)
        img_y3 = st.file_uploader("อัปโหลดรูปภาพ ปี 3", type=['png', 'jpg', 'jpeg'], key="t5_img_y3", disabled=d5)
        if img_y3 is not None:
            st.image(img_y3, use_container_width=True, caption="รูปภาพ ปี 3")
        else:
            st.markdown(placeholder_style.format(year="ปี 3"), unsafe_allow_html=True)
            
    with col_img4:
        st.markdown("<h4 style='color: #3B82F6;'>ปี 4</h4>", unsafe_allow_html=True)
        img_y4 = st.file_uploader("อัปโหลดรูปภาพ ปี 4", type=['png', 'jpg', 'jpeg'], key="t5_img_y4", disabled=d5)
        if img_y4 is not None:
            st.image(img_y4, use_container_width=True, caption="รูปภาพ ปี 4")
        else:
            st.markdown(placeholder_style.format(year="ปี 4"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### เอกสารสำคัญอื่นๆ (PDF)")
    
    pdf_doc = st.file_uploader("อัปโหลดเอกสารประกอบอื่นๆ (เช่น สำเนาบัตร, ใบรายงานผลการศึกษา)", type=['pdf'], key="t5_pdf_doc", disabled=d5)
    
    if pdf_doc is not None:
        st.success(f"ไฟล์ '{pdf_doc.name}' พร้อมสำหรับการบันทึกเข้าสู่ระบบแล้ว")
    
    st.write("<br>", unsafe_allow_html=True)
    if not st.session_state['edit_t5']:
        if st.button("เปิดโหมดอัปโหลดไฟล์", use_container_width=True, key="btn_edit_t5"):
            st.session_state['edit_t5'] = True
            st.rerun()
    else:
        if st.button("บันทึกไฟล์ทั้งหมดเข้าสู่ระบบ", use_container_width=True, type="primary", key="btn_save_t5"):
            st.session_state['edit_t5'] = False
            st.success("อัปโหลดไฟล์สำเร็จ!")
            st.rerun()

# --- TAB 6: บันทึกการเข้าพบอาจารย์ที่ปรึกษา (แสดงเฉพาะอาจารย์/แอดมิน) ---
if is_staff:
    tab6 = tabs[5] # ดึง Tab ที่ 6 มาใช้งาน
    
    with tab6:
        st.subheader("บันทึกการเข้าพบอาจารย์ที่ปรึกษา")
        st.markdown("กรุณากรอกรายละเอียดการเข้าพบอาจารย์ที่ปรึกษาเพื่อเก็บเป็นประวัติการให้คำปรึกษา")
        
        with st.form("consultation_form"):
            topic = st.text_input("เรื่องที่เข้าพบ", placeholder="ระบุหัวข้อการเข้าพบ เช่น ปรึกษาเรื่องการลงทะเบียน", key="con_topic")
            
            details = st.text_area("รายละเอียดการปรึกษา", placeholder="ระบุเนื้อหาโดยสรุปของการเข้าพบ", key="con_details")
            
            col_name, col_year, col_term = st.columns([2, 1, 1])
            with col_name:
                student_full_name = get_student_name(target_id)
                st.text_input("ชื่อ-นามสกุล นักศึกษา", value=student_full_name, disabled=True, key="con_std_name")
                
            with col_year:
                year_level = st.selectbox("ชั้นปี", ["ปี 1", "ปี 2", "ปี 3", "ปี 4", "ปีอื่นๆ"], key="con_year_level")
            with col_term:
                academic_year = st.text_input("ปีการศึกษา", placeholder="เช่น 2568", key="con_academic_year")
                
            col_date, col_empty = st.columns([1, 1])
            with col_date:
                meeting_date = st.date_input("วันที่เข้าพบ", key="con_meeting_date")
                
            st.write("<br>", unsafe_allow_html=True)
            
            submit_consult = st.form_submit_button("บันทึกข้อมูลการเข้าพบ", use_container_width=True)
            
            if submit_consult:
                if topic and academic_year:
                    success = save_consultation(target_id, topic, details, year_level, academic_year, meeting_date)
                    if success:
                        st.success("บันทึกข้อมูลการเข้าพบเรียบร้อยแล้ว")
                        st.rerun() 
                    else:
                        st.error("เกิดข้อผิดพลาดในการบันทึกข้อมูล")
                else:
                    st.warning("กรุณากรอกข้อมูล เรื่อง และ ปีการศึกษา ให้ครบถ้วน")
                    
        # ==========================================
        # 🌟 ส่วนแสดงผลตารางประวัติการเข้าพบ
        # ==========================================
        st.markdown("---")
        st.subheader("ประวัติการเข้าพบอาจารย์ที่ปรึกษา")
        
        df_consultations = get_consultations_by_student(target_id)
        
        if not df_consultations.empty:
            st.dataframe(df_consultations, use_container_width=True, hide_index=True)
        else:
            st.info("ยังไม่มีประวัติการเข้าพบอาจารย์ที่ปรึกษาในระบบ")
                
    