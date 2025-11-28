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

def edit_course(user_id, oldname, newname):
    """修改课程名称"""
    return db.edit_course(user_id, oldname, newname)


def edit_note(user_id, courseName, oldname, newname):
    """修改笔记名称"""
    return db.edit_note(user_id, courseName, oldname, newname)


# 常用链接相关方法
def add_link_category(user_id, category, icon, sort_order=0):
    """添加链接分类"""
    return db.add_link_category(user_id, category, icon, sort_order)


def get_link_categories(user_id):
    """获取用户的所有链接分类"""
    return db.get_link_categories(user_id)


def add_useful_link(user_id, category_id, name, url, description="", is_trusted=False, sort_order=0):
    """添加常用链接"""
    return db.add_useful_link(user_id, category_id, name, url, description, is_trusted, sort_order)


def get_useful_links_by_category(user_id):
    """获取用户的所有链接，按分类组织"""
    return db.get_useful_links_by_category(user_id)


def delete_link_category(user_id, category_id):
    """删除链接分类"""
    return db.delete_link_category(user_id, category_id)


def delete_useful_link(user_id, link_id):
    """删除常用链接"""
    return db.delete_useful_link(user_id, link_id)


# 任务管理相关方法
def add_task(user_id, title, description, deadline, priority=1):
    """添加任务"""
    return db.add_task(user_id, title, description, deadline, priority)


def get_tasks(user_id):
    """获取用户的任务列表"""
    return db.get_tasks(user_id)


def update_task(user_id, task_id, **updates):
    """更新任务信息"""
    return db.update_task(user_id, task_id, **updates)


def delete_task(user_id, task_id):
    """删除任务"""
    return db.delete_task(user_id, task_id)


def update_deadlines(user_id, deadlines):
    """批量更新用户的DDL列表"""
    return db.update_deadlines(user_id, deadlines)