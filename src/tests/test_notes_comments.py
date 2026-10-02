from datetime import date

import pytest

from models import Comment, Note, build_session_factory
from tokens import issue_token


@pytest.fixture()
def test_context(tmp_path, notes_create_app):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"

    users = {
        "Bearer valid-user-1": {
            "id": 1,
            "display_name": "User One",
        },
        "Bearer valid-user-2": {
            "id": 2,
            "display_name": "User Two",
        },
    }

    def fake_identity(authorization):
        return users.get(authorization)

    app = notes_create_app(
        database_url=database_url,
        identity=fake_identity,
    )
    app.config.update(TESTING=True)

    session_factory = build_session_factory(database_url)

    return app, session_factory


@pytest.fixture()
def client(test_context):
    app, _ = test_context
    return app.test_client()


def create_test_note(session_factory, note_id=1):
    note = Note(
        id=note_id,
        title="Test Note",
        subject_name="Software Engineering",
        subject_code="SE101",
        faculty="Engineering",
        year_level=1,
        lesson="Testing",
        topic="Comments",
        class_date=date(2026, 9, 29),
        description="Test note",
        file_name="test.txt",
        content_type="text/plain",
        size_bytes=12,
        storage_key=f"test-{note_id}.txt",
        uploader_id=1,
        uploader_name="User One",
        edit_token_hash="a" * 64,
    )

    with session_factory() as session:
        session.add(note)
        session.commit()

    return note_id


def test_create_comment_without_login_returns_401(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    response = client.post(
        f"/notes/{note_id}/comments",
        json={"content": "Hello"},
    )

    assert response.status_code == 401


def test_create_comment_with_invalid_token_returns_401(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    response = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer invalid-token"},
        json={"content": "Hello"},
    )

    assert response.status_code == 401


def test_create_comment_with_empty_content_returns_400(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    response = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "   "},
    )

    assert response.status_code == 400


def test_create_comment_over_1000_characters_returns_400(
    test_context,
    client,
):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    response = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "a" * 1001},
    )

    assert response.status_code == 400


def test_create_comment_for_nonexistent_note_returns_404(client):
    response = client.post(
        "/notes/99999/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "Hello"},
    )

    assert response.status_code == 404


def test_comments_are_sorted_newest_first(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    first = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "First"},
    )
    assert first.status_code == 201

    second = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-2"},
        json={"content": "Second"},
    )
    assert second.status_code == 201

    response = client.get(f"/notes/{note_id}/comments")

    assert response.status_code == 200

    comments = response.get_json()["comments"]

    assert [comment["content"] for comment in comments] == [
        "Second",
        "First",
    ]


def test_user_can_delete_own_comment(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    created = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "My comment"},
    )
    assert created.status_code == 201

    comment_id = created.get_json()["id"]

    response = client.delete(
        f"/notes/{note_id}/comments/{comment_id}",
        headers={"Authorization": "Bearer valid-user-1"},
    )

    assert response.status_code == 204


def test_user_cannot_delete_someone_elses_comment(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    created = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "User One comment"},
    )
    assert created.status_code == 201

    comment_id = created.get_json()["id"]

    response = client.delete(
        f"/notes/{note_id}/comments/{comment_id}",
        headers={"Authorization": "Bearer valid-user-2"},
    )

    assert response.status_code == 403


def test_deleting_note_also_deletes_comments(test_context, client):
    _, session_factory = test_context
    note_id = create_test_note(session_factory)

    created = client.post(
        f"/notes/{note_id}/comments",
        headers={"Authorization": "Bearer valid-user-1"},
        json={"content": "Comment to be deleted with the note"},
    )
    assert created.status_code == 201

    comment_id = created.get_json()["id"]

    with session_factory() as session:
        comment = session.get(Comment, comment_id)
        assert comment is not None

    edit_token, edit_token_hash = issue_token()

    with session_factory() as session:
        note = session.get(Note, note_id)
        note.edit_token_hash = edit_token_hash
        session.commit()

    response = client.delete(
        f"/notes/{note_id}",
        headers={"X-Note-Token": edit_token},
    )

    assert response.status_code == 204

    with session_factory() as session:
        comment = session.get(Comment, comment_id)
        assert comment is None