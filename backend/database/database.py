import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Optional

# --- 配置 ---
try:
    import dotenv  # type: ignore

    dotenv.load_dotenv()
except Exception:
    # 未安装 python-dotenv 时忽略，直接使用系统环境变量
    pass

DB_FILE = os.getenv("dbfile", "./database/database.db")
STOREBASE_DIR = os.getenv("storage_dir", "./uploads/")


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
        if not hasattr(self._local, "connection"):
            # 使用实例的 db_path 创建连接
            self._local.connection = sqlite3.connect(self.db_path)
            # 设置行工厂，方便通过列名访问数据
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def close_connection(self):
        """关闭当前线程的数据库连接。"""
        if hasattr(self._local, "connection"):
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
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """
        )

        # 创建课程表
        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS courses (
        #    id INTEGER PRIMARY KEY AUTOINCREMENT,
        #    title TEXT NOT NULL
        #    )
        #''')

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                tags TEXT, -- 存储JSON格式的标签列表，例如: '["基础", "必修"]'
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )
        # 索引
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_courses_title ON courses(title)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_courses_user_id ON courses(user_id)
        """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_courses_user_title ON courses(user_id, title)
        """
        )

        # 创建笔记表
        # cursor.execute('''
        #    CREATE TABLE IF NOT EXISTS notes (
        #        id INTEGER PRIMARY KEY AUTOINCREMENT,
        #        content TEXT,
        #        user_id INTEGER NOT NULL,
        #        course_id INTEGER,
        #        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        #        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE SET NULL
        #    )
        #''')

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,      -- 对应 myNotes 中的 "name"
                file TEXT,          -- 对应 myNotes 中的 "file"，允许为NULL
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
            )
        """
        )

        # 创建链接分类表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS link_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                icon TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_link_categories_user_id ON link_categories(user_id)
        """
        )

        # 创建链接表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS useful_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                is_trusted BOOLEAN DEFAULT FALSE,
                category_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES link_categories (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_useful_links_user_id ON useful_links(user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_useful_links_category_id ON useful_links(category_id)
        """
        )

        # 创建任务管理表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,           -- 对应 deadlines 列表中的 name
                deadline TEXT NOT NULL,       -- 截止日期时间字符串
                message TEXT,                 -- 对应 message，允许为空
                status TEXT DEFAULT 'pending', -- 状态: pending, completed, overdue 等
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_tasks_user_id ON tasks(user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_tasks_deadline ON tasks(deadline)
        """
        )

        # 初始化一个默认管理员用户（如果不存在）
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, username, email, password) VALUES (1, 'admin', 'admin@example.com', 'adminpass')"
        )
        # 创建课表表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,               -- 课程名称
                teacher TEXT,                     -- 教师姓名
                location TEXT,                    -- 上课地点
                week_type INTEGER DEFAULT 0,      -- 周次类型：0-每周，1-单周，2-双周
                user_id INTEGER NOT NULL,         -- 用户ID
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # 创建上课时间表（多对多关系，因为一门课可能有多个上课时间）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_schedule_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_schedule_id INTEGER NOT NULL,  -- 课程表ID
                time_index INTEGER NOT NULL,          -- 时间索引（0-83，对应一周的课程时间段）
                FOREIGN KEY (course_schedule_id) REFERENCES course_schedules (id) ON DELETE CASCADE,
                UNIQUE(course_schedule_id, time_index)  -- 确保同一门课同一时间不重复
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_course_schedules_user_id ON course_schedules(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_course_schedule_times_course_id ON course_schedule_times(course_schedule_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_course_schedule_times_time_index ON course_schedule_times(time_index)
        """)

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

    def add_course_to_user(self, user_id, course_title, tags=[]):
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
                    (user_id, course_title),
                )
                existing = cursor.fetchone()

                if existing:
                    return None
                else:
                    # 2) 为该用户创建一条新的课程记录（允许与其他用户同名）
                    cursor.execute(
                        "INSERT INTO courses (title, tags, user_id) VALUES (?, ?, ?)",
                        (course_title, tags, user_id),
                    )
                    course_id = cursor.lastrowid
                    # 为该课程创建存储目录
                    try:
                        course_storage_path = (
                            Path(STOREBASE_DIR) / str(user_id) / str(course_title)
                        )
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
        conn.row_factory = sqlite3.Row  # 确保返回字典式行
        cursor = conn.cursor()

        # 获取用户基本信息
        user = self.get_user(user_id)
        if not user:
            return None

        # 获取用户的所有课程
        cursor.execute(
            """
            SELECT c.* FROM courses c
            WHERE c.user_id = ?
        """,
            (user_id,),
        )

        courses = cursor.fetchall()

        # 将结果组装成类似原始JSON的结构
        user_dict = dict(user)
        user_dict["courses"] = [dict(c) for c in courses]

        for course in user_dict["courses"]:
            course_id = course["id"]
            course["tags"] = json.loads(course["tags"]) if course["tags"] else []
            # 获取该课程的所有笔记
            cursor.execute(
                """
                SELECT n.id, n.name, n.file FROM notes n
                WHERE n.user_id = ? AND n.course_id = ?
            """,
                (user_id, course_id),
            )
            notes = cursor.fetchall()
            # 组装 myNotes 列表
            course["myNotes"] = [dict(n) for n in notes]
            # 将 title 重命名为 name 以匹配目标JSON
            course["name"] = course.pop("title")
            # 为myNotes添加 lessonName 字段
            for note in course["myNotes"]:
                note["lessonName"] = course["name"]

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
            user_dict.pop("password", None)  # 安全地移除密码
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
            with conn:  # 自动提交或回滚
                # 检查重复。数据库的UNIQUE约束是第一道防线，这里检查是为了更快返回
                if self.find_user_by_username_or_email(
                    username
                ) or self.find_user_by_username_or_email(email):
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
                user_dict.pop("password", None)
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
                    (user_id, lessonName),
                )
                course = cursor.fetchone()
                if not course:
                    print(
                        f"错误：用户 {user_id} 下不存在课程 '{lessonName}'，无法添加笔记。"
                    )
                    return None
                course_id = (
                    course["id"] if isinstance(course, sqlite3.Row) else course[0]
                )
                # 插入新笔记
                # print(f"已找到课程ID {course_id}，正在为用户 {user_id} 添加笔记 '{title}'")
                cursor.execute(
                    "INSERT INTO notes (name, file, user_id, course_id) VALUES (?, ?, ?, ?)",
                    (title, files[0] if files else None, user_id, course_id),
                )
                new_note_id = cursor.lastrowid

                # 为新笔记创建存储目录（如果需要）
                try:
                    note_storage_path = (
                        Path(STOREBASE_DIR)
                        / str(user_id)
                        / str(lessonName)
                        / str(title)
                    )
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
        
    def edit_course(self, user_id, old_title, new_title):
        """
        修改课程名称
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                # 检查新名称是否已存在
                cursor.execute(
                    "SELECT id FROM courses WHERE user_id = ? AND title = ?",
                    (user_id, new_title)
                )
                existing = cursor.fetchone()
                if existing:
                    return {"error": "课程名称已存在"}
                
                # 更新课程名称
                cursor.execute(
                    "UPDATE courses SET title = ? WHERE user_id = ? AND title = ?",
                    (new_title, user_id, old_title)
                )
                
                if cursor.rowcount == 0:
                    return {"error": "课程不存在或无权修改"}
                
                return {"success": True, "message": "课程名称修改成功"}
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return {"error": f"数据库错误: {e}"}

    def edit_note(self, user_id, course_name, old_note_name, new_note_name):
        """
        修改笔记名称
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                # 获取课程ID
                cursor.execute(
                    "SELECT id FROM courses WHERE user_id = ? AND title = ?",
                    (user_id, course_name)
                )
                course = cursor.fetchone()
                if not course:
                    return {"error": "课程不存在"}
                
                course_id = course["id"] if isinstance(course, sqlite3.Row) else course[0]
                
                # 检查新名称是否已存在
                cursor.execute(
                    "SELECT id FROM notes WHERE user_id = ? AND course_id = ? AND name = ?",
                    (user_id, course_id, new_note_name)
                )
                existing = cursor.fetchone()
                if existing:
                    return {"error": "笔记名称已存在"}
                
                # 更新笔记名称
                cursor.execute(
                    "UPDATE notes SET name = ? WHERE user_id = ? AND course_id = ? AND name = ?",
                    (new_note_name, user_id, course_id, old_note_name)
                )
                
                if cursor.rowcount == 0:
                    return {"error": "笔记不存在或无权修改"}
                
                return {"success": True, "message": "笔记名称修改成功"}
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return {"error": f"数据库错误: {e}"}

    # 常用链接相关方法
    def add_link_category(self, user_id, category, icon, sort_order=0):
        """
        添加链接分类
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(
                    "INSERT INTO link_categories (category, icon, user_id, sort_order) VALUES (?, ?, ?, ?)",
                    (category, icon, user_id, sort_order)
                )
                category_id = cursor.lastrowid
                
                cursor.execute("SELECT * FROM link_categories WHERE id = ?", (category_id,))
                new_category = cursor.fetchone()
                return dict(new_category) if new_category else None
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return None

    def get_link_categories(self, user_id):
        """
        获取用户的所有链接分类
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM link_categories WHERE user_id = ? ORDER BY sort_order, created_at",
                (user_id,)
            )
            categories = cursor.fetchall()
            return [dict(cat) for cat in categories]
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return []

    def add_useful_link(self, user_id, category_id, name, url, description="", is_trusted=False, sort_order=0):
        """
        添加常用链接
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(
                    "INSERT INTO useful_links (name, url, description, is_trusted, category_id, user_id, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, url, description, is_trusted, category_id, user_id, sort_order)
                )
                link_id = cursor.lastrowid
                
                cursor.execute("SELECT * FROM useful_links WHERE id = ?", (link_id,))
                new_link = cursor.fetchone()
                return dict(new_link) if new_link else None
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return None

    def get_useful_links_by_category(self, user_id):
        """
        获取用户的所有链接，按分类组织
        返回格式符合 LinkCategory 结构
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            # 获取所有分类
            categories = self.get_link_categories(user_id)
            
            result = []
            for category in categories:
                cursor.execute(
                    "SELECT * FROM useful_links WHERE user_id = ? AND category_id = ? ORDER BY sort_order, created_at",
                    (user_id, category['id'])
                )
                links = cursor.fetchall()
                
                link_list = []
                for link in links:
                    link_dict = dict(link)
                    link_list.append({
                        "name": link_dict['name'],
                        "url": link_dict['url'],
                        "desc": link_dict['description'] or "",
                        "isTrusted": bool(link_dict['is_trusted'])
                    })
                
                result.append({
                    "category": category['category'],
                    "icon": category['icon'],
                    "links": link_list
                })
            
            return result
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return []

    def delete_link_category(self, user_id, category_id):
        """
        删除链接分类（会级联删除该分类下的所有链接）
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(
                    "DELETE FROM link_categories WHERE id = ? AND user_id = ?",
                    (category_id, user_id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False

    def delete_useful_link(self, user_id, link_id):
        """
        删除常用链接
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(
                    "DELETE FROM useful_links WHERE id = ? AND user_id = ?",
                    (link_id, user_id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False

    # 任务管理相关方法
    def add_task(self, user_id, name, deadline, message="", status="pending"):
        """
        添加任务
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(
                    "INSERT INTO tasks (name, deadline, message, status, user_id) VALUES (?, ?, ?, ?, ?)",
                    (name, deadline, message, status, user_id)
                )
                task_id = cursor.lastrowid
                
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                new_task = cursor.fetchone()
                return dict(new_task) if new_task else None
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return None

    def get_tasks(self, user_id):
        """
        获取用户的任务列表，返回格式与 deadlines 数据结构一致
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM tasks WHERE user_id = ? ORDER BY deadline ASC",
                (user_id,)
            )
            tasks = cursor.fetchall()
            # 转换为 deadlines 数据结构
            deadlines = []
            for task in tasks:
                task_dict = dict(task)
                deadlines.append({
                    "name": task_dict['name'],
                    "deadline": task_dict['deadline'],
                    "message": task_dict['message'] or "",
                    "status": task_dict['status']
                })
            return deadlines
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return []

    def update_task(self, user_id, task_id, **updates):
        """
        更新任务信息
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                # 构建动态更新语句
                set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
                values = list(updates.values())
                values.extend([task_id, user_id])
                
                cursor.execute(
                    f"UPDATE tasks SET {set_clause} WHERE id = ? AND user_id = ?",
                    values
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False

    def delete_task(self, user_id, task_id):
        """
        删除任务
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                cursor.execute(
                    "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                    (task_id, user_id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False

    def update_deadlines(self, user_id, deadlines):
        """
        批量更新用户的DDL列表
        deadlines: 任务对象列表，格式为 [{"name": "...", "deadline": "...", "message": "...", "status": "..."}, ...]
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            with conn:
                # 先删除用户的所有现有任务
                cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
                
                # 批量插入新任务
                for task in deadlines:
                    cursor.execute(
                        "INSERT INTO tasks (name, deadline, message, status, user_id) VALUES (?, ?, ?, ?, ?)",
                        (
                            task.get('name', ''),
                            task.get('deadline', ''),
                            task.get('message', ''),
                            task.get('status', 'pending'),
                            user_id
                        )
                    )
                
                return True
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False