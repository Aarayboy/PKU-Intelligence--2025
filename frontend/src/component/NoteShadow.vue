<script setup>
const props = defineProps(["visible", "lessonLists", "userId"]);
const emit = defineEmits(['close', 'showNotification', 'note-saved']);
import { ref, reactive, toRef, watch } from 'vue';

// 表单数据
const formData = reactive({
    title: '',
});

// 标签相关
const tags = ref([]);
const newTag = ref('');

// 上传文件相关（仅允许单文件）
const uploadedFiles = ref([]);
const fileError = ref('');
// 选择的课程
const selectedLesson = ref('');

// 课程列表来自父组件，保持与 userData 同步
const lessonList = toRef(props, 'lessonLists');

// 当课程列表更新时，如果当前选择不在列表中则清空，以保持一致
watch(lessonList, (newList) => {
    const list = Array.isArray(newList) ? newList : [];
    if (selectedLesson.value && !list.includes(selectedLesson.value)) {
        selectedLesson.value = '';
    }
});

// 关闭窗口
const closeWindow = () => {
    // 重置表单
    resetForm();
    emit('close');
};

// 添加标签
const addTag = () => {
    if (newTag.value.trim() && tags.value.length < 5) {
        tags.value.push(newTag.value.trim());
        newTag.value = '';
    } else if (tags.value.length >= 5) {
        // 通过父组件的事件通知，而不是直接调用不存在的函数
        emit('showNotification', '标签数量限制', '最多只能添加5个标签', false);
    }
};

// 删除标签
const removeTag = (index) => {
    tags.value.splice(index, 1);
};

// 处理文件上传
const handleFileUpload = (e) => {
        fileError.value = '';
        const files = Array.from(e.target.files || []);
        if (!files.length) {
            e.target.value = '';
            return;
        }
        const file = files[0];
        // basic size check (10MB)
        const MAX = 10 * 1024 * 1024;
        if (file.size > MAX) {
            fileError.value = '文件大小不能超过 10MB';
            emit('showNotification', '文件过大', fileError.value, false);
            e.target.value = '';
            return;
        }
        // replace any existing file (only single file allowed)
        uploadedFiles.value.splice(0, uploadedFiles.value.length, file);
        // 清空input值，允许重复上传同一文件
        e.target.value = '';
};

// 删除已上传文件
const removeFile = (index) => {
    uploadedFiles.value.splice(index, 1);
};

import api from '../api';

// 使用集中化的 API 模块上传到服务器（可被替换为 mock 或不同后端地址）
// payload: { title, tags, files: File[], lessonName }
const upToServer = async (data) => {
    // 调用统一的 uploadNote，并传入 userId（如果有）
    return api.uploadNote({
        title: data?.title ?? '',
        tags: data?.tags ?? [],
        files: data?.files ?? [],
        lessonName: data?.lessonName ?? '',
        userId: props.userId,
    });
};

// 上传中的状态，避免重复提交
const isSubmitting = ref(false);

// 表单提交
const handleSubmit = async () => {
    if (isSubmitting.value) return;

        if (!selectedLesson.value) {
                emit('showNotification', '请选择所属课程', '请先选择一个课程后再保存笔记', false);
                return;
        }
        if (uploadedFiles.value.length > 1) {
                emit('showNotification', '文件数量错误', '每个笔记最多只能包含一个文件', false);
                return;
        }
        if (uploadedFiles.value.length === 1) {
            // ensure userId exists before uploading file
            if (!props.userId) {
                emit('showNotification', '缺少用户信息', '请先登录后再上传文件', false);
                return;
            }
        }
    isSubmitting.value = true;

    // 构建完整的表单数据，包括标签和文件
    const completeData = {
        ...formData,
        tags: [...tags.value],
        files: [...uploadedFiles.value],
        lessonName: selectedLesson.value
    };

    try {
        // 上传到后端并使用后端返回的数据
        const res = await upToServer(completeData);
        const saved = res?.note || res;
        const savedFiles = res?.saved_files || [];
        console.log('保存笔记:', saved);
        // 通知父组件新增的笔记，优先使用后端返回的信息
        emit('note-saved', {
            name: saved?.name || formData.title,
            file: (savedFiles && savedFiles.length) ? savedFiles[0] : (uploadedFiles.value[0] ? uploadedFiles.value[0].name : null),
            lessonName: saved?.lessonName || selectedLesson.value,
        });
        emit('showNotification', '成功', '笔记已保存成功！', true);
        closeWindow();
    } catch (err) {
        const message = err?.message || '上传失败，请稍后重试';
        emit('showNotification', '上传失败', message, false);
    } finally {
        isSubmitting.value = false;
    }
};

// 重置表单
const resetForm = () => {
    formData.title = '';
    tags.value = [];
    uploadedFiles.value = [];
    selectedLesson.value = '';
};




</script>

<template>
    <div v-show="visible" class="global-mask">
        <div
            class="bg-white rounded-2xl shadow-soft p-5 md:p-8 mb-8 transition-custom hover:shadow-hover max-w-2xl w-full">
            <h2 class="text-2xl font-bold mb-6 text-center text-pkured">添加新笔记</h2>
            <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- 标题输入 -->
                <div>
                    <label for="noteTitle0" class="block text-sm font-medium text-neutral-700 mb-1">笔记标题 <span
                            class="text-danger">*</span></label>
                    <input type="text" id="noteTitle0" v-model="formData.title" placeholder="输入笔记标题..." required
                        class="w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-custom text-lg">
                </div>
                <!-- 所属课程选择 -->
                <div>
                    <label for="noteCategory" class="block text-sm font-medium text-neutral-700 mb-1">所属课程<span
                            class="text-danger">*</span></label>
                        <select id="noteCategory" name="noteCategory"
                            class="w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-custom appearance-none bg-white max-h-20"
                            v-model="selectedLesson"
                            required>
                        <option value="" disabled>选择所属课程</option>
                        <option v-for="(lesson, index) in lessonList" :key="index" :value="lesson">
                            {{ lesson }}
                        </option>
                    </select>
                    <div class="relative">
                        <i
                            class="fa fa-chevron-down absolute right-4 top-[-35px] text-neutral-400 pointer-events-none"></i>
                    </div>
                </div>
                <!-- 标签输入 -->
                <div>
                    <label class="block text-sm font-medium text-neutral-700 mb-1">标签</label>
                    <div
                        class="flex flex-wrap gap-2 p-2 border border-neutral-300 rounded-xl min-h-[58px] focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-custom">
                        <div v-for="(tag, index) in tags" :key="index"
                            class="inline-flex items-center bg-primary/10 text-primary px-3 py-1 rounded-full text-sm">
                            {{ tag }}
                            <button type="button" class="ml-1 text-primary/70 hover:text-primary transition-custom"
                                @click="removeTag(index)">
                                <i class="fa fa-times-circle"></i>
                            </button>
                        </div>
                        <input type="text" placeholder="添加标签并按回车..."
                            class="flex-grow min-w-[100px] px-2 py-1 bg-transparent border-none outline-none text-neutral-700"
                            @keydown.enter.prevent="addTag" v-model="newTag">
                    </div>
                    <p class="mt-1 text-xs text-neutral-500">使用回车键添加标签，最多可添加5个标签</p>
                </div>
                <!-- 附件上传 -->
                <div>
                    <label class="block text-sm font-medium text-neutral-700 mb-1">附件</label>
                    <div
                        class="border-2 border-dashed border-neutral-300 rounded-xl p-6 text-center hover:border-primary transition-custom">
                        <i class="fa fa-cloud-upload text-4xl text-neutral-400 mb-3"></i>
                        <p class="text-neutral-600 mb-3">拖放文件到此处，或点击上传</p>
                        <p class="text-xs text-neutral-500 mb-4">支持图片、文档、音频等格式，单个文件不超过10MB</p>
                        <label
                            class="inline-block px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-custom cursor-pointer">
                            <i class="fa fa-plus mr-1"></i> 选择文件
                            <input type="file" class="hidden" @change="handleFileUpload">
                        </label>
                        <p v-if="fileError" class="mt-2 text-sm text-danger">{{ fileError }}</p>
                    </div>
                    <div v-if="uploadedFiles.length">
                        <p class="mt-2 text-sm text-neutral-600">已上传文件:</p>
                        <div class="flex flex-wrap gap-2 mt-1">
                            <div v-for="(file, index) in uploadedFiles" :key="index"
                                class="flex items-center bg-neutral-100 px-3 py-1 rounded-full text-sm">
                                <i class="fa fa-file-o mr-2 text-neutral-500"></i>
                                <span class="truncate max-w-[150px]">{{ file.name }}</span>
                                <button type="button" class="ml-2 text-neutral-500 hover:text-danger transition-custom"
                                    @click="removeFile(index)">
                                    <i class="fa fa-times"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- 提交按钮 -->
                <div class="flex justify-end space-x-4 pt-4 border-t border-neutral-200">
                    <button type="button" @click="closeWindow"
                        class="px-6 py-3 border border-neutral-300 rounded-lg text-neutral-700 hover:bg-neutral-50 transition-custom">
                        取消
                    </button>
                    <button type="submit" :disabled="isSubmitting"
                        class="px-6 py-3 bg-gradient-custom text-white rounded-lg hover:opacity-90 transition-custom shadow-lg shadow-primary/20 flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
                        <i class="fa" :class="isSubmitting ? 'fa-spinner fa-spin mr-2' : 'fa-check mr-2'"></i>
                        {{ isSubmitting ? '保存中…' : '保存笔记' }}
                    </button>
                </div>
            </form>
        </div>
    </div>


</template>

<style scoped>
/* 样式已在 main.js 全局引入，无需 @reference */

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
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
}
</style>