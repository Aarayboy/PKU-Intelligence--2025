<script setup>
import { ref, reactive, computed, onMounted, provide, readonly } from 'vue';

import Banner from './component/Banner.vue';
import NavAndMain from './component/NavAndMain.vue';
import ClassShadow from './component/ClassShadow.vue';
import NoteShadow from './component/NoteShadow.vue';
import Notification from './component/Notification.vue';
import LoginModal from './component/LoginModal.vue';
import RegisterModal from './component/RegisterModal.vue';
import WelcomePage from './component/WelcomePage.vue';

class MyNote {
  constructor(name, file, lessonName) {
    this.name = name;
    this.file = file;
    this.lessonName = lessonName;
  }
}

class MyCourse {
  constructor(name, tags, myNotes=[]) {
    this.name = name;
    this.tags = tags;
    this.myNotes = myNotes;
  }
}

class UserData {
  constructor(courses = []) {
    this.courses = courses;
  }
}

// 登录状态
const isLoggedIn = ref(false);
const currentUser = ref(null);
const showLoginModal = ref(false);
const showRegisterModal = ref(false);

const showNewCourseModal = ref(false);
const showNewNoteModal = ref(false);

const notificationData = ref({
  visible: false,
  title: '',
  message: '',
  success: true,
});

// 用户数据（使用本地模拟数据，不从接口获取）
const userData = reactive(new UserData());

provide('userData', readonly(userData));
provide('isLoggedIn', isLoggedIn);
provide('currentUser', currentUser);

// localUsers为现阶段的模拟用户数据，后端接口未完成
const localUsers = ref([
  { id: 1, username: 'admin', password: '123456', email: 'admin@example.com' },
  { id: 2, username: 'user1', password: '123456', email: 'user1@example.com' }
]);

// 自动登录，开发中
onMounted(() => {
  /*const savedUser = localStorage.getItem('currentUser');
  const savedLoginState = localStorage.getItem('isLoggedIn');
  
  if (savedUser && savedLoginState === 'true') {
    currentUser.value = JSON.parse(savedUser);
    isLoggedIn.value = true;
    loadUserData(); // 加载用户数据
  }*/
});

// 模拟现阶段不同用户的数据，后端接口未完成
function loadUserData() {
  userData.courses.splice(0, userData.courses.length);
  
  if (currentUser.value?.username === 'admin') {
    userData.courses.push(
      new MyCourse('高等数学', ['基础', '必修'], [
        new MyNote('极限与连续笔记', null, '高等数学'),
        new MyNote('导数与微分整理', null, '高等数学'),
      ]),
      new MyCourse('数据结构', ['编程', '必修'], [
        new MyNote('栈和队列总结', null, '数据结构'),
      ]),
      new MyCourse('操作系统', ['系统'], [])
    );
  } else if (currentUser.value?.username === 'user1') {
    userData.courses.push(
      new MyCourse('英语', ['语言', '必修'], [
        new MyNote('语法总结', null, '英语'),
      ]),
      new MyCourse('计算机基础', ['编程'], [])
    );
  } else {
    // 默认数据
    userData.courses.push(
      new MyCourse('示例课程', ['示例'], [
        new MyNote('示例笔记', null, '示例课程'),
      ])
    );
  }
}

// 本地模拟数据（用上面的函数替代）
/*userData.courses.splice(0, userData.courses.length,
  new MyCourse('高等数学', ['基础', '必修'], [
    new MyNote('极限与连续笔记', null, '高等数学'),
    new MyNote('导数与微分整理', null, '高等数学'),
  ]),
  new MyCourse('数据结构', ['编程', '必修'], [
    new MyNote('栈和队列总结', null, '数据结构'),
  ]),
  new MyCourse('操作系统', ['系统'], [])
);*/

// 将后端数据映射为本地类结构的辅助函数
function mapToUserData(payload) {
  const courses = (payload?.courses ?? payload?.data?.courses ?? [])
    .map((c) => new MyCourse(
      c?.name ?? '',
      Array.isArray(c?.tags) ? c.tags : [],
      (c?.myNotes ?? []).map((n) => new MyNote(
        n?.name ?? '',
        n?.file ?? null,
        n?.lessonName ?? c?.name ?? ''
      ))
    ));
  return new UserData(courses);
}

// 如需恢复接口加载，可使用下方函数并在 onMounted 调用，目前使用本地模拟数据，因此暂时隐藏本函数
/*async function loadUserData() {
  try {
    const res = await fetch('https://example.com/userdata');
    if (!res.ok) {
      let detail = '';
      try { detail = await res.text(); } catch {}
      throw new Error(`加载用户数据失败(${res.status}): ${detail || res.statusText}`);
    }
    const data = await res.json();
    const mapped = mapToUserData(data);
    userData.courses.splice(0, userData.courses.length, ...mapped.courses);
  } catch (err) {
    console.error(err);
    setNotification('加载失败', err?.message || '无法获取用户数据', false);
  }
}*/

// onMounted(() => { // 先不下载数据
//   loadUserData();
// });

// 登录功能
const handleLogin = (loginData) => {
  const user = localUsers.value.find(u => 
    (u.username === loginData.username || u.email === loginData.username) && 
    u.password === loginData.password
  );
  
  if (user) {
    currentUser.value = { ...user };
    isLoggedIn.value = true;
    localStorage.setItem('currentUser', JSON.stringify(user));
    localStorage.setItem('isLoggedIn', 'true');
    
    loadUserData();
    showLoginModal.value = false;
    setNotification('登录成功', `欢迎回来，${user.username}`, true);
  } else {
    setNotification('登录失败', '用户名或密码错误', false);
  }
};

// 注册功能
const handleRegister = (registerData) => {
  // 检查用户名是否已存在
  const existingUser = localUsers.value.find(u => 
    u.username === registerData.username || u.email === registerData.email
  );
  
  if (existingUser) {
    setNotification('注册失败', '用户名或邮箱已存在', false);
    return;
  }
  
  // 创建新用户
  const newUser = {
    id: localUsers.value.length + 1,
    username: registerData.username,
    password: registerData.password,
    email: registerData.email
  };
  
  localUsers.value.push(newUser);
  showRegisterModal.value = false;
  setNotification('注册成功', '请使用新账号登录', true);
  
  // 自动跳转到登录界面
  setTimeout(() => {
    showLoginModal.value = true;
  }, 1000);
};

// 退出登录
const handleLogout = () => {
  currentUser.value = null;
  isLoggedIn.value = false;
  localStorage.removeItem('currentUser');
  localStorage.removeItem('isLoggedIn');
  userData.courses.splice(0, userData.courses.length);
  setNotification('已退出登录', '欢迎再次使用', true);
};

// 外部组件触发：更新课程标签
const handleUpdateCourseTags = ({ index, tags }) => {
  if (!Number.isInteger(index) || index < 0 || index >= userData.courses.length) return;
  // 在 App.vue 内修改 reactive 的 userData（provide 时对外只读）
  userData.courses[index].tags = Array.isArray(tags) ? tags : [];
  setNotification('标签已更新', '课程标签已保存', true);
};

// 打开登录模态框
const openLoginModal = () => {
  showLoginModal.value = true;
  showRegisterModal.value = false;
};

// 打开注册模态框
const openRegisterModal = () => {
  showRegisterModal.value = true;
  showLoginModal.value = false;
};

// 切换到注册
const switchToRegister = () => {
  showLoginModal.value = false;
  showRegisterModal.value = true;
};

// 切换到登录
const switchToLogin = () => {
  showRegisterModal.value = false;
  showLoginModal.value = true;
};

const setNotification = (title, message, success = true) => {
    notificationData.value.title = title;
    notificationData.value.message = message;
    notificationData.value.success = success;
    notificationData.value.visible = true;

    // 3秒后自动隐藏
    setTimeout(() => {
        notificationData.value.visible = false;
    }, 3000);
};

</script>

<template>
  <Notification v-bind="notificationData" @close="() => notificationData.visible = false"/>

  <!-- 登录模态框 -->
  <LoginModal 
    :visible="showLoginModal"
    @close="() => showLoginModal = false"
    @login="handleLogin"
    @switch-to-register="switchToRegister"
  />
  
  <!-- 注册模态框 -->
  <RegisterModal 
    :visible="showRegisterModal"
    @close="() => showRegisterModal = false"
    @register="handleRegister"
    @switch-to-login="switchToLogin"
  />

  <!-- 主应用内容 -->
  <div v-if="isLoggedIn">
    <Banner :user="currentUser" @logout="handleLogout"/>
    <ClassShadow :visible="showNewCourseModal"
                @close="() => showNewCourseModal = false"
                @showNotification="setNotification"
                @course-saved="(course) => {
                  // 若课程已存在则忽略添加，可改为通知提示
                  const exists = userData.courses.some(c => c.name === course.name);
                  if (!exists) {
                    userData.courses.push(new MyCourse(course.name, course.tags || [], []));
                  }
                }"/>
    <NoteShadow :visible="showNewNoteModal" :lesson-lists="userData.courses.map(c => c.name)"
                @close="() => showNewNoteModal = false" @showNotification="setNotification"
                @note-saved="(note) => {
                  const course = userData.courses.find(c => c.name === note.lessonName);
                  if (course) {
                    course.myNotes.push(new MyNote(note.name, note.file, note.lessonName));
                  } else {
                    // 若课程不存在，自动创建课程并加入该笔记
                    userData.courses.push(new MyCourse(note.lessonName, [], [new MyNote(note.name, note.file, note.lessonName)]));
                  }
                }"/>
  <NavAndMain @NewCourse="showNewCourseModal = true" @NewNote="showNewNoteModal = true" @update-course-tags="handleUpdateCourseTags"/>
  </div>

  <!-- 未登录状态显示登录界面 -->
  <WelcomePage v-else @show-login="showLoginModal = true" @show-register="showRegisterModal = true"/>

</template>

<style scoped>
/* 全局样式在 main.js 中引入 */
</style>
