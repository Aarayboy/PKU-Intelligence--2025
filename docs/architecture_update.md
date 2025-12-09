# 项目类图

---

## 后端类图（Python / Flask & FastAPI）

```mermaid
classDiagram
    class FlaskApp {
      +userdata()
      +create_course()
      +upload_note()
      +get_note_files()
      +download_note_file()
      +auth_login()
      +auth_register()
      +cloud_status()
    }

    class ChatApp {
      +chat_endpoint(req: ChatRequest)
      +root()
    }

    class Storage {
      db: Database
      +get_user(user_id)
      +add_user(username, email, password)
      +find_user_by_credentials(username_or_email, password)
      +find_user_by_username_or_email(value)
      +add_course(title, tags, user_id)
      +add_note(title, lessonName, tags, files, user_id)
      +edit_course(user_id, oldname, newname)
      +edit_note(user_id, courseName, oldname, newname)
      +add_link_category(user_id, category, icon, sort_order)
      +get_useful_links_by_category(user_id)
      +add_useful_link(user_id, category_id, name, url, description, is_trusted)
      +add_task(user_id, title, description, deadline, priority)
      +get_tasks(user_id)
      +update_task(user_id, task_id, updates)
      +delete_task(user_id, task_id)
    }

    class Database {
      db_path: Path
      _local: threading.local
      +get_db_connection()
      +close_connection()
      +setup_database()
      +get_user(user_id)
      +get_user_with_courses_and_notes(user_id)
      +add_user(username, email, password)
      +find_user_by_credentials(username_or_email, password)
      +find_user_by_username_or_email(value)
      +add_course_to_user(user_id, course_title, tags)
      +add_note(title, lessonName, tags, files, user_id)
      +add_link_category(user_id, category, icon, sort_order)
      +get_useful_links_by_category(user_id)
      +add_useful_link(user_id, category_id, name, url, description, is_trusted)
      +add_task(user_id, title, description, deadline, priority)
      +get_tasks(user_id)
      +add_course_schedule(user_id, name, teacher, location, week_type, times)
      +get_course_schedules(user_id)
      +update_course_schedule(user_id, schedule_id, updates)
      +delete_course_schedule(user_id, schedule_id)
      +update_course_table(user_id, course_table)
    }

    class ChatSession {
      +memory: List[Dict]
      +add(role, content)
      +chat(user_input)
    }

    class LLMService {
      +call_llm_api(messages)
    }

    class SpiderService {
      +login_and_get_session(id, password)
      +collect_all_assignment_texts(session)
      +call_llm_for_deadlines(raw_items)
    }

    FlaskApp --> Storage : uses
    Storage --> Database : uses
    FlaskApp --> SpiderService : uses
    ChatApp --> ChatSession : manages
    ChatSession --> LLMService : calls

    class User {
      +id: int
      +username: str
      +email: str
      +password: str
    }
    class Course {
      +id: int
      +title: str
      +tags: JSON
      +user_id: int
    }
    class Note {
      +id: int
      +name: str
      +file: str
      +user_id: int
      +course_id: int
    }
    class LinkCategory {
      +id: int
      +name: str
      +icon: str
      +user_id: int
    }
    class UsefulLink {
      +id: int
      +name: str
      +url: str
      +category_id: int
    }
    class Task {
      +id: int
      +title: str
      +deadline: datetime
      +user_id: int
    }
    class CourseSchedule {
      +id: int
      +name: str
      +teacher: str
      +location: str
      +week_type: int
      +user_id: int
    }
    class CourseScheduleTime {
      +id: int
      +course_schedule_id: int
      +time_index: int
    }

    User "1" --> "many" Course
    User "1" --> "many" Note
    User "1" --> "many" LinkCategory
    User "1" --> "many" Task
    User "1" --> "many" CourseSchedule
    LinkCategory "1" --> "many" UsefulLink
    Course "1" --> "many" Note
    CourseSchedule "1" --> "many" CourseScheduleTime
```

要点：
- Flask 路由作为控制器层，全部通过 `Storage`（门面）访问 `Database`。
- `ChatApp` (FastAPI) 独立运行，负责处理 AI 对话请求，管理 `ChatSession`。
- `SpiderService` 封装了爬虫逻辑，包括登录北大门户、抓取作业信息以及调用 LLM 解析 DDL。
- `Database` 负责连接复用、DDL 初始化，以及增删查业务。
- 领域数据扩展为多张表：`users`、`courses`、`notes`、`link_categories`、`useful_links`、`tasks`、`course_schedules` 等。
- `Course.tags` 为 JSON 字符串；`Note.file` 为单文件名（文本）。
- 常用链接 (`UsefulLink`) 按分类 (`LinkCategory`) 组织。
- 任务 (`Task`) 包含截止日期和状态管理。
- 课程表 (`CourseSchedule`) 支持多时段 (`CourseScheduleTime`) 和周次类型设置。

---

## 前端类图（Vue 3 / 组合式 API）

```mermaid
classDiagram
    class ApiClient {
      +getUserData(userId)
      +createCourse(payload)
      +uploadNote(payload)
      +getNoteFiles(params)
      +getNoteFileUrl(params)
      +downloadNoteFile(params)
      +login(credentials)
      +register(payload)
      +cloud(params)
      -request(path, options)
    }

    class ChatApiClient {
      +baseURL: string
      +post(url, data)
    }

    class UserData {
      +username: string
      +userId: number|Null
      +email: string
      +courses: MyCourse[]
    }

    class MyCourse {
      +name: string
      +tags: string[]
      +myNotes: MyNote[]
    }

    class MyNote {
      +name: string
      +file: string|Null
      +lessonName: string
    }

    class UseAuth {
      +isLoggedIn: Ref<boolean>
      +currentUser: Ref<any>
      +showRegisterModal: Ref<boolean>
      +login(credentials)
      +register(payload)
      +logout()
    }

    class NotificationState {
      +visible: boolean
      +title: string
      +message: string
      +success: boolean
    }

    class UseNotification {
      +notificationData: Ref<NotificationState>
      +setNotification(title, message, success, timeout)
    }

    class UseUserData {
      +userData: Reactive<UserData>
      +loadUserData(userId, setNotification)
      +mapToUserData(payload)
      +ensureUserData(payload)
    }

    class App {
      +provide(userData,isLoggedIn,currentUser,fileview,filepath)
      +loadUserData()
      +handleLogin()
      +handleRegister()
      +handleLogout()
    }

    class ChatView {
      +input: Ref<string>
      +messages: Ref<Array>
      +sessionId: string
      +sendMessage()
    }

    UseAuth --> ApiClient : calls
    UseUserData --> ApiClient : calls
    ChatView --> ChatApiClient : calls
    App --> UseAuth : composes
    App --> UseUserData : composes
    App --> UseNotification : composes
    App --> ChatView : contains

    UserData "1" o--> "many" MyCourse
    MyCourse "1" o--> "many" MyNote
```

要点：
- `useUserData` 内部定义 `MyCourse / MyNote` 两个类并维护一个全局响应式 `userData`。
- `useAuth` / `useUserData` 通过 `ApiClient` 访问后端 Flask 服务。
- `ChatView` 组件通过独立的 `ChatApiClient` 访问后端 FastAPI AI 服务。
- `App.vue` 提供 `provide` 注入 `userData`、`isLoggedIn`、`currentUser`、`fileview`、`filepath` 等给子组件。

