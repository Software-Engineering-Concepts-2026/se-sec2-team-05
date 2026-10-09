"""เทสต์ "โน้ตของฉัน" และการแก้/ลบด้วยบัญชีเจ้าของ — Issue #82, ADR-008

โครงเดียวกับ test_notes_thanks.py: Flask test client + SQLite ชั่วคราว และ `FakeIdentity`
Alice เป็นเจ้าของโน้ต Bob, Carol, Dave เป็นคนอื่นที่ login อยู่
"""

import io

import pytest
from identity import IdentityUnavailable
from models import build_session_factory
from storage import LocalFileStorage

ALICE = {"Authorization": "Bearer alice"}
BOB = {"Authorization": "Bearer bob"}
CAROL = {"Authorization": "Bearer carol"}
DAVE = {"Authorization": "Bearer dave"}
USERS = {
    "Bearer alice": {"id": 1, "display_name": "Alice"},
    "Bearer bob": {"id": 2, "display_name": "Bob"},
    "Bearer carol": {"id": 3, "display_name": "Carol"},
    "Bearer dave": {"id": 4, "display_name": "Dave"},
}

FORM = {
    "title": "สรุปบทที่ 3",
    "subject_name": "Operating Systems",
    "subject_code": "CS301",
    "faculty": "ICT",
    "year_level": "3",
    "lesson": "บทที่ 3 — Scheduling",
}


class FakeIdentity:
    """รู้จัก token ใน USERS นอกนั้นถือว่าใช้ไม่ได้ · `down=True` จำลอง auth-service ล่ม"""

    def __init__(self):
        self.down = False
        self.calls = 0

    def __call__(self, authorization):
        self.calls += 1
        if self.down:
            raise IdentityUnavailable("auth-service is down")
        user = USERS.get(authorization)
        return dict(user) if user else None


@pytest.fixture
def identity():
    return FakeIdentity()


@pytest.fixture
def database_url(make_db_url):
    return make_db_url("test.db")


@pytest.fixture
def storage_dir(tmp_path):
    return tmp_path / "storage"


@pytest.fixture
def client(database_url, storage_dir, notes_create_app, identity):
    app = notes_create_app(
        database_url=database_url,
        storage=LocalFileStorage(str(storage_dir)),
        identity=identity,
    )
    app.config.update(TESTING=True)
    return app.test_client()


@pytest.fixture
def db(database_url, client):
    return build_session_factory(database_url)


def upload(client, headers=ALICE, **overrides):
    form = {**FORM, **overrides}
    form["file"] = (io.BytesIO(b"%PDF-1.4 fake note"), "note.pdf", "application/pdf")
    response = client.post("/notes", data=form, headers=headers, content_type="multipart/form-data")
    assert response.status_code == 201
    body = response.get_json()
    return body["id"], body["edit_token"]


def new_note(client, headers=ALICE, **overrides):
    return upload(client, headers, **overrides)[0]


def rate(client, note_id, value, headers):
    # ต้องเคยเปิดดูก่อนถึงให้คะแนนได้ (Issue #13)
    client.get(f"/notes/{note_id}", headers=headers)
    assert client.put(f"/notes/{note_id}/rating", json={"rating": value}, headers=headers).status_code == 200


def title_of(client, note_id):
    return client.get(f"/notes/{note_id}").get_json()["title"]


# --- A. แก้/ลบด้วยบัญชีเจ้าของ (ADR-008) ---


def test_owner_can_edit_without_edit_token(client):
    note_id = new_note(client)

    response = client.patch(f"/notes/{note_id}", data={"title": "ชื่อใหม่"}, headers=ALICE)

    assert response.status_code == 200
    assert response.get_json()["title"] == "ชื่อใหม่"
    assert title_of(client, note_id) == "ชื่อใหม่"


def test_owner_can_delete_without_edit_token_and_files_are_removed(client, storage_dir):
    note_id = new_note(client)
    assert any(storage_dir.iterdir())

    response = client.delete(f"/notes/{note_id}", headers=ALICE)

    assert response.status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404
    assert not any(p.is_file() for p in storage_dir.rglob("*"))


def test_other_member_cannot_edit_or_delete(client):
    note_id = new_note(client)

    patched = client.patch(f"/notes/{note_id}", data={"title": "แอบแก้"}, headers=BOB)
    deleted = client.delete(f"/notes/{note_id}", headers=BOB)

    assert patched.status_code == 403
    assert patched.get_json()["error"] == "forbidden"
    assert deleted.status_code == 403
    assert title_of(client, note_id) == FORM["title"]


def test_no_token_and_no_login_is_still_403(client):
    note_id = new_note(client)

    assert client.patch(f"/notes/{note_id}", data={"title": "x"}).status_code == 403
    assert client.delete(f"/notes/{note_id}").status_code == 403


def test_unknown_bearer_without_edit_token_is_401(client):
    note_id = new_note(client)

    response = client.delete(f"/notes/{note_id}", headers={"Authorization": "Bearer expired"})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert client.get(f"/notes/{note_id}").status_code == 200


def test_auth_service_down_without_edit_token_is_503(client, identity):
    note_id = new_note(client)
    identity.down = True

    response = client.patch(f"/notes/{note_id}", data={"title": "x"}, headers=ALICE)

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_valid_edit_token_skips_auth_service(client, identity):
    """token ถูกตรวจก่อน — ใช้ได้แม้ auth-service ล่ม และไม่ต้องถาม auth-service เลย"""
    note_id, token = upload(client)
    identity.down = True
    calls = identity.calls

    response = client.patch(
        f"/notes/{note_id}", data={"title": "แก้ด้วย token"}, headers={**BOB, "X-Note-Token": token}
    )

    assert response.status_code == 200
    assert identity.calls == calls


def test_wrong_edit_token_from_owner_still_passes_by_login(client):
    note_id = new_note(client)

    response = client.patch(
        f"/notes/{note_id}", data={"title": "ชื่อใหม่"}, headers={**ALICE, "X-Note-Token": "wrong"}
    )

    assert response.status_code == 200


def test_missing_note_is_404_before_any_auth_check(client):
    assert client.delete("/notes/999", headers=BOB).status_code == 404


# --- B. GET /notes/mine ---


def test_my_notes_requires_login(client):
    response = client.get("/notes/mine")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_my_notes_is_503_when_auth_service_is_down(client, identity):
    identity.down = True

    assert client.get("/notes/mine", headers=ALICE).status_code == 503


def test_my_notes_lists_only_my_notes_newest_first(client):
    first = new_note(client, title="เก่า")
    new_note(client, headers=BOB, title="ของ Bob")
    second = new_note(client, title="ใหม่")

    body = client.get("/notes/mine", headers=ALICE).get_json()

    assert [item["id"] for item in body["items"]] == [second, first]
    assert body["count"] == 2


def test_my_notes_never_leak_the_edit_token(client):
    new_note(client)

    item = client.get("/notes/mine", headers=ALICE).get_json()["items"][0]

    assert "edit_token" not in item
    assert "edit_token_hash" not in item


def test_my_notes_without_uploads_has_zero_summary(client):
    new_note(client, headers=BOB)

    body = client.get("/notes/mine", headers=ALICE).get_json()

    assert body["items"] == []
    assert body["summary"] == {
        "note_count": 0,
        "total_views": 0,
        "total_downloads": 0,
        "total_thanks": 0,
        "average_rating": None,
        "rating_count": 0,
    }


def test_summary_counts_every_note_not_only_the_page(client):
    notes = [new_note(client) for _ in range(3)]
    client.get(f"/notes/{notes[0]}/download")
    client.get(f"/notes/{notes[0]}/download")
    client.get(f"/notes/{notes[2]}/download")
    client.get(f"/notes/{notes[1]}")

    body = client.get("/notes/mine?limit=1", headers=ALICE).get_json()

    assert body["count"] == 1
    assert body["summary"]["note_count"] == 3
    assert body["summary"]["total_downloads"] == 3
    assert body["summary"]["total_views"] == 1


def test_summary_average_is_weighted_by_every_rating(client):
    """5 + 5 + 2 = เฉลี่ย 4.0 ไม่ใช่ค่าเฉลี่ยของค่าเฉลี่ยรายโน้ต (5 กับ 2 = 3.5)"""
    popular = new_note(client)
    other = new_note(client)
    rate(client, popular, 5, BOB)
    rate(client, popular, 5, CAROL)
    rate(client, other, 2, DAVE)

    summary = client.get("/notes/mine", headers=ALICE).get_json()["summary"]

    assert summary["average_rating"] == 4.0
    assert summary["rating_count"] == 3


def test_thank_counts_per_note_and_in_total(client):
    thanked = new_note(client)
    quiet = new_note(client)
    for who in (BOB, CAROL):
        assert client.post(f"/notes/{thanked}/thanks", headers=who).status_code == 201

    body = client.get("/notes/mine", headers=ALICE).get_json()

    counts = {item["id"]: item["thank_count"] for item in body["items"]}
    assert counts == {thanked: 2, quiet: 0}
    assert body["summary"]["total_thanks"] == 2


def test_my_notes_rejects_bad_paging(client):
    response = client.get("/notes/mine?limit=abc", headers=ALICE)

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_filter", "field": "limit/offset"}
