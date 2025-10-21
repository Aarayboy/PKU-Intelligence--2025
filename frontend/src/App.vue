<script setup>
import { ref, reactive, computed, onMounted, provide, readonly } from 'vue';

import Banner from './component/Banner.vue';
import NavAndMain from './component/NavAndMain.vue';
import ClassShadow from './component/ClassShadow.vue';
import NoteShadow from './component/NoteShadow.vue';
import Notification from './component/Notification.vue';

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

// 本地模拟数据
userData.courses.splice(0, userData.courses.length,
  new MyCourse('高等数学', ['基础', '必修'], [
    new MyNote('极限与连续笔记', null, '高等数学'),
    new MyNote('导数与微分整理', null, '高等数学'),
  ]),
  new MyCourse('数据结构', ['编程', '必修'], [
    new MyNote('栈和队列总结', null, '数据结构'),
  ]),
  new MyCourse('操作系统', ['系统'], [])
);

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

// 如需恢复接口加载，可使用下方函数并在 onMounted 调用
async function loadUserData() {
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
}

// onMounted(() => { // 先不下载数据
//   loadUserData();
// });

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
  <Banner />
  <NavAndMain @NewCourse="showNewCourseModal = true" @NewNote="showNewNoteModal = true"/>
</template>

<style scoped>
/* 全局样式在 main.js 中引入 */
</style>
