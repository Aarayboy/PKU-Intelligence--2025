<script setup>
import { ref, computed, watch } from 'vue';

// 使用 ref 包装数据，使其成为响应式状态
const learningLinks = ref([
  {
    category: "学术研究与资料库",
    icon: "📚",
    links: [
      {
        name: "Google Scholar",
        url: "https://scholar.google.com/",
        desc: "全球论文搜索，查找引文",
        isTrusted: true, 
      },
      {
        name: "CNKI (中国知网)",
        url: "https://www.cnki.net/",
        desc: "中文学术期刊、学位论文",
        isTrusted: true, 
      },
      {
        name: "一个不信任的网站",
        url: "http://untrusted-example.com/",
        desc: "一个会弹出警告的链接",
        isTrusted: false, 
      },
      {
        // 即使是超长的名称，在 UI 中也会被省略号截断，但悬浮时会显示全部
        name: "这是一个超长的链接名称测试截断", 
        url: "http://long-name-test.com/",
        desc: "测试链接名称超出限制时的显示效果",
        isTrusted: false, 
      },
    ],
  },
  {
    category: "在线课程与终身学习",
    icon: "💻",
    links: [
      {
        name: "Coursera",
        url: "https://www.coursera.org/",
        desc: "全球顶级大学专业课程",
        isTrusted: true, 
      },
    ],
  },
  {
    category: "实用工具与作业网站",
    icon: "🛠️",
    links: [
      {
        name: "GitHub",
        url: "https://github.com/",
        desc: "代码托管与开源协作平台",
        isTrusted: true, 
      },
    ],
  },
]);

// --- 状态管理 ---
const isLinkPanelOpen = ref(false); 
const isCategoryPanelOpen = ref(false); 
const isManageLinksPanelOpen = ref(false); 
const currentCategoryToManage = ref(null); 

// 链接确认模态框状态
const isConfirmModalOpen = ref(false);
const linkToOpen = ref(null); 
// 新增：模态框内用户是否选择信任
const shouldTrustInModal = ref(false); 

// 计算初始分类名，作为 newLink.category 的默认值
const initialCategory = learningLinks.value.length > 0 ? learningLinks.value[0].category : '';

const newLink = ref({
  name: '',
  url: '',
  desc: '',
  category: initialCategory,
  isTrusted: true, // 添加链接时默认信任
});

const newCategoryName = ref('');
const newCategoryIcon = ref('💡');

// 所有分类的列表 (计算属性, 确保实时更新)
const categories = computed(() => {
  return learningLinks.value.map(g => g.category);
});

// 计算属性：当前正在管理链接列表
const linksToManage = computed(() => {
  const category = learningLinks.value.find(g => g.category === currentCategoryToManage.value);
  return category ? category.links : [];
});

// --- 互斥逻辑 (更新以包含新的侧边栏) ---
watch(isLinkPanelOpen, (newVal) => {
  if (newVal) {
    isCategoryPanelOpen.value = false;
    isManageLinksPanelOpen.value = false;
  }
});
watch(isCategoryPanelOpen, (newVal) => {
  if (newVal) {
    isLinkPanelOpen.value = false;
    isManageLinksPanelOpen.value = false;
  }
});
watch(isManageLinksPanelOpen, (newVal) => {
  if (newVal) {
    isLinkPanelOpen.value = false;
    isCategoryPanelOpen.value = false;
  }
});


// --- 核心切换方法 (保持不变) ---
const toggleLinkPanel = () => {
    isLinkPanelOpen.value = !isLinkPanelOpen.value;
}

const toggleCategoryPanel = () => {
    isCategoryPanelOpen.value = !isCategoryPanelOpen.value;
}

// 【已修改】：链接管理侧边栏的开关逻辑
const openManageLinksPanel = (categoryName) => {
    // 检查是否点击了当前已打开的分类
    if (isManageLinksPanelOpen.value && currentCategoryToManage.value === categoryName) {
        // 如果是，则关闭面板
        isManageLinksPanelOpen.value = false;
        currentCategoryToManage.value = null; // 清除当前管理分类
    } else {
        // 否则，更新当前管理分类，并打开面板
        currentCategoryToManage.value = categoryName;
        isManageLinksPanelOpen.value = true;
    }
}


// --- 链接确认逻辑 ---
const confirmLinkNavigation = (link) => {
    linkToOpen.value = link;
    
    if (link.isTrusted) {
        window.open(link.url, '_blank');
        linkToOpen.value = null; // 清除状态
    } else {
        // 在打开模态框前，重置 shouldTrustInModal
        shouldTrustInModal.value = false;
        isConfirmModalOpen.value = true;
    }
}

// 核心修改：在打开链接时检查并更新信任状态
const openLink = () => {
    if (linkToOpen.value && linkToOpen.value.url) {
        
        // 检查用户是否勾选了“始终信任该网站”
        if (shouldTrustInModal.value) {
            // 找到该链接并将其 isTrusted 属性设为 true
            learningLinks.value.forEach(group => {
                const foundLink = group.links.find(l => l.url === linkToOpen.value.url);
                if (foundLink) {
                    foundLink.isTrusted = true;
                }
            });
        }

        window.open(linkToOpen.value.url, '_blank');
    }
    closeConfirmModal();
}

const closeConfirmModal = () => {
    isConfirmModalOpen.value = false;
    linkToOpen.value = null; 
    shouldTrustInModal.value = false; // 确保关闭时重置
}


// --- 链接操作方法 ---
const removeLink = (category, url) => {
  const group = learningLinks.value.find(g => g.category === category);
  if (group && confirm(`确定要删除链接 "${group.links.find(l => l.url === url)?.name}" 吗？`)) {
    group.links = group.links.filter(link => link.url !== url);
    // 如果在管理侧边栏删除，需要重新计算 linksToManage
    if (currentCategoryToManage.value === category) {
        currentCategoryToManage.value = category; 
    }
  }
};

/**
 * 添加新链接到指定分类，并进行去重检查
 */
const addLink = () => {
  if (!newLink.value.name || !newLink.value.url || !newLink.value.category) {
    alert("名称、URL 和分类不能为空！");
    return;
  }
  
  // 统一 URL 格式进行比较，默认添加 https://
  let newUrl = newLink.value.url;
  if (!newUrl.startsWith('http://') && !newUrl.startsWith('https://')) {
      newUrl = 'https://' + newUrl;
  }
  
  const group = learningLinks.value.find(g => g.category === newLink.value.category);
  
  if (group) {
    // ------------------- 【链接去重检查】 -------------------
    const nameExists = group.links.some(link => link.name === newLink.value.name);
    const urlExists = group.links.some(link => link.url === newUrl);

    if (nameExists) {
        alert(`添加失败：该分类下已存在名为 "${newLink.value.name}" 的链接！`);
        return;
    }
    
    // 允许同名但不同分类的链接，但 URL 必须全局唯一或至少在同一分类下唯一
    if (urlExists) {
        alert(`添加失败：链接地址 "${newLink.value.url}" 已存在于该分类中！`);
        return;
    }
    // ---------------------------------------------------

    group.links.push({
      name: newLink.value.name,
      url: newUrl, // 使用修正后的 URL
      desc: newLink.value.desc,
      isTrusted: newLink.value.isTrusted, // 保存 isTrusted 属性
    });

    // 重置表单并关闭抽屉
    newLink.value.name = '';
    newLink.value.url = '';
    newLink.value.desc = '';
    newLink.value.category = categories.value.length > 0 ? categories.value[0] : '';
    newLink.value.isTrusted = true; // 重置 isTrusted 为默认值
    isLinkPanelOpen.value = false;
  } else {
    alert("选择的分类不存在！");
  }
};

// 新增：切换链接的信任状态
const toggleLinkTrust = (link) => {
    link.isTrusted = !link.isTrusted;
};


// --- 分类操作方法 ---

/**
 * 添加新分类，并进行去重检查
 */
const addCategory = () => {
  const name = newCategoryName.value.trim();
  if (!name) {
    alert("分类名称不能为空！");
    return;
  }
  
  // ------------------- 【分类去重检查】 -------------------
  if (learningLinks.value.some(g => g.category === name)) {
    alert(`添加失败：分类 "${name}" 已经存在！`);
    return;
  }
  // ---------------------------------------------------

  // 添加新分类
  learningLinks.value.push({
    category: name,
    icon: newCategoryIcon.value || '💡',
    links: [],
  });

  // 重置表单
  newCategoryName.value = '';
  newCategoryIcon.value = '💡';
};

const removeCategory = (categoryName) => {
  if (!confirm(`确定要删除分类 "${categoryName}" 吗？这将会删除该分类下的所有链接！`)) return;

  // 过滤掉需要删除的分类
  learningLinks.value = learningLinks.value.filter(g => g.category !== categoryName);

  // 检查链接模态框的默认分类是否被删除，如果是，则更新它
  if (newLink.value.category === categoryName && learningLinks.value.length > 0) {
    newLink.value.category = learningLinks.value[0].category;
  }
  
  // 如果正在管理被删除的分类，则关闭链接管理面板
  if (currentCategoryToManage.value === categoryName) {
      isManageLinksPanelOpen.value = false;
      currentCategoryToManage.value = null;
  }
};
</script>

<template>
  <div class="p-4 sm:p-6 lg:p-10 bg-gray-50 min-h-screen font-sans">
    <header class="flex justify-between items-center mb-10">
      <h1 class="text-3xl lg:text-4xl font-extrabold text-gray-900 border-b-4 border-indigo-500 pb-2 inline-block">
        🚀 学习链接导航站
      </h1>
      <div class="flex space-x-3">
        <button
          @click="toggleCategoryPanel" 
          class="flex items-center bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
        >
          <span class="text-xl mr-1">⚙️</span> 管理分类
        </button>
        <button
          @click="toggleLinkPanel" 
          class="flex items-center bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
        >
          <span class="text-xl mr-1">+</span> 添加新链接
        </button>
      </div>
    </header>

    <div v-if="learningLinks.length > 0" class="grid gap-6 sm:gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="group in learningLinks"
        :key="group.category"
        class="bg-white rounded-xl shadow-2xl p-6 border-t-4 border-indigo-500 transition-all duration-300 hover:shadow-indigo-300/50"
      >
        <h2
          class="text-xl font-bold text-gray-900 mb-6 flex items-center border-b pb-3 justify-between"
        >
          <div class="flex items-center">
            <span class="mr-3 text-3xl">{{ group.icon }}</span>
            {{ group.category }}
          </div>
          <button @click="openManageLinksPanel(group.category)" class="text-sm text-indigo-500 hover:text-indigo-700 transition">
              管理链接
          </button>
        </h2>

        <ul class="space-y-4">
          <li v-for="link in group.links" :key="link.url">
            <div
              class="relative flex items-center p-4 bg-gray-50 border border-gray-200 rounded-xl transition duration-200 hover:shadow-md hover:border-indigo-400 group/link"
            >
              <a
                @click.prevent="confirmLinkNavigation(link)" 
                href="#"
                target="_blank"
                rel="noopener noreferrer"
                class="flex-grow pr-10 cursor-pointer"
              >
                <div class="font-semibold text-gray-800 group-hover/link:text-indigo-700 transition flex items-center min-w-0">
                  <span :title="link.name" class="truncate pr-2 min-w-0">{{ link.name }}</span>
                  <span v-if="link.isTrusted" class="flex-shrink-0 text-xs font-normal text-green-500 bg-green-100 px-2 py-0.5 rounded-full">信任</span>
                  <span v-else class="flex-shrink-0 text-xs font-normal text-amber-500 bg-amber-100 px-2 py-0.5 rounded-full">外部</span>
                </div>
                <p class="text-sm text-gray-500 mt-1 line-clamp-1">
                    {{ link.desc }}
                </p>
              </a>
              
              <button
                @click.stop.prevent="removeLink(group.category, link.url)"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 opacity-0 group-hover/link:opacity-100 text-red-500 hover:text-red-700 p-1 rounded-full transition duration-300 focus:outline-none"
                aria-label="删除链接"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </li>
          <li v-if="group.links.length === 0" class="text-center text-gray-400 italic p-3">
              该分类下暂无链接
          </li>
        </ul>
      </div>
    </div>
    <div v-else class="text-center p-10 text-gray-500 text-lg border-2 border-dashed border-gray-300 rounded-xl">
        目前没有学习分类，请点击 "管理分类" 添加第一个分类。
    </div>

    <div 
        :class="[
            'fixed top-0 right-0 h-full w-80 lg:w-96 bg-white shadow-2xl z-50 transition-transform duration-500 ease-in-out',
            isLinkPanelOpen ? 'translate-x-0' : 'translate-x-full'
        ]"
    >
        <div class="flex flex-col h-full p-6">
            <div class="flex justify-between items-center border-b pb-4 mb-6 flex-shrink-0">
                <h3 class="text-2xl font-bold text-indigo-600">➕ 添加新链接</h3>
                <button @click="isLinkPanelOpen = false" class="text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <form v-if="categories.length > 0" @submit.prevent="addLink" class="space-y-4 overflow-y-auto pr-2 flex-grow">
                <div>
                    <label for="link-name" class="block text-sm font-medium text-gray-700 mb-1">链接名称 *</label>
                    <input
                    id="link-name"
                    type="text"
                    v-model="newLink.name"
                    placeholder="如：Vue.js 官方文档 (可超长，超长部分会用...代替)"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition"
                    required
                    />
                    <p class="mt-1 text-xs text-gray-500">当前长度: {{ newLink.name.length }} 字符</p>
                </div>
                <div>
                    <label for="link-url" class="block text-sm font-medium text-gray-700 mb-1">链接 URL *</label>
                    <input
                    id="link-url"
                    type="url"
                    v-model="newLink.url"
                    placeholder="如：https://cn.vuejs.org/"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition"
                    required
                    />
                </div>
                <div>
                    <label for="link-desc" class="block text-sm font-medium text-gray-700 mb-1">链接描述</label>
                    <input
                    id="link-desc"
                    type="text"
                    v-model="newLink.desc"
                    placeholder="简短描述该链接的作用"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition"
                    />
                </div>
                <div>
                    <label for="link-category" class="block text-sm font-medium text-gray-700 mb-1">所属分类 *</label>
                    <select
                    id="link-category"
                    v-model="newLink.category"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-indigo-500 focus:border-indigo-500 transition"
                    required
                    >
                    <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                    </select>
                </div>
                <div class="flex items-center space-x-3 pt-2">
                    <input
                        id="is-trusted"
                        type="checkbox"
                        v-model="newLink.isTrusted"
                        class="h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                    />
                    <label for="is-trusted" class="text-sm font-medium text-gray-700">信任该网站（直接打开，不弹警告）</label>
                </div>

                <div class="flex justify-end pt-4 space-x-3 flex-shrink-0">
                    <button
                    type="button"
                    @click="isLinkPanelOpen = false"
                    class="py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition"
                    >
                    取消
                    </button>
                    <button
                    type="submit"
                    class="py-2 px-4 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 shadow-md transition"
                    >
                    确认添加
                    </button>
                </div>
            </form>
            <div v-else class="text-center py-6 text-gray-500 flex-grow">
                请先通过 **“管理分类”** 功能添加至少一个分类。
            </div>
        </div>
    </div>


    <div 
        :class="[
            'fixed top-0 right-0 h-full w-80 lg:w-96 bg-white shadow-2xl z-50 transition-transform duration-500 ease-in-out',
            isCategoryPanelOpen ? 'translate-x-0' : 'translate-x-full'
        ]"
    >
        <div class="flex flex-col h-full p-6">
            <div class="flex justify-between items-center border-b pb-4 mb-6 flex-shrink-0">
                <h3 class="text-2xl font-bold text-gray-600">⚙️ 分类管理</h3>
                <button @click="isCategoryPanelOpen = false" class="text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <form @submit.prevent="addCategory" class="border p-4 rounded-lg bg-indigo-50 mb-6 space-y-3 flex-shrink-0">
                <h4 class="text-lg font-semibold text-indigo-700 border-b pb-1">➕ 添加新分类</h4>
                <div class="flex space-x-2">
                    <div class="flex-shrink-0">
                        <label for="category-icon" class="block text-xs font-medium text-gray-600 mb-1">图标</label>
                         <input
                            id="category-icon"
                            type="text"
                            v-model="newCategoryIcon"
                            placeholder="如: 🚀"
                            maxlength="2"
                            class="w-12 text-center px-1 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition"
                        />
                    </div>
                    <div class="flex-grow">
                         <label for="category-name" class="block text-xs font-medium text-gray-600 mb-1">分类名称 *</label>
                        <input
                            id="category-name"
                            type="text"
                            v-model="newCategoryName"
                            placeholder="如：AI 工具"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition"
                            required
                        />
                    </div>
                   
                </div>
                <button
                    type="submit"
                    class="w-full py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition"
                >
                    创建分类
                </button>
            </form>

            <h4 class="text-lg font-semibold text-gray-700 border-b pb-1 mb-3 flex-shrink-0">➖ 现有分类</h4>
            <ul v-if="learningLinks.length > 0" class="space-y-2 flex-grow overflow-y-auto pr-2">
                <li
                    v-for="group in learningLinks"
                    :key="group.category"
                    class="flex justify-between items-center p-3 bg-gray-50 border border-gray-200 rounded-lg"
                >
                    <span class="font-medium text-gray-800 truncate">{{ group.icon }} {{ group.category }} ({{ group.links.length }})</span>
                    <button
                        @click="removeCategory(group.category)"
                        :disabled="learningLinks.length === 1"
                        :class="[
                            'text-red-500 p-1 rounded-full transition duration-150 flex-shrink-0',
                            learningLinks.length > 1 ? 'hover:bg-red-100 hover:text-red-700' : 'opacity-50 cursor-not-allowed'
                        ]"
                        :title="learningLinks.length === 1 ? '至少保留一个分类' : '删除该分类'"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </li>
            </ul>
            <div v-else class="text-center text-gray-400 italic py-4 flex-grow">
                暂无分类。
            </div>

            <div class="mt-4 pt-3 border-t text-sm text-gray-500 flex-shrink-0">
                注意：删除分类将同时删除该分类下的所有学习链接。
            </div>
        </div>
    </div>
    
    <div 
        :class="[
            'fixed top-0 right-0 h-full w-96 lg:w-[400px] bg-white shadow-2xl z-50 transition-transform duration-500 ease-in-out',
            isManageLinksPanelOpen ? 'translate-x-0' : 'translate-x-full'
        ]"
    >
        <div class="flex flex-col h-full p-6">
            <div class="flex justify-between items-center border-b pb-4 mb-6 flex-shrink-0">
                <h3 class="text-2xl font-bold text-indigo-600 truncate">
                    🔗 管理链接 ({{ currentCategoryToManage }})
                </h3>
                <button @click="isManageLinksPanelOpen = false" class="text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <h4 v-if="linksToManage.length > 0" class="text-lg font-semibold text-gray-700 mb-3 flex-shrink-0">
                切换信任状态
            </h4>
            
            <ul v-if="linksToManage.length > 0" class="space-y-3 flex-grow overflow-y-auto pr-2">
                <li
                    v-for="link in linksToManage"
                    :key="link.url"
                    class="flex items-center p-3 bg-gray-50 border border-gray-200 rounded-lg justify-between"
                >
                    <div class="flex-grow min-w-0 pr-2">
                        <span :title="link.name" class="font-medium text-gray-800 block truncate">{{ link.name }}</span>
                        <span class="text-xs text-gray-500 block truncate">{{ link.url }}</span>
                    </div>

                    <div class="flex items-center space-x-2 flex-shrink-0">
                        <button
                            @click="toggleLinkTrust(link)"
                            :class="[
                                'text-sm font-medium py-1 px-3 rounded-full transition duration-200',
                                link.isTrusted ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                            ]"
                            :title="link.isTrusted ? '点击取消信任，访问时将弹出警告' : '点击设置为信任，将直接打开链接'"
                        >
                            {{ link.isTrusted ? '✅ 信任' : '❌ 外部' }}
                        </button>
                        
                        <button
                            @click="removeLink(currentCategoryToManage, link.url)"
                            class="text-red-500 hover:text-red-700 p-1 rounded-full transition duration-150"
                            title="删除链接"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </li>
            </ul>
            <div v-else class="text-center text-gray-400 italic py-4 flex-grow">
                该分类下暂无链接。
            </div>

            <div class="mt-4 pt-3 border-t text-sm text-gray-500 flex-shrink-0">
                信任网站将直接跳转，不信任网站会弹出安全提示。
            </div>
        </div>
    </div>

    <Transition name="modal-fade">
      <div 
        v-if="isConfirmModalOpen" 
        class="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900 bg-opacity-70 backdrop-blur-sm"
        @click.self="closeConfirmModal"
      >
        <div class="bg-white rounded-lg shadow-xl w-full max-w-sm p-6 transition-all duration-300 transform scale-100">
          
          <div class="flex items-center text-xl font-bold text-red-600 border-b pb-3 mb-4">
            <span class="mr-2">⚠️</span> 外部链接提醒
          </div>

          <div v-if="linkToOpen" class="space-y-3">
            <p class="text-gray-700">您即将访问外部网站：</p>
            <div class="p-3 bg-gray-100 rounded-md border border-gray-300">
                <p class="font-semibold text-indigo-700 break-words">{{ linkToOpen.name }}</p>
                <p class="text-sm text-gray-500 truncate">{{ linkToOpen.url }}</p>
            </div>
            <p class="text-sm text-gray-600 mb-4">
                点击 **"确认跳转"** 将在新标签页中打开链接。
            </p>

            <div class="flex items-center pt-2">
                <input
                    id="modal-trust-checkbox"
                    type="checkbox"
                    v-model="shouldTrustInModal"
                    class="h-5 w-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
                />
                <label for="modal-trust-checkbox" class="ml-2 text-sm font-medium text-gray-700 select-none">
                    始终信任该网站（下次不再提示）
                </label>
            </div>
            
          </div>
          
          <div class="mt-6 flex justify-end space-x-3">
            <button
              @click="closeConfirmModal"
              class="py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition"
            >
              取消
            </button>
            <button
              @click="openLink"
              class="py-2 px-4 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 shadow-md transition"
            >
              确认跳转
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* 样式保持不变 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out;
}
.overflow-y-auto::-webkit-scrollbar {
    width: 8px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: #cbd5e1;
    border-radius: 4px;
}
.overflow-y-auto::-webkit-scrollbar-track {
    background: #f1f5f9;
}

/* Modal 过渡样式 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
/* 可选：给模态框内部内容添加缩放动画 */
.modal-fade-enter-active .bg-white,
.modal-fade-leave-active .bg-white {
    transition: all 0.3s ease-in-out;
}

.modal-fade-enter-from .bg-white,
.modal-fade-leave-to .bg-white {
    transform: scale(0.9);
}
</style>