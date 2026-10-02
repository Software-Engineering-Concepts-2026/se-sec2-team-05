# Test Plan & Report — NoteShare

เอกสารนี้สรุปว่าทีมทดสอบอะไร ด้วยเครื่องมืออะไร และผลล่าสุดเป็นอย่างไร
ตัวไฟล์เทสต์อยู่ที่ [`src/tests/`](../../src/tests/) และ [`prototypes/sprint1/`](../../prototypes/sprint1/)

## 1. กลยุทธ์การทดสอบ

ปัจจุบัน Stats Service อ่านสถิติของโน้ตจริงจาก database และให้บริการ HTTP contract สำหรับ front-end โดยทดสอบทั้ง endpoint ของ Stats Service และการนับ view/download ของ Notes Service

| ระดับ | ขอบเขต | เครื่องมือ | ทำไมเลือกตัวนี้ |
| --- | --- | --- | --- |
| Unit (JS) | pure function ที่แยกออกมาตอน Lab 7 | `node --test` (built-in) | ไม่ต้องเพิ่ม dependency หรือ `package.json` ให้โปรเจกต์ |
| Unit / API (Python) | HTTP contract ของ Stats Service ผ่าน Flask test client | `pytest` + Flask test client | ทดสอบ endpoint ได้โดยไม่ต้องสตาร์ต server จริง |
| Integration (API) | Notes Service ทั้งเส้น — อัปโหลด → กรอง → ดาวน์โหลด ผ่าน Flask test client + SQLite ชั่วคราว | `pytest` | ทดสอบพฤติกรรมจริงของ endpoint ได้โดยไม่ต้องยก Postgres |
| Smoke (container) | ทั้ง stack (`docker compose up`) ตอบ health และวิ่งครบเส้น upload → filter → download | `docker compose` + `curl` ใน CI | จับปัญหาที่ unit test มองไม่เห็น เช่น gunicorn/CMD พัง, service ต่อ Postgres ไม่ติด, volume ไม่ mount |

**ยังไม่ทำในรอบนี้:** E2E ผ่านเบราว์เซอร์, load/performance test, security scan — จะทำเมื่อมี service จริงและฐานข้อมูล

## 2. Test Cases

### 2.1 `note-utils.js` — helper ของ prototype (`node --test`)

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| JS-01 | `escapeHtml` แปลงอักขระพิเศษของ HTML | `<script>alert(1)</script>` | ได้ `&lt;script&gt;...` ไม่มีแท็กหลุด |
| JS-02 | `escapeHtml` รับ null/undefined ได้ | `null`, `undefined` | ได้ string ว่าง ไม่ throw |
| JS-03 | `formatStars` ปัดเศษคะแนน | `4.2`, `4.8` | `★★★★☆`, `★★★★★` |
| JS-04 | `formatStars` clamp ค่านอกช่วง | `-3`, `10` | `☆☆☆☆☆`, `★★★★★` |
| JS-05 | `compareNotes` เรียงตามคะแนน | `sortMode = 'rating'` | คะแนนสูงมาก่อน |
| JS-06 | `compareNotes` เรียงตามยอดดาวน์โหลด | `sortMode = 'download'` | ดาวน์โหลดเยอะมาก่อน |
| JS-07 | `compareNotes` fallback เมื่อ sortMode ไม่รู้จัก | `sortMode = 'xxx'` | เรียงใหม่สุดก่อน (`new`) |

### 2.2 Stats Service — HTTP contract (`pytest`)

| # | Test case | Request | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| PY-01 | health check ตอบปกติ | `GET /health` | `200`, `status = ok`, `service = stats-service` |
| PY-02 | timestamp เป็น ISO และมี timezone | `GET /health` | `datetime.fromisoformat()` parse ผ่าน และ `tzinfo` ไม่เป็น `None` |
| PY-03 | รูปร่าง response ของ stats ตรง contract | `GET /stats` | `200`, มีคีย์ `total_downloads`, `total_notes`, `top_contributors` ครบและชนิดถูก |
| PY-04 | route ที่ไม่มีอยู่ | `GET /does-not-exist` | `404` |
| PY-05 | ต้อง login ก่อนดูสถิติของโน้ต | `GET /notes/<id>/stats` ไม่มี Authorization | `401` |
| PY-06 | ผู้ใช้ที่ไม่ใช่เจ้าของดูสถิติไม่ได้ | `GET /notes/<id>/stats` ด้วยบัญชีอื่น | `403` |
| PY-07 | โน้ตที่ไม่มีอยู่ | `GET /notes/<id>/stats` ด้วย id ที่ไม่มี | `404` |
| PY-08 | เจ้าของโน้ตดูสถิติได้ | `GET /notes/<id>/stats` ด้วยบัญชีเจ้าของ | `200` + `note_id`, `views`, `downloads` |
| PY-09 | view และ download แยกจากกัน | `GET /notes/<id>` แล้วตรวจ counters | `view_count` เพิ่ม โดย `download_count` ไม่เพิ่ม |

### 2.3 Notes Service — validation ของ metadata (`pytest`, US-08 AC ข้อ 2–3)

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| NV-01 | ฟอร์มครบถ้วนผ่าน และ cast `year_level` เป็น int | ฟอร์มครบ | ไม่มี error, `year_level == 2` |
| NV-02 | ฟิลด์บังคับที่ขาด ต้องรายงานครบในครั้งเดียว | มีแค่ `title` | error ครบทั้ง 5 ฟิลด์ที่ขาด |
| NV-03 | ค่าที่มีแต่ช่องว่างนับเป็นไม่กรอก | `subject_code = "   "` | `"จำเป็นต้องกรอก"` |
| NV-04 | ชั้นปีนอกช่วง/ไม่ใช่ตัวเลข | `0`, `9`, `-1`, `"สอง"` | error ทั้ง 4 เคส |
| NV-05 | `class_date` ที่ถูกรูปแบบถูก parse เป็น date | `2026-08-20` | `date(2026, 8, 20)` |
| NV-06 | `class_date` ผิดรูปแบบ | `20/08/2026` | `"ต้องเป็นรูปแบบ YYYY-MM-DD"` |
| NV-07 | ฟิลด์ไม่บังคับที่ไม่กรอก ต้องไม่เป็น error | ไม่ส่ง `topic`/`class_date` | ผ่าน |
| NV-08 | ข้อความยาวเกินขีดจำกัดคอลัมน์ | `title` 201 ตัวอักษร | `"ยาวเกิน 200 ตัวอักษร"` |
| NV-09 | ไฟล์ PDF ผ่าน | `application/pdf` | ผ่าน + ได้ขนาดไฟล์ถูกต้อง |
| NV-10 | ไม่แนบไฟล์ | `None` | `"ต้องแนบไฟล์โน้ต"` |
| NV-11 | ชนิดไฟล์ที่ไม่รองรับ | `.exe` | ถูกปฏิเสธ |
| NV-12 | ไฟล์ว่าง | 0 byte | `"ไฟล์ว่าง"` |
| NV-13 | ไฟล์ใหญ่เกิน 20 MB | 20 MB + 1 byte | ถูกปฏิเสธ |
| NV-14 | หลัง validate แล้ว stream ต้องถูก rewind | อ่าน stream ซ้ำ | ได้เนื้อไฟล์เดิม (ถ้าลืม `seek(0)` ไฟล์ที่เซฟจะว่าง) |
| NV-15 | `uploader_name` ในฟอร์มไม่ถูกใช้ (US-31) | ฟอร์มครบ + `uploader_name=คนอื่น` | ไม่มี error และไม่มี `uploader_name` ในผลลัพธ์ — ชื่อมาจากบัญชีที่ `app.py` |

### 2.4 Notes Service — API (`pytest`, US-08 AC ข้อ 4)

ทุกเคสที่อัปโหลดส่ง Bearer token ของบัญชีทดสอบ ผ่าน `FakeIdentity` ที่ inject แทน auth-service (US-31)

| # | Test case | Request | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| NA-01 | health check | `GET /health` | `200`, `service = notes-service` |
| NA-02 | อัปโหลดพร้อม metadata ครบ | `POST /notes` | `201` + echo `subject_code`, `year_level`, `topic`, `class_date`, `download_url` |
| NA-03 | metadata ไม่ครบต้องไม่ถูกบันทึก | `POST /notes` ขาดฟิลด์ | `400` และ `GET /notes` ยังได้ `count = 0` |
| NA-04 | ไม่แนบไฟล์ | `POST /notes` ไม่มี `file` | `400` |
| NA-05 | ดาวน์โหลดได้ไฟล์เดิมกลับมา | `GET /notes/<id>/download` | byte ตรงกับที่อัปโหลด + ชื่อไฟล์เดิมใน `Content-Disposition` |
| NA-06 | ค้นด้วยคำค้นเจอจากชื่อวิชา/บทเรียน | `GET /notes?q=Calculus` | เจอ 1 รายการที่ถูกต้อง |
| NA-07 | กรองด้วยคณะและชั้นปี รวมถึงเงื่อนไขผสม | `?faculty=ICT&year_level=4` | กรองถูก และเงื่อนไขที่ไม่มีใครตรงได้ `count = 0` |
| NA-08 | กรองด้วยช่วงวันที่ของคาบเรียน | `?date_from=...&date_to=...` | ได้เฉพาะที่อยู่ในช่วง |
| NA-09 | ค่ากรองที่ผิดรูปต้องได้ 400 ไม่ใช่ 500 | `year_level=สอง`, วันที่ผิดรูป, `sort=; DROP TABLE notes` | `400` ทั้งสามเคส |
| NA-10 | โน้ตที่ไม่มีอยู่ | `GET /notes/999`, `/999/download` | `404` |
| NA-11 | ไม่เชื่อชื่อไฟล์จากผู้ใช้ | อัปโหลดชื่อ `../../evil.pdf` | ไฟล์จริงถูกเก็บในโฟลเดอร์ storage ด้วยชื่อที่ระบบสร้างเอง ชื่อเดิมเก็บไว้แค่แสดงผล |
| NA-12 | commit ล้มแล้วต้องไม่เหลือไฟล์กำพร้า | `Session.commit` raise | โฟลเดอร์ storage ว่าง ไม่มีไฟล์ค้าง |
| NA-13 | `limit`/`offset` ติดลบถูก clamp | `?limit=-1`, `?offset=-5` | `limit=-1` ได้ 1 รายการ (ไม่ใช่ทั้งหมดแบบที่ SQLite ตีความ), `offset=-5` เท่ากับ 0 |
| NA-14 | request ใหญ่เกินได้ 413 เป็น JSON | body เกิน `MAX_CONTENT_LENGTH` | `413` + `error = validation_failed` ไม่ใช่หน้า HTML ของ Werkzeug |
| NA-15 | โน้ตใหม่เริ่มที่ 0 ดาวน์โหลด (US-12) | `GET /notes/<id>` หลังอัปโหลด | `download_count = 0` |
| NA-16 | ดาวน์โหลดสำเร็จแล้วยอดเพิ่ม 1 | `GET /notes/<id>/download` | `download_count = 1` |
| NA-17 | ดาวน์โหลดซ้ำสะสมยอด | ดาวน์โหลด 3 ครั้ง | `download_count = 3` |
| NA-18 | ไฟล์หายจาก storage ต้องไม่นับ | ลบไฟล์ออกจาก storage แล้วดาวน์โหลด | `404` `{"error": "file_not_found"}` และ `download_count` ยังเป็น 0 (AC ข้อ 3 ของ #12) |
| NA-19 | ยอดดาวน์โหลดแยกรายโน้ต | โหลดโน้ต A 2 ครั้ง | A = 2, B = 0 |
| NA-20 | อัปโหลดโดยไม่ได้ login ไม่ได้ (US-31) | ไม่มี header, token ที่ไม่รู้จัก, ลืม `Bearer` | `401` `{"error": "unauthorized"}` + `WWW-Authenticate: Bearer` · DB และ storage ว่าง |
| NA-21 | ตรวจ login ก่อน validate ฟอร์ม | ไม่ login + ฟอร์มขาดฟิลด์ | `401` ไม่ใช่ `400` |
| NA-22 | ชื่อผู้อัปโหลดมาจากบัญชี ไม่ใช่ฟอร์ม (AC 1–3 ของ #31) | ส่ง `uploader_name=คนอื่นที่อยากสวมรอย` | `uploader_name` = `display_name` ของบัญชี ทั้งใน response, `GET /notes/<id>` และ `GET /notes` |
| NA-23 | เก็บ `uploader_id` แต่ไม่ส่งออก | อ่านคอลัมน์ใน DB ตรง ๆ | `uploader_id` = id ของบัญชี · ไม่มี `uploader_id` ใน response |
| NA-24 | auth-service ล่ม | identity โยน `IdentityUnavailable` | `503` `{"error": "auth_unavailable"}` · storage ว่าง |
| NA-25 | endpoint อ่านอย่างเดียวยังเปิด (รวม `/preview`, US-11) | `GET /notes`, `/notes/<id>`, `/download`, `/preview` โดยไม่ login | `200` ทั้งหมด ยกเว้น `/preview` ที่ไม่ใช่ `401` (ไฟล์ default ของเทสต์เป็น PDF ปลอม จึงได้ `422` แทน) และไม่มีการเรียก auth-service เพิ่ม |
| NA-26 | login อย่างเดียวแก้/ลบไม่ได้ (ADR-004 ยังใช้) | `PATCH`/`DELETE` ด้วย Bearer token แต่ไม่มี edit token | `403` ทั้งคู่ · ด้วย edit token ลบได้ `204` |
| NA-27 | กรองตามหัวข้อเลกเชอร์แบบ partial ไม่สนตัวพิมพ์ (US-26) | `?topic=search tree` | เจอเฉพาะโน้ตที่ `topic` มีคำนั้นเป็นส่วนหนึ่ง |
| NA-28 | `topic` กรองแยกจาก `q` | `?topic=Tree` โดยชื่อวิชามีคำว่า Tree แต่ `topic` ไม่มี | `count = 0` |
| NA-29 | `topic` escape wildcard ของ SQL | `?topic=50%` โดยมีโน้ต `topic` เป็น `50%` และ `Recursion` | เจอเฉพาะโน้ตที่ `topic` เป็น `50%` จริง ไม่ใช่ทุกโน้ต |
| NA-30 | โน้ตที่ไม่มี `topic` ไม่ขึ้นเมื่อกรองด้วย `topic` | อัปโหลดไม่ระบุ `topic` แล้ว `?topic=anything` | `count = 0` |
| NA-31 | `topic` ที่ไม่ตรงกับใครเลยต้องได้ผลว่างไม่ใช่ error | โน้ตมี `topic="Recursion"` แล้ว `?topic=Quantum Computing` | `200` + `count = 0` |
| NA-32 | ช่วงวันที่กลับด้านต้องได้ 400 | `?date_from=2026-08-31&date_to=2026-08-01` | `400 {"error": "invalid_filter", "field": "date_to"}` |
| NA-33 | ช่วงวันที่นับวันขอบด้วย (inclusive) | โน้ตตรงวันขอบทั้งสองฝั่งพอดี + ก่อน/หลังช่วง 1 วัน | ได้เฉพาะ 2 ตัวที่ตรงวันขอบ |
| NA-34 | กรองวันเดียว และส่งมาฝั่งเดียว | `date_from == date_to` และส่งแค่ `date_from` | กรองถูกทั้งสองแบบ |
| NA-35 | โน้ตที่ไม่มี `class_date` ไม่ขึ้นเมื่อกรองด้วยวันที่ | อัปโหลดไม่ระบุ `class_date` แล้วกรองด้วยช่วงกว้าง | `count = 0` |
| NA-36 | ใช้ `topic` + `date_from`/`date_to` + `faculty` + `file_type` พร้อมกัน (US-10 + US-26) | โน้ตที่ตรงทุกเงื่อนไข ปนกับโน้ตที่ไม่ตรงทีละเงื่อนไข | ได้เฉพาะโน้ตที่ตรงทุกเงื่อนไข |
| NA-37 | บันทึกเข้ารายการโปรดครั้งแรก (US-15) | `POST /notes/<id>/favorite` | `201` + `note_id`, `is_favorited = true`, `favorited_at` |
| NA-38 | กดบันทึกซ้ำ idempotent | `POST /notes/<id>/favorite` สองครั้ง | ครั้งที่สอง `200` · `favorited_at` เท่าเดิม · ในรายการมีโน้ตนี้แค่ 1 รายการ |
| NA-39 | บันทึก/เอาออกต้อง login | ไม่มี header หรือ token ที่ไม่รู้จัก · auth-service ล่ม | `401` `unauthorized` · `503` `auth_unavailable` |
| NA-40 | โน้ตที่ไม่มีอยู่ | `POST`/`DELETE /notes/999/favorite` | `404` `not_found` ทั้งคู่ |
| NA-41 | บันทึกโน้ตที่ตัวเองอัปโหลดได้ | Alice อัปโหลดแล้ว `POST .../favorite` ด้วย token ของ Alice | `201` |
| NA-42 | เอาออกจากรายการโปรด idempotent | `DELETE .../favorite` โน้ตที่อยู่ในรายการ และโน้ตที่ไม่เคยบันทึก | `204` ทั้งคู่ · โน้ตแรกหายจากรายการ |
| NA-43 | เอาออกได้เฉพาะรายการของตัวเอง | Alice กับ Bob บันทึกโน้ตเดียวกัน แล้ว Bob เอาออก | รายการของ Alice ยังมีโน้ตนั้น |
| NA-44 | `GET /notes/favorites` เห็นเฉพาะของตัวเอง เรียงล่าสุดก่อน | Alice บันทึก 3 โน้ต · Bob บันทึกอีกโน้ตหนึ่ง | Alice ได้ 3 โน้ตเรียงที่เพิ่งบันทึกก่อน · Bob เห็นเฉพาะของ Bob · แต่ละ item มี `is_favorited = true` และ `favorited_at` |
| NA-45 | ยังไม่มีรายการโปรด / ต้อง login | Alice ที่ยังไม่บันทึกอะไร · ไม่ login · auth-service ล่ม | `200 {"items": [], "count": 0}` · `401` · `503` |
| NA-46 | โน้ตที่เจ้าของลบแล้ว (US-20) ไม่แสดงในรายการโปรด | บันทึก 2 โน้ต แล้วลบโน้ตหนึ่งด้วย edit token | ในรายการเหลือแค่โน้ตที่ยังอยู่ |
| NA-47 | รายการโปรดแบ่งหน้าและ clamp เหมือน `GET /notes` | `?limit=2`, `?limit=2&offset=2`, `?limit=-5&offset=-3`, `?limit=abc` | แบ่งหน้าถูก · ค่าติดลบถูก clamp · `limit=abc` ได้ `400` |
| NA-48 | `/notes/favorites` ไม่ถูกตีความเป็น `/notes/<id>` · `GET /notes` ไม่ถูกกรองด้วยรายการโปรด | ไม่ login เรียก `/notes/favorites` · บันทึก 1 จาก 2 โน้ตแล้วค้นหา | `401` (ไม่ใช่ `404`) · ค้นหาได้ทั้ง 2 โน้ต |
| NA-49 | `is_favorited` บน `GET /notes` และ `GET /notes/<id>` แยกตามผู้ใช้ | Alice บันทึกโน้ตหนึ่ง แล้วอ่านด้วย token ของ Alice และ Bob | Alice: `true` / `false` ถูกโน้ต · Bob: `false` ทั้งหมด · สลับเป็น `false` หลังเอาออก |
| NA-50 | ไม่ login หรือ token ใช้ไม่ได้ ได้ `is_favorited = null` | `GET /notes`, `GET /notes/<id>` โดยไม่มี header และด้วย token ที่ไม่รู้จัก | `200` และ `is_favorited = null` |
| NA-51 | auth-service ล่มระหว่างค้นหา ค้นหายังใช้ได้ | identity โยน `IdentityUnavailable` แล้ว `GET /notes`, `GET /notes/<id>` ด้วย token ที่ถูก | `200` และ `is_favorited = null` (ไม่ใช่ `503`) |
| NA-52 | ดึงสถานะของทั้งหน้าใน query เดียว (D5) | บันทึก 5 โน้ต แล้วนับ SQL ตอน `GET /notes` | มี query ที่อ่านตาราง `favorites` เพียง 1 ครั้ง |
| NA-53 | แสดงความคิดเห็นโดยไม่ login | `POST /notes/<id>/comments` ไม่มี Authorization | `401` |
| NA-54 | token ไม่ถูกต้อง | `POST /notes/<id>/comments` + invalid Bearer token | `401` |
| NA-55 | comment ว่าง | `POST /notes/<id>/comments` + `{"content": "   "}` | `400` |
| NA-56 | comment ยาวเกิน 1000 ตัวอักษร | `POST /notes/<id>/comments` + content 1001 chars | `400` |
| NA-57 | แสดงความคิดเห็นใน note ที่ไม่มีอยู่ | `POST /notes/999/comments` | `404` |
| NA-58 | แสดง comments เรียงจากใหม่ไปเก่า | `GET /notes/<id>/comments` | `200` + comments เรียง `created_at` ล่าสุดก่อน |
| NA-59 | ลบ comment ของตัวเอง | `DELETE /notes/<id>/comments/<comment_id>` | `204` |
| NA-60 | ลบ comment ของคนอื่น | `DELETE /notes/<id>/comments/<comment_id>` ด้วย user คนอื่น | `403` |
| NA-61 | ลบ note แล้ว comments ถูกลบด้วย | สร้าง comment → `DELETE /notes/<id>` → ตรวจ DB | comment ไม่เหลือใน DB |
| NA-62 | รายงานโน้ตสำเร็จ | `POST /notes/<id>/reports` ด้วยเหตุผลที่ถูกต้อง | `201` + report fields และชื่อ/ID จากบัญชี |
| NA-63 | เหตุผลรายงานต้องเป็นข้อความไม่ว่าง ไม่เกิน 500 ตัวอักษร | ไม่มี `reason`, JSON ไม่ใช่ object, whitespace, ชนิดผิด หรือยาวเกิน | `400 validation_failed` พร้อม `fields.reason` |
| NA-64 | รายงานต้อง login และ auth-service พร้อมใช้งาน | ไม่มี Bearer token หรือ identity โยน `IdentityUnavailable` | `401 unauthorized` + `WWW-Authenticate` หรือ `503 auth_unavailable` |
| NA-65 | รายงานโน้ตที่ไม่มีอยู่ | `POST /notes/<id>/reports` ด้วย id ที่ไม่มี | `404 not_found` |
| NA-66 | รายงานซ้ำถูกป้องกันทั้งใน service และฐานข้อมูล | ผู้ใช้เดิมรายงานโน้ตเดิมซ้ำ และ insert ซ้ำตรงผ่าน SQLAlchemy | API `409 already_reported` · unique constraint `uq_reports_reporter_note` ปฏิเสธ insert |
| NA-67 | ผู้ใช้ต่างคนรายงานโน้ตเดียวกันได้ | สมาชิกสองคน `POST /notes/<id>/reports` | ทั้งคู่ `201` และ admin เห็นสองรายการ |
| NA-68 | admin ดูรายงานทั้งหมดได้ตามลำดับล่าสุด | `GET /reports` ด้วย admin | `200` + `count`, `reports` พร้อมข้อมูลผู้รายงาน/เหตุผล เรียง `created_at`, `id` DESC; กรณีว่างได้ list ว่าง |
| NA-69 | จำกัดการดูรายงานให้ admin | `GET /reports` ด้วยสมาชิก, ไม่มี token หรือ auth-service ล่ม | `403 forbidden`, `401 unauthorized` หรือ `503 auth_unavailable` |
| NA-70 | admin ลบรายการรายงานได้ | `DELETE /reports/<report_id>` ด้วย admin | `204` · รายงานหาย แต่ Note ยังอยู่ |
| NA-71 | สมาชิกทั่วไปลบรายงานไม่ได้ | `DELETE /reports/<report_id>` ด้วย member | `403 forbidden` และ report ยังอยู่ |
| NA-72 | ลบ report ที่ไม่มีอยู่ | admin `DELETE /reports/<id>` ด้วย id ที่ไม่มี | `404 not_found` |
| NA-73 | admin IDs อ่านจาก env และข้ามค่าที่ไม่ใช่ตัวเลข | `ADMIN_USER_IDS` มี whitespace และค่าที่ไม่ใช่ตัวเลข | แปลงเฉพาะ numeric IDs; ไม่มีค่าแล้วไม่มี admin |
| NA-74 | ลบ Note ยังคงทำงานเมื่อมี report ผูกอยู่ | ลบ Note ด้วย edit token หลังสร้าง report | Note และ report ที่ผูกผ่าน FK ถูกลบตาม cascade |
| NA-75 | ขอบคุณเจ้าของโน้ตครั้งแรก (US-28) | Bob `POST /notes/<id>/thanks` โน้ตของ Alice | `201` + `note_id`, `thanked = true`, `thanked_at` |
| NA-76 | กดขอบคุณซ้ำไม่เพิ่มยอด | `POST .../thanks` สองครั้ง | ครั้งที่สอง `200` · `thanked_at` เท่าเดิม · ตาราง `thanks` มี 1 แถว |
| NA-77 | ขอบคุณต้อง login | ไม่มี header · token ที่ไม่รู้จัก · auth-service ล่ม | `401` `unauthorized` (ไม่มีแถวใน `thanks`) · `401` · `503` `auth_unavailable` |
| NA-78 | โน้ตที่ไม่มีอยู่ | `POST /notes/999/thanks` | `404` `not_found` |
| NA-79 | ขอบคุณโน้ตของตัวเองไม่ได้ | Alice `POST .../thanks` โน้ตที่ตัวเองอัปโหลด | `403` `own_note` · ไม่มีแถวใน `thanks` |
| NA-80 | หลายคนขอบคุณโน้ตเดียวกันได้คนละครั้ง และนับแยกโน้ต | Bob กับ Carol ขอบคุณ แล้ว Bob กดซ้ำ · ขอบคุณโน้ตหนึ่งจากสองโน้ต | `201` ทั้งคู่ · ยอดของโน้ตนั้น = 2 · อีกโน้ต = 0 |
| NA-81 | ยกเลิกคำขอบคุณไม่ได้ | `DELETE /notes/<id>/thanks` หลังขอบคุณ | `405` · `thank_status` ยังเป็น `thanked` |
| NA-82 | API ไม่ตรวจว่าดาวน์โหลดแล้ว ("หลังดาวน์โหลด" เป็นเงื่อนไขฝั่ง UI) | ขอบคุณโน้ตที่ `download_count = 0` | `201` |
| NA-83 | `thank_status` เปลี่ยนตามการขอบคุณ และแยกตามผู้ใช้ | อ่านโน้ตก่อน/หลัง Bob ขอบคุณ · Carol อ่านโน้ตเดียวกัน | Bob: `can_thank` → `thanked` · Carol: `can_thank` |
| NA-84 | `thank_status` ของเจ้าของโน้ต | Alice อ่านโน้ตตัวเอง | `own_note` |
| NA-85 | ไม่ login หรือ token ใช้ไม่ได้ ได้ `thank_status = null` | `GET /notes`, `GET /notes/<id>` ไม่มี header และด้วย token ที่ไม่รู้จัก | `200` และ `thank_status = null` |
| NA-86 | auth-service ล่มระหว่างค้นหา ค้นหายังใช้ได้ | identity โยน `IdentityUnavailable` แล้ว `GET /notes`, `GET /notes/<id>` ด้วย token ที่ถูก | `200` และ `thank_status = null` (ไม่ใช่ `503`) |
| NA-87 | `GET /notes` ให้สถานะต่อโน้ตถูกต้องในหน้าเดียวกัน และ query `thanks` ครั้งเดียว | Bob ค้นหาเจอโน้ตที่ยังไม่ขอบคุณ, ขอบคุณแล้ว และโน้ตของตัวเอง · นับ SQL ตอนมี 5 โน้ต | `can_thank` · `thanked` · `own_note` · อ่านตาราง `thanks` 1 ครั้ง |
| NA-88 | ลบโน้ตลบคำขอบคุณของโน้ตนั้น (US-20) | Bob กับ Carol ขอบคุณ แล้วลบโน้ตด้วย edit token · มีอีกโน้ตที่ Bob ขอบคุณไว้ | `204` ไม่ชน FK · thanks ของโน้ตที่ลบหายหมด · ของอีกโน้ตยังอยู่ |

### 2.5 Notes Service — แก้ไข/ลบโน้ต (`pytest`, US-19 #19 + US-20 #20)

ความเป็นเจ้าของพิสูจน์ด้วย edit token ต่อโน้ต ([ADR-004](../architecture/adr/0004-per-note-edit-token.th.md))

| # | Test case | Request | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| NE-01 | token ออกให้ครั้งเดียวตอนสร้าง และไม่รั่วออกทาง endpoint อื่น | `POST /notes` แล้ว `GET /notes/<id>`, `GET /notes` | response ตอนสร้างมี `edit_token` · การอ่านครั้งต่อ ๆ ไปไม่มีทั้ง `edit_token` และ `edit_token_hash` |
| NE-02 | PATCH แก้เฉพาะฟิลด์ที่ส่งมา และประทับ `updated_at` | `PATCH` ส่ง `subject_code` + `topic` | สองฟิลด์นั้นเปลี่ยน ฟิลด์อื่นคงเดิม `updated_at` จาก `null` เป็นเวลาจริง |
| NE-03 | ล้างค่าฟิลด์ไม่บังคับได้ | `PATCH` ส่ง `topic=` (ว่าง) | `topic` เป็น `null` |
| NE-04 | ค่าผิดรูปต้องไม่ทำให้ข้อมูลเดิมเสีย | `PATCH` ส่ง `year_level=99` | `400` และค่าเดิมใน DB ไม่เปลี่ยน |
| NE-05 | ฟิลด์ที่แก้ไม่ได้ถูกเมิน ไม่ใช่ error | `PATCH` ส่ง `uploader_name` + `title` | `title` เปลี่ยน `uploader_name` คงเดิม |
| NE-06 | PATCH ที่ไม่มีฟิลด์ให้แก้ | `PATCH` body ว่าง | `400` `no_fields_to_update` |
| NE-07 | ลบแล้วหายทั้ง record และไฟล์ | `DELETE` ด้วย token ถูก | `204` · `GET` ได้ `404` · โฟลเดอร์ storage ว่าง |
| NE-08 | ไม่ส่ง token | `PATCH`/`DELETE` ไม่มี header | `403` ทั้งคู่ |
| NE-09 | token ผิด | `PATCH`/`DELETE` ด้วย token มั่ว | `403` ทั้งคู่ |
| NE-10 | token ของโน้ตใบหนึ่งใช้กับใบอื่นไม่ได้ | ใช้ token ของโน้ต A ไปแก้/ลบโน้ต B | `403` ทั้งคู่ · โน้ต B ไม่ถูกแตะทั้งใน DB และ storage · เจ้าของตัวจริงยังใช้ token ของตัวเองได้ |
| NE-11 | แก้/ลบโน้ตที่ไม่มีอยู่ | `PATCH`/`DELETE /notes/999` | `404` ทั้งคู่ |

### 2.6 Container smoke test (CI เท่านั้น)

> **หมายเหตุ:** `view_count` เป็นคอลัมน์ใหม่ในตาราง `notes` และโปรเจกต์ยังไม่มี migration สำหรับ schema นี้ หากมี PostgreSQL volume เก่าอยู่ ให้รัน `docker compose down -v` ก่อน `docker compose up` เพื่อสร้าง database schema ใหม่

| # | Test case | ขั้นตอน | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| DK-01 | ทั้ง stack build และสตาร์ตได้ | `docker compose up -d --build` | exit code 0 |
| DK-02 | ทุก service ตอบ health | `curl :5000/health`, `:5001/health`, `:5002/health` (retry 20 ครั้ง ห่างละ 3 วิ) | `200` ทั้งหมด |
| DK-03 | end-to-end ของ US-08 | อัปโหลด (พร้อม token ของบัญชีผู้อัปโหลด) พร้อม metadata → กรองด้วย `faculty`+`year_level`+`q` → ดาวน์โหลด | `count = 1` และไฟล์ที่ดาวน์โหลดตรงกับต้นฉบับ (`cmp`) |
| DK-04 | validation ทำงานจริงบน stack ที่รัน | `POST /notes` (มี token) ส่งแค่ `title` | `400` |
| DK-05 | สมัคร → login → ใช้ token → logout บน Postgres จริง (US-05/US-06) | `curl` ไปที่ `:5002/auth/*` | สมัคร `201` · สมัครซ้ำ `409` · โดเมนอื่น `400` · รหัสผิดกับอีเมลที่ไม่มีได้ body เดียวกัน · `me` ได้ชื่อถูก · logout `204` แล้ว `me` ด้วย token เดิมได้ `401` |
| DK-06 | อัปโหลดต้อง login และเครดิตมาจากบัญชี (US-31) บน stack จริง | สมัคร + login บัญชี `CI Uploader` แล้ว `POST /notes` สามแบบ (ไม่มี token / token มั่ว / token จริง + `uploader_name=spoofed name`) | สองแบบแรกได้ `401` · แบบที่สามได้ `uploader_name = CI Uploader` · `count = 1` (ครั้งที่ไม่ผ่านไม่ถูกบันทึก) · notes-service คุยกับ auth-service ผ่านเครือข่ายของ compose จริง |
| DK-07 | preview endpoint ทำงานจริงบน image ที่ build (US-11) — กัน regression ของบั๊ก Dockerfile ที่เคยลืม copy `preview.py` (commit `8f25b9b`) ซึ่ง unit test จับไม่ได้เพราะ import จาก source tree ตรง ๆ | อัปโหลด PNG จริงแล้ว `GET .../preview` โดยไม่ส่ง token, กับอัปโหลดไฟล์ที่ประกาศเป็น `image/png` แต่เนื้อไม่ใช่รูป | ไฟล์จริงได้ `200` + header `Content-Type: image/png` + ไบต์ 8 ตัวแรกตรง PNG signature · ไฟล์ปลอมได้ `422` ไม่ใช่ `500` |
| DK-08 | web gateway เสิร์ฟหน้าเว็บและส่งต่อ API จาก origin เดียว (ADR-006, US-11/US-31) | `curl :8080/`, `/login.html`, `/upload.html`, ไฟล์ JS ทั้ง 7 ไฟล์และไฟล์เทสต์ทั้ง 3 ไฟล์ · `GET :8080/notes?subject_code=CS201&year_level=2` และ `?year_level=abc` · `GET :8080/auth/me` แบบไม่มี token และมี token · อัปโหลด PNG ผ่าน `:8080/notes` แล้วเปิด `preview_url` ผ่าน `:8080` · `POST :8080/auth/login` (JSON) → `POST :8080/auth/logout` → `GET :8080/auth/me` ด้วย token เดิม | หน้าแรกมี `id="searchForm"`, หน้า login มี `id="loginForm"`, หน้าอัปโหลดมี `id="uploadForm"` · ไฟล์ JS ได้ `200` · ไฟล์เทสต์ได้ `404` (ไม่ถูก copy เข้า image) · query string ไปถึง service ครบ (`count = 1`, ค่าผิดได้ `400`) · `me` ไม่มี token `401` มี token ได้ `CI Uploader` (header `Authorization` ผ่าน nginx) · upload ได้ `uploader_name = CI Uploader` และ preview ได้ `200` + `image/png` · login ได้ token, logout ได้ `204` แล้ว token เดิมได้ `401` (US-05/US-06 ผ่าน gateway แบบที่หน้าเว็บเรียก) |

### 2.7 Auth Service — ตรวจข้อมูลสมัครและ hash รหัสผ่าน (`pytest`, US-05 #5)

ไฟล์ [`test_auth_credentials.py`](../../src/tests/test_auth_credentials.py) — pure function ไม่ต้องมี Flask/DB

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| AC-01 | ข้อมูลถูกต้องผ่าน และถูก normalize | อีเมลตัวใหญ่มีช่องว่าง, ชื่อมีช่องว่างหัวท้าย | อีเมลเป็นตัวพิมพ์เล็ก, ชื่อถูก trim |
| AC-02 | ช่องที่ขาดรายงานครบในครั้งเดียว | body ว่าง | error ครบ `email`, `password`, `display_name` |
| AC-03 | อีเมลนอกโดเมนมหาวิทยาลัย | `gmail.com`, `mail.up.ac.th`, `up.ac.th.example.com`, `notup.ac.th` | ปฏิเสธทั้ง 4 เคส (ไม่นับ subdomain และโดเมนที่ต่อท้ายหลอก) |
| AC-04 | อีเมลผิดรูป | ไม่มี `@`, local ว่าง, `@` สองตัว, มีช่องว่าง | `"รูปแบบอีเมลไม่ถูกต้อง"` |
| AC-05 | อีเมลยาวเกิน RFC | 255 ตัวอักษร | `"ยาวเกิน 254 ตัวอักษร"` |
| AC-06 | ขอบของความยาวรหัสผ่าน | 7 / 8 / 128 / 129 | ผ่านเฉพาะ 8 และ 128 |
| AC-07 | รหัสผ่านไม่ถูกตัดช่องว่าง | `"  pass  "` | ผ่านและเก็บตามที่พิมพ์ |
| AC-08 | ขอบของความยาว `display_name` | ว่าง / มีแต่ช่องว่าง / 1 / 120 / 121 | ผ่านเฉพาะ 1 และ 120 |
| AC-09 | ค่าที่ไม่ใช่ข้อความ | ตัวเลข, list จาก JSON | ได้ error ไม่ crash |
| AC-10 | แปลงค่า `ALLOWED_EMAIL_DOMAINS` | ไม่ตั้ง, ค่าว่าง, ตัวใหญ่, มี `@` และ comma เกิน | ค่าว่างกลับเป็น `up.ac.th` ไม่ใช่ลิสต์ว่าง |
| AC-11 | hash ไม่มี plaintext และใช้ cost ตาม ADR-005 | hash รหัสผ่านจริง | ขึ้นต้นด้วย `scrypt:131072:8:1$` · ตรวจรหัสถูกผ่าน รหัสผิดไม่ผ่าน |
| AC-12 | salt ทำให้รหัสเดียวกันได้ hash ต่างกัน | hash รหัสเดียวกันสองครั้ง | hash ไม่เท่ากัน แต่ตรวจผ่านทั้งคู่ |

### 2.8 Auth Service — JWT (`pytest`, US-06 #6)

ไฟล์ [`test_auth_tokens.py`](../../src/tests/test_auth_tokens.py) — ตรวจเฉพาะลายเซ็นกับเวลาหมดอายุ

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| AT-01 | อายุ token เริ่มต้น | `DEFAULT_TTL` | 8 ชั่วโมง |
| AT-02 | encode แล้ว decode ได้ claim เดิม | token ที่เพิ่งออก | `sub`, `jti`, `iss`, `exp` ตรง |
| AT-03 | token หมดอายุ | ออกเมื่อ 9 ชั่วโมงก่อน | ไม่ผ่าน |
| AT-04 | เซ็นด้วย secret อื่น | secret ต่างกัน | ไม่ผ่าน |
| AT-05 | แก้ payload แต่ใช้ลายเซ็นเดิม | เปลี่ยน `sub` เป็น user อื่น | ไม่ผ่าน |
| AT-06 | token ไม่เซ็น (`alg: none`) | JWT ที่ไม่มีลายเซ็น | ไม่ผ่าน |
| AT-07 | token ที่ไม่มี `jti` | ลายเซ็นถูกแต่ขาด claim | ไม่ผ่าน เพราะผูกกับ session ไม่ได้ |
| AT-08 | ค่าขยะ | `None`, `""`, `"not-a-jwt"` | ไม่ผ่านและไม่ raise |
| AT-09 | secret ไม่ได้ตั้งหรือสั้นเกิน | `None`, `""`, 31 ไบต์ | service ไม่ยอมสตาร์ต |
| AT-10 | `jti` ไม่ซ้ำ | สุ่ม 1,000 ครั้ง | ไม่ซ้ำเลย |

### 2.9 Auth Service — API (`pytest`, US-05 #5 + US-06 #6)

ไฟล์ [`test_auth_api.py`](../../src/tests/test_auth_api.py) — Flask test client + SQLite ชั่วคราว
เทสต์ส่วนใหญ่ลด cost ของ scrypt ลงเพื่อความเร็ว ส่วน cost จริงของ production ตรวจใน AA-03 และ AC-11

| # | Test case | Request | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| AA-01 | health check | `GET /health` | `200`, `service = auth-service` |
| AA-02 | สมัครสำเร็จโดยไม่คืนรหัสผ่าน | `POST /auth/register` | `201` · ไม่มี `password`/`password_hash` ใน response · ในตาราง `users` มีแค่ hash |
| AA-03 | app ที่ไม่ได้ตั้งค่าเก็บรหัสด้วย cost จริง | สมัครผ่าน app ค่า default | hash ขึ้นต้นด้วย `scrypt:131072:8:1$` |
| AA-04 | สมัครด้วยอีเมลนอกโดเมน | `someone@gmail.com` | `400` + ข้อความบอกโดเมนที่อนุญาต |
| AA-05 | error ครบทุกช่องในครั้งเดียว | อีเมลผิด + รหัสสั้น + ไม่มีชื่อ | `400` error ครบสามช่อง |
| AA-06 | อีเมลซ้ำแบบไม่สนตัวพิมพ์ | สมัครซ้ำด้วย `...@UP.AC.TH` | `409 email_taken` |
| AA-07 | รับ form data ได้ด้วย | `curl -d` แบบ form | `201` |
| AA-08 | ตั้งหลายโดเมนได้ | `ALLOWED_EMAIL_DOMAINS="up.ac.th, cmu.ac.th"` | `cmu.ac.th` ผ่าน, `gmail.com` ไม่ผ่าน |
| AA-09 | body ใหญ่เกิน | 20 KB | `413` เป็น JSON |
| AA-10 | login ได้ Bearer token อายุ 8 ชั่วโมง | `POST /auth/login` | `200` · `expires_at` ห่างจากตอนนี้ประมาณ 8 ชั่วโมง |
| AA-11 | อีเมลตอน login ไม่สนตัวพิมพ์ | `...@UP.ac.th` | `200` |
| AA-12 | รหัสผิดกับอีเมลที่ไม่มีได้คำตอบเดียวกัน | login สองแบบ | `401` ทั้งคู่ และ body เท่ากันทุกไบต์ (AC ข้อ 3 ของ #6) |
| AA-13 | รหัสผ่านยาวผิดปกติ | 10,000 ตัวอักษร | `401 invalid_credentials` |
| AA-14 | login โดยไม่กรอก | body ว่าง | `400` บอกว่าช่องไหนว่าง |
| AA-15 | `me` คืนบัญชีของ token | `GET /auth/me` | `200` + `display_name` ถูก |
| AA-16 | ไม่มี Bearer token ที่ใช้ได้ | ไม่มี header, `Bearer` เปล่า, ขยะ, `Basic` | `401` + `WWW-Authenticate: Bearer` |
| AA-17 | token หมดอายุ | ตั้ง ttl ติดลบ | `401` |
| AA-18 | ลายเซ็นถูกแต่ไม่มี session ในฐานข้อมูล | token ที่สร้างเองด้วย secret จริง | `401` — พิสูจน์ว่าไม่ได้เชื่อ JWT อย่างเดียว |
| AA-19 | token จาก secret อื่น | ฐานข้อมูลเดียวกัน secret ต่างกัน | `401` |
| AA-20 | logout แล้ว token ใช้ไม่ได้ทันที | logout แล้วเรียก `me` และ logout ซ้ำ | `204` แล้ว `401` ทั้งสองครั้ง (AC ข้อ 2 ของ #6) |
| AA-21 | logout เพิกถอนเฉพาะ session ของตัวเอง | login สองเครื่องแล้ว logout เครื่องเดียว | เครื่องที่ logout ได้ `401` อีกเครื่องยัง `200` |
| AA-22 | logout โดยไม่มี token | `POST /auth/logout` | `401` |
| AA-23 | login ใหม่หลัง logout | login อีกครั้ง | token ใหม่ใช้ได้ |
| AA-24 | ไม่มี secret หรือ `AUTH_TOKEN_TTL_HOURS` ผิด | สร้าง app | service ไม่ยอมสตาร์ต |

**ตรวจว่าเทสต์จับบั๊กได้จริง (2026-09-25):** ลองทำโค้ดพังชั่วคราว 4 จุดแล้วรันใหม่ ทุกจุดมีเทสต์ที่ fail จริง จากนั้น revert แล้วผ่านครบ

| โค้ดที่ทำพัง | เทสต์ที่จับได้ |
| --- | --- |
| ไม่เช็ค `revoked_at` ตอนตรวจ token | AA-20, AA-21 |
| เทียบโดเมนด้วย `endswith` แทนการตรงตัว | AC-03 (`mail.up.ac.th`, `notup.ac.th`) |
| login ตอบต่างกันเมื่ออีเมลไม่มีในระบบ | AA-12 |
| ยอมรับ `alg: none` | AT-06 |

### 2.10 Notes Service — ตรวจตัวตนกับ auth-service ตัวจริง (`pytest`, US-31 #31)

ไฟล์ [`test_notes_identity.py`](../../src/tests/test_notes_identity.py) — ยก auth-service ตัวจริง (SQLite ชั่วคราว)
ขึ้นเป็น HTTP server ในเธรดของเทสต์ แล้วให้ `HttpIdentity` คุยผ่าน urllib จริง ไม่ต้องใช้ Docker
ส่วนที่ `FakeIdentity` ใน 2.4 เช็คไม่ได้ (รูปแบบ response ของ `/auth/me` และการคุย HTTP) อยู่ในไฟล์นี้

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| NI-01 | token ที่ใช้ได้ได้บัญชีกลับมา | login จริงแล้วส่ง `Bearer <token>` | `{"id": int, "display_name": ...}` ตรงกับที่สมัคร |
| NI-02 | logout แล้วใช้ไม่ได้ทันที | logout แล้วส่ง token เดิม | `None` |
| NI-03 | ไม่มี token หรือ token ใช้ไม่ได้ | `None`, `""`, `Bearer not-a-jwt`, `Basic ...` | `None` ทั้งหมด |
| NI-04 | auth-service ตอบผิดปกติไม่ถือเป็น "token ใช้ไม่ได้" | stub ตอบ `500`, HTML, JSON ผิดรูป | `IdentityUnavailable` ทั้งสามแบบ (→ `503` ไม่ใช่ `401`) |
| NI-05 | auth-service ช้าเกิน | stub หน่วง 1 วินาที, timeout 0.2 วินาที | `IdentityUnavailable` |
| NI-06 | ต่อ auth-service ไม่ติด | พอร์ตที่ไม่มีใครฟัง | `IdentityUnavailable` |
| NI-07 | อ่านที่อยู่จาก env | `AUTH_SERVICE_URL=http://auth-service:5002/` | เรียก `http://auth-service:5002/auth/me` |
| NI-08 | ต่อครบสอง service | สมัคร → login → อัปโหลด (แนบ `uploader_name` ปลอม) → logout → อัปโหลดซ้ำ | `201` ด้วยชื่อจากบัญชี แล้ว `401` · มีโน้ตใบเดียว |

**ตรวจว่าเทสต์จับบั๊กได้จริง (2026-09-27):** ลองแก้ `POST /notes` ให้ปล่อยผ่านเมื่อ token ใช้ไม่ได้
(ใส่บัญชี anonymous แทนการตอบ 401) มี 5 เทสต์ fail — NA-20 ทั้งสามแบบ, NA-21 และ NI-08 — จากนั้น revert แล้วผ่านครบ

### 2.11 Auth Service — `email_error()` โดยตรง (`pytest`, US-05 #5, Lab 12B)

ไฟล์ [`test_email_error.py`](../../src/tests/test_email_error.py) — เรียก `email_error()` ตรง ๆ ไม่ผ่าน `validate_registration()`
ชุด AC-03 ถึง AC-05 ใน 2.7 ทดสอบอีเมลผ่านการ normalize เสมอ ไฟล์นี้ตรึงสัญญาของฟังก์ชันเอง
(รับค่าที่ normalize แล้ว, ขอบความยาว 254 ทั้งสองฝั่ง, ข้อความเมื่อตั้งหลายโดเมน) · coverage ของ `credentials.py`
เป็น 100% อยู่แล้วก่อนเพิ่มชุดนี้ จึงไม่ได้ทำให้ตัวเลขขึ้น

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| AE-01 | อีเมลมหาวิทยาลัยผ่าน | `67026168@up.ac.th` | `None` |
| AE-02 | โดเมนที่สองที่อนุญาตผ่าน | `x@ict.up.ac.th` กับ (`up.ac.th`, `ict.up.ac.th`) | `None` |
| AE-03 | ยาวพอดีเพดาน | 254 ตัวอักษร | `None` (ขอบฝั่งที่ต้องผ่าน — AC-05 เช็คแค่ 255) |
| AE-04 | ยาวเกินเพดาน 1 ตัว | 255 ตัวอักษร | `"ยาวเกิน 254 ตัวอักษร"` |
| AE-05 | ไม่ normalize เอง | `A@UP.AC.TH` | error โดเมน — คนเรียกต้องแปลงเป็นตัวพิมพ์เล็กก่อน |
| AE-06 | ค่าว่าง | `""` | `"จำเป็นต้องกรอก"` |
| AE-07 | whitespace ที่ไม่ใช่ช่องว่าง | `a\t@up.ac.th` | `"รูปแบบอีเมลไม่ถูกต้อง"` |
| AE-08 | ข้อความ error บอกครบทุกโดเมน | `x@gmail.com` กับ (`up.ac.th`, `ict.up.ac.th`) | `"ต้องใช้อีเมลของมหาวิทยาลัย (@up.ac.th, @ict.up.ac.th)"` |
| AE-09 | มี `@` แต่ไม่มีโดเมน | `a@` | `"รูปแบบอีเมลไม่ถูกต้อง"` — **xfail**: โค้ดตอนนี้คืน error โดเมน เพราะเช็ค local ว่างแต่ไม่เช็ค domain ว่าง ทีมตกลงว่าเป็นบั๊ก ยังไม่ได้แก้ `credentials.py` · ตั้ง `strict=True` ไว้ ถ้าแก้แล้วเทสต์ผ่าน CI จะแดงเตือนให้เอา xfail ออก |

### 2.12 Notes Service — preview (`pytest`, US-11 #11)

ไฟล์ [`test_notes_preview.py`](../../src/tests/test_notes_preview.py) ครอบทั้ง `GET /notes/<id>/preview`
และ `render_preview()` ที่เป็น pure function แยกออกมา (แนวเดียวกับ `validation.py`) ไม่รู้จัก Flask/DB/storage
เลย จึงทดสอบตรง ๆ ได้ · ครอบ AC ข้อ 1–2 ของ #11 ฝั่ง backend เท่านั้น ส่วน AC ข้อ 3 (ปิดตัวอย่างแล้วกลับ
ตำแหน่งเดิมในผลค้นหา) เป็นงาน UI ยังไม่อยู่ในชุดนี้

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| NP-01 | รูป PNG ได้ตัวอย่างที่ย่อขนาดแล้วเป็น PNG | อัปโหลด PNG 1600x1200 | `200`, `image/png`, กว้าง `PREVIEW_MAX_WIDTH` (800) |
| NP-02 | รูป JPEG ก็ได้กลับมาเป็น PNG เสมอ | อัปโหลด JPEG | `200`, `image/png` |
| NP-03 | แสดงผลแบบ inline และแคชได้ | `GET .../preview` | ไม่มี `attachment` ใน `Content-Disposition`, `Cache-Control: public, max-age=86400` |
| NP-04 | render ครั้งแรกแล้วเสิร์ฟจาก cache ครั้งถัดไป | เรียกซ้ำหลังลบไฟล์ต้นฉบับ | ได้ไบต์เดิมทั้งสองครั้ง มีไฟล์ตัวอย่างแค่ไฟล์เดียวใน `previews/` |
| NP-05 | PDF ได้ตัวอย่างจากหน้าแรกเท่านั้น | PDF 2 หน้าคนละขนาด | ขนาดรูปตรงกับหน้า 1 ที่สเกลแล้ว ไม่ใช่หน้า 2 |
| NP-06 | ตัวอย่างของ PDF ก็ถูกแคชเหมือนรูป | เรียก `.../preview` ของโน้ต PDF | มีไฟล์ตัวอย่างในโฟลเดอร์ `previews/` |
| NP-07 | PDF ปลอม (ไม่ใช่ PDF จริง) | เนื้อไฟล์ `%PDF-1.4 fake note` | `422 {"error": "preview_unavailable"}` |
| NP-08 | โน้ตที่ไม่มีอยู่ | `GET /notes/999/preview` | `404 {"error": "not_found"}` |
| NP-09 | ไฟล์ต้นฉบับหายจาก storage | ลบไฟล์ทิ้งก่อนขอตัวอย่าง | `404 {"error": "file_not_found"}` |
| NP-10 | ไฟล์ประกาศเป็นรูปแต่เนื้อไม่ใช่ | อัปโหลด `image/png` ที่เนื้อเป็นข้อความ | `422 {"error": "preview_unavailable"}` (ไม่ใช่ `500`) |
| NP-11 | render ไม่สำเร็จต้องไม่ทิ้งอะไรไว้ใน storage | เหมือน NP-10 | โฟลเดอร์ `previews/` ว่างหรือไม่มี |
| NP-12 | ลบโน้ตแล้วลบตัวอย่างตามไปด้วย | สร้างตัวอย่างก่อน แล้ว `DELETE` โน้ต | ทั้งไฟล์ต้นฉบับและไฟล์ใน `previews/` หายหมด |
| NP-13 | response ของโน้ตมี `preview_url` | `GET /notes/<id>`, `GET /notes` | `preview_url == "/notes/<id>/preview"` ทั้งสอง endpoint |
| NP-14 | ไม่ขยายรูปที่เล็กกว่าเพดานอยู่แล้ว | รูป 300x200 | ขนาดคงเดิม ไม่ถูกขยาย |
| NP-15 | JPEG โหมด CMYK ถูกแปลงเป็น PNG ได้ | รูป CMYK | ได้ PNG จริง ไม่ throw |
| NP-16 | คงความโปร่งใสของ PNG โหมด RGBA | รูป RGBA | ผลลัพธ์ยังเป็นโหมด `RGBA` |
| NP-17 | ปฏิเสธรูปที่ใหญ่เกิน `MAX_SOURCE_PIXELS` (กัน decompression bomb) | รูปเกิน 50 ล้านพิกเซล | `PreviewUnavailable` |
| NP-18 | ปฏิเสธไฟล์รูปที่เสีย (truncate) | ตัดไฟล์ PNG ให้ขาด | `PreviewUnavailable` |
| NP-19 | ปฏิเสธเมื่อ content type ไม่ตรงเนื้อไฟล์จริง | ประกาศ `image/jpeg` แต่เนื้อเป็น PNG | `PreviewUnavailable` |
| NP-20 | ปฏิเสธ content type ที่ยังไม่รองรับ | `text/plain` | `PreviewUnavailable` |
| NP-21 | PDF render เฉพาะหน้าแรกเท่านั้น | PDF 2 หน้าคนละขนาด | ขนาดตรงกับหน้า 1 ที่สเกล 2 เท่า |
| NP-22 | PDF ไม่ถูกขยายเกินความกว้างสูงสุด | หน้ากว้าง 2000pt | กว้างไม่เกิน `PREVIEW_MAX_WIDTH` |
| NP-23 | ปฏิเสธ PDF ที่ไม่มีหน้าเลย | PDF 0 หน้า | `PreviewUnavailable` |
| NP-24 | ปฏิเสธหน้าแรกที่ใหญ่ผิดปกติ | หน้าขนาด 100x300000pt | `PreviewUnavailable` |
| NP-25 | ปฏิเสธ PDF ที่เสีย (truncate) | ตัดไฟล์ PDF ให้ขาด | `PreviewUnavailable` |
| NP-26 | รูปจากกล้องมือถือหมุนตาม EXIF Orientation ก่อนย่อขนาด | JPEG 1200x800 ที่มี `exif[0x0112] = 6` | ผลลัพธ์เป็นแนวตั้ง 800x1200 ไม่ใช่แนวนอนตะแคง |
| NP-27 | PDF หน้า A4 ไม่เกินความกว้างสูงสุดแม้ pdfium ปัดพิกเซลขึ้น | หน้า A4 (595x842pt) | กว้างไม่เกิน `PREVIEW_MAX_WIDTH` |

**รันแยกยืนยัน (2026-09-29):** `pytest src/tests/test_notes_preview.py -v` ✅ 27 passed / 0 failed (~2 วิ)
รันด้วย Python 3.13 เพราะเครื่องที่ใช้เขียนมี Python 3.14 เป็นค่าเริ่มต้น ซึ่ง SQLAlchemy เวอร์ชันที่ pin ไว้ยังใช้กับ
3.14 ไม่ได้ (`TypeError` ใน `sqlalchemy.util.typing`) — ไม่เกี่ยวกับโค้ดของ #11 · CI ใช้ Python 3.12 ตามที่ตั้งไว้ใน
`ci.yml` จึงไม่เจอปัญหานี้ · การ render ภาพจริง (PNG/PDF ผ่าน docker compose, PDF ปลอมได้ 422) เคย verify
ผ่าน container จริงมาแล้วตอนแก้ Dockerfile (commit `8f25b9b`)

### 2.13 Web app — `search-utils.js` (`node --test`, US-11 #11 + US-31 #31)

pure function ของหน้าค้นหาใน [`web/`](../../web/) แยกออกจากส่วนที่แตะ DOM (`app.js`) ไว้ให้เทสต์ได้โดยไม่ต้องมี browser

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| WEB-01 | `buildQuery` ไม่ใส่ช่องว่างและ sort ค่าเริ่มต้น | ตัวกรองว่างทั้งหมด, `q = '  '` | ได้ `''` |
| WEB-02 | `buildQuery` trim ข้อความและส่งตัวกรองของ API ครบ | `q=' CS201 '`, `faculty`, `year_level`, `topic`, `date_from`, `date_to`, `sort=title` | query string ตรงตามลำดับ ไม่มีช่องว่างหัวท้าย |
| WEB-03 | `buildQuery` ส่ง `file_type` ซ้ำตามจำนวนที่เลือก และตัดค่าที่ API ไม่รู้จัก | `['pdf', 'jpeg', 'png']` | `file_type=pdf&file_type=png` (ไม่ส่ง `jpeg` ที่ API ตอบ `400`) |
| WEB-04 | `buildQuery` ใส่ paging เฉพาะเมื่อขอ | `{limit: 20, offset: 0}`, `{limit: 20, offset: 40}` | `limit=20` (ไม่มี `offset=0`), `limit=20&offset=40` |
| WEB-05 | `parseQuery` อ่านกลับได้ค่าเดิม (URL ↔ ฟอร์ม) | ผลของ `buildQuery` | ได้ตัวกรองชุดเดิมทุกช่อง |
| WEB-06 | `parseQuery` กลับไปค่าเริ่มต้นเมื่อเจอ sort/ประเภทไฟล์ที่ไม่รู้จัก | `?sort=rating&file_type=docx&file_type=pdf&file_type=pdf` | `sort = new`, `file_type = ['pdf']` (ตัดซ้ำด้วย) |
| WEB-07 | `escapeHtml` กัน markup และรับ null | `<img src=x onerror="a()">`, `null` | escape ครบ, ได้ `''` |
| WEB-08 | `formatSize` เลือกหน่วยที่อ่านง่าย | 512, 2048, 3 MB | `512 B`, `2.0 KB`, `3.0 MB` |
| WEB-09 | `fileTypeLabel` บอกชื่อประเภทไฟล์ที่รับ | `application/pdf`, `image/jpeg`, `text/plain` | `PDF`, `JPG`, `ไฟล์` |
| WEB-10 | การ์ดโน้ตแสดงชื่อผู้อัปโหลดเสมอ (US-31 AC3) | โน้ตที่มี `uploader_name = Somchai` | มี `อัปโหลดโดย <strong>Somchai</strong>` และปุ่ม `data-preview-id` |
| WEB-11 | การ์ดโน้ต escape ค่าที่ผู้ใช้คนอื่นพิมพ์มา | `title = <script>…`, `uploader_name = "><img src=x>` | ไม่มีแท็ก `<script>`/`<img` หลุดออกมา |
| WEB-12 | การ์ดโน้ตข้ามช่องที่ไม่มีค่า | `topic = null`, `class_date = null` | ไม่มีคำว่า `null` และไม่มีบรรทัดวันที่เรียน |
| WEB-13 | `errorMessage` บอกชื่อช่องที่ผิดเมื่อ `invalid_filter` | `400 {error: invalid_filter, field: date_to}` | ข้อความมี "วันที่สิ้นสุด" |
| WEB-14 | `errorMessage` ครอบ preview, โน้ตหาย และเน็ตหลุด | `422 preview_unavailable`, `404 not_found`, status `0`, `502` ไม่มี body | ข้อความเฉพาะของแต่ละกรณี · `502` บอกเลข HTTP |
| WEB-15 | `hasMore` เป็นจริงเฉพาะหน้าที่เต็ม | 20, 19, 0 | `true`, `false`, `false` (API ไม่มียอดรวม) |

**ตรวจบน browser จริง (2026-10-01, ด้วยมือ ยังไม่ใช่ E2E อัตโนมัติ):** Docker ไม่ได้เปิดบนเครื่องที่ใช้เขียน จึงรัน
`auth-service` กับ `notes-service` ตัวจริงบน SQLite และใช้สคริปต์ Python ที่ทำตัวแทน `web/nginx.conf` (path เดียวกัน)
แล้วเปิดใน Chrome ผล: ค้นหา/กรอง/เรียงได้ผลจาก API จริง · โหลดเพิ่มจาก 20 → 25 แล้วปุ่มหาย · เปิด preview จากการ์ดที่ 22
แล้วปิดด้วย Esc, คลิกฉากหลัง และปุ่ม ✕ ตำแหน่ง scroll เท่าเดิม (2397 px) การ์ดยังอยู่ 25 ใบ focus กลับไปที่ปุ่มเดิม (US-11 AC3)
· PNG ปลอมแสดงข้อความ preview ไม่ได้แทนรูปแตก · ช่วงวันที่กลับด้านแสดง error ชื่อช่อง · back คืนค่าฟอร์มเดิม · ชื่อโน้ตที่มี
`<script>` แสดงเป็นข้อความ · ค้นด้วยคำภาษาไทยได้ · console ไม่มี error · ตัว nginx จริงยืนยันผ่าน DK-08 บน CI

### 2.14 Web app — `session-utils.js` + `upload-utils.js` (`node --test`, US-05 #5 + US-06 #6 + US-08 #8 + US-31 #31)

pure function ของหน้าเข้าสู่ระบบและหน้าอัปโหลดใน [`web/`](../../web/) แยกจากส่วนที่แตะ DOM (`site.js`, `login.js`, `upload.js`)
· storage ถูกส่งเข้าฟังก์ชัน จึงใช้ object ธรรมดาแทน `sessionStorage` ในเทสต์ได้

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| WEB-16 | `sessionFromLogin` เก็บ token วันหมดอายุ และชื่อผู้ใช้จาก `POST /auth/login` | body จริงของ login | ได้ `{token, expiresAt, user: {id, email, display_name}}` ไม่เก็บ `created_at` |
| WEB-17 | `sessionFromLogin` ไม่รับ body ที่ไม่ครบ | `null`, token ว่าง, `expires_at = 'soon'`, `user = null` | ได้ `null` ทุกกรณี |
| WEB-18 | `saveSession` แล้ว `loadSession` ได้ session เดิมก่อนหมดอายุ | session ที่หมดอายุ 18:00, เวลาตอนนี้ 10:00 | ได้ค่าเดิม |
| WEB-19 | `loadSession` ลบ session ที่หมดอายุแล้ว | เวลาตอนนี้ = `expires_at` พอดี | ได้ `null` และ key `noteshare.session` ถูกลบ |
| WEB-20 | `loadSession` ลบ session ที่อ่านไม่ออก | `'not json'`, `'{}'`, `expiresAt = 'later'` | ได้ `null` และ key ถูกลบทุกกรณี |
| WEB-21 | storage ใช้ไม่ได้ = ยังไม่ได้เข้าสู่ระบบ | storage ที่ throw ทุก method, `null` | `loadSession` ได้ `null`, `saveSession` ได้ `false`, `clearSession` ไม่ throw |
| WEB-22 | `clearSession` ทำให้ออกจากระบบ | session ที่บันทึกไว้ | `loadSession` ได้ `null` |
| WEB-23 | `authHeaders` ส่ง token เป็น Bearer | session, `null` | `{Authorization: 'Bearer …'}`, `{}` |
| WEB-24 | `safeNextPath` รับเฉพาะหน้าของเว็บนี้และเก็บ query string ไว้ | `/upload.html`, `/?q=CS201&year_level=2`, `/index.html` | ได้ค่าเดิม |
| WEB-25 | `safeNextPath` กัน open redirect | `null`, `''`, `upload.html`, `https://evil.example/`, `//evil.example/…`, `/\evil.example`, `javascript:…`, `/login.html`, `/notes/1/download` | ได้ `/` ทุกกรณี |
| WEB-26 | `loginUrl` แนบหน้าที่จะกลับไป | `/upload.html`, `https://evil.example/` | `/login.html?next=%2Fupload.html`, `/login.html?next=%2F` |
| WEB-27 | `fieldErrors` อ่านเหตุผลรายช่องของ `validation_failed` | `{fields: {email, password}}`, `invalid_credentials`, `null`, `fields` เป็น array | ได้ object ของช่องที่ผิด, `{}` ในกรณีอื่น |
| WEB-28 | `authErrorMessage` ครอบทุก error ของ auth-service | `invalid_credentials`, `email_taken`, `validation_failed`, `unauthorized`, `auth_unavailable`, status `0`, `502` | login ผิดใช้ `message` ของ service · ข้อความเฉพาะของแต่ละกรณี · `502` บอกเลข HTTP |
| WEB-29 | `validateUpload` ผ่านเมื่อกรอกครบและแนบ PDF | ฟอร์มครบ + PDF 1 KB | ได้ `{}` |
| WEB-30 | `validateUpload` รายงานทุกช่องบังคับที่ขาดพร้อมไฟล์ในครั้งเดียว | `title = '   '`, ไม่มีไฟล์ | error ครบ 6 ช่อง + `file = ต้องแนบไฟล์โน้ต` |
| WEB-31 | `validateUpload` ใช้เพดานความยาวเดียวกับ `validation.py` | title 201, subject_code 31, topic 201 ตัวอักษร · title 200 ตัวอักษร | `ยาวเกิน 200/30/200 ตัวอักษร` · 200 ตัวผ่าน |
| WEB-32 | `validateUpload` รับชั้นปี 1–8 เท่านั้น | `0`, `9`, `two`, `8` | `ต้องอยู่ระหว่าง 1-8` ×2, `ต้องเป็นตัวเลข`, ผ่าน |
| WEB-33 | `validateUpload` ตรวจวันที่เรียนเป็นวันจริงแบบ `YYYY-MM-DD` | `2026-08-20`, `20/08/2026`, `2026-02-30`, `2026-13-01` | ผ่าน, ที่เหลือได้ `ต้องเป็นรูปแบบ YYYY-MM-DD` |
| WEB-34 | `validateUpload` รับ PDF/PNG/JPG เท่านั้น | `image/png`, `image/jpeg` · `application/msword`, `image/gif`, type ว่าง | ผ่าน · `รองรับเฉพาะไฟล์ PDF, PNG และ JPG` |
| WEB-35 | `validateUpload` ไม่รับไฟล์ว่างและไฟล์เกิน 20 MB | 0 byte, 20 MB + 1 byte, 20 MB พอดี | `ไฟล์ว่าง`, `ไฟล์ใหญ่เกิน 20 MB`, ผ่าน |
| WEB-36 | `uploadFields` trim ค่าและไม่ส่งช่องไม่บังคับที่ว่าง | `title = '  Calc  '`, `topic` มีค่า, `class_date`/`description` ว่าง, มี `uploader_name` ปนมา | ได้เฉพาะ 6 ช่องบังคับ + `topic` ที่ trim แล้ว ไม่มี `uploader_name` (US-31) |
| WEB-37 | `uploadErrorMessage` ครอบ error ของ notes-service และเพดานของ gateway | `400 validation_failed`, `401 unauthorized`, `503 auth_unavailable`, `413` ไม่มี body, status `0`, `500` | ข้อความเฉพาะของแต่ละกรณี · `413` = `ไฟล์ใหญ่เกิน 20 MB` |
| WEB-38 | `searchUrlFor` เปิดหน้าค้นหาที่โน้ตที่เพิ่งอัปโหลด | `title = 'Linked List & Stack'` | `/?q=Linked+List+%26+Stack` |

**ตรวจบน browser จริง (2026-10-02, ด้วยมือ ยังไม่ใช่ E2E อัตโนมัติ):** Docker ไม่ได้เปิด จึงรัน `auth-service` กับ `notes-service`
ตัวจริงบน SQLite และใช้สคริปต์ Python ที่ทำตัวแทน `web/nginx.conf` (เสิร์ฟเฉพาะไฟล์ที่ `web/Dockerfile` copy) แล้วเปิดใน Chrome ผล:
เปิด `/upload.html` ตอนยังไม่เข้าสู่ระบบถูกพาไป `/login.html?next=%2Fupload.html` · สมัครแบบไม่กรอกอะไรได้ error ใต้ทั้ง 3 ช่องจาก service
· อีเมล `@gmail.com` กับรหัสผ่าน 5 ตัวได้เหตุผลตรงช่อง · สมัครสำเร็จแล้วเข้าสู่ระบบต่อเองและกลับไปหน้าอัปโหลด แถบเมนูแสดงชื่อภาษาไทย
· ส่งฟอร์มอัปโหลดว่างได้ error ครบ 7 ช่องโดยไม่มี request ไป `/notes` · แนบ `.txt` ได้ error ที่ช่องไฟล์ · อัปโหลด PNG สำเร็จ ชื่อโน้ตที่มี
`<b>` แสดงเป็นข้อความ · ปุ่มคัดลอกรหัสแก้ไขขึ้น "คัดลอกแล้ว" · "ดูในหน้าค้นหา" เจอโน้ตพร้อมชื่อผู้อัปโหลด และ preview แสดงภาพ
· ออกจากระบบได้ `204` แล้ว token เดิมเรียก `/auth/me` ได้ `401` · login ด้วยรหัสผิดได้ข้อความกลาง ๆ และช่องรหัสผ่านถูกล้าง · login ด้วยอีเมล
ตัวพิมพ์ใหญ่ปนแล้วกลับหน้าค้นหาพร้อมคำค้นเดิม · เพิกถอน session จากที่อื่นแล้วกดอัปโหลดได้ข้อความพร้อมลิงก์เข้าสู่ระบบ ข้อมูลในฟอร์มยังอยู่
และไม่มีโน้ตถูกสร้าง · "อัปโหลดอีกไฟล์" ล้างรหัสออกจากหน้าจอและล้างฟอร์ม · เปิด `/login.html?next=https%3A%2F%2Fevil.example%2F`
ตอนเข้าสู่ระบบอยู่แล้วไปที่ `/` · ออกจากระบบจากหน้าอัปโหลดกลับหน้าค้นหา · console ไม่มี error · DK-08 ตัวใหม่รันผ่านกับตัวแทน nginx
(`gateway OK`) ตัว nginx จริงยืนยันบน CI · ยังไม่ได้ตรวจบนหน้าจอมือถือ

## 3. Test Report

**รันล่าสุด:** 2026-09-27 (เครื่อง local, Windows 11, branch `feature/safety-net`)

| ชุด | คำสั่ง | ผล |
| --- | --- | --- |
| JS unit | `cd prototypes/sprint1 && node --test` | ✅ 7 passed / 0 failed (69 ms) |
| Python unit + integration | `pytest src/tests -v` | ✅ 233 passed / 0 failed / 1 xfailed — stats 9, notes validation 18 + boundary 19, notes API 47, notes identity 13, edit-token property 2, fizzbuzz 5, auth credentials 29, auth email_error 9 (AE-09 เป็น xfail), auth tokens 14, auth API 30 · coverage รวม 99% (`identity.py` 100%, `credentials.py` 100%) |
| Smoke DK-03 ถึง DK-06 แบบไม่ใช้ Docker | รัน `auth-service` กับ `notes-service` ตัวจริงบน SQLite (notes ชี้ `AUTH_SERVICE_URL` ไปที่ auth) แล้วรันสคริปต์ `run:` ของแต่ละ step ที่ดึงออกมาจาก `ci.yml` ตรง ๆ | ✅ ผ่านครบ 6 step (`upload auth OK`, `end-to-end OK`, `edit/delete OK`, `auth OK`, validation `400`) · บน Postgres + compose จริงรอผลจาก CI เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน · ตอนรันบน Windows ต้องแทน `/tmp/` เป็น path ของ Windows เพราะ curl ของ Windows อ่าน `/tmp` ของ Git Bash ไม่ได้ (ไม่ได้แก้ใน `ci.yml` เพราะ CI รันบน Linux) |
| Container smoke (compose e2e) | `docker compose up` + `curl` | ✅ ผ่านบน CI ([run #33351842320](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/33351842320), 1m6s) — log ยืนยัน `created note #1` และ `end-to-end OK` · ไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน |
| JS unit (web) | `cd web && node --test` | ✅ 38 passed / 0 failed (2026-10-02, branch `feature/web-login-upload`) — search-utils 15, session-utils 13, upload-utils 10 |

**ผลรันบน CI (PR #56):** ทั้ง 3 job ผ่านหมด — `js-tests` 13s, `python-tests` 13s, `docker-build` 1m6s

CI จับของจริงไปแล้ว 2 ครั้งตั้งแต่ตั้งขึ้นมา ทั้งที่เทสต์ในเครื่องเขียวหมด:
1. PR ที่ base เป็น feature branch อื่นไม่ถูกทดสอบเลย เพราะ trigger กรองไว้แค่ `branches: [main]` → เอาตัวกรองออกจาก `pull_request`
2. `printf '%PDF-1.4 ...'` ใน smoke test ล้มเพราะ `%P` ถูกตีความเป็น format specifier → เปลี่ยนเป็น `printf '%s'`

> DK-01 เคยผ่านมาแล้วตอน Lab 6 (build + push ขึ้น Docker Hub สำเร็จ ดู [`docker/README.md`](../../docker/README.md))
> รอบนี้เพิ่ม DK-02/DK-03 เข้ามาเป็น smoke test อัตโนมัติใน CI ซึ่ง Lab 6 ยังทำด้วยมือ

## 4. CI

[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) รันทุก push เข้า `main` และทุก PR ที่ยิงเข้า `main`
โดยแบ่งเป็น 3 job เพื่อให้อ่านผลได้ว่าอะไรพัง

```
js-tests ──┐
           ├──> docker-build (รันต่อเมื่อสองอันแรกผ่าน)
python-tests ─┘
```

`docker-build` ตั้ง `needs: [js-tests, python-tests]` ไว้ เพราะไม่มีประโยชน์ที่จะเสียเวลา build image
ถ้าเทสต์ยังแดงอยู่

## 5. งานที่ยังค้าง

- [ ] **วชิรวิทย์** — เขียน unit test ของตัวเอง (เสนอ: logic filter คณะ/ปี/ประเภทไฟล์ และประวัติการค้นหาใน `wachirawit_search_note_prototype.html` ต้องแยก pure function ออกมาก่อนแบบเดียวกับ Lab 7)
- [ ] **กฤตเมธ** — เขียน unit test ของตัวเอง (เสนอ: การคำนวณคะแนนเฉลี่ยหลังส่ง rating ใน `kittamet_note_rating_prototype.html`)
- [x] เขียนเทสต์ของ `POST /notes` ที่ commit ไม่ผ่าน แล้วต้องไม่ทิ้งไฟล์กำพร้าไว้ใน storage — NA-12
- [ ] เทสต์ที่รันกับ PostgreSQL จริง — ตอนนี้เทสต์ Python ใช้ SQLite ส่วน compose ใช้ Postgres จึงมีช่องว่างเรื่องความต่างของ dialect (`ilike`, การเทียบวันที่) ที่จับได้แค่ตอน smoke test
- [ ] เพิ่ม branch protection ให้ `main` ต้องผ่าน CI ก่อน merge (ตั้งใน GitHub Settings ไม่ใช่ในโค้ด)
- [ ] E2E test อัตโนมัติผ่าน browser — มีหน้าเว็บจริงแล้ว (`web/`) แต่ยังตรวจด้วยมือ (ดูท้าย 2.13) ยังไม่มีเครื่องมืออย่าง Playwright ใน CI
