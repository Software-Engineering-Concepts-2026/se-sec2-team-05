"""Integration tests ของ Notes Service — US-08 (#8)

รันจริงผ่าน Flask test client + SQLite ชั่วคราว + โฟลเดอร์ storage ชั่วคราว
ครอบ AC ข้อ 4 โดยเฉพาะ: metadata ที่กรอกต้องใช้เป็นเงื่อนไขค้นหา/กรองได้จริง
"""

import io

import pytest
from werkzeug.datastructures import FileStorage

from storage import LocalFileStorage

BASE_FORM = {
    "title": "สรุปบทที่ 3",
    "subject_name": "Data Structures",
    "subject_code": "CS201",
    "faculty": "ICT",
    "year_level": "2",
    "lesson": "บทที่ 3 — Linked List",
}


@pytest.fixture
def client(tmp_path, notes_create_app):
    app = notes_create_app(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        storage=LocalFileStorage(str(tmp_path / "storage")),
    )
    app.config.update(TESTING=True)
    return app.test_client()


def upload(client, **overrides):
    form = {**BASE_FORM, **overrides}
    form["file"] = (io.BytesIO(b"%PDF-1.4 fake note"), "note.pdf", "application/pdf")
    return client.post("/notes", data=form, content_type="multipart/form-data")


def test_health(client):
    body = client.get("/health").get_json()

    assert body["status"] == "ok"
    assert body["service"] == "notes-service"


def test_upload_with_full_metadata_returns_201_and_echoes_fields(client):
    response = upload(client, topic="Linked List", class_date="2026-08-20")

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] > 0
    assert body["subject_code"] == "CS201"
    assert body["year_level"] == 2
    assert body["topic"] == "Linked List"
    assert body["class_date"] == "2026-08-20"
    assert body["download_url"] == f"/notes/{body['id']}/download"


def test_upload_without_required_metadata_is_rejected_before_saving(client):
    response = client.post(
        "/notes",
        data={"title": "ไม่มีอะไรเลย", "file": (io.BytesIO(b"%PDF-1.4"), "n.pdf", "application/pdf")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "validation_failed"
    assert "subject_code" in body["fields"]
    # ของเสียต้องไม่ถูกบันทึกลงระบบ
    assert client.get("/notes").get_json()["count"] == 0


def test_upload_without_file_is_rejected(client):
    response = client.post("/notes", data=BASE_FORM, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.get_json()["fields"]["file"] == "ต้องแนบไฟล์โน้ต"


def test_uploaded_file_can_be_downloaded_back_unchanged(client):
    note_id = upload(client).get_json()["id"]

    response = client.get(f"/notes/{note_id}/download")

    assert response.status_code == 200
    assert response.data == b"%PDF-1.4 fake note"
    assert "note.pdf" in response.headers["Content-Disposition"]


def test_search_by_keyword_matches_subject_and_lesson(client):
    upload(client)
    upload(client, title="สรุปแคลคูลัส", subject_name="Calculus", subject_code="MA101", lesson="ลิมิต")

    hits = client.get("/notes?q=Calculus").get_json()

    assert hits["count"] == 1
    assert hits["items"][0]["subject_code"] == "MA101"


def test_filter_by_faculty_and_year_level(client):
    upload(client)
    upload(client, faculty="Engineering", year_level="4", subject_code="EN401")

    assert client.get("/notes?faculty=ICT").get_json()["count"] == 1
    assert client.get("/notes?year_level=4").get_json()["items"][0]["subject_code"] == "EN401"
    assert client.get("/notes?faculty=ICT&year_level=4").get_json()["count"] == 0


def test_filter_by_class_date_range(client):
    upload(client, class_date="2026-08-01", subject_code="CS101")
    upload(client, class_date="2026-08-20", subject_code="CS201")

    hits = client.get("/notes?date_from=2026-08-10&date_to=2026-08-31").get_json()

    assert [n["subject_code"] for n in hits["items"]] == ["CS201"]


def test_invalid_filter_value_returns_400_not_500(client):
    assert client.get("/notes?year_level=สอง").status_code == 400
    assert client.get("/notes?date_from=20-08-2026").status_code == 400
    assert client.get("/notes?sort=; DROP TABLE notes").status_code == 400


def test_get_and_download_unknown_note_returns_404(client):
    assert client.get("/notes/999").status_code == 404
    assert client.get("/notes/999/download").status_code == 404


def test_stored_file_name_does_not_trust_user_supplied_path(client, tmp_path):
    form = {**BASE_FORM}
    form["file"] = (io.BytesIO(b"%PDF-1.4"), "../../evil.pdf", "application/pdf")

    note_id = client.post("/notes", data=form, content_type="multipart/form-data").get_json()["id"]

    # ชื่อเดิมยังถูกเก็บไว้แสดงผล แต่ไฟล์จริงต้องอยู่ในโฟลเดอร์ storage เท่านั้น
    assert client.get(f"/notes/{note_id}").get_json()["file_name"] == "../../evil.pdf"
    stored = list((tmp_path / "storage").iterdir())
    assert len(stored) == 1
    assert stored[0].name.endswith(".pdf")
    assert ".." not in stored[0].name


def test_failed_commit_does_not_leave_orphan_file(client, tmp_path, monkeypatch):
    """ถ้า commit ไม่ผ่าน ไฟล์ที่เพิ่งเซฟลง storage ต้องถูกลบตามไปด้วย

    ไม่งั้นทุกครั้งที่ DB ล้ม จะเหลือไฟล์กำพร้าที่ไม่มี record ไหนชี้ถึงและไม่มีใครเก็บกวาด
    """
    from sqlalchemy.orm import Session

    def commit_fails(self):
        raise RuntimeError("db is down")

    monkeypatch.setattr(Session, "commit", commit_fails)
    storage_dir = tmp_path / "storage"

    with pytest.raises(RuntimeError):
        upload(client)

    assert list(storage_dir.iterdir()) == []


def test_negative_limit_and_offset_are_clamped(client):
    """`limit=-1` แปลว่า "ไม่จำกัด" บน SQLite แต่เป็น error บน Postgres จึงต้อง clamp ก่อนถึง SQL"""
    upload(client, subject_code="CS101")
    upload(client, subject_code="CS201")

    assert client.get("/notes?limit=-1").get_json()["count"] == 1
    assert client.get("/notes?offset=-5").get_json()["count"] == 2
    # ขอบบนยังทำงานเหมือนเดิม
    assert client.get("/notes?limit=999").get_json()["count"] == 2


def test_oversized_request_returns_json_413_not_html(client):
    """413 ต้องมี contract เดียวกับ validation error ตัวอื่น ไม่ใช่หน้า HTML ของ Werkzeug"""
    client.application.config["MAX_CONTENT_LENGTH"] = 512

    response = upload(client, description="x" * 1024)

    assert response.status_code == 413
    assert response.get_json()["error"] == "validation_failed"
    assert "file" in response.get_json()["fields"]
