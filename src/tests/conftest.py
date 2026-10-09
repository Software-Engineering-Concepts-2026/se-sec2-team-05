"""ทำให้ pytest มองเห็นโค้ดของแต่ละ service โดยไม่ต้องติดตั้งเป็น package

ตอนนี้ service ยังเป็น script ธรรมดา ยังไม่มี setup.py/pyproject ให้ pip install -e ได้
จึงเติม path เข้า sys.path ตรง ๆ ไปก่อน เมื่อ service ถูกยกระดับเป็น package จริงให้ลบไฟล์นี้ได้

หมายเหตุสำคัญ: ทุก service มีไฟล์ entrypoint ชื่อ `app.py` เหมือนกันหมด ถ้าปล่อยให้
เทสต์ `import app` ตรง ๆ ตัวไหนอยู่ต้น sys.path ก็จะชนะแล้วอีก service ถูกเทสต์ผิดตัว
(เจอจริงตอนเพิ่ม notes-service — เทสต์ของ stats-service กลายเป็นไปเรียก notes-service)
จึงโหลด `app.py` ของแต่ละ service ด้วย importlib ภายใต้ชื่อโมดูลที่ไม่ซ้ำกัน แล้วส่งต่อ
ให้เทสต์ผ่าน fixture แทน ส่วนโมดูลอื่น (models/storage/validation) ชื่อไม่ชนกันจึง import ปกติได้
— auth-service จึงตั้งชื่อโมดูลเป็น `auth_models`/`auth_tokens`/`credentials` ไม่ใช้
`models`/`tokens` ที่ notes-service ใช้อยู่แล้ว
"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES = REPO_ROOT / "services"

for service in ("stats-service", "notes-service", "auth-service"):
    path = str(SERVICES / service)
    if path not in sys.path:
        sys.path.insert(0, path)

# fizzbuzz.py ไม่มี __init__.py จึงไม่ใช่ package - เติม src/ เข้า sys.path ตรง ๆ
# แทนที่จะพึ่ง `python -m pytest` ที่เติม cwd ให้เอง (CI เรียก `pytest` ตรง ๆ ไม่ผ่าน -m)
SRC = str(REPO_ROOT / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import pytest  # noqa: E402  (ต้องเติม sys.path ให้เสร็จก่อน)

# `app.py` ของ Notes Service สร้าง app ตอน import (gunicorn ต้องการ `app:app`) ซึ่งแปลว่า
# แค่โหลดโมดูลก็จะสร้างไฟล์ DB และโฟลเดอร์ storage ตามค่า default ทันที ชี้ทั้งสองอย่าง
# ไปที่ temp dir ก่อนโหลด เทสต์จะได้ไม่ทิ้งขยะไว้ในรีโปหรือที่ /data บนเครื่องคนรัน
_SANDBOX = Path(tempfile.mkdtemp(prefix="noteshare-tests-"))
# TEST_DATABASE_URL ชี้ไปที่ Postgres จริง (CI job "Unit tests on PostgreSQL") — ถ้าไม่ตั้ง
# ทุกเทสต์ใช้ SQLite ในไฟล์ชั่วคราวเหมือนเดิม · ฐานข้อมูลนี้ถูกล้างทิ้งทุกเทสต์ ห้ามชี้ไปที่ DB ที่มีข้อมูลจริง
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL or f"sqlite:///{_SANDBOX / 'import-time.db'}"
os.environ["NOTES_STORAGE_DIR"] = str(_SANDBOX / "storage")
# auth-service ไม่ยอมสตาร์ตถ้าไม่มี secret (ไม่มีค่า default โดยตั้งใจ) — ค่านี้ใช้แค่ในเทสต์
os.environ["AUTH_JWT_SECRET"] = "test-only-secret-that-is-at-least-32-bytes"


def _load_entrypoint(service: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SERVICES / service / "app.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


stats_app_module = _load_entrypoint("stats-service", "stats_service_app")
notes_app_module = _load_entrypoint("notes-service", "notes_service_app")
auth_app_module = _load_entrypoint("auth-service", "auth_service_app")


def _reset_postgres(url):
    """ล้าง schema ทั้งหมดแล้วสร้างตารางของทุก service ใหม่ ให้แต่ละเทสต์เริ่มจาก DB ว่างเหมือน SQLite

    ตัด connection อื่นของ DB นี้ทิ้งก่อน — engine ของเทสต์ก่อนหน้ายังถือ connection ไว้ใน pool
    ถ้าไม่ตัด DROP SCHEMA จะรอ lock และ connection จะสะสมจนเกิน max_connections
    (engine ของทุก service ตั้ง pool_pre_ping ไว้ connection ที่ถูกตัดจึงถูกเปิดใหม่เอง)
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import NullPool

    from auth_models import Base as AuthBase
    from models import Base as NotesBase, sqlalchemy_url

    engine = create_engine(sqlalchemy_url(url), poolclass=NullPool)
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = current_database() AND pid <> pg_backend_pid()"
            ))
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
        # stats-service อ่านตารางของ notes-service และสร้าง engine ไว้ตั้งแต่ตอน import
        # จึงต้องมีตารางให้ครบเหมือนใน compose ก่อนเทสต์เริ่ม
        NotesBase.metadata.create_all(engine)
        AuthBase.metadata.create_all(engine)
    finally:
        engine.dispose()


@pytest.fixture(autouse=True)
def _fresh_postgres():
    if TEST_DATABASE_URL:
        _reset_postgres(TEST_DATABASE_URL)
    yield


@pytest.fixture
def make_db_url(tmp_path):
    """คืนฟังก์ชันสร้าง database URL ของเทสต์ — SQLite แยกไฟล์ตามชื่อ หรือ Postgres ตัวเดียวกัน

    บน Postgres ทุกชื่อได้ DB เดียวกัน ซึ่งไม่ชนกันเพราะแต่ละ service ใช้ชื่อตารางไม่ซ้ำกัน
    (users/auth_sessions ของ auth, notes/... ของ notes) เหมือนที่รันใน compose
    """

    def make(name="test.db"):
        if TEST_DATABASE_URL:
            return TEST_DATABASE_URL
        return f"sqlite:///{tmp_path / name}"

    return make


@pytest.fixture
def stats_client():
    stats_app_module.app.config.update(TESTING=True)
    return stats_app_module.app.test_client()


@pytest.fixture
def notes_create_app():
    """คืนฟังก์ชัน create_app ของ Notes Service ให้เทสต์ประกอบ app เองตามต้องการ"""
    return notes_app_module.create_app


@pytest.fixture
def auth_create_app():
    """คืนฟังก์ชัน create_app ของ User & Auth Service ให้เทสต์ประกอบ app เองตามต้องการ"""
    return auth_app_module.create_app
