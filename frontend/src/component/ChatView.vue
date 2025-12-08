<template>
  <div class="chat-container">
    <h2>PKU Intelligence AI Assistant</h2>

    <div class="chat-box">
      <div 
        v-for="(msg, idx) in messages" 
        :key="idx"
        :class="msg.role"
      >
        <strong>{{ msg.role }}:</strong> {{ msg.content }}
      </div>
    </div>

    <div class="input-area">
      <input v-model="input" @keyup.enter="sendMessage" placeholder="输入你的问题..." />
      <button @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "@/chatapi/request.js";

const input = ref("");
const messages = ref([]);

const sessionId =
  localStorage.getItem("session_id") ||
  (() => {
    const id = Math.random().toString(36).substring(2);
    localStorage.setItem("session_id", id);
    return id;
  })();

async function sendMessage() {
  if (!input.value.trim()) return;

  messages.value.push({ role: "user", content: input.value });
  const userInput = input.value;
  input.value = "";

  messages.value.push({ role: "assistant", content: "正在思考..." });

  try {
    const res = await api.post("/chat", {
      message: userInput,
      session_id: sessionId,
    });

    messages.value.pop(); 
    messages.value.push({ role: "assistant", content: res.data.reply });

  } catch (err) {
    messages.value.push({ role: "assistant", content: "后端错误: " + err });
  }
}
</script>

<style>
.chat-container { max-width: 700px; margin: auto; }
.user { text-align: right; color: blue; }
.assistant { text-align: left; color: green; }
</style>