<template>
  <div class="page-container">
    <!-- 新增顶部北大红导航栏 -->
    <header class="pku-header">
      <div class="header-content">

        <img src="@/assets/WelcomePageLogo.png" alt="PKU Intelligence Logo" class="header-logo" />
        <!-- 顶部slogan -->
        <div class="header-slogan-container">
          <h1 class="header-slogan">PKU Intelligence</h1>
        </div>
      </div>
    </header>

    <div class="login-container">
      <!-- 左侧内容区域 -->
      <div class="left-space">
        <img
          src="@/assets/WelcomePagePicture.jpg"
          alt="PKU Intelligence 背景图"
          class="left-bg-img"
        />
      </div>

      <!-- 右侧内容区域 -->
      <div class="right-content">
        <!-- 原有标语区域 -->
        <div class="slogan">
          <h1>PKU Intelligence</h1>
          <p>更适合北京大学学生的笔记管理系统</p>
        </div>

        <!-- 登录框 -->
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
              <a href="#" @click.prevent="emit('show-register')">立即注册</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";

const emit = defineEmits(["show-login", "show-register", "login"]);

const loading = ref(false);
const formData = reactive({
  username: "",
  password: "",
});

const handleSubmit = async () => {
  if (!formData.username || !formData.password) {
    return;
  }

  loading.value = true;
  await new Promise((resolve) => setTimeout(resolve, 1000));
  emit("login", { ...formData });
  loading.value = false;
  formData.username = "";
  formData.password = "";
};
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.pku-header {
  background-color: #8A0000;
  color: white;
  padding: 0.8rem 0;
  width: 100%;
}

.header-content {
  max-width: 1200px;
  margin: 0 0 0 40px;
  padding: 0;
  display: flex; /* 使图片和文字横向排列 */
  align-items: center; /* 垂直居中对齐 */
  justify-content: flex-start; /* 水平靠左对齐 */
  gap: 1rem; /* 图片和文字之间的间距 */
}

/* 顶部logo图片样式 */
.header-logo {
  height: 60px;
  width: 60px;
  object-fit: contain;
}

.header-slogan-container {
  display: flex; /* 使图片和文字横向排列 */
  align-items: center; /* 垂直居中对齐 */
  justify-content: flex-start; /* 水平靠左对齐 */
  flex-direction: column;
}

.header-slogan {
  font-size: 1.5rem;
  margin: 0 0 0.2rem 0;
  font-weight: 500;
  font-family: "Times New Roman", Times, serif;
}

.login-container {
  flex: 1;
  display: flex;
  background: white;
}

.left-space {
  flex: 3 1 0%;
  position: relative;
  overflow: hidden;
}

.left-bg-img {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 80%;
  object-fit: cover;
  transform: none;
}

.right-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 2rem;
  padding-top: 2rem;
}

.slogan {
  text-align: center;
  margin-bottom: 2rem;
  padding-top: 0;
}

.slogan h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 300;
  color: #333;
  font-family: "Times New Roman", Times, serif;
}

.slogan p {
  font-size: 1.2rem;
  color: #666;
  opacity: 0.9;
}

.login-form-container {
  text-align: center;
  padding: 2.5rem;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
}

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
  padding: 1.25rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1.2rem;
  min-height: 48px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4caf50;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.05rem;
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
  color: #4caf50;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .left-space {
    height: 100px;
    flex: none;
  }

  .header-slogan {
    font-size: 1.2rem;
  }

  .header-logo {
    height: 30px; /* 小屏幕下缩小图片 */
  }

  .slogan h1 {
    font-size: 2rem;
  }

  .slogan p {
    font-size: 1rem;
  }

  .right-content {
    padding: 1rem;
    justify-content: center;
  }

  .login-form-container {
    padding: 1.5rem;
    margin: 1rem;
    max-width: 100%;
  }

  .form-group input {
    padding: 0.9rem 1rem;
    font-size: 1rem;
    min-height: 44px;
  }

  .submit-btn {
    padding: 0.9rem;
    font-size: 1rem;
  }
}
</style>