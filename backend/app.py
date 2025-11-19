from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
from pathlib import Path
import os
from werkzeug.utils import secure_filename
from database import storage
import dotenv
import spider.spider as spider
dotenv.load_dotenv()
LocalHost = os.getenv('localhost') or ''
# Resolve and ensure the base storage directory exists
BASE_STORAGE_DIR = Path(os.getenv('storage_dir', './uploads/')).resolve()
BASE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
CORS(app)


@app.route('/userdata', methods=['GET'])
def userdata():
    user_id = request.args.get('id', 1)
    user = storage.get_user(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    # Return user data with courses
    return jsonify({'data': user})


@app.route('/courses/create', methods=['POST'])
def create_course():
    # Accept JSON or form-data
    data = None
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form or request.values or {}

    title = data.get('title') or data.get('name')

    # tags may be sent as an array (from JSON) or as a JSON string (from form)
    tags = []
    tags_raw = data.get('tags')
    if isinstance(tags_raw, list):
        tags = tags_raw
    else:
        try:
            import json as _json
            tags = _json.loads(tags_raw) if isinstance(tags_raw, str) else (tags_raw or [])
        except Exception:
            tags = []

    if not title:
        return jsonify({'error': 'title required'}), 400

    # optional userId to attach course to specific user
    user_id = data.get('userId') or None
    course = storage.add_course(title, tags, user_id)

    if not course:
        return jsonify({'error': 'failed to create course'}), 500
    
    return jsonify({'success': True, 'course': course})


@app.route('/notes/upload', methods=['POST'])
def upload_note():
    title = request.form.get('title') or request.values.get('title')
    lessonName = request.form.get('lessonName') or request.form.get('lesson') or request.values.get('lessonName')
    tags_raw = request.form.get('tags') or '[]'
    user_id = request.form.get('userId') or request.values.get('userId')
    try:
        import json
        tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
    except Exception:
        tags = []

    files = request.files.getlist('files') or []
    # enforce at most one file per note
    if len(files) > 1:
        return jsonify({'error': '每个笔记只允许上传一个文件'}), 400
    # require lessonName (course name) and user_id to be present
    if not lessonName:
        return jsonify({'error': 'lessonName (课程名) is required'}), 400
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400

    # Save file (0 or 1) under BASE_STORAGE_DIR/<userId>/<lessonName>/<noteTitle>/<filename>
    saved_filenames = []
    if files:
        for f in files:
            filename = secure_filename(f.filename)
            if not filename:
                continue
            note_dir = BASE_STORAGE_DIR / str(user_id) / str(lessonName) / str(title or 'Untitled')
            note_dir.mkdir(parents=True, exist_ok=True)
            file_path = note_dir / filename
            f.save(str(file_path))
            saved_filenames.append(filename)

    # Record note with sanitized filenames
    note = storage.add_note(title or 'Untitled', lessonName, tags=tags, files=saved_filenames, user_id=user_id)

    return jsonify({'success': True, 'note': note, 'saved_files': saved_filenames})


@app.route('/auth/login', methods=['POST'])
def auth_login():
    # Accept JSON or form
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400

    user = storage.find_user_by_credentials(username, password)
    if not user:
        return jsonify({'error': 'invalid credentials'}), 401
    return jsonify({'success': True, 'user': user})


@app.route('/auth/register', methods=['POST'])
def auth_register():
    # Accept JSON or form
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password required'}), 400

    created = storage.add_user(username, email, password)
    if not created:
        return jsonify({'error': 'username or email already exists'}), 409
    return jsonify({'success': True, 'user': created}), 201


@app.route('/notes/files', methods=['GET'])
def get_note_files():
    # Parameters: userId, lessonName (course name), noteName
    user_id = request.args.get('userId')
    lessonName = request.args.get('lessonName')
    noteName = request.args.get('noteName')

    if not user_id or not lessonName or not noteName:
        return jsonify({'error': 'userId, lessonName and noteName are required'}), 400

    # verify user exists
    user = storage.get_user(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404

    # find course in user's courses
    course = None
    for c in user.get('courses', []):
        if c.get('name') == lessonName:
            course = c
            break
    if course is None:
        return jsonify({'error': 'course not found for user'}), 404

    # find note in course.myNotes
    note_entry = None
    for n in course.get('myNotes', []):
        if n.get('name') == noteName:
            note_entry = n
            break
    if note_entry is None:
        return jsonify({'error': 'note not found in this course for user'}), 404

    # 收集已保存的文件列表：兼容 file 为字符串、列表或 None
    saved_files = []
    file_field = note_entry.get('file')
    if isinstance(file_field, list):
        saved_files.extend([f for f in file_field if f])
    elif isinstance(file_field, str) and file_field:
        saved_files.append(file_field)
    # 其他类型（None/空）则保持为空列表，后续将返回空文件数组

    files_info = []
    for fname in saved_files:
        # build a URL to download via the secured endpoint /notes/file
        file_url = f"{LocalHost}" + url_for('download_note_file', _external=False) + f"?userId={user_id}&lessonName={lessonName}&noteName={noteName}&filename={fname}"
        files_info.append({'name': fname, 'url': file_url})

    return jsonify({'success': True, 'files': files_info})


@app.route('/notes/file', methods=['GET'])
def download_note_file():
    # Parameters: userId, lessonName, noteName, filename
    user_id = request.args.get('userId')
    lessonName = request.args.get('lessonName')
    noteName = request.args.get('noteName')
    filename = request.args.get('filename')
    print("Download request:", user_id, lessonName, noteName, filename)

    if not user_id or not lessonName or not noteName or not filename:
        return jsonify({'error': 'userId, lessonName, noteName and filename are required'}), 400

    # verify user exists
    user = storage.get_user(user_id)    
    if not user:
        return jsonify({'error': 'user not found'}), 404

    print(user_id, lessonName, noteName, filename)
    # verify note belongs to user/course
    course = None
    for c in user.get('courses', []):
        if c.get('name') == lessonName:
            course = c
            break
    if course is None:
        return jsonify({'error': 'course not found for user'}), 404

    note_entry = None
    for n in course.get('myNotes', []):
        if n.get('name') == noteName:
            note_entry = n
            break
    if note_entry is None:
        return jsonify({'error': 'note not found in this course for user'}), 404

    # check that filename is among saved files
    saved_files = []
    file_field = note_entry.get('file')
    if isinstance(file_field, list):
        saved_files.extend([f for f in file_field if f])
    elif isinstance(file_field, str) and file_field:
        saved_files.append(file_field)

    if filename not in saved_files:
        return jsonify({'error': 'file not associated with specified note'}), 404

    # serve file from uploads directory

    directory = BASE_STORAGE_DIR / str(user_id) / str(lessonName) / str(noteName)
    try:
        return send_from_directory(str(directory), filename, as_attachment=False)
    except Exception:
        return jsonify({'error': 'file not found on server'}), 404

@app.route('/cloud', methods=['POST'])
def cloud_status():
    data = None
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form or request.values

    userId = data.get('userId')
    xuehao = data.get('xuehao')
    password = data.get('password')
    course = data.get('course')  # currently unused
    print(f"UserId:{userId},xuehao:{xuehao}, password:{password}, course:{course}")
    
    if not userId or not xuehao or not password:
        return jsonify({'success': False, 'error': 'userId, xuehao和password均为必填'}), 400

    # 先获取课程列表，course为空即为需要爬取所有课程名字
    if course == None or course == '':
        sample_courses = [{'id': 1, 'name': '计算机网络'}, {'id': 2, 'name': '操作系统'}] # 示例课程列表
        return jsonify({'success': True, 'message': '课程为空，准备爬取所有课程', 'courses': sample_courses}), 200
    # course不为空，爬取指定课程，返回的course是课程ID
    else:
        return jsonify({'success': True, 'message': f'准备爬取课程: {course}', 'courses': []}), 200
    # try:
    #     # 1. 验证用户是否存在
    #     user = storage.get_user(userId)
    #     if not user:
    #         return jsonify({'success': False, 'error': '用户不存在'}), 404

    #     # 2. 更新爬虫凭证并运行爬虫
    #     import spider.login as login_module
    #     login_module.PKU_USERNAME = xuehao
    #     login_module.PKU_PASSWORD = password
        
    #     session = login_module.pku_login_and_get_session(xuehao, password, login_module.COURSE_BASE_URL)
    #     if not session:
    #         return jsonify({'success': False, 'error': '登录课程网站失败，请检查学号和密码'}), 401

    #     # 3. 运行爬虫下载文件
    #     downloaded_files,course_name = spider.start_spidering()
        
    #     if not downloaded_files:
    #         return jsonify({
    #             'success': True, 
    #             'message': '爬虫已运行，但没有下载到任何文件',
    #             'downloaded_files': []
    #         }), 200

    #     # 4. 为爬虫文件创建统一的课程
    #     course_title = course_name
    #     course_tags = ["自动爬取"]
        
    #     # 使用 storage.add_course 创建课程
    #     course = storage.add_course(course_title, course_tags, userId)
    #     if not course:
    #         print(f"课程 '{course_title}' 可能已存在")

    #     # 5. 为每个文件创建笔记记录
    #     results = []
    #     for file_path in downloaded_files:
    #         # 提取文件名和笔记标题
    #         file_name = os.path.basename(file_path)
    #         note_title = os.path.splitext(file_name)[0]  # 去掉扩展名作为笔记标题
            
    #         # 创建笔记目录：uploads/userId/course_title/note_title/
    #         note_dir = BASE_STORAGE_DIR / str(userId) / course_title / note_title
    #         note_dir.mkdir(parents=True, exist_ok=True)
            
    #         # 复制文件到笔记目录
    #         dest_path = note_dir / file_name
    #         import shutil
    #         shutil.copy2(file_path, dest_path)
            
    #         # 使用 storage.add_note 创建笔记
    #         # 参数对应数据库字段：
    #         # - title -> notes.name (笔记标题)
    #         # - lessonName -> courses.title (通过course_id关联)
    #         # - files -> notes.file (文件名)
    #         note = storage.add_note(
    #             title=note_title,        # 对应 notes.name
    #             lessonName=course_title, # 对应 courses.title
    #             tags=["爬虫文件"],       # 笔记标签
    #             files=[file_name],       # 对应 notes.file (存储文件名)
    #             user_id=userId
    #         )
            
    #         if note:
    #             results.append({
    #                 'note_name': note_title,      # 对应 notes.name
    #                 'file_name': file_name,       # 对应 notes.file
    #                 'course_title': course_title, # 对应 courses.title
    #                 'status': 'success',
    #                 'note_id': note.get('id')
    #             })
    #             print(f"✓ 成功创建笔记: {note_title}, 文件: {file_name}")
    #         else:
    #             results.append({
    #                 'note_name': note_title,
    #                 'file_name': file_name, 
    #                 'course_title': course_title,
    #                 'status': 'failed'
    #             })
    #             print(f"✗ 创建笔记失败: {note_title}")

    #     # 6. 验证存储结果
    #     updated_user = storage.get_user(userId)
    #     if updated_user:
    #         # 检查课程是否创建成功
    #         for course in updated_user.get('courses', []):
    #             if course.get('name') == course_title:
    #                 print(f"课程 '{course_title}' 创建成功，包含 {len(course.get('myNotes', []))} 个笔记")
    #                 for note in course.get('myNotes', []):
    #                     print(f"  - 笔记: {note.get('name')}, 文件: {note.get('file')}")

    #     return jsonify({
    #         'success': True, 
    #         'message': f'爬虫完成，成功存储 {len([r for r in results if r["status"] == "success"])} 个文件',
    #         'storage_info': {
    #             'course_created': course_title,
    #             'notes_count': len([r for r in results if r["status"] == "success"]),
    #             'storage_path': f"uploads/{userId}/{course_title}/"
    #         },
    #         'results': results
    #     }), 200

    # except Exception as e:
    #     print(f"cloud_status 过程出错: {e}")
    #     import traceback
    #     traceback.print_exc()
        
    #     return jsonify({
    #         'success': False, 
    #         'error': f'处理过程中发生错误: {str(e)}'
    #     }), 500







if __name__ == '__main__':
    # Run on port 4000
    app.run(host='0.0.0.0', port=4000, debug=True)
