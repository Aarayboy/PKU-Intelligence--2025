<script setup>
const emit = defineEmits(['update:currentTab']);

const tabs = [
  'Note',
  'Links',
  'Tasks',
  'Courses'
];

function switchTab(tab) {
  emit('update:currentTab', tab);
  for (const t of tabs) {
    const btn = document.getElementById(t);
    if (t === tab) {
      btn.classList.add('active');
      btn.classList.remove('inactive');
    } else {
      btn.classList.add('inactive');
      btn.classList.remove('active');
    }
  }
}

</script>
<template>
  <div className="max-w-7xl mx-auto px-10 py-4">
    <div class="flex gap-4">
      <button
        id="Note"
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 active"
        @click="switchTab('Note')"
      >
        笔记管理
      </button>
      <button
        id="Links"
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 inactive"
        @click="switchTab('Links')"
      >
        常用链接
      </button>
      <button
        id="Tasks"
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 inactive"
        @click="switchTab('Tasks')"
      >
        任务管理
      </button>
      <button
        id="Courses"
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 inactive"
        @click="switchTab('Courses')"
      >
        课程管理
      </button>
    </div>
  </div>
</template>
<style scoped>

</style>
