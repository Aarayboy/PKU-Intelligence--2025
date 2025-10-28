from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS
from pathlib import Path
import os
from werkzeug.utils import secure_filename
import storage
import dotenv
dotenv.load_dotenv()
LocalHost = os.getenv('localhost')


UPLOAD_DIR = Path(__file__).parent / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
    return jsonify({'success': True, 'course': course})


@app.route('/notes/upload', methods=['POST'])
def upload_note():
    title = request.form.get('title') or request.values.get('title')
    lessonName = request.form.get('lessonName') or request.form.get('lesson') or request.values.get('lessonName')
    tags_raw = request.form.get('tags') or '[]'
    try:
        import json
        tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
    except Exception:
        tags = []

    files = request.files.getlist('files') or []
    # enforce at most one file per note
    if len(files) > 1:
        return jsonify({'error': '每个笔记只允许上传一个文件'}), 400
    saved_files = []
    # require lessonName (course name) and user_id to be present
    user_id = request.form.get('userId') or request.values.get('userId')
    if not lessonName:
        return jsonify({'error': 'lessonName (课程名) is required'}), 400
    if not user_id:
        return jsonify({'error': 'userId is required'}), 400
    for f in files:
        filename = secure_filename(f.filename)
        if not filename:
            continue
        out_path = UPLOAD_DIR / filename
        # if name collision, append number
        base, ext = os.path.splitext(filename)
        counter = 1
        while out_path.exists():
            filename = f"{base}-{counter}{ext}"
            out_path = UPLOAD_DIR / filename
            counter += 1
        f.save(str(out_path))
        saved_files.append(str(out_path.name))

    note = storage.add_note(title or 'Untitled', lessonName, tags=tags, files=[f.filename for f in files], saved_files=saved_files, user_id=user_id)
    return jsonify({'success': True, 'note': note, 'saved_files': saved_files})


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

    # try to find matching global note to get saved files list
    data = storage.read_data()
    saved_files = []
    for n in data.get('notes', []):
        if n.get('name') == noteName and n.get('lessonName') == lessonName:
            saved_files = n.get('files', [])
            break

    # fall back to file field on course note entry
    if not saved_files and note_entry.get('file'):
        saved_files = [note_entry.get('file')]

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

    note_found = False
    for n in course.get('myNotes', []):
        if n.get('name') == noteName:
            note_found = True
            break
    if not note_found:
        return jsonify({'error': 'note not found in this course for user'}), 404

    
    # check that filename is among saved files
    data = storage.read_data()
    saved_files = []
    for n in data.get('notes', []):
        if n.get('name') == noteName and n.get('lessonName') == lessonName:
            saved_files = n.get('files', [])
            break

    if filename not in saved_files:
        # also allow the legacy course.myNotes 'file' reference
        if not any(n.get('file') == filename for n in course.get('myNotes', [])):
            return jsonify({'error': 'file not associated with specified note'}), 404

    # serve file from uploads directory
    try:
        return send_from_directory(str(UPLOAD_DIR), filename, as_attachment=False)
    except Exception:
        return jsonify({'error': 'file not found on server'}), 404


if __name__ == '__main__':
    # Run on port 4000
    app.run(host='0.0.0.0', port=4000, debug=True)
