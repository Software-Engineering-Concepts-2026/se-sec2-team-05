"""Notes Service — US-08 (#8) ระบุ metadata ของโน้ต

Endpoint:
    GET  /health              health check (รูปแบบเดียวกับ stats-service)
    POST /notes               อัปโหลดไฟล์ + metadata (multipart/form-data) ต้อง login (US-31)
    GET  /notes               ค้นหา/กรองด้วย metadata ที่กรอกไว้ (AC ข้อ 4)
    GET  /notes/<id>          รายละเอียดโน้ตหนึ่งรายการ
    PATCH  /notes/<id>        แก้ metadata บางส่วน (US-19) ต้องมี X-Note-Token
    DELETE /notes/<id>        ลบโน้ตพร้อมไฟล์ (US-20) ต้องมี X-Note-Token
    GET  /notes/<id>/download ดาวน์โหลดไฟล์จริง

การอัปโหลดต้องส่ง `Authorization: Bearer <token>` ที่ได้จาก auth-service ชื่อผู้อัปโหลด
มาจากบัญชีนั้น ไม่รับจากฟอร์ม (ดู identity.py) — endpoint ที่อ่านอย่างเดียวยังเปิดหมด
ส่วนการแก้/ลบยังใช้ edit token ต่อโน้ตเหมือนเดิม (ดู ADR-004 และ tokens.py)
"""

import os
from datetime import date, datetime, timezone

from flask import Flask, jsonify, request, send_file
from sqlalchemy import select, update

from identity import IdentityUnavailable, identity_from_env
from models import Note, build_session_factory
from storage import storage_from_env
from tokens import HEADER_NAME, issue_token, token_matches
from validation import ALLOWED_CONTENT_TYPES, MAX_FILE_BYTES, validate_file, validate_metadata

DEFAULT_DATABASE_URL = "sqlite:///notes.db"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# เพดานขนาด request ทั้งก้อน = ขนาดไฟล์สูงสุด + ที่เผื่อไว้ให้ multipart boundary กับฟิลด์ metadata
# ตั้งให้สูงกว่า MAX_FILE_BYTES เล็กน้อยโดยตั้งใจ ไฟล์ที่เกินนิดเดียวจะได้ตกที่ validate_file
# ซึ่งบอกเหตุผลรายฟิลด์ แทนที่จะถูกตัดทิ้งแบบไม่มีรายละเอียดตั้งแต่ชั้น Werkzeug
REQUEST_OVERHEAD_BYTES = 1024 * 1024
MAX_REQUEST_BYTES = MAX_FILE_BYTES + REQUEST_OVERHEAD_BYTES

# เรียงผลลัพธ์ได้เท่าที่กำหนดไว้เท่านั้น ไม่ให้ client ส่งชื่อคอลัมน์อะไรมาก็ได้
SORT_COLUMNS = {
    "new": Note.created_at.desc(),
    "old": Note.created_at.asc(),
    "class_date": Note.class_date.desc(),
    "title": Note.title.asc(),
}

# รับค่าจาก client เป็นนามสกุลไฟล์สั้นๆ (pdf, png, jpg) แทน MIME type เต็ม
# เพื่อให้ frontend ส่งค่าที่คนอ่านง่ายกว่า "application/pdf"
# สร้าง reverse map จาก ALLOWED_CONTENT_TYPES เดิมใน validation.py ไม่ต้อง hardcode ซ้ำ
EXT_TO_CONTENT_TYPE = {
    ext.lstrip("."): content_type
    for content_type, ext in ALLOWED_CONTENT_TYPES.items()
}


def create_app(database_url: str | None = None, storage=None, identity=None) -> Flask:
    app = Flask(__name__)
    # ตัดคำขอที่ใหญ่เกินตั้งแต่ชั้น Werkzeug ไม่ต้องรอให้ validate_file เห็นขนาด
    # เพราะกว่าจะถึงตรงนั้น request body ถูกอ่านเข้ามาครบแล้ว
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES
    session_factory = build_session_factory(
        database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    )
    file_storage = storage or storage_from_env()
    current_user = identity or identity_from_env()

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            service="notes-service",
            time=datetime.now(timezone.utc).isoformat(),
        )

    @app.errorhandler(413)
    def too_large(_error):
        """ให้ 413 ตอบเป็น JSON รูปแบบเดียวกับ validation error ตัวอื่น

        ถ้าไม่ดักไว้ Werkzeug จะคืนหน้า HTML ซึ่ง client ที่ parse JSON อยู่แล้วจะพัง
        """
        limit_mb = MAX_FILE_BYTES // (1024 * 1024)
        return (
            jsonify(
                error="validation_failed",
                fields={"file": f"ไฟล์ใหญ่เกิน {limit_mb} MB"},
            ),
            413,
        )

    @app.post("/notes")
    def create_note():
        # ตรวจตัวตนก่อนแตะ body — ถ้าไม่ผ่านจะไม่มีการอ่านไฟล์หรือบันทึกอะไรลง storage เลย
        try:
            user = current_user(request.headers.get("Authorization"))
        except IdentityUnavailable:
            return jsonify(error="auth_unavailable"), 503
        if user is None:
            return jsonify(error="unauthorized"), 401, {"WWW-Authenticate": "Bearer"}

        cleaned, errors = validate_metadata(request.form)
        content_type, size_bytes, file_error = validate_file(request.files.get("file"))
        if file_error:
            errors["file"] = file_error

        if errors:
            return jsonify(error="validation_failed", fields=errors), 400

        upload = request.files["file"]
        storage_key = file_storage.build_key(content_type)
        file_storage.save(storage_key, upload)

        token, token_hash = issue_token()
        note = Note(
            **cleaned,
            # US-31: เจ้าของโน้ตมาจากบัญชีที่ login เสมอ uploader_name ในฟอร์ม (ถ้ามี) ถูกเมิน
            uploader_id=user["id"],
            uploader_name=user["display_name"],
            file_name=upload.filename,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_key=storage_key,
            edit_token_hash=token_hash,
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
            # ครั้งเดียวที่ token ตัวจริงออกจาก service — ในฐานข้อมูลมีแค่ hash
            return jsonify(**note.to_dict(), edit_token=token), 201

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

        # US-10: กรองตามประเภทไฟล์ — รับหลายค่าพร้อมกันได้ (OR ภายในตัวกรองนี้)
        file_types = args.getlist("file_type")
        if file_types:
            invalid = [ft for ft in file_types if ft not in EXT_TO_CONTENT_TYPE]
            if invalid:
                return jsonify(error="invalid_filter", field="file_type"), 400
            content_types = [EXT_TO_CONTENT_TYPE[ft] for ft in file_types]
            stmt = stmt.where(Note.content_type.in_(content_types))

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
            # clamp ทั้งขอบบนและขอบล่าง — ค่าติดลบผ่าน int() ได้ แต่ LIMIT -1 มีความหมาย
            # ต่างกันระหว่าง SQLite (ไม่จำกัด) กับ Postgres (error) จึงกันไว้ที่ชั้นนี้
            limit = max(1, min(int(args.get("limit", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE))
            offset = max(0, int(args.get("offset", 0)))
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

    @app.patch("/notes/<int:note_id>")
    def update_note(note_id):
        """แก้ metadata บางส่วน — US-19 (#19)

        เป็น partial update: ส่งมาเฉพาะฟิลด์ที่จะแก้ ฟิลด์ที่ไม่ส่งคงค่าเดิม
        ไฟล์แก้ไม่ได้ ต้องอัปโหลดใหม่ (AC ของ #19 พูดถึงแค่ metadata)
        """
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404
            if not token_matches(request.headers.get(HEADER_NAME), note.edit_token_hash):
                return jsonify(error="forbidden"), 403

            cleaned, errors = validate_metadata(request.form, partial=True)
            if errors:
                return jsonify(error="validation_failed", fields=errors), 400
            if not cleaned:
                return jsonify(error="no_fields_to_update"), 400

            for field, value in cleaned.items():
                setattr(note, field, value)
            note.updated_at = datetime.now(timezone.utc)

            session.commit()
            return jsonify(note.to_dict())

    @app.delete("/notes/<int:note_id>")
    def delete_note(note_id):
        """ลบโน้ตพร้อมไฟล์ — US-20 (#20)

        ลบแถวใน DB ให้ commit ผ่านก่อน แล้วค่อยลบไฟล์ ถ้าสลับลำดับแล้ว commit ล้ม
        จะเหลือ record ที่ชี้ไปยังไฟล์ที่ไม่มีอยู่จริง ซึ่งพังกว่าไฟล์กำพร้าที่ไม่มีใครชี้ถึง
        """
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404
            if not token_matches(request.headers.get(HEADER_NAME), note.edit_token_hash):
                return jsonify(error="forbidden"), 403

            storage_key = note.storage_key
            session.delete(note)
            session.commit()

        file_storage.delete(storage_key)
        return "", 204

    @app.get("/notes/<int:note_id>/download")
    def download_note(note_id):
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404

            # เปิดไฟล์ก่อนแล้วค่อยนับ — นับเฉพาะดาวน์โหลดที่สำเร็จ (AC ข้อ 3 ของ #12)
            try:
                file_handle = file_storage.open(note.storage_key)
            except FileNotFoundError:
                return jsonify(error="file_not_found"), 404

            # update แบบ atomic ใน SQL กันนับตกหล่นเมื่อมีดาวน์โหลดพร้อมกันหลาย request
            session.execute(
                update(Note)
                .where(Note.id == note_id)
                .values(download_count=Note.download_count + 1)
            )
            session.commit()

            return send_file(
                file_handle,
                mimetype=note.content_type,
                as_attachment=True,
                download_name=note.file_name,
            )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
