from typing import Dict


def _register_user(client, username="alice", email="alice@example.com", password="secret") -> Dict:
    resp = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    return data["user"]


def test_userdata_default_admin(client):
    resp = client.get("/userdata", query_string={"id": 1})
    assert resp.status_code == 200
    payload = resp.get_json()["data"]
    assert payload["id"] == 1
    assert "deadlines" in payload and isinstance(payload["deadlines"], list)
    assert "linkCategories" in payload and isinstance(payload["linkCategories"], list)
    assert "courseTable" in payload and isinstance(payload["courseTable"], list)


def test_register_and_login_flow(client):
    created = _register_user(client)
    login_resp = client.post(
        "/auth/login",
        json={"username": created["username"], "password": "secret"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()
    assert login_data["success"] is True
    assert login_data["user"]["username"] == created["username"]

    wrong = client.post(
        "/auth/login",
        json={"username": created["username"], "password": "bad-pass"},
    )
    assert wrong.status_code == 401
    assert wrong.get_json()["error"] == "invalid credentials"


def test_register_conflict_returns_409(client):
    _register_user(client, username="bob", email="bob@example.com")
    duplicate = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "secret"},
    )
    assert duplicate.status_code == 409
    assert duplicate.get_json()["error"] == "username or email already exists"


def test_register_conflict_username_or_email_individual(client):
    _register_user(client, username="bob2", email="bob2@example.com")
    same_username = client.post(
        "/auth/register",
        json={"username": "bob2", "email": "other@example.com", "password": "pw"},
    )
    assert same_username.status_code == 409
    same_email = client.post(
        "/auth/register",
        json={"username": "other", "email": "bob2@example.com", "password": "pw"},
    )
    assert same_email.status_code == 409


def test_register_missing_fields(client):
    resp_user = client.post("/auth/register", json={"email": "x@example.com", "password": "pw"})
    resp_email = client.post("/auth/register", json={"username": "u", "password": "pw"})
    resp_pw = client.post("/auth/register", json={"username": "u2", "email": "e@example.com"})
    assert resp_user.status_code == 400
    assert resp_email.status_code == 400
    assert resp_pw.status_code == 400


def test_login_unknown_user_and_bad_payload(client):
    resp = client.post("/auth/login", json={"username": "missing", "password": "pw"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "invalid credentials"

    resp_bad = client.post("/auth/login", data="nonsense", content_type="text/plain")
    assert resp_bad.status_code == 400
    assert "required" in resp_bad.get_json()["error"]


def test_userdata_not_found(client):
    resp = client.get("/userdata", query_string={"id": 999})
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "user not found"


def test_create_course_attaches_to_user(client):
    user = _register_user(client, username="carol", email="carol@example.com")
    course_resp = client.post(
        "/courses/create",
        json={"title": "Algebra", "tags": ["math"], "userId": user["id"]},
    )
    assert course_resp.status_code == 200
    course_data = course_resp.get_json()
    assert course_data["success"] is True
    course = course_data["course"]
    assert course["title"] == "Algebra"
    assert course["user_id"] == user["id"]

    userdata_resp = client.get("/userdata", query_string={"id": user["id"]})
    assert userdata_resp.status_code == 200
    user_payload = userdata_resp.get_json()["data"]
    assert len(user_payload["courses"]) == 1
    assert user_payload["courses"][0]["name"] == "Algebra"
