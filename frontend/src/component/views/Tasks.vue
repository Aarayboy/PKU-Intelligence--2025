<script setup>
import { inject, computed, ref, reactive, watch } from "vue";
const userData = inject("userData");
const DdlIdx = inject("DdlIdx");
const emit = defineEmits(["DdlDetail"]);
const deadlines = computed(() => {
  return userData.deadlines || [];
});

userData.deadlines;
import api from "@/api";

const gridIdx = ref([]);

watch(
  deadlines,
  () => {
    gridIdx.value = [];
    for (let i = 0; i < deadlines.value.length; i++) {
      if (
        i === 0 ||
        deadlines.value[i].deadline.slice(0, 7) !==
          deadlines.value[i - 1].deadline.slice(0, 7)
      ) {
        gridIdx.value.push(i);
      }
    }
  },
  {
    immediate: true,
    deep: true,
  }
);

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

async function finishWork(idx) {
  // delete idx
  deadlines.value.splice(idx, 1);
  const res = await api.UpdateDDL({
    UserId: userData.userId,
    deadlines: deadlines.value || [],
  });
}

// const changeStatus = (idx, newStatus) => {
//   deadlines.value[idx].status = newStatus;
//   // TODO: 调用API保存修改后的任务状态
// };

const getToMonth = computed(() => {
  return (date) => {
    const year = date.slice(0, 4);
    const month = date.slice(5, 7);
    return `${year}年${month}月`;
  };
});

const showDetail = (idx) => {
  // show detail of deadlines[idx]
  DdlIdx.value = idx;
  emit("DdlDetail");
  console.log("Show detail of ", deadlines.value[idx]);
};

const SliceIdx = computed(() => {
  return (idx) => {
    if (idx < gridIdx.value.length - 1) {
      // console.log("Slicing from", gridIdx.value[idx], "to", gridIdx.value[idx + 1]);
      // console.log(
      //   deadlines.value.slice(
      //     gridIdx.value[idx],
      //     gridIdx.value[idx + 1]
      //   )
      // );
      return deadlines.value.slice(gridIdx.value[idx], gridIdx.value[idx + 1]);
    } else {
      // console.log("Slicing from", gridIdx.value[idx], "to end");
      // console.log(
      //   deadlines.value.slice(gridIdx.value[idx], deadlines.value.length)
      // );
      return deadlines.value.slice(gridIdx.value[idx], deadlines.value.length);
    }
  };
});
</script>

<template>
  <div class="mt-10">
    <div v-for="(seq, idx1) in gridIdx" :key="idx1" :id="'grid-' + idx1">
      <!-- header 部分 展示日期  -->
      <div class="text-lg font-bold text-gray-700 mb-4 mt-4">
        {{ getToMonth(deadlines[seq].deadline) }}
      </div>
      <div class="grid grid-cols-3 gap-7">
        <div
          v-for="(ddl, idx) in SliceIdx(idx1)"
          :key="idx"
          :id="'ddl-' + idx1 + '-' + idx"
          class="relative flex card-container"
        >
          <!-- 内容卡片 -->
          <div
            class="ddl-card flex-1 max-h-[300px] w-full cursor-pointer overflow-hidden"
            :class="{ urgent: ddl.status === 0, 'no-urgent': ddl.status === 1 }"
            @click="showDetail(seq + idx)"
            :id="'card-' + idx1 + '-' + idx"
          >
            <div class="text-xl font-medium text-black">
              {{
                (ddl?.name || "").length > 10
                  ? (ddl?.name || "").slice(0, 10) + "……"
                  : ddl?.name || ""
              }}
            </div>
            <p class="text-gray-500">
              {{
                (ddl?.message || "").length > 30
                  ? (ddl?.message || "").slice(0, 30) + "……"
                  : ddl?.message || ""
              }}
            </p>
            <div class="mt-4 text-sm text-neutral-700">
              截止时间: {{ ddl.deadline }}
            </div>
          </div>
          <!-- 完成按钮 -->
          <div
            class="finish-button absolute top-3 right-3 cursor-pointer border-none rounded-full bg-gray-300 hover:bg-gray-400 transition-colors duration-200 h-5 w-5"
            @click.stop="finishWork(seq + idx)"
            :id="'finish-' + idx1 + '-' + idx"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ddl-card {
  border-radius: 8px;
  padding: 24px;
  /* margin-bottom: 8px; */
  background-color: #f9f9f9;
}

.card-container {
  box-shadow:
    4px 4px 8px #b5b5b5,
    -4px -4px 8px #ffffff;
  border-radius: 12px;
  background-color: #f0f0f0;
  position: relative;
}

.card-container:hover {
  box-shadow:
    8px 8px 16px #b5b5b5,
    -8px -8px 16px #ffffff;
  transform: translateY(-4px);
  transition: all 0.3s ease;
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
