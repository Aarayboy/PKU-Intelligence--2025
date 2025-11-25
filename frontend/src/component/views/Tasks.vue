<script setup>
import { inject, computed, ref, reactive } from "vue";
const userData = inject("userData");
const DdlIdx = inject("DdlIdx");
const emit = defineEmits(["DdlDetail"]);
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

const getStatus = computed(() => {
  return (status) => {
    if (status === 0) {
      return "urgent";
    } else if (status === 1) {
      return "no-urgent";
    } else {
      return "";
    }
  };
});

function finishWork(idx){
  // delete idx
  const elem = document.getElementById("img" + idx);
  elem.classList.remove("hidden");
  setTimeout(async () => {
    deadlines.value.splice(idx, 1);
    if (elem) {
      elem.classList.add("hidden");
    }
    // const res = await api.UpdateDDL({ userId: userData.id, deadlines: deadlines.value });
    // TODO: 错误验证
  }, 300);
};

// const changeStatus = (idx, newStatus) => {
//   deadlines.value[idx].status = newStatus;
//   // TODO: 调用API保存修改后的任务状态
// };

const showDetail = (idx) => {
  // show detail of deadlines[idx]
  DdlIdx.value = idx;
  emit("DdlDetail");
  console.log("Show detail of ", deadlines.value[idx]);
};
</script>

<template>
  <div class="mt-10">
    <div
      v-for="(ddl, idx) in deadlines"
      :key="idx"
      :id="'deadline-' + idx"
      class="relative flex"
    >
      <!-- 左侧：按钮 + 时间 -->
      <div class="flex min-w-[140px] mr-3 ml-2 items-center">
        <button
          class="w-6 h-6 border-black border-2 rounded-full flex items-center justify-center bg-white mr-2 z-10"
          @click="finishWork(idx)"
        >
          <img
            src="@/assets/right.svg"
            class="hidden bg-green-300 rounded-full"
            :id="'img' + idx"
          />
        </button>
        <span class="text-sm font-semibold text-gray-500">{{
          deadlines[idx].deadline
        }}</span>
      </div>

      <!-- 右侧：内容卡片 -->
      <div
        class="ddl-card hover:-translate-y-1 transition-transform duration-300 flex-1 max-h-[100px]"
        @click="showDetail(idx)"
      >
        <div class="text-xl font-medium text-black">
          {{
            deadlines[idx].name.length > 10
              ? deadlines[idx].name.slice(0, 10) + "……"
              : deadlines[idx].name
          }}
        </div>
        <p class="text-gray-500">
          {{
            deadlines[idx].message.length > 10
              ? deadlines[idx].message.slice(0, 10) + "……"
              : deadlines[idx].message
          }}
        </p>
        <button
          class="w-4 h-4 rounded-full transition-colors absolute right-6 top-6 ring-4 z-100"
          :class="getStatus(deadlines[idx].status)"
        ></button>
        <!--@click="changeStatus(idx, deadlines[idx].status === 0 ? 1 : 0)"-->
      </div>

      <!-- 竖线 -->
      <div
        class="timeline-line ml-2"
        :class="{ hidden: idx === deadlines.length - 1 }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.ddl-card {
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  background-color: #f9f9f9;
  box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1);
}

.timeline-line {
  content: "";
  position: absolute;
  left: 11px;
  /* 按钮中心位置 */
  top: 50px;
  /* 第一个按钮下方 */
  bottom: -50px;
  /* 延伸到下一个按钮 */
  width: 2px;
  background-color: #e5e7eb;
  /* gray-200 */
  z-index: 0;
}
</style>
