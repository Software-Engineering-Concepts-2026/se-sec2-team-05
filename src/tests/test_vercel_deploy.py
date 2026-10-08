"""Tests ของการ deploy บน Vercel (ADR-009)

ครอบ 4 เรื่องที่ Vercel ต่างจาก docker compose:
1. ไฟล์โน้ตเก็บใน Vercel Blob แบบ private ผ่าน `BlobFileStorage` (ใช้ client ปลอม ไม่ต่อเน็ต)
2. URL ของ Neon (`postgres://` / `postgresql://`) ต้องถูกแปลงให้ใช้ psycopg 3
3. request ทั้งก้อนต้องไม่เกินเพดาน body 4.5 MB ของ Vercel Functions
4. `vercel.json` ส่ง path ไปถูก service แบบเดียวกับ `web/nginx.conf`
"""

import io
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

import auth_models
import models
import stats_db
from storage import BlobFileStorage, LocalFileStorage, storage_from_env
from test_notes_api import AUTH_HEADER, BASE_FORM, FakeIdentity
from test_notes_preview import make_image

REPO_ROOT = Path(__file__).resolve().parents[2]
VERCEL_BODY_LIMIT_BYTES = 4_500_000  # เพดาน body ของ Vercel Functions (นับแบบทศนิยมให้เข้มที่สุด)


class FakeNotFound(Exception):
    pass


class FakeBlobClient:
    """เลียน `vercel.blob.BlobClient` เท่าที่ BlobFileStorage ใช้ และจดทุก call ไว้ตรวจ"""

    def __init__(self):
        self.blobs = {}
        self.puts = []

    def put(self, path, body, *, access, content_type=None, overwrite=False):
        if path in self.blobs and not overwrite:
            raise AssertionError(f"overwrite {path!r} without overwrite=True")
        self.puts.append({"path": path, "access": access, "content_type": content_type, "overwrite": overwrite})
        self.blobs[path] = bytes(body)

    def get(self, path, *, access):
        assert access == "private"
        if path not in self.blobs:
            raise FakeNotFound(path)
        return SimpleNamespace(content=self.blobs[path])

    def head(self, path):
        if path not in self.blobs:
            raise FakeNotFound(path)
        return SimpleNamespace(size=len(self.blobs[path]))

    def delete(self, path):
        if path not in self.blobs:
            raise FakeNotFound(path)
        del self.blobs[path]


@pytest.fixture
def blob():
    client = FakeBlobClient()
    return client, BlobFileStorage(client, FakeNotFound)


@pytest.fixture
def blob_app(tmp_path, notes_create_app, blob):
    client, storage = blob
    app = notes_create_app(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        storage=storage,
        identity=FakeIdentity(),
    )
    app.config.update(TESTING=True)
    return app.test_client(), client


def upload(client, data=b"%PDF-1.4 vercel test", name="note.pdf", mimetype="application/pdf"):
    form = {**BASE_FORM, "file": (io.BytesIO(data), name, mimetype)}
    response = client.post("/notes", data=form, headers=AUTH_HEADER, content_type="multipart/form-data")
    assert response.status_code == 201
    return response.get_json()


# --- 1. BlobFileStorage ---


def test_blob_storage_keeps_the_same_key_format_as_local(blob, tmp_path):
    _, storage = blob
    local = LocalFileStorage(str(tmp_path / "local"))

    blob_key = storage.build_key("application/pdf")

    assert blob_key.endswith(".pdf")
    assert len(blob_key) == len(local.build_key("application/pdf"))
    assert blob_key != storage.build_key("application/pdf")


def test_blob_storage_round_trip_is_private(blob):
    client, storage = blob
    upload_file = SimpleNamespace(stream=io.BytesIO(b"note bytes"), mimetype="application/pdf")

    storage.save("a.pdf", upload_file)

    assert client.puts == [
        {"path": "a.pdf", "access": "private", "content_type": "application/pdf", "overwrite": False}
    ]
    assert storage.exists("a.pdf")
    with storage.open("a.pdf") as handle:
        assert handle.read() == b"note bytes"


def test_blob_storage_missing_file_looks_like_a_missing_file_on_disk(blob):
    _, storage = blob

    assert not storage.exists("gone.pdf")
    with pytest.raises(FileNotFoundError):
        storage.open("gone.pdf")
    storage.delete("gone.pdf")  # ลบของที่ไม่มีต้องไม่ error เหมือน unlink(missing_ok=True)


def test_blob_storage_preview_can_be_written_twice(blob):
    client, storage = blob

    storage.save_bytes("a.preview.png", b"one")
    storage.save_bytes("a.preview.png", b"two")

    assert client.blobs["a.preview.png"] == b"two"
    assert {put["overwrite"] for put in client.puts} == {True}


def test_upload_download_preview_and_delete_through_the_api_with_blob(blob_app):
    client, blob_client = blob_app
    note = upload(client, make_image("PNG"), "a.png", "image/png")
    [stored_key] = blob_client.blobs

    download = client.get(f"/notes/{note['id']}/download")
    preview = client.get(f"/notes/{note['id']}/preview")

    assert download.status_code == 200
    assert download.data == blob_client.blobs[stored_key]
    assert preview.status_code == 200
    assert preview.mimetype == "image/png"
    assert len(blob_client.blobs) == 2  # ไฟล์จริง + รูปตัวอย่างที่สร้างครั้งแรก

    deleted = client.delete(f"/notes/{note['id']}", headers={"X-Note-Token": note["edit_token"]})

    assert deleted.status_code == 204
    assert blob_client.blobs == {}


def test_download_of_a_note_whose_blob_is_gone_is_not_a_crash(blob_app):
    client, blob_client = blob_app
    note = upload(client)
    blob_client.blobs.clear()

    response = client.get(f"/notes/{note['id']}/download")

    assert response.status_code == 404


def test_storage_from_env_defaults_to_local_disk(monkeypatch, tmp_path):
    monkeypatch.delenv("NOTES_STORAGE_BACKEND", raising=False)
    monkeypatch.setenv("NOTES_STORAGE_DIR", str(tmp_path / "files"))

    assert isinstance(storage_from_env(), LocalFileStorage)


def test_storage_from_env_picks_blob_when_asked(monkeypatch):
    pytest.importorskip("vercel.blob")
    monkeypatch.setenv("NOTES_STORAGE_BACKEND", "blob")

    assert isinstance(storage_from_env(), BlobFileStorage)


# --- 2. DATABASE_URL จาก Neon ---


@pytest.mark.parametrize("module", [models, auth_models, stats_db], ids=["notes", "auth", "stats"])
@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("postgres://u:p@host/db?sslmode=require", "postgresql+psycopg://u:p@host/db?sslmode=require"),
        ("postgresql://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql+psycopg://u:p@db:5432/noteshare", "postgresql+psycopg://u:p@db:5432/noteshare"),
        ("sqlite:///notes.db", "sqlite:///notes.db"),
    ],
)
def test_neon_urls_use_psycopg3(module, given, expected):
    assert module.sqlalchemy_url(given) == expected


# --- 3. เพดาน body ---


def test_largest_accepted_request_fits_the_vercel_body_limit(notes_create_app, tmp_path):
    app = notes_create_app(database_url=f"sqlite:///{tmp_path / 'test.db'}", identity=FakeIdentity(),
                           storage=LocalFileStorage(str(tmp_path / "s")))

    assert app.config["MAX_CONTENT_LENGTH"] < VERCEL_BODY_LIMIT_BYTES


# --- 4. vercel.json ---


def _vercel_config():
    return json.loads((REPO_ROOT / "vercel.json").read_text(encoding="utf-8"))


def _service_for(path):
    """จำลองการจับคู่ rewrite ของ Vercel ตามลำดับ (รองรับเฉพาะรูปแบบที่ไฟล์นี้ใช้)"""
    for rule in _vercel_config()["rewrites"]:
        pattern = re.sub(r":\w+\(([^)]*)\)", r"(\1)", rule["source"])
        if re.fullmatch(pattern, path):
            return rule["destination"]["service"]
    return None


@pytest.mark.parametrize(
    ("path", "service"),
    [
        ("/notes/12/stats", "stats"),
        ("/stats", "stats"),
        ("/notes", "notes"),
        ("/notes/12", "notes"),
        ("/notes/12/download", "notes"),
        ("/notes/mine", "notes"),
        ("/reports", "notes"),
        ("/reports/3", "notes"),
        ("/auth/login", "auth"),
        ("/", "web"),
        ("/edit.html", "web"),
    ],
)
def test_vercel_routes_match_the_nginx_gateway(path, service):
    assert _service_for(path) == service


def test_vercel_services_exist_and_call_auth_privately():
    config = _vercel_config()
    services = config["services"]

    for rule in config["rewrites"]:
        assert rule["destination"]["service"] in services
    assert config["rewrites"][-1]["source"] == "/(.*)"
    for name in ("notes", "stats"):
        assert services[name]["bindings"] == [
            {"type": "service", "service": "auth", "format": "url", "env": "AUTH_SERVICE_URL"}
        ]
    for name, service in services.items():
        assert (REPO_ROOT / service["root"]).is_dir(), name
