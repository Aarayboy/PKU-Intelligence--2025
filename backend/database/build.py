# build.py - 数据库构建脚本
import sqlite3
import json
import os

def build_user_database(db_path="user_database.db"):
    """构建用户数据库"""
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("创建 UserData 表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserData (
            ID TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            key TEXT NOT NULL,
            courses TEXT NOT NULL  -- 存储为JSON字符串
        )
    ''')
    
    # 插入用户数据
    users = [
        ("user001", "张三", "password123", json.dumps(["数学", "物理", "编程基础"])),
        ("user002", "李四", "mypassword", json.dumps(["语文", "英语", "历史"])),
        ("user003", "王五", "hello123", json.dumps(["数学", "化学", "生物"])),
        ("admin", "管理员", "admin123", json.dumps(["数学", "物理", "化学", "语文", "英语"]))
    ]
    
    cursor.executemany(
        "INSERT INTO UserData (ID, name, key, courses) VALUES (?, ?, ?, ?)",
        users
    )
    
    conn.commit()
    conn.close()
    print(f"✓ 用户数据库构建完成: {db_path}")
    return len(users)

def build_course_database(db_path="course_database.db"):
    """构建课程数据库"""
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("创建 Course 表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Course (
            name TEXT PRIMARY KEY,
            tags TEXT NOT NULL,  -- 存储为JSON字符串
            myNotes TEXT NOT NULL,  -- 存储为JSON字符串
            classTime TEXT NOT NULL  -- 上课时间
        )
    ''')
    
    # 插入课程数据（新增classTime字段）
    courses = [
        ("数学", json.dumps(["理科", "计算", "基础"]), json.dumps([1, 2]), "周一 9:00-11:00"),
        ("物理", json.dumps(["理科", "实验", "理论"]), json.dumps([3, 4]), "周二 14:00-16:00"),
        ("化学", json.dumps(["理科", "实验", "反应"]), json.dumps([5]), "周三 10:00-12:00"),
        ("语文", json.dumps(["文科", "语言", "文学"]), json.dumps([6]), "周四 8:00-10:00"),
        ("英语", json.dumps(["文科", "语言", "国际"]), json.dumps([7]), "周五 15:00-17:00"),
        ("编程基础", json.dumps(["计算机", "实践", "技术"]), json.dumps([8]), "周六 9:00-12:00"),
        ("历史", json.dumps(["文科", "文化", "记忆"]), json.dumps([9]), "周一 16:00-18:00"),
        ("生物", json.dumps(["理科", "生命", "实验"]), json.dumps([10]), "周三 14:00-16:00")
    ]
    
    cursor.executemany(
        "INSERT INTO Course (name, tags, myNotes, classTime) VALUES (?, ?, ?, ?)",
        courses
    )
    
    conn.commit()
    conn.close()
    print(f"✓ 课程数据库构建完成: {db_path}")
    return len(courses)

def build_note_database(db_path="note_database.db"):
    """构建笔记数据库"""
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("创建 MyNote 表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MyNote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file TEXT NOT NULL,
            lessonName TEXT NOT NULL
        )
    ''')
    
    # 插入笔记数据
    notes = [
        ("三角函数基础", "/notes/math/trigonometry.pdf", "数学"),
        ("导数与微分", "/notes/math/derivative.pdf", "数学"),
        ("牛顿力学", "/notes/physics/newton.pdf", "物理"),
        ("电磁学原理", "/notes/physics/electromagnetism.pdf", "物理"),
        ("化学反应基础", "/notes/chemistry/reactions.pdf", "化学"),
        ("古诗词赏析", "/notes/chinese/poetry.pdf", "语文"),
        ("英语语法", "/notes/english/grammar.pdf", "英语"),
        ("Python入门", "/notes/programming/python_basics.pdf", "编程基础"),
        ("中国古代史", "/notes/history/ancient_china.pdf", "历史"),
        ("细胞生物学", "/notes/biology/cell_biology.pdf", "生物")
    ]
    
    cursor.executemany(
        "INSERT INTO MyNote (name, file, lessonName) VALUES (?, ?, ?)",
        notes
    )
    
    conn.commit()
    conn.close()
    print(f"✓ 笔记数据库构建完成: {db_path}")
    return len(notes)

def build_all_databases():
    """构建所有三个数据库"""
    print("🚀 开始分别构建三个数据库...")
    print("=" * 50)
    
    # 构建三个独立的数据库
    user_count = build_user_database()
    course_count = build_course_database()
    note_count = build_note_database()
    
    print("=" * 50)
    print("✅ 所有数据库构建完成！")
    print(f"📁 生成的数据库文件:")
    print(f"  - user_database.db (用户数据)")
    print(f"  - course_database.db (课程数据)")
    print(f"  - note_database.db (笔记数据)")

if __name__ == "__main__":
    build_all_databases()