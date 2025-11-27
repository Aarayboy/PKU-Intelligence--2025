```js
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
// LinkCategory实例
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
}
```