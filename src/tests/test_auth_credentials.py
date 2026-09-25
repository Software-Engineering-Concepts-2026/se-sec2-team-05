"""Unit tests ของการตรวจข้อมูลสมัครสมาชิกและ hash รหัสผ่าน — US-05 (#5)

เป็น pure function ล้วน ไม่ต้องมี Flask/DB เคสขอบทั้งหมดของความยาวจึงอยู่ในไฟล์นี้
"""

import pytest

from credentials import (
    MAX_DISPLAY_NAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    PASSWORD_HASH_METHOD,
    hash_password,
    parse_allowed_domains,
    validate_registration,
    verify_password,
)

UP = ("up.ac.th",)

VALID = {
    "email": "67026168@up.ac.th",
    "password": "correct horse",
    "display_name": "อติชาติ",
}


def register(**overrides):
    return validate_registration({**VALID, **overrides}, UP)


def test_valid_registration_passes_and_is_cleaned():
    cleaned, errors = register(email="  67026168@UP.AC.TH ", display_name="  อติชาติ  ")

    assert errors == {}
    # อีเมลเก็บเป็นตัวพิมพ์เล็ก การกันอีเมลซ้ำจึงไม่หลุดเพราะพิมพ์ตัวใหญ่
    assert cleaned["email"] == "67026168@up.ac.th"
    assert cleaned["display_name"] == "อติชาติ"
    assert cleaned["password"] == "correct horse"


def test_missing_fields_are_all_reported_at_once():
    cleaned, errors = validate_registration({}, UP)

    assert set(errors) == {"email", "password", "display_name"}
    assert cleaned == {}


@pytest.mark.parametrize(
    "email",
    [
        "someone@gmail.com",
        "someone@mail.up.ac.th",  # subdomain ไม่นับ
        "someone@up.ac.th.example.com",  # ต่อท้ายหลอกให้ดูเหมือนโดเมนมหาวิทยาลัย
        "someone@notup.ac.th",
    ],
)
def test_email_outside_university_domain_is_rejected(email):
    _, errors = register(email=email)

    assert "ต้องใช้อีเมลของมหาวิทยาลัย" in errors["email"]


@pytest.mark.parametrize(
    "email",
    ["no-at-sign.up.ac.th", "@up.ac.th", "a@b@up.ac.th", "a b@up.ac.th"],
)
def test_malformed_email_is_rejected(email):
    _, errors = register(email=email)

    assert errors["email"] == "รูปแบบอีเมลไม่ถูกต้อง"


def test_email_longer_than_rfc_limit_is_rejected():
    long_local = "a" * (254 - len("@up.ac.th") + 1)

    _, errors = register(email=f"{long_local}@up.ac.th")

    assert errors["email"] == "ยาวเกิน 254 ตัวอักษร"


@pytest.mark.parametrize(
    ("length", "ok"),
    [
        (MIN_PASSWORD_LENGTH - 1, False),
        (MIN_PASSWORD_LENGTH, True),
        (MAX_PASSWORD_LENGTH, True),
        (MAX_PASSWORD_LENGTH + 1, False),
    ],
)
def test_password_length_boundaries(length, ok):
    _, errors = register(password="x" * length)

    assert ("password" not in errors) is ok


def test_password_is_not_stripped():
    # ช่องว่างนับเป็นตัวอักษรของรหัสผ่าน — ถ้า strip ทิ้ง รหัส 8 ตัวที่มีช่องว่างจะกลายเป็นสั้นเกิน
    cleaned, errors = register(password="  pass  ")

    assert errors == {}
    assert cleaned["password"] == "  pass  "


@pytest.mark.parametrize(
    ("name", "ok"),
    [
        ("", False),
        ("   ", False),  # มีแต่ช่องว่างนับเป็นไม่กรอก
        ("ก", True),
        ("ก" * MAX_DISPLAY_NAME_LENGTH, True),
        ("ก" * (MAX_DISPLAY_NAME_LENGTH + 1), False),
    ],
)
def test_display_name_length_boundaries(name, ok):
    _, errors = register(display_name=name)

    assert ("display_name" not in errors) is ok


def test_non_string_values_are_rejected_not_crashed():
    # JSON ส่งตัวเลขหรือ list มาได้ ต้องได้ error ไม่ใช่ AttributeError ตอน .strip()
    _, errors = validate_registration({"email": 123, "password": 12345678, "display_name": []}, UP)

    assert set(errors) == {"email", "password", "display_name"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, ("up.ac.th",)),
        ("", ("up.ac.th",)),  # ตั้งเป็นค่าว่างต้องไม่กลายเป็น "ไม่มีโดเมนไหนสมัครได้เลย"
        ("UP.AC.TH", ("up.ac.th",)),
        ("@up.ac.th, cmu.ac.th ,", ("up.ac.th", "cmu.ac.th")),
    ],
)
def test_parse_allowed_domains(raw, expected):
    assert parse_allowed_domains(raw) == expected


def test_second_allowed_domain_is_accepted():
    _, errors = validate_registration(
        {**VALID, "email": "someone@cmu.ac.th"}, parse_allowed_domains("up.ac.th,cmu.ac.th")
    )

    assert errors == {}


def test_password_hash_uses_owasp_minimum_scrypt_cost_and_no_plaintext():
    stored = hash_password("correct horse")

    # NFR-004: ห้ามเก็บ plaintext · ADR-005: scrypt N=2^17, r=8, p=1
    assert "correct horse" not in stored
    assert stored.startswith(PASSWORD_HASH_METHOD + "$")
    assert PASSWORD_HASH_METHOD == "scrypt:131072:8:1"
    assert verify_password(stored, "correct horse")
    assert not verify_password(stored, "wrong horse")


def test_same_password_hashes_differently_because_of_salt():
    # cost ต่ำเพื่อความเร็ว — เทสต์นี้ดูแค่ salt ส่วน cost จริงตรวจในเทสต์ข้างบนแล้ว
    first = hash_password("correct horse", method="scrypt:1024:8:1")
    second = hash_password("correct horse", method="scrypt:1024:8:1")

    assert first != second
    assert verify_password(first, "correct horse")
    assert verify_password(second, "correct horse")
