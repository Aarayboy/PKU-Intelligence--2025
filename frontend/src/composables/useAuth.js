import { ref } from 'vue';
import api from '@/api';

const isLoggedIn = ref(false);
const currentUser = ref(null);
const showLoginModal = ref(false);
const showRegisterModal = ref(false);

async function login(credentials) {
  const res = await api.login({ username: credentials.username, password: credentials.password });
  const user = res?.user || res;
  if (!user) throw new Error('登录失败');
  currentUser.value = { ...user };
  isLoggedIn.value = true;
  localStorage.setItem('currentUser', JSON.stringify(user));
  localStorage.setItem('isLoggedIn', 'true');
  return user;
}

async function register(payload) {
  // 1. 调用注册接口
  const res = await api.register({ 
    username: payload.username, 
    email: payload.email, 
    password: payload.password 
  });
  // 2. 解析用户数据
  const user = res?.user || res;
  
  // 3. 验证注册结果
  if (!user) throw new Error('注册失败');
  
  // // 4. 注册成功后自动登录（更新状态和本地存储）
  // currentUser.value = { ...user };
  // isLoggedIn.value = true;
  // localStorage.setItem('currentUser', JSON.stringify(user));
  // localStorage.setItem('isLoggedIn', 'true');
  
  // 5. 关闭注册模态框（如果打开）
  showRegisterModal.value = false;
  
  return user;
}

function logout() {
  currentUser.value = null;
  isLoggedIn.value = false;
  localStorage.removeItem('currentUser');
  localStorage.removeItem('isLoggedIn');
}

export function useAuth() {
  return {
    isLoggedIn,
    currentUser,
    showLoginModal,
    showRegisterModal,
    login,
    register,
    logout,
  };
}

export default useAuth;