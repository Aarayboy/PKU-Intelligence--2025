```js
// For LinksPage
class LinkCategory{
  // category, icon, array of links
  constructor(category="", icon="", links=[]){
    this.category=category;
    this.icon=icon;
    this.links=links;
  }
}
class Link{
  constructor(name="",url="", desc="", isTrusted=false){
    this.name=name;
    this.url=url;
    this.desc=desc;
    this.isTrusted=isTrusted;
  }
}
// LinkCategory实例
{
    category: "学术研究与资料库",
    icon: "📚",
    links: [
      {
        name: "Google Scholar",
        url: "https://scholar.google.com/",
        desc: "全球论文搜索，查找引文",
        isTrusted: true, 
      },
      {
        name: "CNKI (中国知网)",
        url: "https://www.cnki.net/",
        desc: "中文学术期刊、学位论文",
        isTrusted: true, 
      },
      {
        name: "一个不信任的网站",
        url: "http://untrusted-example.com/",
        desc: "一个会弹出警告的链接",
        isTrusted: false, 
      },
      {
        // 即使是超长的名称，在 UI 中也会被省略号截断，但悬浮时会显示全部
        name: "这是一个超长的链接名称测试截断", 
        url: "http://long-name-test.com/",
        desc: "测试链接名称超出限制时的显示效果",
        isTrusted: false, 
      },
    ],
}
```

# 新增接口文档

## 课程和笔记编辑接口

### 修改课程名称
- **URL**: `/edit/course`
- **方法**: `POST`
- **参数**:
  ```json
  {
    "userId": 1,
    "oldname": "原课程名",
    "newname": "新课程名"
  }
响应:

json
{
  "success": true,
  "message": "课程名称修改成功"
}
修改笔记名称
URL: /edit/note

方法: POST

参数:

json
{
  "userId": 1,
  "courseName": "课程名称",
  "oldname": "原笔记名",
  "newname": "新笔记名"
}
响应:

json
{
  "success": true,
  "message": "笔记名称修改成功"
}
常用链接接口
创建链接分类
URL: /links/categories

方法: POST

参数:

json
{
  "userId": 1,
  "category": "学术研究与资料库",
  "icon": "📚",
  "sortOrder": 0
}
响应:

json
{
  "success": true,
  "category": {
    "id": 1,
    "category": "学术研究与资料库",
    "icon": "📚",
    "userId": 1,
    "sortOrder": 0
  }
}
创建链接
URL: /links

方法: POST

参数:

json
{
  "userId": 1,
  "categoryId": 1,
  "name": "Google Scholar",
  "url": "https://scholar.google.com/",
  "description": "全球论文搜索，查找引文",
  "isTrusted": true,
  "sortOrder": 0
}
响应:

json
{
  "success": true,
  "link": {
    "id": 1,
    "name": "Google Scholar",
    "url": "https://scholar.google.com/",
    "description": "全球论文搜索，查找引文",
    "isTrusted": true,
    "categoryId": 1,
    "userId": 1
  }
}
获取用户所有链接
URL: /links?userId=1

方法: GET

响应:

json
{
  "success": true,
  "categories": [
    {
      "category": "学术研究与资料库",
      "icon": "📚",
      "links": [
        {
          "name": "Google Scholar",
          "url": "https://scholar.google.com/",
          "desc": "全球论文搜索，查找引文",
          "isTrusted": true
        }
      ]
    }
  ]
}
删除链接分类
URL: /links/categories/1?userId=1

方法: DELETE

响应:

json
{
  "success": true,
  "message": "分类删除成功"
}
删除链接
URL: /links/1?userId=1

方法: DELETE

响应:

json
{
  "success": true,
  "message": "链接删除成功"
}
任务管理接口
创建任务
URL: /tasks

方法: POST

参数:

json
{
  "userId": 1,
  "title": "完成项目报告",
  "description": "需要完成项目最终报告",
  "deadline": "2025-01-15 23:59:59",
  "priority": 3
}
响应:

json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "完成项目报告",
    "description": "需要完成项目最终报告",
    "deadline": "2025-01-15 23:59:59",
    "priority": 3,
    "completed": false,
    "userId": 1
  }
}
获取任务列表
URL: /tasks?userId=1

方法: GET

响应:

json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "title": "完成项目报告",
      "description": "需要完成项目最终报告",
      "deadline": "2025-01-15 23:59:59",
      "priority": 3,
      "completed": false,
      "userId": 1
    }
  ]
}
更新任务
URL: /tasks/1

方法: PUT

参数:

json
{
  "userId": 1,
  "title": "更新后的任务标题",
  "completed": true
}
响应:

json
{
  "success": true,
  "message": "任务更新成功"
}
删除任务
URL: /tasks/1?userId=1

方法: DELETE

响应:

json
{
  "success": true,
  "message": "任务删除成功"
}
批量更新DDL列表
URL: /edit/deadline

方法: POST

参数:

json
{
  "userId": 1,
  "deadlines": [
    {
      "title": "任务1",
      "description": "任务描述",
      "deadline": "2025-01-15 23:59:59",
      "priority": 3,
      "completed": false
    }
  ]
}
响应:

json
{
  "success": true,
  "message": "DDL列表更新成功"
}