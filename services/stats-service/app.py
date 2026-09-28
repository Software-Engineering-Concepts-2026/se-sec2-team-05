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
# ============================================================


from datetime import datetime, timezone

from flask import Flask, jsonify, request

from storage import StatsStorage


app = Flask(__name__)

storage = StatsStorage()


# ============================================================
# Existing Stats Service Mock Data
# ของเดิมจากเพื่อน - ห้ามลบ
# ============================================================

_MOCK_STATS = {
    "total_downloads": 0,
    "total_notes": 0,
    "top_contributors": [],
}


# ============================================================
# Issue #16 - Mock Note Statistics
#
# ใช้สำหรับทดสอบ Feature #16 ก่อนเชื่อม PostgreSQL
# ============================================================

storage.create(
    note_id=1,
    owner_id=101
)

storage.create(
    note_id=2,
    owner_id=101
)

storage.create(
    note_id=3,
    owner_id=102
)

# เพิ่มข้อมูลตัวอย่างสำหรับทดสอบ
for _ in range(25):
    storage.add_view(1)

for _ in range(8):
    storage.add_download(1)

for _ in range(42):
    storage.add_view(2)

for _ in range(15):
    storage.add_download(2)

for _ in range(18):
    storage.add_view(3)

for _ in range(4):
    storage.add_download(3)


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
    return jsonify(_MOCK_STATS)


# ============================================================
# Issue #16 - View Own Note Stats
#
# GET /notes/<note_id>/stats
#
# ดูจำนวน Views และ Downloads ของ Note ที่ตัวเองเป็นเจ้าของ
#
# สำหรับตอนนี้ใช้ X-User-ID เป็น Mock Authentication
# ============================================================

@app.get("/notes/<int:note_id>/stats")
def get_note_stats(note_id):

    # --------------------------------------------------------
    # Mock Authentication
    # --------------------------------------------------------

    user_id = request.headers.get("X-User-ID")

    if user_id is None:
        return jsonify(
            error="Authentication required"
        ), 401

    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify(
            error="Invalid X-User-ID"
        ), 400

    # --------------------------------------------------------
    # หา Statistics ของ Note
    # --------------------------------------------------------

    stat = storage.get_by_note(note_id)

    if stat is None:
        return jsonify(
            error="Note statistics not found"
        ), 404

    # --------------------------------------------------------
    # Issue #16 - ตรวจว่าเป็นเจ้าของ Note หรือไม่
    # --------------------------------------------------------

    if stat.owner_id != user_id:
        return jsonify(
            error="You can only view statistics of your own note"
        ), 403

    # --------------------------------------------------------
    # Issue #16 - แสดง Views และ Downloads แยกกัน
    # --------------------------------------------------------

    return jsonify({
        "note_id": stat.note_id,
        "views": stat.views,
        "downloads": stat.downloads
    })


# ============================================================
# Issue #16 - Record Note View
#
# ใช้สำหรับจำลองการเพิ่มจำนวนครั้งที่ Note ถูกเปิด
# ============================================================

@app.post("/notes/<int:note_id>/view")
def record_note_view(note_id):

    stat = storage.add_view(note_id)

    if stat is None:
        return jsonify(
            error="Note statistics not found"
        ), 404

    return jsonify({
        "note_id": stat.note_id,
        "views": stat.views,
        "downloads": stat.downloads
    })


# ============================================================
# Issue #16 - Record Note Download
#
# ใช้สำหรับจำลองการเพิ่มจำนวนครั้งที่ Note ถูกดาวน์โหลด
# ============================================================

@app.post("/notes/<int:note_id>/download")
def record_note_download(note_id):

    stat = storage.add_download(note_id)

    if stat is None:
        return jsonify(
            error="Note statistics not found"
        ), 404

    return jsonify({
        "note_id": stat.note_id,
        "views": stat.views,
        "downloads": stat.downloads
    })


# ============================================================
# Run Stats Service
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )