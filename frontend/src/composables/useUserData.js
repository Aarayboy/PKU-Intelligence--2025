import { reactive } from "vue";
import api from "@/api";

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
  constructor({ courses = [], username = "", userId = null, email = "", deadlines = [], LinkCategorys = [], courseTable = []} = {}) {
    this.username = username;
    this.userId = userId;
    this.email = email;
    this.courses = courses;
    this.deadlines = deadlines.map((d) =>
      new DDL(
        d?.name ?? "",
        d?.deadline ?? "",
        d?.message ?? "",
        d?.status ?? "",
      ),
    );
    this.courseTable = new CourseTable(courseTable);

    this.LinkCategorys = LinkCategorys.map((lc) =>
      new LinkCategory(
        lc?.category ?? "",
        lc?.icon ?? "",
        (lc?.links ?? []).map(
          (l) =>
            new Links(
              l?.name ?? "",
              l?.url ?? "",
              l?.desc ?? "",
              l?.isTrusted ?? false,
            ),
        ),
      ),
    );
  }

  updateCourseTable(courses) {
    this.courseTable = new CourseTable(courses);
  }
}

// For LinksPage
class LinkCategory{
  // category, icon, array of links
  constructor(category="", icon="", links=[]){
    this.category=category;
    this.icon=icon;
    this.links=links;
  }
}
class Link{
  constructor(name="",url="", desc="", isTrusted=false){
    this.name=name;
    this.url=url;
    this.desc=desc;
    this.isTrusted=isTrusted;
  }
}



class DDL{
  constructor(name="",deadline="",message="", status=""){
    this.name=name;
    this.deadline=deadline;
    this.message=message;
    this.status=status;
  }
}

// For CoursePage
class Course {
  constructor({
    id = '',
    name = '',
    teacher = '',
    location = '',
    weekType = 0,
    times = []
  } = {}) {
    this.id = id; // 课程唯一标识
    this.name = name;
    this.teacher = teacher;
    this.location = location; // 上课地点
    this.weekType = weekType; // 周次类型，0-每周，1-单周，2-双周
    this.times = times; // 上课时间数组, 元素为整型，表示其是这周的第几节课
    this.timeIndexes = new Set(this.times); // 用于检测时间冲突
  }

  // 判断当前课程与另一门课程是否时间冲突
  isConflict(otherCourse) {
    for (const index of this.timeIndexes) {
      if (otherCourse.timeIndexes.has(index)) return true;
    }
    return false;
  }

  // 获取周次类型的文本描述
  getTimeText() {
    const getWeekdayAndPeriod = (index) => {
      const weekday = Math.floor(index / 12) + 1; // 1-7（周一到周日）
      const period = (index % 12) + 1; // 1-12（节次）
      return { weekday, period };
    };

    const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    return this.times.map(index => {
      const { weekday, period } = getWeekdayAndPeriod(index);
      return `${weekdays[weekday - 1]} 第${period}节`;
    }).join('、');
  }
}

/**
 * 用户课表总类：管理所有课程，提供课表查询、冲突检测等功能
 */
class CourseTable {
  constructor(courses = []) {
    this.CourseTableMap = new Map(); // 时间索引→课程的映射（快速查询）
    this.allCourses = []; // 存储所有课程的数组
    this.addCourses(courses); // 初始化时添加课程
  }

  // 批量添加课程（支持单个课程或课程数组）
  addCourses(courses) {
    const courseList = Array.isArray(courses) ? courses : [courses];
    courseList.forEach(courseData => {
      const course = new Course(courseData);
      this.allCourses.push(course);
      // 将课程关联到对应的时间索引
      course.times.forEach(time => {
        this.CourseTableMap.set(time, course);
      });
    });
  }

  // 根据星期和节次查询课程
  getCourseByIndex(index) {
    if (!Number.isInteger(index) || index < 0 || index > 83) return null;
    return this.CourseTableMap.get(index) || null;
  }

  // 获取某一天的所有课程
  getCoursesByWeekday(targetWeekday) {
    // 校验目标星期：1-7（周一到周日）
    if (![1, 2, 3, 4, 5, 6, 7].includes(targetWeekday)) return [];
    
    const dayCourses = [];
    // 遍历当天的所有节次索引
    const startIndex = (targetWeekday - 1) * 12;
    const endIndex = targetWeekday * 12 - 1;

    for (let index = startIndex; index <= endIndex; index++) {
      const course = this.getCourseByIndex(index);
      if (course) {
        // 计算当前索引对应的节次（1-12）
        const period = (index % 12) + 1;
        dayCourses.push({ ...course, period, index });
      }
    }
    return dayCourses;
  }

  // 检测所有课程的时间冲突
  checkConflicts() {
    const conflicts = [];
    for (let i = 0; i < this.allCourses.length; i++) {
      for (let j = i + 1; j < this.allCourses.length; j++) {
        if (this.allCourses[i].isConflict(this.allCourses[j])) {
          conflicts.push({
            course1: this.allCourses[i],
            course2: this.allCourses[j]
          });
        }
      }
    }
    return conflicts;
  }
}

const userData = reactive(new UserData());

function mapToUserData(payload) {
  // payload may be the response body or an object like { data: { ... } }
  const body = payload?.data ?? payload ?? {};

  const courses = (body?.courses ?? []).map(
    (c) =>
      new MyCourse(
        c?.name ?? "",
        Array.isArray(c?.tags) ? c.tags : [],
        (c?.myNotes ?? []).map(
          (n) =>
            new MyNote(
              n?.name ?? "",
              n?.file ?? null,
              n?.lessonName ?? c?.name ?? "",
            ),
        ),
      ),
  );

  const deadlines = (body?.deadlines ?? []).map((d) =>
    new DDL(
      d?.name ?? "",
      d?.deadline ?? "",
      d?.message ?? "",
      d?.status ?? "",
    ),
  );

  // Build a user data object that preserves any extra fields from backend
  const userDataObj = {
    courses,
    username: body?.username ?? body?.name ?? "",
    userId: body?.userId ?? body?.id ?? null,
    email: body?.email ?? "",
    
    deadlines,
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

    userData.deadlines.splice(0, userData.deadlines.length, ...mapped.deadlines);

    return userData;
  } catch (err) {
    if (typeof setNotification === "function") {
      setNotification("加载失败", err?.message || "无法获取用户数据", false);
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
