"""เทสต์ `GET /notes?sort=rating` — Issue #83

เรียงคะแนนเฉลี่ยมากไปน้อย · ยังไม่มีคะแนนอยู่ท้าย · เท่ากันดูจำนวนคนให้คะแนน แล้วดูความใหม่
"""

import io
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import update

from identity import IdentityUnavailable
from models import Note, build_session_factory
from storage import LocalFileStorage

UPLOADER = {"Authorization": "Bearer uploader"}
RATERS = [{"Authorization": f"Bearer rater{i}"} for i in range(3)]
USERS = {"Bearer uploader": {"id": 1, "display_name": "Uploader"}}
USERS.update({f"Bearer rater{i}": {"id": 10 + i, "display_name": f"Rater {i}"} for i in range(3)})

FORM = {
    "title": "โน้ต",
    "subject_name": "Operating Systems",
    "subject_code": "CS301",
    "faculty": "ICT",
    "year_level": "3",
    "lesson": "บทที่ 1",
}


class FakeIdentity:
    def __call__(self, authorization):
        user = USERS.get(authorization)
        if authorization == "Bearer down":
            raise IdentityUnavailable("down")
        return dict(user) if user else None


@pytest.fixture
def database_url(make_db_url):
    return make_db_url("test.db")


@pytest.fixture
def client(tmp_path, database_url, notes_create_app):
    app = notes_create_app(
        database_url=database_url,
        storage=LocalFileStorage(str(tmp_path / "storage")),
        identity=FakeIdentity(),
    )
    app.config.update(TESTING=True)
    return app.test_client()


@pytest.fixture
def db(database_url, client):
    return build_session_factory(database_url)


def new_note(client, title, **overrides):
    form = {**FORM, "title": title, **overrides}
    form["file"] = (io.BytesIO(b"%PDF-1.4 fake"), "n.pdf", "application/pdf")
    response = client.post("/notes", data=form, headers=UPLOADER, content_type="multipart/form-data")
    assert response.status_code == 201
    return response.get_json()["id"]


def rate(client, note_id, *values):
    for rater, value in zip(RATERS, values):
        client.get(f"/notes/{note_id}", headers=rater)
        assert client.put(f"/notes/{note_id}/rating", json={"rating": value}, headers=rater).status_code == 200


def titles(client, query="sort=rating"):
    response = client.get(f"/notes?{query}")
    assert response.status_code == 200
    return [item["title"] for item in response.get_json()["items"]]


def test_highest_average_first_and_unrated_last(client):
    rate(client, new_note(client, "สาม"), 3)
    new_note(client, "ไม่มีคะแนน")
    rate(client, new_note(client, "ห้า"), 5)
    rate(client, new_note(client, "สี่"), 4)

    assert titles(client) == ["ห้า", "สี่", "สาม", "ไม่มีคะแนน"]


def test_average_not_last_rating_decides(client):
    rate(client, new_note(client, "เฉลี่ย 3.5"), 5, 2)
    rate(client, new_note(client, "เฉลี่ย 4"), 4)

    assert titles(client) == ["เฉลี่ย 4", "เฉลี่ย 3.5"]


def test_same_average_more_ratings_first(client):
    rate(client, new_note(client, "สองคน"), 4, 4)
    rate(client, new_note(client, "คนเดียว"), 4)
    rate(client, new_note(client, "สามคน"), 4, 4, 4)

    assert titles(client) == ["สามคน", "สองคน", "คนเดียว"]


def test_full_tie_newest_first(client, db):
    older = new_note(client, "เก่า")
    newer = new_note(client, "ใหม่")
    rate(client, older, 5)
    rate(client, newer, 5)
    with db() as session:
        session.execute(
            update(Note)
            .where(Note.id == older)
            .values(created_at=datetime.now(timezone.utc) - timedelta(days=1))
        )
        session.commit()

    assert titles(client) == ["ใหม่", "เก่า"]


def test_unrated_notes_keep_newest_first_among_themselves(client):
    new_note(client, "แรก")
    new_note(client, "สอง")

    assert titles(client) == ["สอง", "แรก"]


def test_sort_by_rating_works_with_filters_and_paging(client):
    rate(client, new_note(client, "CS ห้า"), 5)
    rate(client, new_note(client, "MA ห้า", subject_code="MA101"), 5, 5)
    rate(client, new_note(client, "CS สาม"), 3)
    new_note(client, "CS ไม่มีคะแนน")

    assert titles(client, "sort=rating&subject_code=CS301") == ["CS ห้า", "CS สาม", "CS ไม่มีคะแนน"]
    assert titles(client, "sort=rating&subject_code=CS301&limit=1&offset=1") == ["CS สาม"]


def test_unknown_sort_is_still_400(client):
    response = client.get("/notes?sort=popular")

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_filter", "field": "sort"}
