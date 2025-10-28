import { reactive } from 'vue';
import api from '@/api';

class MyNote {
  constructor(name, file, lessonName) {
    this.name = name;
    this.file = file;
    this.lessonName = lessonName;
  }
}

class MyCourse {
  constructor(name, tags, myNotes = []) {
    this.name = name;
    this.tags = tags;
    this.myNotes = myNotes;
  }
}

class UserData {
  // accept an options object so we can keep backward compatibility and also
  // assign any extra properties that backend may return (e.g. avatar, bio, role)
  constructor({ courses = [], username = '', userId = null, email = ''} = {}) {
    this.username = username;
    this.userId = userId;
    this.email = email;
    this.courses = courses;
  }
}

const userData = reactive(new UserData());

function mapToUserData(payload) {
  // payload may be the response body or an object like { data: { ... } }
  const body = payload?.data ?? payload ?? {};

  const courses = (body?.courses ?? [])
    .map((c) => new MyCourse(
      c?.name ?? '',
      Array.isArray(c?.tags) ? c.tags : [],
      (c?.myNotes ?? []).map((n) => new MyNote(
        n?.name ?? '',
        n?.file ?? null,
        n?.lessonName ?? c?.name ?? ''
      ))
    ));

  // Build a user data object that preserves any extra fields from backend
  const userDataObj = {
    courses,
    username: body?.username ?? body?.name ?? '',
    userId: body?.userId ?? body?.id ?? null,
    email: body?.email ?? '',
  };

  // copy any other top-level properties from body into the userDataObj
  // (this ensures the three new properties you added will be retained)
  Object.keys(body).forEach((k) => {
    if (!(k in userDataObj)) {
      userDataObj[k] = body[k];
    }
  });

  return new UserData(userDataObj);
}

function ensureUserData(payload) {
  // If it's already an instance, return as-is. Otherwise map to UserData.
  if (payload instanceof UserData) return payload;
  return mapToUserData(payload);
}

async function loadUserData(userId, setNotification) {
  // clear
  userData.courses.splice(0, userData.courses.length);
  if (!userId) {
    return userData;
  }

  try {
    const res = await api.getUserData(userId);
    const mapped = mapToUserData(res);
    userData.courses.splice(0, userData.courses.length, ...mapped.courses);
    userData.username = mapped.username;
    userData.userId = userId;
    userData.email = mapped.email;
    return userData;
  } catch (err) {
    if (typeof setNotification === 'function') {
      setNotification('加载失败', err?.message || '无法获取用户数据', false);
    }
    throw err;
  }
}

export function useUserData() {
  return { userData, loadUserData, mapToUserData };
}

export default useUserData;

// named exports so components can import and ensure they only pass UserData
export { UserData, mapToUserData, ensureUserData };
