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

// 获取用户数据（直接在URL参数中传递userId）
export async function getUserData(userId) {
  const query = userId ? `?id=${encodeURIComponent(userId)}` : '';
  return request(`/userdata${query}`, { method: 'GET' });
}

// 创建课程（使用 JSON body）
export async function createCourse(payload = {}) {
  const body = { title: payload.title || '', tags: Array.isArray(payload.tags) ? payload.tags : (payload.tags ? [payload.tags] : []) };
  if (payload.userId !== undefined && payload.userId !== null) {
    // keep as string on server side for compatibility
    body.userId = String(payload.userId);
  }
  return request('/courses/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

// 上传笔记（包含文件）
export async function uploadNote(payload = {}) {
  // 1. 基础参数校验
  if (typeof payload.lessonName !== 'string' || !payload.lessonName.trim()) {
    throw new Error('上传笔记必须包含非空课程名 (lessonName)');
  }
  if (payload.userId === undefined || payload.userId === null) {
    throw new Error('上传笔记必须包含用户 ID (userId)');
  }
  if (typeof payload.userId !== 'string' && typeof payload.userId !== 'number') {
    throw new Error('userId 必须是字符串或数字类型');
  }

  // 2. 文件参数标准化与校验
  const rawFiles = payload.files || [];
  const filesArr = Array.isArray(rawFiles) ? rawFiles : (rawFiles ? [rawFiles] : []);
  
  // 限制最多1个文件
  if (filesArr.length > 1) {
    throw new Error('每个笔记最多只能包含一个文件');
  }
  
  // 校验文件类型合法性
  filesArr.forEach((file, index) => {
    if (!(file instanceof File)) {
      throw new Error(`第 ${index + 1} 个文件必须是 File 类型`);
    }
  });

  // 3. 统一构建表单数据
  const form = new FormData();
  form.append('title', (payload.title || '').toString()); // 确保是字符串
  form.append('lessonName', payload.lessonName.trim()); // 去除首尾空格
  form.append('userId', String(payload.userId));
  form.append('tags', JSON.stringify(Array.isArray(payload.tags) ? payload.tags : [])); // 确保tags是数组

  // 添加文件（最多1个）
  filesArr.forEach(file => {
    form.append('files', file, file.name);
  });

  // 4. 发送请求
  return request('/notes/upload', { method: 'POST', body: form });
}

// 列出某用户某课程下某笔记关联的已保存文件
export async function getNoteFiles({ userId, lessonName, noteName } = {}) {
  if (!userId || !lessonName || !noteName) {
    throw new Error('getNoteFiles 需要 userId, lessonName, noteName');
  }
  const qs = `?userId=${encodeURIComponent(String(userId))}&lessonName=${encodeURIComponent(String(lessonName))}&noteName=${encodeURIComponent(String(noteName))}`;
  return request(`/notes/files${qs}`, { method: 'GET' });
}

// 返回可用于直接下载/预览的 URL（不发起请求）
export function getNoteFileUrl({ userId, lessonName, noteName, filename } = {}) {
  if (!userId || !lessonName || !noteName || !filename) {
    throw new Error('getNoteFileUrl 需要 userId, lessonName, noteName, filename');
  }
  const base = BASE || '';
  const qs = `?userId=${encodeURIComponent(String(userId))}&lessonName=${encodeURIComponent(String(lessonName))}&noteName=${encodeURIComponent(String(noteName))}&filename=${encodeURIComponent(String(filename))}`;
  return `${base}/notes/file${qs}`;
}

// 直接下载文件，返回 Response（如果是二进制流）或 JSON（如果后端返回 JSON 错误）
export async function downloadNoteFile({ userId, lessonName, noteName, filename } = {}) {
  if (!userId || !lessonName || !noteName || !filename) {
    throw new Error('downloadNoteFile 需要 userId, lessonName, noteName, filename');
  }
  const qs = `?userId=${encodeURIComponent(String(userId))}&lessonName=${encodeURIComponent(String(lessonName))}&noteName=${encodeURIComponent(String(noteName))}&filename=${encodeURIComponent(String(filename))}`;
  // request 会在非 JSON 响应时返回原始 Response 对象
  return request(`/notes/file${qs}`, { method: 'GET' });
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

export async function cloud({userId, xuehao, password} = {}) {
  return request('/cloud', { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: userId, xuehao: xuehao, password: password }),
   });
}



export default {
  getUserData,
  createCourse,
  uploadNote,
  login,
  register,
  getNoteFileUrl,
  getNoteFiles,
  downloadNoteFile,
  cloud,
};
