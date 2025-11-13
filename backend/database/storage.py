from pathlib import Path
from .database import Database


db = Database()


def get_user(user_id=1):
    return db.get_user_with_courses_and_notes(user_id)

def find_user_by_credentials(username_or_email, password):
    return db.find_user_by_credentials(username_or_email, password)

def find_user_by_username_or_email(value):
    return db.find_user_by_username_or_email(value)

def add_user(username, email, password):
    user = db.add_user(username, email, password)
    # 返回不包含密码的用户信息
    user_copy = user.copy()
    return user_copy

def add_course(title, tags=None, user_id=None):
    tags = tags or []
    course = db.add_course_to_user(user_id, title, tags)
    if not course:
        return None
    return course

def add_note(title, lessonName, tags=None, files=None, user_id=None):
    tags = tags or []
    files = files or []
    note = db.add_note(title, lessonName, tags, files, user_id)
    return note
