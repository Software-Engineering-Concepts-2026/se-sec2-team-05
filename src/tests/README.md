# 🧪 Automated Testing

โฟลเดอร์นี้เก็บ **unit / integration test ของโค้ดฝั่ง service** ส่วนเทสต์ของ prototype ฝั่ง front-end
อยู่ติดกับโค้ดที่มันทดสอบ (`prototypes/sprint1/note-utils.test.js`) เพื่อให้ไฟล์เทสต์กับไฟล์ต้นทางอยู่ด้วยกัน

| ไฟล์ | ทดสอบอะไร | ผู้เขียน |
| --- | --- | --- |
| `test_stats_service.py` | endpoint `/health`, `/stats` ของ Stats Service | อติชาติ |
| `conftest.py` | ทำให้ pytest มองเห็น `services/stats-service/app.py` (ยังไม่ได้ทำเป็น package) | อติชาติ |
| `test_auth_credentials.py` | ตรวจข้อมูลสมัครสมาชิกและ hash รหัสผ่านของ User & Auth Service (US-05) | อติชาติ |
| `test_auth_tokens.py` | ออก/ตรวจ JWT ของ User & Auth Service (US-06) | อติชาติ |
| `test_auth_api.py` | endpoint `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me` (US-05, US-06) | อติชาติ |
| `test_notes_identity.py` | Notes Service ตรวจ token ผ่าน auth-service ตัวจริงทาง HTTP (US-31) | อติชาติ |
| `test_notes_reports.py` | รายงานเนื้อหาและ workflow ตรวจ/ปฏิเสธ/ลบโน้ตของ admin (Issues #17, #18) | กฤตเมธ |
| `test_notes_ratings.py` | Notes Service rating: eligibility, การสร้าง/แก้ไข Rating, ค่าเฉลี่ย, authorization และ cleanup (Issue #13) | กฤตเมธ |
| `../../prototypes/sprint1/note-utils.test.js` | `escapeHtml`, `formatStars`, `compareNotes` | อติชาติ (Lab 7) |

> ⚠️ **ยังขาด:** เทสต์ของ วชิรวิทย์ และ กฤตเมธ — ตามใบงานทุกคนต้องมีเทสต์เป็นของตัวเอง
> ดูหัวข้อ "งานที่ยังค้าง" ใน [`docs/testing/readme.md`](../../docs/testing/readme.md)

## วิธีรันในเครื่อง

**เทสต์ Python (Stats Service)** — แนะนำให้ใช้ virtualenv แยก

```bash
python -m venv venv
# Windows: venv\Scripts\activate   |   macOS/Linux: source venv/bin/activate
pip install -r services/stats-service/requirements.txt
pip install -r services/notes-service/requirements.txt
pip install -r services/auth-service/requirements.txt
pip install -r src/tests/requirements-dev.txt
pytest src/tests -v
```

**เทสต์ JavaScript (prototypes)** — ใช้ test runner ที่มากับ Node 18+ ไม่ต้อง npm install

```bash
cd prototypes/sprint1
node --test
```

> ต้อง `cd` เข้าไปก่อน แล้วรัน `node --test` เปล่า ๆ — ถ้าส่ง path โฟลเดอร์เป็น argument
> ตรง ๆ (`node --test prototypes/sprint1/`) Node 24 จะตีความว่าเป็นชื่อ module แล้วพังด้วย
> `MODULE_NOT_FOUND`

ทั้งสองชุดถูกรันอัตโนมัติทุก PR ผ่าน [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
