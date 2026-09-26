"""Tests ของ Preview Note Before Download — US-11 (#11)

ครอบ AC ข้อ 1-2 ฝั่ง backend: ดูตัวอย่างได้โดยไม่ต้องโหลดไฟล์เต็ม (ได้รูป PNG ย่อขนาด)
ส่วน AC ข้อ 3 (ปิดตัวอย่างแล้วกลับตำแหน่งเดิมในผลค้นหา) เป็นงาน UI ยังไม่อยู่ในชุดนี้
"""

import io

import pytest
from PIL import Image

from preview import MAX_SOURCE_PIXELS, PREVIEW_MAX_WIDTH, PreviewUnavailable, render_preview
from storage import LocalFileStorage
from test_notes_api import BASE_FORM

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def make_image(fmt, size=(1600, 1200), mode="RGB"):
    buffer = io.BytesIO()
    Image.new(mode, size, "white").save(buffer, format=fmt)
    return buffer.getvalue()


@pytest.fixture
def env(tmp_path, notes_create_app):
    storage = LocalFileStorage(str(tmp_path / "storage"))
    app = notes_create_app(database_url=f"sqlite:///{tmp_path / 'test.db'}", storage=storage)
    app.config.update(TESTING=True)
    return app.test_client(), storage, tmp_path / "storage"


def upload(client, data, name, mimetype, **overrides):
    form = {**BASE_FORM, **overrides, "file": (io.BytesIO(data), name, mimetype)}
    response = client.post("/notes", data=form, content_type="multipart/form-data")
    assert response.status_code == 201
    return response.get_json()


def result_size(response):
    return Image.open(io.BytesIO(response.data)).size


# --- API ---


def test_png_preview_is_a_downscaled_png(env):
    client, _, _ = env
    note = upload(client, make_image("PNG"), "a.png", "image/png")

    response = client.get(f"/notes/{note['id']}/preview")

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(PNG_MAGIC)
    assert result_size(response) == (PREVIEW_MAX_WIDTH, 600)


def test_jpeg_preview_is_returned_as_png(env):
    client, _, _ = env
    note = upload(client, make_image("JPEG"), "a.jpg", "image/jpeg")

    response = client.get(f"/notes/{note['id']}/preview")

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(PNG_MAGIC)


def test_preview_is_inline_and_cacheable(env):
    client, _, _ = env
    note = upload(client, make_image("PNG"), "a.png", "image/png")

    response = client.get(f"/notes/{note['id']}/preview")

    assert "attachment" not in response.headers.get("Content-Disposition", "")
    assert response.headers["Cache-Control"] == "public, max-age=86400"


def test_preview_is_generated_once_and_then_served_from_storage(env):
    client, storage, root = env
    note = upload(client, make_image("PNG"), "a.png", "image/png")
    first = client.get(f"/notes/{note['id']}/preview")
    assert len(list((root / "previews").glob("*.png"))) == 1

    # ลบไฟล์ต้นฉบับทิ้ง ถ้ายังได้รูปเดิมแปลว่ารอบสองส่งจากที่ cache ไม่ได้ render ใหม่
    key = next(p.name for p in root.iterdir() if p.is_file())
    storage.delete(key)
    second = client.get(f"/notes/{note['id']}/preview")

    assert second.status_code == 200
    assert second.data == first.data


def test_preview_of_unknown_note_returns_404(env):
    client, _, _ = env

    response = client.get("/notes/999/preview")

    assert response.status_code == 404
    assert response.get_json() == {"error": "not_found"}


def test_preview_when_file_is_missing_returns_file_not_found(env):
    client, storage, root = env
    note = upload(client, make_image("PNG"), "a.png", "image/png")
    key = next(p.name for p in root.iterdir() if p.is_file())
    storage.delete(key)

    response = client.get(f"/notes/{note['id']}/preview")

    assert response.status_code == 404
    assert response.get_json() == {"error": "file_not_found"}


def test_preview_of_content_that_is_not_an_image_returns_422(env):
    client, _, _ = env
    # validate_file เชื่อ mimetype ที่ client ส่งมา จึงอัปโหลดผ่านได้ แต่ render ต้องไม่พัง
    note = upload(client, b"this is not a png", "fake.png", "image/png")

    response = client.get(f"/notes/{note['id']}/preview")

    assert response.status_code == 422
    assert response.get_json() == {"error": "preview_unavailable"}


def test_failed_preview_leaves_nothing_in_storage(env):
    client, _, root = env
    note = upload(client, b"this is not a png", "fake.png", "image/png")

    client.get(f"/notes/{note['id']}/preview")

    assert not (root / "previews").exists() or not list((root / "previews").iterdir())


def test_deleting_a_note_removes_its_preview(env):
    client, _, root = env
    note = upload(client, make_image("PNG"), "a.png", "image/png")
    client.get(f"/notes/{note['id']}/preview")
    assert list((root / "previews").glob("*.png"))

    response = client.delete(
        f"/notes/{note['id']}", headers={"X-Note-Token": note["edit_token"]}
    )

    assert response.status_code == 204
    assert not list((root / "previews").glob("*.png"))
    assert not [p for p in root.iterdir() if p.is_file()]


def test_note_responses_include_preview_url(env):
    client, _, _ = env
    note = upload(client, make_image("PNG"), "a.png", "image/png")

    detail = client.get(f"/notes/{note['id']}").get_json()
    listing = client.get("/notes").get_json()

    assert detail["preview_url"] == f"/notes/{note['id']}/preview"
    assert listing["items"][0]["preview_url"] == f"/notes/{note['id']}/preview"


# --- render_preview (pure function) ---


def test_render_does_not_upscale_small_images():
    data = render_preview(io.BytesIO(make_image("PNG", size=(300, 200))), "image/png")

    assert Image.open(io.BytesIO(data)).size == (300, 200)


def test_render_converts_cmyk_jpeg_to_png():
    data = render_preview(io.BytesIO(make_image("JPEG", mode="CMYK")), "image/jpeg")

    assert data.startswith(PNG_MAGIC)


def test_render_keeps_transparency_of_rgba_png():
    data = render_preview(io.BytesIO(make_image("PNG", mode="RGBA")), "image/png")

    assert Image.open(io.BytesIO(data)).mode == "RGBA"


def test_render_rejects_oversized_source_image():
    side = int(MAX_SOURCE_PIXELS**0.5) + 1
    source = io.BytesIO(make_image("PNG", size=(side, side), mode="1"))

    with pytest.raises(PreviewUnavailable):
        render_preview(source, "image/png")


def test_render_rejects_corrupted_image():
    truncated = make_image("PNG")[:100]

    with pytest.raises(PreviewUnavailable):
        render_preview(io.BytesIO(truncated), "image/png")


def test_render_rejects_content_type_mismatch():
    # ประกาศว่าเป็น JPEG แต่เนื้อจริงเป็น PNG — formats ที่จำกัดไว้ต้องไม่ยอมรับ
    with pytest.raises(PreviewUnavailable):
        render_preview(io.BytesIO(make_image("PNG")), "image/jpeg")


def test_render_rejects_unsupported_content_type():
    with pytest.raises(PreviewUnavailable):
        render_preview(io.BytesIO(b"%PDF-1.4"), "application/pdf")
