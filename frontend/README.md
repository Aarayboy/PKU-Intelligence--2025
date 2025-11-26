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
  constructor({ courses = [], username = "", userId = null, email = "", deadlines = [] } = {}) {
    this.username = username;
    this.userId = userId;
    this.email = email;
    this.courses = courses;
    this.deadlines = deadlines.map((d) =>
      new DDL(
        d?.name ?? "",
        d?.deadline ?? "",
        d?.message ?? "",
        d?.status ?? "",
      ),
    );
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

DDL 类：表示任务清单

```javaScript
class DDL{
  constructor(name="",deadline="",message="", status=""){
    this.name=name;
    this.deadline=deadline; // 格式 YYYY-MM-DD HH:mm
    this.message=message;
    this.status=status;     // 目前有两种状态： 0表示紧急， 1表示不紧急
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
    ],
    "deadlines":[
      {
        "name": "苦来西苦",
        "deadline": "2025-11-25 20:15",
        "message": "为什么要演奏春日影",
        "status": 0,
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

#### 7) 修改课程名称

- Method: POST
- URL: /edit/course
- Headers: Content-Type: application/json
- Body (JSON):

```json
{ "userId": "1", "oldname": "旧课程名", "newname": "新课程名" }
```

响应示例：

```json
{ "success": true }
```

错误示例：

```json
{ "error": "course not found" }
```

用途：将某用户拥有的课程重命名；后端需校验该课程属于该用户且新名称不与其已有课程冲突。

#### 8) 修改笔记名称

- Method: POST
- URL: /edit/note
- Headers: Content-Type: application/json
- Body (JSON):

```json
{ "userId": "1", "coursename": "所属课程名", "oldname": "旧笔记名", "newname": "新笔记名" }
```

响应示例：

```json
{ "success": true }
```

用途：重命名课程下的某个笔记。后端应同步更新存储目录（若设计为基于笔记名的目录结构）。

#### 9) 更新 DDL / 任务截止列表

- Method: POST
- URL: /edit/deadline
- Headers: Content-Type: application/json
- Body (JSON):

```json
{
  "UserId": "1",
  "deadlines": [
    { "name": "作业1", "deadline": "2025-12-01 23:59", "message": "完成第3章", "status": 0 },
    { "name": "Project Milestone", "deadline": "2025-12-15 12:00", "message": "提交原型", "status": 1 }
  ]
}
```

响应示例：

```json
{ "success": true }
```

说明：`status` 目前约定 0 表示紧急，1 表示不紧急。后端可选择：整表覆盖 / 逐条 upsert，自行实现。

#### 10) Cloud 同步 / 扩展操作

- Method: POST
- URL: /cloud
- Headers: Content-Type: application/json
- Body (JSON):

```json
{ "userId": "1", "xuehao": "学号或外部账号", "password": "凭证", "course": "课程名或标识" }
```

用途：外部云端或教务系统同步的占位接口（根据实际业务实现）。

响应示例（占位）：

```json
{ "success": true, "data": { "synced": true } }
```

错误示例：

```json
{ "error": "invalid credentials" }
```

<!-- #### 11) 构造与下载笔记文件的辅助方法（前端工具）

在 `frontend/src/api/index.js` 中还提供了纯前端辅助：

- `getNoteFileUrl({ userId, lessonName, noteName, filename })`：返回字符串形式的文件访问 URL，不直接发请求。
- `downloadNoteFile({ userId, lessonName, noteName, filename })`：发起 GET 请求，非 JSON 响应时返回原始 Response，可再 `blob()` 处理生成本地预览。

示例：

```js
const url = api.getNoteFileUrl({ userId: 1, lessonName: '线性代数', noteName: '第1章笔记', filename: 'note-1.pdf' });
// 用于 <iframe src={url}> 或 <a href={url}>

const res = await api.downloadNoteFile({ userId: 1, lessonName: '线性代数', noteName: '第1章笔记', filename: 'note-1.pdf' });
if (res instanceof Response) {
  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);
  // iframe.src = objectUrl;
}
``` -->

---

---

#### 通用说明

- 请求基地址由 `VITE_API_BASE` 控制（前端 `.env` 可设置为 `http://localhost:4000`）。
- 统一请求封装 `frontend/src/api/index.js` 的 `request()`：默认超时 15000ms，若响应 `Content-Type` 包含 `application/json`，会自动解析并返回 JSON；非 JSON 则返回 Response 对象。
- 错误处理：若响应非 2xx，会尝试读取响应文本作为错误详情并抛出 Error。调用端应使用 try/catch 并通过通知组件显示错误。



