<script setup>
import { inject, ref, onMounted } from "vue";
import api from "@/api";
import { useNotification } from "@/composables/useNotification";

const emit = defineEmits(["DdlDetail"]);
const userData = inject("userData");
const { setNotification } = useNotification();
const isAddingCourse = ref(false);
const newCourse = ref({
  name: "",
  teacher: "",
  location: "",
  weekType: 0,
  times: []
});

// 课程时间索引映射（0-83，对应周一到周日的12节课）
const timeSlots = Array.from({ length: 84 }, (_, i) => i);
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

// 加载用户课表
const loadSchedule = async () => {
  if (!userData.userId) return;
  try {
    const res = await api.getSchedule(userData.userId);
    userData.updateCourseTable(res.courses || []);
  } catch (err) {
    setNotification("加载失败", "无法获取课表数据", false);
  }
};

// 添加课程到课表
const handleAddCourse = async () => {
  if (!newCourse.value.name.trim()) {
    setNotification("输入错误", "课程名称不能为空", false);
    return;
  }
  if (newCourse.value.times.length === 0) {
    setNotification("选择错误", "请选择上课时间", false);
    return;
  }

  try {
    await api.addCourseToSchedule({
      userId: userData.userId,
      courseData: newCourse.value
    });
    setNotification("添加成功", "课程已添加到课表", true);
    loadSchedule(); // 重新加载课表
    resetNewCourseForm();
    isAddingCourse.value = false;
  } catch (err) {
    setNotification("添加失败", err.message || "无法添加课程", false);
  }
};

// 切换时间选择
const toggleTimeSlot = (index) => {
  const idx = newCourse.value.times.indexOf(index);
  if (idx > -1) {
    newCourse.value.times.splice(idx, 1);
  } else {
    newCourse.value.times.push(index);
  }
};

// 重置课程表单
const resetNewCourseForm = () => {
  newCourse.value = {
    name: "",
    teacher: "",
    location: "",
    weekType: 0,
    times: []
  };
};

// 删除课程
const handleDeleteCourse = async (courseId) => {
  if (!confirm("确定要删除这门课程吗？")) return;
  try {
    await api.deleteCourseFromSchedule({
      userId: userData.userId,
      courseId
    });
    setNotification("删除成功", "课程已从课表移除", true);
    loadSchedule();
  } catch (err) {
    setNotification("删除失败", err.message || "无法删除课程", false);
  }
};

// 获取时间段文本
const getTimeText = (index) => {
  const weekday = Math.floor(index / 12);
  const period = (index % 12) + 1;
  return `${weekdays[weekday]} 第${period}节`;
};

// 检查是否有冲突
const checkConflict = (index) => {
  return userData.courseTable.getCourseByIndex(index) !== null;
};

onMounted(() => {
  loadSchedule();
});
</script>

<template>
  <div id="courses-component" class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">我的课表</h2>
      <button 
        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        @click="isAddingCourse = !isAddingCourse"
      >
        {{ isAddingCourse ? '取消' : '+ 添加课程' }}
      </button>
    </div>

    <!-- 添加课程表单 -->
    <div v-if="isAddingCourse" class="bg-white p-4 rounded-lg shadow mb-6">
      <h3 class="text-xl font-semibold mb-4">添加新课程</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block mb-1">课程名称 *</label>
          <input 
            v-model="newCourse.name" 
            class="w-full p-2 border rounded"
            placeholder="输入课程名称"
          >
        </div>
        <div>
          <label class="block mb-1">教师</label>
          <input 
            v-model="newCourse.teacher" 
            class="w-full p-2 border rounded"
            placeholder="输入教师姓名"
          >
        </div>
        <div>
          <label class="block mb-1">上课地点</label>
          <input 
            v-model="newCourse.location" 
            class="w-full p-2 border rounded"
            placeholder="输入上课地点"
          >
        </div>
        <div>
          <label class="block mb-1">周次类型</label>
          <select v-model="newCourse.weekType" class="w-full p-2 border rounded">
            <option value="0">每周</option>
            <option value="1">单周</option>
            <option value="2">双周</option>
          </select>
        </div>
      </div>

      <div class="mt-4">
        <label class="block mb-2">上课时间选择 (可多选)</label>
        <div class="grid grid-cols-7 gap-2">
          <div v-for="(day, dayIdx) in weekdays" :key="dayIdx" class="text-center font-medium">
            {{ day }}
          </div>
          <div 
            v-for="index in timeSlots" 
            :key="index"
            class="relative"
          >
            <button
              class="w-full h-12 border rounded-md hover:bg-blue-100 transition-colors"
              :class="{
                'bg-blue-200': newCourse.times.includes(index),
                'bg-red-100': checkConflict(index) && !newCourse.times.includes(index),
                'opacity-50': checkConflict(index)
              }"
              :disabled="checkConflict(index)"
              @click="toggleTimeSlot(index)"
            >
              <span class="text-xs">{{ (index % 12) + 1 }}</span>
            </button>
          </div>
        </div>
        <p class="text-sm text-red-500 mt-2" v-if="newCourse.times.some(checkConflict)">
          红色区域表示已有课程，不可选择
        </p>
      </div>

      <div class="mt-4 flex justify-end">
        <button 
          class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
          @click="handleAddCourse"
        >
          保存课程
        </button>
      </div>
    </div>

    <!-- 课表冲突提示 -->
    <div v-if="userData.courseTable.checkConflicts().length > 0" class="bg-yellow-100 p-3 rounded-lg mb-4">
      <h3 class="font-semibold text-yellow-800">⚠️ 检测到课程冲突</h3>
      <ul class="text-sm text-yellow-700 mt-1">
        <li v-for="(conflict, idx) in userData.courseTable.checkConflicts()" :key="idx">
          {{ conflict.course1.name }} 与 {{ conflict.course2.name }} 时间冲突
        </li>
      </ul>
    </div>

    <!-- 课表展示 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="grid grid-cols-7 border-b">
        <div class="col-span-1 bg-gray-100 p-2 font-medium">时间/星期</div>
        <div class="col-span-1 bg-gray-100 p-2 font-medium text-center" v-for="day in weekdays" :key="day">
          {{ day }}
        </div>
      </div>
      
      <div v-for="period in 12" :key="period" class="grid grid-cols-7 border-b last:border-b-0">
        <div class="col-span-1 bg-gray-100 p-2 font-medium text-center">
          第{{ period }}节
        </div>
        <div 
          class="col-span-1 border-l last:border-r p-1 min-h-[100px]"
          v-for="(day, dayIdx) in weekdays" 
          :key="day"
        >
          <div 
            v-if="userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1))"
            class="bg-blue-100 p-1 rounded-md mb-1 relative group"
          >
            <div class="font-medium text-sm truncate">
              {{ userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1)).name }}
            </div>
            <div class="text-xs text-gray-600 truncate">
              {{ userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1)).teacher }}
            </div>
            <div class="text-xs text-gray-600 truncate">
              {{ userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1)).location }}
            </div>
            <div class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                class="text-red-500 hover:text-red-700"
                @click="handleDeleteCourse(userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1)).id)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-cols-7 {
  grid-template-columns: repeat(7, minmax(0, 1fr));
}
</style>