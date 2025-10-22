<template>
    <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>用户注册</h2>
          <button class="close-btn" @click="$emit('close')">
            <i class="fa fa-times"></i>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="register-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              placeholder="请输入用户名"
              minlength="3"
            >
          </div>
          
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="请输入邮箱地址"
            >
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              placeholder="请输入密码"
              minlength="6"
            >
          </div>
          
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input
              id="confirmPassword"
              v-model="formData.confirmPassword"
              type="password"
              required
              placeholder="请再次输入密码"
            >
          </div>
          
          <button type="submit" class="submit-btn" :disabled="loading || !passwordsMatch">
            <span v-if="loading">注册中...</span>
            <span v-else><i class="fa fa-user-plus"></i> 注册</span>
          </button>
        </form>
        
        <div class="form-footer">
          <p>已有账号？ 
            <a href="#" @click.prevent="$emit('switch-to-login')">立即登录</a>
          </p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, computed } from 'vue';
  
  const props = defineProps({
    visible: Boolean
  });
  
  const emit = defineEmits(['close', 'register', 'switch-to-login']);
  
  const loading = ref(false);
  const formData = reactive({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const passwordsMatch = computed(() => {
    return formData.password === formData.confirmPassword && formData.password.length >= 6;
  });
  
  const handleSubmit = async () => {
    if (!passwordsMatch.value) {
      return;
    }
    
    loading.value = true;
    
    // 模拟网络请求延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    emit('register', { 
      username: formData.username,
      email: formData.email,
      password: formData.password
    });
    
    loading.value = false;
    
    // 清空表单
    formData.username = '';
    formData.email = '';
    formData.password = '';
    formData.confirmPassword = '';
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
  
  .register-form {
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
    border-color: #4CAF50;
  }
  
  .form-group input:invalid {
    border-color: #ff4444;
  }
  
  .submit-btn {
    width: 100%;
    padding: 0.75rem;
    background: #4CAF50;
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
    color: #4CAF50;
    text-decoration: none;
  }
  
  .form-footer a:hover {
    text-decoration: underline;
  }
  </style>