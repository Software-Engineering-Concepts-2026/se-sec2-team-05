"""เทสต์รายการโปรดของ Notes Service — US-15 (#15)

ใช้ Flask test client + SQLite ชั่วคราวเหมือน test_notes_api.py แต่ต้องมีผู้ใช้หลายคน
(เช็กว่ารายการของ A ไม่ปนกับ B) จึงใช้ `FakeIdentity` ของไฟล์นี้ที่แยก token ต่อผู้ใช้
"""

import io

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine

from identity import IdentityUnavailable
from storage import LocalFileStorage

ALICE = {"Authorization": "Bearer alice"}
BOB = {"Authorization": "Bearer bob"}
USERS = {"Bearer alice": {"id": 1, "display_name": "Alice"}, "Bearer bob": {"id": 2, "display_name": "Bob"}}

FORM = {
    "title": "สรุปบทที่ 3",
    "subject_name": "Data Structures",
    "subject_code": "CS201",
    "faculty": "ICT",
    "year_level": "2",
    "lesson": "บทที่ 3 — Linked List",
}


class FakeIdentity:
    """รู้จัก token ของ Alice กับ Bob นอกนั้นถือว่าใช้ไม่ได้ · `down=True` จำลอง auth-service ล่ม"""

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
def client(tmp_path, make_db_url, notes_create_app, identity):
    app = notes_create_app(
        database_url=make_db_url("test.db"),
        storage=LocalFileStorage(str(tmp_path / "storage")),
        identity=identity,
    )
    app.config.update(TESTING=True)
    return app.test_client()


def upload(client, headers=ALICE, **overrides):
    form = {**FORM, **overrides}
    form["file"] = (io.BytesIO(b"%PDF-1.4 fake note"), "note.pdf", "application/pdf")
    return client.post("/notes", data=form, headers=headers, content_type="multipart/form-data")


def new_note(client, **overrides):
    return upload(client, **overrides).get_json()["id"]


def favorite(client, note_id, headers=ALICE):
    return client.post(f"/notes/{note_id}/favorite", headers=headers)


def unfavorite(client, note_id, headers=ALICE):
    return client.delete(f"/notes/{note_id}/favorite", headers=headers)


def favorite_ids(client, headers=ALICE, query=""):
    return [n["id"] for n in client.get(f"/notes/favorites{query}", headers=headers).get_json()["items"]]


# --- A. เพิ่มเข้ารายการโปรด ---


def test_first_favorite_returns_201_with_new_state(client):
    note_id = new_note(client)

    response = favorite(client, note_id)

    assert response.status_code == 201
    body = response.get_json()
    assert body["note_id"] == note_id
    assert body["is_favorited"] is True
    assert body["favorited_at"]


def test_favoriting_twice_returns_200_and_keeps_one_row(client):
    note_id = new_note(client)
    first = favorite(client, note_id).get_json()

    second = favorite(client, note_id)

    assert second.status_code == 200
    assert second.get_json()["favorited_at"] == first["favorited_at"]
    assert favorite_ids(client) == [note_id]


def test_favorite_requires_login(client):
    note_id = new_note(client)

    response = client.post(f"/notes/{note_id}/favorite")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_favorite_with_unknown_token_is_401(client):
    note_id = new_note(client)

    assert favorite(client, note_id, headers={"Authorization": "Bearer nobody"}).status_code == 401


def test_favorite_when_auth_service_is_down_is_503(client, identity):
    note_id = new_note(client)
    identity.down = True

    response = favorite(client, note_id)

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_favorite_unknown_note_is_404(client):
    response = favorite(client, 999)

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_member_can_favorite_their_own_note(client):
    note_id = new_note(client, headers=ALICE)

    assert favorite(client, note_id, headers=ALICE).status_code == 201


# --- B. เอาออกจากรายการโปรด ---


def test_unfavorite_returns_204_and_removes_it_from_the_list(client):
    note_id = new_note(client)
    favorite(client, note_id)

    response = unfavorite(client, note_id)

    assert response.status_code == 204
    assert favorite_ids(client) == []


def test_unfavorite_note_that_was_never_favorited_is_204(client):
    note_id = new_note(client)

    assert unfavorite(client, note_id).status_code == 204


def test_unfavorite_requires_login(client):
    note_id = new_note(client)

    assert client.delete(f"/notes/{note_id}/favorite").status_code == 401


def test_unfavorite_when_auth_service_is_down_is_503(client, identity):
    note_id = new_note(client)
    identity.down = True

    assert unfavorite(client, note_id).status_code == 503


def test_unfavorite_unknown_note_is_404(client):
    assert unfavorite(client, 999).status_code == 404


def test_one_user_unfavoriting_does_not_touch_another_users_list(client):
    note_id = new_note(client)
    favorite(client, note_id, headers=ALICE)
    favorite(client, note_id, headers=BOB)

    unfavorite(client, note_id, headers=BOB)

    assert favorite_ids(client, headers=ALICE) == [note_id]
    assert favorite_ids(client, headers=BOB) == []


# --- C. ดูรายการโปรด ---


def test_list_shows_only_own_favorites(client):
    mine, theirs = new_note(client), new_note(client)
    favorite(client, mine, headers=ALICE)
    favorite(client, theirs, headers=BOB)

    assert favorite_ids(client, headers=ALICE) == [mine]
    assert favorite_ids(client, headers=BOB) == [theirs]


def test_list_is_newest_favorite_first(client):
    first, second, third = new_note(client), new_note(client), new_note(client)
    for note_id in (first, third, second):
        favorite(client, note_id)

    assert favorite_ids(client) == [second, third, first]


def test_list_items_carry_note_fields_and_state(client):
    note_id = new_note(client)
    favorite(client, note_id)

    item = client.get("/notes/favorites", headers=ALICE).get_json()["items"][0]

    assert item["id"] == note_id
    assert item["title"] == "สรุปบทที่ 3"
    assert item["is_favorited"] is True
    assert item["favorited_at"]


def test_empty_list_is_200_with_no_items(client):
    response = client.get("/notes/favorites", headers=ALICE)

    assert response.status_code == 200
    assert response.get_json() == {"items": [], "count": 0}


def test_list_requires_login(client):
    assert client.get("/notes/favorites").status_code == 401


def test_list_when_auth_service_is_down_is_503(client, identity):
    identity.down = True

    assert client.get("/notes/favorites", headers=ALICE).status_code == 503


def test_deleted_note_disappears_from_the_list(client):
    kept = new_note(client)
    doomed_response = upload(client).get_json()
    doomed, token = doomed_response["id"], doomed_response["edit_token"]
    favorite(client, kept)
    favorite(client, doomed)

    assert client.delete(f"/notes/{doomed}", headers={"X-Note-Token": token}).status_code == 204

    assert favorite_ids(client) == [kept]


def test_deleting_a_note_favorited_by_several_users_removes_every_favorite_row(client):
    created = upload(client).get_json()
    favorite(client, created["id"], ALICE)
    favorite(client, created["id"], BOB)

    response = client.delete(f"/notes/{created['id']}", headers={"X-Note-Token": created["edit_token"]})

    assert response.status_code == 204
    assert favorite_ids(client, ALICE) == []
    assert favorite_ids(client, BOB) == []


def test_list_supports_limit_and_offset(client):
    ids = [new_note(client) for _ in range(3)]
    for note_id in ids:
        favorite(client, note_id)
    newest_first = list(reversed(ids))

    assert favorite_ids(client, query="?limit=2") == newest_first[:2]
    assert favorite_ids(client, query="?limit=2&offset=2") == newest_first[2:]


def test_list_clamps_limit_and_offset_like_search(client):
    note_id = new_note(client)
    favorite(client, note_id)

    assert favorite_ids(client, query="?limit=-5&offset=-3") == [note_id]
    assert client.get("/notes/favorites?limit=abc", headers=ALICE).status_code == 400


def test_favorites_route_is_not_taken_for_a_note_id(client):
    # /notes/favorites ต้องไม่ถูกตีความเป็น /notes/<id> — ไม่ login ต้องได้ 401 ไม่ใช่ 404
    assert client.get("/notes/favorites").status_code == 401


def test_search_is_not_filtered_by_favorites(client):
    faved, other = new_note(client), new_note(client)
    favorite(client, faved)

    items = client.get("/notes", headers=ALICE).get_json()["items"]

    assert {n["id"] for n in items} == {faved, other}


# --- D. สถานะ is_favorited ---


def test_search_marks_favorited_notes_when_logged_in(client):
    faved, other = new_note(client), new_note(client)
    favorite(client, faved)

    items = client.get("/notes", headers=ALICE).get_json()["items"]

    assert {n["id"]: n["is_favorited"] for n in items} == {faved: True, other: False}


def test_state_is_per_user(client):
    note_id = new_note(client)
    favorite(client, note_id, headers=ALICE)

    as_bob = client.get(f"/notes/{note_id}", headers=BOB).get_json()
    as_alice = client.get(f"/notes/{note_id}", headers=ALICE).get_json()

    assert as_alice["is_favorited"] is True
    assert as_bob["is_favorited"] is False


def test_state_is_null_when_not_logged_in(client):
    note_id = new_note(client)
    favorite(client, note_id)

    assert client.get(f"/notes/{note_id}").get_json()["is_favorited"] is None
    assert client.get("/notes").get_json()["items"][0]["is_favorited"] is None


def test_state_is_null_with_an_unusable_token(client):
    note_id = new_note(client)

    body = client.get(f"/notes/{note_id}", headers={"Authorization": "Bearer nobody"}).get_json()

    assert body["is_favorited"] is None


def test_search_still_works_when_auth_service_is_down(client, identity):
    note_id = new_note(client)
    favorite(client, note_id)
    identity.down = True

    response = client.get("/notes", headers=ALICE)

    assert response.status_code == 200
    assert response.get_json()["items"][0]["is_favorited"] is None
    assert client.get(f"/notes/{note_id}", headers=ALICE).get_json()["is_favorited"] is None


def test_state_flips_after_unfavorite(client):
    note_id = new_note(client)
    favorite(client, note_id)
    unfavorite(client, note_id)

    assert client.get(f"/notes/{note_id}", headers=ALICE).get_json()["is_favorited"] is False


def test_state_is_fetched_for_the_whole_page_in_one_query(client):
    """D5: จำนวน query ที่แตะตาราง favorites ต้องไม่โตตามจำนวนโน้ตในหน้า"""
    for _ in range(5):
        favorite(client, new_note(client))

    statements = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(Engine, "before_cursor_execute", record)
    try:
        client.get("/notes", headers=ALICE)
    finally:
        event.remove(Engine, "before_cursor_execute", record)

    assert sum("FROM favorites" in s for s in statements) == 1
