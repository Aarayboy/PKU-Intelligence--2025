# Backend (Flask) — 简单本地实现

这是一个用于本地开发的最简 Flask 后端实现，不使用数据库，使用 JSON 文件存储数据，并保存上传的文件到 `backend/uploads`。

运行要求
- Python 3.8+
- flask 模块

依赖安装
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-cors
```

启动
```powershell
python app.py
```

接口说明（示例）

- GET /userdata?id=1
  - 返回：{ data: { id, username, email, courses: [...] } }

- POST /courses/create
  - 表单字段：title (string), tags (JSON 字符串)
  - 返回：{ success: true, course: {...} }

- POST /notes/upload
  - 表单字段：title, lessonName, tags (JSON 字符串)
  - 文件字段：files（可以多文件）
  - 返回：{ success: true, note: {...}, saved_files: [...] }

数据存储
- 文件：`backend/data.json`
- 上传文件目录：`backend/uploads/`

# ！！！ 目前仅用json格式储存，未采用数据库，需要后续实现
