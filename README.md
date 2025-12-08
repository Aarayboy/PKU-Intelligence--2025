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
