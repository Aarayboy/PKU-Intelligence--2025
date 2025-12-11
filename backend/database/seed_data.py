"""
Seed the SQLite database with test data.

Usage:
  python seed_data.py

It will create:
- Users: admin (already ensured in schema), alice, bob
- Courses per user:
    - 高等数学 (tags: 基础, 必修)
    - 数据结构 (tags: 编程, 必修)
- Notes per course (one or two demo notes)

Database location is determined by Database() (env var 'dbfile' or default ./database/database.db).
"""

from __future__ import annotations

import json
import sqlite3
from typing import Optional

from .database import Database


def ensure_user(
    db: Database, username: str, email: str, password: str
) -> Optional[int]:
    """Create user if not exists, return user id."""
    user = db.add_user(username, email, password)
    if not user:
        # already exists -> fetch
        user = db.find_user_by_username_or_email(
            username
        ) or db.find_user_by_username_or_email(email)
    return user.get("id") if user else None


def add_note(
    db: Database, user_id: int, course_id: int, name: str, file: Optional[str] = None
) -> int:
    """Insert a note row. Returns new note id."""
    db.add_note(name, course_id, [], [file] if file else [], user_id)

def add_ddl(
    db: Database, user_id: int
) -> int:
    """Insert a deadline row. Returns new deadline id."""
    sample_deadlines = [
        {"name": "高等数学期中考试", "deadline": "2024-10-15 23:12", "message": "考试提醒", "status": 0},
        {"name": "数据结构作业1", "deadline": "2024-09-30 23:12", "message": "balabala", "status": 1},
    ]
    db.update_deadlines(user_id, sample_deadlines)


def seed():
    db = Database()

    # Users
    alice_id = ensure_user(db, "alice", "alice@example.com", "pass123")
    bob_id = ensure_user(db, "bob", "bob@example.com", "pass123")

    # Admin
    admin_id = ensure_user(db, "admin", "admin@example.com", "adminpass")

    if not alice_id or not bob_id:
        raise RuntimeError("Failed to ensure seed users")

    # Courses for Alice
    math_alice = db.add_course_to_user(alice_id, "高等数学", ["基础", "必修"])
    ds_alice = db.add_course_to_user(alice_id, "数据结构", ["编程", "必修"])

    # Courses for Bob (same titles allowed, separate rows per user)
    math_bob = db.add_course_to_user(bob_id, "高等数学", ["基础"])
    os_bob = db.add_course_to_user(bob_id, "操作系统", ["系统"])

    print(math_alice, ds_alice, math_bob, os_bob)
    # Notes for Alice

    add_note(db, alice_id, math_alice["title"], "导数与微分整理")
    add_note(db, alice_id, math_alice["title"], "极限与连续笔记")

    add_note(db, alice_id, ds_alice["title"], "栈和队列总结")

    add_note(db, bob_id, math_bob["title"], "积分与级数简记")
    add_note(db, bob_id, os_bob["title"], "进程与线程概览")

    add_ddl(db, alice_id)
    add_ddl(db, bob_id)

    # Summary
    alice_data = {}
    bob_data = {}
    alice_data = db.get_user_with_courses_and_notes(alice_id)
    bob_data = db.get_user_with_courses_and_notes(bob_id)

    alice_data["deadlines"] = db.get_tasks(alice_id)
    bob_data["deadlines"] = db.get_tasks(bob_id)

    print("Seeded data for Alice:")
    print(json.dumps(alice_data, ensure_ascii=False, indent=2))
    print("Seeded data for Bob:")
    print(json.dumps(bob_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    seed()
