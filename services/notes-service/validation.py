"""Validation ของ metadata ตาม AC ข้อ 3 ของ US-08 (#8)

แยกออกมาจาก app.py เพราะเป็น pure function ล้วน ทดสอบได้โดยไม่ต้องมี request/DB
(บทเรียนเดียวกับ Lab 7 ที่แยก note-utils.js ออกจากหน้า HTML)
"""

from datetime import date

# ฟิลด์ที่บังคับกรอกตาม AC ข้อแรก: ชื่อวิชา รหัสวิชา คณะ ชั้นปี บทเรียน (+ ชื่อโน้ต)
REQUIRED_FIELDS = ("title", "subject_name", "subject_code", "faculty", "year_level", "lesson")

# ชั้นปีของหลักสูตรปริญญาตรี — ใช้เป็นขอบเขตจนกว่าจะรองรับบัณฑิตศึกษา
MIN_YEAR_LEVEL = 1
MAX_YEAR_LEVEL = 8

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
}

MAX_FILE_BYTES = 20 * 1024 * 1024  # 20 MB

MAX_LENGTHS = {
    "title": 200,
    "subject_name": 200,
    "subject_code": 30,
    "faculty": 100,
    "lesson": 200,
    "topic": 200,
}


def validate_metadata(form):
    """ตรวจ metadata ที่ผู้ใช้กรอก

    คืน (cleaned, errors) — `errors` เป็น dict ของ {field: เหตุผล} ถ้าว่างแปลว่าผ่าน
    เก็บ error ให้ครบทุกฟิลด์ก่อนค่อยคืน ไม่หยุดที่ตัวแรก เพื่อให้ผู้ใช้แก้ทีเดียวจบ
    """
    cleaned, errors = {}, {}

    for field in REQUIRED_FIELDS:
        value = (form.get(field) or "").strip()
        if not value:
            errors[field] = "จำเป็นต้องกรอก"
            continue
        limit = MAX_LENGTHS.get(field)
        if limit and len(value) > limit:
            errors[field] = f"ยาวเกิน {limit} ตัวอักษร"
            continue
        cleaned[field] = value

    if "year_level" in cleaned:
        try:
            year = int(cleaned["year_level"])
        except ValueError:
            errors["year_level"] = "ต้องเป็นตัวเลข"
        else:
            if not MIN_YEAR_LEVEL <= year <= MAX_YEAR_LEVEL:
                errors["year_level"] = f"ต้องอยู่ระหว่าง {MIN_YEAR_LEVEL}-{MAX_YEAR_LEVEL}"
            else:
                cleaned["year_level"] = year

    # topic กับ class_date ไม่บังคับ แต่ถ้ากรอกมาต้องถูกรูปแบบ (AC ข้อ 2)
    topic = (form.get("topic") or "").strip()
    if topic:
        if len(topic) > MAX_LENGTHS["topic"]:
            errors["topic"] = f"ยาวเกิน {MAX_LENGTHS['topic']} ตัวอักษร"
        else:
            cleaned["topic"] = topic

    raw_date = (form.get("class_date") or "").strip()
    if raw_date:
        try:
            cleaned["class_date"] = date.fromisoformat(raw_date)
        except ValueError:
            errors["class_date"] = "ต้องเป็นรูปแบบ YYYY-MM-DD"

    description = (form.get("description") or "").strip()
    if description:
        cleaned["description"] = description

    uploader = (form.get("uploader_name") or "").strip()
    # ยังไม่มี auth (#5, #6) จึงรับชื่อจากฟอร์มไปก่อน — เมื่อมี session จริงให้ดึงจาก token แทน
    cleaned["uploader_name"] = uploader or "anonymous"

    return cleaned, errors


def validate_file(file_storage):
    """ตรวจไฟล์แนบ คืน (content_type, size_bytes, error)"""
    if file_storage is None or not file_storage.filename:
        return None, None, "ต้องแนบไฟล์โน้ต"

    content_type = (file_storage.mimetype or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        return None, None, f"รองรับเฉพาะ {allowed}"

    # หาขนาดไฟล์จาก stream โดยไม่อ่านทั้งก้อนเข้า memory
    stream = file_storage.stream
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)

    if size == 0:
        return None, None, "ไฟล์ว่าง"
    if size > MAX_FILE_BYTES:
        return None, None, f"ไฟล์ใหญ่เกิน {MAX_FILE_BYTES // (1024 * 1024)} MB"

    return content_type, size, None
