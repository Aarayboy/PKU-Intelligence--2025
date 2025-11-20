<script setup>
import { Edit, User } from "lucide-react";
import api, { EditNote } from "@/api";
import { ref, reactive, inject, watch } from "vue";
const userData = inject("userData");
const fileview = inject("fileview");
const filepath = inject("filepath");
const searchinput = ref(null);
const EditCourseName = ref(new Array(userData.courses.length).fill(false));
const EditNoteName = ref([]);
const UserInput = ref("");

watch(
  () => userData.courses,
  (newCourses) => {
    // 重新映射生成 EditNoteName 的新结构
    EditNoteName.value = newCourses.map((course) =>
      new Array(course.myNotes ? course.myNotes.length : 0).fill(false),
    );
    // console.log("EditNoteName initialized:", EditNoteName.value);
  },
  {
    immediate: true, // 确保组件加载时立即执行一次初始化
    deep: true, // 可选，如果 myNotes 列表本身也会变化，则需要深度监听
  },
);

function DisplayNotesList(index) {
  // 调整svg旋转状态
  const icon = document.getElementById(`icon-${index}`);
  if (icon.classList.contains("rotate-180")) {
    icon.classList.remove("rotate-180");
    icon.classList.add("rotate-0");
  } else {
    icon.classList.remove("rotate-0");
    icon.classList.add("rotate-180");
  }

  // FIX: 使用 .value 访问 ref
  const notesList = document.getElementById(`notes-list-${index}`);
  if (notesList.classList.contains("hidden")) {
    notesList.classList.remove("hidden");
  } else {
    notesList.classList.add("hidden");
  }
}

async function DisplayNoteFile(coursename, notename) {
  // 查找文件路径 (保持原样，但注意查找失败时的 Type Error 风险)
  // 最佳实践应使用 ?. 可选链
  // window.console.log("课程名: ", coursename);
  // window.console.log("笔记名: ", notename);
  // window.console.log("用户ID: ", userData.userId);
  const Filepath = await api
    .getNoteFiles({
      userId: userData.userId,
      lessonName: coursename,
      noteName: notename,
    })
    .then((res) => {
      window.console.log("获取到的文件列表: ", res);
      if (res && res.files && res.files.length > 0) {
        return res.files[0].url; // 假设返回的文件对象中有 url 字段
      } else {
        return null;
      }
    })
    .catch((err) => {
      window.console.error("获取文件路径出错: ", err);
      return null;
    });
  // window.console.log("文件路径: ", Filepath);

  if (Filepath) {
    // FIX: 使用 .value 访问 ref
    fileview.value = true;
    filepath.value = Filepath;
    // window.alert('正在预览文件: ' + Filepath);
  } else {
    window.alert("该笔记暂无文件内容");
  }
}

const SearchHandler = (event) => {
  const query = event.target.value.toLowerCase();

  userData.courses.forEach((course) => {
    let courseMatch =
      course.name.toLowerCase().includes(query) ||
      course.tags.some((tag) => tag.toLowerCase().includes(query));

    // 检查课程下的笔记
    let notesMatch = false;
    if (course.myNotes) {
      course.myNotes.forEach((note) => {
        if (note.name.toLowerCase().includes(query)) {
          notesMatch = true;
        }
      });
    }

    // 显示或隐藏课程项
    const courseElements = document.getElementsByClassName("course-item");
    for (let elem of courseElements) {
      if (elem.querySelector(".course-name").textContent === course.name) {
        if (courseMatch || notesMatch || query === "") {
          elem.style.display = "";
        } else {
          elem.style.display = "none";
        }
      }
    }
  });
};

function Del_Course(Coursename) {
  window.alert("删除课程: " + Coursename);
}
</script>

<template>
  <div id="search-bar" class="mb-4">
    <input
      type="text"
      placeholder="搜索笔记..."
      class="w-full p-2 border rounded-lg"
      id="searchinput"
      @input="SearchHandler"
    />
  </div>

  <div
    id="main-content-wrapper"
    class="relative"
    :class="{ 'flex h-[calc(100vh-80px)] space-x-4': fileview }"
  >
    <div
      id="show-case"
      :class="{
        'overflow-y-auto': true /* 确保列表内容可滚动 */,
      }"
      class="w-full"
    >
      <div id="Notes">
        <div
          v-for="(course, index) in userData.courses"
          :key="index"
          class="course-item p-2 bg-white shadow-sm mb-2"
        >
          <div class="px-4 py-2 flex justify-between items-center border-b">
            <div class="flex items-center flex-wrap">
              <div class="CourseNameContainer">
                <span
                  v-if="!EditCourseName[index]"
                  class="text-lg font-semibold text-gray-800 mr-4 course-name"
                  @dblclick="
                    () => {
                      EditCourseName[index] = true;
                      UserInput = course.name;
                    }
                  "
                >
                  {{ course.name }}
                </span>
                <input
                  v-else
                  ref="EditCourseName[index]"
                  type="text"
                  class="border border-gray-300 rounded px-2 py-1"
                  v-model="UserInput"
                  @keyup.enter="EditCourseName[index] = false"
                  @blur="
                    () => {
                      // console.log('课程名修改为: ', UserInput);
                      EditCourseName[index] = false;
                      api.EditCourse({
                        userId: userData.userId,
                        oldName: course.name,
                        newName: UserInput,
                      });
                      userData.courses[index].name = UserInput;
                      console.log(
                        '课程名已更新为: ',
                        userData.courses[index].name,
                      );
                      UserInput = '';
                    }
                  "
                />
              </div>

              <div class="tags inline-block">
                <span
                  v-for="(tag, tagIndex) in course.tags"
                  :key="tagIndex"
                  class="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full mr-2 mb-1"
                >
                  {{ tag }}
                </span>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <button class="p-1" @click="DisplayNotesList(index)">
                <svg
                  :id="'icon-' + index"
                  class="w-5 h-5 text-gray-600 transition-transform duration-300 rotate-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  ></path>
                </svg>
              </button>

              <button class="p-1" @click="Del_Course">
                <img src="@/assets/trash.svg" class="h-5" />
              </button>
            </div>
          </div>

          <div
            class="notes-list max-h-48 hidden overflow-y-auto"
            :id="'notes-list-' + index"
          >
            <p
              v-if="!course.myNotes || course.myNotes.length === 0"
              class="text-sm text-gray-500 italic px-4 py-2"
            >
              暂无详细笔记内容。
            </p>

            <ul v-else class="space-y-1 p-2">
              <li
                v-for="(note, noteIndex) in course.myNotes"
                :key="noteIndex"
                class="flex items-center text-sm text-gray-700 py-2 px-3 hover:bg-indigo-50 hover:text-indigo-800 rounded-lg transition duration-150 cursor-pointer"
              >
                <svg
                  class="w-3 h-3 mr-2 text-indigo-400 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clip-rule="evenodd"
                  ></path>
                </svg>

                <span class="flex items-center w-full">
                  <span
                    v-if="!EditNoteName[index][noteIndex]"
                    @click="DisplayNoteFile(course.name, note.name)"
                    class="text-base content-center flex-1"
                  >
                    {{ note.name }}
                  </span>
                  <input
                    v-else
                    ref="EditNoteName[index][noteIndex]"
                    type="text"
                    class="border border-gray-300 rounded px-2 py-1 flex-1"
                    v-model="UserInput"
                    @keyup.enter="EditNoteName[index][noteIndex] = false"
                    @blur="
                      () => {
                        EditNoteName[index][noteIndex] = false;
                        api.EditNote({
                          userId: userData.userId,
                          lessonName: course.name,
                          oldName: note.name,
                          newName: UserInput,
                        });
                        userData.courses[index].myNotes[noteIndex].name =
                          UserInput;
                        UserInput = '';
                      }
                    "
                  />
                  <button
                    class="p-1"
                    @click="
                      () => {
                        EditNoteName[index][noteIndex] =
                          !EditNoteName[index][noteIndex];
                        UserInput = note.name;
                      }
                    "
                  >
                    <img src="@/assets/edit.svg" class="h-5" />
                  </button>
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- <div id="Note-content" 
         v-if="fileview" 
         class="flex-grow bg-gray-100 p-4 border rounded-lg shadow-inner overflow-y-auto"
    >
        <div class="flex justify-between items-center mb-4 border-b pb-2">
            <h3 class="text-lg font-semibold text-gray-700 truncate">预览文件: {{ filepath }}</h3>
            <button @click="CloseFileView" class="text-gray-500 hover:text-red-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>

        <iframe 
            :src="filepath" 
            width="100%" 
            height="calc(100% - 60px)" 
            frameborder="0"
            class="rounded-lg"
            title="PDF Document Viewer">
        </iframe>

    </div> -->
  </div>
</template>

<style scoped>
/* 可选：如果你想确保整个页面内容不超过视口高度，可以取消注释 */
/* #main-content-wrapper.flex {
    height: calc(100vh - 80px); 
    /* 假设顶部 header 和 search bar 占据 80px 左右的高度 */
/* } */
</style>
