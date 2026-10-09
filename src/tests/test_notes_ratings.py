from datetime import date

import pytest
from sqlalchemy import func, select

from identity import IdentityUnavailable
from models import Note, NoteAccess, Rating, build_session_factory
from storage import LocalFileStorage
from tokens import issue_token

ALICE = {"Authorization": "alice-token"}
BOB = {"Authorization": "bob-token"}
USERS = {
    "alice-token": {"id": 1, "display_name": "Alice"},
    "bob-token": {"id": 2, "display_name": "Bob"},
}


class FakeIdentity:
    def __init__(self):
        self.down = False

    def __call__(self, authorization):
        if self.down:
            raise IdentityUnavailable("auth-service is down")
        user = USERS.get(authorization)
        return dict(user) if user else None


@pytest.fixture
def rating_context(tmp_path, make_db_url, notes_create_app):
    database_url = make_db_url("ratings.db")
    storage = LocalFileStorage(str(tmp_path / "storage"))
    identity = FakeIdentity()
    app = notes_create_app(
        database_url=database_url,
        storage=storage,
        identity=identity,
    )
    app.config.update(TESTING=True)
    session_factory = build_session_factory(database_url)
    return app.test_client(), session_factory, storage, identity


def create_note(session_factory, storage, note_id=1):
    storage.save_bytes(f"note-{note_id}.pdf", b"%PDF-1.4 test note")
    note = Note(
        id=note_id,
        title="Rating test note",
        subject_name="Software Engineering",
        subject_code="SE101",
        faculty="Engineering",
        year_level=1,
        lesson="Rating",
        class_date=date(2026, 10, 1),
        file_name="note.pdf",
        content_type="application/pdf",
        size_bytes=18,
        storage_key=f"note-{note_id}.pdf",
        uploader_id=1,
        uploader_name="Alice",
        edit_token_hash="a" * 64,
    )
    with session_factory() as session:
        session.add(note)
        session.commit()
    return note_id


def make_eligible(client, note_id, headers=ALICE):
    return client.get(f"/notes/{note_id}", headers=headers)


def rate(client, note_id, value, headers=ALICE):
    return client.put(
        f"/notes/{note_id}/rating",
        headers=headers,
        json={"rating": value},
    )


def test_authenticated_detail_open_records_eligibility(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)

    response = make_eligible(client, note_id)

    assert response.status_code == 200
    assert response.get_json()["can_rate"] is True
    with session_factory() as session:
        access = session.scalars(select(NoteAccess)).one()
        assert (access.user_id, access.note_id) == (1, note_id)


def test_authenticated_download_records_eligibility(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)

    response = client.get(f"/notes/{note_id}/download", headers=ALICE)

    assert response.status_code == 200
    with session_factory() as session:
        access = session.scalars(select(NoteAccess)).one()
        note = session.get(Note, note_id)
        assert (access.user_id, access.note_id) == (1, note_id)
        assert note.download_count == 1


def test_unauthenticated_detail_does_not_record_user_eligibility(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)

    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 200
    assert "can_rate" not in response.get_json()
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(NoteAccess)) == 0


def test_eligible_user_can_create_rating(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)

    response = rate(client, note_id, 5)

    assert response.status_code == 200
    assert response.get_json()["rating"] == 5
    assert response.get_json()["average_rating"] == 5.0
    assert response.get_json()["rating_count"] == 1
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Rating)) == 1


@pytest.mark.parametrize("value", [1, 5])
def test_rating_scale_accepts_both_endpoints(rating_context, value):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)

    response = rate(client, note_id, value)

    assert response.status_code == 200
    assert response.get_json()["rating"] == value


@pytest.mark.parametrize("value", [0, 6, -1, 2.5, "5", True, None])
def test_invalid_rating_values_return_400(rating_context, value):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)

    response = rate(client, note_id, value)

    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_failed"


def test_repeat_rating_updates_existing_row(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)
    first = rate(client, note_id, 2)

    updated = rate(client, note_id, 4)

    assert first.status_code == updated.status_code == 200
    assert updated.get_json()["rating"] == 4
    assert updated.get_json()["average_rating"] == 4.0
    assert updated.get_json()["rating_count"] == 1
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Rating)) == 1
        assert session.scalars(select(Rating)).one().value == 4


def test_average_is_calculated_and_included_in_note_responses(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id, ALICE)
    make_eligible(client, note_id, BOB)
    assert rate(client, note_id, 5, ALICE).status_code == 200
    assert rate(client, note_id, 4, BOB).status_code == 200

    detail = client.get(f"/notes/{note_id}").get_json()
    listed = client.get("/notes").get_json()["items"][0]

    assert detail["average_rating"] == 4.5
    assert detail["rating_count"] == 2
    assert listed["average_rating"] == 4.5
    assert listed["rating_count"] == 2
    assert "user_rating" not in detail


def test_ineligible_authenticated_user_cannot_rate(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)

    response = rate(client, note_id, 3)

    assert response.status_code == 403
    assert response.get_json()["error"] == "not_eligible"


def test_rating_requires_authentication(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)

    response = client.put(f"/notes/{note_id}/rating", json={"rating": 3})

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_rating_for_unknown_note_returns_404(rating_context):
    client, _, _, _ = rating_context

    response = rate(client, 999, 3)

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_rating_when_auth_service_is_unavailable_returns_503(rating_context):
    client, session_factory, storage, identity = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)
    identity.down = True

    response = rate(client, note_id, 3)

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_users_have_independent_ratings_and_detail_exposes_only_their_own(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id, ALICE)
    make_eligible(client, note_id, BOB)
    rate(client, note_id, 2, ALICE)
    rate(client, note_id, 5, BOB)

    alice_detail = client.get(f"/notes/{note_id}", headers=ALICE).get_json()
    bob_detail = client.get(f"/notes/{note_id}", headers=BOB).get_json()

    assert alice_detail["user_rating"] == 2
    assert bob_detail["user_rating"] == 5
    assert alice_detail["average_rating"] == bob_detail["average_rating"] == 3.5
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(Rating)) == 2


def test_deleting_note_removes_access_and_rating_records(rating_context):
    client, session_factory, storage, _ = rating_context
    note_id = create_note(session_factory, storage)
    make_eligible(client, note_id)
    assert rate(client, note_id, 5).status_code == 200
    edit_token, token_hash = issue_token()
    with session_factory() as session:
        note = session.get(Note, note_id)
        note.edit_token_hash = token_hash
        session.commit()

    response = client.delete(
        f"/notes/{note_id}",
        headers={"X-Note-Token": edit_token},
    )

    assert response.status_code == 204
    with session_factory() as session:
        assert session.scalar(select(func.count()).select_from(NoteAccess)) == 0
        assert session.scalar(select(func.count()).select_from(Rating)) == 0
