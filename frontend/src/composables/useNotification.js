import { ref } from "vue";

const notificationData = ref({
  visible: false,
  title: "",
  message: "",
  success: true,
});

function setNotification(title, message, success = true, timeout = 3000) {
  notificationData.value.title = title;
  notificationData.value.message = message;
  notificationData.value.success = success;
  notificationData.value.visible = true;

  if (timeout > 0) {
    setTimeout(() => {
      notificationData.value.visible = false;
    }, timeout);
  }
}

export function useNotification() {
  return { notificationData, setNotification };
}

export default useNotification;
