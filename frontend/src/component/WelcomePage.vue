<template>
    <div class="login-container">
      <div class="welcome-section">
        <h1>课程笔记管理系统</h1>
        <p>高效管理你的学习笔记和课程资料</p>
        <div class="auth-buttons">
          <button class="btn btn-primary" @click="$emit('show-login')">
            <i class="fa fa-sign-in"></i> 登录
          </button>
          <button class="btn btn-secondary" @click="$emit('show-register')">
            <i class="fa fa-user-plus"></i> 注册
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  // 定义组件触发的事件
  defineEmits(['show-login', 'show-register']);
  </script>
  
  <style scoped>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .welcome-section {
    text-align: center;
    color: white;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
  
  .welcome-section h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: 300;
  }
  
  .welcome-section p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    opacity: 0.9;
  }
  
  .auth-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }
  
  .btn {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 50px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .btn-primary {
    background: #4CAF50;
    color: white;
  }
  
  .btn-primary:hover {
    background: #45a049;
    transform: translateY(-2px);
  }
  
  .btn-secondary {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
  }
  
  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .welcome-section {
      padding: 1.5rem;
      margin: 1rem;
    }
    
    .welcome-section h1 {
      font-size: 2rem;
    }
    
    .welcome-section p {
      font-size: 1rem;
    }
    
    .auth-buttons {
      flex-direction: column;
      align-items: center;
    }
    
    .btn {
      width: 200px;
      justify-content: center;
    }
  }
  </style>