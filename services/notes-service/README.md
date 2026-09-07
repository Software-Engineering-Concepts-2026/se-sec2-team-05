# Notes Service

Service ที่ดูแล metadata และไฟล์ของโน้ต — ทำตาม [US-08 (#8)](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/issues/8)
ขอบเขตและสิ่งที่จงใจยังไม่ทำในรอบนี้อธิบายไว้ใน [ADR-003](../../docs/architecture/adr/0003-tracer-bullet-scope.th.md)

> ⚠️ **ยังไม่มี authentication** — ทุก endpoint เปิดหมด และ `uploader_name` รับมาจากฟอร์มตรง ๆ
> ห้าม deploy ออกสู่สาธารณะก่อน #5/#6 เสร็จ

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
| `GET` | `/notes/<id>/download` | ดาวน์โหลดไฟล์จริง (ตั้งชื่อไฟล์ตามที่ผู้ใช้อัปโหลดมา) |

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
`date_from`, `date_to`, `sort` (`new` | `old` | `class_date` | `title`), `limit` (สูงสุด 100), `offset`

`limit` ถูก clamp ไว้ที่ 1–100 และ `offset` ต่ำสุด 0 ค่าติดลบจึงไม่หลุดไปถึง SQL

ค่าที่ผิดรูปจะได้ `400` (`{"error": "invalid_filter", "field": ...}`) ไม่ใช่ `500`
และ `sort` รับได้เฉพาะค่าใน allowlist เท่านั้น ไม่ได้เอาค่าจาก client ไปต่อเป็น SQL

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
