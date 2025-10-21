<script setup>
import { ref, reactive, inject } from 'vue';
const userData = inject('userData'); // readonly user data from App.vue
</script>

<template>
  <div id="search-bar">

  </div>
  <div id="show-case">

    <div id="Notes">
      <div v-for="(course, index) in userData.courses" :key="index"
        class="course-item border p-4 mb-4 rounded-lg shadow-sm">
        <h2 class="text-xl font-semibold mb-2">{{ course.name }}</h2>
        <div class="tags mb-2">
          <span v-for="(tag, tagIndex) in course.tags" :key="tagIndex"
            class="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full mr-2">
            {{ tag }}
          </span>
        </div>
        <div class="notes-list hidden max-h-48 overflow-y-auto">
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