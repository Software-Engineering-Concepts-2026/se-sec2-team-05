import os

from sqlalchemy import Integer, String, create_engine
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


def build_session_factory(database_url: str | None = None):
    url = database_url or os.getenv(
        "DATABASE_URL",
        "sqlite:///stats.db",
    )

    engine = create_engine(url)
    return sessionmaker(bind=engine, expire_on_commit=False)