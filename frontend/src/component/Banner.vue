<script setup>
const emit = defineEmits(['logout', 'cloud']);
</script>
<template>
  <div class="bg-white shadow-md">
    <div class="max-w-7xl mx-auto px-10 py-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-pkured">PKU 智慧助手</h1>

      <nav class="flex items-center gap-4">
        <button
          class="p-2 rounded-lg hover:cursor-pointer hover:bg-gray-200"
          @click="emit('cloud')"
        >
          <img src="../assets/cloud.svg" class="h-5" />
        </button>
        <button class="p-2 rounded-lg hover:cursor-pointer hover:bg-gray-200">
          <img src="../assets/client.svg" class="h-5" />
        </button>
        <button
          class="p-2 rounded-lg hover:cursor-pointer hover:bg-gray-200"
          @click="emit('logout')"
        >
          <img src="../assets/logout.svg" class="h-5" />
        </button>
      </nav>
    </div>
  </div>
</template>
<style scoped></style>
