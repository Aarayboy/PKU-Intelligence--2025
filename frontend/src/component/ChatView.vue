<template>
  <div class="flex flex-col h-[calc(100vh-72px)] bg-gradient-to-b from-blue-50 to-indigo-100 mt-1">
    <!-- 返回按钮 -->
    <div class="px-6 py-3 bg-transparent">
      <button
        @click="goBack"
        class="flex items-center gap-2 px-3 py-2 text-gray-700 hover:text-indigo-600 hover:bg-indigo-100 rounded-lg transition-all active:scale-95"
        title="返回"
      >
        <span class="">←</span>
        <span class="text-sm font-medium">返回</span>
      </button>
    </div>

    <!-- 聊天消息区域 -->
    <div class="flex-1 overflow-y-auto px-6 py-4 flex flex-col">
      <div class="max-w-4xl mx-auto w-full flex-1 flex flex-col">
        <!-- 空状态 -->
        <div
          v-if="messages.length === 0"
          class="flex flex-col items-center justify-center flex-1 text-gray-400"
        >
          <div class="text-7xl mb-4">💬</div>
          <p class="text-lg font-medium">上传文件后开始提问</p>
        </div>

        <!-- 消息列表 -->
        <div v-else class="space-y-4 flex-1 flex flex-col justify-start">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="[
              'flex gap-3 animate-fade-in',
              msg.role === 'user' ? 'justify-end' : 'justify-start',
            ]"
          >
            <div v-if="msg.role === 'assistant'" class="flex-shrink-0 text-2xl pt-1">
              🤖
            </div>
            <div
              :class="[
                'px-4 py-3 rounded-lg max-w-2xl break-words prose prose-sm',
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-br-none'
                  : 'bg-white text-gray-800 shadow-sm rounded-bl-none',
              ]"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <div v-if="msg.role === 'user'" class="flex-shrink-0 text-2xl pt-1">
              👤
            </div>
          </div>
        </div>
        <div ref="messagesEnd"></div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="bg-white border-t border-gray-200 px-6 py-4 shadow-lg">
      <div class="max-w-4xl mx-auto">
        <div class="flex gap-3 items-end mb-2">
          <!-- 上传按钮 -->
          <div class="flex items-center gap-2">
            <input
              type="file"
              ref="fileInput"
              accept=".pdf"
              @change="handleFileSelectAndUpload"
              class="hidden"
            />
            <button
              @click="$refs.fileInput.click()"
              class="p-2.5 bg-white border border-gray-300 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isSending"
              title="上传PDF文件"
            >
              📎
            </button>
            <span
              v-if="uploadedFileName"
              class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded truncate max-w-xs"
            >
              {{ uploadedFileName }}
            </span>
          </div>

          <!-- 输入框 -->
          <input
            v-model="input"
            @keyup.enter="sendMessage"
            :disabled="!sessionId"
            placeholder="输入你的问题..."
            class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 disabled:bg-gray-100 disabled:cursor-not-allowed transition"
          />

          <!-- 发送按钮 -->
          <button
            @click="sendMessage"
            :disabled="!sessionId || !input.trim() || isSending"
            class="px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-lg hover:shadow-indigo-400 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
          >
            <span v-if="isSending" class="inline-block animate-spin">⏳</span>
            <span v-else>发送</span>
          </button>
        </div>

        <!-- 提示文字 -->
        <p v-if="!sessionId" class="text-xs text-gray-500 text-center">
          💡 请先上传 PDF 文件初始化会话
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, inject } from "vue";
import MarkdownIt from "markdown-it";
import api from "@/chatapi/request.js";


// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
});

// 输入框和消息数组
const input = ref("");
const messages = ref([]);
const isSending = ref(false);
const uploadedFileName = ref("");
const chatView = inject("chatView");

// 会话 ID 管理
const sessionId = ref(localStorage.getItem("session_id"));

// 文件上传部分
const fileInput = ref(null);
const messagesEnd = ref(null);

// 返回上一步
const goBack = () => {
  chatView.value = !chatView.value;
};

// 自动滚动到最新消息
const scrollToBottom = async () => {
  await nextTick();
  messagesEnd.value?.scrollIntoView({ behavior: "smooth" });
};

// 渲染 Markdown
const renderMarkdown = (content) => {
  return md.render(content);
};

// 处理文件选择
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    uploadedFileName.value = file.name;
  }
}

// 处理文件选择并自动上传
async function handleFileSelectAndUpload(event) {
  const file = event.target.files[0];
  if (file) {
    uploadedFileName.value = file.name;
    // 自动上传
    await uploadFile();
  }
}

// 上传文件并存储会话 ID
async function uploadFile() {
  if (!uploadedFileName.value) {
    alert("请选择一个 PDF 文件");
    return;
  }

  isSending.value = true;
  try {
    const file = fileInput.value.files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_id", sessionId.value || "");

    const response = await api.post("/upload_pdf", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    const newSessionId = response.data.session_id;
    sessionId.value = newSessionId;
    localStorage.setItem("session_id", newSessionId);

    messages.value.push({
      role: "assistant",
      content: response.data.reply || "文件上传成功，请开始提问",
    });

    uploadedFileName.value = "";
    await scrollToBottom();
  } catch (err) {
    messages.value.push({ role: "assistant", content: "文件上传失败: " + err });
  } finally {
    isSending.value = false;
  }
}

// 发送提问
async function sendMessage() {
  if (!input.value.trim()) return;

  // 检查是否有 session_id，如果没有提示用户先上传文件
  if (!sessionId.value) {
    alert("请先上传 PDF 文件以初始化会话！");
    return;
  }

  messages.value.push({ role: "user", content: input.value });
  const userInput = input.value;
  input.value = "";

  messages.value.push({ role: "assistant", content: "正在思考..." });

  try {
    const res = await api.post("/ask_question", {
      session_id: sessionId.value, // 使用当前内存中的 sessionId
      message: userInput,
    });

    messages.value.pop(); // 移除“正在思考...”消息
    messages.value.push({ role: "assistant", content: res.data.reply });
  } catch (err) {
    messages.value.push({ role: "assistant", content: "后端错误: " + err });
  }
}
</script>

<style scoped>

* {
  box-sizing: border-box;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease;
}

/* Markdown 样式 */
:deep(h1) {
  font-size: 1.25rem;
  font-weight: bold;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}

:deep(h2) {
  font-size: 1.125rem;
  font-weight: bold;
  margin-top: 0.625rem;
  margin-bottom: 0.375rem;
}

:deep(h3) {
  font-size: 1rem;
  font-weight: bold;
  margin-top: 0.5rem;
  margin-bottom: 0.25rem;
}

:deep(p) {
  margin-bottom: 0.5rem;
}

:deep(ul),
:deep(ol) {
  margin-bottom: 0.5rem;
  margin-left: 1rem;
}

:deep(li) {
  margin-bottom: 0.25rem;
}

:deep(code) {
  background-color: #e5e7eb;
  padding: 0.375rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: monospace;
}

:deep(pre) {
  background-color: #111827;
  color: #f3f4f6;
  padding: 0.75rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 0.5rem;
}

:deep(pre code) {
  background-color: transparent;
  padding: 0;
}

:deep(blockquote) {
  border-left: 4px solid #d1d5db;
  padding-left: 0.75rem;
  font-style: italic;
  color: #4b5563;
  margin: 0.5rem 0;
}

:deep(a) {
  color: #3b82f6;
}

:deep(a:hover) {
  text-decoration: underline;
}

:deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 0.5rem;
}

:deep(th),
:deep(td) {
  border: 1px solid #d1d5db;
  padding: 0.5rem;
}

:deep(th) {
  background-color: #f3f4f6;
}

/* 用户消息中的 markdown 样式 */
.bg-gradient-to-r :deep(code) {
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.bg-gradient-to-r :deep(a) {
  color: #dbeafe;
}

.bg-gradient-to-r :deep(a:hover) {
  color: white;
}
</style>
