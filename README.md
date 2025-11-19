# PKU-Intelligence--2025
### 运行说明
#### 后端

依赖下载

```shell
cd backend
pip install -r requirements.txt
```

然后运行`seed_data.py`来创建模拟数据（可选）

```shell
python seed.py
```

最后运行服务

```shell
python app.py
```

获取教学网对应数据

#### 前端

依赖下载

```
cd frontend
npm install
```

运行（开发阶段）

```
npm run dev
```

### 实现细节

后端现在已经采用了数据库来存储信息，数据库位置`/backend/database/database.db`（默认）

上传的文件位于`/backend/uploads/`目录下，命名规则:`userid/course_name/notename/filename`

每次重新运行前最好删掉`database.db`和`uploads/`目录下内容以重新创建

目前前端预览只支持pdf,txt文件，未来可以实现预览office文件 `<iframe :src="https://view.officeapps.live.com/op/view.aspx?src=后面是文件的地址"   frame ></iframe>`

## !TODO!

与做爬虫的同学统一对应接口，实现自动获取课程功能
