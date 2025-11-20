<script setup>
import { ref, reactive } from "vue";

const props = defineProps(["visible", "userId"]);
const emit = defineEmits(["close", "showNotification", "course-saved"]);

// 表单数据
const formData = reactive({
  title: "",
});

// 标签相关
const tags = ref([]);
const newTag = ref("");

// 关闭窗口
const closeWindow = () => {
  // 重置表单
  resetForm();
  emit("close");
};

// 添加标签
const addTag = () => {
  if (newTag.value.trim() && tags.value.length < 5) {
    tags.value.push(newTag.value.trim());
    newTag.value = "";
  } else if (tags.value.length >= 5) {
    // 通过父组件的事件通知，而不是直接调用不存在的函数
    emit("showNotification", "标签数量限制", "最多只能添加5个标签", false);
  }
};

// 删除标签
const removeTag = (index) => {
  tags.value.splice(index, 1);
};

// 上传中的状态，避免重复提交
const isSubmitting = ref(false);

import api from "../api";

// 使用集中化的 API 模块创建课程
// payload: { title, tags }
const upToServer = async (data) => {
  return api.createCourse({
    title: data?.title ?? "",
    tags: data?.tags ?? [],
    userId: props.userId,
  });
};

// 提交表单
const handleSubmit = async () => {
  if (isSubmitting.value) return;
  if (!formData.title.trim()) {
    emit("showNotification", "请输入课程名称", "课程名称不能为空", false);
    return;
  }
  isSubmitting.value = true;
  const payload = {
    title: formData.title.trim(),
    tags: [...tags.value],
  };
  try {
    // 上传到后端并使用后端返回的数据
    const res = await upToServer(payload);
    const created = res?.course || res;
    // 通知父组件新增课程，优先使用后端返回的数据字段
    emit("course-saved", {
      name: created?.name || payload.title,
      tags: created?.tags || payload.tags,
    });
    emit("showNotification", "成功", "课程已创建！", true);
    closeWindow();
  } catch (err) {
    emit(
      "showNotification",
      "上传失败",
      err?.message || "创建课程失败，请稍后重试",
      false,
    );
  } finally {
    isSubmitting.value = false;
  }
};

// 重置表单
const resetForm = () => {
  formData.title = "";
  tags.value = [];
};
</script>

<template>
  <div v-show="visible" class="global-mask">
    <div
      class="bg-white rounded-2xl shadow-soft p-5 md:p-8 mb-8 transition-custom hover:shadow-hover max-w-2xl w-full"
    >
      <h2 class="text-2xl font-bold mb-6 text-center text-pkured">
        添加新课程
      </h2>
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- 课程名输入 -->
        <div>
          <label
            for="noteTitle1"
            class="block text-sm font-medium text-neutral-700 mb-1"
            >课程名称 <span class="text-danger">*</span></label
          >
          <input
            type="text"
            id="noteTitle1"
            v-model="formData.title"
            placeholder="输入课程名称..."
            required
            class="w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-custom text-lg"
          />
        </div>

        <!-- 标签输入 -->
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-1"
            >标签</label
          >
          <div
            class="flex flex-wrap gap-2 p-2 border border-neutral-300 rounded-xl min-h-[58px] focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-custom"
          >
            <div
              v-for="(tag, index) in tags"
              :key="index"
              class="inline-flex items-center bg-primary/10 text-primary px-3 py-1 rounded-full text-sm"
            >
              {{ tag }}
              <button
                type="button"
                class="ml-1 text-primary/70 hover:text-primary transition-custom"
                @click="removeTag(index)"
              >
                <i class="fa fa-times-circle"></i>
              </button>
            </div>
            <input
              type="text"
              placeholder="添加标签并按回车..."
              class="flex-grow min-w-[100px] px-2 py-1 bg-transparent border-none outline-none text-neutral-700"
              @keydown.enter.prevent="addTag"
              v-model="newTag"
            />
          </div>
          <p class="mt-1 text-xs text-neutral-500">
            使用回车键添加标签，最多可添加5个标签
          </p>
        </div>

        <!-- 提交按钮 -->
        <div
          class="flex justify-end space-x-4 pt-4 border-t border-neutral-200"
        >
          <button
            type="button"
            @click="closeWindow"
            class="px-6 py-3 border border-neutral-300 rounded-lg text-neutral-700 hover:bg-neutral-50 transition-custom"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-6 py-3 bg-gradient-custom text-white rounded-lg hover:opacity-90 transition-custom shadow-lg shadow-primary/20 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i
              class="fa"
              :class="
                isSubmitting ? 'fa-spinner fa-spin mr-2' : 'fa-check mr-2'
              "
            ></i>
            {{ isSubmitting ? "保存中…" : "保存课程" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.global-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  /* 品牌主色调遮罩 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 8000;
}

.loader-content {
  text-align: center;
  width: 100%;
  max-width: 600px;
  background: white;
}

.transition-custom {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.bg-gradient-custom {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}
</style>
