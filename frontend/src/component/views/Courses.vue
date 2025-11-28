<script setup>
import { inject, onMounted, computed } from "vue";
import api from "@/api";
import { useNotification } from "@/composables/useNotification";
import { generateMockSchedule } from "@/composables/useUserData";

const userData = inject("userData");
const { setNotification } = useNotification();
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

// 生成颜色表
const generateColorPalette = (count) => {
  if (count <= 1) return ['hsl(210, 70%, 80%)'];
  
  const palette = [];
  for (let i = 0; i < count; i++) {
    const hue = (i * (360 / count)) % 360;
    palette.push(`hsl(${hue}, 70%, 80%)`);
  }
  return palette;
};

// 获取所有不重复的课程
const uniqueCourses = computed(() => {
  const courseSet = new Set();
  const unique = [];
  
  userData.courseTable.allCourses.forEach(course => {
    if (!courseSet.has(course.id)) {
      courseSet.add(course.id);
      unique.push(course);
    }
  });
  
  return unique;
});

// 生成对应数量的颜色表
const colorPalette = computed(() => generateColorPalette(uniqueCourses.value.length));

// 创建课程ID到颜色的映射
const courseColorMap = computed(() => {
  return uniqueCourses.value.reduce((map, course, index) => {
    map[course.id] = colorPalette.value[index];
    return map;
  }, {});
});

// 根据课程对象获取颜色
const getCourseColor = (course) => {
  if (!course) return '#e5e7eb';
  return courseColorMap.value[course.id] || '#e5e7eb';
};

// 加载课表数据
const loadSchedule = async (useMock = false) => {
  if (!userData.userId && !useMock) return;
  
  try {
    if (useMock) {
      const mockData = generateMockSchedule();
      userData.updateCourseTable(mockData);
    } else {
      const res = await api.getSchedule(userData.userId);
      userData.updateCourseTable(res.courses || []);
    }
  } catch (err) {
    setNotification("加载失败，请检查后端服务", "使用模拟数据展示", false);
    userData.updateCourseTable(generateMockSchedule());
  }
};

onMounted(() => {
  loadSchedule(import.meta.env.DEV);
});
</script>

<template>
  <div id="courses-component" class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">我的课表</h2>
    </div>

    <!-- 课表展示 -->
    <div class="bg-white rounded-lg shadow overflow-hidden border border-black-200">
      <!-- 表头 -->
      <div class="grid grid-cols-8">
        <div class="col-span-1 bg-gray-100 p-2 font-medium border border-black">时间/星期</div>
        <div 
          class="col-span-1 bg-gray-100 p-2 font-medium text-center border border-black" 
          v-for="day in weekdays" 
          :key="day"
        >
          {{ day }}
        </div>
      </div>
      
      <div v-for="period in 12" :key="period" class="grid grid-cols-8">
        <div class="col-span-1 bg-gray-100 p-2 font-medium text-center border border-black">
          第{{ period }}节
        </div>
        <div 
          class="col-span-1 p-1 min-h-[100px] border border-black"
          v-for="(day, dayIdx) in weekdays" 
          :key="day"
        >
          <div 
            v-if="userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1))"
            class="p-2 rounded-md mb-1"
            :style="{ 
              backgroundColor: getCourseColor(userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1)))
            }"
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-cols-8 {
  grid-template-columns: repeat(8, minmax(0, 1fr));
}

:deep(.truncate) {
  color: #333;
  text-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}
</style>