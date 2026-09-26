"""ตรวจข้อมูลสมัครสมาชิกและ hash รหัสผ่าน — US-05 (#5)

แยกออกมาจาก app.py เป็น pure function เหมือน validation.py ของ notes-service
ทดสอบเคสขอบได้โดยไม่ต้องมี request/DB
"""

from werkzeug.security import check_password_hash, generate_password_hash

DEFAULT_ALLOWED_DOMAINS = "up.ac.th"

MAX_EMAIL_LENGTH = 254  # เพดานความยาวอีเมลตาม RFC 5321
MIN_PASSWORD_LENGTH = 8
# scrypt ไม่มีเพดาน 72 ไบต์แบบ bcrypt แต่ยังจำกัดไว้ ไม่ให้ใครส่งรหัสผ่านยาวเป็นเมกะไบต์มาให้ hash
MAX_PASSWORD_LENGTH = 128
MIN_DISPLAY_NAME_LENGTH = 1
MAX_DISPLAY_NAME_LENGTH = 120

# scrypt ที่ N=2^17, r=8, p=1 = ค่าขั้นต่ำของ OWASP Password Storage Cheat Sheet
# ต้องระบุเอง เพราะค่า default ของ Werkzeug คือ N=2^15 ซึ่งต่ำกว่านั้น
# เหตุผลที่ใช้แทน bcrypt ตาม NFR-004 อยู่ใน ADR-005
PASSWORD_HASH_METHOD = "scrypt:131072:8:1"


def parse_allowed_domains(raw: str | None) -> tuple[str, ...]:
    """แปลงค่า `ALLOWED_EMAIL_DOMAINS` (คั่นด้วย comma) เป็น tuple ของโดเมนตัวพิมพ์เล็ก

    ยอมให้ใส่ `@` นำหน้ามาได้ (`@up.ac.th`) เพราะคนตั้ง env มักพิมพ์แบบนั้น
    ถ้าไม่ได้ตั้งหรือตั้งเป็นค่าว่างจะใช้ค่า default แทน ไม่ปล่อยให้เป็นลิสต์ว่าง
    ซึ่งจะทำให้ไม่มีใครสมัครได้เลยแบบเงียบ ๆ
    """
    domains = tuple(
        part.strip().lstrip("@").lower()
        for part in (raw or "").split(",")
        if part.strip().lstrip("@")
    )
    return domains or (DEFAULT_ALLOWED_DOMAINS,)


def normalize_email(raw) -> str:
    if not isinstance(raw, str):
        return ""
    return raw.strip().lower()


def email_error(email: str, allowed_domains: tuple[str, ...]) -> str | None:
    """คืนเหตุผลที่อีเมลใช้ไม่ได้ หรือ None ถ้าใช้ได้ — รับค่าที่ normalize แล้ว

    โดเมนต้องตรงตัวกับที่อนุญาต ไม่นับ subdomain — `x@mail.up.ac.th` และ
    `x@up.ac.th.example.com` ไม่ผ่าน เพราะ AC ข้อแรกของ #5 ระบุโดเมนมหาวิทยาลัยเท่านั้น
    """
    if not email:
        return "จำเป็นต้องกรอก"
    if len(email) > MAX_EMAIL_LENGTH:
        return f"ยาวเกิน {MAX_EMAIL_LENGTH} ตัวอักษร"
    local, sep, domain = email.rpartition("@")
    if not sep or not local or "@" in local or any(ch.isspace() for ch in email):
        return "รูปแบบอีเมลไม่ถูกต้อง"
    if domain not in allowed_domains:
        return "ต้องใช้อีเมลของมหาวิทยาลัย (" + ", ".join(f"@{d}" for d in allowed_domains) + ")"
    return None


def password_error(password) -> str | None:
    # ไม่ strip รหัสผ่าน — ช่องว่างเป็นส่วนหนึ่งของรหัสผ่านได้
    if not isinstance(password, str) or password == "":
        return "จำเป็นต้องกรอก"
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"ต้องมีอย่างน้อย {MIN_PASSWORD_LENGTH} ตัวอักษร"
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"ยาวเกิน {MAX_PASSWORD_LENGTH} ตัวอักษร"
    return None


def validate_registration(data, allowed_domains: tuple[str, ...]):
    """ตรวจข้อมูลสมัครสมาชิก คืน (cleaned, errors) รูปแบบเดียวกับ validate_metadata

    เก็บ error ให้ครบทุกฟิลด์ก่อนค่อยคืน ผู้ใช้จะได้แก้ทีเดียวจบ (AC ข้อ 4 ของ #5)
    """
    cleaned, errors = {}, {}

    email = normalize_email(data.get("email"))
    reason = email_error(email, allowed_domains)
    if reason:
        errors["email"] = reason
    else:
        cleaned["email"] = email

    password = data.get("password")
    reason = password_error(password)
    if reason:
        errors["password"] = reason
    else:
        cleaned["password"] = password

    raw_name = data.get("display_name")
    display_name = raw_name.strip() if isinstance(raw_name, str) else ""
    if len(display_name) < MIN_DISPLAY_NAME_LENGTH:
        errors["display_name"] = "จำเป็นต้องกรอก"
    elif len(display_name) > MAX_DISPLAY_NAME_LENGTH:
        errors["display_name"] = f"ยาวเกิน {MAX_DISPLAY_NAME_LENGTH} ตัวอักษร"
    else:
        cleaned["display_name"] = display_name

    return cleaned, errors


def hash_password(password: str, method: str = PASSWORD_HASH_METHOD) -> str:
    """hash รหัสผ่านด้วย scrypt + salt สุ่มต่อบัญชี (Werkzeug สร้าง salt 16 ตัวอักษรให้เอง)"""
    return generate_password_hash(password, method=method)


def verify_password(stored_hash: str, password: str) -> bool:
    """เทียบรหัสผ่านกับ hash แบบ constant-time — ค่า cost อ่านจากตัว hash เอง"""
    return check_password_hash(stored_hash, password)
