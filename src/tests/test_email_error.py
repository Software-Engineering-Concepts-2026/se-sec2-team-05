"""Unit tests ของ email_error() โดยตรง — Lab 12B (Safety Net Sprint), US-05 (#5)

test_auth_credentials.py ทดสอบอีเมลผ่าน validate_registration() ซึ่ง normalize ให้ก่อนเสมอ
ไฟล์นี้เรียก email_error() ตรง ๆ เพื่อตรึงสัญญาของฟังก์ชันเอง: รับค่าที่ normalize แล้ว,
ขอบความยาว 254 ทั้งสองฝั่ง และข้อความ error เมื่ออนุญาตหลายโดเมน
"""

from credentials import MAX_EMAIL_LENGTH, email_error

UP = ("up.ac.th",)
UP_AND_ICT = ("up.ac.th", "ict.up.ac.th")


def email_of_length(length, domain="up.ac.th"):
    suffix = f"@{domain}"
    return "a" * (length - len(suffix)) + suffix


# ── HAPPY PATH ──


def test_university_email_is_accepted():
    """อีเมล @up.ac.th ปกติต้องผ่าน (คืน None)"""
    # Arrange
    email = "67026168@up.ac.th"

    # Act
    result = email_error(email, UP)

    # Assert
    assert result is None


def test_second_allowed_domain_is_accepted():
    """ถ้าตั้งให้รับ 2 โดเมน อีเมลของโดเมนที่สองต้องผ่านด้วย"""
    # Arrange
    email = "x@ict.up.ac.th"

    # Act
    result = email_error(email, UP_AND_ICT)

    # Assert
    assert result is None


# ── EDGE CASE ──


def test_email_at_exact_max_length_is_accepted():
    """ยาว 254 ตัวพอดีต้องผ่าน — จุดขอบฝั่งที่ต้องผ่าน (กัน off-by-one แบบ > กับ >=)"""
    # Arrange
    email = email_of_length(MAX_EMAIL_LENGTH)
    assert len(email) == 254

    # Act
    result = email_error(email, UP)

    # Assert
    assert result is None


def test_email_one_over_max_length_is_rejected():
    """ยาว 255 ตัวต้องไม่ผ่าน — จุดขอบฝั่งที่ต้องตก"""
    # Arrange
    email = email_of_length(MAX_EMAIL_LENGTH + 1)

    # Act
    result = email_error(email, UP)

    # Assert
    assert result == "ยาวเกิน 254 ตัวอักษร"


def test_uppercase_domain_is_rejected_because_caller_must_normalize():
    """email_error() ไม่ normalize เอง — ตัวพิมพ์ใหญ่ที่ยังไม่แปลงต้องไม่ผ่าน"""
    # Arrange
    email = "A@UP.AC.TH"

    # Act
    result = email_error(email, UP)

    # Assert
    assert result == "ต้องใช้อีเมลของมหาวิทยาลัย (@up.ac.th)"


# ── ERROR CASE ──


def test_empty_email_is_required():
    """ค่าว่างต้องได้ error ว่าจำเป็นต้องกรอก ไม่ใช่ error รูปแบบ"""
    # Arrange
    email = ""

    # Act
    result = email_error(email, UP)

    # Assert
    assert result == "จำเป็นต้องกรอก"


def test_tab_inside_email_is_malformed():
    """whitespace ทุกชนิด (ไม่ใช่แค่ช่องว่าง) ต้องถือว่ารูปแบบผิด"""
    # Arrange
    email = "a\t@up.ac.th"

    # Act
    result = email_error(email, UP)

    # Assert
    assert result == "รูปแบบอีเมลไม่ถูกต้อง"


def test_rejection_message_lists_every_allowed_domain():
    """เมื่อรับหลายโดเมน ข้อความ error ต้องบอกครบทุกโดเมนให้ผู้ใช้รู้ว่าใช้อะไรได้"""
    # Arrange
    email = "x@gmail.com"

    # Act
    result = email_error(email, UP_AND_ICT)

    # Assert
    assert result == "ต้องใช้อีเมลของมหาวิทยาลัย (@up.ac.th, @ict.up.ac.th)"
