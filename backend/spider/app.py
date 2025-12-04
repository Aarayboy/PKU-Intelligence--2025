from flask import Flask, jsonify
import spider # 导入爬虫模块
import ddl_spider
import ddl_LLM
import login

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False # 传给前端的json信息直接使用中文，不转义为 Unicode

# 全局复用的 session，但先不登录，等第一次请求再说
_session = None

def get_session():
    """懒加载：第一次用到时才登录，后面复用同一个 session。"""
    global _session
    if _session is not None:
        return _session

    s = login.pku_login_and_get_session(
        login.PKU_USERNAME,
        login.PKU_PASSWORD,
        login.COURSE_BASE_URL
    )
    if s is None:
        print("登录失败")
        return None

    _session = s
    return _session


@app.route('/courses/current-semester', methods=['GET'])
def current_semester_courses():
    session = get_session()
    courses = spider.get_current_semester_course_list(session)
    return jsonify({
        "success": True,
        "message": "课程为空，准备爬取所有课程",
        "courses": courses,
    }), 200


@app.route('/courses/test-download', methods=['GET'])
def test_download_handouts():
    """
    测试下载“课程讲义”接口。
    通过查询参数 ?courseId=1 指定要下载的课程（1 是当前学期列表中的第一个）。
    """

    course_id = 9

    print(f"当前session为:{ _session}")

    files = spider.download_handouts_for_course(_session, course_id, section_names=None, max_files=4, download_root='download')

    return jsonify({
        "success": True,
        "message": f"为课程 {course_id} 下载完成",
        "files": files,
    }), 200


@app.route('/courses/assignments', methods=['GET'])
def current_semester_assignments_raw():
    # 和 current_semester_courses 一样，先拿到已登录 session
    session = get_session()

    texts = ddl_spider.collect_all_assignment_texts(session)

    return jsonify({
        "success": True,
        "count": len(texts),
        "texts": texts,  # 这里就是所有 span/div 的原始字符串
    }), 200


@app.route('/courses/assignments/refresh', methods=['POST'])
def refresh_deadlines():
    """
    示例：
      前端调用这个接口时，后端会：
        1. 用当前登录信息拿 session
        2. 爬取所有课程作业信息
        3. 让 LLM 清洗成统一的 deadlines 结构
        4. 返回给前端（或者在这里顺便写入数据库，再返回 success）
    """
    # 这里的 get_session() 你按自己的登录逻辑来写
    session = get_session()
    user_id = 1

    payload = ddl_LLM.build_deadline_payload_with_llm(session, user_id=user_id)

    # 这里你可以选择：
    #   - 直接把 payload['deadlines'] 写入数据库
    #   - 或者调用内部的 /edit/deadline 逻辑
    #   - 下例中先简单原样返回
    return jsonify({
        "success": True,
        "data": payload,
    }), 200


if __name__ == '__main__':
    # 运行 Flask app
    # debug=True 模式会在修改代码后自动重启服务器
    app.run(host='0.0.0.0', port=5001, debug=True)