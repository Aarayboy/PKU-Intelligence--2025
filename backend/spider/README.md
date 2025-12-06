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

触发测试获取课程列表：

```bash
curl -X GET http://127.0.0.1:5001/courses/current-semester
```

触发测试下载选中课程所有文件：

```bash
curl -X GET http://127.0.0.1:5001/courses/test-download   
```
