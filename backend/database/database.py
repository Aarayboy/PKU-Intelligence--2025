import sqlite3
import threading
from pathlib import Path
import json
import os
from typing import Optional

# --- 配置 ---
try:
    import dotenv  # type: ignore
    dotenv.load_dotenv()
except Exception:
    # 未安装 python-dotenv 时忽略，直接使用系统环境变量
    pass

DB_FILE = os.getenv('dbfile', './database/database.db')
STOREBASE_DIR = os.getenv('storage_dir', './uploads/')



class Database:
    
    _local = threading.local()
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库对象。
        db_path 优先级：
        1) 传入的 db_path 参数（若提供）
        2) 环境变量 dbfile（dotenv 支持）
        3) 默认 ./database/database.db
        """
        # 选择数据库路径
        effective_path = db_path if db_path else DB_FILE
        # 将路径字符串转换为Path对象，并解析为绝对路径
        self.db_path = Path(effective_path).resolve()
        # 确保数据库目录存在
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            # 目录创建失败时忽略，让后续连接抛出更明确的异常
            pass
        self.setup_database()

    def get_db_connection(self):
        """
        获取当前线程的数据库连接。
        如果当前线程还没有连接，则创建一个新的并存储起来。
        """
        # 检查当前线程是否已经有连接
        if not hasattr(self._local, 'connection'):
            # 使用实例的 db_path 创建连接
            self._local.connection = sqlite3.connect(self.db_path)
            # 设置行工厂，方便通过列名访问数据
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def close_connection(self):
        """关闭当前线程的数据库连接。"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
        
    def setup_database(self):
        """
        初始化数据库，创建所有表。
        如果表已存在，则什么也不做。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
    
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # 创建课程表
        #cursor.execute('''
            #CREATE TABLE IF NOT EXISTS courses (
            #    id INTEGER PRIMARY KEY AUTOINCREMENT,
            #    title TEXT NOT NULL
        #    )
        #''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                tags TEXT, -- 存储JSON格式的标签列表，例如: '["基础", "必修"]'
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        # 索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS ix_courses_title ON courses(title)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS ix_courses_user_id ON courses(user_id)
        ''')
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS ux_courses_user_title ON courses(user_id, title)
        ''')
        
        # 创建笔记表
        #cursor.execute('''
        #    CREATE TABLE IF NOT EXISTS notes (
        #        id INTEGER PRIMARY KEY AUTOINCREMENT,
        #        content TEXT,
        #        user_id INTEGER NOT NULL,
        #        course_id INTEGER,
        #        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        #        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE SET NULL
        #    )
        #''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,      -- 对应 myNotes 中的 "name"
                file TEXT,          -- 对应 myNotes 中的 "file"，允许为NULL
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
            )
        ''')
        

        # 初始化一个默认管理员用户（如果不存在）
        cursor.execute("INSERT OR IGNORE INTO users (id, username, email, password) VALUES (1, 'admin', 'admin@example.com', 'adminpass')")
    
        conn.commit()
        # 注意：这里不关闭连接，因为它被线程局部存储管理了



    def get_user(self, user_id=1):
        """
        根据ID获取用户信息。
        返回一个类似字典的sqlite3.Row对象，如果找不到则返回None。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return user

    def add_course_to_user(self, user_id, course_title, tags = []):
        """
        为指定用户添加一门新课程。
        如果该用户已有同名课程，则复用该课程；
        如果没有，则为该用户创建一条新的 courses 记录。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        tags = json.dumps(tags)  # 将标签列表转换为JSON字符串存储
        try:
            # 使用事务确保操作的原子性
            with conn:
                # 1) 检查该用户是否已有同名课程
                cursor.execute(
                    "SELECT id FROM courses WHERE user_id = ? AND title = ?",
                    (user_id, course_title)
                )
                existing = cursor.fetchone()

                if existing:
                    return None
                else:
                    # 2) 为该用户创建一条新的课程记录（允许与其他用户同名）
                    cursor.execute(
                        "INSERT INTO courses (title, tags, user_id) VALUES (?, ?, ?)",
                        (course_title, tags, user_id)
                    )
                    course_id = cursor.lastrowid
                    # 为该课程创建存储目录
                    try:
                        course_storage_path = Path(STOREBASE_DIR) / str(user_id)  / str(course_title)
                        course_storage_path.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        print(f"创建课程存储目录时出错: {e}")
                
            
                # print(f"成功为用户 {user_id} 添加课程 '{course_title}' (课程ID: {course_id})")
                # 查询并返回课程信息
                cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
                course = cursor.fetchone()
                return dict(course)
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False

    def get_user_with_courses_and_notes(self, user_id=1):
        """
        获取用户信息，以及该用户拥有的所有课程。
        这演示了如何进行JOIN查询来重组数据。
        返回UserData数据结构。
        """
        conn = self.get_db_connection()
        conn.row_factory = sqlite3.Row # 确保返回字典式行
        cursor = conn.cursor()
    
        # 获取用户基本信息
        user = self.get_user(user_id)
        if not user:
            return None

        # 获取用户的所有课程
        cursor.execute('''
            SELECT c.* FROM courses c
            WHERE c.user_id = ?
        ''', (user_id,))
    
        courses = cursor.fetchall()
    
        # 将结果组装成类似原始JSON的结构
        user_dict = dict(user)
        user_dict['courses'] = [dict(c) for c in courses]

        for course in user_dict['courses']:
            course_id = course['id']
            course["tags"] = json.loads(course["tags"]) if course["tags"] else []
            # 获取该课程的所有笔记
            cursor.execute('''
                SELECT n.id, n.name, n.file FROM notes n
                WHERE n.user_id = ? AND n.course_id = ?
            ''', (user_id, course_id))
            notes = cursor.fetchall()
            # 组装 myNotes 列表
            course['myNotes'] = [dict(n) for n in notes]
            # 将 title 重命名为 name 以匹配目标JSON
            course['name'] = course.pop('title')
            # 为myNotes添加 lessonName 字段
            for note in course['myNotes']:
                note['lessonName'] = course['name']
    
        return user_dict





    def find_user_by_credentials(self, username_or_email, password):
        """
        通过用户名/邮箱和密码查找用户。
        返回一个不含密码字段的用户信息字典，如果找不到则返回None。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        # 使用 OR 来匹配用户名或邮箱
        sql = "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?"
        cursor.execute(sql, (username_or_email, username_or_email, password))
        user = cursor.fetchone()

        if user:
            # 将sqlite3.Row对象转换为字典，并移除password字段
            user_dict = dict(user)
            user_dict.pop('password', None) # 安全地移除密码
            return user_dict
        return None

    def find_user_by_username_or_email(self, value):
        """
        通过用户名或邮箱查找用户。
        返回完整的用户信息（包含密码），如果找不到则返回None。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE username = ? OR email = ?"
        cursor.execute(sql, (value, value))
        user = cursor.fetchone()
        return dict(user) if user else None

    def add_user(self, username, email, password):
        """
        添加一个新用户。
        如果用户名或邮箱已存在，则返回None。
        成功则返回不含密码的用户信息字典。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn: # 自动提交或回滚
                # 检查重复。数据库的UNIQUE约束是第一道防线，这里检查是为了更快返回
                if self.find_user_by_username_or_email(username) or self.find_user_by_username_or_email(email):
                    return None
            
                # 插入新用户。id会自动生成
                sql = "INSERT INTO users (username, email, password) VALUES (?, ?, ?)"
                cursor.execute(sql, (username, email, password))
            
                # 获取新创建用户的ID
                new_user_id = cursor.lastrowid
            
                # 查询新用户信息以返回
                cursor.execute("SELECT * FROM users WHERE id = ?", (new_user_id,))
                new_user = cursor.fetchone()

                # 为新用户创建存储目录
                try:
                    user_storage_path = Path(STOREBASE_DIR) / str(new_user_id)
                    user_storage_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"创建用户存储目录时出错: {e}")
            
                # 返回不含密码的副本
                user_dict = dict(new_user)
                user_dict.pop('password', None)
                return user_dict
            
        except sqlite3.IntegrityError:
            # 如果因为UNIQUE约束失败（例如并发插入），捕获错误
            print(f"错误：用户名 '{username}' 或邮箱 '{email}' 已存在。")
            return None
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return None
    
    def add_note(self, title, lessonName, tags, files, user_id):
        """
        添加一条新笔记，并将其关联到指定用户和课程。
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        tags = json.dumps(tags)  # 将标签列表转换为JSON字符串存储
        try:
            with conn:
                # 查询课程ID
                cursor.execute(
                    "SELECT id FROM courses WHERE user_id = ? AND title = ?",
                    (user_id, lessonName)
                )
                course = cursor.fetchone()
                if not course:
                    print(f"错误：用户 {user_id} 下不存在课程 '{lessonName}'，无法添加笔记。")
                    return None
                course_id = course['id'] if isinstance(course, sqlite3.Row) else course[0]
                # 插入新笔记
                # print(f"已找到课程ID {course_id}，正在为用户 {user_id} 添加笔记 '{title}'")
                cursor.execute(
                    "INSERT INTO notes (name, file, user_id, course_id) VALUES (?, ?, ?, ?)",
                    (title, files[0] if files else None, user_id, course_id)
                )
                new_note_id = cursor.lastrowid

                # 为新笔记创建存储目录（如果需要）
                try:
                    note_storage_path = Path(STOREBASE_DIR) / str(user_id) / str(lessonName) / str(title)
                    note_storage_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"创建笔记存储目录时出错: {e}")

                # 查询并返回新创建的笔记信息
                cursor.execute("SELECT * FROM notes WHERE id = ?", (new_note_id,))
                new_note = cursor.fetchone()
                return dict(new_note)

        except sqlite3.Error as e:
            print(f"添加笔记时发生数据库错误: {e}")
            return None
    