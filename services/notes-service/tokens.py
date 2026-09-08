"""Edit token ของโน้ต — กลไกชั่วคราวระหว่างที่ยังไม่มี User & Auth Service (#5, #6)

US-19 (#19) และ US-20 (#20) ระบุว่า "เจ้าของเท่านั้น" ที่แก้หรือลบโน้ตได้ แต่ตอนนี้ระบบ
ยังไม่มี identity ที่เชื่อถือได้เลย — `uploader_name` มาจากฟอร์มและแสดงอยู่บนโน้ตทุกใบ
ใครก็พิมพ์ตามได้ ถ้าเอามาใช้ตรวจสิทธิ์เท่ากับไม่ได้ตรวจอะไรเลย

จึงออก token สุ่มให้ตอนสร้างโน้ต คืนให้ผู้สร้างครั้งเดียว และเก็บแค่ hash ไว้ในฐานข้อมูล
รายละเอียดและข้อจำกัดอยู่ใน ADR-004

นี่ไม่ใช่ระบบ authentication — ไม่มี identity, ไม่มี session, ไม่มีการเพิกถอน token
เมื่อ #5/#6 เสร็จให้ลบไฟล์นี้และเปลี่ยนไปตรวจ `note.owner_id` แทน
"""

import hashlib
import secrets

# 32 ไบต์จาก secrets ให้ entropy 256 บิต เดาไม่ได้ในทางปฏิบัติ
TOKEN_BYTES = 32

HEADER_NAME = "X-Note-Token"


def issue_token() -> tuple[str, str]:
    """สุ่ม token ใหม่ คืน (token ตัวจริง, hash ที่เอาไปเก็บ)"""
    token = secrets.token_urlsafe(TOKEN_BYTES)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    """hash ด้วย SHA-256 เฉย ๆ ไม่ต้อง bcrypt/argon2

    token เป็นค่าสุ่ม 256 บิตที่เครื่องสร้างเอง ไม่ใช่รหัสผ่านที่คนตั้ง จึงไม่มีอะไรให้
    brute-force หรือเทียบกับ rainbow table — key stretching ไม่ได้เพิ่มความปลอดภัยตรงนี้
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def token_matches(token: str | None, stored_hash: str | None) -> bool:
    """เทียบ token กับ hash ที่เก็บไว้ แบบ constant-time"""
    if not token or not stored_hash:
        return False
    return secrets.compare_digest(hash_token(token), stored_hash)
