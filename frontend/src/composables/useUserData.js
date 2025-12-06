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
}

class CourseTable {
  constructor(courses = []) {
    this.CourseTableMap = new Map();
    this.allCourses = [];
    this.addCourses(courses);
  }

  addCourses(courses) {
    const courseList = Array.isArray(courses) ? courses : [courses];
    courseList.forEach(courseData => {
      const course = new Course(courseData);
      this.allCourses.push(course);
      course.times.forEach(time => {
        this.CourseTableMap.set(time, course);
      });
    });
  }

  addCourse(courseData) {
    this.addCourses(courseData);
  }

  removeCourseById(courseId) {
    this.allCourses = this.allCourses.filter(c => c.id !== courseId);
    this.CourseTableMap = new Map();
    this.allCourses.forEach(course => {
      course.times.forEach(time => {
        this.CourseTableMap.set(time, course);
      });
    });
  }

  getCourseByIndex(index) {
    if (!Number.isInteger(index) || index < 0 || index > 83) return null;
    return this.CourseTableMap.get(index) || null;
  }

  getCoursesByWeekday(targetWeekday) {
    if (![1, 2, 3, 4, 5, 6, 7].includes(targetWeekday)) return [];
    
    const dayCourses = [];
    const startIndex = (targetWeekday - 1) * 12;
    const endIndex = targetWeekday * 12 - 1;

    for (let index = startIndex; index <= endIndex; index++) {
      const course = this.getCourseByIndex(index);
      if (course) {
        dayCourses.push({ ...course, period: (index % 12) + 1, index });
      }
    }
    return dayCourses;
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

export function addCourse(courseData) {
  const current = userData.courseTable?.allCourses ?? [];
  // 确保传入是对象，避免引用被直接修改
  const merged = current.concat([courseData]);
  userData.courseTable = new CourseTable(merged);
  return userData.courseTable;
}

export function removeCourse(courseId) {
  const current = userData.courseTable?.allCourses ?? [];
  const filtered = current.filter(c => c.id !== courseId);
  userData.courseTable = new CourseTable(filtered);
  return userData.courseTable;
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

// 模拟数据
export function generateMockSchedule() {
  return [
    {
      id: 1,
      name: '软件工程',
      teacher: '孙老师',
      location: '二教406',
      weekType: 0,
      times: [14, 15, 40, 41]
    },
    {
      id: 2,
      name: '高等数学B',
      teacher: '李老师',
      location: '二教202',
      weekType: 1,
      times: [24, 25, 38, 39]
    },
    {
      id: 3,
      name: '线性代数',
      teacher: '王老师',
      location: '理教301',
      weekType: 2,
      times: [12, 13, 60, 61]
    }
  ];
}

export function useUserData() {
  return { userData, loadUserData, mapToUserData, addCourse, removeCourse };
}

export default useUserData;

// named exports so components can import and ensure they only pass UserData
export { UserData, mapToUserData, ensureUserData };
