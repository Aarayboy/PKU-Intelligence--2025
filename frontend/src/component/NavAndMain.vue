<script setup>
import { inject, ref } from 'vue';

import Note from './views/Note.vue';
import Links from './views/Links.vue';
import Tasks from './views/Tasks.vue';
import Courses from './views/Courses.vue';

defineEmits(['NewNote', 'NewCourse']);
const fileview = inject('fileview');

const currentTab = ref('Note');

const tabs = {
  Note,
  Links,
  Tasks,
  Courses,
};

const tabsName = {
  Note: '笔记管理',
  Links: '常用链接',
  Tasks: '任务管理',
  Courses: '课程管理',
};
</script>
<template>
  <div class="max-w-7xl mx-auto px-10 py-4">
    <div
      class="flex justify-between items-center mb-4"
      :class="{ hidden: fileview }"
    >
      <div class="flex gap-4">
        <button
          v-for="(_, tab) in tabs"
          :key="tab"
          class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 hover:cursor-pointer"
          :class="{ active: currentTab === tab, inactive: currentTab !== tab }"
          @click="currentTab = tab"
        >
          {{ tabsName[tab] }}
        </button>
      </div>

      <div class="flex gap-4" :class="{ hidden: currentTab !== 'Note' }">
        <button
          class="px-4 py-2 rounded-lg bg-green-500 text-white hover:bg-green-600 hover:cursor-pointer transition-all duration-200"
          @click="$emit('NewCourse')"
        >
          +新建课程
        </button>

        <button
          class="px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 hover:cursor-pointer transition-all duration-200"
          @click="$emit('NewNote')"
        >
          +新建笔记
        </button>
      </div>
    </div>
    <component :is="tabs[currentTab]"> </component>
  </div>
</template>

<style scoped>
@reference "../style/index.css";
</style>
