from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import os
from werkzeug.utils import secure_filename
import storage

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
    # Accept form-data
    title = request.form.get('title') or request.form.get('name') or request.values.get('title')
    tags_raw = request.form.get('tags') or '[]'
    try:
        import json
        tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
    except Exception:
        tags = []

    if not title:
        return jsonify({'error': 'title required'}), 400

    # optional userId to attach course to specific user
    user_id = request.form.get('userId') or request.values.get('userId')
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
    saved_files = []
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

    user_id = request.form.get('userId') or request.values.get('userId')
    note = storage.add_note(title or 'Untitled', lessonName or 'Unknown', tags=tags, files=[f.filename for f in files], saved_files=saved_files, user_id=user_id)
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


if __name__ == '__main__':
    # Run on port 4000
    app.run(host='0.0.0.0', port=4000, debug=True)
