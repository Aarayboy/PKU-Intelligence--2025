<script setup>
import { ref, reactive, inject } from 'vue';
const userData = inject('userData'); // readonly user data from App.vue
</script>

<template>
  <div id="search-bar" class="mb-4">
    <input type="text" placeholder="搜索笔记..." class="w-full p-2 border rounded-lg" />
  </div>
  <div id="show-case">

    <div id="Notes">
      <div v-for="(course, index) in userData.courses" :key="index" class="course-item p-2 bg-white shadow-sm">
        <div class="px-4 py-2 relative">
          <h2 class="text-xl font-semibold mb-2 inline-block">{{ course.name }}</h2>
          <div class="tags mb-2 inline-block ml-4">
            <span v-for="(tag, tagIndex) in course.tags" :key="tagIndex"
              class="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full mr-2">
              {{ tag }}
            </span>
          </div>
          <div class="create-time absolute top-3 right-4 text-sm text-gray-500">
            创建时间: 2024-06-01 <!-- 后续要修改为真实时间 -->
          </div>
        </div>
        <div class="">

        </div>
        <div class="notes-list max-h-48 overflow-y-auto">
          <ul>
            <li v-for="(note, noteIndex) in course.myNotes" :key="noteIndex" class="mb-1">
              {{ note.name }}
            </li>
          </ul>
        </div>
      </div>

    </div>
    <div id="Note-content">

    </div>
  </div>
</template>

<style scoped></style>