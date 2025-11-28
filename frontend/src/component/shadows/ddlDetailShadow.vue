<script setup>
import { ref, reactive, inject, computed, onMounted } from "vue";
import api from "@/api";
const props = defineProps(["visible", "userId", "data"]);
const emit = defineEmits(["close", "done", "showNotification"]);
const userData = inject("userData");
const DdlIdx = inject("DdlIdx");
const deadlines = computed(() => userData.deadlines);
// const deadlines = ref([
//   {
//     name: "提交作业1",
//     deadline: "2024-06-15 23:59",
//     message: "记得检查格式要求",
//     status: 0,
//   },
//   {
//     name: "实验报告",
//     deadline: "2024-06-18 18:00",
//     message: "数据分析部分待完成",
//     status: 1,
//   },
//   {
//     name: "项目报告",
//     deadline: "2024-06-20 17:00",
//     message: "团队合作完成",
//     status: 0,
//   },
//   {
//     name: "期末考试复习",
//     deadline: "2024-06-25 12:00",
//     message: "重点复习章节1-5balabala",
//     status: 1,
//   },
// ]);

const MynewTasks = reactive({
  name: "",
  deadline: "",
  message: "",
  status: 0,
});
const selectNumber = ref(0);

const getTask = computed(() => {
  if (DdlIdx.value >= 0 && DdlIdx.value < deadlines.value.length) {
    return deadlines.value[DdlIdx.value];
  } else {
    return MynewTasks;
  }
});

const finishWork = async (idx) => {
  console.log("finishWork called with idx:", idx);
  if (idx >= 0 && idx < deadlines.value.length) {
    console.log("edit existing task");
    // edit existing task
    if (!getTask.value.name || !getTask.value.deadline) {
      emit("showNotification", "错误", "任务名称和截止时间不能为空", false);
      return;
    }
    getTask.value.status = parseInt(selectNumber.value);
    getTask.value.deadline = formatIsoToCustom(getTask.value.deadline);
  } else {
    // add new task
    console.log("add new task");
    if (!getTask.value.name || !getTask.value.deadline) {
      emit("showNotification", "错误", "任务名称和截止时间不能为空", false);
      return;
    }
    deadlines.value.push({
      name: getTask.value.name,
      deadline: formatIsoToCustom(getTask.value.deadline),
      message: getTask.value.message || "这里什么也没有~",
      status: parseInt(selectNumber.value),
    });
  }
  // const res = await api.UpdateDDL({ userId: userData.id, deadlines: deadlines.value });
  // TODO: 错误验证
  console.log(deadlines.value);
  emit("showNotification", "成功", "任务已保存", true);
  sortTimeLine();
  emit("close");
  emit("done");
};

function sortTimeLine() {
  for (let i = 0; i < deadlines.value.length - 1; i++) {
    for (let j = 0; j < deadlines.value.length - i - 1; j++) {
      if (
        new Date(deadlines.value[j].deadline) >
        new Date(deadlines.value[j + 1].deadline)
      ) {
        // 交换
        const temp = deadlines.value[j];
        deadlines.value[j] = deadlines.value[j + 1];
        deadlines.value[j + 1] = temp;
      }
    }
  }
}

function formatIsoToCustom(isoString) {
  // 1. 尝试使用 ISO 字符串创建一个 Date 对象
  const date = new Date(isoString);

  // 2. 检查日期是否有效
  if (isNaN(date.getTime())) {
    console.error("无效的 ISO 日期字符串:", isoString);
    return "";
  }

  // 3. 提取年、月、日、时、分
  // getFullYear() 返回四位数的年份
  const year = date.getFullYear();

  // getMonth() 返回 0-11，所以需要 +1，并且确保是两位数
  const month = String(date.getMonth() + 1).padStart(2, "0");

  // getDate() 返回月份中的某一天 (1-31)，确保是两位数
  const day = String(date.getDate()).padStart(2, "0");

  // getHours() 返回小时 (0-23)，确保是两位数
  const hours = String(date.getHours()).padStart(2, "0");

  // getMinutes() 返回分钟 (0-59)，确保是两位数
  const minutes = String(date.getMinutes()).padStart(2, "0");

  // 4. 拼接成目标格式
  return `${year}-${month}-${day} ${hours}:${minutes}`;
}

</script>
<template>
  <div class="global-mask" v-if="props.visible">
    <div class="mx-auto p-6 w-full max-w-2xl">
    <div class="bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg">
      <div class="p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">任务详情</h2>
        
        <!-- 任务名称 -->
        <div class="mb-6">
          <label for="task-name" class="block text-sm font-medium text-gray-700 mb-2">任务名称</label>
          <input
            type="text"
            id="task-name"
            v-model="getTask.name"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 outline-none"
            placeholder="输入任务名称"
          />
        </div>
        
        <!-- 截止时间 -->
        <div class="mb-6">
          <label for="deadline" class="block text-sm font-medium text-gray-700 mb-2">截止时间</label>
          <input
            type="datetime-local"
            id="deadline"
            v-model="getTask.deadline"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 outline-none"
          />
        </div>
        
        <!-- 紧急程度 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">紧急程度</label>
          <div class="flex items-center space-x-6">
            <div class="flex items-center">
              <input
                type="radio"
                id="urgent"
                value="0"
                v-model="selectNumber"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <label for="urgent" class="ml-2 block text-sm text-gray-700">紧急</label>
            </div>
            <div class="flex items-center">
              <input
                type="radio"
                id="no-urgent"
                value="1"
                v-model="selectNumber"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <label for="no-urgent" class="ml-2 block text-sm text-gray-700">不紧急</label>
            </div>
          </div>
        </div>
        
        <!-- 任务详情 -->
        <div class="mb-6">
          <label for="task-message" class="block text-sm font-medium text-gray-700 mb-2">任务详情</label>
          <textarea
            id="task-message"
            v-model="getTask.message"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 outline-none"
            placeholder="输入任务详情..."
          ></textarea>
        </div>
        
        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            class="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
            @click="emit('close')"
          >
            取消
          </button>
          <button
            class="px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
            @click="finishWork(DdlIdx)"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>
<style scoped>
.global-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  /* 品牌主色调遮罩 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 8000;
}

.loader-content {
  text-align: center;
  width: 100%;
  max-width: 600px;
  background: white;
}
</style>
