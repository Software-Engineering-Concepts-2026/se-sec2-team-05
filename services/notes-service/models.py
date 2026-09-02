"""Data model ของ Notes Service

ตาราง `notes` เก็บ metadata ตาม US-08 (#8) — ชื่อวิชา รหัสวิชา คณะ ชั้นปี บทเรียน
หัวข้อ และวันที่ของคาบเรียน — ทุกคอลัมน์ที่ใช้กรองมี index เพราะ AC ข้อสุดท้าย
ระบุว่าข้อมูลที่กรอกต้องนำไปใช้เป็นเงื่อนไขค้นหา/กรองได้จริง

ตัวไฟล์โน้ตไม่ได้เก็บใน DB (ดูเหตุผลใน docs/architecture/tech_stack.md แถว File
storage) — เก็บแค่ `storage_key` ที่ชี้ไปยังไฟล์ใน object storage
"""

from datetime import date as date_type, datetime, timezone

from sqlalchemy import Date, DateTime, Integer, String, Text, create_engine, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # --- metadata ที่ผู้แบ่งปันกรอก (US-08) ---
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_code: Mapped[str] = mapped_column(String(30), nullable=False)
    faculty: Mapped[str] = mapped_column(String(100), nullable=False)
    year_level: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson: Mapped[str] = mapped_column(String(200), nullable=False)
    topic: Mapped[str | None] = mapped_column(String(200))
    class_date: Mapped[date_type | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)

    # --- ไฟล์ ---
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # เจ้าของโน้ต — ยังเป็น string ไปก่อนจนกว่า User & Auth service จะมีจริง (#5, #6)
    uploader_name: Mapped[str] = mapped_column(String(120), nullable=False, default="anonymous")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subject_name": self.subject_name,
            "subject_code": self.subject_code,
            "faculty": self.faculty,
            "year_level": self.year_level,
            "lesson": self.lesson,
            "topic": self.topic,
            "class_date": self.class_date.isoformat() if self.class_date else None,
            "description": self.description,
            "file_name": self.file_name,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "uploader_name": self.uploader_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "download_url": f"/notes/{self.id}/download",
        }


# index สำหรับเงื่อนไขกรองที่ใช้บ่อยตาม #10, #26
Index("ix_notes_subject_code", Note.subject_code)
Index("ix_notes_faculty_year", Note.faculty, Note.year_level)
Index("ix_notes_class_date", Note.class_date)


def build_session_factory(database_url: str):
    """สร้าง engine + session factory และ create ตารางถ้ายังไม่มี

    ยังไม่ใช้ migration tool (Alembic) ในรอบ tracer bullet นี้ — schema ยังเปลี่ยนบ่อย
    และยังไม่มีข้อมูลจริงที่ต้องรักษา ถ้า schema เริ่มนิ่งค่อยเพิ่มทีหลัง
    """
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
