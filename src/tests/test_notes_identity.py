"""เทสต์การตรวจตัวตนของ Notes Service กับ auth-service — US-31 (#31)

test_notes_api.py ใช้ตัวปลอมแทน auth-service ไฟล์นี้จึงเช็คส่วนที่ตัวปลอมเช็คไม่ได้:
`HttpIdentity` คุย HTTP จริงผ่าน urllib และตีความ response ของ `GET /auth/me` ถูกต้อง
โดยยก auth-service ตัวจริง (SQLite ชั่วคราว) ขึ้นเป็น HTTP server ในเธรดของเทสต์เอง
ไม่ต้องใช้ Docker และไม่ต่อเครือข่ายนอกเครื่อง
"""

import io
import json
import socket
import threading
import time
import urllib.request

import pytest
from flask import Flask, jsonify
from werkzeug.serving import make_server

from identity import HttpIdentity, IdentityUnavailable, identity_from_env
from storage import LocalFileStorage

SECRET = "test-only-secret-that-is-at-least-32-bytes"
FAST_HASH = "scrypt:1024:8:1"  # ค่า cost จริงช้าเกินสำหรับเทสต์ (ดู test_auth_api.py)
MEMBER = {"email": "uploader@up.ac.th", "password": "correct horse", "display_name": "ผู้อัปโหลดตัวจริง"}

NOTE_FORM = {
    "title": "สรุปบทที่ 3",
    "subject_name": "Data Structures",
    "subject_code": "CS201",
    "faculty": "ICT",
    "year_level": "2",
    "lesson": "บทที่ 3 — Linked List",
}


def serve(app):
    """ยก Flask app ขึ้นเป็น HTTP server บนพอร์ตว่าง คืน (base_url, หยุด server)"""
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def stop():
        server.shutdown()
        thread.join()

    return f"http://127.0.0.1:{server.server_port}", stop


@pytest.fixture
def auth_url(make_db_url, auth_create_app):
    app = auth_create_app(
        database_url=make_db_url("auth.db"), secret=SECRET, password_hash_method=FAST_HASH
    )
    url, stop = serve(app)
    yield url
    stop()


@pytest.fixture
def stub_url():
    """auth-service ปลอมที่ตอบผิดปกติ ใช้เช็คว่า HttpIdentity ไม่ตีความ error เป็น "token ใช้ไม่ได้" """
    app = Flask("stub-auth")

    @app.get("/broken/auth/me")
    def broken():
        return jsonify(error="boom"), 500

    @app.get("/not-json/auth/me")
    def not_json():
        return "<html>proxy error</html>", 200

    @app.get("/wrong-shape/auth/me")
    def wrong_shape():
        return jsonify(user="someone"), 200

    @app.get("/slow/auth/me")
    def slow():
        time.sleep(1)
        return jsonify(id=1, display_name="ช้า")

    url, stop = serve(app)
    yield url
    stop()


def login(auth_url):
    """สมัคร + login ผ่าน HTTP จริง คืน (access_token, ฟังก์ชัน logout)"""

    def post(path, payload, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(
            auth_url + path, data=json.dumps(payload).encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read() or b"{}")

    post("/auth/register", MEMBER)
    body = post("/auth/login", {"email": MEMBER["email"], "password": MEMBER["password"]})
    return body["access_token"], lambda: post("/auth/logout", {}, token=body["access_token"])


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


# --- HttpIdentity กับ auth-service ตัวจริง ----------------------------------------------


def test_valid_token_resolves_to_the_account(auth_url):
    token, _logout = login(auth_url)

    user = HttpIdentity(auth_url)(f"Bearer {token}")

    assert user["display_name"] == MEMBER["display_name"]
    assert isinstance(user["id"], int)


def test_logged_out_token_is_rejected_immediately(auth_url):
    token, logout = login(auth_url)
    logout()

    assert HttpIdentity(auth_url)(f"Bearer {token}") is None


@pytest.mark.parametrize("authorization", [None, "", "Bearer not-a-jwt", "Basic dXNlcjpwYXNz"])
def test_missing_or_invalid_token_is_none(auth_url, authorization):
    assert HttpIdentity(auth_url)(authorization) is None


# --- auth-service ตอบผิดปกติต้องเป็น IdentityUnavailable ไม่ใช่ None -------------------------


@pytest.mark.parametrize("path", ["/broken", "/not-json", "/wrong-shape"])
def test_unexpected_auth_response_is_unavailable_not_unauthorized(stub_url, path):
    with pytest.raises(IdentityUnavailable):
        HttpIdentity(stub_url + path)("Bearer anything")


def test_slow_auth_service_times_out_as_unavailable(stub_url):
    with pytest.raises(IdentityUnavailable):
        HttpIdentity(stub_url + "/slow", timeout=0.2)("Bearer anything")


def test_unreachable_auth_service_is_unavailable():
    with pytest.raises(IdentityUnavailable):
        HttpIdentity(f"http://127.0.0.1:{free_port()}")("Bearer anything")


def test_identity_from_env_reads_auth_service_url(monkeypatch):
    monkeypatch.setenv("AUTH_SERVICE_URL", "http://auth-service:5002/")

    assert identity_from_env().me_url == "http://auth-service:5002/auth/me"


# --- ต่อครบทั้งสอง service: สมัคร → login → อัปโหลด → logout → อัปโหลดไม่ได้ ------------------


def test_upload_flow_against_the_real_auth_service(tmp_path, make_db_url, auth_url, notes_create_app):
    notes = notes_create_app(
        database_url=make_db_url("notes.db"),
        storage=LocalFileStorage(str(tmp_path / "storage")),
        identity=HttpIdentity(auth_url),
    ).test_client()
    token, logout = login(auth_url)

    def upload():
        form = {**NOTE_FORM, "uploader_name": "สวมรอย"}
        form["file"] = (io.BytesIO(b"%PDF-1.4 fake note"), "note.pdf", "application/pdf")
        return notes.post(
            "/notes",
            data=form,
            headers={"Authorization": f"Bearer {token}"},
            content_type="multipart/form-data",
        )

    created = upload()
    assert created.status_code == 201
    assert created.get_json()["uploader_name"] == MEMBER["display_name"]

    logout()
    assert upload().status_code == 401
    assert notes.get("/notes").get_json()["count"] == 1
