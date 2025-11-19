<script setup>
import { ref, toRef, watchEffect } from 'vue';
const props = defineProps(['visible', 'title', 'message', 'success']);
const emit = defineEmits(['close']);

const showNotificationFlag = toRef(props, 'visible');
const notificationTitle = toRef(props, 'title');
const notificationMessage = toRef(props, 'message');
const isSuccess = toRef(props, 'success');
const notificationIconClass = ref('');
const notificationIcon = ref('');

watchEffect(() => {
  if (isSuccess.value) {
    notificationIconClass.value =
      'w-6 h-6 rounded-full bg-success/20 flex items-center justify-center text-success mr-3 mt-0.5';
    notificationIcon.value = 'fa fa-check';
  } else {
    notificationIconClass.value =
      'w-6 h-6 rounded-full bg-error/20 flex items-center justify-center text-error mr-3 mt-0.5';
    notificationIcon.value = 'fa fa-exclamation';
  }
});
</script>

<template>
  <!-- 通知提示框 -->
  <div
    id="notification"
    class="fixed top-5 bg-white rounded-lg shadow-lg p-4 transform transition-all duration-300 w-xs left-1/2 -translate-x-1/2 z-9999"
    :class="{
      'translate-y-0 opacity-100': showNotificationFlag,
      'translate-y-20 opacity-0 hidden': !showNotificationFlag,
    }"
  >
    <div class="flex items-start">
      <div id="notificationIcon" :class="notificationIconClass">
        <i :class="notificationIcon"></i>
      </div>
      <div>
        <h4 id="notificationTitle" class="font-medium text-neutral-800">
          {{ notificationTitle }}
        </h4>
        <p id="notificationMessage" class="text-neutral-600 text-sm mt-1">
          {{ notificationMessage }}
        </p>
      </div>
      <button
        id="closeNotification"
        class="ml-auto text-neutral-400 hover:text-neutral-600"
        @click="emit('close')"
      >
        <i class="fa fa-times"></i>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* 组件样式若需全局样式，已通过 main.js 引入 */
</style>
