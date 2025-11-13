# 前端

### 环境

运行
```
npm install
npm run dev
```

##### 关于tailwind

目前应该可以自由使用tailwind css，如果不想使用，正常写css即可

### 数据结构说明

UserData类：

```javaScript
class UserData {
  constructor(id, email, username, courses = []) {
    this.id = id;
    this.email = email;
    this.username = username;
    this.courses = courses;         // 用户下的课程:List[MyCourse]
  }
}
``` 

MyCourse类：表示课程

```javaScript
class MyCourse {
  constructor(name, tags, myNotes=[]) {
    this.name = name;               // 课程名字:String
    this.tags = tags;               // 课程Tags:List[String]
    this.myNotes = myNotes;         // 课程下的笔记:List[MyNote]
  }
}
```

MyNote类：表示笔记

```javaScript
class MyNote {
  constructor(name, file, lessonName) {
    this.name = name;               // 笔记名字:String
    this.file = file;               // 笔记文件名:String
    this.lessonName = lessonName;   // 笔记对应课程名字: String
  }
}
```

### 请求
以下为当前前端中使用到的主要接口请求格式（基于 `frontend/src/api/index.js` 的实现），便于与后端对齐与联调。

注意：默认后端基本地址由 Vite 环境变量 `VITE_API_BASE` 提供，开发时通常为 `http://localhost:4000`。

---

#### 1) 获取用户数据

- Method: GET
- URL: /userdata?id=<userId>
- Headers: Accept: application/json
- Body: 无

响应示例（实际后端返回结构为 { data: user }）：

```json
{
  "data": {
    "id": "1",
    "username": "alice",
    "email": "alice@example.com",
    "courses": [
      {
        "name": "线性代数",
        "tags": ["代数","必修"],
        "myNotes": [
          { "name": "笔记1", "file": "note-1.pdf", "lessonName": "线性代数" }
        ]
      }
    ]
  }
}
```

错误处理：非 2xx 时前端会尝试读取响应文本作为错误详情并抛出异常。

---

#### 2) 创建课程（推荐 JSON）

- Method: POST
- URL: /courses/create
- Headers: Content-Type: application/json
- Body (JSON):

```json
{
  "title": "新课程名称",
  "tags": ["tag1", "tag2"],
  "userId": "1"   // 可选，后端会将课程关联到该用户
}
```

后端仍向后兼容 form-data，但前端现在默认以 JSON 发送。响应示例：

```json
{ "success": true, "course": { "id": "c1", "name": "新课程名称", "tags": ["tag1"] } }
```

示例 curl：

```bash
curl -X POST http://localhost:4000/courses/create \
  -H "Content-Type: application/json" \
  -d '{"title":"新课程","tags":["a","b"],"userId":"1"}'
```

---

#### 3) 上传笔记（包含单文件，使用 FormData）

- Method: POST
- URL: /notes/upload
- Headers: 不要手动设置 `Content-Type`（浏览器会处理 boundary）
- Body: multipart/form-data（FormData 字段）
  - title: string（可选，后端默认 'Untitled'）
  - lessonName: string（必须，表示课程名，后端会把笔记关联到该课程）
  - tags: JSON 字符串或数组（前端会使用 JSON.stringify 发送字符串）
  - files: File（仅允许 0 或 1 个文件；当有文件时把该文件保存为笔记附件）
  - userId: string|number（必须，用于把笔记关联到某用户；生产环境应改为基于认证的用户识别）

请求数据（前端封装）：

```js
// 调用 api.uploadNote
api.uploadNote({
  title: '第1章笔记',
  lessonName: '线性代数', // 必填
  tags: ['代数'],
  files: [ FileObject ] , // 可选，数组但长度 <= 1
  userId: '1' // 必填
})
```

响应（成功示例）：

```json
{
  "success": true,
  "note": { "id": 123, "name": "第1章笔记", "lessonName": "线性代数" },
  "saved_files": ["note-1.pdf"]
}
```

常见错误行为与注意事项：
- 后端对多文件上传会返回 400（项目约束：每个笔记最多包含 1 个文件）。
- 前端 `uploadNote` 在调用前会做简单校验（确保 `lessonName` 与 `userId` 存在，且文件数量 <= 1）。
- 上传大文件可能触发默认超时（request 默认 15000ms），需要时可扩展 API 以支持自定义 timeout。

---

#### 4) 获取笔记的已保存文件列表（用于 iframe 预览 / 列表展示）

- Method: GET
- URL: /notes/files?userId=<userId>&lessonName=<lessonName>&noteName=<noteName>
- Headers: Accept: application/json
- Body: 无

响应示例：

```json
{
  "success": true,
  "files": [
    { "name": "note-1.pdf", "url": "/notes/file?userId=1&lessonName=线性代数&noteName=笔记1&filename=note-1.pdf" }
  ]
}
```

说明：返回的 `url` 可用于直接设置在 iframe 的 src 或用作下载链接；若后端和前端跨域，请确保后端允许 CORS 并且不设置阻止 iframe 的 `X-Frame-Options`。

---
<!-- 
#### 5) 获取笔记文件的访问 URL（构造器）

- 功能：前端可使用 `api.getNoteFileUrl({ userId, lessonName, noteName, filename })` 构造访问 URL，返回字符串（不发请求）。

示例返回值：
```
"http://localhost:4000/notes/file?userId=1&lessonName=线性代数&noteName=笔记1&filename=note-1.pdf"
```

用途：适合直接在 `<iframe>`、`<a href>` 等处使用（若后端允许直接访问）。

---

#### 6) 直接下载/流式获取笔记文件（用于 Blob 处理或鉴权场景）

- Method: GET
- URL: /notes/file?userId=<userId>&lessonName=<lessonName>&noteName=<noteName>&filename=<filename>
- Headers: 可携带鉴权 header（如果后端要求）
- Body: 无

说明：前端有 `api.downloadNoteFile(...)`，会通过统一的 `request()` 发起 GET；当响应不是 JSON 时 `request()` 会返回原始 Response 对象，调用方可用 `response.blob()` 或 `response.arrayBuffer()` 处理并生成 object URL，用于 `<iframe>` 或下载。

示例（保存为本地文件）：

```js
const res = await api.downloadNoteFile({ userId, lessonName, noteName, filename });
if (res instanceof Response) {
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  // 用法：设置 iframe src 或创建 <a download> 强制下载
}
```

注意：若要在 iframe 中显示 PDF 且后端需要自定义 header（如 Authorization），请使用此方法（先 fetch 为 Blob，再生成 object URL 赋值给 iframe 的 src）。

---

--- -->

#### 5) 登录

- Method: POST
- URL: /auth/login
- Headers: Content-Type: application/json
- Body (JSON): { "username": "alice", "password": "pwd" }

响应示例：
```json
{ "success": true, "user": { "id": "1", "username": "alice", "email": "alice@example.com" } }
```

---

#### 6) 注册

- Method: POST
- URL: /auth/register
- Headers: Content-Type: application/json
- Body (JSON): { "username": "bob", "email": "bob@example.com", "password": "pwd" }

响应示例：
```json
{ "success": true, "user": { "id": "2", "username": "bob", "email": "bob@example.com" } }
```

##### 需要后端为新用户创建基本数据

---

#### 通用说明

- 请求基地址由 `VITE_API_BASE` 控制（前端 `.env` 可设置为 `http://localhost:4000`）。
- 统一请求封装 `frontend/src/api/index.js` 的 `request()`：默认超时 15000ms，若响应 `Content-Type` 包含 `application/json`，会自动解析并返回 JSON；非 JSON 则返回 Response 对象。
- 错误处理：若响应非 2xx，会尝试读取响应文本作为错误详情并抛出 Error。调用端应使用 try/catch 并通过通知组件显示错误。



