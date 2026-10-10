"""เทสต์การขอบคุณเจ้าของโน้ตของ Notes Service — US-28 (#28)

โครงเดียวกับ test_notes_favorites.py: Flask test client + SQLite ชั่วคราว และ `FakeIdentity`
ที่แยก token ต่อผู้ใช้ Alice เป็นเจ้าของโน้ต Bob กับ Carol เป็นผู้ค้นหา
"""

import io

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.engine import Engine

from identity import IdentityUnavailable
from models import Thank, build_session_factory
from storage import LocalFileStorage

ALICE = {"Authorization": "Bearer alice"}
BOB = {"Authorization": "Bearer bob"}
CAROL = {"Authorization": "Bearer carol"}
USERS = {
    "Bearer alice": {"id": 1, "display_name": "Alice"},
    "Bearer bob": {"id": 2, "display_name": "Bob"},
    "Bearer carol": {"id": 3, "display_name": "Carol"},
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
    """รู้จัก token ของ Alice, Bob, Carol นอกนั้นถือว่าใช้ไม่ได้ · `down=True` จำลอง auth-service ล่ม"""

    def __init__(self):
        self.down = False

    def __call__(self, authorization):
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
def client(tmp_path, database_url, notes_create_app, identity):
    app = notes_create_app(
        database_url=database_url,
        storage=LocalFileStorage(str(tmp_path / "storage")),
        identity=identity,
    )
    app.config.update(TESTING=True)
    return app.test_client()


@pytest.fixture
def db(database_url, client):
    """session ตรงเข้า DB เดียวกับ client ไว้นับแถวที่ API ไม่เปิดเผย (จำนวนคำขอบคุณ)"""
    return build_session_factory(database_url)


def upload(client, headers=ALICE):
    form = {**FORM, "file": (io.BytesIO(b"%PDF-1.4 fake note"), "note.pdf", "application/pdf")}
    return client.post("/notes", data=form, headers=headers, content_type="multipart/form-data")


def new_note(client, headers=ALICE):
    return upload(client, headers).get_json()["id"]


def thank(client, note_id, headers=BOB):
    return client.post(f"/notes/{note_id}/thanks", headers=headers)


def status_of(client, note_id, headers=BOB):
    return client.get(f"/notes/{note_id}", headers=headers).get_json()["thank_status"]


def thank_count(db, note_id=None):
    stmt = select(func.count()).select_from(Thank)
    if note_id is not None:
        stmt = stmt.where(Thank.note_id == note_id)
    with db() as session:
        return session.scalar(stmt)


# --- A. กดขอบคุณ ---


def test_first_thanks_returns_201_with_new_state(client):
    note_id = new_note(client)

    response = thank(client, note_id)

    assert response.status_code == 201
    body = response.get_json()
    assert body["note_id"] == note_id
    assert body["thanked"] is True
    assert body["thanked_at"]


def test_thanking_twice_returns_200_and_does_not_add_a_row(client, db):
    note_id = new_note(client)
    first = thank(client, note_id).get_json()

    second = thank(client, note_id)

    assert second.status_code == 200
    assert second.get_json()["thanked_at"] == first["thanked_at"]
    assert thank_count(db, note_id) == 1


def test_thanks_requires_login(client, db):
    note_id = new_note(client)

    response = client.post(f"/notes/{note_id}/thanks")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"
    assert thank_count(db) == 0


def test_thanks_with_unknown_token_is_401(client):
    note_id = new_note(client)

    assert thank(client, note_id, headers={"Authorization": "Bearer nobody"}).status_code == 401


def test_thanks_is_503_when_auth_service_is_down(client, identity):
    note_id = new_note(client)
    identity.down = True

    response = thank(client, note_id)

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_thanks_for_missing_note_is_404(client):
    response = thank(client, 999)

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_cannot_thank_your_own_note(client, db):
    note_id = new_note(client)

    response = thank(client, note_id, ALICE)

    assert response.status_code == 403
    assert response.get_json()["error"] == "own_note"
    assert thank_count(db) == 0


def test_each_user_can_thank_once_and_counts_add_up(client, db):
    note_id = new_note(client)

    assert thank(client, note_id, BOB).status_code == 201
    assert thank(client, note_id, CAROL).status_code == 201
    thank(client, note_id, BOB)

    assert thank_count(db, note_id) == 2


def test_thanks_are_counted_per_note(client, db):
    first, second = new_note(client), new_note(client)

    thank(client, first, BOB)

    assert thank_count(db, first) == 1
    assert thank_count(db, second) == 0


def test_there_is_no_endpoint_to_take_a_thanks_back(client):
    note_id = new_note(client)
    thank(client, note_id)

    assert client.delete(f"/notes/{note_id}/thanks", headers=BOB).status_code == 405
    assert status_of(client, note_id) == "thanked"


def test_thanks_does_not_need_a_download_through_the_api(client):
    """"หลังดาวน์โหลด" เป็นเงื่อนไขฝั่ง UI — API ไม่ได้เก็บว่าใครดาวน์โหลด"""
    note_id = new_note(client)

    assert thank(client, note_id).status_code == 201
    assert client.get(f"/notes/{note_id}").get_json()["download_count"] == 0


# --- B. thank_status ---


def test_status_flips_from_can_thank_to_thanked(client):
    note_id = new_note(client)
    assert status_of(client, note_id) == "can_thank"

    thank(client, note_id)

    assert status_of(client, note_id) == "thanked"


def test_status_is_own_note_for_the_uploader(client):
    note_id = new_note(client)

    assert status_of(client, note_id, ALICE) == "own_note"


def test_status_is_per_user(client):
    note_id = new_note(client)
    thank(client, note_id, BOB)

    assert status_of(client, note_id, BOB) == "thanked"
    assert status_of(client, note_id, CAROL) == "can_thank"


def test_status_is_null_when_not_logged_in(client):
    note_id = new_note(client)

    assert client.get(f"/notes/{note_id}").get_json()["thank_status"] is None
    assert client.get("/notes").get_json()["items"][0]["thank_status"] is None


def test_status_is_null_with_an_unusable_token(client):
    note_id = new_note(client)
    nobody = {"Authorization": "Bearer nobody"}

    single = client.get(f"/notes/{note_id}", headers=nobody)
    listed = client.get("/notes", headers=nobody)

    assert single.status_code == listed.status_code == 200
    assert single.get_json()["thank_status"] is None
    assert listed.get_json()["items"][0]["thank_status"] is None


def test_search_still_works_when_auth_service_is_down(client, identity):
    note_id = new_note(client)
    identity.down = True

    listed = client.get("/notes", headers=BOB)
    single = client.get(f"/notes/{note_id}", headers=BOB)

    assert listed.status_code == single.status_code == 200
    assert listed.get_json()["items"][0]["thank_status"] is None
    assert single.get_json()["thank_status"] is None


def test_list_reports_a_status_per_note(client):
    plain, thanked, owned = new_note(client), new_note(client), new_note(client, BOB)
    thank(client, thanked)

    items = {n["id"]: n["thank_status"] for n in client.get("/notes", headers=BOB).get_json()["items"]}

    assert items == {plain: "can_thank", thanked: "thanked", owned: "own_note"}


def test_status_is_fetched_for_the_whole_page_in_one_query(client):
    """จำนวน query ที่แตะตาราง thanks ต้องไม่โตตามจำนวนโน้ตในหน้า"""
    for _ in range(5):
        thank(client, new_note(client))

    statements = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", record)
    try:
        client.get("/notes", headers=BOB)
    finally:
        event.remove(Engine, "before_cursor_execute", record)

    assert sum("FROM thanks" in s for s in statements) == 1


# --- C. ลบโน้ต (US-20) ---


def test_deleting_a_thanked_note_removes_its_thanks(client, db):
    created = upload(client).get_json()
    kept = new_note(client)
    for headers in (BOB, CAROL):
        thank(client, created["id"], headers)
    thank(client, kept, BOB)

    response = client.delete(f"/notes/{created['id']}", headers=ALICE)

    assert response.status_code == 204
    assert thank_count(db, created["id"]) == 0
    assert thank_count(db, kept) == 1
