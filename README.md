# PKU-Intelligence--2025

PKU 智慧助手 (PKU-Intelligence) 是一个集成了课程管理、笔记记录、文件存储和爬虫功能的综合性 Web 应用。

## 项目架构

本项目采用前后端分离架构：

- **前端**: Vue 3 + Vite + Tailwind CSS
- **后端**: Flask + SQLite
- **爬虫**: Python (Selenium + BeautifulSoup)
```shell
python seed.py
```

### 目录结构

```
PKU-Intelligence--2025/
├── backend/                # 后端代码
│   ├── app.py              # Flask 应用入口
│   ├── database/           # 数据库模块
│   ├── spider/             # 爬虫模块
│   └── uploads/            # 文件存储目录
├── frontend/               # 前端代码
│   ├── src/                # Vue 源码
│   └── vite.config.js      # Vite 配置
├── docs/                   # 文档
└── README.md               # 项目说明
```

## 启动

### 环境要求

- Node.js (v20+)
- Python (v3.8+)

### 后端启动

1. 进入后端目录:
   ```bash
   cd backend
   ```
2. 创建环境(optional)
   ```bash
   uv venv --python 3.12
   # 启动环境
   .venv\Scripts\activate # windows
   source .venv/bin/activate # Mac&Linux
   ```
  
3. 安装依赖:
   ```bash
   (uv) pip install -r requirements.txt
   ```
4. (可选) 创建模拟数据。注：会自动运行clear.py删除旧数据
   ```bash
   python seed.py
   uv run seed.py # uv
   ```
5. 启动 Flask 服务:
   ```bash
   python app.py
   uv run app.py # uv
   ```
   服务将运行在 `http://localhost:4000`
6. 启动AI chat 服务
   ```bash
   python chatapp.py
   uv run chatapp.py # uv
   ```

### 前端启动

1. 进入前端目录:
   ```bash
   cd frontend
   ```
2. 安装依赖:
   ```bash
   npm install
   ```
3. 启动开发服务器:
   ```bash
   npm run dev
   ```
   访问 `http://localhost:8081`

## 测试
### 前端测试(目前实现了对Note.vue 和 Links.vue 的单元测试)
1. 进入前端目录:
   ```bash
   cd frontend
   ```
2. 运行测试:
   ```bash
   npm run test
   ```
### 后端测试
1. 进入总目录：
    ```bash
   cd PKU-Intelligence--2025
   ```
2. 运行测试：
    ```bash
   python -m pytest -q
   ```
3. 测试内容：
    #### tests/test_basic.py
    - 注册 / 登录：成功、缺字段 400、冲突 409、无效登录 401/400  
    - userdata：admin 正常；不存在用户 404  
    - 课程创建：创建后能在 userdata 中看到  

    #### tests/test_cloud.py
    - /cloud 校验：缺必填字段 400；course 非整数 400  
    - course 为空：并发同步课表 + 返回课程列表  
    - course 非空：下载课件 + 解析 DDL，校验 notes/deadlines 结构  

    #### tests/test_tasks.py
    - /edit/deadline：正常更新、缺 userId/空列表 400、幂等  
    - 课表：完整 CRUD、必填校验 400、跨用户隔离、无效 id 更新/删除 400  

    #### tests/test_notes.py
    - 上传笔记：缺字段 400、多文件 400、无课程返回 note=None  
    - 上传 → 列表 → 下载 happy path  
    - /notes/files：不存在课程 404  
    - 重命名文件期望（当前未实现，xfail）  
    - 链接：创建/列出/删除；缺字段 400；跨用户隔离  




## 代码规范

本项目遵循严格的代码风格规范。详细信息请参考 [CONTRIBUTING.md](./CONTRIBUTING.md)。

- **前端**: 使用 Prettier 格式化。
- **后端**: 使用 Black 和 isort 格式化。

## 功能特性

- **用户认证**: 注册、登录
- **课程管理**: 创建课程、标签管理
- **笔记系统**: 课程关联笔记、文件上传与预览
- **云端同步**: 集成爬虫功能，自动抓取课程资料

## 实现细节

- **数据库**: SQLite，默认位置 `/backend/database/database.db`
- **文件存储**: 上传的文件位于 `/backend/uploads/` 目录下，结构为 `userid/course_name/notename/filename`
- **文件预览**: 目前前端预览支持 PDF 和 TXT 文件。

## 贡献

欢迎提交 Pull Request！请确保在提交前运行格式化命令。

---
© 2025 PKU-Intelligence Team
