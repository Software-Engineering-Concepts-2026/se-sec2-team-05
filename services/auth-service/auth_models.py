"""Data model ของ User & Auth Service — US-05 (#5), US-06 (#6)

มีสองตาราง
- `users` บัญชีสมาชิก เก็บรหัสผ่านเป็น hash เท่านั้น (NFR-004)
- `auth_sessions` session ฝั่งเซิร์ฟเวอร์ 1 แถวต่อการ login 1 ครั้ง ผูกกับ `jti` ของ JWT
  มีไว้เพื่อให้ logout เพิกถอน token ได้ทันทีตาม AC ข้อ 2 ของ #6 (ดู ADR-005)

ชื่อไฟล์ไม่ใช้ `models.py` เพราะ conftest เติมทุก service เข้า sys.path พร้อมกัน
ถ้าชื่อซ้ำกับ `models.py` ของ notes-service ตัวไหนอยู่ต้น path ก็จะชนะ
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # เก็บเป็นตัวพิมพ์เล็กเสมอ (normalize ใน credentials.py) unique จึงกันซ้ำแบบไม่สนตัวพิมพ์ได้
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    # ชื่อที่ผู้ใช้ตั้งเอง ใช้แสดงเป็นเครดิตบนโน้ต (US-31 จะดึงค่านี้ไปใช้)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    # รูปแบบของ Werkzeug: "scrypt:<n>:<r>:<p>$<salt>$<hash>" ไม่มี plaintext ที่ไหนเลย
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    def to_dict(self):
        # ห้ามใส่ password_hash — endpoint ไหนก็ไม่ควรคืนค่านี้ออกไป
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    # = claim `jti` ของ JWT ที่ออกให้ตอน login
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    # ตรงกับ claim `exp` ของ JWT ซึ่งเป็นตัวตัดสินจริงตอนตรวจ token
    # เก็บไว้เพื่อให้ไล่ดู/ล้าง session ที่หมดอายุได้จากฐานข้อมูลโดยไม่ต้อง decode token
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # ว่างจนกว่าจะ logout — มีค่าเมื่อไหร่ token ของ session นี้ใช้ไม่ได้ทันที
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


def sqlalchemy_url(url: str) -> str:
    """ให้ URL แบบ `postgres://` / `postgresql://` (ที่ Neon บน Vercel ให้มา) ใช้ driver psycopg 3

    ถ้าไม่ระบุ driver SQLAlchemy จะหา psycopg2 ซึ่งไม่ได้ติดตั้ง (ADR-009)
    """
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def build_session_factory(database_url: str):
    """สร้าง engine + session factory และ create ตารางถ้ายังไม่มี

    ยังไม่มี migration tool เหมือน notes-service (ADR-003) — ตารางของ service นี้
    ชื่อไม่ชนกับ `notes` จึงอยู่ในฐานข้อมูล Postgres ก้อนเดียวกันได้
    """
    # pool_pre_ping: Neon ปิด connection ที่ว่างนาน ต้องเช็คก่อนหยิบจาก pool มาใช้
    engine = create_engine(sqlalchemy_url(database_url), future=True, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
