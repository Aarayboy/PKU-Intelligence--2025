<script setup></script>
<template>
  <div class="bg-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-bold text-pkured">PKU 智慧助手</h1>

            <nav class="flex space-x-6 justify-between items-center">
                <a href="/" class="hover:text-pkured">个人资料</a>
                <a href="/" class="hover:text-pkured">
                  <img src="../assets/cloud.svg" class="h-8"></img>
                </a>
                <a href="/" class="hover:text-pkured">
                  <img src="../assets/client.svg" class="h-8"></img>
                </a>
                <button class="hover:text-pkured" onclick="logout()">
                <img src="../assets/logout.svg" class="h-8"></img>
                </button>
            </nav>
    </div>
  </div>
</template>
<style scoped></style>