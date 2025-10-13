<script setup>
import { ref } from 'vue';

import Banner from './component/Banner.vue';
import Note from './component/Note.vue';
import Links from './component/Links.vue';
import Tasks from './component/Tasks.vue';
import Courses from './component/Courses.vue';

const currentTab = ref('Note');

const tabs = {
  Note,
  Links,
  Tasks,
  Courses
}

const tabsName = {
  'Note': '笔记管理',
  'Links': '常用链接',
  'Tasks': '任务管理',
  'Courses': '课程管理'
}

</script>

<template>
  <Banner />

  <div className="max-w-7xl mx-auto px-10 py-4">
    <div class="flex gap-4">
      <button v-for="(_, tab) in tabs" :key="tab"
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200"
        :class="{ 'active': currentTab === tab, 'inactive': currentTab !== tab }" @click="currentTab = tab">
        {{ tabsName[tab] }}
      </button>
    </div>
    <component :is=tabs[currentTab]> </component>
  </div>

</template>

<style scoped>
@reference "./style/index.css";
</style>
