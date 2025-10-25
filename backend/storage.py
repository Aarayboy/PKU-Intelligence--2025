import json
import threading
from pathlib import Path

DATA_FILE = Path(__file__).parent / 'data.json'

_lock = threading.Lock()

def ensure_data_file():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        # Initialize with a simple structure
        initial = {
            "users": [
                {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "courses": []
                }
            ],
            "courses": [],
            "notes": []
        }
        write_data(initial)

def read_data():
    ensure_data_file()
    with _lock:
        with DATA_FILE.open('r', encoding='utf-8') as f:
            return json.load(f)

def write_data(data):
    ensure_data_file()
    with _lock:
        with DATA_FILE.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id=1):
    data = read_data()
    for u in data.get('users', []):
        if u.get('id') == int(user_id):
            return u
    return None

def find_user_by_credentials(username_or_email, password):
    data = read_data()
    for u in data.get('users', []):
        if (u.get('username') == username_or_email or u.get('email') == username_or_email) and u.get('password') == password:
            # return a copy without password
            user_copy = {k: v for k, v in u.items() if k != 'password'}
            return user_copy
    return None

def find_user_by_username_or_email(value):
    data = read_data()
    for u in data.get('users', []):
        if u.get('username') == value or u.get('email') == value:
            return u
    return None

def add_user(username, email, password):
    data = read_data()
    # check duplicates
    if find_user_by_username_or_email(username) or find_user_by_username_or_email(email):
        return None
    next_id = max((u.get('id', 0) for u in data.get('users', [])), default=0) + 1
    user = { 'id': next_id, 'username': username, 'email': email, 'password': password, 'courses': [] }
    data.setdefault('users', []).append(user)
    write_data(data)
    user_copy = {k: v for k, v in user.items() if k != 'password'}
    return user_copy

def add_course(title, tags=None, user_id=None):
    tags = tags or []
    data = read_data()
    # simple id assignment
    next_id = max((c.get('id', 0) for c in data.get('courses', [])), default=0) + 1
    course = { 'id': next_id, 'name': title, 'tags': tags, 'myNotes': [] }
    data.setdefault('courses', []).append(course)
    # attach to specified user if provided, else to first user
    target_user = None
    if user_id is not None:
        try:
            uid = int(user_id)
            for u in data.get('users', []):
                if u.get('id') == uid:
                    target_user = u
                    break
        except Exception:
            target_user = None

    if target_user is None and data.get('users'):
        target_user = data['users'][0]

    if target_user is not None:
        target_user.setdefault('courses', []).append(course)

    write_data(data)
    return course

def add_note(title, lessonName, tags=None, files=None, saved_files=None, user_id=None):
    tags = tags or []
    files = files or []
    saved_files = saved_files or []
    data = read_data()
    next_id = max((n.get('id', 0) for n in data.get('notes', [])), default=0) + 1
    note = {
        'id': next_id,
        'name': title,
        'lessonName': lessonName,
        'tags': tags,
        'files': saved_files,
    }
    data.setdefault('notes', []).append(note)

    # find target user
    target_user = None
    if user_id is not None:
        try:
            uid = int(user_id)
            for u in data.get('users', []):
                if u.get('id') == uid:
                    target_user = u
                    break
        except Exception:
            target_user = None

    # helper to append note to a course object
    def append_note_to_course_obj(course_obj):
        course_obj.setdefault('myNotes', []).append({ 'name': title, 'file': saved_files[0] if saved_files else None, 'lessonName': lessonName })

    # 1) try to find course in target user's courses
    course_found = False
    if target_user is not None:
        for c in target_user.get('courses', []):
            if c.get('name') == lessonName:
                append_note_to_course_obj(c)
                course_found = True
                break

    # 2) if not found in user's courses, try to find in global courses and append a reference in user's courses
    if not course_found:
        for c in data.get('courses', []):
            if c.get('name') == lessonName:
                # append to global course
                append_note_to_course_obj(c)
                # also ensure user's courses include this course object (reference)
                if target_user is not None:
                    target_user.setdefault('courses', []).append(c)
                course_found = True
                break

    # 3) if still not found, create new course object and attach to user's courses (and optionally global list)
    if not course_found:
        new_course_id = max((c.get('id',0) for c in data.get('courses', [])), default=0)+1
        new_course = { 'id': new_course_id, 'name': lessonName, 'tags': [], 'myNotes': [ { 'name': title, 'file': saved_files[0] if saved_files else None, 'lessonName': lessonName } ] }
        # add to global courses
        data.setdefault('courses', []).append(new_course)
        # attach to target user if available
        if target_user is not None:
            target_user.setdefault('courses', []).append(new_course)
        course_found = True

    write_data(data)
    return note
