"""Tests ของการอัปโหลดตรงเข้า Vercel Blob (ADR-012) — BU-01 ถึง BU-16

browser ขอ client token จาก POST /notes/uploads → ส่งไฟล์ตรงเข้า Blob → POST /notes แบบ JSON
ส่วน Blob ใช้ client ปลอมจาก test_vercel_deploy.py ไฟล์ที่ "browser อัปโหลด" จึงจำลองด้วย
`client.put(...)` ตรง ๆ แบบเดียวกับที่ Blob จะมีไฟล์นั้นหลัง PUT สำเร็จ
"""

import base64
import hashlib
import hmac
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import pytest

from storage import BlobFileStorage, LocalFileStorage, generate_client_token, store_id_from_token
from test_notes_api import AUTH_HEADER, BASE_FORM, MEMBER, FakeIdentity
from test_vercel_deploy import FakeBlobClient, FakeNotFound

RW_TOKEN = "vercel_blob_rw_StoreAbc123_s3cretPart"
NOW = 1_800_000_000.0
TEN_MB = 10 * 1024 * 1024
PDF = {"file_name": "week3.pdf", "content_type": "application/pdf", "size_bytes": 9 * 1024 * 1024}


def decode_client_token(token):
    """แยก client token กลับเป็น (store_id, ลายเซ็น, payload ที่ยังเป็น base64, payload ที่ถอดแล้ว)"""
    prefix = "vercel_blob_client_"
    assert token.startswith(prefix)
    store_id, secured = token[len(prefix):].split("_", 1)
    signature, payload = base64.b64decode(secured).decode().split(".", 1)
    return store_id, signature, payload, json.loads(base64.b64decode(payload))


@pytest.fixture
def blob_client():
    return FakeBlobClient()


@pytest.fixture
def make_app(make_db_url, notes_create_app, blob_client):
    def build(storage=None):
        storage = storage or BlobFileStorage(blob_client, FakeNotFound, RW_TOKEN, clock=lambda: NOW)
        app = notes_create_app(database_url=make_db_url("test.db"), storage=storage, identity=FakeIdentity())
        app.config.update(TESTING=True)
        return app.test_client()

    return build


def start(client, body=PDF, headers=AUTH_HEADER):
    return client.post("/notes/uploads", json=body, headers=headers)


def browser_put(blob_client, ticket, data=b"%PDF-1.4 direct", content_type="application/pdf"):
    """สิ่งที่ Blob มีหลัง browser PUT ไฟล์ด้วย client token สำเร็จ"""
    blob_client.put(ticket["pathname"], data, access="private", content_type=content_type)


def finish(client, ticket, **extra):
    body = {**BASE_FORM, "file_name": "week3.pdf", "upload_pathname": ticket["pathname"], **extra}
    return client.post("/notes", json=body, headers=AUTH_HEADER)


# --- client token ---


def test_client_token_is_signed_like_vercel_blob():
    """BU-01: รูปแบบเดียวกับ generateClientTokenFromReadWriteToken ของ @vercel/blob 2.8.0"""
    token = generate_client_token(
        RW_TOKEN, pathname="uploads/7/a.pdf", maximum_size_in_bytes=TEN_MB,
        allowed_content_types=["application/pdf"], valid_until_ms=1234,
    )

    store_id, signature, payload, decoded = decode_client_token(token)
    assert store_id == "StoreAbc123"
    assert signature == hmac.new(RW_TOKEN.encode(), payload.encode(), hashlib.sha256).hexdigest()
    assert decoded == {
        "pathname": "uploads/7/a.pdf",
        "maximumSizeInBytes": TEN_MB,
        "allowedContentTypes": ["application/pdf"],
        "addRandomSuffix": False,
        "allowOverwrite": False,
        "validUntil": 1234,
    }
    # token ไม่มี read-write token ตัวจริงติดไปถึง browser
    assert "s3cretPart" not in token and "s3cretPart" not in base64.b64decode(token.split("_", 4)[4]).decode()


@pytest.mark.parametrize("bad", ["", "vercel_blob_rw", "vercel_blob_rw__x", "abc"])
def test_store_id_needs_a_read_write_token(bad):
    """BU-02: token ผิดรูปแบบ → error ตอนออก token ไม่ใช่ token เสียที่ Blob ปฏิเสธทีหลัง"""
    with pytest.raises(ValueError):
        store_id_from_token(bad)


# --- POST /notes/uploads ---


def test_upload_ticket_needs_login(make_app):
    """BU-03"""
    response = start(make_app(), headers={})

    assert response.status_code == 401


def test_upload_ticket_on_blob_allows_one_file_for_ten_minutes(make_app):
    """BU-04: token ผูกกับ pathname ใต้ uploads/<id ของผู้ใช้>/ ชนิดเดียว ขนาดไม่เกิน 10 MB"""
    response = start(make_app())

    assert response.status_code == 200
    ticket = response.get_json()
    assert ticket["mode"] == "direct"
    assert ticket["max_file_bytes"] == TEN_MB
    assert re.fullmatch(rf"uploads/{MEMBER['id']}/[0-9a-f]{{32}}\.pdf", ticket["pathname"])
    url = urlparse(ticket["upload_url"])
    assert (url.scheme, url.netloc, url.path) == ("https", "vercel.com", "/api/blob/")
    assert parse_qs(url.query) == {"pathname": [ticket["pathname"]]}
    assert ticket["store_id"] == "StoreAbc123"
    assert ticket["api_version"] == "12"

    _, _, _, payload = decode_client_token(ticket["client_token"])
    assert payload["pathname"] == ticket["pathname"]
    assert payload["allowedContentTypes"] == ["application/pdf"]
    assert payload["maximumSizeInBytes"] == TEN_MB
    assert payload["allowOverwrite"] is False
    assert payload["validUntil"] == ticket["expires_at"] == int((NOW + 600) * 1000)


def test_each_ticket_gets_its_own_file(make_app):
    """BU-05"""
    client = make_app()

    assert start(client).get_json()["pathname"] != start(client).get_json()["pathname"]


@pytest.mark.parametrize("body, reason", [
    ({**PDF, "size_bytes": TEN_MB + 1}, "ไฟล์ใหญ่เกิน 10 MB"),
    ({**PDF, "size_bytes": 0}, "ไฟล์ว่าง"),
    ({**PDF, "size_bytes": "9"}, "ไฟล์ว่าง"),
    ({**PDF, "content_type": "image/gif"}, "รองรับเฉพาะ application/pdf, image/jpeg, image/png"),
])
def test_upload_ticket_checks_the_declared_file(make_app, body, reason):
    """BU-06: ไฟล์ที่ประกาศมาไม่ผ่าน → ไม่ออก token เลย"""
    response = start(make_app(), body=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "validation_failed", "fields": {"file": reason}}


def test_upload_ticket_on_local_disk_says_use_the_form(make_app, tmp_path):
    """BU-07: compose ไม่มี Blob → หน้าเว็บส่งไฟล์มาในฟอร์มเหมือนเดิม เต็ม 10 MB"""
    client = make_app(LocalFileStorage(str(tmp_path / "files")))

    response = start(client)

    assert response.get_json() == {"mode": "form", "max_file_bytes": TEN_MB}


# --- POST /notes แบบ JSON ---


def test_note_from_direct_upload(make_app, blob_client):
    """BU-08: ขนาดและชนิดมาจาก Blob เอง ได้ edit token แบบเดียวกับการอัปโหลดผ่านฟอร์ม"""
    client = make_app()
    ticket = start(client).get_json()
    browser_put(blob_client, ticket, data=b"%PDF-1.4 " + b"x" * 5000)

    response = finish(client, ticket, size_bytes=1, year_level=2)

    assert response.status_code == 201
    note = response.get_json()
    assert note["size_bytes"] == 5009
    assert note["content_type"] == "application/pdf"
    assert note["file_name"] == "week3.pdf"
    assert note["uploader_name"] == MEMBER["display_name"]
    assert note["year_level"] == 2
    assert note["edit_token"]
    assert client.get(f"/notes/{note['id']}/download").data == blob_client.blobs[ticket["pathname"]]


def test_direct_note_checks_the_metadata(make_app, blob_client):
    """BU-09: ฟิลด์ผิดได้ error รายฟิลด์เหมือนฟอร์ม และไฟล์ใน Blob ยังอยู่ให้กดส่งใหม่ได้"""
    client = make_app()
    ticket = start(client).get_json()
    browser_put(blob_client, ticket)

    response = finish(client, ticket, title=" ", year_level=True)

    assert response.status_code == 400
    assert set(response.get_json()["fields"]) == {"title", "year_level"}
    assert ticket["pathname"] in blob_client.blobs


@pytest.mark.parametrize("pathname", [
    "uploads/8/0123456789abcdef0123456789abcdef.pdf",  # ไฟล์ที่ออก token ให้คนอื่น
    "0123456789abcdef0123456789abcdef.pdf",  # ไฟล์ของโน้ตที่อัปโหลดผ่านฟอร์ม
    "previews/uploads/7/0123456789abcdef0123456789abcdef.pdf.png",
    "uploads/7/../8/0123456789abcdef0123456789abcdef.pdf",
    "",
])
def test_direct_note_only_takes_this_users_upload(make_app, blob_client, pathname):
    """BU-10: pathname ที่ไม่ได้ออกให้ผู้ใช้คนนี้ → 400 และไม่แตะไฟล์นั้น"""
    blob_client.put(pathname or "x", b"%PDF-1.4", access="private", content_type="application/pdf")
    before = dict(blob_client.blobs)

    response = finish(make_app(), {"pathname": pathname})

    assert response.status_code == 400
    assert response.get_json()["fields"] == {"file": "ไม่พบไฟล์ที่อัปโหลด กรุณาอัปโหลดใหม่"}
    assert blob_client.blobs == before


def test_direct_note_when_the_file_never_arrived(make_app):
    """BU-11: ได้ token แต่ PUT ไม่สำเร็จ (ปิดแท็บ, เน็ตหลุด)"""
    client = make_app()
    ticket = start(client).get_json()

    response = finish(client, ticket)

    assert response.status_code == 400
    assert response.get_json()["fields"] == {"file": "ไม่พบไฟล์ที่อัปโหลด กรุณาอัปโหลดใหม่"}


@pytest.mark.parametrize("data, content_type, reason", [
    (b"x" * (TEN_MB + 1), "application/pdf", "ไฟล์ใหญ่เกิน 10 MB"),
    (b"GIF89a", "image/gif", "รองรับเฉพาะ application/pdf, image/jpeg, image/png"),
    (b"\x89PNG", "image/png", "ชนิดไฟล์ไม่ตรงกับที่ขออัปโหลด"),
], ids=["too-big", "gif", "png-under-pdf-name"])
def test_direct_note_rejects_and_removes_a_file_blob_should_have_refused(make_app, blob_client, data,
                                                                         content_type, reason):
    """BU-12: client token กันไว้แล้ว ถ้ายังหลุดมาก็ไม่สร้างโน้ตและลบไฟล์ทิ้ง"""
    client = make_app()
    ticket = start(client).get_json()
    browser_put(blob_client, ticket, data=data, content_type=content_type)

    response = finish(client, ticket)

    assert response.status_code == 400
    assert response.get_json()["fields"] == {"file": reason}
    assert ticket["pathname"] not in blob_client.blobs


def test_one_upload_makes_one_note(make_app, blob_client):
    """BU-13: ส่ง JSON เดิมซ้ำ (กดสองครั้ง) → 409 และไฟล์ของโน้ตแรกยังอยู่"""
    client = make_app()
    ticket = start(client).get_json()
    browser_put(blob_client, ticket)
    first = finish(client, ticket)

    again = finish(client, ticket)

    assert first.status_code == 201
    assert again.status_code == 409
    assert again.get_json() == {"error": "upload_already_used"}
    assert ticket["pathname"] in blob_client.blobs
    assert client.get("/notes").get_json()["total"] == 1


def test_direct_note_on_local_disk_is_refused(make_app, tmp_path):
    """BU-14: compose ไม่มีทางอัปโหลดตรง JSON ที่อ้าง pathname จึงใช้ไม่ได้"""
    client = make_app(LocalFileStorage(str(tmp_path / "files")))

    response = finish(client, {"pathname": f"uploads/{MEMBER['id']}/0123456789abcdef0123456789abcdef.pdf"})

    assert response.status_code == 400


def test_new_ticket_removes_this_users_abandoned_uploads(make_app, blob_client):
    """BU-15: ไฟล์ที่อัปโหลดตรงแล้วไม่มีโน้ตตามมาเกินอายุ token ถูกลบตอนขอ token ครั้งถัดไป

    ไฟล์ที่ยังใหม่ ไฟล์ของโน้ตจริง และไฟล์ของผู้ใช้คนอื่นต้องอยู่ครบ
    """
    client = make_app()
    used = start(client).get_json()
    browser_put(blob_client, used)
    assert finish(client, used).status_code == 201
    abandoned = start(client).get_json()
    browser_put(blob_client, abandoned)
    recent = start(client).get_json()
    browser_put(blob_client, recent)
    other_user = "uploads/8/0123456789abcdef0123456789abcdef.pdf"
    blob_client.put(other_user, b"%PDF", access="private", content_type="application/pdf")
    long_ago = datetime.now(timezone.utc) - timedelta(minutes=11)
    for path in (used["pathname"], abandoned["pathname"], other_user):
        blob_client.uploaded_at[path] = long_ago

    assert start(client).status_code == 200

    assert abandoned["pathname"] not in blob_client.blobs
    assert {used["pathname"], recent["pathname"], other_user} <= set(blob_client.blobs)


def test_cleanup_failure_does_not_block_the_upload(make_app, blob_client):
    """BU-16: list ของ Blob ล่ม → ยังได้ token ตามปกติ รอบหน้าค่อยล้าง"""
    def broken(**_kwargs):
        raise RuntimeError("blob list is down")

    blob_client.iter_objects = broken

    assert start(make_app()).status_code == 200
