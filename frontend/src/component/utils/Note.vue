<script setup>
import { ref, reactive, inject } from 'vue';
const userData = inject('userData'); // readonly user data from App.vue

const emit = defineEmits(['update-course-tags']);

// 编辑标签的状态
const editingTagsIndex = ref(null);
const tagInput = ref('');

const openEditTags = (courseIndex) => {
  const course = userData.courses[courseIndex];
  tagInput.value = Array.isArray(course?.tags) ? course.tags.join(',') : '';
  editingTagsIndex.value = courseIndex;
};

const saveTags = (courseIndex) => {
  const raw = (tagInput.value || '').trim();
  const tags = raw === '' ? [] : raw.split(',').map(t => t.trim()).filter(Boolean);
  emit('update-course-tags', { index: courseIndex, tags });
  editingTagsIndex.value = null;
};

const cancelEdit = () => {
  editingTagsIndex.value = null;
};
</script>

<template>
  <div id="search-bar" class="mb-4">
    <input type="text" placeholder="搜索笔记..." class="w-full p-2 border rounded-lg" />
  </div>
  <div id="show-case">

    <div id="Notes">
        <div v-for="(course, courseIndex) in userData.courses" :key="courseIndex" class="course-item p-2 bg-white shadow-sm mb-4">
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
          <div class="notes-list max-h-48 overflow-y-auto px-4 pb-3">
            <ul>
              <li v-for="(note, noteIndex) in course.myNotes" :key="noteIndex" class="mb-2 flex items-center justify-between">
                <div class="note-name">{{ note.name }}</div>

                <div class="note-actions flex items-center gap-3">
                  <!-- 编辑课程标签（在笔记右侧显示图标） -->
                  <i class="fa fa-tag action-icon text-gray-500 hover:text-blue-600 hover:cursor-pointer" title="编辑标签" @click="openEditTags(courseIndex)"></i>
                </div>
              </li>
            </ul>

            <!-- 内联编辑区域：显示在列表底部（也可以按需移动到覆盖在右侧） -->
            <div v-if="editingTagsIndex !== null" class="mt-2 p-2 bg-gray-50 border rounded">
              <label class="text-sm text-gray-600">编辑课程标签（用逗号分隔）</label>
              <div class="flex gap-2 mt-2">
                <input v-model="tagInput" class="flex-1 p-2 border rounded" placeholder="例如: 必修, 编程" />
                <button class="px-3 py-1 bg-green-500 text-white rounded" @click="saveTags(editingTagsIndex)">保存</button>
                <button class="px-3 py-1 bg-gray-300 text-gray-800 rounded" @click="cancelEdit">取消</button>
              </div>
            </div>
          </div>
        </div>

      </div>
    <div id="Note-content">

    </div>
  </div>
</template>

<style scoped></style>