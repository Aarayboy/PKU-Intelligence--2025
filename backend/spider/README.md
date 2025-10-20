## 使用说明

1. 安装依赖：  
```bash
pip install -r requirements.txt
```

2. 在 login 文件中将你的学号和密码填入对应位置；检查有没有关闭VPN，在开启状态下登录过程会非常慢


3. 运行 Flask 服务器：  
```bash
python app.py
```

4. 触发爬虫：打开另一个终端，使用 curl（或其他 API 工具）向 API 发送一个 POST 请求：  
```bash
curl -X POST http://127.0.0.1:5001/api/start-spider
```

5. 在运行 curl 的终端中预期应该可以看到输出形如：  
```json
{
  "files": [
    "downloads/SlidesCarnival-presentation-template-16-9-1.pptx"
  ],
  "message": "成功下载 1 个文件。",
  "status": "success"
}
```

6. 在运行 Flask 的服务终端中，目前可以看到输出形如：  
```text
收到爬取请求...
-> 访问课程平台首页: https://course.pku.edu.cn/
-> 等待并点击登录按钮，触发跳转...
-> 等待跳转到统一身份认证页面 (iaaa.pku.edu.cn)...
-> 正在输入 IAAA 认证页面的用户名和密码...
-> 正在点击 IAAA 登录...
-> 等待跳转回课程平台 (webapps/portal)...
-> 登录成功，正在提取 Cookies...
-> Cookies 注入 requests Session 成功。
-> 访问课程主页: https://course.pku.edu.cn/
```