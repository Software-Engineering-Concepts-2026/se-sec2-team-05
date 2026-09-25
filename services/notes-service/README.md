# Notes Service

Service ที่ดูแล metadata และไฟล์ของโน้ต — ทำตาม [US-08 (#8)](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/issues/8)
ขอบเขตและสิ่งที่จงใจยังไม่ทำในรอบนี้อธิบายไว้ใน [ADR-003](../../docs/architecture/adr/0003-tracer-bullet-scope.th.md)

> ⚠️ **ยังไม่มี authentication** — endpoint ที่อ่านอย่างเดียวเปิดหมด และ `uploader_name`
> รับมาจากฟอร์มตรง ๆ ส่วนการแก้/ลบกันด้วย edit token ต่อโน้ต ซึ่ง **ไม่ใช่** ระบบ auth
> (ดู [ADR-004](../../docs/architecture/adr/0004-per-note-edit-token.th.md)) ห้าม deploy ออกสู่สาธารณะก่อน #5/#6 เสร็จ

## รันในเครื่อง

```bash
docker compose up --build        # ยก Postgres + notes-service (:5001) + stats-service (:5000)
docker compose down -v           # ลบ volume ด้วย — จำเป็นเมื่อแก้ schema เพราะยังไม่มี migration
```

รันแบบไม่ใช้ Docker (ใช้ SQLite แทน Postgres):

```bash
pip install -r services/notes-service/requirements.txt
NOTES_STORAGE_DIR=./data python services/notes-service/app.py
```

| Environment variable | ค่า default | ใช้ทำอะไร |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///notes.db` | SQLAlchemy URL — compose ตั้งเป็น `postgresql+psycopg://...` |
| `NOTES_STORAGE_DIR` | `/data/notes` | โฟลเดอร์เก็บไฟล์โน้ต (mount เป็น volume ใน compose) |

## API

| Method | Path | คำอธิบาย |
| --- | --- | --- |
| `GET` | `/health` | health check |
| `POST` | `/notes` | อัปโหลดไฟล์ + metadata (`multipart/form-data`) → `201` พร้อม object ของโน้ต |
| `GET` | `/notes` | ค้นหา/กรอง → `{ items: [...], count: n }` |
| `GET` | `/notes/<id>` | รายละเอียดโน้ตหนึ่งรายการ |
| `PATCH` | `/notes/<id>` | แก้ metadata บางส่วน — ต้องมี `X-Note-Token` (US-19) |
| `DELETE` | `/notes/<id>` | ลบโน้ตพร้อมไฟล์ — ต้องมี `X-Note-Token` (US-20) → `204` |
| `GET` | `/notes/<id>/download` | ดาวน์โหลดไฟล์จริง (ตั้งชื่อไฟล์ตามที่ผู้ใช้อัปโหลดมา) และนับยอดดาวน์โหลด (US-12) |

### `POST /notes`

| ฟิลด์ | บังคับ | หมายเหตุ |
| --- | --- | --- |
| `file` | ✅ | PDF / PNG / JPEG เท่านั้น ไม่เกิน 20 MB |
| `title` | ✅ | ชื่อโน้ต |
| `subject_name`, `subject_code`, `faculty`, `lesson` | ✅ | ข้อความ |
| `year_level` | ✅ | ตัวเลข 1–8 |
| `topic`, `class_date`, `description`, `uploader_name` | — | `class_date` เป็น `YYYY-MM-DD` |

ถ้า validate ไม่ผ่านจะได้ `400` พร้อมรายการ error **ครบทุกฟิลด์ในครั้งเดียว** ไม่ได้หยุดที่ตัวแรก

```json
{ "error": "validation_failed", "fields": { "subject_code": "จำเป็นต้องกรอก", "year_level": "ต้องเป็นตัวเลข" } }
```

request ที่ใหญ่เกิน 21 MB (ไฟล์ 20 MB + ที่เผื่อให้ multipart/metadata) จะถูกตัดตั้งแต่ชั้น Werkzeug
และได้ `413` ที่มีรูปร่าง JSON เดียวกัน — ไม่ต้องรอให้อ่าน body เข้ามาครบก่อนถึงจะปฏิเสธ

### `GET /notes` — query parameters

`q` (ค้นในชื่อ/วิชา/รหัส/บทเรียน/หัวข้อ), `faculty`, `subject_code`, `year_level`,
`file_type` (`pdf` | `png` | `jpg`), `date_from`, `date_to`,
`sort` (`new` | `old` | `class_date` | `title`), `limit` (สูงสุด 100), `offset`

`file_type` ส่งซ้ำได้หลายค่าเพื่อกรองแบบ OR เช่น `?file_type=pdf&file_type=png` (US-10)
ค่าที่รับมาจาก client เป็นนามสกุลสั้น แล้วแปลงเป็น content type ผ่าน allowlist ของ `validation.py`
ถ้ามีค่าใดไม่อยู่ใน allowlist จะปฏิเสธทั้งชุดด้วย `400` ไม่ใช่กรองเฉพาะค่าที่ถูก

`limit` ถูก clamp ไว้ที่ 1–100 และ `offset` ต่ำสุด 0 ค่าติดลบจึงไม่หลุดไปถึง SQL

ค่าที่ผิดรูปจะได้ `400` (`{"error": "invalid_filter", "field": ...}`) ไม่ใช่ `500`
และ `sort` รับได้เฉพาะค่าใน allowlist เท่านั้น ไม่ได้เอาค่าจาก client ไปต่อเป็น SQL

### `GET /notes/<id>/download` — ดาวน์โหลดและนับยอด (US-12)

ตอบเป็นไฟล์แนบ (`Content-Disposition: attachment`) ชื่อไฟล์ตามที่ผู้อัปโหลดตั้งไว้
พร้อมเพิ่ม `download_count` ของโน้ตนั้นทีละ 1 ซึ่งแสดงอยู่ใน object ของโน้ต (`GET /notes`, `GET /notes/<id>`)
และเป็นข้อมูลตั้งต้นให้สถิติของเจ้าของโน้ตใน US-16

| กรณี | Response | `download_count` |
| --- | --- | --- |
| ดาวน์โหลดสำเร็จ | `200` + ไฟล์ | +1 |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` | — |
| มี record แต่ไฟล์หายจาก storage | `404` `{"error": "file_not_found"}` | ไม่เปลี่ยน |

- **นับเฉพาะที่สำเร็จ** — service เปิดไฟล์จาก storage ก่อน แล้วค่อยนับ ไฟล์หายจึงไม่ทำให้ยอดเพิ่มโดยที่ผู้ใช้ไม่ได้ไฟล์ไป
- **นับแบบ atomic** — ใช้ `UPDATE notes SET download_count = download_count + 1` ใน SQL ตรง ๆ
  ไม่อ่านค่ามาบวกใน Python จึงไม่นับตกหล่นเมื่อมีหลาย request โหลดพร้อมกัน
- นับต่อ request ที่ดาวน์โหลดสำเร็จ ยังไม่ตัดซ้ำรายผู้ใช้ เพราะยังไม่มีระบบ auth (#5/#6) ให้ระบุตัวผู้ดาวน์โหลด
- ตาราง `notes` มีคอลัมน์ `download_count` เพิ่มมา ยังไม่มี migration จึงต้อง `docker compose down -v` ตอนอัปเดต schema

### `PATCH /notes/<id>` และ `DELETE /notes/<id>` — ต้องมี edit token

ตอน `POST /notes` สำเร็จ response จะมีฟิลด์ `edit_token` เพิ่มมา **ครั้งเดียวเท่านั้น**
เก็บไว้ให้ดี เพราะฐานข้อมูลเก็บแค่ hash และไม่มี endpoint ไหนคืนค่านี้ให้อีก ถ้าทำหาย
จะแก้หรือลบโน้ตใบนั้นไม่ได้อีกเลย เหตุผลของกลไกนี้และข้อจำกัดอยู่ใน ADR-004

```bash
# แก้เฉพาะฟิลด์ที่ส่งมา ฟิลด์ที่ไม่ส่งคงค่าเดิม (partial update)
curl -X PATCH localhost:5001/notes/1 \
  -H "X-Note-Token: $TOKEN" \
  -d 'subject_code=CS202' -d 'topic=Binary Tree'

curl -X DELETE localhost:5001/notes/1 -H "X-Note-Token: $TOKEN"
```

| กรณี | Response |
| --- | --- |
| `PATCH` สำเร็จ | `200` + object ของโน้ต (มี `updated_at` ที่เพิ่งอัปเดต) |
| `DELETE` สำเร็จ | `204` ไม่มี body · ลบทั้ง record และไฟล์ใน storage |
| ค่าที่ส่งมาผิดรูป | `400` `{"error": "validation_failed", "fields": {...}}` |
| `PATCH` ที่ไม่มีฟิลด์ให้แก้เลย | `400` `{"error": "no_fields_to_update"}` |
| ไม่ส่ง token หรือ token ผิด | `403` `{"error": "forbidden"}` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` |

แก้ได้เฉพาะ metadata — ตัวไฟล์แก้ไม่ได้ ต้องอัปโหลดใหม่ · ส่ง `uploader_name`,
`created_at` หรือฟิลด์ของไฟล์มาใน `PATCH` จะถูกเมิน ไม่ถือเป็น error ·
ฟิลด์ไม่บังคับ (`topic`, `class_date`, `description`) ล้างค่าได้ด้วยการส่งค่าว่าง


## ตัวอย่างการเรียกใช้

```bash
curl -X POST http://localhost:5001/notes \
  -F 'title=สรุปบทที่ 3' -F 'subject_name=Data Structures' -F 'subject_code=CS201' \
  -F 'faculty=ICT' -F 'year_level=2' -F 'lesson=Linked List' -F 'class_date=2026-08-20' \
  -F 'file=@note.pdf;type=application/pdf'

curl 'http://localhost:5001/notes?faculty=ICT&year_level=2&sort=class_date'
curl -O -J http://localhost:5001/notes/1/download
```

## โครงไฟล์

| ไฟล์ | หน้าที่ |
| --- | --- |
| `app.py` | route ทั้งหมด + app factory (`create_app`) |
| `models.py` | ตาราง `notes` และ session factory |
| `validation.py` | ตรวจ metadata/ไฟล์ — pure function ทดสอบแยกได้ |
| `storage.py` | interface เก็บไฟล์ (ตอนนี้เป็น local disk) |

เทสต์อยู่ที่ [`src/tests/test_notes_validation.py`](../../src/tests/test_notes_validation.py) และ
[`src/tests/test_notes_api.py`](../../src/tests/test_notes_api.py)
