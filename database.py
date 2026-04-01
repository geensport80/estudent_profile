import sqlite3
import pandas as pd

def get_connection():
    # สร้างการเชื่อมต่อกับไฟล์ student_profile.db
    conn = sqlite3.connect('student_profile.db', check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. สร้างตารางอาจารย์ (teachers)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id TEXT PRIMARY KEY, 
            full_name TEXT NOT NULL, 
            department TEXT
        )
    ''')
    
    # 2. สร้างตารางนักศึกษา (students)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY, 
            advisor_id TEXT, 
            prefix TEXT, 
            first_name TEXT, 
            last_name TEXT, 
            nickname TEXT, 
            tel TEXT,
            FOREIGN KEY(advisor_id) REFERENCES teachers(teacher_id)
        )
    ''')
    
    # 3. ใส่ข้อมูลอาจารย์จำลองตั้งต้น
    cursor.execute("INSERT OR IGNORE INTO teachers VALUES ('T001', 'อ.สมศรี ใจดี', 'การบิน')")
    cursor.execute("INSERT OR IGNORE INTO teachers VALUES ('T002', 'อ.มานะ ขยัน', 'การบิน')")
    
    conn.commit()
    conn.close()

def import_students_from_csv(df, advisor_id):
    conn = get_connection()
    cursor = conn.cursor()
    success_count = 0
    
    # ใช้ Index [0] และ [1] แทนการล็อกชื่อคอลัมน์ (แก้ปัญหาชื่อคอลัมน์มีวรรคซ่อนอยู่)
    col_id = df.columns[0]
    col_name = df.columns[1]
    
    for index, row in df.iterrows():
        std_id = str(row[col_id]).strip()
        full_name = str(row[col_name]).strip()
        
        name_parts = full_name.split(maxsplit=1)
        fname = name_parts[0] if len(name_parts) > 0 else full_name
        lname = name_parts[1] if len(name_parts) > 1 else ""
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO students (student_id, advisor_id, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (std_id, advisor_id, fname, lname))
            
            # ถ้า rowcount > 0 แปลว่าเพิ่งนำเข้าใหม่สำเร็จ (ถ้าเป็น 0 คือมีรหัสนี้ในระบบอยู่แล้ว)
            if cursor.rowcount > 0:
                success_count += 1
        except sqlite3.Error as e:
            print(f"Error inserting {std_id}: {e}")
            
    conn.commit()
    conn.close()
    return success_count

def get_teacher_dict():
    conn = get_connection()
    df = pd.read_sql_query("SELECT teacher_id, full_name FROM teachers", conn)
    conn.close()
    return dict(zip(df['teacher_id'], df['full_name']))

def get_students_by_advisor(advisor_id):
    conn = get_connection()
    query = """
        SELECT student_id AS 'รหัสประจำตัว', 
               first_name || ' ' || last_name AS 'ชื่อ-นามสกุล',
               tel AS 'เบอร์โทรศัพท์'
        FROM students 
        WHERE advisor_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(advisor_id,))
    conn.close()
    return df

# ========================================================
# 🌟 ทริคสำคัญ: สั่งรัน init_db() อัตโนมัติทุกครั้งที่ไฟล์นี้ถูกเรียกใช้
# ========================================================
init_db()