"""Integration tests ของ User & Auth Service — US-05 (#5) และ US-06 (#6)

รันจริงผ่าน Flask test client + SQLite ชั่วคราว เหมือน test_notes_api.py
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text

from auth_tokens import encode_access_token, new_session_id

SECRET = "api-test-secret-that-is-at-least-32-bytes"

# scrypt ตามค่าจริง (N=2^17) ใช้เวลา ~0.4 วินาทีต่อครั้ง เทสต์ในไฟล์นี้ hash หลายสิบครั้ง
# จึงลด cost ลงตอนประกอบ app — ค่าจริงของ production ตรวจแยกไว้ใน
# test_default_app_stores_password_with_production_cost และ test_auth_credentials.py
FAST_HASH = "scrypt:1024:8:1"

MEMBER = {
    "email": "67026168@up.ac.th",
    "password": "correct horse",
    "display_name": "อติชาติ",
}


@pytest.fixture
def db_url(tmp_path):
    return f"sqlite:///{tmp_path / 'auth.db'}"


@pytest.fixture
def make_client(db_url, auth_create_app):
    def make(**overrides):
        options = {
            "database_url": db_url,
            "secret": SECRET,
            "allowed_domains": "up.ac.th",
            "password_hash_method": FAST_HASH,
            **overrides,
        }
        app = auth_create_app(**options)
        app.config.update(TESTING=True)
        return app.test_client()

    return make


@pytest.fixture
def client(make_client):
    return make_client()


def register(client, **overrides):
    return client.post("/auth/register", json={**MEMBER, **overrides})


def login(client, email=MEMBER["email"], password=MEMBER["password"]):
    return client.post("/auth/login", json={"email": email, "password": password})


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def logged_in_token(client):
    register(client)
    return login(client).get_json()["access_token"]


# --- health ---


def test_health(client):
    body = client.get("/health").get_json()

    assert body["status"] == "ok"
    assert body["service"] == "auth-service"


# --- US-05: สมัครสมาชิก ---


def test_register_returns_201_without_any_password_field(client):
    response = register(client)

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] > 0
    assert body["email"] == MEMBER["email"]
    assert body["display_name"] == MEMBER["display_name"]
    assert "password" not in body
    assert "password_hash" not in body


def test_register_stores_only_a_hash(client, db_url):
    register(client)

    stored = create_engine(db_url).connect().execute(text("SELECT password_hash FROM users")).scalar()
    # NFR-004: ในฐานข้อมูลต้องไม่มีรหัสผ่านตัวจริง
    assert MEMBER["password"] not in stored
    assert stored.startswith("scrypt:")


def test_default_app_stores_password_with_production_cost(auth_create_app, db_url):
    # ไม่ส่ง password_hash_method → ต้องได้ cost ตาม ADR-005 ไม่ใช่ค่า default ของ Werkzeug
    app = auth_create_app(database_url=db_url, secret=SECRET)
    app.test_client().post("/auth/register", json=MEMBER)

    stored = create_engine(db_url).connect().execute(text("SELECT password_hash FROM users")).scalar()
    assert stored.startswith("scrypt:131072:8:1$")


def test_register_outside_university_domain_is_rejected(client):
    response = register(client, email="someone@gmail.com")

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "validation_failed"
    assert "@up.ac.th" in body["fields"]["email"]


def test_register_reports_every_invalid_field_at_once(client):
    response = client.post("/auth/register", json={"email": "x@gmail.com", "password": "short"})

    assert response.status_code == 400
    assert set(response.get_json()["fields"]) == {"email", "password", "display_name"}


def test_register_duplicate_email_is_rejected_case_insensitively(client):
    assert register(client).status_code == 201

    response = register(client, email="67026168@UP.AC.TH", display_name="คนอื่น")

    assert response.status_code == 409
    assert response.get_json()["error"] == "email_taken"


def test_register_accepts_form_data_too(client):
    response = client.post("/auth/register", data=MEMBER)

    assert response.status_code == 201


def test_allowed_domains_can_be_configured(make_client):
    client = make_client(allowed_domains="up.ac.th, cmu.ac.th")

    assert register(client, email="someone@cmu.ac.th").status_code == 201
    assert register(client, email="someone@gmail.com").status_code == 400


def test_oversized_request_gets_json_413(client):
    response = client.post("/auth/register", json={**MEMBER, "display_name": "x" * 20_000})

    assert response.status_code == 413
    assert response.get_json()["error"] == "request_too_large"


# --- US-06: login ---


def test_login_returns_bearer_token_valid_for_eight_hours(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    body = response.get_json()
    assert body["token_type"] == "Bearer"
    assert body["access_token"]
    assert body["user"]["email"] == MEMBER["email"]
    lifetime = datetime.fromisoformat(body["expires_at"]) - datetime.now(timezone.utc)
    assert timedelta(hours=7, minutes=59) < lifetime <= timedelta(hours=8)


def test_login_email_is_case_insensitive(client):
    register(client)

    assert login(client, email="67026168@UP.ac.th").status_code == 200


def test_wrong_password_and_unknown_email_look_identical(client):
    # AC ข้อ 3 ของ #6: ไม่บอกว่าผิดที่ช่องไหน ทั้ง status และ body ต้องเหมือนกันทุกไบต์
    register(client)

    wrong_password = login(client, password="wrong horse")
    unknown_email = login(client, email="nobody@up.ac.th")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.get_json() == unknown_email.get_json()
    assert wrong_password.get_json()["error"] == "invalid_credentials"


def test_overlong_password_is_just_invalid_credentials(client):
    register(client)

    response = login(client, password="x" * 10_000)

    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid_credentials"


def test_login_with_empty_fields_says_which_are_empty(client):
    response = client.post("/auth/login", json={})

    assert response.status_code == 400
    assert set(response.get_json()["fields"]) == {"email", "password"}


# --- US-06: คงสถานะ login / ตรวจ token ---


def test_me_returns_the_account_of_the_token(client):
    token = logged_in_token(client)

    response = client.get("/auth/me", headers=bearer(token))

    assert response.status_code == 200
    assert response.get_json()["display_name"] == MEMBER["display_name"]


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer"},
        {"Authorization": "Bearer not-a-jwt"},
        {"Authorization": "Basic dXNlcjpwYXNz"},
    ],
)
def test_me_without_a_valid_bearer_token_is_401(client, headers):
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_expired_token_is_401(make_client):
    # ttl ติดลบ = token หมดอายุตั้งแต่ตอนออก ใช้แทนการรอ 8 ชั่วโมงจริง
    client = make_client(token_ttl=timedelta(seconds=-1))

    token = logged_in_token(client)

    assert client.get("/auth/me", headers=bearer(token)).status_code == 401


def test_validly_signed_token_without_a_session_row_is_401(client):
    # ลายเซ็นถูกแต่ไม่มี session ในฐานข้อมูล — พิสูจน์ว่าการตรวจไม่ได้เชื่อ JWT อย่างเดียว
    register(client)
    token, _ = encode_access_token(
        SECRET, 1, new_session_id(), datetime.now(timezone.utc), timedelta(hours=8)
    )

    assert client.get("/auth/me", headers=bearer(token)).status_code == 401


def test_token_from_another_secret_is_401(make_client, db_url):
    issuer = make_client(secret="some-other-secret-that-is-at-least-32-bytes")
    token = logged_in_token(issuer)

    # ใช้ฐานข้อมูลเดียวกัน session มีอยู่จริง แต่ลายเซ็นไม่ใช่ของ secret นี้
    verifier = make_client()

    assert verifier.get("/auth/me", headers=bearer(token)).status_code == 401


# --- US-06: logout ---


def test_logout_revokes_the_token_immediately(client):
    token = logged_in_token(client)

    assert client.post("/auth/logout", headers=bearer(token)).status_code == 204

    # AC ข้อ 2 ของ #6: token เดิมต้องใช้ไม่ได้ทันที ทั้งที่ JWT ยังไม่หมดอายุ
    assert client.get("/auth/me", headers=bearer(token)).status_code == 401
    assert client.post("/auth/logout", headers=bearer(token)).status_code == 401


def test_logout_only_revokes_its_own_session(client):
    register(client)
    phone = login(client).get_json()["access_token"]
    laptop = login(client).get_json()["access_token"]

    client.post("/auth/logout", headers=bearer(phone))

    assert client.get("/auth/me", headers=bearer(phone)).status_code == 401
    assert client.get("/auth/me", headers=bearer(laptop)).status_code == 200


def test_logout_without_token_is_401(client):
    assert client.post("/auth/logout").status_code == 401


def test_login_again_after_logout_works(client):
    token = logged_in_token(client)
    client.post("/auth/logout", headers=bearer(token))

    fresh = login(client).get_json()["access_token"]

    assert client.get("/auth/me", headers=bearer(fresh)).status_code == 200


# --- การตั้งค่า ---


def test_app_refuses_to_start_without_secret(auth_create_app, db_url, monkeypatch):
    monkeypatch.delenv("AUTH_JWT_SECRET", raising=False)

    with pytest.raises(RuntimeError):
        auth_create_app(database_url=db_url)


@pytest.mark.parametrize("raw", ["abc", "0"])
def test_invalid_ttl_env_refuses_to_start(auth_create_app, db_url, monkeypatch, raw):
    monkeypatch.setenv("AUTH_TOKEN_TTL_HOURS", raw)

    with pytest.raises(RuntimeError):
        auth_create_app(database_url=db_url, secret=SECRET, password_hash_method=FAST_HASH)
