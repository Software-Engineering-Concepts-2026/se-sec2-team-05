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
    """อัปโหลดโน้ตด้วย BASE_FORM — ส่ง `file=` มา override ไฟล์ default (pdf) ได้"""
    form = {**BASE_FORM, **overrides}
    form.setdefault("file", (io.BytesIO(b"%PDF-1.4 fake note"), "note.pdf", "application/pdf"))
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


def test_filter_by_file_type_alone(client):
    upload(client)  # pdf, ICT, year 2 ตาม BASE_FORM

    hits = client.get("/notes?file_type=pdf").get_json()

    assert hits["count"] == 1
    assert hits["items"][0]["content_type"] == "application/pdf"


def test_filter_combined_faculty_year_file_type(client):
    upload(client)  # ตรงทุกเงื่อนไข: ICT, year 2, pdf
    upload(client, faculty="Business", year_level="1", subject_code="BUS101")  # ไม่ตรง faculty/year

    hits = client.get("/notes?faculty=ICT&year_level=2&file_type=pdf").get_json()

    assert hits["count"] == 1
    assert hits["items"][0]["subject_code"] == "CS201"  # จาก BASE_FORM


def test_filter_multiple_file_types_combine_with_or(client):
    upload(client, subject_code="PDF1")  # pdf จาก upload() helper
    upload(
        client,
        subject_code="PNG1",
        file=(io.BytesIO(b"fake-png-bytes"), "note.png", "image/png"),
    )

    # ยืนยันก่อนว่าอัปโหลดได้สองชนิดจริง ไม่ใช่ pdf สองไฟล์ — ไม่งั้นเคสนี้เขียวแบบหลอก
    stored = client.get("/notes").get_json()["items"]
    assert {n["content_type"] for n in stored} == {"application/pdf", "image/png"}

    hits = client.get("/notes?file_type=pdf&file_type=png").get_json()

    assert hits["count"] == 2
    assert {n["subject_code"] for n in hits["items"]} == {"PDF1", "PNG1"}

    # แต่ละชนิดเดี่ยว ๆ ต้องได้แค่ตัวของมัน มิฉะนั้นแปลว่า in_() ไม่ได้กรองจริง
    only_pdf = client.get("/notes?file_type=pdf").get_json()
    only_png = client.get("/notes?file_type=png").get_json()
    assert [n["subject_code"] for n in only_pdf["items"]] == ["PDF1"]
    assert [n["subject_code"] for n in only_png["items"]] == ["PNG1"]


def test_file_type_filter_with_no_match_returns_empty_not_error(client):
    upload(client)  # มีแต่ pdf ในระบบ

    hits = client.get("/notes?file_type=png").get_json()

    assert hits["count"] == 0
    assert hits["items"] == []


def test_invalid_file_type_returns_400_not_500(client):
    response = client.get("/notes?file_type=docx")
    body = response.get_json()

    assert response.status_code == 400
    assert body["error"] == "invalid_filter"
    assert body["field"] == "file_type"


def test_invalid_file_type_mixed_with_valid_still_rejects_whole_request(client):
    """ส่งมาหลายค่าแล้วมีตัวเดียวผิด ต้อง reject ทั้งชุด ไม่ใช่กรองเฉพาะตัวที่ถูก"""
    response = client.get("/notes?file_type=pdf&file_type=docx")

    assert response.status_code == 400


# --- US-19 (#19) แก้ไขโน้ต / US-20 (#20) ลบโน้ต -----------------------------------
# ความเป็นเจ้าของพิสูจน์ด้วย edit token ต่อโน้ต (ADR-004) ระหว่างที่ยังไม่มี Auth Service


def upload_with_token(client, **overrides):
    """อัปโหลดแล้วคืน (note_id, edit_token) — token ออกมาให้ครั้งเดียวตอนสร้าง"""
    body = upload(client, **overrides).get_json()
    return body["id"], body["edit_token"]


def test_create_returns_edit_token_once_and_never_stores_it_plainly(client):
    body = upload(client).get_json()
    token = body["edit_token"]

    assert len(token) >= 32
    # อ่านโน้ตซ้ำต้องไม่มี token หรือ hash ของมันหลุดออกมาอีก
    again = client.get(f"/notes/{body['id']}").get_json()
    assert "edit_token" not in again
    assert "edit_token_hash" not in again
    assert token not in client.get("/notes").get_data(as_text=True)


def test_patch_updates_only_given_fields_and_stamps_updated_at(client):
    note_id, token = upload_with_token(client)
    assert client.get(f"/notes/{note_id}").get_json()["updated_at"] is None

    body = client.patch(
        f"/notes/{note_id}",
        data={"subject_code": "CS202", "topic": "Binary Tree"},
        headers={"X-Note-Token": token},
    ).get_json()

    assert body["subject_code"] == "CS202"
    assert body["topic"] == "Binary Tree"
    # ฟิลด์ที่ไม่ได้ส่งมาต้องคงค่าเดิม
    assert body["subject_name"] == BASE_FORM["subject_name"]
    assert body["lesson"] == BASE_FORM["lesson"]
    assert body["updated_at"] is not None


def test_patch_can_clear_an_optional_field(client):
    note_id, token = upload_with_token(client, topic="เดิม")

    body = client.patch(
        f"/notes/{note_id}", data={"topic": ""}, headers={"X-Note-Token": token}
    ).get_json()

    assert body["topic"] is None


def test_patch_rejects_invalid_value_and_keeps_old_data(client):
    note_id, token = upload_with_token(client)

    response = client.patch(
        f"/notes/{note_id}", data={"year_level": "99"}, headers={"X-Note-Token": token}
    )

    assert response.status_code == 400
    assert "year_level" in response.get_json()["fields"]
    assert client.get(f"/notes/{note_id}").get_json()["year_level"] == 2


def test_patch_ignores_immutable_fields(client):
    note_id, token = upload_with_token(client, uploader_name="อติชาติ")

    body = client.patch(
        f"/notes/{note_id}",
        data={"uploader_name": "คนอื่น", "title": "ชื่อใหม่"},
        headers={"X-Note-Token": token},
    ).get_json()

    assert body["title"] == "ชื่อใหม่"
    assert body["uploader_name"] == "อติชาติ"


def test_patch_with_no_usable_field_returns_400(client):
    note_id, token = upload_with_token(client)

    response = client.patch(f"/notes/{note_id}", data={}, headers={"X-Note-Token": token})

    assert response.status_code == 400
    assert response.get_json()["error"] == "no_fields_to_update"


def test_delete_removes_record_and_file(client, tmp_path):
    note_id, token = upload_with_token(client)
    storage_dir = tmp_path / "storage"
    assert len(list(storage_dir.iterdir())) == 1

    response = client.delete(f"/notes/{note_id}", headers={"X-Note-Token": token})

    assert response.status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404
    assert list(storage_dir.iterdir()) == []


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_edit_and_delete_are_rejected_without_token(client, method):
    note_id, _ = upload_with_token(client)

    response = getattr(client, method)(f"/notes/{note_id}", data={"title": "แอบแก้"})

    assert response.status_code == 403
    assert response.get_json()["error"] == "forbidden"


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_edit_and_delete_are_rejected_with_wrong_token(client, method):
    note_id, _ = upload_with_token(client)

    response = getattr(client, method)(
        f"/notes/{note_id}",
        data={"title": "แอบแก้"},
        headers={"X-Note-Token": "not-the-right-token"},
    )

    assert response.status_code == 403


def test_token_of_one_note_cannot_touch_another_note(client, tmp_path):
    """token ของโน้ตใบหนึ่งต้องใช้กับใบอื่นไม่ได้ — AC "เจ้าของเท่านั้น" ของทั้ง #19 และ #20"""
    mine, my_token = upload_with_token(client, title="โน้ตของฉัน")
    theirs, _ = upload_with_token(client, title="โน้ตของคนอื่น")

    assert client.patch(
        f"/notes/{theirs}", data={"title": "โดนแก้"}, headers={"X-Note-Token": my_token}
    ).status_code == 403
    assert client.delete(f"/notes/{theirs}", headers={"X-Note-Token": my_token}).status_code == 403

    # ของคนอื่นต้องไม่ถูกแตะทั้งใน DB และใน storage
    assert client.get(f"/notes/{theirs}").get_json()["title"] == "โน้ตของคนอื่น"
    assert len(list((tmp_path / "storage").iterdir())) == 2
    # แต่เจ้าของตัวจริงยังใช้ token ของตัวเองกับโน้ตตัวเองได้ตามปกติ
    assert client.delete(f"/notes/{mine}", headers={"X-Note-Token": my_token}).status_code == 204


def test_edit_and_delete_unknown_note_returns_404(client):
    _, token = upload_with_token(client)

    assert client.patch("/notes/999", data={"title": "x"}, headers={"X-Note-Token": token}).status_code == 404
    assert client.delete("/notes/999", headers={"X-Note-Token": token}).status_code == 404
