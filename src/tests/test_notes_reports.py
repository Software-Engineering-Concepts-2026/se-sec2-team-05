"""Tests for Notes Service reports — Issue #17."""

import io

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from identity import IdentityUnavailable
from models import Note, Report, build_session_factory
from storage import LocalFileStorage

MEMBER = {"id": 7, "display_name": "สมาชิก"}
OTHER_MEMBER = {"id": 8, "display_name": "สมาชิกอีกคน"}
ADMIN = {"id": 99, "display_name": "Admin"}

MEMBER_AUTH = {"Authorization": "Bearer valid-member-token"}
OTHER_MEMBER_AUTH = {"Authorization": "Bearer valid-other-token"}
ADMIN_AUTH = {"Authorization": "Bearer valid-admin-token"}

USERS = {
    "Bearer valid-member-token": MEMBER,
    "Bearer valid-other-token": OTHER_MEMBER,
    "Bearer valid-admin-token": ADMIN,
}

BASE_FORM = {
    "title": "สรุปบทเรียน",
    "subject_name": "Software Engineering",
    "subject_code": "SE101",
    "faculty": "ICT",
    "year_level": "2",
    "lesson": "Testing",
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
def report_context(tmp_path, notes_create_app, monkeypatch):
    monkeypatch.setenv("ADMIN_USER_IDS", "99")
    database_url = f"sqlite:///{tmp_path / 'reports.db'}"
    identity = FakeIdentity()
    app = notes_create_app(
        database_url=database_url,
        storage=LocalFileStorage(str(tmp_path / "storage")),
        identity=identity,
    )
    app.config.update(TESTING=True)
    return {
        "client": app.test_client(),
        "identity": identity,
        "session_factory": build_session_factory(database_url),
    }


@pytest.fixture
def client(report_context):
    return report_context["client"]


@pytest.fixture
def identity(report_context):
    return report_context["identity"]


@pytest.fixture
def session_factory(report_context):
    return report_context["session_factory"]


def upload_note(client, headers=MEMBER_AUTH):
    form = {
        **BASE_FORM,
        "file": (io.BytesIO(b"%PDF-1.4 report test"), "note.pdf", "application/pdf"),
    }
    response = client.post(
        "/notes",
        data=form,
        headers=headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    return response.get_json()


def create_report(client, note_id, headers=MEMBER_AUTH, reason="เนื้อหาไม่เหมาะสม"):
    return client.post(
        f"/notes/{note_id}/reports",
        headers=headers,
        json={"reason": reason},
    )


def report_count(session_factory):
    with session_factory() as session:
        return session.scalar(select(func.count()).select_from(Report))


def test_report_note_returns_201(client):
    note = upload_note(client)

    response = create_report(client, note["id"], reason="  เนื้อหาละเมิดลิขสิทธิ์  ")

    assert response.status_code == 201
    body = response.get_json()
    assert set(body) == {
        "id",
        "note_id",
        "reporter_id",
        "reporter_name",
        "reason",
        "created_at",
    }
    assert body["note_id"] == note["id"]
    assert body["reporter_id"] == MEMBER["id"]
    assert body["reporter_name"] == MEMBER["display_name"]
    assert body["reason"] == "เนื้อหาละเมิดลิขสิทธิ์"
    assert body["created_at"]


def test_report_requires_reason(client):
    note = upload_note(client)

    response = client.post(
        f"/notes/{note['id']}/reports",
        headers=MEMBER_AUTH,
        json={},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "validation_failed",
        "fields": {"reason": "required"},
    }


def test_report_rejects_blank_reason(client):
    note = upload_note(client)

    response = create_report(client, note["id"], reason="   ")

    assert response.status_code == 400
    assert response.get_json()["fields"]["reason"] == "required"


@pytest.mark.parametrize("payload", [None, [], "reason", {"reason": 123}])
def test_report_requires_json_object_with_string_reason(client, payload):
    note = upload_note(client)
    response = client.post(
        f"/notes/{note['id']}/reports",
        headers=MEMBER_AUTH,
        json=payload,
    )

    assert response.status_code == 400
    assert response.get_json()["fields"]["reason"] == "required"


def test_report_rejects_reason_over_500_characters(client):
    note = upload_note(client)

    response = create_report(client, note["id"], reason="x" * 501)

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "validation_failed",
        "fields": {"reason": "max_length"},
    }


def test_report_requires_authentication(client):
    note = upload_note(client)

    response = client.post(f"/notes/{note['id']}/reports", json={"reason": "เหตุผล"})

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_report_returns_503_when_identity_unavailable(client, identity):
    note = upload_note(client)
    identity.down = True

    response = create_report(client, note["id"])

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_report_missing_note_returns_404(client):
    response = create_report(client, 99999)

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_duplicate_report_from_same_user_returns_409(client, session_factory):
    note = upload_note(client)
    assert create_report(client, note["id"]).status_code == 201

    response = create_report(client, note["id"])

    assert response.status_code == 409
    assert response.get_json()["error"] == "already_reported"
    assert report_count(session_factory) == 1


def test_report_unique_constraint_rejects_duplicate_database_insert(client, session_factory):
    note = upload_note(client)
    assert create_report(client, note["id"]).status_code == 201

    with session_factory() as session:
        session.add(
            Report(
                note_id=note["id"],
                reporter_id=MEMBER["id"],
                reporter_name=MEMBER["display_name"],
                reason="duplicate inserted directly",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()

    constraint_names = {
        constraint.name for constraint in Report.__table__.constraints
    }
    assert "uq_reports_reporter_note" in constraint_names
    assert report_count(session_factory) == 1


def test_different_users_can_report_same_note(client):
    note = upload_note(client)

    first = create_report(client, note["id"], headers=MEMBER_AUTH)
    second = create_report(client, note["id"], headers=OTHER_MEMBER_AUTH)
    listed = client.get("/reports", headers=ADMIN_AUTH).get_json()

    assert first.status_code == 201
    assert second.status_code == 201
    assert listed["count"] == 2
    assert {report["reporter_id"] for report in listed["reports"]} == {7, 8}


def test_non_admin_cannot_list_reports(client):
    response = client.get("/reports", headers=MEMBER_AUTH)

    assert response.status_code == 403
    assert response.get_json()["error"] == "forbidden"


def test_admin_can_list_reports(client):
    note = upload_note(client)
    create_report(client, note["id"], reason="first report")
    create_report(client, note["id"], headers=OTHER_MEMBER_AUTH, reason="second report")

    response = client.get("/reports", headers=ADMIN_AUTH)

    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 2
    assert all(
        {
            "id",
            "note_id",
            "reporter_id",
            "reporter_name",
            "reason",
            "created_at",
            "note",
        }
        == set(report)
        for report in body["reports"]
    )
    assert all(report["note"]["id"] == note["id"] for report in body["reports"])
    assert {report["reason"] for report in body["reports"]} == {
        "first report",
        "second report",
    }
    assert {report["reporter_name"] for report in body["reports"]} == {
        MEMBER["display_name"],
        OTHER_MEMBER["display_name"],
    }
    assert {report["reporter_id"] for report in body["reports"]} == {
        MEMBER["id"],
        OTHER_MEMBER["id"],
    }
    assert all(report["note"]["title"] == note["title"] for report in body["reports"])
    assert [report["id"] for report in body["reports"]] == sorted(
        (report["id"] for report in body["reports"]), reverse=True
    )


def test_admin_list_reports_returns_empty_list(client):
    response = client.get("/reports", headers=ADMIN_AUTH)

    assert response.status_code == 200
    assert response.get_json() == {"count": 0, "reports": []}


def test_admin_cannot_list_reports_without_auth(client):
    response = client.get("/reports")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_admin_list_reports_returns_503_when_identity_unavailable(client, identity):
    identity.down = True

    response = client.get("/reports", headers=ADMIN_AUTH)

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_admin_can_delete_report(client):
    note = upload_note(client)
    report_id = create_report(client, note["id"]).get_json()["id"]

    response = client.delete(f"/reports/{report_id}", headers=ADMIN_AUTH)

    assert response.status_code == 204
    assert client.get("/reports", headers=ADMIN_AUTH).get_json() == {
        "count": 0,
        "reports": [],
    }
    assert client.get(f"/notes/{note['id']}").status_code == 200


def test_non_admin_cannot_delete_report(client, session_factory):
    note = upload_note(client)
    report_id = create_report(client, note["id"]).get_json()["id"]

    response = client.delete(f"/reports/{report_id}", headers=MEMBER_AUTH)

    assert response.status_code == 403
    assert report_count(session_factory) == 1


def test_delete_missing_report_returns_404(client):
    response = client.delete("/reports/99999", headers=ADMIN_AUTH)

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_admin_can_delete_reported_note_and_cascade_report(client, session_factory):
    note = upload_note(client)
    report_id = create_report(client, note["id"]).get_json()["id"]

    response = client.delete(f"/reports/{report_id}/note", headers=ADMIN_AUTH)

    assert response.status_code == 204
    assert report_count(session_factory) == 0
    assert client.get(f"/notes/{note['id']}").status_code == 404


def test_delete_reported_note_removes_stored_file(client, tmp_path):
    note = upload_note(client)
    storage = tmp_path / "storage"
    assert any(p.is_file() for p in storage.rglob("*"))

    report_id = create_report(client, note["id"]).get_json()["id"]

    response = client.delete(
        f"/reports/{report_id}/note",
        headers=ADMIN_AUTH,
    )

    assert response.status_code == 204
    assert not any(p.is_file() for p in storage.rglob("*"))


def test_admin_can_reject_report_without_deleting_note(client, session_factory):
    note = upload_note(client)
    report_id = create_report(client, note["id"]).get_json()["id"]

    response = client.delete(f"/reports/{report_id}", headers=ADMIN_AUTH)

    assert response.status_code == 204
    assert report_count(session_factory) == 0
    assert client.get(f"/notes/{note['id']}").status_code == 200


def test_deleting_reported_note_does_not_affect_unrelated_note_or_report(
    client, session_factory
):
    reported_note = upload_note(client)
    unrelated_note = upload_note(client)
    reported_id = create_report(client, reported_note["id"]).get_json()["id"]
    unrelated_report = create_report(
        client, unrelated_note["id"], headers=OTHER_MEMBER_AUTH
    ).get_json()

    response = client.delete(f"/reports/{reported_id}/note", headers=ADMIN_AUTH)

    assert response.status_code == 204
    assert client.get(f"/notes/{reported_note['id']}").status_code == 404
    assert client.get(f"/notes/{unrelated_note['id']}").status_code == 200
    assert report_count(session_factory) == 1
    with session_factory() as session:
        assert session.get(Report, unrelated_report["id"]) is not None
        assert session.get(Note, unrelated_note["id"]) is not None


def test_non_admin_cannot_delete_reported_note(client, session_factory):
    note = upload_note(client)
    report_id = create_report(client, note["id"]).get_json()["id"]

    response = client.delete(
        f"/reports/{report_id}/note", headers=MEMBER_AUTH
    )

    assert response.status_code == 403
    assert client.get(f"/notes/{note['id']}").status_code == 200
    assert report_count(session_factory) == 1


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/reports"),
        ("DELETE", "/reports/99999"),
        ("DELETE", "/reports/99999/note"),
    ],
)
def test_admin_report_actions_require_authentication(client, method, path):
    response = client.open(path, method=method)

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_delete_reported_note_returns_503_when_identity_unavailable(
    client, identity
):
    identity.down = True

    response = client.delete("/reports/99999/note", headers=ADMIN_AUTH)

    assert response.status_code == 503
    assert response.get_json()["error"] == "auth_unavailable"


def test_delete_missing_reported_note_returns_404(client):
    response = client.delete("/reports/99999/note", headers=ADMIN_AUTH)

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"


def test_admin_ids_ignore_whitespace_and_non_numeric_values(client, monkeypatch):
    monkeypatch.setenv("ADMIN_USER_IDS", " 7, invalid, 99.0 ")

    assert client.get("/reports", headers=MEMBER_AUTH).status_code == 200
    assert client.get("/reports", headers=ADMIN_AUTH).status_code == 403


def test_deleting_note_cascades_to_its_reports(client, session_factory):
    note = upload_note(client)
    create_report(client, note["id"])

    response = client.delete(
        f"/notes/{note['id']}",
        headers={"X-Note-Token": note["edit_token"]},
    )

    assert response.status_code == 204
    assert report_count(session_factory) == 0