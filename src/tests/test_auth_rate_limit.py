"""เทสต์ rate limit ของ login และสมัครสมาชิก (ADR-011) — RL-01 ถึง RL-12

รันผ่าน Flask test client เหมือน test_auth_api.py ทั้งบน SQLite และ Postgres (`make_db_url`)
นาฬิกาเป็นของปลอมที่เลื่อนเองได้ จึงเทสต์หน้าต่างเวลา 15 นาทีได้โดยไม่ต้องรอจริง
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text

from auth_rate_limit import Limit, RateLimits, limits_from_env
from auth_models import sqlalchemy_url

SECRET = "rate-limit-test-secret-that-is-32-bytes+"
FAST_HASH = "scrypt:1024:8:1"
START = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)

MEMBER = {"email": "67026168@up.ac.th", "password": "correct horse", "display_name": "อติชาติ"}

# เพดานเล็ก ๆ ให้อ่านเทสต์ง่าย — ค่าจริงอยู่ใน RateLimits() (RL-10)
SMALL = RateLimits(
    login_per_email=Limit(3, timedelta(minutes=15)),
    login_per_ip=Limit(5, timedelta(minutes=15)),
    register_per_ip=Limit(3, timedelta(hours=1)),
)


class Clock:
    def __init__(self):
        self.now = START

    def __call__(self):
        return self.now

    def advance(self, **delta):
        self.now += timedelta(**delta)


@pytest.fixture
def db_url(make_db_url):
    return make_db_url("rate-limit.db")


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(db_url, auth_create_app, clock):
    app = auth_create_app(
        database_url=db_url,
        secret=SECRET,
        allowed_domains="up.ac.th",
        password_hash_method=FAST_HASH,
        rate_limits=SMALL,
        clock=clock,
    )
    app.config.update(TESTING=True)
    return app.test_client()


def from_ip(ip):
    # proxy ตัวหน้า service (nginx, Vercel) ต่อท้าย X-Forwarded-For ด้วยที่อยู่ที่มันเห็น
    return {"X-Forwarded-For": ip}


def register(client, ip="10.0.0.1", **overrides):
    return client.post("/auth/register", json={**MEMBER, **overrides}, headers=from_ip(ip))


def login(client, email=MEMBER["email"], password=MEMBER["password"], ip="10.0.0.1"):
    return client.post("/auth/login", json={"email": email, "password": password}, headers=from_ip(ip))


def fail(client, times, **kwargs):
    for _ in range(times):
        assert login(client, password="wrong password", **kwargs).status_code == 401


def test_login_locks_the_email_after_too_many_failures(client):
    """RL-01: ผิดครบเพดานต่ออีเมลแล้วได้ 429 ทันที แม้รหัสถูกก็ไม่ให้เข้า"""
    register(client)
    fail(client, 3)

    response = login(client)

    assert response.status_code == 429
    body = response.get_json()
    assert body["error"] == "rate_limited"
    assert "15 นาที" in body["message"]
    assert int(response.headers["Retry-After"]) == body["retry_after"] == 15 * 60
    assert "access_token" not in body


def test_unknown_email_is_locked_the_same_way(client):
    """RL-02: นับตามอีเมลที่ส่งมา ไม่สนว่ามีบัญชีหรือไม่ — ดูจากคำตอบแยกไม่ออกว่าอีเมลไหนสมัครไว้"""
    register(client)
    fail(client, 3)
    fail(client, 3, email="nobody@up.ac.th", ip="10.0.0.2")

    known = login(client, password="wrong password")
    unknown = login(client, email="nobody@up.ac.th", password="wrong password", ip="10.0.0.2")

    assert known.status_code == unknown.status_code == 429
    assert known.get_json() == unknown.get_json()


def test_lock_ends_when_the_failures_leave_the_window(client, clock):
    """RL-03: Retry-After นับจากครั้งที่ทำให้ครบเพดาน · เลยเวลานั้นแล้ว login ได้ตามปกติ"""
    register(client)
    fail(client, 1)
    clock.advance(minutes=4)
    fail(client, 2)
    clock.advance(minutes=5)

    blocked = login(client)
    # ต้องรอจนครั้งแรก (นาทีที่ 0) หลุดหน้าต่าง 15 นาที — ตอนนี้นาทีที่ 9 เหลือ 6 นาที
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == str(6 * 60)

    clock.advance(minutes=6, seconds=1)
    assert login(client).status_code == 200


def test_successful_login_clears_the_email_counter(client):
    """RL-04: login สำเร็จแล้วล้างตัวนับของอีเมลนั้น ผิดต่ออีก 2 ครั้งยังไม่ถูกล็อก"""
    register(client)
    fail(client, 2)
    assert login(client).status_code == 200

    fail(client, 2)
    assert login(client).status_code == 200


def test_one_ip_guessing_many_accounts_is_limited(client):
    """RL-05: ต่อ IP นับรวมทุกอีเมล · IP อื่นยังเข้าได้ตามปกติ"""
    register(client)
    for i in range(5):
        assert login(client, email=f"guess{i}@up.ac.th", password="x").status_code == 401

    assert login(client).status_code == 429
    assert login(client, ip="10.0.0.2").status_code == 200


def test_client_cannot_dodge_the_ip_limit_with_its_own_forwarded_for(client):
    """RL-06: ใช้ค่าขวาสุดของ X-Forwarded-For (ที่ proxy เติม) ไม่ใช่ค่าที่ client ใส่มาเอง"""
    register(client)
    for i in range(5):
        spoofed = {"X-Forwarded-For": f"203.0.113.{i}, 10.0.0.9"}
        response = client.post("/auth/login", json={"email": f"g{i}@up.ac.th", "password": "x"}, headers=spoofed)
        assert response.status_code == 401

    assert login(client, ip="198.51.100.7, 10.0.0.9").status_code == 429
    # ไม่มี header เลย (เรียก service ตรง) ใช้ที่อยู่ของ connection แทน
    assert client.post("/auth/login", json={"email": MEMBER["email"], "password": MEMBER["password"]}).status_code == 200


def test_register_is_limited_per_ip_including_duplicates(client):
    """RL-07: สมัครนับต่อ IP รวมครั้งที่ชนอีเมลซ้ำ (409 เผยว่าอีเมลมีบัญชี) แต่ไม่นับคำขอที่ไม่ผ่าน validation"""
    assert register(client).status_code == 201
    assert register(client).status_code == 409
    assert register(client, email="bad@gmail.com").status_code == 400
    assert register(client, email="second@up.ac.th").status_code == 201

    blocked = register(client, email="third@up.ac.th")

    assert blocked.status_code == 429
    assert blocked.get_json()["error"] == "rate_limited"
    assert blocked.headers["Retry-After"] == str(60 * 60)
    assert "60 นาที" in blocked.get_json()["message"]
    assert register(client, ip="10.0.0.2", email="third@up.ac.th").status_code == 201


def test_register_limit_resets_after_an_hour(client, clock):
    """RL-08: ครบชั่วโมงนับจากครั้งแรกแล้วสมัครจาก IP เดิมได้อีก"""
    for i in range(3):
        assert register(client, email=f"user{i}@up.ac.th").status_code == 201
    assert register(client, email="late@up.ac.th").status_code == 429

    clock.advance(hours=1, seconds=1)
    assert register(client, email="late@up.ac.th").status_code == 201


def test_old_attempts_are_pruned(client, clock, db_url):
    """RL-09: แถวที่เก่ากว่าหน้าต่างที่ยาวที่สุด (1 ชั่วโมง) ถูกลบตอนบันทึกครั้งถัดไป"""
    fail(client, 2)
    register(client)
    clock.advance(hours=2)
    fail(client, 1)

    engine = create_engine(sqlalchemy_url(db_url))
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT kind, key FROM auth_attempts ORDER BY id")).all()
    engine.dispose()
    assert rows == [("login_failed", "email:67026168@up.ac.th"), ("login_failed", "ip:10.0.0.1")]


def test_overlong_password_counts_as_a_failure(client):
    """RL-10: รหัสผ่านยาวเกินเพดาน (ตอบ 401 โดยไม่ hash) ยังนับเป็นครั้งที่ผิด"""
    register(client)
    for _ in range(3):
        assert login(client, password="x" * 1000).status_code == 401

    assert login(client).status_code == 429


def test_defaults_and_environment_overrides():
    """RL-11: ค่า default ที่ใช้จริง และอ่านค่าจาก environment ได้"""
    default = limits_from_env({})
    assert default == RateLimits()
    assert default.login_per_email == Limit(5, timedelta(minutes=15))
    assert default.login_per_ip == Limit(30, timedelta(minutes=15))
    assert default.register_per_ip == Limit(20, timedelta(hours=1))

    custom = limits_from_env({
        "AUTH_LOGIN_MAX_FAILS_PER_EMAIL": "7",
        "AUTH_LOGIN_MAX_FAILS_PER_IP": "50",
        "AUTH_LOGIN_WINDOW_MINUTES": "10",
        "AUTH_REGISTER_MAX_PER_IP": "40",
        "AUTH_REGISTER_WINDOW_MINUTES": "30",
    })
    assert custom == RateLimits(
        login_per_email=Limit(7, timedelta(minutes=10)),
        login_per_ip=Limit(50, timedelta(minutes=10)),
        register_per_ip=Limit(40, timedelta(minutes=30)),
    )


@pytest.mark.parametrize("raw", ["abc", "0", "-3"])
def test_invalid_limit_env_refuses_to_start(auth_create_app, db_url, monkeypatch, raw):
    """RL-12: ค่าเพดานที่ไม่ใช่จำนวนเต็มบวกทำให้ service ไม่ยอมสตาร์ต แทนที่จะปิด limit ไปเงียบ ๆ"""
    monkeypatch.setenv("AUTH_LOGIN_MAX_FAILS_PER_EMAIL", raw)
    with pytest.raises(RuntimeError, match="AUTH_LOGIN_MAX_FAILS_PER_EMAIL"):
        auth_create_app(database_url=db_url, secret=SECRET, password_hash_method=FAST_HASH)
