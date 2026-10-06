# Notes Service

Service ที่ดูแล metadata และไฟล์ของโน้ต — ทำตาม [US-08 (#8)](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/issues/8)
ขอบเขตและสิ่งที่จงใจยังไม่ทำในรอบนี้อธิบายไว้ใน [ADR-003](../../docs/architecture/adr/0003-tracer-bullet-scope.th.md)

> ⚠️ **การอัปโหลดต้อง login แล้ว** (US-31) แต่ endpoint ที่อ่านอย่างเดียวยังเปิดหมด ส่วนการแก้/ลบใช้ได้ทั้ง
> edit token ต่อโน้ต ([ADR-004](../../docs/architecture/adr/0004-per-note-edit-token.th.md)) และบัญชีเจ้าของที่ login อยู่
> ([ADR-008](../../docs/architecture/adr/0008-owner-login-for-note-changes.th.md)) และ auth-service ยังไม่มีการยืนยันอีเมล ([ADR-005](../../docs/architecture/adr/0005-auth-jwt-with-server-side-sessions.th.md))
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

การอัปโหลด รายการโปรด และการขอบคุณต้องมี auth-service รันอยู่ด้วย (ดู [README ของ auth-service](../auth-service/README.md))
ถ้าเรียกไม่ถึง `POST /notes`, endpoint ของรายการโปรด และ `POST /notes/<id>/thanks` จะตอบ `503` ส่วน endpoint อ่านอย่างเดียวใช้ได้ตามปกติ
(`is_favorited` และ `thank_status` จะเป็น `null` ระหว่างนั้น)

| Environment variable | ค่า default | ใช้ทำอะไร |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///notes.db` | SQLAlchemy URL — compose ตั้งเป็น `postgresql+psycopg://...` · URL แบบ `postgres://`/`postgresql://` (Neon บน Vercel) ถูกแปลงให้ใช้ psycopg 3 เอง |
| `NOTES_STORAGE_DIR` | `/data/notes` | โฟลเดอร์เก็บไฟล์โน้ต (mount เป็น volume ใน compose) |
| `NOTES_STORAGE_BACKEND` | `local` | `blob` = เก็บไฟล์ใน Vercel Blob แบบ private แทนดิสก์ (ADR-009) ต้องมี `BLOB_READ_WRITE_TOKEN` ด้วย |
| `AUTH_SERVICE_URL` | `http://localhost:5002` | ที่อยู่ของ auth-service ใช้ตรวจ token ตอนอัปโหลด ใช้รายการโปรด และขอบคุณเจ้าของโน้ต — compose ตั้งเป็น `http://auth-service:5002` |
| `ADMIN_USER_IDS` | ว่าง | comma-separated user IDs ที่จัดการรายงานได้ เช่น `99,100` — ไม่มีค่าแปลว่าไม่มี admin |

## API

| Method | Path | คำอธิบาย |
| --- | --- | --- |
| `GET` | `/health` | health check |
| `POST` | `/notes` | อัปโหลดไฟล์ + metadata (`multipart/form-data`) → `201` พร้อม object ของโน้ต — **ต้อง login** (US-31) |
| `GET` | `/notes` | ค้นหา/กรอง → `{ items: [...], count: n }` |
| `GET` | `/notes/favorites` | รายการโปรดของตัวเอง เรียงที่เพิ่งบันทึกก่อน — **ต้อง login** (US-15) |
| `GET` | `/notes/mine` | โน้ตที่ตัวเองอัปโหลด ใหม่สุดก่อน พร้อม `summary` ยอดรวม — **ต้อง login** (Issue #82) |
| `GET` | `/notes/<id>` | รายละเอียดโน้ตหนึ่งรายการ |
| `POST` | `/notes/<id>/reports` | รายงานโน้ตด้วย JSON `{"reason": "..."}` → `201` — ต้อง login และรายงานซ้ำต่อโน้ตได้ครั้งเดียว (Issue #17) |
| `GET` | `/reports` | ดูรายงานพร้อมข้อมูลโน้ต เหตุผล และผู้รายงาน เรียงใหม่ไปเก่า — ต้องเป็น admin (Issue #17) |
| `DELETE` | `/reports/<report_id>` | ปฏิเสธ/ปิดรายงาน โดยลบเฉพาะ Report และเก็บ Note ไว้ → `204` — ต้องเป็น admin (Issue #17) |
| `DELETE` | `/reports/<report_id>/note` | ลบ Note ที่ถูกรายงานพร้อมไฟล์และรายงานที่ผูกอยู่ผ่าน cascade → `204` — ต้องเป็น admin (Issue #18) |
| `POST` | `/notes/<id>/comments` | แสดงความคิดเห็นใต้โน้ต — ต้อง login และส่ง JSON `{"content": "..."}` → `201` (Issue #14) |
| `GET` | `/notes/<id>/comments` | แสดงความคิดเห็นของโน้ต เรียงจากใหม่ไปเก่า (Issue #14) |
| `DELETE` | `/notes/<id>/comments/<comment_id>` | ลบความคิดเห็นของตัวเอง — ต้อง login → `204` (Issue #14) |
| `POST` | `/notes/<id>/favorite` | บันทึกเข้ารายการโปรด → `201` (ครั้งแรก) / `200` (มีอยู่แล้ว) — **ต้อง login** (US-15) |
| `DELETE` | `/notes/<id>/favorite` | เอาออกจากรายการโปรด → `204` — **ต้อง login** (US-15) |
| `POST` | `/notes/<id>/thanks` | ขอบคุณเจ้าของโน้ต → `201` (ครั้งแรก) / `200` (กดซ้ำ) — **ต้อง login** กดได้ครั้งเดียวต่อโน้ต (US-28) |
| `PATCH` | `/notes/<id>` | แก้ metadata บางส่วน — ต้องมี `X-Note-Token` หรือ login เป็นเจ้าของ (US-19, ADR-008) |
| `DELETE` | `/notes/<id>` | ลบโน้ตพร้อมไฟล์ — ต้องมี `X-Note-Token` หรือ login เป็นเจ้าของ (US-20, ADR-008) → `204` |
| `GET` | `/notes/<id>/download` | ดาวน์โหลดไฟล์จริง (ตั้งชื่อไฟล์ตามที่ผู้ใช้อัปโหลดมา) และนับยอดดาวน์โหลด (US-12) |
| `GET` | `/notes/<id>/preview` | รูปตัวอย่างของโน้ต (PNG) ดูได้โดยไม่ต้องดาวน์โหลดไฟล์เต็ม ไม่นับ `download_count` (US-11) |

### ให้คะแนนโน้ต (Issue #13)

`GET /notes` และ `GET /notes/<id>` ใส่ `average_rating` กับ `rating_count` ใน object โน้ต
เพื่อให้ผู้ใช้ทุกคนเห็นคะแนนเฉลี่ยและจำนวนผู้ให้คะแนน โน้ตที่ยังไม่มีคะแนนคืน
`average_rating: null` และ `rating_count: 0` ค่าเฉลี่ยถูกปัดเป็นทศนิยมสองตำแหน่ง
ส่วน `GET /notes/<id>` จะเพิ่ม `can_rate: true` และ `user_rating` เฉพาะเมื่อระบุตัวสมาชิกได้
(`user_rating` เป็น `null` หากยังไม่เคยให้คะแนน)

`GET /notes/<id>` ยังคงเปิดสาธารณะเหมือนเดิม หากเรียกพร้อม token ที่ตรวจสอบได้ จะบันทึกสิทธิ์
ให้สมาชิกคนนั้นให้คะแนนโน้ตได้ การดาวน์โหลดด้วย `GET /notes/<id>/download` พร้อม token
ที่ตรวจสอบได้ก็บันทึกสิทธิ์เช่นกัน การเปิดหรือดาวน์โหลดแบบไม่ login จะไม่สร้างสิทธิ์

ส่งคะแนนด้วย `PUT /notes/<id>/rating` โดยต้อง login และเคยเปิดหรือดาวน์โหลดโน้ตขณะ login:

```json
{"rating": 4}
```

คะแนนต้องเป็น integer ตั้งแต่ 1 ถึง 5 สมาชิกมีคะแนนเดียวต่อโน้ต; การส่งซ้ำจะอัปเดตคะแนนเดิม
และคืน `200` พร้อม `{ "note_id", "rating", "average_rating", "rating_count" }`
การมีสิทธิ์และคะแนนถูกเก็บในตารางใหม่ที่ `models.py` สร้างผ่าน `create_all` ตามรูปแบบเดิม
ไม่ต้องลบ database volume เพื่อเพิ่มตารางเหล่านี้

| กรณี | Response |
| --- | --- |
| ให้คะแนนหรือแก้คะแนนสำเร็จ | `200` + คะแนนของสมาชิกและค่าเฉลี่ยล่าสุด |
| ไม่มี token หรือ token ใช้ไม่ได้ | `401` `{"error": "unauthorized"}` |
| auth-service ไม่พร้อมใช้งาน | `503` `{"error": "auth_unavailable"}` |
| body ไม่ใช่ object หรือคะแนนไม่ใช่ integer 1–5 | `400` `{"error": "validation_failed", "fields": {"rating": ...}}` |
| โน้ตไม่มีอยู่ | `404` `{"error": "not_found"}` |
| สมาชิกยังไม่เคยเปิด/ดาวน์โหลดโน้ตขณะ login | `403` `{"error": "not_eligible"}` |

### `POST /notes`

ต้องส่ง header `Authorization: Bearer <access_token>` ที่ได้จาก `POST /auth/login` ของ auth-service
notes-service ส่ง header นี้ต่อไปตรวจที่ `GET /auth/me` (ตามที่ ADR-005 กำหนด ไม่ได้ถือ secret เอง)
จึงรู้ทันทีถ้า token ถูก logout ไปแล้ว · ตรวจตัวตน**ก่อน**อ่านฟอร์มและไฟล์ ถ้าไม่ผ่านจะไม่มีอะไรถูกบันทึก

| ฟิลด์ | บังคับ | หมายเหตุ |
| --- | --- | --- |
| `file` | ✅ | PDF / PNG / JPEG เท่านั้น ไม่เกิน 4 MB |
| `title` | ✅ | ชื่อโน้ต |
| `subject_name`, `subject_code`, `faculty`, `lesson` | ✅ | ข้อความ |
| `year_level` | ✅ | ตัวเลข 1–8 |
| `topic`, `class_date`, `description` | — | `class_date` เป็น `YYYY-MM-DD` |

**ชื่อผู้อัปโหลดมาจากบัญชีที่ login เสมอ** (US-31) — `uploader_name` ในโน้ตคือ `display_name` ของบัญชี
ณ ตอนอัปโหลด ถ้าฟอร์มส่ง `uploader_name` มาด้วยจะถูกเมิน ไม่ถือเป็น error · ระบบเก็บ id ของบัญชีไว้ใน
คอลัมน์ `uploader_id` ด้วย ซึ่งใช้เช็คความเป็นเจ้าของตอนแก้/ลบ (ADR-008) และกรอง `GET /notes/mine` แต่ไม่ส่งออกใน API

| กรณี | Response |
| --- | --- |
| ไม่มี token, token ผิด/หมดอายุ หรือ logout ไปแล้ว | `401` `{"error": "unauthorized"}` + header `WWW-Authenticate: Bearer` |
| เรียก auth-service ไม่ถึงหรือตอบผิดปกติ (timeout 3 วินาที) | `503` `{"error": "auth_unavailable"}` — ไม่ใช่ 401 เพราะ token อาจยังใช้ได้ |

ถ้า validate ไม่ผ่านจะได้ `400` พร้อมรายการ error **ครบทุกฟิลด์ในครั้งเดียว** ไม่ได้หยุดที่ตัวแรก

```json
{ "error": "validation_failed", "fields": { "subject_code": "จำเป็นต้องกรอก", "year_level": "ต้องเป็นตัวเลข" } }
```

request ที่ใหญ่เกิน 4 MB + 256 KB (ไฟล์ 4 MB + ที่เผื่อให้ multipart/metadata) จะถูกตัดตั้งแต่ชั้น Werkzeug
และได้ `413` ที่มีรูปร่าง JSON เดียวกัน — ไม่ต้องรอให้อ่าน body เข้ามาครบก่อนถึงจะปฏิเสธ

### `GET /notes` — query parameters

`q` (ค้นในชื่อ/วิชา/รหัส/บทเรียน/หัวข้อ), `faculty`, `subject_code`, `year_level`,
`file_type` (`pdf` | `png` | `jpg`), `topic`, `date_from`, `date_to`,
`sort` (`new` | `old` | `class_date` | `title` | `rating`), `limit` (สูงสุด 100), `offset`

`file_type` ส่งซ้ำได้หลายค่าเพื่อกรองแบบ OR เช่น `?file_type=pdf&file_type=png` (US-10)
ค่าที่รับมาจาก client เป็นนามสกุลสั้น แล้วแปลงเป็น content type ผ่าน allowlist ของ `validation.py`
ถ้ามีค่าใดไม่อยู่ใน allowlist จะปฏิเสธทั้งชุดด้วย `400` ไม่ใช่กรองเฉพาะค่าที่ถูก

`topic` กรองเฉพาะคอลัมน์ `topic` แบบ partial match ไม่สนตัวพิมพ์เล็ก/ใหญ่ (US-26) — ต่างจาก `q`
ที่ค้นหลายคอลัมน์พร้อมกันรวมถึง `topic` ด้วย ใช้ `topic` เมื่อต้องการกรองเฉพาะหัวข้อเลกเชอร์เท่านั้น
โน้ตที่ไม่ได้ระบุ `topic` ตอนอัปโหลด (ฟิลด์นี้ไม่บังคับ) จะไม่ถูกนับเมื่อใช้ตัวกรองนี้

`date_from`/`date_to` เป็นช่วงแบบ inclusive ทั้งสองขอบ เทียบกับ `class_date` เท่านั้น (ไม่มีระดับเวลา)
ส่งมาฝั่งเดียวก็ได้ (เท่ากับไม่จำกัดฝั่งนั้น) ส่งค่าเดียวกันทั้งคู่เพื่อกรองวันเดียว ถ้า `date_from` มาหลัง
`date_to` จะได้ `400 {"error": "invalid_filter", "field": "date_to"}` โน้ตที่ไม่ได้ระบุ `class_date`
จะไม่ถูกนับเมื่อใช้ตัวกรองนี้เช่นกัน (หาเจอได้ด้วย `q` หรือตัวกรองอื่นตามปกติ)

ทุกตัวกรองต่อกันด้วย AND ใช้พร้อมกันได้ทั้งหมด (US-10 + US-26)

`sort=rating` (Issue #83) เรียงคะแนนเฉลี่ยมากไปน้อย โน้ตที่ยังไม่มีใครให้คะแนนอยู่ท้ายสุด ·
คะแนนเฉลี่ยเท่ากันให้โน้ตที่มีคนให้คะแนนมากกว่าขึ้นก่อน แล้วค่อยดูว่าใหม่กว่า · ใช้กับตัวกรองอื่นได้ตามปกติ

`limit` ถูก clamp ไว้ที่ 1–100 และ `offset` ต่ำสุด 0 ค่าติดลบจึงไม่หลุดไปถึง SQL

ค่าที่ผิดรูปจะได้ `400` (`{"error": "invalid_filter", "field": ...}`) ไม่ใช่ `500`
และ `sort` รับได้เฉพาะค่าใน allowlist เท่านั้น ไม่ได้เอาค่าจาก client ไปต่อเป็น SQL

### รายการโปรด (US-15)

สมาชิกที่ login แล้วบันทึกโน้ตไว้อ่านทีหลังได้ ทุก endpoint ต้องส่ง `Authorization: Bearer <access_token>`
เหมือน `POST /notes` และ**เจ้าของรายการมาจาก token เสมอ** ไม่รับ user id จาก URL หรือ body จึงแตะรายการของคนอื่นไม่ได้

| Method | Path | ผลลัพธ์ |
| --- | --- | --- |
| `POST` | `/notes/<id>/favorite` | ครั้งแรก `201`, กดซ้ำ `200` (ไม่เกิดแถวซ้ำ) · body `{"note_id", "is_favorited": true, "favorited_at"}` |
| `DELETE` | `/notes/<id>/favorite` | `204` ทั้งกรณีเอาออกสำเร็จและกรณีโน้ตไม่ได้อยู่ในรายการอยู่แล้ว |
| `GET` | `/notes/favorites` | `200 {"items": [...], "count": n}` — ว่างได้ `{"items": [], "count": 0}` |

| กรณี | Response |
| --- | --- |
| ไม่มี token, token ผิด/หมดอายุ หรือ logout ไปแล้ว | `401` `{"error": "unauthorized"}` |
| เรียก auth-service ไม่ถึง | `503` `{"error": "auth_unavailable"}` |
| `POST`/`DELETE` กับโน้ตที่ไม่มีอยู่ | `404` `{"error": "not_found"}` |

- **บันทึกโน้ตของตัวเองได้** ไม่มีข้อจำกัดว่าต้องเป็นโน้ตของคนอื่น
- **`GET /notes/favorites`** แสดงเฉพาะของตัวเอง เรียง `favorited_at` ล่าสุดก่อน ทุก item เป็น object ของโน้ตเดิม
  บวก `is_favorited: true` และ `favorited_at` · รับ `limit`/`offset` กติกา clamp เดียวกับ `GET /notes`
  (`limit` 1–100, `offset` ต่ำสุด 0, ค่าที่ไม่ใช่ตัวเลขได้ `400`)
- **แยกจากผลค้นหา** — `GET /notes` ไม่ถูกกรองด้วยรายการโปรด ยังคืนโน้ตทั้งหมดตามตัวกรองเหมือนเดิม
- **โน้ตที่เจ้าของลบแล้ว (US-20)** ไม่แสดงในรายการ — ตอนอ่าน JOIN กับ `notes` ไม่ได้ไปแก้ `DELETE /notes/<id>`
  เพราะ SQLite ไม่บังคับ cascade ถ้าไม่เปิดเอง แถวใน `favorites` ที่ค้างอยู่จึงไม่มีผลต่อสิ่งที่ผู้ใช้เห็น
- **`is_favorited` ในโน้ตแต่ละรายการ** (`GET /notes`, `GET /notes/<id>`):

  | ผู้เรียก | ค่า |
  | --- | --- |
  | login แล้ว | `true` / `false` ตามรายการโปรดของตัวเอง |
  | ไม่ login หรือ token ใช้ไม่ได้ | `null` (UI ควรชวน login แทนการแสดงปุ่ม ★) |
  | auth-service ล่ม | `null` — การค้นหายังใช้ได้ (`200`) ไม่กลายเป็น `503` |

  ดึงสถานะของทั้งหน้าด้วย query เดียว (`note_id IN (...)`) ไม่ query ทีละโน้ต · ถ้าไม่มี header `Authorization`
  เลยจะไม่เรียก auth-service เลย endpoint อ่านอย่างเดียวจึงยังไม่พึ่ง auth-service เหมือนเดิม
- ตาราง `favorites` เป็นตารางใหม่ (`user_id`, `note_id`, `created_at`, unique `(user_id, note_id)`) สร้างให้อัตโนมัติ
  ไม่ต้อง `docker compose down -v` · `user_id` ไม่ใช่ foreign key เพราะตาราง users เป็นของ auth-service (ADR-005)
  เหตุผลเดียวกับ `uploader_id`
- ยังไม่มีจำนวนคนที่บันทึกต่อโน้ต (`favorite_count`) — ตัดออกจากขอบเขตของ US-15

```bash
curl -X POST   http://localhost:5001/notes/1/favorite -H "Authorization: Bearer $TOKEN"   # 201 ครั้งแรก, 200 ถ้าซ้ำ
curl           http://localhost:5001/notes/favorites -H "Authorization: Bearer $TOKEN"
curl -X DELETE http://localhost:5001/notes/1/favorite -H "Authorization: Bearer $TOKEN"   # 204
```

### `GET /notes/mine` — โน้ตของฉัน (Issue #82)

ต้องส่ง `Authorization: Bearer <access_token>` · เจ้าของรายการมาจาก token เสมอ ไม่รับ user id จาก URL
· รับ `limit`/`offset` กติกาเดียวกับ `GET /notes` · เรียงที่อัปโหลดล่าสุดก่อน

```json
{
  "items": [{ "id": 7, "title": "...", "view_count": 12, "download_count": 4,
              "average_rating": 4.5, "rating_count": 2, "thank_count": 1, "...": "..." }],
  "count": 1,
  "summary": { "note_count": 3, "total_views": 30, "total_downloads": 9,
               "total_thanks": 2, "average_rating": 4.25, "rating_count": 4 }
}
```

- **`items`** เป็น object ของโน้ตแบบเดียวกับ `GET /notes` บวก `thank_count` (จำนวนคำขอบคุณของโน้ตนั้น
  ไม่บอกว่าใครกด เหมือน stats-service ใน US-28 AC3) · ไม่มี `edit_token`
- **`summary`** นับจาก**โน้ตทั้งหมด**ของผู้ใช้ ไม่ใช่แค่หน้าที่ส่งกลับ · `average_rating` เฉลี่ยจากคะแนนทุกครั้ง
  ที่ได้รับ (โน้ตที่มีคนให้คะแนนมากมีน้ำหนักมากกว่า) เป็น `null` ถ้ายังไม่มีใครให้คะแนนเลย
- ไม่ login / token ใช้ไม่ได้ → `401` · auth-service ล่ม → `503` · `limit`/`offset` ไม่ใช่ตัวเลข → `400`

### ขอบคุณเจ้าของโน้ต (US-28)

สมาชิกที่ login แล้วกดขอบคุณเจ้าของโน้ตได้ เป็นปุ่มกดอย่างเดียว **ไม่มีข้อความ** (อยากเขียนถึงเจ้าของให้ใช้คอมเมนต์ของ Issue #14)
ต้องส่ง `Authorization: Bearer <access_token>` เหมือน `POST /notes` และผู้ขอบคุณมาจาก token เสมอ ไม่รับ user id จาก body

`POST /notes/<id>/thanks` — ไม่ต้องมี body

| กรณี | Response |
| --- | --- |
| ขอบคุณครั้งแรก | `201` `{"note_id", "thanked": true, "thanked_at"}` |
| กดซ้ำ | `200` body เดิม (`thanked_at` ไม่เปลี่ยน) · ไม่เกิดแถวซ้ำ ยอดไม่เพิ่ม |
| ไม่มี token, token ผิด/หมดอายุ หรือ logout ไปแล้ว | `401` `{"error": "unauthorized"}` |
| เรียก auth-service ไม่ถึง | `503` `{"error": "auth_unavailable"}` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` |
| ขอบคุณโน้ตของตัวเอง | `403` `{"error": "own_note"}` |

- **กดได้ครั้งเดียวต่อโน้ตต่อผู้ใช้ และยกเลิกไม่ได้** — ไม่มี `DELETE` (ได้ `405`) ตาราง `thanks` มี unique `(user_id, note_id)`
  กันแถวซ้ำแม้กดพร้อมกันสองครั้ง
- **"หลังดาวน์โหลด" เป็นเงื่อนไขของ UI** — ให้หน้าเว็บแสดงปุ่มหลังดาวน์โหลดสำเร็จ API ไม่ได้ตรวจเพราะระบบไม่ได้เก็บว่าใครดาวน์โหลดอะไร
  (`download_count` เป็นยอดรวม และการดาวน์โหลดไม่ต้อง login) ตอนนี้หน้าเว็บยังไม่มีปุ่มนี้ ใช้ได้ผ่าน API เท่านั้น
- **ไม่เปิดเผยตัวผู้ขอบคุณ** — notes-service ไม่มี endpoint ที่คืนรายชื่อหรือยอดขอบคุณ
- **เจ้าของลบโน้ต (US-20)** — `DELETE /notes/<id>` ลบแถว `thanks` ของโน้ตนั้นใน transaction เดียวกับตัวโน้ต
- **`thank_status` ในโน้ตแต่ละรายการ** (`GET /notes`, `GET /notes/<id>`):

  | ผู้เรียก | ค่า |
  | --- | --- |
  | ไม่ login หรือ token ใช้ไม่ได้ | `null` |
  | auth-service ล่ม | `null` — การค้นหายังใช้ได้ (`200`) ไม่กลายเป็น `503` |
  | เป็นเจ้าของโน้ต | `"own_note"` |
  | ขอบคุณไปแล้ว | `"thanked"` |
  | login แล้วยังไม่ได้ขอบคุณ | `"can_thank"` |

  ดึงสถานะของทั้งหน้าด้วย query เดียว (`note_id IN (...)`) ไม่ query ทีละโน้ต เหมือน `is_favorited`
- ตาราง `thanks` เป็นตารางใหม่ (`user_id`, `note_id`, `created_at`, unique `(user_id, note_id)`) สร้างให้อัตโนมัติ
  ไม่ต้อง `docker compose down -v` · `user_id` ไม่ใช่ foreign key เหตุผลเดียวกับ `favorites`

```bash
curl -X POST http://localhost:5001/notes/1/thanks -H "Authorization: Bearer $TOKEN"   # 201 ครั้งแรก, 200 ถ้าซ้ำ
```

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

### `PATCH /notes/<id>` และ `DELETE /notes/<id>` — edit token หรือบัญชีเจ้าของ

ยืนยันความเป็นเจ้าของได้สองทาง ทางใดทางหนึ่งก็พอ:

1. **edit token** (ADR-004) — ตอน `POST /notes` สำเร็จ response จะมีฟิลด์ `edit_token` เพิ่มมา **ครั้งเดียวเท่านั้น**
   ฐานข้อมูลเก็บแค่ hash และไม่มี endpoint ไหนคืนค่านี้ให้อีก ส่งมาใน header `X-Note-Token`
2. **login เป็นบัญชีที่อัปโหลดโน้ตนั้น** (ADR-008, Issue #82) — ส่ง `Authorization: Bearer <access_token>`
   ไม่ต้องมี edit token ทำ token หายก็ยังแก้/ลบได้ถ้า login เป็นเจ้าของ

token ถูกตรวจก่อน ถ้าใช้ได้จะไม่เรียก auth-service เลย จึงยังแก้/ลบได้แม้ auth-service ล่ม

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
| ไม่ส่งทั้ง token และ `Authorization` หรือ token ผิดและไม่ได้ login | `403` `{"error": "forbidden"}` |
| login อยู่แต่ไม่ใช่เจ้าของ (และไม่มี token ที่ถูก) | `403` `{"error": "forbidden"}` |
| ส่ง Bearer ที่ใช้ไม่ได้/หมดอายุ (และไม่มี token ที่ถูก) | `401` `{"error": "unauthorized"}` + `WWW-Authenticate: Bearer` |
| ไม่มี token ที่ถูก และเรียก auth-service ไม่ถึง | `503` `{"error": "auth_unavailable"}` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` — ตรวจก่อนเรื่องสิทธิ์ |

```bash
# เจ้าของที่ login อยู่ ไม่ต้องมี edit token
curl -X PATCH  localhost:5001/notes/1 -H "Authorization: Bearer $ACCESS_TOKEN" -d 'topic=Heap'
curl -X DELETE localhost:5001/notes/1 -H "Authorization: Bearer $ACCESS_TOKEN"
```

แก้ได้เฉพาะ metadata — ตัวไฟล์แก้ไม่ได้ ต้องอัปโหลดใหม่ · ส่ง `uploader_name`, `uploader_id`,
`created_at` หรือฟิลด์ของไฟล์มาใน `PATCH` จะถูกเมิน ไม่ถือเป็น error ·
ฟิลด์ไม่บังคับ (`topic`, `class_date`, `description`) ล้างค่าได้ด้วยการส่งค่าว่าง

### `POST /notes/<id>/comments` — แสดงความคิดเห็นใต้โน้ต (Issue #14)

ต้อง login ก่อน โดยส่ง header `Authorization: Bearer <access_token>` ที่ได้จาก auth-service
notes-service ส่ง token ต่อไปตรวจที่ `GET /auth/me` ตาม ADR-005 โดยไม่ได้ถือ JWT secret เอง

Request body เป็น JSON:

```json
{
  "content": "ขอบคุณสำหรับสรุปครับ ตรงส่วนนี้มีตัวอย่างเพิ่มเติมไหมครับ?"
}
```

ข้อความจะถูก `strip` ช่องว่างหัวและท้ายก่อนบันทึก และต้องมีความยาว 1–1000 ตัวอักษร

| กรณี | Response |
| --- | --- |
| สร้างความคิดเห็นสำเร็จ | `201` + object ของ comment |
| ไม่มี token หรือ token ไม่ถูกต้อง | `401` `{"error": "unauthorized"}` |
| เรียก auth-service ไม่ถึง | `503` `{"error": "auth_unavailable"}` |
| body ไม่ใช่ JSON object | `400` `{"error": "invalid_json"}` |
| `content` ว่างหรือยาวเกิน 1000 ตัวอักษร | `400` `{"error": "invalid_comment"}` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` |

### `GET /notes/<id>/comments` — ดูความคิดเห็น (Issue #14)

แสดงความคิดเห็นทั้งหมดของโน้ต โดยเรียงจากเวลาล่าสุดไปเก่าสุด

| กรณี | Response |
| --- | --- |
| สำเร็จ | `200` `{ "comments": [...] }` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` |

### `DELETE /notes/<id>/comments/<comment_id>` — ลบความคิดเห็นของตัวเอง (Issue #14)

ต้อง login และสามารถลบได้เฉพาะความคิดเห็นที่เป็นของบัญชีที่ login อยู่เท่านั้น

| กรณี | Response |
| --- | --- |
| ลบสำเร็จ | `204` ไม่มี body |
| ไม่มี token หรือ token ไม่ถูกต้อง | `401` `{"error": "unauthorized"}` |
| ไม่พบความคิดเห็นหรือความคิดเห็นไม่ได้อยู่ใต้โน้ตนี้ | `404` `{"error": "not_found"}` |
| ความคิดเห็นเป็นของผู้ใช้อื่น | `403` `{"error": "forbidden"}` |

ความคิดเห็นถูกเก็บในฐานข้อมูลและผูกกับ `note_id` โดยตรง เมื่อลบโน้ต ระบบจะลบความคิดเห็นของโน้ตนั้นก่อนลบ record ของโน้ต เพื่อไม่ให้มีความคิดเห็นตกค้างในฐานข้อมูล

### รายงานเนื้อหา (Issue #17)

สมาชิกที่ login แล้วรายงานโน้ตได้ด้วย `POST /notes/<id>/reports` โดยส่ง JSON `{"reason": "..."}`
เหตุผลถูกตัดช่องว่างหัวท้ายและจำกัดไม่เกิน 500 ตัวอักษร ผู้ใช้หนึ่งคนรายงานโน้ตเดิมซ้ำไม่ได้:
service ตรวจสอบก่อนบันทึก และฐานข้อมูลบังคับ unique `(reporter_id, note_id)` เพื่อกัน request ที่เข้าพร้อมกัน

#### `POST /notes/<id>/reports`

| กรณี | Response |
| --- | --- |
| สำเร็จ | `201` + report |
| ไม่มี `reason` / ว่าง / ชนิดผิด / ยาวเกิน 500 | `400` `{"error": "validation_failed", "fields": {"reason": "required" \| "max_length"}}` |
| ไม่มี token หรือ token ไม่ถูกต้อง | `401` `{"error": "unauthorized"}` |
| ไม่มีโน้ตนั้น | `404` `{"error": "not_found"}` |
| รายงานโน้ตนี้ไปแล้ว | `409` `{"error": "already_reported"}` |
| auth-service ล่ม | `503` `{"error": "auth_unavailable"}` |

`GET /reports`, `DELETE /reports/<report_id>` และ `DELETE /reports/<report_id>/note` จำกัดเฉพาะ user ID
ที่อยู่ใน `ADMIN_USER_IDS` (คั่นด้วย comma; ตัวอย่าง `ADMIN_USER_IDS=99,100`) รายการเรียง
`created_at` ใหม่ไปเก่า และใช้ `id` เป็นตัวตัดสินเมื่อเวลาเท่ากัน `GET /reports` แสดง report ID,
note ID พร้อมข้อมูลโน้ต, เหตุผล, reporter ID/ชื่อ และเวลาที่รายงาน

`DELETE /reports/<report_id>` ใช้ปฏิเสธ/ปิดรายงาน: ลบเฉพาะ record ของ Report และเก็บ Note ไว้
ส่วน `DELETE /reports/<report_id>/note` ลบ Note พร้อมไฟล์และ preview โดยใช้การ cleanup เดียวกับการลบโน้ตปกติ
รายงานทั้งหมดที่ผูกกับ Note นั้นจะถูกลบผ่าน foreign-key cascade ไม่กระทบ Note หรือ Report อื่น

#### `GET /reports`

| กรณี | Response |
| --- | --- |
| สำเร็จ | `200` + `{count, reports}` |
| ไม่มี token หรือ token ไม่ถูกต้อง | `401` `{"error": "unauthorized"}` |
| ไม่ใช่ admin | `403` `{"error": "forbidden"}` |
| auth-service ล่ม | `503` `{"error": "auth_unavailable"}` |

#### `DELETE /reports/<report_id>` — ปฏิเสธรายงาน เก็บ Note ไว้

| กรณี | Response |
| --- | --- |
| สำเร็จ | `204` |
| ไม่มี token หรือ token ไม่ถูกต้อง | `401` `{"error": "unauthorized"}` |
| ไม่ใช่ admin | `403` `{"error": "forbidden"}` |
| ไม่พบ report | `404` `{"error": "not_found"}` |
| auth-service ล่ม | `503` `{"error": "auth_unavailable"}` |

#### `DELETE /reports/<report_id>/note` — ลบ Note ที่ถูกรายงาน

| กรณี | Response |
| --- | --- |
| ลบ Note, ไฟล์ และ Report ที่เกี่ยวข้องสำเร็จ | `204` |
| ไม่มี token หรือ token ไม่ถูกต้อง | `401` `{"error": "unauthorized"}` |
| ไม่ใช่ admin | `403` `{"error": "forbidden"}` |
| ไม่พบ report หรือ Note ที่เกี่ยวข้อง | `404` `{"error": "not_found"}` |
| auth-service ล่ม | `503` `{"error": "auth_unavailable"}` |

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
| `models.py` | ตาราง `notes`, `favorites` (US-15), `thanks` (US-28) และ session factory |
| `validation.py` | ตรวจ metadata/ไฟล์ — pure function ทดสอบแยกได้ |
| `storage.py` | interface เก็บไฟล์ (ตอนนี้เป็น local disk) |
| `preview.py` | สร้างรูปตัวอย่าง (PNG/PDF → PNG) — pure function ทดสอบแยกได้เหมือน `validation.py` (US-11) |

เทสต์อยู่ที่ [`src/tests/test_notes_validation.py`](../../src/tests/test_notes_validation.py),
[`src/tests/test_notes_api.py`](../../src/tests/test_notes_api.py),
[`src/tests/test_notes_identity.py`](../../src/tests/test_notes_identity.py) (คุยกับ auth-service ตัวจริงผ่าน HTTP) และ
[`src/tests/test_notes_preview.py`](../../src/tests/test_notes_preview.py),
[`src/tests/test_notes_favorites.py`](../../src/tests/test_notes_favorites.py) และ
[`src/tests/test_notes_thanks.py`](../../src/tests/test_notes_thanks.py)
