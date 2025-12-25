<template>
  <div class="chat-container">
    <!-- <header class="chat-header">
      <div class="header-content">
        <h1 class="header-title">🤖 PKU Intelligence</h1>
        <p class="header-subtitle">AI 助手</p>
      </div>
      <div class="header-badge">在线</div>
    </header> -->
    <section ref="chatBox" class="chat-box" aria-label="messages">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message-row"
        :class="msg.role === 'user' ? 'is-user' : 'is-assistant'"
      >
        <div class="avatar" :class="msg.role === 'user' ? 'avatar-user' : 'avatar-assistant'">
          <span v-if="msg.role === 'user'">👤</span>
          <span v-else>🤖</span>
        </div>
        <div class="bubble">
          <div class="bubble-content">{{ msg.content }}</div>
          <div class="bubble-meta">
            <span class="role">{{ msg.role === 'user' ? '你' : '助手' }}</span>
            <span class="dot">•</span>
            <span class="time">{{ formatTime(msg.ts) }}</span>
          </div>
        </div>
      </div>

      <div v-if="isThinking" class="message-row is-assistant typing-row">
        <div class="avatar avatar-assistant">🤖</div>
        <div class="bubble typing">
          <span class="dot dot-1"></span>
          <span class="dot dot-2"></span>
          <span class="dot dot-3"></span>
        </div>
      </div>

      <!-- 空状态提示 -->
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <p class="empty-text">开始对话</p>
        <p class="empty-hint">向我提问有关你的课程、任务或笔记</p>
      </div>
    </section>

    <footer class="input-area">
      <div class="input-wrapper">
        <div class="note-selector-wrapper">
          <!-- 改为附件选择按钮 -->
          <input ref="fileInput" type="file" class="hidden" @change="handleFileUpload" />
          <button class="note-selector-btn" @click="triggerFileSelect" title="添加附件">
            📎
            <span v-if="selectedFile" class="badge">1</span>
          </button>
        </div>
        
        <!-- 已选择的附件预览与移除 -->
        <div v-if="selectedFile" class="selected-note" style="margin-left: 4px;">
          <div class="note-item active">
            <span class="note-name">{{ selectedFile.name }}</span>
            <button class="remove-btn" @click="removeSelectedFile">✕</button>
          </div>
        </div>
        
        <textarea
          v-model="input"
          class="input"
          rows="1"
          placeholder="输入你的问题，Enter 发送，Shift+Enter 换行..."
          @keydown.enter.prevent="onEnter"
        />
        <button class="send-btn" :disabled="!canSend || isThinking" @click="sendMessage" title="发送消息 (Enter)">
          <span v-if="isThinking">⏳</span>
          <span v-else>📤</span>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, inject, computed, nextTick } from "vue";
import api from "@/chatapi/request.js";

const input = ref("");
const messages = ref([]);
const isThinking = ref(false);
const chatBox = ref(null);

const userData = inject("userData");
// 附件上传（仅单文件）
const selectedFile = ref(null);
const fileInput = ref(null);
function triggerFileSelect() {
  fileInput.value && fileInput.value.click();
}
function handleFileUpload(e) {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;
  const file = files[0];
  const MAX = 10 * 1024 * 1024; // 10MB
  if (file.size > MAX) {
    messages.value.push({ role: "assistant", content: "文件过大，最大 10MB", ts: Date.now() });
    return;
  }
  selectedFile.value = file;
}
function removeSelectedFile() {
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = "";
}

const sessionId =
  localStorage.getItem("session_id") ||
  (() => {
    const id = Math.random().toString(36).substring(2);
    localStorage.setItem("session_id", id);
    return id;
  })();

const canSend = computed(() => input.value.trim().length > 0 || !!selectedFile.value);

function formatTime(ts) {
  if (!ts) return "";
  const d = new Date(ts);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

function scrollToBottom() {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight;
    }
  });
}

function onEnter(e) {
  // Shift+Enter 换行；Enter 发送
  if (e.shiftKey) return; // 默认行为已 prevent
  sendMessage();
}

async function sendMessage() {
  if (!canSend.value || isThinking.value) return;

  const userInput = input.value.trim();
  input.value = "";

  const displayContent = selectedFile.value
    ? `${userInput || ""}\n[附件: ${selectedFile.value.name}]`
    : userInput;
  messages.value.push({ role: "user", content: displayContent, ts: Date.now() });
  isThinking.value = true;
  scrollToBottom();

  try {
    // 若存在附件，先上传到后端存储
    // if (selectedFile.value) {
    //   const uid = userData?.userId;
    //   if (!uid) {
    //     throw new Error("缺少用户ID，无法上传附件");
    //   }
    //   const lesson = "ChatUploads"; // 统一放入聊天上传目录
    //   const title = selectedFile.value.name;
    //   await uploadNote({
    //     userId: uid,
    //     lessonName: lesson,
    //     title: title,
    //     tags: ["chat-attachment"],
    //     files: [selectedFile.value],
    //   });
    // }

    const res = await api.post("/chat", {
      message: userInput || (selectedFile.value ? `请参考附件 ${selectedFile.value.name}` : ""),
      session_id: sessionId,
    });

    messages.value.push({ role: "assistant", content: res?.data?.reply ?? "[无响应]", ts: Date.now() });
  } catch (err) {
    messages.value.push({ role: "assistant", content: `后端错误: ${err?.message || err}` , ts: Date.now() });
  } finally {
    isThinking.value = false;
    removeSelectedFile();
    scrollToBottom();
  }
}
</script>

<style>
.chat-container {
  max-width: 900px;
  margin: 24px auto;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #ffffff 0%, #f5f7ff 100%);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

/* ===== 顶部标题栏 ===== */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}
.header-content {
  flex: 1;
}
.header-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.header-subtitle {
  margin: 2px 0 0 0;
  font-size: 12px;
  opacity: 0.9;
  font-weight: 400;
}
.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(10px);
}
.header-badge::before {
  content: '';
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== 聊天消息区 ===== */
.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 8px 20px;
  background: white;
  position: relative;
  scroll-behavior: smooth;
}
.chat-box::-webkit-scrollbar {
  width: 8px;
}
.chat-box::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 10px;
}
.chat-box::-webkit-scrollbar-thumb {
  background: #d0d0d0;
  border-radius: 10px;
}
.chat-box::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin: 16px 0;
  animation: slideIn 0.3s ease-out;
}
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.message-row.is-user { 
  flex-direction: row-reverse; 
  justify-content: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.avatar-user { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
.avatar-assistant { 
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.bubble {
  max-width: 70%;
  padding: 12px 14px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  animation: bubbleIn 0.3s ease-out;
}
@keyframes bubbleIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.is-user .bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}
.is-assistant .bubble {
  background: #f0f4ff;
  color: #111827;
  border-bottom-left-radius: 4px;
  border: 1px solid #e0e7ff;
}
.bubble-content {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 14px;
  word-wrap: break-word;
}
.bubble-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 11px;
}
.is-user .bubble-meta {
  opacity: 0.8;
  color: rgba(255, 255, 255, 0.9);
}
.is-assistant .bubble-meta {
  color: #6b7280;
}
.bubble-meta .dot { 
  opacity: 0.6;
}

/* ===== 打字指示器 ===== */
.typing {
  display: inline-flex;
  gap: 4px;
  padding: 10px 14px;
}
.typing .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: blink 1.4s infinite;
}
.typing .dot-1 { animation-delay: 0s; }
.typing .dot-2 { animation-delay: 0.2s; }
.typing .dot-3 { animation-delay: 0.4s; }
@keyframes blink {
  0%, 100% { 
    opacity: 0.3;
    transform: translateY(0);
  }
  50% { 
    opacity: 1;
    transform: translateY(-8px);
  }
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
}
.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.6;
}
.empty-text {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 6px;
}
.empty-hint {
  margin: 0;
  font-size: 13px;
  color: #a0aec0;
}

/* ===== 输入区 ===== */
.input-area {
  padding: 16px 20px;
  background: linear-gradient(180deg, #ffffff 0%, #f5f7ff 100%);
  border-top: 2px solid #e0e7ff;
}
.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  position: relative;
}

/* 笔记选择器 */
.note-selector-wrapper {
  position: relative;
  flex-shrink: 0;
}
.note-selector-btn {
  width: 44px;
  height: 44px;
  border: 2px solid #e0e7ff;
  border-radius: 12px;
  background: white;
  color: #667eea;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
}
.note-selector-btn:hover {
  border-color: #667eea;
  background: #fafbff;
}
.note-selector-btn .badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  background: #f5576c;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.note-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 8px;
  width: 300px;
  max-height: 400px;
  background: white;
  border: 2px solid #e0e7ff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 100;
  display: flex;
  flex-direction: column;
  animation: dropdownSlide 0.2s ease-out;
}
@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid #e0e7ff;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
}
.close-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.selected-note {
  padding: 8px 10px;
  border-bottom: 1px solid #e0e7ff;
  background: #fafbff;
}

.dropdown-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 4px;
}
.dropdown-content::-webkit-scrollbar {
  width: 6px;
}
.dropdown-content::-webkit-scrollbar-thumb {
  background: #d0d0d0;
  border-radius: 10px;
}

.note-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  margin: 2px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  gap: 8px;
}
.note-item:hover {
  background: #f0f4ff;
}
.note-item.active {
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
  border: 1px solid #c7d2fe;
}
.note-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.note-course {
  font-size: 11px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 6px;
  white-space: nowrap;
}
.remove-btn {
  width: 20px;
  height: 20px;
  border: none;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
.remove-btn:hover {
  background: #ef4444;
  color: white;
}

.empty-notes {
  padding: 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}

.input-area .input {
  flex: 1;
  resize: none;
  border: 2px solid #e0e7ff;
  border-radius: 12px;
  padding: 12px 14px;
  min-height: 44px;
  max-height: 120px;
  line-height: 1.6;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  background: white;
  transition: all 0.2s ease;
}
.input-area .input:focus { 
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: #fafbff;
}
.input-area .input::placeholder {
  color: #a0aec0;
}

.send-btn {
  width: 44px;
  height: 44px;
  padding: 0;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}
.send-btn:hover:not([disabled]) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}
.send-btn:active:not([disabled]) {
  transform: translateY(0);
}
.send-btn[disabled] { 
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

/* ===== 响应式适配 ===== */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
    margin: 0;
    border-radius: 0;
  }
  .header-title {
    font-size: 18px;
  }
  .bubble {
    max-width: 85%;
  }
}

/* ===== 深色模式 ===== */
@media (prefers-color-scheme: dark) {
  .chat-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  }
  .chat-box {
    background: #1e293b;
  }
  .chat-box::-webkit-scrollbar-track {
    background: #334155;
  }
  .chat-box::-webkit-scrollbar-thumb {
    background: #64748b;
  }
  .is-assistant .bubble {
    background: #334155;
    color: #e2e8f0;
    border-color: #475569;
  }
  .is-assistant .bubble-meta {
    color: #94a3b8;
  }
  .input-area {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-color: #334155;
  }
  .input-area .input {
    background: #1e293b;
    color: #e2e8f0;
    border-color: #334155;
  }
  .input-area .input:focus {
    background: #1e293b;
    border-color: #667eea;
  }
  .input-area .input::placeholder {
    color: #64748b;
  }
  .empty-text {
    color: #94a3b8;
  }
  .empty-hint {
    color: #64748b;
  }
}
</style>