<script setup>
import { ref, reactive } from 'vue';
import api from '@/api';
const props = defineProps(['visible', 'userId']);
const emit = defineEmits(['close', 'showNotification', 'hasCloud']);

const formData = reactive({
    xuehao: '',
    password: '',
    userId: props.userId,
});

// 关闭窗口
const closeWindow = () => {
    // 重置表单
    resetForm();
    emit('close');
};

const isSubmitting = ref(false);

// 提交表单
const handleSubmit = async () => {
    if (isSubmitting.value) return;
    if (!formData.xuehao.trim()) {
        emit('showNotification', '请输入学号', '学号不能为空', false);
        return;
    }
    if (!formData.password.trim()) {
        emit('showNotification', '请输入密码', '密码不能为空', false);
        return;
    }
    isSubmitting.value = true;
    const payload = {
        xuehao : formData.xuehao.trim(),
        password: formData.password.trim(),
        userId: formData.userId,
    };
    try {
        // 上传到后端并使用后端返回的数据
        const res = await upToServer(payload);
        const Isok = res?.message || res;

        emit('hasCloud');
        emit('showNotification', '成功', Isok, true);
        closeWindow();
    } catch (err) {
        emit('showNotification', '同步失败', err?.message || '同步失败，请稍后重试', false);
    } finally {
        isSubmitting.value = false;
    }
};

const upToServer = async (data) => {
    const response = await api.cloud({userId: data.userId, xuehao: data.xuehao, password: data.password});
    return response;
};

// 重置表单
const resetForm = () => {
    formData.xuehao = '';
    formData.password = '';
};

</script>
<template>
 <div v-show="visible" class="global-mask">
        <div
            class="bg-white rounded-2xl shadow-soft p-5 md:p-8 mb-8 transition-custom hover:shadow-hover max-w-2xl w-full">
            <h2 class="text-2xl font-bold mb-6 text-center text-pkured">同步云端课程</h2>
            <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- 学号输入 -->
                <div>
                    <label for="xuehao" class="block text-sm font-medium text-neutral-700 mb-1">学号输入 <span
                            class="text-danger">*</span></label>
                    <input type="text" id="xuehao" v-model="formData.xuehao" placeholder="输入学号..." required
                        class="w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-custom text-lg">
                </div>
                
                <!-- 密码输入 -->
                <div>
                    <label for="password" class="block text-sm font-medium text-neutral-700 mb-1">密码输入 <span
                            class="text-danger">*</span></label>
                    <input type="password" id="password" v-model="formData.password" placeholder="输入密码..." required
                        class="w-full px-4 py-3 rounded-xl border border-neutral-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-custom text-lg">
                </div>
                
                <!-- 提交按钮 -->
                <div class="flex justify-end space-x-4 pt-4 border-t border-neutral-200">
                    <button type="button" @click="closeWindow" :disabled="isSubmitting"
                        class="px-6 py-3 border border-neutral-300 rounded-lg text-neutral-700 hover:bg-neutral-50 transition-custom">
                        取消
                    </button>
                    <button type="submit" :disabled="isSubmitting"
                        class="px-6 py-3 bg-gradient-custom text-white rounded-lg hover:opacity-90 transition-custom shadow-lg shadow-primary/20 flex items-center disabled:opacity-50 disabled:cursor-not-allowed">
                        <i class="fa" :class="isSubmitting ? 'fa-spinner fa-spin mr-2' : 'fa-check mr-2'"></i>
                        {{ isSubmitting ? '同步中…' : '同步课程' }}
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
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
}
</style>