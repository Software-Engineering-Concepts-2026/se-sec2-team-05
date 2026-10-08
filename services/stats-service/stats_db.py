import os
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uploader_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    uploader_name: Mapped[str] = mapped_column(String(120), nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Thank(Base):
    """ตาราง `thanks` ของ notes-service (US-28 #28) — stats-service อ่านอย่างเดียว

    notes-service เป็นเจ้าของตารางและเป็นคนสร้าง คอลัมน์ที่นี่ต้องตรงกับ `Thank`
    ใน services/notes-service/models.py เพราะเทสต์อาจสร้างตารางจากฝั่งนี้ก่อน
    """

    __tablename__ = "thanks"
    __table_args__ = (UniqueConstraint("user_id", "note_id", name="uq_thanks_user_note"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    note_id: Mapped[int] = mapped_column(Integer, ForeignKey("notes.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


def sqlalchemy_url(url: str) -> str:
    """ให้ URL แบบ `postgres://` / `postgresql://` (ที่ Neon บน Vercel ให้มา) ใช้ driver psycopg 3

    ถ้าไม่ระบุ driver SQLAlchemy จะหา psycopg2 ซึ่งไม่ได้ติดตั้ง (ADR-009)
    """
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def build_session_factory(database_url: str | None = None):
    url = database_url or os.getenv(
        "DATABASE_URL",
        "sqlite:///stats.db",
    )

    # pool_pre_ping: Neon ปิด connection ที่ว่างนาน ต้องเช็คก่อนหยิบจาก pool มาใช้
    engine = create_engine(sqlalchemy_url(url), pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)