from flask import Flask, jsonify, request
import sync_schedule
import login
import spider  # 导入爬虫模块

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # 传给前端的json信息直接使用中文，不转义为 Unicode

# 全局复用的 session，但先不登录，等第一次请求再说
_session = None


def get_session():
    """懒加载：第一次用到时才登录，后面复用同一个 session。"""
    global _session
    if _session is not None:
        return _session

    s = login.pku_login_and_get_session(
        login.PKU_USERNAME, login.PKU_PASSWORD, login.COURSE_BASE_URL
    )
    if s is None:
        print("登录失败")
        return None

    _session = s
    return _session


@app.route("/courses/current-semester", methods=["GET"])
def current_semester_courses():
    session = get_session()
    courses = spider.get_current_semester_course_list(session)
    return (
        jsonify(
            {
                "success": True,
                "message": "课程为空，准备爬取所有课程",
                "courses": courses,
            }
        ),
        200,
    )


@app.route("/courses/test-download", methods=["GET"])
def test_download_handouts():
    """
    测试下载“课程讲义”接口。
    通过查询参数 ?courseId=1 指定要下载的课程（1 是当前学期列表中的第一个）。
    """

    course_id = 9

    print(f"当前session为:{ _session}")
'''
@app.route("/sync", methods=["POST"])
def sync_route():
    payload = request.get_json()
    username = payload.get("username")
    password = payload.get("password")

    ok, data = sync_schedule(username, password)
    if not ok:
        return jsonify(success=False, message=data)

    # 这里你可以只返回 grid，也可以两个都返回
    return jsonify(success=True, schedule=data["grid"], course_list=data["course_list"])
'''
'''
@app.route('/')
def home():
    return 'Welcome to my site!'
'''
if __name__ == '__main__':
    # 运行 Flask app
    # debug=True 模式会在修改代码后自动重启服务器
    app.run(host="0.0.0.0", port=5001, debug=True)
