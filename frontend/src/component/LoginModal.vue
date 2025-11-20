<template>
  <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>用户登录</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="fa fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="username">用户名或邮箱</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            required
            placeholder="请输入用户名或邮箱"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            placeholder="请输入密码"
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading">登录中...</span>
          <span v-else><i class="fa fa-sign-in"></i> 登录</span>
        </button>
      </form>

      <div class="form-footer">
        <p>
          还没有账号？
          <a href="#" @click.prevent="$emit('switch-to-register')">立即注册</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const props = defineProps({
  visible: Boolean,
});

const emit = defineEmits(['close', 'login', 'switch-to-register']);

const loading = ref(false);
const formData = reactive({
  username: '',
  password: '',
});

const handleSubmit = async () => {
  if (!formData.username || !formData.password) {
    return;
  }

  loading.value = true;

  // 模拟网络请求延迟
  await new Promise((resolve) => setTimeout(resolve, 1000));

  emit('login', { ...formData });
  loading.value = false;

  // 清空表单
  formData.username = '';
  formData.password = '';
};

const handleOverlayClick = (event) => {
  if (event.target.classList.contains('modal-overlay')) {
    emit('close');
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 0;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #333;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #999;
  padding: 0.5rem;
}

.close-btn:hover {
  color: #666;
}

.login-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4caf50;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background: #45a049;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.form-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  text-align: center;
  color: #666;
}

.form-footer a {
  color: #4caf50;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>
