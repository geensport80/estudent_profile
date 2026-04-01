import sqlite3
import pandas as pd

def get_connection():
    conn = sqlite3.connect('student_profile.db', check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. ตารางอาจารย์
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
        teacher_id TEXT PRIMARY KEY, 
        full_name TEXT NOT NULL, 
        department TEXT)''')
    
    # 2. ตารางนักศึกษา (ข้อมูลหลัก)
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY, 
        advisor_id TEXT, 
        prefix TEXT, first_name TEXT, last_name TEXT, nickname TEXT, eng_name TEXT,
        FOREIGN KEY(advisor_id) REFERENCES teachers(teacher_id))''')

    # 3. ตารางรายละเอียดส่วนตัว
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_details (
        student_id TEXT PRIMARY KEY,
        dob TEXT, age INTEGER, nationality TEXT, ethnicity TEXT, religion TEXT,
        hometown TEXT, tel TEXT, line_id TEXT, res_type TEXT,
        address_json TEXT, family_json TEXT, emergency_json TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id))''')

    # 4. ตารางประวัติการศึกษาและคะแนน TOEIC
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_education (
        student_id TEXT PRIMARY KEY,
        school_name TEXT, school_prov TEXT, school_gpa TEXT,
        toeic_scores_json TEXT, major TEXT, minor TEXT, finance_type TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id))''')

    # 5. ตารางความประพฤติ
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_conduct (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        detail TEXT,
        date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id))''')

    # 6. ตารางบันทึกการเข้าพบอาจารย์ที่ปรึกษา (ของ Tab 6)
    cursor.execute('''CREATE TABLE IF NOT EXISTS advisor_consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        topic TEXT,
        details TEXT,
        year_level TEXT,
        academic_year TEXT,
        meeting_date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id))''')

    # ใส่ข้อมูลอาจารย์ตั้งต้น (Mockup)
    cursor.execute("INSERT OR IGNORE INTO teachers VALUES ('T001', 'อ.สมศรี ใจดี', 'การบิน')")
    cursor.execute("INSERT OR IGNORE INTO teachers VALUES ('T002', 'อ.มานะ ขยัน', 'การบิน')")
    
    conn.commit()
    conn.close()

# ==========================================
# 🌟 ฟังก์ชันจัดการข้อมูล (ที่ระบบหาไม่เจอ ผมเอามารวมให้ครบแล้วครับ)
# ==========================================

def get_teacher_dict():
    """ดึงรายชื่ออาจารย์ไปแสดงใน Dropdown หน้า Teacher Panel"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT teacher_id, full_name FROM teachers", conn)
    conn.close()
    return dict(zip(df['teacher_id'], df['full_name']))

def import_students_from_csv(df, advisor_id):
    """นำเข้ารายชื่อนักศึกษาจากไฟล์ CSV"""
    conn = get_connection()
    cursor = conn.cursor()
    success_count = 0
    col_id, col_name = df.columns[0], df.columns[1]
    
    for _, row in df.iterrows():
        std_id = str(row[col_id]).strip()
        full_name = str(row[col_name]).strip()
        name_parts = full_name.split(maxsplit=1)
        fname = name_parts[0] if len(name_parts) > 0 else full_name
        lname = name_parts[1] if len(name_parts) > 1 else ""
        
        try:
            cursor.execute('INSERT OR IGNORE INTO students (student_id, advisor_id, first_name, last_name) VALUES (?, ?, ?, ?)', 
                           (std_id, advisor_id, fname, lname))
            if cursor.rowcount > 0: success_count += 1
        except: pass
            
    conn.commit()
    conn.close()
    return success_count

def get_students_by_advisor(advisor_id):
    """ดึงรายชื่อนักศึกษาตามอาจารย์ที่ปรึกษา ไปแสดงในตารางหน้า Teacher Panel"""
    conn = get_connection()
    query = "SELECT student_id AS 'รหัสประจำตัว', first_name || ' ' || last_name AS 'ชื่อ-นามสกุล' FROM students WHERE advisor_id = ?"
    df = pd.read_sql_query(query, conn, params=(advisor_id,))
    conn.close()
    return df

def save_consultation(student_id, topic, details, year_level, academic_year, meeting_date):
    """บันทึกข้อมูลการเข้าพบอาจารย์ลงฐานข้อมูล (Tab 6)"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO advisor_consultations (student_id, topic, details, year_level, academic_year, meeting_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, topic, details, year_level, academic_year, str(meeting_date)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving consultation: {e}")
        return False
    finally:
        conn.close()

def get_consultations_by_student(student_id):
    """ดึงประวัติการเข้าพบอาจารย์ของนักศึกษาแต่ละคน"""
    conn = get_connection()
    query = """
    SELECT meeting_date AS 'วันที่เข้าพบ', 
           topic AS 'เรื่องที่เข้าพบ', 
           details AS 'รายละเอียด', 
           year_level AS 'ชั้นปี', 
           academic_year AS 'ปีการศึกษา'
    FROM advisor_consultations 
    WHERE student_id = ?
    ORDER BY meeting_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(student_id,))
    conn.close()
    return df

def get_student_name(student_id):
    """ดึงชื่อ-นามสกุล ของนักศึกษาจาก Database โดยใช้รหัส"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        fname = result[0] if result[0] else ""
        lname = result[1] if result[1] else ""
        return f"{fname} {lname}".strip()
    return "ไม่พบข้อมูลชื่อในระบบ"

# รันฟังก์ชันสร้างตารางทันทีที่ไฟล์นี้ถูกเรียกใช้งาน
init_db()