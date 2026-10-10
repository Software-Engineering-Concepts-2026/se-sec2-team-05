"""Unit tests สำหรับ Stats Service (ผู้เขียน: อติชาติ)

ครอบคลุม health, aggregate stats และการอ่านสถิติของโน้ตจาก Notes Service DB
รวมจำนวนคำขอบคุณ (US-28 AC3)
"""

from datetime import datetime
import os

import pytest

from models import Note, build_session_factory
from stats_db import Base as StatsBase, Thank


@pytest.fixture
def client(stats_client):
    # ตัว app ถูกโหลดใน conftest.py เพราะทุก service มี app.py ชื่อซ้ำกัน
    return stats_client


@pytest.fixture
def stats_db(client, monkeypatch):
    session_factory = build_session_factory(os.environ["DATABASE_URL"])
    # ตาราง thanks เป็นของ notes-service (#76) ถ้ายังไม่มีก็สร้างจาก mapping ฝั่ง stats
    StatsBase.metadata.create_all(session_factory.kw["bind"], tables=[Thank.__table__])

    def authenticate(authorization):
        if authorization == "Bearer owner-101":
            return {"id": 101, "display_name": "Owner 101"}

        if authorization == "Bearer owner-102":
            return {"id": 102, "display_name": "Owner 102"}

        return None

    route_globals = client.application.view_functions["get_note_stats"].__globals__
    monkeypatch.setitem(route_globals, "identity", authenticate)

    with session_factory() as session:
        session.query(Thank).delete()
        session.query(Note).delete()
        session.commit()

        note = Note(
            id=9001,
            title="Stats Test Note",
            subject_name="Stats Test Subject",
            subject_code="STATS101",
            faculty="ICT",
            year_level=1,
            lesson="Stats test lesson",
            file_name="stats-test.txt",
            content_type="text/plain",
            size_bytes=18,
            storage_key="stats-test-note.txt",
            uploader_id=101,
            uploader_name="Owner 101",
            view_count=7,
            download_count=3,
        )

        other_note = Note(
            id=9002,
            title="Other Owner Note",
            subject_name="Other Test Subject",
            subject_code="STATS102",
            faculty="ICT",
            year_level=2,
            lesson="Other test lesson",
            file_name="other-test.txt",
            content_type="text/plain",
            size_bytes=13,
            storage_key="other-test-note.txt",
            uploader_id=102,
            uploader_name="Owner 102",
            view_count=4,
            download_count=2,
        )

        session.add_all([note, other_note])
        session.commit()

    yield session_factory

    with session_factory() as session:
        session.query(Thank).delete()
        session.query(Note).delete()
        session.commit()


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["service"] == "stats-service"


def test_health_time_is_valid_iso_timestamp(client):
    body = client.get("/health").get_json()

    # ต้อง parse กลับเป็น datetime ได้ และต้องมี timezone ติดมาด้วย (UTC)
    parsed = datetime.fromisoformat(body["time"])
    assert parsed.tzinfo is not None


def test_stats_returns_expected_shape(client):
    response = client.get("/stats")

    assert response.status_code == 200
    body = response.get_json()
    assert set(body) == {"total_downloads", "total_notes", "top_contributors"}
    assert isinstance(body["total_downloads"], int)
    assert isinstance(body["total_notes"], int)
    assert isinstance(body["top_contributors"], list)


def test_unknown_route_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_counter_write_endpoints_are_not_exposed(client):
    assert client.post("/notes/1/view").status_code == 404
    assert client.post("/notes/1/download").status_code == 404


def test_note_stats_requires_login(client, stats_db):
    response = client.get("/notes/9001/stats")

    assert response.status_code == 401


def test_note_stats_rejects_non_owner(client, stats_db):
    response = client.get(
        "/notes/9001/stats",
        headers={"Authorization": "Bearer owner-102"},
    )

    assert response.status_code == 403


def test_note_stats_returns_404_for_missing_note(client, stats_db):
    response = client.get(
        "/notes/9999/stats",
        headers={"Authorization": "Bearer owner-101"},
    )

    assert response.status_code == 404


def test_note_stats_returns_separate_view_and_download_counts(client, stats_db):
    response = client.get(
        "/notes/9001/stats",
        headers={"Authorization": "Bearer owner-101"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "note_id": 9001,
        "views": 7,
        "downloads": 3,
        "thanks": 0,
    }


def test_note_stats_counts_thanks_of_that_note_only(client, stats_db):
    with stats_db() as session:
        session.add_all([
            Thank(user_id=201, note_id=9001),
            Thank(user_id=202, note_id=9001),
            Thank(user_id=201, note_id=9002),
        ])
        session.commit()

    own = client.get(
        "/notes/9001/stats",
        headers={"Authorization": "Bearer owner-101"},
    )
    other = client.get(
        "/notes/9002/stats",
        headers={"Authorization": "Bearer owner-102"},
    )

    assert own.status_code == 200
    assert own.get_json()["thanks"] == 2
    assert other.get_json()["thanks"] == 1


def test_note_stats_hides_thanks_from_non_owner(client, stats_db):
    with stats_db() as session:
        session.add(Thank(user_id=201, note_id=9001))
        session.commit()

    response = client.get(
        "/notes/9001/stats",
        headers={"Authorization": "Bearer owner-102"},
    )

    assert response.status_code == 403
    assert "thanks" not in response.get_json()
