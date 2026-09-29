# Notes Service

Service ที่ดูแล metadata และไฟล์ของโน้ต — ทำตาม [US-08 (#8)](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/issues/8)
ขอบเขตและสิ่งที่จงใจยังไม่ทำในรอบนี้อธิบายไว้ใน [ADR-003](../../docs/architecture/adr/0003-tracer-bullet-scope.th.md)

> ⚠️ **การอัปโหลดต้อง login แล้ว** (US-31) แต่ endpoint ที่อ่านอย่างเดียวยังเปิดหมด ส่วนการแก้/ลบยังกันด้วย
> edit token ต่อโน้ต ไม่ได้ดูจากบัญชีที่ login (ดู [ADR-004](../../docs/architecture/adr/0004-per-note-edit-token.th.md))
> และ auth-service ยังไม่มีการยืนยันอีเมล ([ADR-005](../../docs/architecture/adr/0005-auth-jwt-with-server-side-sessions.th.md))
> จึงยังห้าม deploy ออกสู่สาธารณะ

## รันในเครื่อง

```bash
docker compose up --build        # ยก Postgres + notes-service (:5001) + auth-service (:5002) + stats-service (:5000)
docker compose down -v           # ลบ volume ด้วย — จำเป็นเมื่อแก้ schema เพราะยังไม่มี migration
```

รันแบบไม่ใช้ Docker (ใช้ SQLite แทน Postgres):

```bash
pip install -r services/notes-service/requirements.txt
NOTES_STORAGE_DIR=./data python services/notes-service/app.py
```

การอัปโหลดต้องมี auth-service รันอยู่ด้วย (ดู [README ของ auth-service](../auth-service/README.md))
ถ้าเรียกไม่ถึง `POST /notes` จะตอบ `503` ส่วน endpoint อื่นใช้ได้ตามปกติ

| Environment variable | ค่า default | ใช้ทำอะไร |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///notes.db` | SQLAlchemy URL — compose ตั้งเป็น `postgresql+psycopg://...` |
| `NOTES_STORAGE_DIR` | `/data/notes` | โฟลเดอร์เก็บไฟล์โน้ต (mount เป็น volume ใน compose) |
| `AUTH_SERVICE_URL` | `http://localhost:5002` | ที่อยู่ของ auth-service ใช้ตรวจ token ตอนอัปโหลด — compose ตั้งเป็น `http://auth-service:5002` |

## API

| Method | Path | คำอธิบาย |
| --- | --- | --- |
| `GET` | `/health` | health check |
| `POST` | `/notes` | อัปโหลดไฟล์ + metadata (`multipart/form-data`) → `201` พร้อม object ของโน้ต — **ต้อง login** (US-31) |
| `GET` | `/notes` | ค้นหา/กรอง → `{ items: [...], count: n }` |
| `GET` | `/notes/<id>` | รายละเอียดโน้ตหนึ่งรายการ |
| `PATCH` | `/notes/<id>` | แก้ metadata บางส่วน — ต้องมี `X-Note-Token` (US-19) |
| `DELETE` | `/notes/<id>` | ลบโน้ตพร้อมไฟล์ — ต้องมี `X-Note-Token` (US-20) → `204` |
| `GET` | `/notes/<id>/download` | ดาวน์โหลดไฟล์จริง (ตั้งชื่อไฟล์ตามที่ผู้ใช้อัปโหลดมา) และนับยอดดาวน์โหลด (US-12) |
| `GET` | `/notes/<id>/preview` | รูปตัวอย่างของโน้ต (PNG) ดูได้โดยไม่ต้องดาวน์โหลดไฟล์เต็ม ไม่นับ `download_count` (US-11) |

### `POST /notes`

ต้องส่ง header `Authorization: Bearer <access_token>` ที่ได้จาก `POST /auth/login` ของ auth-service
notes-service ส่ง header นี้ต่อไปตรวจที่ `GET /auth/me` (ตามที่ ADR-005 กำหนด ไม่ได้ถือ secret เอง)
จึงรู้ทันทีถ้า token ถูก logout ไปแล้ว · ตรวจตัวตน**ก่อน**อ่านฟอร์มและไฟล์ ถ้าไม่ผ่านจะไม่มีอะไรถูกบันทึก

| ฟิลด์ | บังคับ | หมายเหตุ |
| --- | --- | --- |
| `file` | ✅ | PDF / PNG / JPEG เท่านั้น ไม่เกิน 20 MB |
| `title` | ✅ | ชื่อโน้ต |
| `subject_name`, `subject_code`, `faculty`, `lesson` | ✅ | ข้อความ |
| `year_level` | ✅ | ตัวเลข 1–8 |
| `topic`, `class_date`, `description` | — | `class_date` เป็น `YYYY-MM-DD` |

**ชื่อผู้อัปโหลดมาจากบัญชีที่ login เสมอ** (US-31) — `uploader_name` ในโน้ตคือ `display_name` ของบัญชี
ณ ตอนอัปโหลด ถ้าฟอร์มส่ง `uploader_name` มาด้วยจะถูกเมิน ไม่ถือเป็น error · ระบบเก็บ id ของบัญชีไว้ใน
คอลัมน์ `uploader_id` ด้วย เพื่อให้เปลี่ยนไปเช็คความเป็นเจ้าของจากบัญชีได้ในอนาคต (ADR-004) แต่ยังไม่ส่งออกใน API

| กรณี | Response |
| --- | --- |
| ไม่มี token, token ผิด/หมดอายุ หรือ logout ไปแล้ว | `401` `{"error": "unauthorized"}` + header `WWW-Authenticate: Bearer` |
| เรียก auth-service ไม่ถึงหรือตอบผิดปกติ (timeout 3 วินาที) | `503` `{"error": "auth_unavailable"}` — ไม่ใช่ 401 เพราะ token อาจยังใช้ได้ |

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
- นับต่อ request ที่ดาวน์โหลดสำเร็จ ยังไม่ตัดซ้ำรายผู้ใช้ เพราะการดาวน์โหลดยังไม่ต้อง login จึงไม่รู้ว่าใครโหลด
- ตาราง `notes` มีคอลัมน์ `download_count` เพิ่มมา ยังไม่มี migration จึงต้อง `docker compose down -v` ตอนอัปเดต schema
  (คอลัมน์ `uploader_id` ของ US-31 ก็เช่นกัน)

### `GET /notes/<id>/preview` — ดูตัวอย่างก่อนดาวน์โหลด (US-11)

ตอบเป็นรูป PNG กว้างไม่เกิน 800px (ไม่ขยายรูปที่เล็กอยู่แล้ว) แสดงผลแบบ inline พร้อม
`Cache-Control: public, max-age=86400` ไม่ใช่ `attachment` เหมือน `/download` และ**ไม่นับ `download_count`**
เพราะเป็นการดูตัวอย่างไม่ใช่การโหลดไฟล์เต็ม

รูปแบบไฟล์ต้นฉบับ:

- **PNG / JPEG** — decode ตรง ๆ แล้วย่อขนาด
- **PDF** — render เฉพาะหน้าแรกด้วย pypdfium2 (สเกลให้กว้างไม่เกิน 800px, ~144 dpi สำหรับหน้าขนาดเล็ก)

ตัวอย่างจะ render แค่ครั้งแรกที่มีคนขอ แล้วแคชไว้ใน storage ใต้ `previews/` คำขอครั้งถัดไปเสิร์ฟจากแคชโดยไม่
render ซ้ำ และไฟล์ตัวอย่างจะถูกลบตามเมื่อโน้ตต้นฉบับถูก `DELETE`

เนื้อไฟล์ถูกตรวจด้วย Pillow/pypdfium2 จริง ไม่เชื่อแค่ mimetype ที่ผู้ใช้ส่งตอนอัปโหลด (ต่างจาก validation
ตอน `POST /notes` ที่เชื่อ mimetype) — ไฟล์เสีย/เนื้อไม่ตรงชนิด/ใหญ่ผิดปกติ (กัน decompression bomb) ตอบ `422`
แทนที่จะหลุดเป็น `500`

| กรณี | Response |
| --- | --- |
| render สำเร็จ | `200` + รูป `image/png` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` |
| มี record แต่ไฟล์หายจาก storage | `404` `{"error": "file_not_found"}` |
| ไฟล์เสีย/ชนิดไม่ตรง/ยังไม่รองรับ/ใหญ่ผิดปกติ | `422` `{"error": "preview_unavailable"}` |

response ของโน้ต (`GET /notes`, `GET /notes/<id>`) มีฟิลด์ `preview_url` ชี้มาที่ endpoint นี้เสมอ

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

การแก้/ลบ**ยังไม่ได้ดูจากบัญชีที่ login** — login อยู่แต่ไม่มี edit token ก็ได้ `403` เหมือนเดิม

แก้ได้เฉพาะ metadata — ตัวไฟล์แก้ไม่ได้ ต้องอัปโหลดใหม่ · ส่ง `uploader_name`, `uploader_id`,
`created_at` หรือฟิลด์ของไฟล์มาใน `PATCH` จะถูกเมิน ไม่ถือเป็น error ·
ฟิลด์ไม่บังคับ (`topic`, `class_date`, `description`) ล้างค่าได้ด้วยการส่งค่าว่าง


## ตัวอย่างการเรียกใช้

```bash
# login ที่ auth-service ก่อน (สมัครด้วย POST /auth/register ถ้ายังไม่มีบัญชี)
TOKEN=$(curl -s -X POST localhost:5002/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"67026168@up.ac.th","password":"correct horse"}' | jq -r .access_token)

curl -X POST http://localhost:5001/notes -H "Authorization: Bearer $TOKEN" \
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
| `identity.py` | ตรวจ Bearer token ผ่าน `GET /auth/me` ของ auth-service — `create_app(identity=...)` ส่งตัวปลอมเข้ามาแทนในเทสต์ได้ |
| `models.py` | ตาราง `notes` และ session factory |
| `validation.py` | ตรวจ metadata/ไฟล์ — pure function ทดสอบแยกได้ |
| `storage.py` | interface เก็บไฟล์ (ตอนนี้เป็น local disk) |
| `preview.py` | สร้างรูปตัวอย่าง (PNG/PDF → PNG) — pure function ทดสอบแยกได้เหมือน `validation.py` (US-11) |

เทสต์อยู่ที่ [`src/tests/test_notes_validation.py`](../../src/tests/test_notes_validation.py),
[`src/tests/test_notes_api.py`](../../src/tests/test_notes_api.py),
[`src/tests/test_notes_identity.py`](../../src/tests/test_notes_identity.py) (คุยกับ auth-service ตัวจริงผ่าน HTTP) และ
[`src/tests/test_notes_preview.py`](../../src/tests/test_notes_preview.py)
