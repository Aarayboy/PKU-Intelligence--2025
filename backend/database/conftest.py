"""
pytest配置文件 - 修正mock方式
"""
import pytest
import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

# 创建临时数据库
TEST_DB_PATH = Path(tempfile.mktemp(suffix='.db'))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """每个测试前设置环境"""
    # 保存原始环境变量
    original_dbfile = os.environ.get('dbfile')
    original_storage_dir = os.environ.get('storage_dir')
    
    # 设置测试环境变量
    os.environ['dbfile'] = str(TEST_DB_PATH)
    os.environ['storage_dir'] = str(TEST_DB_PATH.parent / 'test_storage')
    
    # 确保目录存在
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # 清理
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except:
            pass
    
    # 恢复环境变量
    if original_dbfile:
        os.environ['dbfile'] = original_dbfile
    else:
        os.environ.pop('dbfile', None)
    
    if original_storage_dir:
        os.environ['storage_dir'] = original_storage_dir
    else:
        os.environ.pop('storage_dir', None)

@pytest.fixture
def mock_db():
    """模拟数据库 - 正确的方式"""
    # 导入必须在设置环境变量之后
    from database import Database
    
    # 创建数据库实例
    db = Database()
    
    # 清除可能存在的旧数据
    conn = db.get_db_connection()
    cursor = conn.cursor()
    
    # 清空所有表（保持表结构）
    tables = ['users', 'courses', 'notes', 'link_categories', 
              'useful_links', 'tasks', 'course_schedules', 'course_schedule_times']
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except:
            pass  # 表可能不存在
    
    conn.commit()
    
    yield db
    
    # 测试后关闭连接
    try:
        db.close_connection()
    except:
        pass

@pytest.fixture
def test_user(mock_db):
    """创建测试用户"""
    user = mock_db.add_user("testuser", "test@example.com", "password123")
    return user

@pytest.fixture  
def test_course(mock_db, test_user):
    """创建测试课程"""
    if test_user:
        course = mock_db.add_course_to_user(
            test_user['id'], 
            "软件测试", 
            ["必修", "计算机"]
        )
        return course
    return None