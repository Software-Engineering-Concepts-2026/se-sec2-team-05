"""Tests ของ Preview Note Before Download — US-11 (#11)

ครอบ AC ข้อ 1-2 ฝั่ง backend: ดูตัวอย่างได้โดยไม่ต้องโหลดไฟล์เต็ม (ได้รูป PNG ย่อขนาด)
ส่วน AC ข้อ 3 (ปิดตัวอย่างแล้วกลับตำแหน่งเดิมในผลค้นหา) เป็นงาน UI ยังไม่อยู่ในชุดนี้
"""

import io

import pypdfium2
import pytest
from PIL import Image

from preview import MAX_SOURCE_PIXELS, PREVIEW_MAX_WIDTH, PreviewUnavailable, render_preview
from storage import LocalFileStorage
from test_notes_api import AUTH_HEADER, BASE_FORM, FakeIdentity

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def make_image(fmt, size=(1600, 1200), mode="RGB"):
    buffer = io.BytesIO()
    Image.new(mode, size, "white").save(buffer, format=fmt)
    return buffer.getvalue()


def make_pdf(page_sizes):
    """สร้าง PDF จริงด้วย pdfium — ให้แต่ละหน้าขนาดต่างกัน เพื่อดูจากขนาดรูปว่า render หน้าไหน"""
    pdf = pypdfium2.PdfDocument.new()
    for width, height in page_sizes:
        pdf.new_page(width, height)
    buffer = io.BytesIO()
    pdf.save(buffer)
    pdf.close()
    return buffer.getvalue()


@pytest.fixture
def env(tmp_path, make_db_url, notes_create_app):
    storage = LocalFileStorage(str(tmp_path / "storage"))
    app = notes_create_app(
        database_url=make_db_url("test.db"),
        storage=storage,
        identity=FakeIdentity(),
    )
    app.config.update(TESTING=True)
    return app.test_client(), storage, tmp_path / "storage"


def upload(client, data, name, mimetype, **overrides):
    form = {**BASE_FORM, **overrides, "file": (io.BytesIO(data), name, mimetype)}
    response = client.post(
        "/notes", data=form, headers=AUTH_HEADER, content_type="multipart/form-data"
    )
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


def test_pdf_preview_is_first_page_as_png(env):
    client, _, _ = env
    note = upload(client, make_pdf([(600, 800), (300, 300)]), "a.pdf", "application/pdf")

    response = client.get(f"/notes/{note['id']}/preview")

    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(PNG_MAGIC)
    # หน้า 1 ขนาด 600x800pt ลดสเกลให้กว้าง 800px ส่วนหน้า 2 (300x300pt) จะได้ 600x600
    assert result_size(response) == (800, 1067)


def test_pdf_preview_is_cached_like_images(env):
    client, _, root = env
    note = upload(client, make_pdf([(600, 800)]), "a.pdf", "application/pdf")

    client.get(f"/notes/{note['id']}/preview")

    assert len(list((root / "previews").glob("*.png"))) == 1


def test_preview_of_fake_pdf_returns_422(env):
    client, _, _ = env
    note = upload(client, b"%PDF-1.4 fake note", "fake.pdf", "application/pdf")

    response = client.get(f"/notes/{note['id']}/preview")

    assert response.status_code == 422
    assert response.get_json() == {"error": "preview_unavailable"}


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
        render_preview(io.BytesIO(b"hello"), "text/plain")


def test_render_pdf_uses_only_the_first_page():
    data = render_preview(io.BytesIO(make_pdf([(300, 300), (600, 800)])), "application/pdf")

    # หน้า 1 ขนาด 300x300pt render ที่ 2 เท่า = 600x600 ถ้าเป็นหน้า 2 จะกว้าง 800
    assert Image.open(io.BytesIO(data)).size == (600, 600)


def test_render_pdf_never_exceeds_max_width():
    data = render_preview(io.BytesIO(make_pdf([(2000, 1000)])), "application/pdf")

    assert Image.open(io.BytesIO(data)).size == (PREVIEW_MAX_WIDTH, 400)


def test_render_pdf_a4_page_never_exceeds_max_width():
    # A4 (595x842pt): 800/595 คูณ pdfium ปัดขึ้นได้เป็น 801px ถ้าไม่เช็คซ้ำหลัง render
    data = render_preview(io.BytesIO(make_pdf([(595, 842)])), "application/pdf")

    assert Image.open(io.BytesIO(data)).size[0] <= PREVIEW_MAX_WIDTH


def test_render_rejects_pdf_without_pages():
    with pytest.raises(PreviewUnavailable):
        render_preview(io.BytesIO(make_pdf([])), "application/pdf")


def test_render_rejects_pdf_with_oversized_first_page():
    # หน้าแคบแต่สูงผิดปกติ (เกินที่ PDF spec แนะนำ) render แล้วจะเกินเพดานพิกเซล
    with pytest.raises(PreviewUnavailable):
        render_preview(io.BytesIO(make_pdf([(100, 300000)])), "application/pdf")


def test_render_rejects_corrupted_pdf():
    truncated = make_pdf([(600, 800)])[:60]

    with pytest.raises(PreviewUnavailable):
        render_preview(io.BytesIO(truncated), "application/pdf")


def test_render_applies_exif_orientation_from_phone_photos():
    # กล้องมือถือเก็บ sensor เป็นแนวนอน (1200x800) แล้วใช้ EXIF Orientation=6 บอกว่า
    # จริงๆ ภาพเป็นแนวตั้ง ถ้าไม่หมุนตาม EXIF ก่อน จะได้ preview นอนตะแคงผิดกับไฟล์จริง
    buffer = io.BytesIO()
    source = Image.new("RGB", (1200, 800), "white")
    exif = source.getexif()
    exif[0x0112] = 6
    source.save(buffer, format="JPEG", exif=exif)

    data = render_preview(io.BytesIO(buffer.getvalue()), "image/jpeg")

    result = Image.open(io.BytesIO(data))
    assert result.size == (800, 1200)
