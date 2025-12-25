<script setup>
import { inject, onMounted, computed, ref, reactive } from "vue";
import api from "@/api";
import { useNotification } from "@/composables/useNotification";
import { generateMockSchedule, addCourse, removeCourse } from "@/composables/useUserData";

const userData = inject("userData");
const { setNotification } = useNotification();
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const deleteMode = ref(false);

const generateColorPalette = (count) => {
  if (count <= 1) return ['hsl(210, 70%, 80%)'];
  const palette = [];
  for (let i = 0; i < count; i++) {
    const hue = (i * (360 / count)) % 360;
    palette.push(`hsl(${hue}, 70%, 80%)`);
  }
  return palette;
};

const uniqueCourses = computed(() => {
  const courseSet = new Set();
  const unique = [];
  (userData.courseTable?.allCourses ?? []).forEach(course => {
    if (!courseSet.has(course.id)) {
      courseSet.add(course.id);
      unique.push(course);
    }
  });
  return unique;
});
const colorPalette = computed(() => generateColorPalette(uniqueCourses.value.length));
const courseColorMap = computed(() => {
  return uniqueCourses.value.reduce((map, course, index) => {
    map[course.id] = colorPalette.value[index];
    return map;
  }, {});
});
const getCourseColor = (course) => {
  if (!course) return '#e5e7eb';
  return courseColorMap.value[course.id] || '#e5e7eb';
};

const showAddModal = ref(false);
const form = reactive({
  name: "",
  teacher: "",
  location: "",
  weekType: 0,
  dayIdx: 0, // 0..6 -> 周一..周日
  periods: Array.from({ length: 12 }, () => false) // 12 节课可多选
});

const resetForm = () => {
  form.name = "";
  form.teacher = "";
  form.location = "";
  form.weekType = 0;
  form.dayIdx = 0;
  form.periods.fill(false);
};

const openAddModal = () => {
  resetForm();
  showAddModal.value = true;
};
const closeAddModal = () => {
  showAddModal.value = false;
};
const toggleDeleteMode = () => {
  showAddModal.value = false;
  deleteMode.value = !deleteMode.value;
};

const computeIndex = (dayIdx, period) => {
  return (period - 1) * 7 + dayIdx;
};

const rowEmpty = computed(() => {
  return Array.from({ length: 12 }, (_, p) => {
    const period = p + 1;
    for (let dayIdx = 0; dayIdx < weekdays.length; dayIdx++) {
      if (userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period))) {
        return false;
      }
    }
    return true;
  });
});

const colEmpty = computed(() => {
  return weekdays.map((_, dayIdx) => {
    for (let p = 0; p < 12; p++) {
      const period = p + 1;
      if (userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period))) {
        return false;
      }
    }
    return true;
  });
});

const gridTemplate = computed(() => {
  const firstCol = 'minmax(100px, max-content)';
  const dayCols = weekdays.map((_, i) =>
    colEmpty.value[i] ? 'minmax(36px, max-content)' : 'minmax(200px, max-content)'
  );
  return [firstCol, ...dayCols].join(' ');
});

// 提交新增：构建 times 索引并调用 composable / 后端（若存在）
const submitAdd = async () => {
  if (!form.name.trim()) {
    setNotification("错误", "课程名称不能为空", false);
    return;
  }
  const selectedPeriods = form.periods
    .map((v, i) => v ? i + 1 : -1)
    .filter(i => i > 0);
  if (selectedPeriods.length === 0) {
    setNotification("错误", "请至少选择一节课时", false);
    return;
  }

  // 把 dayIdx(0..6) 和 period(1..12) 转换为 index(0..83)
  const times = [];
  selectedPeriods.forEach(p => {
    const index = computeIndex(form.dayIdx, p);
    times.push(index);
  });

  const newCourse = {
    id: `local-${Date.now()}`, // 本地 id，后端可替换
    name: form.name,
    teacher: form.teacher,
    location: form.location,
    weekType: form.weekType,
    times
  };

  try {
    // 先尝试调用后端接口（如果存在）
    if (typeof api?.addCourse === "function") {
      // 后端可能返回带 id 的课程对象
      const res = await api.addCourse(newCourse);
      const serverCourse = res?.data ?? res;
      // 如果后端返回课程数据，用返回的数据替换，否则用本地 newCourse
      addCourse(serverCourse?.id ? serverCourse : newCourse);
    } else {
      // 仅本地添加
      addCourse(newCourse);
    }
    setNotification("成功", "课程已添加", true);
    closeAddModal();
  } catch (err) {
    setNotification("失败", err?.message || "添加课程失败", false);
    addCourse(newCourse);
    closeAddModal();
  }
};

// 删除课程：弹出确认，调用 composable 和后端
const onRemoveCourse = async (courseId) => {
  if (!courseId) return;
  const ok = window.confirm("确认删除该课程吗？此操作会从当前课表移除。");
  if (!ok) return;

  try {
    if (typeof api?.removeCourse === "function") {
      await api.removeCourse(courseId);
    }
    removeCourse(courseId);
    setNotification("成功", "课程已删除", true);
  } catch (err) {
    // 如果后端删除失败，仍在本地尝试移除以保证即时反馈
    removeCourse(courseId);
    setNotification("失败", err?.message || "删除时出错，已在本地移除", false);
  }
};

const loadSchedule = async (useMock = false) => {
  if (!userData.userId && !useMock) return;
  try {
    if (useMock) {
      const mockData = generateMockSchedule();
      userData.updateCourseTable(mockData);
    } else {
      const res = await api.getSchedule(userData.userId);
      console.log("加载课表数据：", res);
      userData.updateCourseTable(res.courseTable || []);
    }
  } catch (err) {
    setNotification("加载失败，请检查后端服务", "使用模拟数据展示", false);
    userData.updateCourseTable(generateMockSchedule());
  }
};

onMounted(() => {
  loadSchedule(false);
});
</script>

<template>
  <div id="courses-component" class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">我的课表</h2>
      <div class="flex gap-2">
        <button class="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-green-600 hover:cursor-pointer transition-all duration-200" @click="openAddModal">新增课程</button>
        <button
          @click="toggleDeleteMode"
          :class="deleteMode ? 'bg-red-500 text-white px-3 py-1 rounded' : 'px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-green-600 hover:cursor-pointer transition-all duration-200'"
          title="切换删除模式：开启后可点击课程右上角删除"
        >
          {{ deleteMode ? '退出删除' : '删除' }}
        </button>
      </div>
    </div>

    <!-- 课表展示 -->
    <div class="overflow-auto flex justify-center">
      <div class="inline-grid mx-auto gap-0" :style="{ gridTemplateColumns: gridTemplate }">
        <!-- 表头 -->
        <div class="bg-gray-100 p-2 font-medium border border-black flex items-center justify-center">时间/星期</div>
        <div 
          v-for="(day, dayIdx) in weekdays" 
          :key="'h-'+dayIdx"
          class="bg-gray-100 p-2 font-medium text-center border border-black flex items-center justify-center"
        >
          {{ day }}
        </div>

        <template v-for="period in 12" :key="'row-'+period">
          <div 
            class="bg-gray-100 p-2 font-medium border border-black flex items-center justify-center"
            :class="rowEmpty[period - 1] ? 'min-h-[36px]' : 'min-h-[200px]'"
          >
            第{{ period }}节
          </div>

          <div 
            v-for="(day, dayIdx) in weekdays" 
            :key="dayIdx + '-' + period"
            :class="[
              'col-span-1 p-1 border border-black flex items-center justify-center overflow-hidden',
              rowEmpty[period - 1] ? 'min-h-[36px]' : 'min-h-[200px]'
            ]"
          >
            <div 
              v-if="userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period))"
              class="p-2 rounded-md relative w-full h-full box-border flex flex-col items-center justify-center text-center"
              :style="{ 
                backgroundColor: getCourseColor(userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period)))
              }"
            >
              <button
                v-if="deleteMode"
                class="absolute top-1 right-1 text-xs bg-red-500 text-white rounded px-1"
                @click.stop="onRemoveCourse(userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period)).id)"
              >删除</button>
              <div class="font-medium text-sm truncate">
                {{ userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period)).name }}
              </div>
              <div class="text-xs text-gray-600 truncate">
                {{ userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period)).teacher }}
              </div>
              <div class="text-xs text-gray-600 truncate">
                {{ userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period)).location }}
              </div>
              <div class="text-xs text-gray-500 truncate">
                {{ ['每周', '单周', '双周'][userData.courseTable.getCourseByIndex(computeIndex(dayIdx, period)).weekType] }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 新增课程弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black opacity-40" @click="closeAddModal"></div>
      <div class="relative bg-white rounded-lg p-6 w-[680px] max-w-[95%] z-60">
        <h3 class="text-lg font-semibold mb-4">新增课程</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm">课程名称</label>
            <input v-model="form.name" class="w-full border rounded px-2 py-1" />
          </div>
          <div>
            <label class="block text-sm">授课教师</label>
            <input v-model="form.teacher" class="w-full border rounded px-2 py-1" />
          </div>
          <div>
            <label class="block text-sm">上课地点</label>
            <input v-model="form.location" class="w-full border rounded px-2 py-1" />
          </div>
          <div>
            <label class="block text-sm">周次类型</label>
            <select v-model.number="form.weekType" class="w-full border rounded px-2 py-1">
              <option :value="0">每周</option>
              <option :value="1">单周</option>
              <option :value="2">双周</option>
            </select>
          </div>

          <div class="col-span-2">
            <label class="block text-sm mb-1">选择星期</label>
            <div class="flex gap-2">
              <button
                v-for="(d, idx) in weekdays"
                :key="d"
                type="button"
                @click="form.dayIdx = idx"
                :class="['px-2 py-1 rounded', form.dayIdx === idx ? 'bg-blue-500 text-white' : 'bg-gray-100']"
              >{{ d }}</button>
            </div>
          </div>

          <div class="col-span-2">
            <label class="block text-sm mb-2">选择节次（可多选）</label>
            <div class="grid grid-cols-6 gap-2">
              <label v-for="n in 12" :key="n" class="flex items-center gap-2">
                <input type="checkbox" v-model="form.periods[n-1]" />
                <span class="text-sm">第{{ n }}节</span>
              </label>
            </div>
          </div>
        </div>

        <div class="mt-4 flex justify-end gap-2">
          <button class="px-3 py-1 rounded bg-gray-200" @click="closeAddModal">取消</button>
          <button class="px-3 py-1 rounded bg-blue-500 text-white" @click="submitAdd">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.truncate) {
  color: #333;
  text-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}
</style>