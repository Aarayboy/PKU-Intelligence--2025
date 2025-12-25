def test_cloud_requires_credentials(client):
    resp = client.post("/cloud", json={})
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["success"] is False
    assert "必填" in body["error"]


def test_cloud_rejects_non_int_course(client):
    resp = client.post(
        "/cloud",
        json={"userId": 1, "xuehao": "20250001", "password": "pwd", "course": "x"},
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["success"] is False
    assert "course 参数非法" in body["error"]


def test_cloud_missing_userid(client):
    resp = client.post(
        "/cloud", json={"xuehao": "20250001", "password": "pwd", "course": 1}
    )
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_cloud_happy_path_monkeypatched(client, monkeypatch):
    """
    覆盖 /cloud 正常分支，避免真实爬虫和网络调用。
    """
    from backend import app as backend_app

    dummy_schedule = [
        {"name": "Algo", "teacher": "T", "location": "L", "weekType": 1, "times": [1, 2]}
    ]
    monkeypatch.setattr("backend.app.sync_schedule", lambda x, y: dummy_schedule)
    monkeypatch.setattr(
        "backend.app.spider.get_current_semester_course_list",
        lambda session: [{"name": "CourseA"}, {"name": "CourseB"}],
    )

    resp = client.post(
        "/cloud",
        json={"userId": 1, "xuehao": "20250001", "password": "pwd", "course": ""},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["courses"][0]["name"] == "CourseA"

    schedule_resp = client.get("/schedule", query_string={"userId": 1})
    assert schedule_resp.status_code == 200
    schedule = schedule_resp.get_json()["courseTable"]
    assert schedule[0]["name"] == "Algo"
    assert schedule[0]["times"] == [1, 2]

    # 为后续 course 分支准备 _courses
    backend_app._courses = [{"name": "CourseA"}]


def test_cloud_course_download_branch(client, monkeypatch, tmp_path):
    import requests

    # 返回一个带 cookies 属性的 session，避免 AttributeError
    monkeypatch.setattr("backend.app.get_session", lambda x, y: requests.Session())

    dummy_file = tmp_path / "handout.pdf"
    dummy_file.write_bytes(b"content")

    monkeypatch.setattr(
        "backend.app.spider.download_handouts_for_course",
        lambda *args, **kwargs: [str(dummy_file)],
    )
    monkeypatch.setattr(
        "backend.app.ddl_LLM.build_deadline_payload_with_llm",
        lambda session, user_id: {"UserId": user_id, "deadlines": [{"name": "ddl1"}]},
    )
    # 预置 _courses 以便 course idx 取值
    from backend import app as backend_app

    backend_app._courses = [{"name": "CourseA"}]

    resp = client.post(
        "/cloud",
        json={"userId": 1, "xuehao": "20250001", "password": "pwd", "course": 1},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["notes"][0]["status"] == "success"
    assert data["deadlines"][0]["name"] == "ddl1"
