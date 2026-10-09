"""อัปเกรด schema ของ User & Auth Service ด้วย Alembic ตอน service สตาร์ต (ADR-010)

แทน `Base.metadata.create_all` เดิม — create_all สร้างได้แค่ตารางที่ยังไม่มี เพิ่มคอลัมน์ให้ตารางเดิมไม่ได้
จึงต้อง `docker compose down -v` ทุกครั้งที่ schema เปลี่ยน ซึ่งทำกับ DB จริงบน Vercel (Neon) ไม่ได้

- รันเองทุกครั้งที่สร้าง session factory ไม่มีขั้นตอนแยก เพราะ Vercel ไม่มีจังหวะให้รันคำสั่งก่อน service สตาร์ต
- บน Postgres ถือ advisory lock ระหว่าง migrate ให้หลาย instance (gunicorn worker, Vercel cold start)
  ที่สตาร์ตพร้อมกันรอกันทีละตัว ไม่ใช่ CREATE TABLE ชนกัน
- DB ที่สร้างด้วย create_all ก่อนมี Alembic (มีตาราง `users` แต่ยังไม่มีตาราง version) ถูก stamp เป็น
  baseline ให้เอง แล้วค่อย upgrade ต่อ — schema ของ DB เหล่านั้นต้องตรงกับ baseline (โค้ดก่อน ADR-010)
- ตาราง version ชื่อ `alembic_version_auth` ไม่ใช้ชื่อ default เพราะ notes-service ใช้ DB ก้อนเดียวกันและมีของตัวเอง

ชื่อ `auth_migrate` ไม่ใช่ `migrate` เพราะ notes-service มี `migrate.py` และเทสต์โหลดโมดูลของทุก service
ไว้ใน sys.path เดียวกัน (เหตุผลเดียวกับ `auth_models`, ดู conftest.py)
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
VERSION_TABLE = "alembic_version_auth"
BASELINE_REVISION = "0001"
# มีตารางนี้แต่ไม่มีตาราง version = DB ที่สร้างด้วย create_all ก่อนมี Alembic
LEGACY_TABLE = "users"
# เลขของ pg_advisory_xact_lock — ใช้คนละเลขกับ notes-service จะได้ไม่รอกันโดยไม่จำเป็น
LOCK_KEY = 7_002


def alembic_config(connection=None):
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.attributes["connection"] = connection
    return config


def upgrade_to_head(engine):
    """ทำให้ schema ของ DB นี้เป็นเวอร์ชันล่าสุด ทั้งหมดอยู่ใน transaction เดียว"""
    with engine.begin() as connection:
        if connection.dialect.name == "postgresql":
            # lock หลุดเองตอน transaction จบ ไม่ว่าจะ commit หรือ rollback
            connection.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": LOCK_KEY})
        config = alembic_config(connection)
        tables = set(inspect(connection).get_table_names())
        if VERSION_TABLE not in tables and LEGACY_TABLE in tables:
            command.stamp(config, BASELINE_REVISION)
        command.upgrade(config, "head")
