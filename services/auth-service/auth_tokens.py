"""ออกและตรวจ JWT access token — US-06 (#6)

JWT อย่างเดียวเพิกถอนไม่ได้ก่อนหมดอายุ แต่ AC ข้อ 2 ของ #6 ต้องการให้ logout แล้ว
token ใช้ไม่ได้ทันที ไฟล์นี้จึงตรวจแค่ลายเซ็นกับเวลา ส่วนการเช็คว่า session ยังไม่ถูก
เพิกถอนอยู่ใน app.py ที่เทียบ claim `jti` กับตาราง `auth_sessions` (ดู ADR-005)

ชื่อไฟล์ไม่ใช้ `tokens.py` เพราะชนกับ edit token ของ notes-service บน sys.path ของเทสต์
"""

import secrets
from datetime import datetime, timedelta

import jwt

# HS256 พอสำหรับตอนนี้ เพราะคนที่ออกและคนที่ตรวจลายเซ็นคือ auth-service ตัวเดียว
# ถ้าวันหนึ่ง API Gateway ต้องตรวจเองโดยไม่ถือ secret ค่อยเปลี่ยนเป็น RS256
ALGORITHM = "HS256"
ISSUER = "noteshare-auth"
DEFAULT_TTL = timedelta(hours=8)

# RFC 7518 §3.2: key ของ HS256 ต้องยาวอย่างน้อยเท่า output ของ hash (256 บิต = 32 ไบต์)
MIN_SECRET_BYTES = 32

REQUIRED_CLAIMS = ("sub", "jti", "iat", "exp", "iss")


def check_secret(secret: str | None) -> str:
    """ไม่ยอมเริ่ม service ถ้า secret ไม่ได้ตั้งหรือสั้นเกิน

    ตั้งใจไม่มีค่า default — ค่า default ที่ commit ไว้ในโค้ดคือ secret ที่ทุกคนรู้
    """
    if not secret:
        raise RuntimeError("ต้องตั้งค่า AUTH_JWT_SECRET ก่อนเริ่ม auth-service")
    if len(secret.encode("utf-8")) < MIN_SECRET_BYTES:
        raise RuntimeError(f"AUTH_JWT_SECRET ต้องยาวอย่างน้อย {MIN_SECRET_BYTES} ไบต์")
    return secret


def new_session_id() -> str:
    """ค่า `jti` สุ่ม 128 บิต ใช้เป็น primary key ของ auth_sessions ด้วย"""
    return secrets.token_hex(16)


def encode_access_token(
    secret: str, user_id: int, session_id: str, issued_at: datetime, ttl: timedelta
) -> tuple[str, datetime]:
    """คืน (token, เวลาหมดอายุ)"""
    expires_at = issued_at + ttl
    claims = {
        # PyJWT 2.10+ บังคับให้ `sub` เป็น string ตาม RFC 7519
        "sub": str(user_id),
        "jti": session_id,
        "iat": issued_at,
        "exp": expires_at,
        "iss": ISSUER,
    }
    return jwt.encode(claims, secret, algorithm=ALGORITHM), expires_at


def decode_access_token(secret: str, token: str | None) -> dict | None:
    """คืน claims ถ้า token ถูกต้องและยังไม่หมดอายุ ไม่งั้นคืน None

    ล็อก `algorithms` ไว้ที่ HS256 ตัวเดียว กัน token ที่ปลอม header เป็น `alg: none`
    หรือสลับไปใช้ algorithm อื่น — ไม่แยกเหตุผลที่ไม่ผ่านให้ผู้เรียก เพราะทุกกรณีตอบ 401 เหมือนกัน
    """
    if not token:
        return None
    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            options={"require": list(REQUIRED_CLAIMS)},
        )
    except jwt.InvalidTokenError:
        return None
