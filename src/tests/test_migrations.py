"""เทสต์ migration ของ Notes Service และ User & Auth Service (ADR-010) — MG-01 ถึง MG-07

รันได้ทั้ง SQLite และ Postgres (`TEST_DATABASE_URL`) · ข้อที่ต้องใช้ lock ของ Postgres ข้ามบน SQLite
"""

import threading
import time

import pytest
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

import auth_migrate
import migrate
from auth_models import Base as AuthBase, build_session_factory as build_auth
from models import Base as NotesBase, build_session_factory as build_notes, sqlalchemy_url

SERVICES = [
    pytest.param(migrate, NotesBase, build_notes, id="notes"),
    pytest.param(auth_migrate, AuthBase, build_auth, id="auth"),
]
# วินาทีที่ MG-06 รอให้ทุก thread จบ — มี lock ทั้ง 4 ตัวจบในไม่ถึง 2 วินาที
JOIN_TIMEOUT = 30


@pytest.fixture
def empty_url(make_db_url, tmp_path):
    """DB ที่ไม่มีตารางเลย — บน Postgres ล้าง schema ที่ autouse fixture สร้างไว้ทิ้งก่อน"""
    url = make_db_url("migrations.db")
    engine = create_engine(sqlalchemy_url(url))
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
    engine.dispose()
    return url


def engine_for(url):
    return create_engine(sqlalchemy_url(url))


def head_of(module):
    return ScriptDirectory.from_config(module.alembic_config()).get_current_head()


def version_in(engine, module):
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT version_num FROM {module.VERSION_TABLE}")).scalars().all()


@pytest.mark.parametrize("module, base, build", SERVICES)
def test_migrations_build_exactly_the_tables_of_the_models(empty_url, module, base, build):
    """MG-01: upgrade จาก DB ว่างได้ schema ตรงกับ models ทุกคอลัมน์/index/constraint

    ใช้ `alembic check` ผ่าน env.py ตัวจริง ขณะที่ DB มีตารางของทั้งสอง service อยู่ด้วยกัน
    จับได้ทั้งกรณีแก้ models แล้วลืมเขียน revision ใหม่ และกรณี env.py ไปเทียบตารางของอีก service
    """
    from alembic import command

    build_notes(empty_url)
    build_auth(empty_url)
    engine = engine_for(empty_url)

    with engine.connect() as conn:
        command.check(module.alembic_config(conn))
    assert version_in(engine, module) == [head_of(module)]


@pytest.mark.parametrize("module, base, build", SERVICES)
def test_database_made_by_create_all_is_stamped_and_keeps_its_rows(empty_url, module, base, build):
    """MG-02: DB เดิมที่สร้างด้วย create_all (compose เก่า, Neon) ถูก stamp เป็น baseline ข้อมูลไม่หาย"""
    engine = engine_for(empty_url)
    base.metadata.create_all(engine)
    table = module.LEGACY_TABLE
    with engine.begin() as conn:
        if table == "notes":
            conn.execute(text(
                "INSERT INTO notes (title, subject_name, subject_code, faculty, year_level, lesson, file_name,"
                " content_type, size_bytes, storage_key, uploader_id, uploader_name, edit_token_hash,"
                " view_count, download_count, created_at)"
                " VALUES ('old', 's', 'OLD1', 'ICT', 1, 'l', 'a.pdf', 'application/pdf', 1, 'k1', 1, 'u', 'h', 0, 0,"
                " CURRENT_TIMESTAMP)"
            ))
        else:
            conn.execute(text(
                "INSERT INTO users (email, display_name, password_hash, created_at)"
                " VALUES ('old@up.ac.th', 'Old', 'x', CURRENT_TIMESTAMP)"
            ))

    build(empty_url)

    assert version_in(engine, module) == [head_of(module)]
    with engine.connect() as conn:
        assert conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one() == 1


@pytest.mark.parametrize("module, base, build", SERVICES)
def test_second_start_changes_nothing(empty_url, module, base, build):
    """MG-03: สตาร์ตซ้ำ (restart, cold start รอบถัดไป) ไม่ error และไม่เพิ่มแถว version"""
    build(empty_url)
    build(empty_url)

    assert version_in(engine_for(empty_url), module) == [head_of(module)]


def test_both_services_share_one_database_with_separate_version_tables(empty_url):
    """MG-04: notes และ auth อยู่ DB เดียวกันได้ (compose, Neon) ต่างคนต่างนับเวอร์ชันของตัวเอง"""
    build_notes(empty_url)
    build_auth(empty_url)
    engine = engine_for(empty_url)

    tables = set(inspect(engine).get_table_names())
    assert {"alembic_version_notes", "alembic_version_auth", "notes", "users"} <= tables
    assert "alembic_version" not in tables
    assert version_in(engine, migrate) == [head_of(migrate)]
    assert version_in(engine, auth_migrate) == [head_of(auth_migrate)]


@pytest.mark.parametrize("module, base, build", SERVICES)
def test_downgrade_to_base_removes_only_this_services_tables(empty_url, module, base, build):
    """MG-05: downgrade() ของ baseline ลบครบและไม่แตะตารางของอีก service · upgrade กลับได้"""
    from alembic import command

    build_notes(empty_url)
    build_auth(empty_url)
    engine = engine_for(empty_url)
    other = AuthBase if base is NotesBase else NotesBase

    with engine.begin() as conn:
        command.downgrade(module.alembic_config(conn), "base")
    tables = set(inspect(engine).get_table_names())
    assert not (set(base.metadata.tables) & tables)
    assert set(other.metadata.tables) <= tables

    build(empty_url)
    assert set(base.metadata.tables) <= set(inspect(engine).get_table_names())


@pytest.mark.parametrize("module, base, build", SERVICES)
def test_instances_starting_together_migrate_one_at_a_time(empty_url, module, base, build):
    """MG-06: 4 instance สตาร์ตพร้อมกันบน DB ว่าง (gunicorn worker, Vercel cold start) ไม่ชนกัน

    ต้องใช้ advisory lock ของ Postgres — SQLite ล็อกทั้งไฟล์อยู่แล้วและไม่ใช่ DB ของ production
    ถ้าไม่มี lock บางรอบ thread จะชน DuplicateTable บางรอบจะค้างอยู่ใน CREATE TABLE ไม่จบเอง
    จึงรอรวมกันแค่ JOIN_TIMEOUT แล้วให้เทสต์ล้มแทนที่จะค้างทั้ง job (thread เป็น daemon
    ไม่กั้น pytest ตอนจบ และ autouse fixture ของเทสต์ถัดไปตัด connection ที่ค้างทิ้งให้)
    """
    if engine_for(empty_url).dialect.name != "postgresql":
        pytest.skip("advisory lock มีเฉพาะ Postgres")
    errors = []
    start = threading.Barrier(4)

    def boot():
        try:
            start.wait()
            build(empty_url)
        except Exception as exc:  # เก็บไว้ดูว่า thread ไหนล้มเพราะอะไร
            errors.append(exc)

    threads = [threading.Thread(target=boot, daemon=True) for _ in range(4)]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + JOIN_TIMEOUT
    for thread in threads:
        thread.join(max(0, deadline - time.monotonic()))

    assert [thread for thread in threads if thread.is_alive()] == []
    assert errors == []
    assert version_in(engine_for(empty_url), module) == [head_of(module)]


@pytest.mark.parametrize("module, base, build", SERVICES)
def test_revisions_form_one_line_from_the_baseline(module, base, build):
    """MG-07: revision ต่อกันเป็นเส้นเดียว มี head เดียว และเริ่มจาก baseline ที่ migrate.py ใช้ stamp"""
    script = ScriptDirectory.from_config(module.alembic_config())

    assert len(script.get_heads()) == 1
    assert script.get_base() == module.BASELINE_REVISION
