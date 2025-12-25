from io import BytesIO
from typing import Dict

import pytest


def _register_user(client, username="note-user", email="note@example.com", password="secret") -> Dict:
    resp = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert resp.status_code == 201
    return resp.get_json()["user"]


def _create_course(client, user_id, title="CS101"):
    resp = client.post(
        "/courses/create",
        json={"title": title, "tags": ["tag"], "userId": user_id},
    )
    assert resp.status_code == 200
    return resp.get_json()["course"]


def test_upload_note_validates_fields(client):
    # missing lessonName
    resp = client.post(
        "/notes/upload",
        data={"title": "Week1", "userId": "1"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert "lessonName" in resp.get_json()["error"]

    resp2 = client.post(
        "/notes/upload",
        data={"title": "Week1", "lessonName": "NA"},
        content_type="multipart/form-data",
    )
    assert resp2.status_code == 400
    assert "userId" in resp2.get_json()["error"]


def test_upload_note_rejects_multiple_files(client):
    data = {
        "title": "Week1",
        "lessonName": "CS101",
        "userId": "1",
        "files": [
            (BytesIO(b"a"), "a.txt"),
            (BytesIO(b"b"), "b.txt"),
        ],
    }
    resp = client.post("/notes/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert "只允许上传一个文件" in resp.get_json()["error"]


def test_upload_and_fetch_note_files(client):
    user = _register_user(client, username="fileuser", email="file@example.com")
    _create_course(client, user["id"], title="CS101")

    upload_resp = client.post(
        "/notes/upload",
        data={
            "title": "Lecture1",
            "lessonName": "CS101",
            "userId": str(user["id"]),
            "files": [(BytesIO(b"hello world"), "notes.txt")],
        },
        content_type="multipart/form-data",
    )
    assert upload_resp.status_code == 200
    body = upload_resp.get_json()
    assert body["success"] is True
    assert body["saved_files"] == ["notes.txt"]

    files_resp = client.get(
        "/notes/files",
        query_string={
            "userId": user["id"],
            "lessonName": "CS101",
            "noteName": "Lecture1",
        },
    )
    assert files_resp.status_code == 200
    files_body = files_resp.get_json()
    assert files_body["success"] is True
    assert files_body["files"][0]["name"] == "notes.txt"

    download_resp = client.get(
        "/notes/file",
        query_string={
            "userId": user["id"],
            "lessonName": "CS101",
            "noteName": "Lecture1",
            "filename": "notes.txt",
        },
    )
    assert download_resp.status_code == 200
    assert download_resp.data == b"hello world"


def test_upload_note_to_missing_course_returns_empty_note(client):
    upload_resp = client.post(
        "/notes/upload",
        data={
            "title": "Lecture1",
            "lessonName": "MissingCourse",
            "userId": "1",
            "files": [(BytesIO(b"hello"), "notes.txt")],
        },
        content_type="multipart/form-data",
    )
    assert upload_resp.status_code == 200
    body = upload_resp.get_json()
    # 当前实现不会直接报错，但 note 为 None（不插入数据库）
    assert body["note"] is None


def test_get_notes_files_handles_missing_resources(client):
    resp = client.get(
        "/notes/files",
        query_string={"userId": 1, "lessonName": "Missing", "noteName": "Note"},
    )
    assert resp.status_code == 404
    assert "course not found" in resp.get_json()["error"]


@pytest.mark.xfail(reason="当前实现重命名后不移动文件夹，下载会失败", strict=False)
def test_renamed_course_and_note_should_keep_files_accessible(client):
    user = _register_user(client, username="editor", email="editor@example.com")
    _create_course(client, user["id"], title="CS101")
    client.post(
        "/notes/upload",
        data={
            "title": "Week1",
            "lessonName": "CS101",
            "userId": str(user["id"]),
            "files": [(BytesIO(b"abc"), "w1.txt")],
        },
        content_type="multipart/form-data",
    )

    edit_course_resp = client.post(
        "/edit/course",
        json={"userId": user["id"], "oldname": "CS101", "newname": "CS102"},
    )
    assert edit_course_resp.status_code == 200
    assert edit_course_resp.get_json()["success"] is True

    edit_note_resp = client.post(
        "/edit/note",
        json={
            "userId": user["id"],
            "courseName": "CS102",
            "oldname": "Week1",
            "newname": "Week2",
        },
    )
    assert edit_note_resp.status_code == 200
    assert edit_note_resp.get_json()["success"] is True

    download_resp = client.get(
        "/notes/file",
        query_string={
            "userId": user["id"],
            "lessonName": "CS102",
            "noteName": "Week2",
            "filename": "w1.txt",
        },
    )
    assert download_resp.status_code == 200


def test_links_crud_flow(client):
    user = _register_user(client, username="linker", email="linker@example.com")

    cat_resp = client.post(
        "/links/categories",
        json={"userId": user["id"], "category": "Docs", "icon": "book", "sortOrder": 1},
    )
    assert cat_resp.status_code == 201
    category = cat_resp.get_json()["category"]

    link_resp = client.post(
        "/links",
        json={
            "userId": user["id"],
            "categoryId": category["id"],
            "name": "Homepage",
            "url": "https://example.com",
            "description": "docs",
            "isTrusted": True,
            "sortOrder": 0,
        },
    )
    assert link_resp.status_code == 201
    link_data = link_resp.get_json()["link"]

    list_resp = client.get("/links", query_string={"userId": user["id"]})
    assert list_resp.status_code == 200
    categories = list_resp.get_json()["categories"]
    assert len(categories) == 1
    assert categories[0]["category"] == "Docs"
    assert categories[0]["links"][0]["name"] == "Homepage"
    assert categories[0]["links"][0]["isTrusted"] is True

    del_link = client.delete(f"/links/{link_data['id']}", query_string={"userId": user["id"]})
    assert del_link.status_code == 200
    assert del_link.get_json()["success"] is True

    del_cat = client.delete(
        f"/links/categories/{category['id']}", query_string={"userId": user["id"]}
    )
    assert del_cat.status_code == 200

    final_list = client.get("/links", query_string={"userId": user["id"]}).get_json()["categories"]
    assert final_list == []


def test_links_validation_and_isolation(client):
    user1 = _register_user(client, username="l1", email="l1@example.com")
    user2 = _register_user(client, username="l2", email="l2@example.com")

    missing_category = client.post(
        "/links/categories", json={"userId": user1["id"], "icon": "i"}
    )
    assert missing_category.status_code == 400

    missing_link_fields = client.post(
        "/links",
        json={"userId": user1["id"], "categoryId": 1, "name": "n"},
    )
    assert missing_link_fields.status_code == 400

    cat_resp = client.post(
        "/links/categories",
        json={"userId": user1["id"], "category": "Docs", "icon": "doc"},
    ).get_json()["category"]
    client.post(
        "/links",
        json={
            "userId": user1["id"],
            "categoryId": cat_resp["id"],
            "name": "Site",
            "url": "https://example.com",
        },
    )

    list_user2 = client.get("/links", query_string={"userId": user2["id"]}).get_json()
    assert list_user2["categories"] == []

    delete_resp = client.delete(
        f"/links/categories/{cat_resp['id']}", query_string={"userId": user2["id"]}
    )
    assert delete_resp.status_code == 400
