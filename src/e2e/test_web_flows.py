"""E2E-01 ถึง E2E-06 — เส้นทางหลักของผู้ใช้ผ่านหน้าเว็บจริง (test plan หัวข้อ 2.21)

ก่อนหน้านี้ตรวจด้วยมือบน compose ทุกครั้งที่แก้หน้าเว็บ (test plan หัวข้อ 3) ชุดนี้ทำซ้ำเส้นทางเดิม
อัตโนมัติ: สมัคร → อัปโหลด → ค้นหา → อีกบัญชีดาวน์โหลด/ให้คะแนน/ขอบคุณ/แสดงความคิดเห็น
→ แก้และลบด้วยรหัสแก้ไข รวมถึงยอดรวมผลค้นหาและความกว้างหน้าจอมือถือ (NFR-008)
"""

from playwright.sync_api import expect

from conftest import unique


def test_register_logs_in_and_the_upload_page_knows_who(page, api):
    """E2E-01: สมัครแล้วเข้าสู่ระบบให้เอง ไม่ต้องกรอกซ้ำ (US-05, US-06)"""
    email = f"{unique('e2e-').lower()}@up.ac.th"

    page.goto("/login.html#register")
    form = page.locator("#registerForm")
    form.locator('[name="display_name"]').fill("สมาชิกใหม่ E2E")
    form.locator('[name="email"]').fill(email)
    form.locator('[name="password"]').fill("e2e-password-123")
    form.get_by_role("button", name="สมัครสมาชิก").click()
    page.wait_for_url("**/")

    page.goto("/upload.html")
    expect(page.locator("#uploadForm")).to_be_visible()
    expect(page.locator("#uploaderLine")).to_contain_text("สมาชิกใหม่ E2E")


def test_upload_gives_an_edit_token_and_search_finds_the_note(page, api, log_in, tmp_path):
    """E2E-02: อัปโหลดผ่านฟอร์มได้รหัสแก้ไข แล้วค้นหาเจอพร้อมชื่อผู้อัปโหลด (US-07, US-08, US-09, US-31)"""
    owner = api.register("เจ้าของโน้ต E2E")
    code = unique("UP")
    # ลิงก์ "ไปหน้าค้นหา" ค้นด้วยชื่อโน้ต ชื่อจึงต้องไม่ซ้ำกับรอบก่อนที่ยังอยู่ใน DB
    title = f"สรุป Big-O จากหน้าเว็บ {code}"
    pdf = tmp_path / "lecture.pdf"
    pdf.write_bytes(b"%PDF-1.4\n% uploaded from the browser\n")

    log_in(owner)
    page.goto("/upload.html")
    page.locator('[name="file"]').set_input_files(pdf)
    page.locator('[name="title"]').fill(title)
    page.locator('[name="subject_code"]').fill(code)
    page.locator('[name="subject_name"]').fill("Algorithms")
    page.locator('[name="faculty"]').fill("ICT")
    page.locator('[name="year_level"]').select_option("2")
    page.locator('[name="lesson"]').fill("บทที่ 2")
    page.get_by_role("button", name="อัปโหลด ✓").click()

    expect(page.locator("#uploadDone")).to_be_visible()
    expect(page.locator("#editToken")).not_to_have_value("")

    page.locator("#doneSearchLink").click()
    expect(page.locator("#resultsCount")).to_have_text("แสดง 1 รายการ")
    card = page.locator("#resultsList").get_by_text(title)
    expect(card).to_be_visible()
    expect(page.locator("#resultsList")).to_contain_text("เจ้าของโน้ต E2E")


def test_reader_downloads_rates_thanks_saves_and_comments(page, api, log_in):
    """E2E-03: อีกบัญชีใช้โน้ตครบทุกปุ่มบนหน้าโน้ต (US-12, US-13, US-14, US-15, US-28)"""
    owner = api.register("เจ้าของ E2E")
    note = api.upload(owner, title="โน้ตให้คนอื่นใช้")
    reader = api.register("ผู้อ่าน E2E")

    log_in(reader)
    page.goto(f"/note.html?id={note['id']}")
    expect(page.locator("#noteTitle")).to_have_text("โน้ตให้คนอื่นใช้")

    with page.expect_download() as download:
        page.locator("#downloadBtn").click()
    assert download.value.suggested_filename == "note.pdf"
    expect(page.locator("#actionStatus")).to_have_text("ดาวน์โหลดแล้ว")

    page.locator('#ratingStars [data-rating="4"]').click()
    page.locator("#submitRating").click()
    expect(page.locator("#ratingSubmitStatus")).to_have_text("บันทึกคะแนนแล้ว")
    expect(page.locator("#ratingAverage")).to_contain_text("4.0")

    # ปุ่มขอบคุณขึ้นหลังดาวน์โหลดเท่านั้น (US-28)
    page.locator("#thanksBtn").click()
    expect(page.locator("#thanksMessage")).to_contain_text("ส่งคำขอบคุณถึงเจ้าของโน้ตแล้ว")

    page.locator("#favoriteBtn").click()
    expect(page.locator("#favoriteBtn")).to_have_attribute("aria-pressed", "true")

    page.locator("#commentInput").fill("ขอบคุณครับ สรุปอ่านง่ายมาก")
    page.locator("#commentForm").get_by_role("button", name="โพสต์").click()
    expect(page.locator("#commentsList")).to_contain_text("ขอบคุณครับ สรุปอ่านง่ายมาก")

    # ทุกอย่างที่กดต้องไปถึง API จริง ไม่ใช่แค่เปลี่ยนหน้าจอ
    page.reload()
    expect(page.locator("#ratingAverage")).to_contain_text("4.0")
    expect(page.locator("#favoriteBtn")).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#commentsList")).to_contain_text("ขอบคุณครับ สรุปอ่านง่ายมาก")
    expect(page.locator("#noteMeta")).to_contain_text("ดาวน์โหลด 1")


def test_edit_and_delete_with_the_edit_token_without_logging_in(page, api):
    """E2E-04: รหัสผิดถูกปฏิเสธ รหัสถูกแก้ชื่อและลบได้ โดยไม่ต้อง login (US-19, US-20)"""
    owner = api.register("เจ้าของรหัส E2E")
    note = api.upload(owner, title="ชื่อเดิม")

    page.goto(f"/edit.html?id={note['id']}")
    token_form = page.locator("#tokenForm")
    token_form.locator('[name="token"]').fill("not-the-real-token")
    token_form.get_by_role("button", name="ตรวจรหัส").click()
    expect(token_form.locator('[data-error-for="token"]')).to_be_visible()
    expect(page.locator("#editForm")).to_be_hidden()

    token_form.locator('[name="token"]').fill(note["edit_token"])
    token_form.get_by_role("button", name="ตรวจรหัส").click()
    expect(page.locator("#pageStatus")).to_have_text("รหัสถูกต้อง แก้ข้อมูลแล้วกดบันทึก หรือลบโน้ตนี้ได้")

    edit_form = page.locator("#editForm")
    edit_form.locator('[name="title"]').fill("ชื่อใหม่จากหน้าแก้ไข")
    edit_form.get_by_role("button", name="บันทึก").click()
    expect(page.locator("#pageStatus")).to_have_text("บันทึกการแก้ไขแล้ว")
    page.goto(f"/note.html?id={note['id']}")
    expect(page.locator("#noteTitle")).to_have_text("ชื่อใหม่จากหน้าแก้ไข")

    page.goto(f"/edit.html?id={note['id']}")
    token_form.locator('[name="token"]').fill(note["edit_token"])
    token_form.get_by_role("button", name="ตรวจรหัส").click()
    page.locator("#deleteOpen").click()
    page.locator("#deleteForm").get_by_role("button", name="ลบโน้ต").click()
    expect(page.locator("#deletedBox")).to_be_visible()
    assert api.note_status(note["id"]) == 404


def test_search_shows_the_total_and_loads_the_rest(page, api):
    """E2E-05: 21 โน้ตเกินหน้าแรก (20) — บอกยอดรวม และปุ่มโหลดเพิ่มหายเมื่อครบ"""
    owner = api.register("คนอัปโหลดเยอะ E2E")
    code = unique("PG")
    for i in range(21):
        api.upload(owner, subject_code=code, title=f"ตอนที่ {i + 1}")

    page.goto(f"/?q={code}")
    expect(page.locator("#resultsCount")).to_have_text("แสดง 20 จาก 21 รายการ")
    expect(page.locator("#loadMoreBtn")).to_be_visible()

    page.locator("#loadMoreBtn").click()
    expect(page.locator("#resultsCount")).to_have_text("แสดง 21 รายการ")
    expect(page.locator("#loadMoreBtn")).to_be_hidden()


def test_search_page_fits_a_phone_screen(page, api):
    """E2E-06: กว้าง 375 px ไม่มี scroll แนวนอน และช่องค้นหาเห็นได้ทันทีโดยไม่ต้อง scroll (NFR-008, NFR-009)"""
    page.set_viewport_size({"width": 375, "height": 740})

    for path in ("/", "/login.html", "/upload.html", "/stats.html"):
        page.goto(path)
        page.wait_for_load_state("networkidle")
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 0, f"{path} เลื่อนแนวนอนได้ {overflow}px"

    page.goto("/")
    search_box = page.locator("#q").bounding_box()
    assert search_box is not None
    assert search_box["y"] + search_box["height"] <= 740
    expect(page.get_by_role("button", name="ค้นหา", exact=True)).to_be_in_viewport()
