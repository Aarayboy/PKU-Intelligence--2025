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

const newCourse = ref({
  id: "",
  name: "",
  teacher: "",
  location: "",
  weekType: 0,
  times: []
});

// 新增课程
const addCourse = () => {
  if (!newCourse.value.name || !newCourse.value.teacher || !newCourse.value.location) {
    setNotification("请填写完整的课程信息", "错误", false);
    return;
  }

  // 自动生成课程ID和时间
  newCourse.value.id = Date.now().toString(); // 简单生成唯一ID
  newCourse.value.times = [0, 1]; // 示例时间，需根据实际需求调整

  userData.courseTable.addCourse(newCourse.value);

  // 清空表单
  newCourse.value = { id: "", name: "", teacher: "", location: "", weekType: 0, times: [] };
};

const removeCourse = (courseId) => {
  userData.courseTable.removeCourse(courseId);
};

const hasCoursesByDay = computed(() => {
  return weekdays.map((_, dayIdx) => {
    // 检查该天是否有任何课程
    for (let period = 0; period < 12; period++) {
      if (userData.courseTable.getCourseByIndex(dayIdx * 12 + period)) {
        return true;
      }
    }
    return false;
  });
});

const hasCoursesByPeriod = computed(() => {
  return Array.from({ length: 12 }, (_, period) => {
    // 检查该节课是否有任何课程
    for (let dayIdx = 0; dayIdx < 7; dayIdx++) {
      if (userData.courseTable.getCourseByIndex(dayIdx * 12 + period)) {
        return true;
      }
    }
    return false;
  });
});

// 获取列宽样式
const getColumnWidth = (dayIdx) => {
  return hasCoursesByDay.value[dayIdx] ? '1fr' : '8px';
};

// 获取行高样式
const getRowHeight = (period) => {
  return hasCoursesByPeriod.value[period] ? 'min-h-[100px]' : '8px';
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

    <!-- 新增课程表单 -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-2">新增课程</h3>
      <form @submit.prevent="addCourse">
        <div class="grid grid-cols-4 gap-4">
          <input
            v-model="newCourse.name"
            type="text"
            placeholder="课程名称"
            class="border p-2 rounded"
            required
          />
          <input
            v-model="newCourse.teacher"
            type="text"
            placeholder="教师名称"
            class="border p-2 rounded"
            required
          />
          <input
            v-model="newCourse.location"
            type="text"
            placeholder="上课地点"
            class="border p-2 rounded"
            required
          />
          <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">
            添加课程
          </button>
        </div>
      </form>
    </div>

    <!-- 课表展示 -->
    <div class="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <!-- 表头 -->
      <div class="grid grid-cols-8">
        <div class="col-span-1 bg-gray-100 p-2 font-medium border border-gray-300">时间/星期</div>
        <div 
          class="p-2 font-medium text-center border border-gray-300" 
          v-for="(day, dayIdx) in weekdays" 
          :key="day"
          :style="{ width: getColumnWidth(dayIdx) }"
        >
          <span v-if="hasCoursesByDay[dayIdx]">{{ day }}</span>
        </div>
      </div>
      
      <div 
        v-for="period in 12" 
        :key="period" 
        class="grid grid-cols-8"
        :style="{ height: getRowHeight(period - 1) }"
      >
        <div class="col-span-1 bg-gray-100 p-2 font-medium text-center border border-gray-300">
          <span v-if="hasCoursesByPeriod[period - 1]">第{{ period }}节</span>
        </div>
        <div 
          class="p-1 border border-gray-300"
          v-for="(day, dayIdx) in weekdays" 
          :key="day"
          :style="{ width: getColumnWidth(dayIdx) }"
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
            <!-- 删除课程按钮 -->
            <button 
              @click="removeCourse(userData.courseTable.getCourseByIndex(dayIdx * 12 + (period - 1)).id)"
              class="text-red-500 text-xs mt-1"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-cols-8 {
  grid-template-columns: auto repeat(7, minmax(0, 1fr));
}
:deep(.border-gray-300) {
  transition: all 0.3s ease;
}

:deep(.border-gray-300) {
  border-color: #e5e7eb;
}
</style>