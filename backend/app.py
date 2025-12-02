import os
from pathlib import Path

import dotenv
from flask import Flask, jsonify, request, send_from_directory, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

import spider.login as login
import spider.spider as spider
from database import storage

dotenv.load_dotenv()
LocalHost = os.getenv("localhost") or ""
# Resolve and ensure the base storage directory exists
BASE_STORAGE_DIR = Path(os.getenv("storage_dir", "./uploads/")).resolve()
BASE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
CORS(app)

# 全局复用的 session，但先不登录，等第一次请求再说
_session = None
# 用于存储本学期课程列表
_courses = None


def get_session(id, password):
    """懒加载：第一次用到时才登录，后面复用同一个 session。"""
    global _session
    if _session is not None:
        return _session

    s = login.pku_login_and_get_session(id, password, login.COURSE_BASE_URL)

    if s is None:
        print("登录失败")
        return None

    _session = s
    return _session


@app.route("/userdata", methods=["GET"])
def userdata():
    user_id = request.args.get("id", 1)
    user = storage.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    
    # Return user data with courses

    """ 这里添加了示例的 ddl 列表，实际应用中应从数据库获取并返回
    YOU CODE HERE
    """
    
    # 添加上实例 ddl 列表
    deadlines = [{"name": "提交作业1", "deadline": "2025-10-01 23:59", "message": "balabala", "status": 0},
                 {"name": "项目报告", "deadline": "2025-10-15 17:00", "message": "balabala", "status": 1},
                 {"name": "期中考试复习", "deadline": "2025-10-20 12:00", "message": "为什么要演奏春日影", "status": 0},
                 {"name": "实验报告提交", "deadline": "2025-10-25 18:00", "message": "balabala", "status": 1},
                 {"name": "阅读论文", "deadline": "2025-10-30 20:00", "message": "balabala", "status": 0},
                 {"name": "准备演讲", "deadline": "2025-11-05 15:00", "message": "balabala", "status": 1},
                 {"name": "期末考试复习", "deadline": "2025-11-20 10:00", "message": "balabala", "status": 0},
                 {"name": "提交毕业论文", "deadline": "2026-12-01 23:59", "message": "balabala", "status": 1},

                 ]

    """ 还要添加 linkCategories 字段，这里没有实例数据，实际应用中应从数据库获取并返回
    """
    user["deadlines"] = deadlines
    return jsonify({"data": user})


@app.route("/courses/create", methods=["POST"])
def create_course():
    # Accept JSON or form-data
    data = None
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or request.values or {}

    title = data.get("title") or data.get("name")

    # tags may be sent as an array (from JSON) or as a JSON string (from form)
    tags = []
    tags_raw = data.get("tags")
    if isinstance(tags_raw, list):
        tags = tags_raw
    else:
        try:
            import json as _json

            tags = (
                _json.loads(tags_raw) if isinstance(tags_raw, str) else (tags_raw or [])
            )
        except Exception:
            tags = []

    if not title:
        return jsonify({"error": "title required"}), 400

    # optional userId to attach course to specific user
    user_id = data.get("userId") or None
    course = storage.add_course(title, tags, user_id)

    if not course:
        return jsonify({"error": "failed to create course"}), 500

    return jsonify({"success": True, "course": course})


@app.route("/notes/upload", methods=["POST"])
def upload_note():
    title = request.form.get("title") or request.values.get("title")
    lessonName = (
        request.form.get("lessonName")
        or request.form.get("lesson")
        or request.values.get("lessonName")
    )
    tags_raw = request.form.get("tags") or "[]"
    user_id = request.form.get("userId") or request.values.get("userId")
    try:
        import json

        tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
    except Exception:
        tags = []

    files = request.files.getlist("files") or []
    # enforce at most one file per note
    if len(files) > 1:
        return jsonify({"error": "每个笔记只允许上传一个文件"}), 400
    # require lessonName (course name) and user_id to be present
    if not lessonName:
        return jsonify({"error": "lessonName (课程名) is required"}), 400
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    # Save file (0 or 1) under BASE_STORAGE_DIR/<userId>/<lessonName>/<noteTitle>/<filename>
    saved_filenames = []
    if files:
        for f in files:
            filename = secure_filename(f.filename)
            if not filename:
                continue
            note_dir = (
                BASE_STORAGE_DIR
                / str(user_id)
                / str(lessonName)
                / str(title or "Untitled")
            )
            note_dir.mkdir(parents=True, exist_ok=True)
            file_path = note_dir / filename
            f.save(str(file_path))
            saved_filenames.append(filename)

    # Record note with sanitized filenames
    note = storage.add_note(
        title or "Untitled",
        lessonName,
        tags=tags,
        files=saved_filenames,
        user_id=user_id,
    )

    return jsonify({"success": True, "note": note, "saved_files": saved_filenames})


@app.route("/auth/login", methods=["POST"])
def auth_login():
    # Accept JSON or form
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    user = storage.find_user_by_credentials(username, password)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"success": True, "user": user})


@app.route("/auth/register", methods=["POST"])
def auth_register():
    # Accept JSON or form
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email and password required"}), 400

    created = storage.add_user(username, email, password)
    if not created:
        return jsonify({"error": "username or email already exists"}), 409
    return jsonify({"success": True, "user": created}), 201


@app.route("/notes/files", methods=["GET"])
def get_note_files():
    # Parameters: userId, lessonName (course name), noteName
    user_id = request.args.get("userId")
    lessonName = request.args.get("lessonName")
    noteName = request.args.get("noteName")

    if not user_id or not lessonName or not noteName:
        return jsonify({"error": "userId, lessonName and noteName are required"}), 400

    # verify user exists
    user = storage.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    # find course in user's courses
    course = None
    for c in user.get("courses", []):
        if c.get("name") == lessonName:
            course = c
            break
    if course is None:
        return jsonify({"error": "course not found for user"}), 404

    # find note in course.myNotes
    note_entry = None
    for n in course.get("myNotes", []):
        if n.get("name") == noteName:
            note_entry = n
            break
    if note_entry is None:
        return jsonify({"error": "note not found in this course for user"}), 404

    # 收集已保存的文件列表：兼容 file 为字符串、列表或 None
    saved_files = []
    file_field = note_entry.get("file")
    if isinstance(file_field, list):
        saved_files.extend([f for f in file_field if f])
    elif isinstance(file_field, str) and file_field:
        saved_files.append(file_field)
    # 其他类型（None/空）则保持为空列表，后续将返回空文件数组

    files_info = []
    for fname in saved_files:
        # build a URL to download via the secured endpoint /notes/file
        file_url = (
            f"{LocalHost}"
            + url_for("download_note_file", _external=False)
            + f"?userId={user_id}&lessonName={lessonName}&noteName={noteName}&filename={fname}"
        )
        files_info.append({"name": fname, "url": file_url})

    return jsonify({"success": True, "files": files_info})


@app.route("/notes/file", methods=["GET"])
def download_note_file():
    # Parameters: userId, lessonName, noteName, filename
    user_id = request.args.get("userId")
    lessonName = request.args.get("lessonName")
    noteName = request.args.get("noteName")
    filename = request.args.get("filename")
    print("Download request:", user_id, lessonName, noteName, filename)

    if not user_id or not lessonName or not noteName or not filename:
        return (
            jsonify(
                {"error": "userId, lessonName, noteName and filename are required"}
            ),
            400,
        )

    # verify user exists
    user = storage.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    print(user_id, lessonName, noteName, filename)
    # verify note belongs to user/course
    course = None
    for c in user.get("courses", []):
        if c.get("name") == lessonName:
            course = c
            break
    if course is None:
        return jsonify({"error": "course not found for user"}), 404

    note_entry = None
    for n in course.get("myNotes", []):
        if n.get("name") == noteName:
            note_entry = n
            break
    if note_entry is None:
        return jsonify({"error": "note not found in this course for user"}), 404

    # check that filename is among saved files
    saved_files = []
    file_field = note_entry.get("file")
    if isinstance(file_field, list):
        saved_files.extend([f for f in file_field if f])
    elif isinstance(file_field, str) and file_field:
        saved_files.append(file_field)

    if filename not in saved_files:
        return jsonify({"error": "file not associated with specified note"}), 404

    # serve file from uploads directory

    directory = BASE_STORAGE_DIR / str(user_id) / str(lessonName) / str(noteName)
    try:
        return send_from_directory(str(directory), filename, as_attachment=False)
    except Exception:
        return jsonify({"error": "file not found on server"}), 404


@app.route("/cloud", methods=["POST"])
def cloud_status():
    global _courses

    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    userId = data.get("userId")
    xuehao = data.get("xuehao")
    password = data.get("password")
    course = data.get("course")  # currently unused
    print(f"UserId:{userId},xuehao:{xuehao}, password:{password}, course:{course}")

    if not userId or not xuehao or not password:
        return (
            jsonify({"success": False, "error": "userId, xuehao和password均为必填"}),
            400,
        )

    # 先获取课程列表，course为空即为需要爬取所有课程名字
    if course == None or course == "":
        session = get_session(xuehao, password)
        # sample_courses = [{'id': 1, 'name': '计算机网络'}, {'id': 2, 'name': '操作系统'}] # 示例课程列表
        courses = spider.get_current_semester_course_list(session)
        _courses = courses
        return (
            jsonify(
                {
                    "success": True,
                    "message": "课程为空，准备爬取所有课程",
                    "courses": courses,
                }
            ),
            200,
        )
    # course不为空，爬取指定课程，返回的course是课程ID
    else:
        # 先下载
        downloaded_files = spider.download_handouts_for_course(
            _session,
            course_id=course,
            section_names=["课程讲义", "课程文件"],
            max_files=3,
            download_root="uploads",
        )  # section_names 想加啥加啥

        # 使用 storage.add_course 创建课程
        course_title = _courses[course - 1]["name"]
        course_tags = ["课程文件", "教学内容"]
        course = storage.add_course(course_title, course_tags, userId)
        if not course:
            print(f"课程 '{course_title}' 可能已存在")

        # 我看不懂下面这段在干嘛
        results = []
        for info in downloaded_files:
            # 提取文件名和笔记标题
            file_path = info.get("path")
            note_title = info.get("name") or ""

            # 创建笔记目录：uploads/userId/course_title/note_title/
            note_dir = BASE_STORAGE_DIR / str(userId) / course_title / note_title
            note_dir.mkdir(parents=True, exist_ok=True)

            # 复制文件到笔记目录
            file_name = os.path.basename(file_path)
            dest_path = note_dir / file_name
            import shutil

            shutil.copy2(file_path, dest_path)

            # 使用 storage.add_note 创建笔记
            # 参数对应数据库字段：
            # - title -> notes.name (笔记标题)
            # - lessonName -> courses.title (通过course_id关联)
            # - files -> notes.file (文件名)
            note = storage.add_note(
                title=note_title,  # 对应 notes.name
                lessonName=course_title,  # 对应 courses.title
                tags=["软工"],  # 笔记标签
                files=[file_name],  # 对应 notes.file (存储文件名)
                user_id=userId,
            )

            if note:
                results.append(
                    {
                        "note_name": note_title,  # 对应 notes.name
                        "file_name": file_name,  # 对应 notes.file
                        "course_title": course_title,  # 对应 courses.title
                        "status": "success",
                        "note_id": note.get("id"),
                    }
                )
                print(f"✓ 成功创建笔记: {note_title}, 文件: {file_name}")
            else:
                results.append(
                    {
                        "note_name": note_title,
                        "file_name": file_name,
                        "course_title": course_title,
                        "status": "failed",
                    }
                )
                print(f"✗ 创建笔记失败: {note_title}")

        # 最后返回信息
        return (
            jsonify(
                {"success": True, "message": f"准备爬取课程: {course}", "courses": []}
            ),
            200,
        )


@app.route("/edit/course", methods=["POST"])
def editCourse():
    """
    修改课程名称
    需要参数：userId, oldname, newname
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values
    
    userId = data.get("userId")
    oldname = data.get("oldname")
    newname = data.get("newname")

    if not userId or not oldname or not newname:
        return jsonify({"success": False, "error": "userId, oldname, newname 均为必填"}), 400

    result = storage.edit_course(userId, oldname, newname)
    
    if "error" in result:
        return jsonify({"success": False, "error": result["error"]}), 400
    
    return jsonify({"success": True, "message": "课程名称修改成功"}), 200


@app.route("/edit/note", methods=["POST"])
def editNote():
    """
    修改笔记名称
    需要参数：userId, courseName, oldname, newname
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values
    
    userId = data.get("userId")
    courseName = data.get("courseName")
    oldname = data.get("oldname")
    newname = data.get("newname")

    if not userId or not courseName or not oldname or not newname:
        return jsonify({"success": False, "error": "userId, courseName, oldname, newname 均为必填"}), 400

    result = storage.edit_note(userId, courseName, oldname, newname)
    
    if "error" in result:
        return jsonify({"success": False, "error": result["error"]}), 400
    
    return jsonify({"success": True, "message": "笔记名称修改成功"}), 200

# 常用链接相关接口
@app.route("/links/categories", methods=["POST"])
def create_link_category():
    """
    创建链接分类
    需要参数：userId, category, icon, sortOrder(可选)
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values
    
    userId = data.get("userId")
    category = data.get("category")
    icon = data.get("icon")
    sort_order = data.get("sortOrder", 0)

    if not userId or not category or not icon:
        return jsonify({"success": False, "error": "userId, category, icon 均为必填"}), 400

    new_category = storage.add_link_category(userId, category, icon, sort_order)
    
    if not new_category:
        return jsonify({"success": False, "error": "创建分类失败"}), 500
    
    return jsonify({"success": True, "category": new_category}), 201


@app.route("/links", methods=["POST"])
def create_link():
    """
    创建常用链接
    需要参数：userId, categoryId, name, url, description(可选), isTrusted(可选), sortOrder(可选)
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values
    
    userId = data.get("userId")
    category_id = data.get("categoryId")
    name = data.get("name")
    url = data.get("url")
    description = data.get("description", "")
    is_trusted = data.get("isTrusted", False)
    sort_order = data.get("sortOrder", 0)

    if not userId or not category_id or not name or not url:
        return jsonify({"success": False, "error": "userId, categoryId, name, url 均为必填"}), 400

    new_link = storage.add_useful_link(userId, category_id, name, url, description, is_trusted, sort_order)
    
    if not new_link:
        return jsonify({"success": False, "error": "创建链接失败"}), 500
    
    return jsonify({"success": True, "link": new_link}), 201


@app.route("/links", methods=["GET"])
def get_links():
    """
    获取用户的所有链接（按分类组织）
    需要参数：userId
    """
    userId = request.args.get("userId")
    
    if not userId:
        return jsonify({"success": False, "error": "userId 为必填"}), 400

    links_by_category = storage.get_useful_links_by_category(userId)
    
    return jsonify({"success": True, "categories": links_by_category}), 200


@app.route("/links/categories/<int:category_id>", methods=["DELETE"])
def delete_link_category(category_id):
    """
    删除链接分类
    需要参数：userId
    """
    userId = request.args.get("userId")
    
    if not userId:
        return jsonify({"success": False, "error": "userId 为必填"}), 400

    success = storage.delete_link_category(userId, category_id)
    
    if not success:
        return jsonify({"success": False, "error": "删除分类失败"}), 400
    
    return jsonify({"success": True, "message": "分类删除成功"}), 200


@app.route("/links/<int:link_id>", methods=["DELETE"])
def delete_link(link_id):
    """
    删除常用链接
    需要参数：userId
    """
    userId = request.args.get("userId")
    
    if not userId:
        return jsonify({"success": False, "error": "userId 为必填"}), 400

    success = storage.delete_useful_link(userId, link_id)
    
    if not success:
        return jsonify({"success": False, "error": "删除链接失败"}), 400
    
    return jsonify({"success": True, "message": "链接删除成功"}), 200


# 任务管理相关接口
@app.route("/tasks", methods=["POST"])
def create_task():
    """
    创建任务
    需要参数：userId, title, description(可选), deadline, priority(可选)
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values
    
    userId = data.get("userId")
    title = data.get("title")
    description = data.get("description", "")
    deadline = data.get("deadline")
    priority = data.get("priority", 1)

    if not userId or not title or not deadline:
        return jsonify({"success": False, "error": "userId, title, deadline 均为必填"}), 400

    new_task = storage.add_task(userId, title, description, deadline, priority)
    
    if not new_task:
        return jsonify({"success": False, "error": "创建任务失败"}), 500
    
    return jsonify({"success": True, "task": new_task}), 201


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    获取用户的任务列表
    需要参数：userId
    """
    userId = request.args.get("userId")
    
    if not userId:
        return jsonify({"success": False, "error": "userId 为必填"}), 400

    tasks = storage.get_tasks(userId)
    
    return jsonify({"success": True, "tasks": tasks}), 200


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """
    更新任务信息
    需要参数：userId, 以及要更新的字段（title, description, deadline, priority, completed）
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values
    
    userId = data.get("userId")
    
    if not userId:
        return jsonify({"success": False, "error": "userId 为必填"}), 400

    # 提取可更新的字段
    updates = {}
    for field in ['title', 'description', 'deadline', 'priority', 'completed']:
        if field in data:
            updates[field] = data[field]

    if not updates:
        return jsonify({"success": False, "error": "没有提供要更新的字段"}), 400

    success = storage.update_task(userId, task_id, **updates)
    
    if not success:
        return jsonify({"success": False, "error": "更新任务失败"}), 400
    
    return jsonify({"success": True, "message": "任务更新成功"}), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    删除任务
    需要参数：userId
    """
    userId = request.args.get("userId")
    
    if not userId:
        return jsonify({"success": False, "error": "userId 为必填"}), 400

    success = storage.delete_task(userId, task_id)
    
    if not success:
        return jsonify({"success": False, "error": "删除任务失败"}), 400
    
    return jsonify({"success": True, "message": "任务删除成功"}), 200

@app.route("/edit/deadline", methods=["POST"])
def updateDeadline():
    """
    更新用户的DDL列表
    需要参数：userId, deadlines（任务对象列表）
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    userId = data.get("UserId")
    deadlines = data.get("deadlines")
    print(userId, deadlines)
    if not userId or not deadlines:
        return jsonify({"success": False, "error": "userId 和 deadlines 均为必填"}), 400

    success = storage.update_deadlines(userId, deadlines)
    
    if not success:
        return jsonify({"success": False, "error": "更新DDL列表失败"}), 500
    
    return jsonify({"success": True, "message": "DDL列表更新成功"}), 200

@app.route("/edit/linkcategory", methods=["POST"])
def updateLinkCategory():
    """
    更新用户的链接分类列表
    需要参数：userId, linkCategories（列表）
    """
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    userId = data.get("userId")
    linkCategories = data.get("linkCategories")

    """ TODO:
    更改用户的链接分类
    YOU CODE HERE
    """
    
    # 如果成功更新，示例返回 
    return jsonify({"success": True, "message": "Link categories updated"}), 200

if __name__ == "__main__":
    # Run on port 4000
    app.run(host="0.0.0.0", port=4000, debug=True)
