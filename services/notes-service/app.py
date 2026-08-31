"""Notes Service — US-08 (#8) ระบุ metadata ของโน้ต

Endpoint:
    GET  /health              health check (รูปแบบเดียวกับ stats-service)
    POST /notes               อัปโหลดไฟล์ + metadata (multipart/form-data)
    GET  /notes               ค้นหา/กรองด้วย metadata ที่กรอกไว้ (AC ข้อ 4)
    GET  /notes/<id>          รายละเอียดโน้ตหนึ่งรายการ
    GET  /notes/<id>/download ดาวน์โหลดไฟล์จริง

ยังไม่มี auth — ทุก endpoint เปิดหมด จนกว่า #5/#6 (User & Auth) จะเสร็จ
"""

import os
from datetime import date, datetime, timezone

from flask import Flask, jsonify, request, send_file
from sqlalchemy import select

from models import Note, build_session_factory
from storage import storage_from_env
from validation import validate_file, validate_metadata

DEFAULT_DATABASE_URL = "sqlite:///notes.db"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# เรียงผลลัพธ์ได้เท่าที่กำหนดไว้เท่านั้น ไม่ให้ client ส่งชื่อคอลัมน์อะไรมาก็ได้
SORT_COLUMNS = {
    "new": Note.created_at.desc(),
    "old": Note.created_at.asc(),
    "class_date": Note.class_date.desc(),
    "title": Note.title.asc(),
}


def create_app(database_url: str | None = None, storage=None) -> Flask:
    app = Flask(__name__)
    session_factory = build_session_factory(
        database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    )
    file_storage = storage or storage_from_env()

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            service="notes-service",
            time=datetime.now(timezone.utc).isoformat(),
        )

    @app.post("/notes")
    def create_note():
        cleaned, errors = validate_metadata(request.form)
        content_type, size_bytes, file_error = validate_file(request.files.get("file"))
        if file_error:
            errors["file"] = file_error

        if errors:
            return jsonify(error="validation_failed", fields=errors), 400

        upload = request.files["file"]
        storage_key = file_storage.build_key(content_type)
        file_storage.save(storage_key, upload)

        note = Note(
            **cleaned,
            file_name=upload.filename,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_key=storage_key,
        )
        with session_factory() as session:
            session.add(note)
            try:
                session.commit()
            except Exception:
                # ถ้า commit ไม่ผ่าน อย่าทิ้งไฟล์กำพร้าไว้ใน storage
                session.rollback()
                file_storage.delete(storage_key)
                raise
            return jsonify(note.to_dict()), 201

    @app.get("/notes")
    def list_notes():
        """ค้นหา/กรองจาก metadata — AC ข้อ 4 ของ #8 และเป็นฐานให้ #10, #26"""
        args = request.args
        stmt = select(Note)

        keyword = (args.get("q") or "").strip()
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                Note.title.ilike(like)
                | Note.subject_name.ilike(like)
                | Note.subject_code.ilike(like)
                | Note.lesson.ilike(like)
                | Note.topic.ilike(like)
            )

        for field, column in (
            ("faculty", Note.faculty),
            ("subject_code", Note.subject_code),
        ):
            value = (args.get(field) or "").strip()
            if value:
                stmt = stmt.where(column == value)

        if args.get("year_level"):
            try:
                stmt = stmt.where(Note.year_level == int(args["year_level"]))
            except ValueError:
                return jsonify(error="invalid_filter", field="year_level"), 400

        for field, condition in (
            ("date_from", lambda d: Note.class_date >= d),
            ("date_to", lambda d: Note.class_date <= d),
        ):
            if args.get(field):
                try:
                    stmt = stmt.where(condition(date.fromisoformat(args[field])))
                except ValueError:
                    return jsonify(error="invalid_filter", field=field), 400

        sort = args.get("sort", "new")
        if sort not in SORT_COLUMNS:
            return jsonify(error="invalid_filter", field="sort"), 400
        stmt = stmt.order_by(SORT_COLUMNS[sort])

        try:
            limit = min(int(args.get("limit", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE)
            offset = int(args.get("offset", 0))
        except ValueError:
            return jsonify(error="invalid_filter", field="limit/offset"), 400

        with session_factory() as session:
            rows = session.scalars(stmt.limit(limit).offset(offset)).all()
            return jsonify(items=[n.to_dict() for n in rows], count=len(rows))

    @app.get("/notes/<int:note_id>")
    def get_note(note_id):
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404
            return jsonify(note.to_dict())

    @app.get("/notes/<int:note_id>/download")
    def download_note(note_id):
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404
            return send_file(
                file_storage.open(note.storage_key),
                mimetype=note.content_type,
                as_attachment=True,
                download_name=note.file_name,
            )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
