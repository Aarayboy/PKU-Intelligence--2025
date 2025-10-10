<script setup></script>
<template>
  <div className="max-w-7xl mx-auto px-10 py-4">
    <div class="flex gap-4">
      <div
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 active"
      >
        笔记管理
      </div>
      <div
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 inactive"
      >
        常用链接
      </div>
      <div
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 inactive"
      >
        任务管理
      </div>
      <div
        class="flex items-center gap-2 px-4 py-3 rounded-lg transition-all duration-200 inactive"
      >
        课程管理
      </div>
    </div>
  </div>
</template>
<style scoped>
@reference "../style/index.css";

.active {
  @apply bg-pkured text-white shadow-lg transform scale-105;
}

.inactive {
  @apply bg-white/80 text-gray-600 hover:bg-white hover:text-pkured hover:shadow-md;
}
</style>
