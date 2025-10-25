// 简单的前后端请求封装，带超时支持
const BASE = import.meta.env.VITE_API_BASE || '';
const DEFAULT_TIMEOUT = 15000; // 毫秒，默认 15 秒

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const timeout = typeof options.timeout === 'number' ? options.timeout : DEFAULT_TIMEOUT;

  // 从 options 中抽离不应传递给 fetch 的字段
  const { timeout: _toRemove, ...fetchOptions } = options;

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, { ...fetchOptions, signal: controller.signal });
    if (!res.ok) {
      let detail = '';
      try { detail = await res.text(); } catch {}
      throw new Error(`请求失败(${res.status}): ${detail || res.statusText}`);
    }

    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      return res.json();
    }
    // 若不是 JSON，则直接返回原始 Response 对象
    return res;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(`请求超时（${timeout}ms）`);
    }
    throw err;
  } finally {
    clearTimeout(id);
  }
}

// 获取用户数据（示例接口）
export async function getUserData(userId) {
  const query = userId ? `?id=${encodeURIComponent(userId)}` : '';
  return request(`/userdata${query}`, { method: 'GET' });
}

// 创建课程（支持 FormData）
export async function createCourse(payload = {}) {
  const form = new FormData();
  form.append('title', payload.title || '');
  form.append('tags', JSON.stringify(payload.tags || []));
  if (payload.userId !== undefined && payload.userId !== null) {
    form.append('userId', String(payload.userId));
  }
  return request('/courses/create', { method: 'POST', body: form });
}

// 上传笔记（包含文件）
export async function uploadNote(payload = {}) {
  const form = new FormData();
  form.append('title', payload.title || '');
  form.append('lessonName', payload.lessonName || '');
  form.append('tags', JSON.stringify(payload.tags || []));
  (payload.files || []).forEach((file) => {
    form.append('files', file, file.name);
  });
  if (payload.userId !== undefined && payload.userId !== null) {
    form.append('userId', String(payload.userId));
  }
  return request('/notes/upload', { method: 'POST', body: form });
}

// 登录（JSON body）
export async function login(credentials = {}) {
  return request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: credentials.username, password: credentials.password }),
  });
}

// 注册（JSON body）
export async function register(payload = {}) {
  return request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: payload.username, email: payload.email, password: payload.password }),
  });
}

export default {
  getUserData,
  createCourse,
  uploadNote,
  login,
  register,
};
