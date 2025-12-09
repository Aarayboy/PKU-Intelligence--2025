<template>
  <div class="home" v-if="isHome">
    <h1>欢迎使用 PKU Intelligence 智能对话系统</h1>

    <p class="desc">
      这是一个由北京大学团队开发的智能问答系统示例。
      你可以点击下方按钮进入 AI 聊天界面。
    </p>

    <button class="btn" @click="() => {isHome=false}">进入 AI 对话</button>
  </div>
    <div v-if="!isHome">
      <ChatView />
    </div>
</template>

<script setup>
  import { ref } from "vue";
  import ChatView from "./ChatView.vue";
  const isHome = ref(true);
</script>

<style>
.home {
  max-width: 700px;
  margin: auto;
  text-align: center;
  padding: 20px;
}

.desc {
  margin: 20px 0;
  color: #555;
  line-height: 1.6;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  background: #1a73e8;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-size: 16px;
}

.btn:hover {
  background: #1558b0;
}
</style>