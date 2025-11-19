# 项目类图

---

## 后端类图（Python / Flask）

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

    class Storage {
      db: Database
      +get_user(user_id)
      +add_user(username, email, password)
      +find_user_by_credentials(username_or_email, password)
      +find_user_by_username_or_email(value)
      +add_course(title, tags, user_id)
      +add_note(title, lessonName, tags, files, user_id)
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
    }

    FlaskApp --> Storage : uses
    Storage --> Database : uses

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

    User "1" --> "many" Course
    User "1" --> "many" Note
    Course "1" --> "many" Note
```

要点：
- Flask 路由作为控制器层，全部通过 `Storage`（门面）访问 `Database`。
- `Database` 负责连接复用、DDL 初始化，以及增删查业务。
- 领域数据以三张表表示：`users`、`courses`、`notes`，`Course.tags` 为 JSON 字符串；`Note.file` 为单文件名（文本）。

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

    UseAuth --> ApiClient : calls
    UseUserData --> ApiClient : calls
    App --> UseAuth : composes
    App --> UseUserData : composes
    App --> UseNotification : composes

    UserData "1" o--> "many" MyCourse
    MyCourse "1" o--> "many" MyNote
```

要点：
- `useUserData` 内部定义 `MyCourse / MyNote` 两个类并维护一个全局响应式 `userData`。
- `useAuth` / `useUserData` 通过 `ApiClient` 访问后端。
- `App.vue` 提供 `provide` 注入 `userData`、`isLoggedIn`、`currentUser`、`fileview`、`filepath` 等给子组件。

---






































