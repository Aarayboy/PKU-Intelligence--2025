# backend/tests/conftest.py
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# 使用独立的临时目录隔离测试产生的数据库与文件
_TEST_ROOT = Path(tempfile.mkdtemp(prefix="pku_backend_test_"))
os.environ.setdefault("dbfile", str(_TEST_ROOT / "test.db"))
os.environ.setdefault("storage_dir", str(_TEST_ROOT / "uploads"))

from backend.app import BASE_STORAGE_DIR, app as flask_app  # noqa: E402


def _reset_storage():
    if BASE_STORAGE_DIR.exists():
        shutil.rmtree(BASE_STORAGE_DIR, ignore_errors=True)
    BASE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=True)
def _clean_state():
    """
    每个用例前清理数据库表、上传目录以及全局缓存的 session/course 列表。
    """
    from backend.database import storage  # noqa: WPS433
    import backend.app as backend_app  # noqa: WPS433

    conn = storage.db.get_db_connection()
    cursor = conn.cursor()
    cursor.executescript(
        """
        DELETE FROM notes;
        DELETE FROM courses;
        DELETE FROM link_categories;
        DELETE FROM useful_links;
        DELETE FROM tasks;
        DELETE FROM course_schedule_times;
        DELETE FROM course_schedules;
        DELETE FROM users WHERE id != 1;
        """
    )
    conn.commit()

    backend_app._session = None
    backend_app._courses = None
    _reset_storage()
    yield


@pytest.fixture
def app():
    """
    提供一个配置为 TESTING 的 Flask app。
    所有测试里如果需要 app，可以直接在参数里写 app。
    """
    flask_app.config.update(
        TESTING=True,
    )
    return flask_app


@pytest.fixture
def client(app):
    """
    Flask 提供的测试客户端，相当于一个不用真的开端口的 HTTP 客户端。
    测试里可以 client.get(...) / client.post(...).
    """
    return app.test_client()
