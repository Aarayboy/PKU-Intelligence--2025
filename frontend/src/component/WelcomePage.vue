<template>
  <div class="login-container">
    <!-- 左侧留白区域 -->
    <div class="left-space"></div>
    
    <!-- 右侧内容区域 -->
    <div class="right-content">
      <!-- 标语区域（居中） -->
      <div class="slogan">
        <h1>课程笔记管理系统</h1>
        <p>高效管理你的学习笔记和课程资料</p>
      </div>
      
      <!-- 直接显示登录框 -->
      <div class="login-form-container">
        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="form-group">
            <label for="username">用户名或邮箱</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              placeholder="请输入用户名或邮箱"
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
            >
          </div>
          
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading">登录中...</span>
            <span v-else><i class="fa fa-sign-in"></i> 登录</span>
          </button>
        </form>
        
        <div class="form-footer">
          <p>还没有账号？ 
            <a href="#" @click.prevent="$emit('show-register')">立即注册</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

// 定义组件触发的事件
defineEmits(['show-login', 'show-register', 'login']);

const loading = ref(false);
const formData = reactive({
  username: '',
  password: ''
});

const handleSubmit = async () => {
  if (!formData.username || !formData.password) {
    return;
  }
  
  loading.value = true;
  
  // 模拟网络请求延迟
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 触发登录事件，将表单数据传递给父组件
  $emit('login', { ...formData });
  loading.value = false;
  
  // 清空表单
  formData.username = '';
  formData.password = '';
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  background: white; /* 整体白色背景 */
}

/* 左侧留白区域 - 占比50% */
.left-space {
  flex: 1; /* 左侧留白占一半宽度 */
}

/* 右侧内容区域 - 占比50% */
.right-content {
  flex: 1; /* 右侧内容占一半宽度 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

/* 标语区域（居中显示） */
.slogan {
  text-align: center;
  margin-bottom: 3rem; /* 与下方登录框保持距离 */
}

.slogan h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 300;
  color: #333; /* 深色文字与白色背景对比 */
}

.slogan p {
  font-size: 1.2rem;
  color: #666; /* 灰色文字 */
  opacity: 0.9;
}

/* 登录表单容器样式 */
.login-form-container {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); /* 浅灰色阴影增强立体感 */
  width: 100%;
  max-width: 400px; /* 限制最大宽度 */
}

/* 登录表单样式 */
.login-form {
  padding: 1.5rem 0;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  background: #45a049;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.form-footer {
  padding: 1rem 0;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column; /* 小屏幕下上下布局 */
  }
  
  .left-space {
    height: 100px; /* 左侧留白改为上方留白 */
    flex: none;
  }
  
  .slogan h1 {
    font-size: 2rem;
  }
  
  .slogan p {
    font-size: 1rem;
  }
  
  .login-form-container {
    padding: 1.5rem;
    margin: 1rem;
    width: auto;
  }
}
</style>