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
  const res = await api.register({ username: payload.username, email: payload.email, password: payload.password });
  const user = res?.user || res;
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
