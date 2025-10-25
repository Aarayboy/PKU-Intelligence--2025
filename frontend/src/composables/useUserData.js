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
  constructor(courses = []) {
    this.courses = courses;
  }
}

const userData = reactive(new UserData());

function mapToUserData(payload) {
  const courses = (payload?.courses ?? payload?.data?.courses ?? [])
    .map((c) => new MyCourse(
      c?.name ?? '',
      Array.isArray(c?.tags) ? c.tags : [],
      (c?.myNotes ?? []).map((n) => new MyNote(
        n?.name ?? '',
        n?.file ?? null,
        n?.lessonName ?? c?.name ?? ''
      ))
    ));
  return new UserData(courses);
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
