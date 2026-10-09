"""Alembic environment ของ User & Auth Service (ADR-010)

รันได้สองทาง:
- จาก `auth_migrate.upgrade_to_head()` ตอน service สตาร์ต — ส่ง connection ที่ถือ lock อยู่มาทาง config.attributes
- จาก CLI ในโฟลเดอร์ `services/auth-service/` เช่น `alembic revision --autogenerate -m "..."` ตอนเพิ่มคอลัมน์
  (อ่าน URL จาก `DATABASE_URL`)

DB ก้อนเดียวกันมีตารางของ notes-service อยู่ด้วย จึงเทียบ/สร้างเฉพาะตารางที่อยู่ใน metadata ของ service นี้
ไม่อย่างนั้น autogenerate จะเสนอให้ drop `notes` และตารางอื่นของ notes-service
"""

import os

from alembic import context
from sqlalchemy import create_engine

from auth_migrate import VERSION_TABLE
from auth_models import Base, sqlalchemy_url

config = context.config
target_metadata = Base.metadata


def include_name(name, type_, parent_names):
    if type_ == "table":
        return name in target_metadata.tables
    return True


def run_with(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table=VERSION_TABLE,
        include_name=include_name,
        compare_type=True,
        # SQLite แก้คอลัมน์ในตารางเดิมไม่ได้ ต้องสร้างตารางใหม่แล้วย้ายข้อมูล (batch mode)
        render_as_batch=connection.dialect.name == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise SystemExit("ไม่รองรับ offline mode (--sql) — รันกับ DB จริงผ่าน DATABASE_URL")

shared_connection = config.attributes.get("connection")
if shared_connection is not None:
    run_with(shared_connection)
else:
    engine = create_engine(sqlalchemy_url(os.environ["DATABASE_URL"]))
    with engine.begin() as connection:
        run_with(connection)
