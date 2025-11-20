# 贡献指南

感谢您对 PKU-Intelligence--2025 项目的关注！为了保持代码库的整洁和一致性，请遵循以下开发规范。

## 代码风格

本项目强制执行统一的代码风格。

### 前端 (Vue/JavaScript)

我们使用 **Prettier** 进行代码格式化。

- **配置文件**: `frontend/.prettierrc.json`
- **规范**:
  - 缩进: 2 空格
  - 语句末尾分号: 是
  - 字符串引号: 单引号
  - 尾随逗号: ES5 (对象/数组末尾)

**如何格式化:**

1. 进入前端目录: `cd frontend`
2. 安装依赖: `npm install`
3. 运行格式化命令: `npm run format`

### 后端 (Python)

我们使用 **Black** 和 **isort** 进行代码格式化。

- **Black**: 强制性的代码格式化工具，保持一致的 Python 风格。
- **isort**: 自动排序 import 导入语句。

**如何格式化:**

1. 进入后端目录: `cd backend`
2. 安装依赖: `pip install -r requirements.txt` (确保包含 black 和 isort)
3. 运行 isort: `isort .`
4. 运行 Black: `black .`

## 开发流程

1. Fork 本仓库。
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 Pull Request。

## 目录结构说明

- `frontend/`: Vue 3 前端项目
- `backend/`: Flask 后端项目


