<script setup>
// 定义链接数据，方便在模板中循环渲染
const learningLinks = [
  {
    category: "学术研究与资料库",
    icon: "📚",
    links: [
      {
        name: "Google Scholar (谷歌学术)",
        url: "https://scholar.google.com/",
        desc: "全球论文搜索，查找引文",
      },
      {
        name: "CNKI (中国知网)",
        url: "https://www.cnki.net/",
        desc: "中文学术期刊、学位论文",
      },
      {
        name: "Web of Science (WOS)",
        url: "https://clarivate.com/webofsciencegroup/solutions/web-of-science/",
        desc: "引文数据库，核心期刊检索",
      },
      {
        name: "ResearchGate",
        url: "https://www.researchgate.net/",
        desc: "科学社交网络，共享论文",
      },
      {
        name: "arXiv",
        url: "https://arxiv.org/",
        desc: "物理、数学、计算机科学预印本",
      },
      {
        name: "ScienceDirect (Elsevier)",
        url: "https://www.sciencedirect.com/",
        desc: "Elsevier期刊与电子书",
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
      },
      {
        name: "edX",
        url: "https://www.edx.org/",
        desc: "MIT、哈佛等大学的MOOC平台",
      },
      {
        name: "慕课 (MOOCs)",
        url: "https://www.icourse163.org/",
        desc: "国内大学在线课程 (中国大学MOOC)",
      },
      {
        name: "国家智慧教育公共服务平台",
        url: "https://www.smartedu.cn/",
        desc: "国家级中小学、职业、高等教育资源",
      },
      {
        name: "Khan Academy (可汗学院)",
        url: "https://www.khanacademy.org/",
        desc: "免费基础知识教学",
      },
      {
        name: "雨课堂",
        url: "https://www.yuketang.cn/",
        desc: "国内混合式教学工具与平台",
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
      },
      {
        name: "Stack Overflow",
        url: "https://stackoverflow.com/",
        desc: "编程问答社区",
      },
      {
        name: "Overleaf",
        url: "https://www.overleaf.com/",
        desc: "在线 LaTeX 协作编辑",
      },
      {
        name: "Grammarly",
        url: "https://www.grammarly.com/",
        desc: "英文写作语法检查工具",
      },
      {
        name: "DeepL Translate",
        url: "https://www.deepl.com/translator",
        desc: "高质量AI翻译工具",
      },
      {
        name: "Miro/Boardmix",
        url: "https://boardmix.cn/",
        desc: "在线协作白板与思维导图",
      },
    ],
  },
];
</script>

<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <h1 class="text-3xl font-bold text-gray-800 mb-8 border-b pb-2">
      常用学习链接导航
    </h1>

    <div class="grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="group in learningLinks"
        :key="group.category"
        class="bg-white rounded-xl shadow-lg p-6 border border-gray-100 transition-shadow hover:shadow-xl"
      >
        <h2
          class="text-xl font-semibold text-indigo-600 mb-4 flex items-center"
        >
          <span class="mr-2 text-2xl">{{ group.icon }}</span>
          {{ group.category }}
        </h2>

        <ul class="space-y-3">
          <li v-for="link in group.links" :key="link.url">
            <a
              :href="link.url"
              target="_blank"
              rel="noopener noreferrer"
              class="block p-3 border border-gray-200 rounded-lg hover:bg-indigo-50 transition duration-150"
            >
              <div class="font-medium text-gray-800 hover:text-indigo-700">
                {{ link.name }}
              </div>
              <p class="text-sm text-gray-500 mt-1">{{ link.desc }}</p>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 可以在这里添加自定义样式，但 Tailwind CSS 已经处理了大部分布局 */
</style>
