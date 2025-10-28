<script setup>
import { ref, onMounted, provide, readonly } from "vue";
import Banner from "./component/Banner.vue";
import NavAndMain from "./component/NavAndMain.vue";
import ClassShadow from "./component/ClassShadow.vue";
import NoteShadow from "./component/NoteShadow.vue";
import Notification from "./component/Notification.vue";
import LoginModal from "./component/LoginModal.vue";
import RegisterModal from "./component/RegisterModal.vue";
import WelcomePage from "./component/WelcomePage.vue";

import { useAuth } from "./composables/useAuth";
import { useUserData } from "./composables/useUserData";
import { useNotification } from "./composables/useNotification";

const {
  isLoggedIn,
  currentUser,
  showLoginModal,
  showRegisterModal,
  login,
  register,
  logout,
} = useAuth();
const { userData, loadUserData } = useUserData();
const { notificationData, setNotification } = useNotification();

const showNewCourseModal = ref(false);
const showNewNoteModal = ref(false);
const fileview = ref(false);
const filepath = ref("");

provide("userData", readonly(userData));
provide("isLoggedIn", isLoggedIn);
provide("currentUser", currentUser);
provide("fileview", fileview);
provide("filepath", filepath);

onMounted(() => {
  const savedUser = localStorage.getItem("currentUser");
  const savedLoginState = localStorage.getItem("isLoggedIn");
  if (savedUser && savedLoginState === "true") {
    try {
      currentUser.value = JSON.parse(savedUser);
      isLoggedIn.value = true;
      loadUserData(currentUser.value.id, setNotification).catch(() => {});
    } catch (e) {
      // ignore
    }
  }
});

async function handleLogin(loginData) {
  try {
    const user = await login(loginData);
    await loadUserData(user.id, setNotification);
    showLoginModal.value = false;
    setNotification("登录成功", `欢迎回来，${user.username}`, true);
  } catch (err) {
    setNotification("登录失败", err?.message || "用户名或密码错误", false);
  }
}

async function handleRegister(registerData) {
  try {
    await register(registerData);
    showRegisterModal.value = false;
    setNotification("注册成功", "请使用新账号登录", true);
    setTimeout(() => {
      showLoginModal.value = true;
    }, 800);
  } catch (err) {
    setNotification("注册失败", err?.message || "注册失败，请稍后重试", false);
  }
}

function handleLogout() {
  logout();
  userData.courses.splice(0, userData.courses.length);
  setNotification("已退出登录", "欢迎再次使用", true);
}

function CloseFileView() {
  fileview.value = false;
}
</script>

<template>
  <Notification
    v-bind="notificationData"
    @close="() => (notificationData.visible = false)"
  />

  <!-- 登录模态框 -->
  <LoginModal
    :visible="showLoginModal"
    @close="() => (showLoginModal = false)"
    @login="handleLogin"
    @switch-to-register="switchToRegister"
  />

  <!-- 注册模态框 -->
  <RegisterModal
    :visible="showRegisterModal"
    @close="() => (showRegisterModal = false)"
    @register="handleRegister"
    @switch-to-login="switchToLogin"
  />

  <!-- 主应用内容 -->
  <div v-if="isLoggedIn">
    <Banner :user="currentUser" @logout="handleLogout" />
    
    <div class="flex w-full justify-center">
      <div class="w-full max-w-7xl px-4">
        <ClassShadow
          :visible="showNewCourseModal"
          :user-id="currentUser?.id"
          @close="() => (showNewCourseModal = false)"
          @showNotification="setNotification"
          @course-saved="
            (course) => {
              // 刷新后端数据以保持一致性
              loadUserData(currentUser?.id);
            }
          "
        />
        <NoteShadow
          :visible="showNewNoteModal"
          :lesson-lists="userData.courses.map((c) => c.name)"
          :user-id="currentUser?.id"
          @close="() => (showNewNoteModal = false)"
          @showNotification="setNotification"
          @note-saved="
            (note) => {
              // 上传笔记后从后端重新加载用户数据以保持一致
              loadUserData(currentUser?.id);
            }
          "
        />
        <NavAndMain
          @NewCourse="showNewCourseModal = true"
          @NewNote="showNewNoteModal = true"
        />
      </div>

      <div
        id="Note-content"
        v-if="fileview"
        class="flex-grow bg-gray-100 p-4 border rounded-lg shadow-inner overflow-y-auto min-w-2/3 ml-4"
      >
        <div class="flex justify-between items-center mb-4 border-b pb-2">
          <h3 class="text-lg font-semibold text-gray-700 truncate">
            正在预览: {{ filepath }}
          </h3>
          <button
            @click="CloseFileView"
            class="text-gray-500 hover:text-red-600"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>




        <iframe
          :src="filepath"
          width="100%"
          height="100%"
          frameborder="0"
          class="rounded-lg"
          title="PDF Document Viewer"
        >
        </iframe>
      </div>
    </div>
  </div>

  <!-- 未登录状态显示登录界面 -->
  <WelcomePage
    v-else
    @show-login="showLoginModal = true"
    @show-register="showRegisterModal = true"
  />
</template>

<style scoped>
/* 全局样式在 main.js 中引入 */
</style>
