"""Notes Service — US-08 (#8) ระบุ metadata ของโน้ต

Endpoint:
    GET  /health              health check (รูปแบบเดียวกับ stats-service)
    POST /notes               อัปโหลดไฟล์ + metadata (multipart/form-data) ต้อง login (US-31)
    GET  /notes               ค้นหา/กรองด้วย metadata ที่กรอกไว้ (AC ข้อ 4)
                              ถ้า login จะมี is_favorited ต่อโน้ต ไม่ login เป็น null (US-15)
                              และ thank_status ต่อโน้ต ไม่ login เป็น null (US-28)
    GET  /notes/favorites     รายการโปรดของตัวเอง ต้อง login (US-15)
    GET  /notes/<id>          รายละเอียดโน้ตหนึ่งรายการ
    PUT  /notes/<id>/rating  ให้/แก้คะแนนโน้ต ต้อง login และเคยเปิด/ดาวน์โหลด (Issue #13)
    POST /notes/<id>/reports รายงานเนื้อหาที่ไม่เหมาะสม (Issue #17)
    GET  /reports             รายการรายงานสำหรับ admin (Issue #17)
    DELETE /reports/<id>      ปฏิเสธรายการรายงานสำหรับ admin (Issue #17)
    DELETE /reports/<id>/note ลบโน้ตที่ถูกรายงานสำหรับ admin (Issue #18)
    POST /notes/<id>/comments แสดงความคิดเห็นใต้โน้ต (Issue #14)
    GET  /notes/<id>/comments  รายการความคิดเห็น (Issue #14)
    DELETE /notes/<id>/comments/<comment_id> ลบความคิดเห็นของตัวเอง (Issue #14)
    POST   /notes/<id>/favorite  บันทึกเข้ารายการโปรด ต้อง login (US-15)
    DELETE /notes/<id>/favorite  เอาออกจากรายการโปรด ต้อง login (US-15)
    POST   /notes/<id>/thanks    ขอบคุณเจ้าของโน้ต ต้อง login กดได้ครั้งเดียวต่อโน้ต (US-28)
    PATCH  /notes/<id>        แก้ metadata บางส่วน (US-19) ต้องมี X-Note-Token
    DELETE /notes/<id>        ลบโน้ตพร้อมไฟล์ (US-20) ต้องมี X-Note-Token
    GET  /notes/<id>/download ดาวน์โหลดไฟล์จริง
    GET  /notes/<id>/preview  รูปตัวอย่าง (PNG) ของโน้ต ไม่นับเป็นการดาวน์โหลด (US-11)

การอัปโหลดต้องส่ง `Authorization: Bearer <token>` ที่ได้จาก auth-service ชื่อผู้อัปโหลด
มาจากบัญชีนั้น ไม่รับจากฟอร์ม (ดู identity.py) — endpoint ที่อ่านอย่างเดียวยังเปิดหมด
ส่วนการแก้/ลบยังใช้ edit token ต่อโน้ตเหมือนเดิม (ดู ADR-004 และ tokens.py)
"""

import io
import os
from datetime import date, datetime, timezone

from flask import Flask, jsonify, request, send_file
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from identity import IdentityUnavailable, identity_from_env
from models import (
    Comment,
    Favorite,
    Note,
    NoteAccess,
    Rating,
    Report,
    Thank,
    build_session_factory,
)
from preview import PreviewUnavailable, render_preview
from storage import storage_from_env
from tokens import HEADER_NAME, issue_token, token_matches
from validation import (
    ALLOWED_CONTENT_TYPES,
    MAX_FILE_BYTES,
    validate_file,
    validate_metadata,
)

DEFAULT_DATABASE_URL = "sqlite:///notes.db"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Issue #14 - Comment validation
MAX_COMMENT_LENGTH = 1000
MAX_REPORT_REASON_LENGTH = 500


def configured_admin_user_ids() -> set[int]:
    return {
        int(value.strip())
        for value in os.environ.get("ADMIN_USER_IDS", "").split(",")
        if value.strip().isascii() and value.strip().isdecimal()
    }


def is_admin(user) -> bool:
    return user is not None and user.get("id") in configured_admin_user_ids()


def validate_report_reason(value):
    if not isinstance(value, str):
        raise ValueError("required")

    reason = value.strip()
    if not reason:
        raise ValueError("required")
    if len(reason) > MAX_REPORT_REASON_LENGTH:
        raise ValueError("max_length")

    return reason


def is_duplicate_report_error(error):
    constraint_name = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
    if constraint_name == "uq_reports_reporter_note":
        return True

    return "UNIQUE constraint failed: reports.reporter_id, reports.note_id" in str(error.orig)


def is_duplicate_access_error(error):
    constraint_name = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
    if constraint_name == "uq_note_accesses_user_note":
        return True

    return "UNIQUE constraint failed: note_accesses.user_id, note_accesses.note_id" in str(error.orig)


def is_duplicate_rating_error(error):
    constraint_name = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
    if constraint_name == "uq_ratings_user_note":
        return True

    return "UNIQUE constraint failed: ratings.user_id, ratings.note_id" in str(error.orig)


def validate_comment_content(value):
    """ตรวจสอบข้อความความคิดเห็นของ Issue #14"""
    if not isinstance(value, str):
        raise ValueError("comment content is required")

    content = value.strip()

    if not content:
        raise ValueError("comment content cannot be empty")

    if len(content) > MAX_COMMENT_LENGTH:
        raise ValueError(
            f"comment content must not exceed {MAX_COMMENT_LENGTH} characters"
        )

    return content


def validate_rating(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
        raise ValueError("rating must be an integer from 1 to 5")
    return value


# เพดานขนาด request ทั้งก้อน = ขนาดไฟล์สูงสุด + ที่เผื่อไว้ให้ multipart boundary กับฟิลด์ metadata
# ตั้งให้สูงกว่า MAX_FILE_BYTES เล็กน้อยโดยตั้งใจ ไฟล์ที่เกินนิดเดียวจะได้ตกที่ validate_file
# ซึ่งบอกเหตุผลรายฟิลด์ แทนที่จะถูกตัดทิ้งแบบไม่มีรายละเอียดตั้งแต่ชั้น Werkzeug
REQUEST_OVERHEAD_BYTES = 1024 * 1024
MAX_REQUEST_BYTES = MAX_FILE_BYTES + REQUEST_OVERHEAD_BYTES

# รูปตัวอย่างของโน้ตไม่เปลี่ยนเลยหลังอัปโหลด (แก้ไฟล์ไม่ได้ ดู IMMUTABLE_FIELDS) จึง cache ได้นาน
PREVIEW_CACHE_CONTROL = "public, max-age=86400"


def preview_key_for(storage_key: str) -> str:
    return f"previews/{storage_key}.png"


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


def parse_page(args) -> tuple[int, int]:
    """อ่าน limit/offset แบบเดียวกับ GET /notes — raise ValueError ถ้าไม่ใช่ตัวเลข"""
    limit = max(1, min(int(args.get("limit", DEFAULT_PAGE_SIZE)), MAX_PAGE_SIZE))
    offset = max(0, int(args.get("offset", 0)))
    return limit, offset


def utc_iso(moment: datetime) -> str:
    """SQLite เก็บเวลาโดยไม่มี timezone — อ่านกลับมาต้องระบุ UTC ให้ตรงกับตอนเพิ่งสร้าง"""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.isoformat()


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
            return jsonify(error="unauthorized"), 401, {
                "WWW-Authenticate": "Bearer"
            }

        cleaned, errors = validate_metadata(request.form)

        content_type, size_bytes, file_error = validate_file(
            request.files.get("file")
        )

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

        # US-26: กรองตามหัวข้อเลกเชอร์แบบ partial match — ต่างจาก `q` ตรงที่ค้นเฉพาะ
        # Note.topic ไม่ปนกับชื่อวิชา/รหัส/บทเรียน · escape %,_ กัน wildcard หลุดจากค่าผู้ใช้
        topic = (args.get("topic") or "").strip()
        if topic:
            escaped = topic.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            stmt = stmt.where(Note.topic.ilike(f"%{escaped}%", escape="\\"))

        if args.get("year_level"):
            try:
                stmt = stmt.where(
                    Note.year_level == int(args["year_level"])
                )
            except ValueError:
                return jsonify(
                    error="invalid_filter",
                    field="year_level",
                ), 400

        # US-10: กรองตามประเภทไฟล์ — รับหลายค่าพร้อมกันได้ (OR ภายในตัวกรองนี้)
        file_types = args.getlist("file_type")

        if file_types:
            invalid = [
                ft for ft in file_types
                if ft not in EXT_TO_CONTENT_TYPE
            ]

            if invalid:
                return jsonify(
                    error="invalid_filter",
                    field="file_type",
                ), 400

            content_types = [
                EXT_TO_CONTENT_TYPE[ft]
                for ft in file_types
            ]

            stmt = stmt.where(
                Note.content_type.in_(content_types)
            )

        parsed_dates = {}
        for field in ("date_from", "date_to"):
            if args.get(field):
                try:
                    parsed_dates[field] = date.fromisoformat(args[field])
                except ValueError:
                    return jsonify(
                        error="invalid_filter",
                        field=field,
                    ), 400

        # ช่วงกลับด้าน (date_from มาหลัง date_to) เดิมได้ผลว่างเงียบๆ — ผู้ใช้กรอกผิดควรรู้ว่าผิด
        # ไม่ใช่เข้าใจว่าไม่มีโน้ตในช่วงนั้น
        if "date_from" in parsed_dates and "date_to" in parsed_dates:
            if parsed_dates["date_from"] > parsed_dates["date_to"]:
                return jsonify(error="invalid_filter", field="date_to"), 400

        if "date_from" in parsed_dates:
            stmt = stmt.where(Note.class_date >= parsed_dates["date_from"])
        if "date_to" in parsed_dates:
            stmt = stmt.where(Note.class_date <= parsed_dates["date_to"])

        sort = args.get("sort", "new")

        if sort not in SORT_COLUMNS:
            return jsonify(
                error="invalid_filter",
                field="sort",
            ), 400

        stmt = stmt.order_by(SORT_COLUMNS[sort])

        try:
            # clamp ทั้งขอบบนและขอบล่าง — ค่าติดลบผ่าน int() ได้ แต่ LIMIT -1 มีความหมาย
            # ต่างกันระหว่าง SQLite (ไม่จำกัด) กับ Postgres (error) จึงกันไว้ที่ชั้นนี้
            limit, offset = parse_page(args)
        except ValueError:
            return jsonify(
                error="invalid_filter",
                field="limit/offset",
            ), 400

        user_id = optional_user_id()
        with session_factory() as session:
            rows = session.scalars(stmt.limit(limit).offset(offset)).all()
            flags = favorite_flags(session, user_id, rows)
            thanks = thank_statuses(session, user_id, rows)
            items = [
                {**n.to_dict(), "is_favorited": flags.get(n.id), "thank_status": thanks.get(n.id)}
                for n in rows
            ]
            return jsonify(items=items, count=len(items))

    def require_user():
        """ตรวจตัวตนสำหรับ route ของรายการโปรด คืน (user, None) หรือ (None, error response)

        แยกจาก create_note ตั้งใจ — ไม่ refactor โค้ดของ US-31 ในงานนี้
        """
        try:
            user = current_user(request.headers.get("Authorization"))
        except IdentityUnavailable:
            return None, (jsonify(error="auth_unavailable"), 503)
        if user is None:
            return None, (jsonify(error="unauthorized"), 401, {"WWW-Authenticate": "Bearer"})
        return user, None

    def require_admin():
        user, failure = require_user()
        if failure:
            return None, failure
        if not is_admin(user):
            return None, (jsonify(error="forbidden"), 403)
        return user, None

    def delete_note_record(session, note):
        storage_key = note.storage_key
        session.execute(delete(Comment).where(Comment.note_id == note.id))
        session.execute(delete(Favorite).where(Favorite.note_id == note.id))
        session.execute(delete(NoteAccess).where(NoteAccess.note_id == note.id))
        session.execute(delete(Thank).where(Thank.note_id == note.id))
        session.delete(note)
        session.commit()
        return storage_key

    def delete_note_files(storage_key):
        file_storage.delete(storage_key)
        file_storage.delete(preview_key_for(storage_key))

    def optional_user_id():
        """id ของผู้ใช้ที่ login หรือ None — ใช้กับ route อ่านที่เปิดให้คนไม่ login ด้วย

        token ใช้ไม่ได้หรือ auth-service ล่มก็ได้ None เหมือนกัน การค้นหาต้องไม่พังเพราะ
        แค่จะใส่สถานะ ★ ไม่ได้ (D2, D3)
        """
        authorization = request.headers.get("Authorization")
        if not authorization:
            # คนไม่ login ไม่ต้องถาม auth-service เลย (US-31: อ่านอย่างเดียวไม่พึ่ง auth)
            return None
        try:
            user = current_user(authorization)
        except IdentityUnavailable:
            return None
        return user["id"] if user else None

    def favorite_flags(session, user_id, notes):
        """คืน {note_id: bool} หรือ {} ถ้าไม่ login — query เดียวทั้งหน้า (D5)"""
        if user_id is None or not notes:
            return {}
        favorited = set(
            session.scalars(
                select(Favorite.note_id).where(
                    Favorite.user_id == user_id,
                    Favorite.note_id.in_([n.id for n in notes]),
                )
            )
        )
        return {n.id: n.id in favorited for n in notes}

    def thank_statuses(session, user_id, notes):
        """คืน {note_id: "own_note" | "thanked" | "can_thank"} หรือ {} ถ้าไม่ login — US-28

        query ตาราง thanks ครั้งเดียวทั้งหน้าเหมือน favorite_flags
        """
        if user_id is None or not notes:
            return {}
        thanked = set(
            session.scalars(
                select(Thank.note_id).where(
                    Thank.user_id == user_id,
                    Thank.note_id.in_([n.id for n in notes]),
                )
            )
        )

        def status_of(note):
            if note.uploader_id == user_id:
                return "own_note"
            return "thanked" if note.id in thanked else "can_thank"

        return {n.id: status_of(n) for n in notes}

    def record_note_access(session, note_id, user_id, counter):
        if user_id is not None:
            already_accessed = session.scalars(
                select(NoteAccess.id).where(
                    NoteAccess.user_id == user_id,
                    NoteAccess.note_id == note_id,
                )
            ).first()
            if already_accessed is None:
                session.add(NoteAccess(user_id=user_id, note_id=note_id))

        session.execute(
            update(Note)
            .where(Note.id == note_id)
            .values({counter: getattr(Note, counter) + 1})
        )
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            if user_id is None or not is_duplicate_access_error(error):
                raise
            # Simultaneous first access by the same member: keep the access row unique,
            # but preserve this request's aggregate view/download count.
            session.execute(
                update(Note)
                .where(Note.id == note_id)
                .values({counter: getattr(Note, counter) + 1})
            )
            session.commit()

    @app.get("/notes/favorites")
    def list_favorites():
        """รายการโปรดของตัวเอง เรียงที่เพิ่งบันทึกก่อน — US-15 (#15)"""
        user, failure = require_user()
        if failure:
            return failure
        try:
            limit, offset = parse_page(request.args)
        except ValueError:
            return jsonify(error="invalid_filter", field="limit/offset"), 400

        # JOIN กับ notes เป็นแนวป้องกันอีกชั้น — delete_note ลบแถว favorites ของโน้ตนั้นทิ้งแล้ว
        stmt = (
            select(Note, Favorite.created_at)
            .join(Favorite, Favorite.note_id == Note.id)
            .where(Favorite.user_id == user["id"])
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
            .limit(limit)
            .offset(offset)
        )
        with session_factory() as session:
            rows = session.execute(stmt).all()
            items = [
                {**note.to_dict(), "is_favorited": True, "favorited_at": utc_iso(favorited_at)}
                for note, favorited_at in rows
            ]
            return jsonify(items=items, count=len(items))

    @app.post("/notes/<int:note_id>/favorite")
    def add_favorite(note_id):
        user, failure = require_user()
        if failure:
            return failure
        with session_factory() as session:
            if session.get(Note, note_id) is None:
                return jsonify(error="not_found"), 404

            def find_existing():
                return session.scalars(
                    select(Favorite).where(
                        Favorite.user_id == user["id"], Favorite.note_id == note_id
                    )
                ).first()

            favorite, status = find_existing(), 200
            if favorite is None:
                favorite, status = Favorite(user_id=user["id"], note_id=note_id), 201
                session.add(favorite)
                try:
                    session.commit()
                except IntegrityError:
                    # กดซ้อนสองครั้งพร้อมกัน — อีก request บันทึกไปก่อน ถือว่า idempotent
                    session.rollback()
                    favorite, status = find_existing(), 200
            return (
                jsonify(
                    note_id=note_id,
                    is_favorited=True,
                    favorited_at=utc_iso(favorite.created_at),
                ),
                status,
            )

    @app.delete("/notes/<int:note_id>/favorite")
    def remove_favorite(note_id):
        user, failure = require_user()
        if failure:
            return failure
        with session_factory() as session:
            if session.get(Note, note_id) is None:
                return jsonify(error="not_found"), 404
            # user_id มาจาก token เท่านั้น จึงลบได้แค่รายการของตัวเอง
            session.execute(
                delete(Favorite).where(
                    Favorite.user_id == user["id"], Favorite.note_id == note_id
                )
            )
            session.commit()
        return "", 204

    @app.post("/notes/<int:note_id>/thanks")
    def thank_owner(note_id):
        """ขอบคุณเจ้าของโน้ต — US-28 (#28)

        ต้อง login · ขอบคุณโน้ตตัวเองไม่ได้ · ครั้งแรก 201 กดซ้ำ 200 (ไม่เพิ่มยอด) ·
        ไม่มี endpoint ยกเลิก · "หลังดาวน์โหลด" เป็นเงื่อนไขฝั่ง UI ไม่ได้ตรวจที่นี่
        """
        user, failure = require_user()
        if failure:
            return failure
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404
            if note.uploader_id == user["id"]:
                return jsonify(error="own_note"), 403

            def find_existing():
                return session.scalars(
                    select(Thank).where(Thank.user_id == user["id"], Thank.note_id == note_id)
                ).first()

            thank, status = find_existing(), 200
            if thank is None:
                thank, status = Thank(user_id=user["id"], note_id=note_id), 201
                session.add(thank)
                try:
                    session.commit()
                except IntegrityError:
                    # กดซ้อนสองครั้งพร้อมกัน — อีก request บันทึกไปก่อน ถือว่ากดซ้ำ
                    session.rollback()
                    thank, status = find_existing(), 200
            return (
                jsonify(note_id=note_id, thanked=True, thanked_at=utc_iso(thank.created_at)),
                status,
            )

    @app.get("/notes/<int:note_id>")
    def get_note(note_id):
        with session_factory() as session:
            note = session.get(Note, note_id)

            if note is None:
                return jsonify(error="not_found"), 404

            user_id = optional_user_id()
            record_note_access(session, note_id, user_id, "view_count")
            session.refresh(note)

            flags = favorite_flags(session, user_id, [note])
            thanks = thank_statuses(session, user_id, [note])
            result = {
                **note.to_dict(),
                "is_favorited": flags.get(note.id),
                "thank_status": thanks.get(note.id),
            }
            if user_id is not None:
                result["can_rate"] = True
                result["user_rating"] = session.scalars(
                    select(Rating.value).where(
                        Rating.user_id == user_id,
                        Rating.note_id == note_id,
                    )
                ).first()
            return jsonify(result)

    # Issue #13 - Rating a Note
    @app.put("/notes/<int:note_id>/rating")
    def set_note_rating(note_id):
        user, failure = require_user()
        if failure:
            return failure

        payload = request.get_json(silent=True)
        try:
            rating_value = validate_rating(
                payload.get("rating") if isinstance(payload, dict) else None
            )
        except ValueError as error:
            return jsonify(
                error="validation_failed",
                fields={"rating": str(error)},
            ), 400

        with session_factory() as session:
            if session.get(Note, note_id) is None:
                return jsonify(error="not_found"), 404

            has_accessed = session.scalars(
                select(NoteAccess.id).where(
                    NoteAccess.user_id == user["id"],
                    NoteAccess.note_id == note_id,
                )
            ).first()
            if has_accessed is None:
                return jsonify(error="not_eligible"), 403

            rating = session.scalars(
                select(Rating).where(
                    Rating.user_id == user["id"],
                    Rating.note_id == note_id,
                )
            ).first()
            created = rating is None
            if created:
                rating = Rating(
                    user_id=user["id"],
                    note_id=note_id,
                    value=rating_value,
                )
                session.add(rating)
            else:
                rating.value = rating_value
                rating.updated_at = datetime.now(timezone.utc)

            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                if not created or not is_duplicate_rating_error(error):
                    raise
                rating = session.scalars(
                    select(Rating).where(
                        Rating.user_id == user["id"],
                        Rating.note_id == note_id,
                    )
                ).first()
                if rating is None:
                    raise
                rating.value = rating_value
                rating.updated_at = datetime.now(timezone.utc)
                session.commit()

            note = session.get(Note, note_id)
            session.expire(note, ["ratings"])
            return jsonify(
                note_id=note_id,
                rating=rating.value,
                average_rating=note.average_rating,
                rating_count=len(note.ratings),
            )

    @app.post("/notes/<int:note_id>/reports")
    def create_report(note_id):
        user, failure = require_user()
        if failure:
            return failure

        payload = request.get_json(silent=True)
        try:
            reason = validate_report_reason(payload.get("reason") if isinstance(payload, dict) else None)
        except ValueError as error:
            return jsonify(error="validation_failed", fields={"reason": str(error)}), 400

        with session_factory() as session:
            if session.get(Note, note_id) is None:
                return jsonify(error="not_found"), 404

            existing = session.scalars(
                select(Report).where(
                    Report.reporter_id == user["id"],
                    Report.note_id == note_id,
                )
            ).first()
            if existing is not None:
                return jsonify(error="already_reported"), 409

            report = Report(
                note_id=note_id,
                reporter_id=user["id"],
                reporter_name=user["display_name"],
                reason=reason,
            )
            session.add(report)
            try:
                session.commit()
            except IntegrityError as error:
                session.rollback()
                if is_duplicate_report_error(error):
                    return jsonify(error="already_reported"), 409
                raise

            return jsonify(report.to_dict()), 201

    @app.get("/reports")
    def list_reports():
        _, failure = require_admin()
        if failure:
            return failure

        with session_factory() as session:
            reports = session.scalars(
                select(Report).order_by(Report.created_at.desc(), Report.id.desc())
            ).all()
            notes = {
                note.id: note
                for note in session.scalars(
                    select(Note).where(Note.id.in_([report.note_id for report in reports]))
                ).all()
            }
            items = [
                {**report.to_dict(), "note": notes[report.note_id].to_dict()}
                for report in reports
            ]
            return jsonify(count=len(items), reports=items)

    @app.delete("/reports/<int:report_id>")
    def delete_report(report_id):
        _, failure = require_admin()
        if failure:
            return failure

        with session_factory() as session:
            report = session.get(Report, report_id)
            if report is None:
                return jsonify(error="not_found"), 404

            session.delete(report)
            session.commit()

        return "", 204

    @app.delete("/reports/<int:report_id>/note")
    def delete_reported_note(report_id):
        _, failure = require_admin()
        if failure:
            return failure

        with session_factory() as session:
            report = session.get(Report, report_id)
            if report is None:
                return jsonify(error="not_found"), 404

            note = session.get(Note, report.note_id)
            if note is None:
                return jsonify(error="not_found"), 404

            storage_key = delete_note_record(session, note)

        delete_note_files(storage_key)
        return "", 204

    # ============================================================
    # Issue #14 - Comment on a Note
    #
    # User Story:
    # ในฐานะสมาชิก ฉันต้องการแสดงความคิดเห็นใต้โน้ต
    # เพื่อสอบถามหรือเสริมข้อมูลกับเจ้าของโน้ต
    #
    # Acceptance Criteria:
    # 1. แสดงความคิดเห็นใต้โน้ตได้เมื่อเข้าสู่ระบบแล้ว
    # 2. แสดงรายการความคิดเห็นเรียงตามเวลาล่าสุด
    # 3. ลบความคิดเห็นของตัวเองได้
    # ============================================================

    @app.post("/notes/<int:note_id>/comments")
    def create_comment(note_id):
        # AC #1: ต้อง login ก่อนจึงจะแสดงความคิดเห็นได้
        try:
            user = current_user(
                request.headers.get("Authorization")
            )
        except IdentityUnavailable:
            return jsonify(error="auth_unavailable"), 503

        if user is None:
            return jsonify(error="unauthorized"), 401, {
                "WWW-Authenticate": "Bearer"
            }

        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify(
                error="validation_failed",
                fields={"content": "required"},
            ), 400

        try:
            content = validate_comment_content(
                payload.get("content")
            )
        except ValueError as error:
            return jsonify(
                error="validation_failed",
                fields={"content": str(error)},
            ), 400

        with session_factory() as session:
            # ป้องกันการสร้าง comment ให้ note ที่ไม่มีอยู่จริง
            note = session.get(Note, note_id)

            if note is None:
                return jsonify(error="not_found"), 404

            comment = Comment(
                note_id=note_id,
                user_id=user["id"],
                content=content,
            )

            session.add(comment)
            session.commit()

            return jsonify(comment.to_dict()), 201

    @app.get("/notes/<int:note_id>/comments")
    def get_comments(note_id):
        with session_factory() as session:
            # note ไม่มีจริง -> 404
            note = session.get(Note, note_id)

            if note is None:
                return jsonify(error="not_found"), 404

            # AC #2: เรียงความคิดเห็นจากใหม่ -> เก่า
            # ใช้ id เป็นตัวสำรองกรณี created_at เท่ากัน
            stmt = (
                select(Comment)
                .where(Comment.note_id == note_id)
                .order_by(
                    Comment.created_at.desc(),
                    Comment.id.desc(),
                )
            )

            comments = session.scalars(stmt).all()

            return jsonify(
                comments=[
                    comment.to_dict()
                    for comment in comments
                ]
            )

    @app.delete("/notes/<int:note_id>/comments/<int:comment_id>")
    def delete_comment(note_id, comment_id):
        # AC #3: ต้อง login ก่อนลบ comment
        try:
            user = current_user(
                request.headers.get("Authorization")
            )
        except IdentityUnavailable:
            return jsonify(error="auth_unavailable"), 503

        if user is None:
            return jsonify(error="unauthorized"), 401, {
                "WWW-Authenticate": "Bearer"
            }

        with session_factory() as session:
            comment = session.get(Comment, comment_id)

            # comment ไม่มี หรือ comment ไม่ได้อยู่ใต้ note นี้
            if comment is None or comment.note_id != note_id:
                return jsonify(error="not_found"), 404

            # AC #3: ลบได้เฉพาะ comment ของตัวเอง
            if comment.user_id != user["id"]:
                return jsonify(error="forbidden"), 403

            session.delete(comment)
            session.commit()

            return "", 204

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

            if not token_matches(
                request.headers.get(HEADER_NAME),
                note.edit_token_hash,
            ):
                return jsonify(error="forbidden"), 403

            cleaned, errors = validate_metadata(
                request.form,
                partial=True,
            )

            if errors:
                return jsonify(
                    error="validation_failed",
                    fields=errors,
                ), 400

            if not cleaned:
                return jsonify(
                    error="no_fields_to_update"
                ), 400

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

            if not token_matches(
                request.headers.get(HEADER_NAME),
                note.edit_token_hash,
            ):
                return jsonify(error="forbidden"), 403

            storage_key = delete_note_record(session, note)

        delete_note_files(storage_key)
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

            # Update แบบ atomic และบันทึกสิทธิ์ให้คะแนนเฉพาะผู้ใช้ที่ตรวจตัวตนได้
            user_id = optional_user_id()
            record_note_access(session, note_id, user_id, "download_count")

            return send_file(
                file_handle,
                mimetype=note.content_type,
                as_attachment=True,
                download_name=note.file_name,
            )

    @app.get("/notes/<int:note_id>/preview")
    def preview_note(note_id):
        """รูปตัวอย่างของโน้ต — US-11 (#11)

        สร้างครั้งแรกที่มีคนขอแล้วเก็บไว้ใน storage ครั้งต่อไปส่งจากที่เก็บเลย ไม่ต้องอ่านไฟล์เต็ม
        แยกจาก /download โดยตั้งใจ จึงไม่ไปแตะ download_count
        """
        with session_factory() as session:
            note = session.get(Note, note_id)
            if note is None:
                return jsonify(error="not_found"), 404
            storage_key, content_type = note.storage_key, note.content_type

        preview_key = preview_key_for(storage_key)
        if not file_storage.exists(preview_key):
            try:
                source = file_storage.open(storage_key)
            except FileNotFoundError:
                return jsonify(error="file_not_found"), 404
            with source:
                try:
                    data = render_preview(source, content_type)
                except PreviewUnavailable:
                    return jsonify(error="preview_unavailable"), 422
            file_storage.save_bytes(preview_key, data)

        # รูปตัวอย่างเล็ก (ไม่กี่ร้อย KB) อ่านเข้า memory แล้วปิดไฟล์ทันที ไม่ต้องถือ file handle
        # ค้างไว้ให้ WSGI server มาปิดทีหลังเหมือนการส่งไฟล์เต็มของ /download
        with file_storage.open(preview_key) as preview_file:
            data = preview_file.read()
        response = send_file(io.BytesIO(data), mimetype="image/png")
        response.headers["Cache-Control"] = PREVIEW_CACHE_CONTROL
        return response

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)