<script setup>
import { ref, onMounted, provide, readonly } from "vue";
import Banner from "./component/Banner.vue";
import NavAndMain from "./component/NavAndMain.vue";
import ClassShadow from "./component/shadows/ClassShadow.vue";
import NoteShadow from "./component/shadows/NoteShadow.vue";
import Notification from "./component/Notification.vue";
import RegisterModal from "./component/RegisterModal.vue";
import WelcomePage from "./component/WelcomePage.vue";
import CloudShadow from "./component/shadows/CloudShadow.vue";
import ddlDetailShadow from "./component/shadows/ddlDetailShadow.vue";

import { useAuth } from "./composables/useAuth";
import { useUserData } from "./composables/useUserData";
import { useNotification } from "./composables/useNotification";

const { isLoggedIn, currentUser, showRegisterModal, login, register, logout } =
  useAuth();
const { userData, loadUserData } = useUserData();
const { notificationData, setNotification } = useNotification();

const showNewCourseModal = ref(false);
const showNewNoteModal = ref(false);
const fileview = ref(false);
const filepath = ref("");
const showCloudModal = ref(false);
const showDdlDetailModal = ref(false);

const DdlIdx = ref(-1);


const shadowSelector = () => {
  if (showCloudModal.value) {
    return CloudShadow;
  } else if (showNewCourseModal.value) {
    return ClassShadow;
  } else if (showNewNoteModal.value) {
    return NoteShadow;
  } else if (showDdlDetailModal.value) {
    return ddlDetailShadow;
  } else {
    return null;
  }
};

const closeShadowHandler = () => {
  showCloudModal.value = false;
  showNewCourseModal.value = false;
  showNewNoteModal.value = false;
  showDdlDetailModal.value = false;
};

const dataSelector = () => {
  if (showNewNoteModal.value) {
    return userData.courses.map((c) => c.name);
  } else {
    return [];
  }
};

provide("DdlIdx", DdlIdx);
provide("userData", userData);
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

const switchToLogin = () => {
  showRegisterModal.value = false;
  // 关闭注册模态框后显示WelcomePage
  setTimeout(() => {
    isLoggedIn.value = false;
    currentUser.value = null;
  }, 300);
};

async function handleLogin(loginData) {
  try {
    const user = await login(loginData);
    await loadUserData(user.id, setNotification);
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
      isLoggedIn.value = false;
      currentUser.value = null;
    }, 800);
  } catch (err) {
    if (err?.code === 409) {
      setNotification("注册失败", "用户名或邮箱已被使用", false);
      return;
    }
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

  <!-- 注册模态框 -->
  <RegisterModal
    :visible="showRegisterModal"
    @close="() => (showRegisterModal = false)"
    @register="handleRegister"
    @switch-to-login="switchToLogin"
  />

  <!-- 主应用内容 -->
  <div v-if="isLoggedIn">
    <Banner
      :user="currentUser"
      @logout="handleLogout"
      @cloud="() => (showCloudModal = true)"
    />

    <div class="flex w-full justify-center">
      <div class="w-full max-w-7xl px-4">
        <component
          :is="shadowSelector()"
          :visible="true"
          :user-id="currentUser?.id"
          :data="dataSelector()"
          @close="closeShadowHandler()"
          @showNotification="setNotification"
          @done="
            () => {
              // 同步数据后从后端重新加载用户数据以保持一致

              loadUserData(currentUser?.id);
            }
          "
        ></component>
        <NavAndMain
          @NewCourse="showNewCourseModal = true"
          @NewNote="showNewNoteModal = true"
          @NewTask="showDdlDetailModal = true"
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
    @show-register="showRegisterModal = true"
    @login="handleLogin"
  />
</template>

<style scoped>
/* 全局样式在 main.js 中引入 */
</style>
