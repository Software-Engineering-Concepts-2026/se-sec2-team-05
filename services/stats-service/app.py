# ============================================================
# Issue #16 - View Own Note Stats
#
# User Story:
# ในฐานะผู้แบ่งปัน ฉันต้องการดูสถิติยอดดาวน์โหลดของโน้ตตัวเอง
# เพื่อรู้ว่าเนื้อหาของฉันมีประโยชน์แค่ไหน
#
# Acceptance Criteria:
# 1. ผู้แบ่งปันดูจำนวนครั้งที่โน้ตตัวเองถูกดาวน์โหลดได้
# 2. ผู้แบ่งปันดูจำนวนครั้งที่โน้ตตัวเองถูกเปิด (view)
#    โดยแยกจากจำนวนดาวน์โหลด
# 3. ดูสถิติแยกเป็นรายโน้ตได้ ไม่รวมทั้งหมดเป็นก้อนเดียว
#
# US-28 (#28) AC3: เจ้าของโน้ตเห็นจำนวนครั้งที่ถูกขอบคุณ (เชื่อมกับ #16)
# ============================================================


from datetime import datetime, timezone

from flask import Flask, jsonify, request
from sqlalchemy import func, select

from stats_identity import IdentityUnavailable, identity_from_env
from stats_db import Note, Thank, build_session_factory


app = Flask(__name__)

session_factory = build_session_factory()
identity = identity_from_env()


# ============================================================
# Existing Endpoint
# GET /health
# ============================================================

@app.get("/health")
def health():
    return jsonify(
        status="ok",
        service="stats-service",
        time=datetime.now(timezone.utc).isoformat()
    )


# ============================================================
# Existing Endpoint
# GET /stats
#
# ของเดิมจากเพื่อน - ยังคงไว้
# ============================================================

@app.get("/stats")
def stats():
    with session_factory() as session:
        notes = session.query(Note).all()

        total_downloads = sum(note.download_count for note in notes)
        total_notes = len(notes)

        contributors = {}
        # ชื่อที่แสดงของเจ้าของ = uploader_name ของโน้ตล่าสุด (id มากสุด) ซึ่งเปิดให้ทุกคนเห็นอยู่แล้วที่ตัวโน้ต
        names = {}
        for note in sorted(notes, key=lambda n: n.id):
            contributors[note.uploader_id] = contributors.get(
                note.uploader_id, 0
            ) + note.download_count
            names[note.uploader_id] = note.uploader_name

        top_contributors = [
            {
                "owner_id": owner_id,
                "owner_name": names[owner_id],
                "total_downloads": downloads,
            }
            for owner_id, downloads in sorted(
                contributors.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

        return jsonify({
            "total_downloads": total_downloads,
            "total_notes": total_notes,
            "top_contributors": top_contributors,
        })


# ============================================================
# Issue #16 - View Own Note Stats
#
# GET /notes/<note_id>/stats
#
# ดูจำนวน Views, Downloads และ Thanks ของ Note ที่ตัวเองเป็นเจ้าของ
# Thanks นับจากตาราง `thanks` ของ notes-service (US-28 AC3) ไม่บอกว่าใครกด
#
# Authenticate through auth-service /auth/me before returning note statistics.
# ============================================================

@app.get("/notes/<int:note_id>/stats")
def get_note_stats(note_id):
    authorization = request.headers.get("Authorization")

    try:
        user = identity(authorization)
    except IdentityUnavailable:
        return jsonify(error="Authentication service unavailable"), 503

    if user is None:
        return jsonify(error="Authentication required"), 401

    with session_factory() as session:
        note = session.get(Note, note_id)

        if note is None:
            return jsonify(error="not_found"), 404

        if note.uploader_id != user["id"]:
            return jsonify(
                error="You can only view statistics of your own note"
            ), 403

        thanks = session.scalar(
            select(func.count()).select_from(Thank).where(Thank.note_id == note.id)
        )

        return jsonify({
            "note_id": note.id,
            "views": note.view_count,
            "downloads": note.download_count,
            "thanks": thanks,
        })


# ============================================================
# Run Stats Service
# ============================================================

if __name__ == "__main__":
    # ใช้แค่ตอนรันตรงเพื่อ dev ใน container ซึ่งต้องรับ request จากนอก container (bandit B104)
    # ใน compose และ Docker image รันผ่าน gunicorn ส่วนบน Vercel ไม่ผ่านบรรทัดนี้
    app.run(
        host="0.0.0.0",  # nosec B104
        port=5000
    )