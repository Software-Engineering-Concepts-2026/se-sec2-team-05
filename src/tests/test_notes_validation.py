"""Unit tests ของ validation ฝั่ง Notes Service — US-08 (#8) AC ข้อ 2 และ 3

เป็น pure function ล้วน ไม่ต้องมี Flask/DB จึงทดสอบเคสขอบได้เยอะโดยไม่ช้า
"""

import io
from datetime import date

import pytest
from werkzeug.datastructures import FileStorage

from validation import MAX_FILE_BYTES, validate_file, validate_metadata

VALID_FORM = {
    "title": "สรุปบทที่ 3 โครงสร้างข้อมูล",
    "subject_name": "Data Structures",
    "subject_code": "CS201",
    "faculty": "ICT",
    "year_level": "2",
    "lesson": "บทที่ 3 — Linked List",
}


def test_valid_form_passes_and_casts_year_level():
    cleaned, errors = validate_metadata(VALID_FORM)

    assert errors == {}
    assert cleaned["year_level"] == 2  # cast เป็น int แล้ว ไม่ใช่ "2"
    assert cleaned["uploader_name"] == "anonymous"  # ยังไม่มี auth (#5, #6)


def test_missing_required_fields_are_all_reported_at_once():
    cleaned, errors = validate_metadata({"title": "x"})

    # ต้องรายงานครบทุกฟิลด์ที่ขาด ไม่ใช่หยุดที่ตัวแรก ผู้ใช้จะได้แก้ทีเดียวจบ
    assert set(errors) == {"subject_name", "subject_code", "faculty", "year_level", "lesson"}
    assert "title" not in errors


def test_whitespace_only_value_counts_as_missing():
    _, errors = validate_metadata({**VALID_FORM, "subject_code": "   "})

    assert errors["subject_code"] == "จำเป็นต้องกรอก"


@pytest.mark.parametrize("bad_year", ["0", "9", "-1", "สอง"])
def test_year_level_out_of_range_or_not_a_number_is_rejected(bad_year):
    _, errors = validate_metadata({**VALID_FORM, "year_level": bad_year})

    assert "year_level" in errors


def test_optional_class_date_is_parsed_when_valid():
    cleaned, errors = validate_metadata({**VALID_FORM, "class_date": "2026-08-20"})

    assert errors == {}
    assert cleaned["class_date"] == date(2026, 8, 20)


def test_malformed_class_date_is_rejected():
    _, errors = validate_metadata({**VALID_FORM, "class_date": "20/08/2026"})

    assert errors["class_date"] == "ต้องเป็นรูปแบบ YYYY-MM-DD"


def test_omitted_optional_fields_are_not_errors():
    cleaned, errors = validate_metadata(VALID_FORM)

    assert errors == {}
    assert "class_date" not in cleaned
    assert "topic" not in cleaned


def test_overlong_field_is_rejected():
    _, errors = validate_metadata({**VALID_FORM, "title": "ก" * 201})

    assert "ยาวเกิน" in errors["title"]


def _file(content=b"%PDF-1.4 fake", name="note.pdf", mimetype="application/pdf"):
    return FileStorage(stream=io.BytesIO(content), filename=name, content_type=mimetype)


def test_pdf_upload_is_accepted():
    content_type, size, error = validate_file(_file())

    assert error is None
    assert content_type == "application/pdf"
    assert size == len(b"%PDF-1.4 fake")


def test_missing_file_is_rejected():
    assert validate_file(None)[2] == "ต้องแนบไฟล์โน้ต"


def test_disallowed_content_type_is_rejected():
    _, _, error = validate_file(_file(name="note.exe", mimetype="application/x-msdownload"))

    assert "รองรับเฉพาะ" in error


def test_empty_file_is_rejected():
    assert validate_file(_file(content=b""))[2] == "ไฟล์ว่าง"


def test_oversized_file_is_rejected():
    _, _, error = validate_file(_file(content=b"x" * (MAX_FILE_BYTES + 1)))

    assert "ใหญ่เกิน" in error


def test_validate_file_rewinds_stream_so_the_file_can_still_be_saved():
    upload = _file()

    validate_file(upload)

    # ถ้าลืม seek(0) กลับ ไฟล์ที่เซฟลง storage จะกลายเป็นไฟล์ว่าง
    assert upload.stream.read() == b"%PDF-1.4 fake"
