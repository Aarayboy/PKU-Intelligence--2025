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

UserData类：暂时只有courses内容，待登陆页面完成再补全其他信息 

```javaScript
class UserData {
  constructor(courses = []) {
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

以下为当前前端中使用到的接口请求格式，便于与后端对齐与联调。

#### 1）获取用户数据

- Method: GET
- URL: https://example.com/userdata
- Headers:
  - Accept: application/json（可选，推荐）
- Body: 无

响应示例（JSON）：

```json
{
  "courses": [
    {
      "name": "课程名",
      "tags": ["标签1", "标签2"],
      "myNotes": [
        { "name": "笔记名", "file": "可选文件URL或文件名", "lessonName": "所属课程名" }
      ]
    }
  ]
}
```

错误约定：非 2xx 返回时，前端会读取 `res.text()` 作为错误详情并提示。

#### 2）上传笔记

- Method: POST
- URL: https://example.com/upload
- Headers:
  - 不手动设置 `Content-Type`，浏览器会为 `FormData` 自动设置 `multipart/form-data` 与 boundary
- Body: multipart/form-data（FormData 字段如下）
  - title: string（笔记标题）
  - tags: string（JSON 字符串化的数组，如 `"[\"tag1\",\"tag2\"]"`）
  - files: file（可多次 append 同名字段 `files` 以支持多文件）

成功响应示例（JSON，推荐）：

```json
{
  "ok": true,
  "noteId": "xxx",
  "message": "上传成功"
}
```

失败时：返回非 2xx，前端读取 `res.text()` 作为错误详情提示。

#### 3）新建课程

- Method: POST
- URL: https://example.com/upload（当前与笔记上传共用上传地址，建议后端提供更清晰的 `/courses/create`）
- Headers:
  - 同上，不手动设置 `Content-Type`
- Body: multipart/form-data（FormData 字段如下）
  - title: string（课程名称）
  - tags: string（JSON 字符串化的数组）

成功响应示例（JSON，推荐）：

```json
{
  "ok": true,
  "courseId": "yyy",
  "message": "课程创建成功"
}
```

失败时：返回非 2xx，前端读取 `res.text()` 作为错误详情提示。

#### 4）鉴权与其他说明（如需）

- 若需鉴权，可在请求头加入 `Authorization: Bearer <token>`，或使用 Cookie 携带会话。
- 跨域时需要服务端配置 CORS；如需携带 Cookie，请在前端 `fetch` 中增加 `credentials: 'include'`，并在服务端允许凭证。

#### 5）前端错误处理策略

- 统一检查 `res.ok`：
  - 否：尝试 `res.text()` 作为错误详情提示。
  - 是：尝试 `res.json()`；若解析失败则不阻断流程（返回 `true`）。
- 通知：统一通过组件内 `emit('showNotification', title, message, success)` 展示。

