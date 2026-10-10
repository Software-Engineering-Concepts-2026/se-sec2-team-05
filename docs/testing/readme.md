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
| Integration (API) บน PostgreSQL | เทสต์ Python ชุดเดียวกันทั้งหมด แต่ต่อ PostgreSQL 16 จริงแทน SQLite (ตั้ง `TEST_DATABASE_URL`) | `pytest` + service container ของ GitHub Actions | จับความต่างของ dialect ที่ SQLite ซ่อนไว้ เช่น `LIKE` สนตัวพิมพ์, foreign key, ชนิดวันที่ — ก่อนหน้านี้จับได้แค่ตอน smoke test หรือตรวจด้วยมือ |
| E2E (browser) | เส้นทางหลักของผู้ใช้ผ่านหน้าเว็บจริงบน stack ของ compose: สมัคร → อัปโหลด → ค้นหา → อีกบัญชีใช้โน้ต → แก้/ลบด้วยรหัส + ความกว้างมือถือ | Playwright (Python) + `pytest` บน Chromium | กดหน้าเว็บแบบเดียวกับผู้ใช้ จับปัญหาที่ unit test ของ `*-utils.js` มองไม่เห็น เช่นปุ่มไม่ขึ้น ลิงก์ผิด หรือ CSS ล้นจอ · ใช้ Python เหมือนเทสต์ฝั่ง service ไม่ต้องเพิ่ม `package.json` |
| Smoke (container) | ทั้ง stack (`docker compose up`) ตอบ health และวิ่งครบเส้น upload → filter → download | `docker compose` + `curl` ใน CI | จับปัญหาที่ unit test มองไม่เห็น เช่น gunicorn/CMD พัง, service ต่อ Postgres ไม่ติด, volume ไม่ mount |

**ยังไม่ทำในรอบนี้:** load/performance test, security scan · E2E ผ่านเบราว์เซอร์เพิ่มแล้ว 2026-10-08 (หัวข้อ 2.21)

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
| PY-08 | เจ้าของโน้ตดูสถิติได้ | `GET /notes/<id>/stats` ด้วยบัญชีเจ้าของ | `200` + `note_id`, `views`, `downloads`, `thanks` (ยังไม่มีใครขอบคุณ = `0`) |
| PY-09 | view และ download แยกจากกัน | `GET /notes/<id>` แล้วตรวจ counters | `view_count` เพิ่ม โดย `download_count` ไม่เพิ่ม |
| PY-10 | เจ้าของเห็นจำนวนคำขอบคุณของโน้ตนั้นเท่านั้น (US-28 AC3) | โน้ต A มีคำขอบคุณ 2 ครั้ง โน้ต B มี 1 ครั้ง → เจ้าของแต่ละคน `GET /notes/<id>/stats` | A ได้ `thanks = 2` · B ได้ `thanks = 1` |
| PY-11 | คนที่ไม่ใช่เจ้าของไม่เห็นจำนวนคำขอบคุณ (US-28 AC3) | `GET /notes/<id>/stats` ด้วยบัญชีอื่น ขณะโน้ตมีคำขอบคุณ | `403` และไม่มีคีย์ `thanks` |

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
| NV-13 | ไฟล์ใหญ่เกิน 10 MB (NFR-006, ADR-012) | 10 MB + 1 byte | ถูกปฏิเสธ |
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
| NA-26 | เจ้าของที่ login อยู่แก้/ลบได้ — ทางเดียวที่เหลือ (ADR-008, ADR-013) | `PATCH` ด้วย Bearer ของเจ้าของ, `DELETE` ด้วย Bearer ของเจ้าของ | `200`, `204` |
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
| NA-74 | ลบ Note ยังคงทำงานเมื่อมี report ผูกอยู่ | ลบ Note ด้วยบัญชีเจ้าของหลังสร้าง report | Note และ report ที่ผูกผ่าน FK ถูกลบตาม cascade |
| NA-75 | เปิดดู Note ขณะเข้าสู่ระบบแล้วมีสิทธิ์ให้คะแนน | authenticated `GET /notes/<id>` | บันทึก eligibility ของผู้ใช้สำหรับ Note นั้น |
| NA-76 | ดาวน์โหลด Note ขณะเข้าสู่ระบบแล้วมีสิทธิ์ให้คะแนน | authenticated download | บันทึก eligibility ของผู้ใช้สำหรับ Note นั้น |
| NA-77 | ผู้ใช้ที่ไม่ได้เข้าสู่ระบบเปิดดู Note | unauthenticated `GET /notes/<id>` | ไม่บันทึก user eligibility |
| NA-78 | ผู้ใช้ที่มีสิทธิ์สามารถสร้าง Rating ได้ | `PUT /notes/<id>/rating` ด้วยค่า `1-5` | `200` และสร้าง Rating |
| NA-79 | Rating รองรับค่าตาม scale 1-5 | `PUT /notes/<id>/rating` ด้วยค่า `1-5` | รับค่าทั้ง 5 ระดับได้ |
| NA-80 | Rating ที่อยู่นอกช่วงไม่ถูกยอมรับ | `PUT /notes/<id>/rating` ด้วยค่าต่ำกว่า 1 หรือมากกว่า 5 | `400 validation` |
| NA-81 | ผู้ใช้ให้คะแนน Note เดิมซ้ำได้โดยการแก้ไข | `PUT /notes/<id>/rating` ซ้ำโดยผู้ใช้เดิม | อัปเดต Rating เดิม ไม่สร้างแถวใหม่ |
| NA-82 | แสดงค่าเฉลี่ย Rating ใน Note | `GET /notes` และ `GET /notes/<id>` | มี `average_rating` และ `rating_count` |
| NA-83 | ผู้ใช้ที่ยังไม่มี eligibility ไม่สามารถให้คะแนน | authenticated `PUT /notes/<id>/rating` | `403 forbidden` |
| NA-84 | การให้คะแนนต้องผ่าน authentication | unauthenticated `PUT /notes/<id>/rating` | `401 unauthorized` |
| NA-85 | ให้คะแนน Note ที่ไม่มีอยู่ | `PUT /notes/<unknown_id>/rating` | `404 not_found` |
| NA-86 | Auth Service ใช้งานไม่ได้ระหว่างให้คะแนน | `PUT /notes/<id>/rating` เมื่อ auth-service unavailable | `503 auth_unavailable` |
| NA-87 | Rating ของผู้ใช้แต่ละคนแยกจากกัน | ผู้ใช้หลายคนให้คะแนน Note เดียวกัน | Rating และ `user_rating` ของแต่ละคนไม่ปะปนกัน |
| NA-88 | ลบ Note แล้วลบ access และ Rating ที่เกี่ยวข้อง | ลบ Note ที่มี access/Rating | access และ Rating ของ Note นั้นถูกลบตาม |
| NA-89 | admin เห็นโน้ตที่ถูกรายงานในรายการรายงาน (Issue #18) | `GET /reports` ด้วย admin หลังสมาชิกสองคนรายงานโน้ตเดียวกัน | แต่ละ report มี object `note` (`id`, `title`) พร้อมเหตุผลและผู้รายงาน |
| NA-90 | admin ลบโน้ตที่ถูกรายงานได้ (Issue #18) | `DELETE /reports/<report_id>/note` ด้วย admin | `204` · Note หาย (`GET /notes/<id>` → `404`) และ report ของโน้ตนั้นถูกลบตาม |
| NA-91 | ลบโน้ตที่ถูกรายงานแล้วไฟล์ใน storage ถูกลบด้วย (Issue #18) | อัปโหลดโน้ต → รายงาน → admin `DELETE /reports/<report_id>/note` | `204` · ไม่เหลือไฟล์ใน storage |
| NA-92 | ลบโน้ตที่ถูกรายงานไม่กระทบโน้ตหรือ report อื่น (Issue #18) | มีสองโน้ตและสอง report → ลบผ่าน report ของโน้ตแรก | โน้ตแรก `404` · โน้ตที่สองและ report ของมันยังอยู่ |
| NA-93 | สมาชิกทั่วไปลบโน้ตผ่าน report ไม่ได้ (Issue #18) | `DELETE /reports/<report_id>/note` ด้วย member | `403 forbidden` · Note และ report ยังอยู่ |
| NA-94 | action ของ admin ต้อง login (Issues #17, #18) | `GET /reports`, `DELETE /reports/<id>`, `DELETE /reports/<id>/note` ไม่มี Bearer token | `401 unauthorized` + `WWW-Authenticate: Bearer` |
| NA-95 | auth-service ล่มตอน admin ลบโน้ต (Issue #18) | identity โยน `IdentityUnavailable` แล้ว `DELETE /reports/<id>/note` | `503 auth_unavailable` |
| NA-96 | ลบโน้ตผ่าน report ที่ไม่มีอยู่ (Issue #18) | admin `DELETE /reports/99999/note` | `404 not_found` |
| NA-97 | ขอบคุณเจ้าของโน้ตครั้งแรก (US-28) | Bob `POST /notes/<id>/thanks` โน้ตของ Alice | `201` + `note_id`, `thanked = true`, `thanked_at` |
| NA-98 | กดขอบคุณซ้ำไม่เพิ่มยอด | `POST .../thanks` สองครั้ง | ครั้งที่สอง `200` · `thanked_at` เท่าเดิม · ตาราง `thanks` มี 1 แถว |
| NA-99 | ขอบคุณต้อง login | ไม่มี header · token ที่ไม่รู้จัก · auth-service ล่ม | `401` `unauthorized` (ไม่มีแถวใน `thanks`) · `401` · `503` `auth_unavailable` |
| NA-100 | โน้ตที่ไม่มีอยู่ | `POST /notes/999/thanks` | `404` `not_found` |
| NA-101 | ขอบคุณโน้ตของตัวเองไม่ได้ | Alice `POST .../thanks` โน้ตที่ตัวเองอัปโหลด | `403` `own_note` · ไม่มีแถวใน `thanks` |
| NA-102 | หลายคนขอบคุณโน้ตเดียวกันได้คนละครั้ง และนับแยกโน้ต | Bob กับ Carol ขอบคุณ แล้ว Bob กดซ้ำ · ขอบคุณโน้ตหนึ่งจากสองโน้ต | `201` ทั้งคู่ · ยอดของโน้ตนั้น = 2 · อีกโน้ต = 0 |
| NA-103 | ยกเลิกคำขอบคุณไม่ได้ | `DELETE /notes/<id>/thanks` หลังขอบคุณ | `405` · `thank_status` ยังเป็น `thanked` |
| NA-104 | API ไม่ตรวจว่าดาวน์โหลดแล้ว ("หลังดาวน์โหลด" เป็นเงื่อนไขฝั่ง UI) | ขอบคุณโน้ตที่ `download_count = 0` | `201` |
| NA-105 | `thank_status` เปลี่ยนตามการขอบคุณ และแยกตามผู้ใช้ | อ่านโน้ตก่อน/หลัง Bob ขอบคุณ · Carol อ่านโน้ตเดียวกัน | Bob: `can_thank` → `thanked` · Carol: `can_thank` |
| NA-106 | `thank_status` ของเจ้าของโน้ต | Alice อ่านโน้ตตัวเอง | `own_note` |
| NA-107 | ไม่ login หรือ token ใช้ไม่ได้ ได้ `thank_status = null` | `GET /notes`, `GET /notes/<id>` ไม่มี header และด้วย token ที่ไม่รู้จัก | `200` และ `thank_status = null` |
| NA-108 | auth-service ล่มระหว่างค้นหา ค้นหายังใช้ได้ | identity โยน `IdentityUnavailable` แล้ว `GET /notes`, `GET /notes/<id>` ด้วย token ที่ถูก | `200` และ `thank_status = null` (ไม่ใช่ `503`) |
| NA-109 | `GET /notes` ให้สถานะต่อโน้ตถูกต้องในหน้าเดียวกัน และ query `thanks` ครั้งเดียว | Bob ค้นหาเจอโน้ตที่ยังไม่ขอบคุณ, ขอบคุณแล้ว และโน้ตของตัวเอง · นับ SQL ตอนมี 5 โน้ต | `can_thank` · `thanked` · `own_note` · อ่านตาราง `thanks` 1 ครั้ง |
| NA-110 | ลบโน้ตลบคำขอบคุณของโน้ตนั้น (US-20) | Bob กับ Carol ขอบคุณ แล้วเจ้าของลบโน้ต · มีอีกโน้ตที่ Bob ขอบคุณไว้ | `204` ไม่ชน FK · thanks ของโน้ตที่ลบหายหมด · ของอีกโน้ตยังอยู่ |
| NA-111 | เจ้าของที่ login แก้ได้ (Issue #82, ADR-008) | Alice `PATCH` ด้วย Bearer ของตัวเอง | `200` · `title` เปลี่ยนจริงเมื่ออ่านซ้ำ |
| NA-112 | เจ้าของที่ login ลบได้ | Alice `DELETE` ด้วย Bearer ของตัวเอง | `204` · `GET` ได้ `404` · ไม่มีไฟล์เหลือใน storage |
| NA-113 | คนอื่นที่ login อยู่แก้/ลบไม่ได้ | Bob `PATCH`/`DELETE` โน้ตของ Alice | `403 forbidden` ทั้งคู่ · `title` คงเดิม |
| NA-114 | ไม่ login ได้ 401 (ADR-013 — เดิม 403 เพราะยังมีทาง edit token) | `PATCH`/`DELETE` ไม่มี header | `401` + `WWW-Authenticate: Bearer` ทั้งคู่ · `title` คงเดิม |
| NA-115 | Bearer ใช้ไม่ได้ | `DELETE` ด้วย `Bearer expired` | `401` + `WWW-Authenticate: Bearer` · โน้ตยังอยู่ |
| NA-116 | auth-service ล่ม | identity โยน `IdentityUnavailable` แล้ว Alice `PATCH` | `503 auth_unavailable` |
| NA-117 | header `X-Note-Token` แบบเดิมไม่มีผลแล้ว (ADR-013) | Bob + `X-Note-Token` · ไม่มี Bearer + `X-Note-Token` · Alice + `X-Note-Token` | `403` · `401` · `200` (ผลตาม login เท่านั้น) |
| NA-118 | ~~token ผิดแต่ login เป็นเจ้าของ~~ | ยกเลิกแล้ว (ADR-013) รวมไว้ใน NA-117 | — |
| NA-119 | โน้ตที่ไม่มีอยู่ได้ 404 ก่อนตรวจสิทธิ์ | Bob `DELETE /notes/999` | `404` |
| NA-120 | `GET /notes/mine` ต้อง login (Issue #82) | ไม่มี header · auth-service ล่ม | `401` + `WWW-Authenticate: Bearer` · `503` |
| NA-121 | โน้ตของฉันมีเฉพาะของตัวเอง ใหม่สุดก่อน | Alice อัปโหลด 2 ใบ Bob 1 ใบ แล้ว Alice `GET /notes/mine` | `items` = 2 ใบของ Alice ใบใหม่ก่อน · `count = 2` |
| NA-122 | edit token ไม่รั่วใน `/notes/mine` | อ่าน item แรก | ไม่มี `edit_token` และ `edit_token_hash` |
| NA-123 | ยังไม่มีโน้ตเลย | Alice `GET /notes/mine` ขณะมีแต่โน้ตของ Bob | `items = []` · `summary` เป็นศูนย์ทั้งหมด · `average_rating = null` |
| NA-124 | `summary` นับทุกโน้ต ไม่ใช่แค่หน้าที่ส่งกลับ | 3 โน้ต ดาวน์โหลดรวม 3 ครั้ง เปิดดู 1 ครั้ง แล้ว `?limit=1` | `count = 1` · `note_count = 3` · `total_downloads = 3` · `total_views = 1` |
| NA-125 | `average_rating` ถ่วงน้ำหนักตามจำนวนคะแนน | โน้ต A ได้ 5, 5 · โน้ต B ได้ 2 | `average_rating = 4.0` (ไม่ใช่ 3.5) · `rating_count = 3` |
| NA-126 | `thank_count` ต่อโน้ตและ `total_thanks` | Bob กับ Carol ขอบคุณโน้ตหนึ่ง อีกโน้ตไม่มีใครขอบคุณ | `thank_count` = 2 กับ 0 · `total_thanks = 2` |
| NA-127 | `limit` ที่ไม่ใช่ตัวเลขใน `/notes/mine` | `?limit=abc` | `400 {"error": "invalid_filter", "field": "limit/offset"}` |
| NA-128 | `sort=rating` เรียงคะแนนเฉลี่ยมากไปน้อย ไม่มีคะแนนอยู่ท้าย (Issue #83) | โน้ตคะแนน 3, ไม่มีคะแนน, 5, 4 | ลำดับ 5, 4, 3, ไม่มีคะแนน |
| NA-129 | ใช้ค่าเฉลี่ย ไม่ใช่คะแนนล่าสุด | โน้ต A ได้ 5 กับ 2 (3.5) · โน้ต B ได้ 4 | B ก่อน A |
| NA-130 | เฉลี่ยเท่ากัน คนให้คะแนนมากกว่าขึ้นก่อน | เฉลี่ย 4 ทุกใบ จาก 2, 1, 3 คน | 3 คน, 2 คน, 1 คน |
| NA-131 | เท่ากันทุกอย่าง ใหม่กว่าขึ้นก่อน | สองโน้ตได้ 5 คนละครั้ง โน้ตหนึ่งเก่ากว่า 1 วัน | ใบใหม่ก่อน |
| NA-132 | ไม่มีคะแนนทั้งหมด ใหม่สุดก่อน | สองโน้ตไม่มีคะแนน | ใบที่อัปโหลดทีหลังก่อน |
| NA-133 | `sort=rating` ใช้กับตัวกรองและ paging ได้ | `subject_code=CS301` + `limit=1&offset=1` | เฉพาะโน้ต CS301 ตามลำดับคะแนน · หน้า 2 ได้ใบที่สอง |
| NA-134 | `sort` ที่ไม่รู้จักยังได้ 400 | `?sort=popular` | `400 {"error": "invalid_filter", "field": "sort"}` |
| NA-135 | คำค้นไม่สนตัวพิมพ์ใหญ่เล็ก ทั้ง 5 ฟิลด์ที่ `q` ค้น | โน้ต `Data Structures` / `Algorithms` / `CS201` / `Linked List` / `Big-O` แล้วค้นด้วยตัวเล็กหมดทีละคำ | เจอ 1 รายการทุกคำ · ผ่านบน SQLite แม้เปลี่ยน `ilike` เป็น `like` เพราะ `LIKE` ของ SQLite ไม่สนตัวพิมพ์อยู่แล้ว จึงจับได้เฉพาะ job บน PostgreSQL (ดูหัวข้อ 4) |
| NA-136 | `file_type` ไม่สนตัวพิมพ์ และ `jpeg` คือ `jpg` | โน้ต PDF กับ JPEG แล้วกรองด้วย `jpg`, `jpeg`, `JPEG`, `Jpg`, `PDF` · `jfif` | ได้เฉพาะโน้ต JPEG ทั้งสี่ค่า · `PDF` ได้โน้ต PDF · `jfif` ยังได้ `400` |
| NA-137 | `total` นับทุกโน้ตที่ตรงตัวกรอง ไม่ใช่แค่หน้านี้ | 5 โน้ต (Math 2) แล้ว `?limit=2`, `?limit=2&offset=4`, `?q=Math&limit=1`, `?offset=50` | `count` 2/1/1/0 · `total` 5/5/2/5 |
| NA-138 | ไม่มีโน้ตตรงเงื่อนไข | `?q=nothing-like-this` | body เท่ากับ `{"items": [], "count": 0, "total": 0}` พอดี |
| NA-139 | `total` กับ `sort=rating` นับโน้ตละครั้ง | โน้ตได้ 3 คะแนน, 1 คะแนน, ไม่มีคะแนน แล้ว `?sort=rating&limit=1` | `count = 1` · `total = 3` (ไม่ใช่จำนวนแถวคะแนน) |

NA-136 ถึง NA-139 (`total` และ `file_type`, 2026-10-08) จับ mutation ได้ครบ 5 แบบ: `total = len(items)`, นับทั้งตารางไม่สนตัวกรอง,
นับแถวคะแนนแทนโน้ต, เอาชื่อ `jpeg` ออก, ไม่แปลงเป็นตัวเล็ก

### 2.5 Notes Service — แก้ไข/ลบโน้ต (`pytest`, US-19 #19 + US-20 #20)

ต้อง login เป็นบัญชีที่อัปโหลดโน้ต ([ADR-008](../architecture/adr/0008-owner-login-for-note-changes.th.md), ดู NA-111 ถึง NA-119)
edit token ต่อโน้ตของ ADR-004 เลิกใช้แล้ว ([ADR-013](../architecture/adr/0013-retire-per-note-edit-token.th.md)) · NE-09 กับ NE-10 จึงถูกถอด (คนอื่นแก้ไม่ได้อยู่ใน NA-113)

| # | Test case | Request | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| NE-01 | ไม่มี edit token แล้ว (ADR-013) | `POST /notes` แล้ว `GET /notes/<id>` | ไม่มี `edit_token` ทั้งตอนสร้างและตอนอ่าน และไม่มี `edit_token_hash` |
| NE-02 | PATCH แก้เฉพาะฟิลด์ที่ส่งมา และประทับ `updated_at` | `PATCH` ส่ง `subject_code` + `topic` | สองฟิลด์นั้นเปลี่ยน ฟิลด์อื่นคงเดิม `updated_at` จาก `null` เป็นเวลาจริง |
| NE-03 | ล้างค่าฟิลด์ไม่บังคับได้ | `PATCH` ส่ง `topic=` (ว่าง) | `topic` เป็น `null` |
| NE-04 | ค่าผิดรูปต้องไม่ทำให้ข้อมูลเดิมเสีย | `PATCH` ส่ง `year_level=99` | `400` และค่าเดิมใน DB ไม่เปลี่ยน |
| NE-05 | ฟิลด์ที่แก้ไม่ได้ถูกเมิน ไม่ใช่ error | `PATCH` ส่ง `uploader_name` + `title` | `title` เปลี่ยน `uploader_name` คงเดิม |
| NE-06 | PATCH ที่ไม่มีฟิลด์ให้แก้ | `PATCH` body ว่าง | `400` `no_fields_to_update` |
| NE-07 | ลบแล้วหายทั้ง record และไฟล์ | `DELETE` ด้วยบัญชีเจ้าของ | `204` · `GET` ได้ `404` · โฟลเดอร์ storage ว่าง |
| NE-08 | ไม่ login | `PATCH`/`DELETE` ไม่มี header | `401 unauthorized` ทั้งคู่ · ข้อมูลคงเดิม |
| NE-09 | ~~token ผิด~~ | ยกเลิกแล้ว (ADR-013) | — |
| NE-10 | ~~token ของโน้ตใบหนึ่งใช้กับใบอื่นไม่ได้~~ | ยกเลิกแล้ว (ADR-013) — คนอื่นแก้ไม่ได้ดู NA-113 | — |
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
| DK-08 | web gateway เสิร์ฟหน้าเว็บและส่งต่อ API จาก origin เดียว (ADR-006, US-11/US-31) | `curl :8080/`, `/login.html`, `/upload.html`, `/note.html?id=1`, `/profile.html` (Issue #85), `/admin.html` (Issues #17, #18), `/stats.html` (Issue #16), `/edit.html` ที่ถูกลบแล้ว (ADR-013), ไฟล์ JS และไฟล์เทสต์ของแต่ละหน้า · `GET :8080/stats` · `GET :8080/notes?subject_code=CS201&year_level=2` และ `?year_level=abc` · `GET :8080/notes/<id ของ CS201>/stats` แบบไม่มี token และด้วยเจ้าของ, `GET :8080/notes/<id>` · `GET :8080/reports` แบบไม่มี token และด้วยสมาชิกทั่วไป, `DELETE :8080/reports/1` ด้วยสมาชิกทั่วไป · `GET :8080/auth/me` แบบไม่มี token และมี token · อัปโหลด PNG ผ่าน `:8080/notes` แล้วเปิด `preview_url` ผ่าน `:8080` · `PATCH :8080/notes/<id ของโน้ตนั้น>` แบบไม่มีฟิลด์ด้วย Bearer ของเจ้าของ และแบบไม่ login · `POST :8080/auth/login` (JSON) → `POST :8080/auth/logout` → `GET :8080/auth/me` ด้วย token เดิม | หน้าแรกมี `id="searchForm"`, หน้า login มี `id="loginForm"`, หน้าอัปโหลดมี `id="uploadForm"`, หน้ารายละเอียดมี `id="noteDetail"`, หน้าโปรไฟล์มี `id="profileStats"`, หน้าผู้ดูแลมี `id="reportsList"`, หน้าสถิติมี `id="overviewCards"` · `/edit.html` ได้ `404` · `/stats` ได้ `total_notes` เป็นตัวเลข · ไฟล์ JS ได้ `200` · ไฟล์เทสต์ได้ `404` (ไม่ถูก copy เข้า image) · query string ไปถึง service ครบ (`count = 1`, ค่าผิดได้ `400`) · `/notes/<id>/stats` ไปถึง stats-service (ไม่ login `401`, เจ้าของได้ `downloads` ≥ 1) และ `/notes/<id>` ยังไป notes-service · `/reports` ไม่มี token `401`, สมาชิกทั่วไปได้ `forbidden` และลบไม่ได้ `403` (nginx ส่ง `/reports` ไปถึง notes-service) · `me` ไม่มี token `401` มี token ได้ `CI Uploader` (header `Authorization` ผ่าน nginx) · upload ได้ `uploader_name = CI Uploader` และ preview ได้ `200` + `image/png` · เจ้าของได้ `no_fields_to_update` ไม่ login ได้ `401` และ `updated_at` ยังเป็น `null` (header `Authorization` ผ่าน nginx) · login ได้ token, logout ได้ `204` แล้ว token เดิมได้ `401` (US-05/US-06 ผ่าน gateway แบบที่หน้าเว็บเรียก) |
| DK-09 | เจ้าของแก้/ลบด้วย login, `/notes/mine` และ `sort=rating` บน Postgres จริง (Issues #82, #83) | สมัคร + login บัญชี `CI Rater` · `CI Uploader` อัปโหลด 2 โน้ต (`CS501`) · Rater เปิดดูแล้วให้คะแนนใบแรก · `GET /notes?subject_code=CS501&sort=rating` · `GET /notes/mine` · Rater แล้วเจ้าของ `PATCH`/`DELETE` | ใบที่มีคะแนนมาก่อนใบใหม่กว่าที่ไม่มีคะแนน (Postgres วาง NULL ไว้หน้าสุดเมื่อ DESC ต่างจาก SQLite) · `/notes/mine` มีทั้งสองใบ, `rating_count = 1`, ไม่ login ได้ `401` · Rater ได้ `403` ทั้งคู่ · เจ้าของ `PATCH` ได้ค่าใหม่และ `DELETE` ได้ `204` |
| DK-10 | gateway ตรวจ login ก่อนส่งต่อ (ADR-014) — step สุดท้ายของ smoke เพราะหยุด auth-service | ผ่าน `:8080`: `GET /notes/<id>/stats` ไม่มี token, token มั่ว, token เจ้าของ · `PATCH /notes/<id>` ไม่มีทั้ง token และรหัส · `GET /notes/mine` ไม่มี token (ดู header) · `GET /notes/<id>` ด้วย token มั่ว · หยุด auth-service แล้ว `GET /notes/mine` ด้วย token จริง และ `GET /notes?subject_code=CS201` | สองแบบแรกได้ `{"error": "unauthorized"}` จาก gateway (ถ้าหลุดไปถึง stats-service จะได้ `Authentication required`) · เจ้าของได้ `200` · `PATCH` ได้ `401` ไม่ใช่ `403` ของ service · มี `WWW-Authenticate: Bearer` และ `Content-Type: application/json` · route ที่เปิดไม่ถูกตรวจ ได้ `200` · auth-service ล่มได้ `503 auth_unavailable` ส่วนการค้นหายังได้ `count = 1` |

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
| WEB-15 | `hasMore` เป็นจริงเฉพาะหน้าที่เต็ม เมื่อไม่มียอดรวม | 20, 19, 0 | `true`, `false`, `false` (ใช้กับรายการที่ API ไม่ส่ง `total` เช่นโน้ตของฉัน รายการโปรด) |
| WEB-95 | `hasMore` ใช้ `total` ของ `GET /notes` เมื่อมี | หน้าเต็มที่แสดงครบ 40/40 · 40/41 · 3/3 · 0/0 · ไม่มี `total` หรือ `total = null` | `false` · `true` · `false` · `false` · กลับไปใช้กฎหน้าเต็ม (`true`) — หน้าสุดท้ายที่เต็มพอดีไม่ต้องขอหน้าว่างอีกรอบ |
| WEB-96 | `resultsSummary` บอกยอดรวมเมื่อยังแสดงไม่ครบ | (20, 57), (57, 57), (0, 0), (20, ไม่มี) | `แสดง 20 จาก 57 รายการ` · `แสดง 57 รายการ` · `แสดง 0 รายการ` · `แสดง 20 รายการ` |
| WEB-39 | `starBar` เติมดาวตามค่าเฉลี่ยที่ปัดแล้ว (Issue #84) | ไม่มีคะแนน, 4.3, 4.5, 1 | `☆☆☆☆☆`, `★★★★☆`, `★★★★★`, `★☆☆☆☆` |
| WEB-40 | การ์ดโน้ตแบบใหม่มีป้ายรหัสวิชาและดาว (Issue #84) | โน้ต `CS201` เฉลี่ย 4.25 | มี `<span class="tag-course">CS201</span>` และ `★★★★☆` · ข้อความของ WEB-10 ถึง WEB-12 ยังผ่านเหมือนเดิม |

**ตรวจบน browser จริง (2026-10-01, ด้วยมือ ยังไม่ใช่ E2E อัตโนมัติ):** Docker ไม่ได้เปิดบนเครื่องที่ใช้เขียน จึงรัน
`auth-service` กับ `notes-service` ตัวจริงบน SQLite และใช้สคริปต์ Python ที่ทำตัวแทน `web/nginx.conf` (path เดียวกัน)
แล้วเปิดใน Chrome ผล: ค้นหา/กรอง/เรียงได้ผลจาก API จริง · โหลดเพิ่มจาก 20 → 25 แล้วปุ่มหาย · เปิด preview จากการ์ดที่ 22
แล้วปิดด้วย Esc, คลิกฉากหลัง และปุ่ม ✕ ตำแหน่ง scroll เท่าเดิม (2397 px) การ์ดยังอยู่ 25 ใบ focus กลับไปที่ปุ่มเดิม (US-11 AC3)
· PNG ปลอมแสดงข้อความ preview ไม่ได้แทนรูปแตก · ช่วงวันที่กลับด้านแสดง error ชื่อช่อง · back คืนค่าฟอร์มเดิม · ชื่อโน้ตที่มี
`<script>` แสดงเป็นข้อความ · ค้นด้วยคำภาษาไทยได้ · console ไม่มี error · ตัว nginx จริงยืนยันผ่าน DK-08 บน CI

**ตรวจหน้าตาใหม่บน browser (2026-10-04, Issue #84, ด้วยมือ):** ตั้งค่าแบบเดียวกับข้างบน (service จริงบน SQLite + ตัวแทน nginx)
ผล: การ์ดเรียงเป็น grid มีป้ายรหัสวิชา ดาว และแท็ก · ชื่อโน้ตยาวภาษาไทยตัดบรรทัดในการ์ดได้ · เปิด preview แล้วปิดด้วย Esc ได้
· เปิดหน้าจากลิงก์ `?faculty=ICT&file_type=png` แผงตัวกรองกางออกเองและชิป PNG ถูกเลือก · หน้าเข้าสู่ระบบเป็นการ์ดสองคอลัมน์
· อัปโหลดผ่านหน้าอัปโหลดแล้วเห็นกล่องรหัสแก้ไข · หน้าค้นหา เข้าสู่ระบบ และอัปโหลด กว้าง 375 px ไม่มี scroll แนวนอน
(`scrollWidth` ไม่เกินความกว้างจอ) · console ไม่มี error

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
| WEB-35 | `validateUpload` ไม่รับไฟล์ว่างและไฟล์เกิน 10 MB (NFR-006, ADR-012) | 0 byte, 10 MB + 1 byte, 10 MB พอดี | `ไฟล์ว่าง`, `ไฟล์ใหญ่เกิน 10 MB`, ผ่าน |
| WEB-36 | `uploadFields` trim ค่าและไม่ส่งช่องไม่บังคับที่ว่าง | `title = '  Calc  '`, `topic` มีค่า, `class_date`/`description` ว่าง, มี `uploader_name` ปนมา | ได้เฉพาะ 6 ช่องบังคับ + `topic` ที่ trim แล้ว ไม่มี `uploader_name` (US-31) |
| WEB-37 | `uploadErrorMessage` ครอบ error ของ notes-service และเพดานของ gateway | `400 validation_failed`, `401 unauthorized`, `503 auth_unavailable`, `413` ไม่มี body, status `0`, `500` | ข้อความเฉพาะของแต่ละกรณี · `413` = `ไฟล์ใหญ่เกิน 10 MB` · `409 upload_already_used` (ADR-012) บอกให้อัปโหลดใหม่ |
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

### 2.15 Web app — `note-utils.js` (`node --test`, Issue #85 หน้ารายละเอียดโน้ต)

pure function ของหน้ารายละเอียดโน้ตใน [`web/`](../../web/) แยกจากส่วนที่แตะ DOM (`note.js`) · storage ถูกส่งเข้าฟังก์ชันเหมือน 2.14

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| WEB-41 | `noteIdFromSearch` รับเฉพาะเลขจำนวนเต็มบวก | `?id=7`, `?q=x&id=120` · `?id=`, `0`, `-3`, `7abc`, `1.5`, ` 7`, เลข 11 หลัก | `7`, `120` · ที่เหลือได้ `null` |
| WEB-42 | `noteUrl` ชี้ไปหน้ารายละเอียด | `7` | `/note.html?id=7` |
| WEB-43 | `formatThaiDateTime` แสดงเวลาไทย (UTC+7) และปี พ.ศ. | `2026-10-04T17:30:00+00:00`, `2026-01-01T02:05:00Z`, เวลาไม่มี timezone (แบบที่ SQLite ส่ง) โดยตั้ง TZ ของเครื่องเป็น `Asia/Bangkok`, `-02:00`, ค่าที่ไม่ใช่วันที่ | `5 ต.ค. 2569 00:30`, `1 ม.ค. 2569 09:05`, `5 ต.ค. 2569 10:24` (ถือเป็น UTC ไม่ใช่เวลาเครื่อง), `12:24`, `''` |
| WEB-44 | `noteMetaLine` บอกผู้อัปโหลด วิชา และยอดดาวน์โหลด/เปิดดู | โน้ตตัวอย่าง · ยอดเป็น `null` | `อัปโหลดโดย Somchai · CS201 Data Structures · ดาวน์โหลด 3 ครั้ง · เปิดดู 12 ครั้ง` · ได้ `0 ครั้ง` |
| WEB-45 | `noteTags` ข้ามช่องไม่บังคับที่ว่าง | มี/ไม่มี `topic` กับ `class_date` | ได้ 5 แท็ก / 3 แท็ก ไม่มี `null` |
| WEB-46 | `commentAuthor` เป็น "คุณ" เฉพาะความคิดเห็นของผู้ชม | ความคิดเห็นของ user 1 ดูโดย user 1, user 2, ไม่ login | `คุณ`, `สมาชิก`, `สมาชิก` |
| WEB-47 | `renderComment` มีปุ่มลบเฉพาะความคิดเห็นของตัวเอง | เหมือน WEB-46 | มี `data-delete-comment="3"` เฉพาะกรณีแรก · แสดงเวลา `4 ต.ค. 2569 10:00` |
| WEB-48 | `renderComment` escape ข้อความที่ผู้ใช้พิมพ์ | `<img src=x onerror=alert(1)>` | ไม่มีแท็ก `<img` ได้ `&lt;img …&gt;` |
| WEB-49 | `textProblem` ใช้กฎเดียวกับ API (trim, ห้ามว่าง, ความยาว) | ช่องว่างล้วน, `undefined`, 1000/1001 ตัว (ความคิดเห็น), 500/501 ตัว (เหตุผลรายงาน) | `ต้องไม่ว่าง` ×2, ผ่าน, `ยาวเกิน 1000 ตัวอักษร`, ผ่าน, `ยาวเกิน 500 ตัวอักษร` |
| WEB-50 | `markDownloaded` จำการดาวน์โหลดแยกตามผู้ใช้และโน้ต | user 1 ดาวน์โหลดโน้ต 7 สองครั้ง | user 1 โน้ต 7 = จริง · โน้ต 8, user 2, ไม่ login = เท็จ · เก็บ `['1:7']` ครั้งเดียว |
| WEB-51 | `markDownloaded` ไม่พังเมื่อ storage เสียหรือถูกบล็อก | ค่าที่ไม่ใช่ JSON · storage ที่ throw | อ่านเป็นว่างแล้วเขียนทับได้ · ไม่ throw และได้เท็จ |
| WEB-52 | `markDownloaded` เก็บแค่ 200 รายการล่าสุด | ดาวน์โหลด 205 โน้ต | เหลือ 200 รายการ โน้ตแรก ๆ หลุด โน้ตล่าสุดยังอยู่ |
| WEB-53 | `thanksView` ให้กดขอบคุณได้หลังดาวน์โหลดเท่านั้น และไม่ใช่โน้ตตัวเอง (US-28) | `thank_status` = `null`, `own_note`, `thanked`, `can_thank` × ดาวน์โหลดแล้ว/ยัง | `login`, `own`, `thanked`, `need_download`, `ready` (`ready` แบบเดียวที่มีปุ่ม) |
| WEB-54 | `actionErrorMessage` ครอบ error ของทุกการกระทำในหน้า | `401`, `503`, `409 already_reported`, `403 own_note`/`not_eligible`/`forbidden`, `400` ของ content/reason/rating, `404`, status `0`, `500` | ข้อความเฉพาะของแต่ละกรณี · ที่เหลือใช้ข้อความเดียวกับหน้าค้นหา |
| WEB-55 | การ์ดค้นหามีลิงก์จากชื่อโน้ตไปหน้ารายละเอียด (`search-utils.test.js`) | โน้ต id 7 | มี `<a class="note-link" href="/note.html?id=7">` |
| WEB-56 | `safeNextPath` ยอมให้กลับมาหน้ารายละเอียดหลัง login (`session-utils.test.js`) | `/note.html?id=7` | ได้ค่าเดิม (ยังไม่รับหน้าอื่นนอกรายการ) |

mutation 11 แบบถูกจับครบ: ตัดเงื่อนไข `own_note`, ไม่ตรวจว่าดาวน์โหลดแล้ว, ให้ทุกความคิดเห็นเป็นของตัวเอง, ไม่แยกการดาวน์โหลดตามผู้ใช้,
ไม่ escape ความคิดเห็น, เลื่อนเพดานความยาว, regex ของ id หลวมลง, ไม่ตัดรายการเหลือ 200, เอา `/note.html` ออกจาก `NEXT_PAGES`,
ตัดลิงก์บนการ์ด และอ่านเวลาที่ไม่มี timezone เป็นเวลาเครื่อง

**ตรวจบน browser จริง (2026-10-05, Issue #85, ด้วยมือ):** รัน `auth-service` กับ `notes-service` ตัวจริงบน SQLite และสคริปต์ Python
ที่ทำตัวแทน `web/nginx.conf` (เสิร์ฟเฉพาะไฟล์ที่ `web/Dockerfile` copy) แล้วเปิดใน Chrome ด้วยบัญชีผู้อัปโหลดกับบัญชีผู้อ่าน ผล:
ไม่ login เห็นโน้ต ภาพตัวอย่าง และลิงก์เข้าสู่ระบบในกล่องคะแนน/ขอบคุณ/ความคิดเห็น · ผู้อ่านกดดาวน์โหลด (ปิดการบันทึกไฟล์ลงดิสก์ไว้)
ได้ไฟล์ชื่อเดิม ยอดดาวน์โหลดขึ้นเป็น 1 แล้วปุ่มขอบคุณจึงขึ้น · กดขอบคุณแล้วปุ่มหาย reload แล้วยังเป็น "ขอบคุณแล้ว" · รายการโปรดสลับได้
และ `GET /notes/favorites` ตรงกัน · ให้ 4 ดาวแล้วค่าเฉลี่ยเปลี่ยน · ส่งรายงานว่างได้ error ใต้ช่อง ส่งจริงได้ข้อความยืนยัน รายงานซ้ำได้
"รายงานไปแล้ว" · ความคิดเห็นที่มี `<b>` แสดงเป็นข้อความ โพสต์และลบของตัวเองได้ ลบของคนอื่นไม่มีปุ่ม · เพิกถอน token จากที่อื่นแล้วกด
รายการโปรดได้ข้อความพร้อมลิงก์ `/login.html?next=%2Fnote.html%3Fid%3D1` แถบเมนูกับทุกกล่องเปลี่ยนเป็นยังไม่ login · เจ้าของโน้ตไม่เห็นปุ่มรายงาน
และกล่องขอบคุณเป็น "นี่คือโน้ตของคุณ" · ชื่อโน้ตที่มี `<script>` แสดงเป็นข้อความ · `?id=abc` และ `?id=999` ได้ข้อความแทนหน้าว่าง
· คลิกชื่อโน้ตจากผลค้นหา `?q=Linked&faculty=ICT` แล้ว "กลับไปหน้าค้นหา" ชี้กลับผลค้นหาเดิม · ปุ่ม "เปิดหน้าโน้ต" ใน preview ชี้ถูกโน้ต
· หน้ารายละเอียด หน้าค้นหา และหน้าอัปโหลดกว้าง 375 px ไม่มี scroll แนวนอน หน้ารายละเอียดเหลือคอลัมน์เดียว · console ไม่มี error
· รอบนี้เจอบั๊กเวลาความคิดเห็นช้าไป 7 ชั่วโมง (SQLite ส่งเวลาไม่มี timezone) แก้แล้วและเพิ่มเป็น WEB-43

### 2.16 Web app — `profile-utils.js` + แถบอัปโหลด + เรียงตามคะแนน (`node --test`, Issue #85 + #83)

pure function ของหน้าโปรไฟล์ใน [`web/`](../../web/) แยกจากส่วนที่แตะ DOM (`profile.js`) · เลข WEB ต่อจาก 2.15 ของ PR #88

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| WEB-57 | `summaryCards` แสดงยอดรวมทุกช่องจาก `GET /notes/mine` | `note_count 3`, `average_rating 4.33` จาก 6 คะแนน, ดาวน์โหลด 9, เปิดดู 40, ขอบคุณ 2 | `3`, `4.3` (ป้าย `คะแนนเฉลี่ย (6 คะแนน)`), `9`, `40`, `2` |
| WEB-58 | `summaryCards` กับผู้ใช้ที่ยังไม่มีโน้ตหรือคะแนน | `average_rating null`, `rating_count 0` · `summary` หายไป | `0`, `–`, `0`, `0`, `0` ทั้งสองกรณี |
| WEB-59 | `renderMyNoteRow` ลิงก์ไปหน้ารายละเอียดและมีปุ่มแก้/ลบ | โน้ต id 7 | มี `href="/note.html?id=7"`, `data-edit-note="7"`, `data-delete-note="7"` และยอดคะแนน/ดาวน์โหลด/เปิดดู/ขอบคุณ |
| WEB-60 | `renderFavoriteRow` บอกผู้อัปโหลดและมีแค่ปุ่มเอาออก | โน้ตของคนอื่น | มี `อัปโหลดโดย …` และ `data-unfavorite` ไม่มีปุ่มแก้/ลบ |
| WEB-61 | แถวในหน้าโปรไฟล์ escape ค่าที่ผู้ใช้พิมพ์ | ชื่อโน้ต `<img src=x onerror=…>`, ชื่อผู้อัปโหลด `<b>x</b>` | ไม่มีแท็ก `<img`/`<b>` ได้ `&lt;img` |
| WEB-62 | `editFormValues` เติมฟอร์มแก้ไขเป็นข้อความทุกช่อง | `year_level 2`, `topic null`, `description null` | ได้ครบ 9 ช่อง `'2'`, `''`, `''` |
| WEB-63 | `changedFields` ส่งเฉพาะช่องที่เปลี่ยนและ trim แล้ว (US-19 partial update) | แก้ชื่อ (มีช่องว่างหัวท้าย) + เติมหัวข้อ · ไม่แก้อะไร · เติมช่องว่างรอบค่าเดิม | `{title, topic}` · `{}` · `{}` |
| WEB-64 | `changedFields` ส่ง `''` เมื่อล้างช่องไม่บังคับ | ลบวันที่เรียนออก | `{class_date: ''}` (API ล้างค่าเมื่อได้ค่าว่าง) |
| WEB-65 | `profileErrorMessage` ครอบ error ของ PATCH/DELETE | `validation_failed`, `no_fields_to_update`, `403 forbidden`, `401`, `503`, `404`, status `0` | ข้อความเฉพาะของแต่ละกรณี |
| WEB-66 | `validateMetadata` ตรวจเฉพาะช่องข้อความ ใช้ร่วมกับฟอร์มแก้ไข | ฟอร์มถูก · ชื่อว่าง + ชั้นปี 9 + `2026-02-30` | `{}` · error 3 ช่อง ไม่มี `file` |
| WEB-67 | `uploadProgress` แปลง event ของการส่งไฟล์เป็นเปอร์เซ็นต์และข้อความ | 0 / 4.5 / 10 MB − 1 byte / 10 MB จาก 10 MB · ไม่รู้ขนาด | `0%`, `45% (4.5 MB จาก 10.0 MB)`, `99` (ยังไม่ขึ้น 100 ก่อนไบต์สุดท้าย), `100` + `รอเซิร์ฟเวอร์บันทึกโน้ต…` · `percent null` |
| WEB-68 | `sort=rating` (Issue #83) อยู่ใน URL ของหน้าได้และส่งต่อถึง API (`search-utils.test.js`) | `?sort=rating` · ตัวกรองที่ `sort = 'rating'` | `sort` เป็น `rating` · query `sort=rating` (เทสต์ "ค่า sort ที่ไม่รู้จัก" เดิมเปลี่ยนไปใช้ `popular`) |
| WEB-69 | `safeNextPath` ยอมให้กลับมาหน้าโปรไฟล์หลัง login (`session-utils.test.js`) | `/profile.html` | ได้ค่าเดิม |

mutation 11 แบบถูกจับครบ: `changedFields` ส่งทุกช่อง/ไม่ trim, `editFormValues` ไม่แปลง `null`, การ์ดคะแนนไม่เช็กว่ามีคะแนน, ไม่ escape ชื่อโน้ต,
ตัดข้อความ `forbidden`, ปัดเปอร์เซ็นต์ขึ้น, ตัดกรณีไม่รู้ขนาดไฟล์, `validateUpload` ไม่เรียก `validateMetadata`, เอา `rating` ออกจาก `SORTS`
และเอา `/profile.html` ออกจาก `NEXT_PAGES`

**ตรวจบน browser จริง (2026-10-05, Issue #85 ส่วนที่สอง, ด้วยมือ):** ตั้งค่าแบบเดียวกับ 2.15 (service จริงบน SQLite + ตัวแทน nginx) ผล:
เปิด `/profile.html` ตอนไม่ login ถูกพาไป `/login.html?next=%2Fprofile.html` · เจ้าของโน้ตเห็นการ์ดสรุปตรงกับ API (2 โน้ต, คะแนน 5.0 จาก 1 คะแนน,
ขอบคุณ 1) แถบเมนูมีลิงก์ "โปรไฟล์" · ชื่อโน้ตที่มี `<script>` แสดงเป็นข้อความทั้งในรายการและในกล่องยืนยันลบ · เปิดฟอร์มแก้ไขแล้วค่าเดิมครบ
กดบันทึกโดยไม่แก้ได้ "ยังไม่ได้แก้ข้อมูลช่องใด" · ล้างชื่อและชั้นปีได้ error ใต้สองช่อง · แก้ชื่อ (มีช่องว่างท้าย) ล้างวันที่เรียน เติมหัวข้อ แล้ว
`GET /notes/1` ได้ชื่อที่ trim แล้ว `class_date = null`, `topic = Pointers` ส่วนช่องอื่นไม่เปลี่ยน · ยกเลิกแก้/ลบแล้ว focus กลับปุ่มเดิม
· ลบโน้ตที่อยู่ในรายการโปรดด้วย: หายจากทั้งสองรายการ การ์ดสรุปลดเป็น 1 โน้ต และ `GET /notes/2` ได้ `404` · ผู้อ่านที่ไม่มีโน้ตเห็น
"ยังไม่ได้อัปโหลดโน้ต" กับการ์ด `0, –, 0, 0, 0` เอาโน้ตออกจากรายการโปรดแล้ว `GET /notes/favorites` ได้ `count 0` · เพิกถอน token แล้ว reload
ถูกพาไปหน้าเข้าสู่ระบบและ session ถูกล้าง · หน้าโปรไฟล์กว้าง 375 px ไม่มี scroll แนวนอน · อัปโหลด PDF 12 MB: แถบขึ้น 0% แล้ว "ส่งไฟล์ครบแล้ว…"
ก่อนเห็นกล่องรหัสแก้ไข และปุ่มกลับเป็น "อัปโหลด ✓" (ในเครื่องส่งเร็วจนไม่เห็นเปอร์เซ็นต์ระหว่างทาง ค่ากลางตรวจด้วย WEB-67)
· `/?sort=rating` เลือก "คะแนนสูงสุด" ในตัวกรองและโน้ตที่มีคะแนนขึ้นก่อน · console ไม่มี error · ในหน้าต่างที่ browser มองว่าซ่อนอยู่
event `close` ของ `<dialog>` มาช้า จึงคืน focus ทันทีตอนปิดแทนการรอ event

### 2.17 Web app — `admin-utils.js` หน้าตรวจรายงานของผู้ดูแล (`node --test`, Issues #17, #18)

pure function ของหน้า `admin.html` ใน [`web/`](../../web/) แยกจากส่วนที่แตะ DOM (`admin.js`) · เลข WEB ต่อจาก 2.16

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| WEB-70 | `groupReports` รวมรายงานตามโน้ต เรียงตามรายงานล่าสุดของแต่ละโน้ต | 3 รายงานจาก `GET /reports` (โน้ต 7, 9, 7 ตามลำดับเวลาใหม่ไปเก่า) | 2 กลุ่ม `[7, 9]` · โน้ต 7 มีรายงาน `[5, 2]` · object `note` อยู่ที่กลุ่ม ไม่ซ้ำในแต่ละรายงาน |
| WEB-71 | `groupReports` กับรายการว่างหรือเสีย | `[]`, `undefined`, รายการที่ไม่มี `note` | `[]` ทุกกรณี |
| WEB-72 | `withoutReport` เอารายงานออกทีละรายการ และเอาโน้ตออกเมื่อไม่เหลือรายงาน | ยกเลิกรายงาน 5 แล้ว `'2'` | หลังครั้งแรกยังมี 2 กลุ่ม · หลังครั้งที่สองเหลือโน้ต 9 · รายการเดิมไม่ถูกแก้ |
| WEB-73 | `withoutNote` เอาโน้ตออกพร้อมรายงานทั้งหมด | ลบโน้ต `'7'` | เหลือโน้ต 9 · `reportCount` = 1 |
| WEB-74 | `summaryLine` นับรายงานและโน้ต | 3 รายงาน 2 โน้ต · ว่าง | `รายงานที่รอตรวจ 3 รายการ จาก 2 โน้ต` · `ไม่มีรายงานที่รอตรวจ` |
| WEB-75 | `renderReportGroup` แสดงโน้ต เหตุผลทุกข้อ และปุ่มทั้งสองแบบ | กลุ่มของโน้ต 7 | ลิงก์ `/note.html?id=7`, วิชา + ผู้อัปโหลด, `ถูกรายงาน 2 ครั้ง`, เหตุผลทั้งสอง, `data-dismiss-report` 5 และ 2, `data-remove-note="7"`, เวลา `6 ต.ค. 2569 10:00` |
| WEB-76 | `renderReportGroup` escape ค่าที่ผู้ใช้พิมพ์ | ชื่อโน้ต `<img …>`, เหตุผล `<script>`, ชื่อผู้รายงาน `<b>x</b>`, ผู้อัปโหลด `"q"` | ไม่มีแท็ก `<img`/`<script`/`<b>` ได้ `&lt;…` และ `&quot;` |
| WEB-77 | `adminErrorMessage` ครอบ error ของ API ผู้ดูแล | `403 forbidden`, `401`, `503`, `404`, status `0`, `500` | ข้อความเฉพาะของแต่ละกรณี (`403` = หน้านี้สำหรับผู้ดูแลระบบเท่านั้น) |
| WEB-78 | `safeNextPath` ยอมให้กลับมาหน้าผู้ดูแลหลัง login (`session-utils.test.js`) | `/admin.html` | ได้ค่าเดิม |

mutation 10 แบบถูกจับครบ: ไม่เช็กกลุ่มเดิม (สร้างกลุ่มทับ), ไม่ข้ามรายงานที่ไม่มี `note`, ไม่เอากลุ่มว่างออก, เทียบ id โดยไม่แปลงเป็นข้อความ,
ไม่ escape เหตุผล/ชื่อผู้รายงาน, ตัดข้อความกรณีว่าง, ตัดข้อความ `forbidden`, ใส่ id ของรายงานแทน id ของโน้ตในปุ่มลบ และเอา `/admin.html` ออกจาก `NEXT_PAGES`

**ตรวจบน browser จริง (2026-10-06, อัตโนมัติ):** รอบนี้ extension ที่ใช้คุม Chrome ต่อไม่ได้ จึงใช้ Microsoft Edge แบบ headless (profile ชั่วคราวแยกจากของผู้ใช้)
คุมผ่าน Chrome DevTools Protocol ด้วยสคริปต์ Node ที่ไม่ได้ commit · service จริงบน SQLite (auth, notes ตั้ง `ADMIN_USER_IDS=1`) + ตัวแทน nginx ที่เพิ่ม `/reports`
ผล: เปิด `/admin.html` ตอนไม่ login ถูกพาไป `/login.html?next=%2Fadmin.html` · สมาชิกทั่วไปเห็น "หน้านี้สำหรับผู้ดูแลระบบเท่านั้น…" ไม่มีรายการ ปุ่มโหลดใหม่ซ่อน
และหน้าโปรไฟล์ไม่มีลิงก์ผู้ดูแล · ผู้ดูแลเห็นลิงก์ในโปรไฟล์ กดแล้วได้ "รายงานที่รอตรวจ 3 รายการ จาก 2 โน้ต" รวมเป็น 2 การ์ด ชื่อโน้ต/ชื่อผู้รายงาน/เหตุผลที่มี
`<script>`, `<b>`, `<img onerror>` แสดงเป็นข้อความ (ไม่มี element ที่ถูกฉีดใน DOM) · ยกเลิกรายงานแล้วได้ "ยกเลิกรายงานแล้ว โน้ตยังอยู่" focus ไปที่ข้อความ
API เหลือ 2 รายงานและโน้ตยังเปิดได้ (`200`) · กดลบโน้ตแล้วยกเลิก focus กลับปุ่มเดิม · ยืนยันลบแล้วการ์ดหาย `GET /notes/2` ได้ `404`
· เพิกถอน token แล้วกดยกเลิกรายงาน ถูกพาไปหน้าเข้าสู่ระบบและ session ถูกล้าง · ยกเลิกรายงานสุดท้ายแล้วได้ "ไม่มีรายงานที่รอตรวจ"
· หน้าผู้ดูแลและหน้าโปรไฟล์กว้าง 375 px ไม่มี scroll แนวนอน · console ไม่มี JavaScript error มีแค่บรรทัด network ของ `403`/`401`/`404` ที่ตั้งใจให้เกิด
(รวม `403` ของการเช็กลิงก์ผู้ดูแลในหน้าโปรไฟล์ของสมาชิกทั่วไป)

### 2.18 Web app — `stats-utils.js` หน้าสถิติ (`node --test`, Issue #16 + US-28 AC3)

pure function ของหน้า `stats.html` ใน [`web/`](../../web/) แยกจากส่วนที่แตะ DOM (`stats.js`) · เลข WEB ต่อจาก 2.17

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| WEB-79 | `overviewCards` แสดงยอดรวมจาก `GET /stats` | `total_notes 9`, `total_downloads 21`, ผู้แบ่งปัน 6 คน | `9`, `21`, `6` |
| WEB-80 | `overviewCards` กับ body ที่ไม่มีหรือว่าง | `null`, `{}`, `top_contributors` ที่ไม่ใช่ list | `0`, `0`, `0` ทุกกรณี |
| WEB-81 | `leaderboard` แสดงอันดับต้น ๆ โดยไม่เปิดเผยเลขบัญชีของคนอื่น | 6 คน, ผู้ดูคือ id 2 (อันดับ 2) · ไม่ login · ไม่มี list | 5 แถว อันดับ 1 = `สมาชิก` 12, อันดับ 2 = `คุณ` 6 ไม่มี `owner_id` ในผล · ไม่ login ทุกแถวเป็น `สมาชิก` · `[]` |
| WEB-82 | `myRank` บอกอันดับของผู้ดู | id 2 · id 3 (อันดับ 6 นอก 5 อันดับแรก) · id ที่ไม่มี · ไม่ login | `คุณอยู่อันดับ 2 จาก 6 ผู้แบ่งปัน (ดาวน์โหลดรวม 6 ครั้ง)` · อันดับ 6 · `null` · `null` |
| WEB-83 | `statsLine` แยกเปิดดูกับดาวน์โหลด และมีคำขอบคุณ (#16 AC2, US-28 AC3) | `views 12`, `downloads 3`, `thanks 2` · `{}` | `เปิดดู 12 · ดาวน์โหลด 3 · ขอบคุณ 2` · ศูนย์ทั้งหมด |
| WEB-84 | `renderStatsRow` แสดงสถานะกำลังโหลด ตัวเลข หรือ error ของโน้ตหนึ่งตัว | `{}` · `{stats}` · `{error}` | `กำลังโหลดสถิติ…` · ลิงก์ `/note.html?id=7` + วิชา + ตัวเลข · ข้อความ error มี class `stats-error` |
| WEB-85 | `renderStatsRow` ไฮไลต์โน้ตที่เปิดมาจากหน้าโปรไฟล์ (`?id=`) | `selected = true` | class `is-selected` และ `aria-current="true"` |
| WEB-86 | `renderStatsRow` escape ค่าที่ผู้ใช้พิมพ์ | ชื่อโน้ต `<img …>`, บทเรียน `<b>x</b>` | ไม่มีแท็ก `<img`/`<b>` ได้ `&lt;img` |
| WEB-87 | `statsErrorMessage` แปลตาม status เพราะ stats-service มีข้อความ error ของตัวเอง | `401`, `403`, `503` (ข้อความอังกฤษจาก service), `404 not_found`, status `0`, `502` | ข้อความไทยเฉพาะของแต่ละกรณี (`403` = ดูสถิติได้เฉพาะโน้ตที่คุณอัปโหลด) |
| WEB-88 | แถวโน้ตของฉันในหน้าโปรไฟล์มีปุ่มไปหน้าสถิติ (`profile-utils.test.js`) | โน้ต id 7 | มี `<a class="secondary-btn" href="/stats.html?id=7">สถิติ</a>` |
| WEB-89 | `safeNextPath` ยอมให้กลับมาหน้าสถิติหลัง login (`session-utils.test.js`) | `/stats.html?id=7` | ได้ค่าเดิมพร้อม query |

mutation 11 แบบ ถูกจับ 10 แบบ: ใส่เลขบัญชีในป้ายอันดับ, ไม่ตัดเหลือ 5 อันดับ, ไม่คืน `null` เมื่อไม่มีอันดับ, รวมเปิดดูกับดาวน์โหลด, ไม่ escape ชื่อโน้ต,
ไม่แสดง error ในแถว, ตัดข้อความ `403`, ไม่เช็กว่า `top_contributors` เป็น list, เอาปุ่มสถิติออกจากหน้าโปรไฟล์ และเอา `/stats.html` ออกจาก `NEXT_PAGES`
· แบบที่หลุดคือเอาเงื่อนไข "ไม่ login" ออกจากการหาแถว "คุณ" ซึ่งเป็นโค้ดที่ไม่มีผล (`owner_id` เป็น `NOT NULL` จึงไม่มีวันเท่ากับ `null`) จึงลบเงื่อนไขนั้นออกจากโค้ดแทน

**ตรวจบน browser จริง (2026-10-06, อัตโนมัติ):** ตั้งค่าแบบเดียวกับ 2.17 (Edge แบบ headless ผ่าน DevTools Protocol) และรัน stats-service ตัวจริงบน SQLite ไฟล์เดียวกับ
notes-service · ตัวแทน nginx ส่ง `/stats` และ `/notes/<id>/stats` ไปที่ stats-service ผล: ไม่ login เห็นการ์ด 3 ใบ (3 โน้ต, ดาวน์โหลด 1, ผู้แบ่งปัน 1)
อันดับเป็น "สมาชิก" ไม่มีกล่องอันดับของตัวเอง ส่วนของฉันมีลิงก์ `/login.html?next=%2Fstats.html` และเมนู "สถิติ" ถูกเลือกอยู่ · เจ้าของโน้ตเห็น
"คุณอยู่อันดับ 1 จาก 1 ผู้แบ่งปัน…" อันดับเป็น "คุณ" และ 3 แถวตรงกับ stats-service ที่เรียกตรง (โน้ต 1: เปิดดู 2 · ดาวน์โหลด 1 · ขอบคุณ 1) ชื่อโน้ตที่มี
`<script>` แสดงเป็นข้อความ และ `view_count` ไม่เพิ่มหลังเปิดหน้า · กดปุ่ม "สถิติ" ในโปรไฟล์ไปที่ `?id=1` แล้วแถวนั้นถูกไฮไลต์ · `?id=99` ได้แถว "โน้ต #99"
พร้อม "ไม่พบโน้ตนี้แล้ว…" · สมาชิกอีกคนเปิด `?id=1` ได้ "ดูสถิติได้เฉพาะโน้ตที่คุณอัปโหลด" · เพิกถอน token แล้ว reload ส่วนของฉันกลายเป็นลิงก์เข้าสู่ระบบ
session ถูกล้าง การ์ดภาพรวมยังอยู่ · หน้าสถิติและหน้าโปรไฟล์กว้าง 375 px ไม่มี scroll แนวนอน · console ไม่มี JavaScript error มีแค่บรรทัด network ของ
`404`/`403`/`401` ที่ตั้งใจให้เกิด

### 2.19 ~~Web app — `edit-utils.js` หน้าแก้/ลบด้วยรหัสแก้ไข~~ (ยกเลิกแล้ว, ADR-013)

หน้า `edit.html`, `edit.js` และ `edit-utils.js` ถูกลบพร้อมกับ edit token ต่อโน้ต เทสต์ WEB-90 ถึง WEB-94 จึงไม่มีแล้ว
เจ้าของแก้/ลบจากหน้าโปรไฟล์ขณะ login (WEB-62 ถึง WEB-64 และ E2E-04) · ผลตรวจบน browser ของหน้านี้ (2026-10-06) ดูได้ในประวัติของไฟล์นี้

### 2.20 Deploy บน Vercel — Blob storage, URL ของ Neon และ `vercel.json` (`pytest`, ADR-009)

ไฟล์ [`src/tests/test_vercel_deploy.py`](../../src/tests/test_vercel_deploy.py) · ใช้ Blob client ปลอมที่จดทุก call ไว้ จึงไม่ต้องต่อเน็ตหรือมี token จริง

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| VC-01 | `BlobFileStorage.build_key` ตั้งชื่อแบบเดียวกับ `LocalFileStorage` | `application/pdf` สองครั้ง | ลงท้าย `.pdf`, ยาวเท่ากัน, ไม่ซ้ำกัน |
| VC-02 | บันทึกแล้วอ่านกลับได้ และเก็บแบบ private | ไฟล์ PDF | `put` ด้วย `access="private"`, content type เดิม, `overwrite=False` · `exists` จริง · อ่านได้ไบต์เดิม |
| VC-03 | ไฟล์ที่ไม่มีใน Blob ทำตัวเหมือนไฟล์ที่หายจากดิสก์ | key ที่ไม่มี | `exists` เป็นเท็จ, `open` โยน `FileNotFoundError`, `delete` ไม่ error |
| VC-04 | รูปตัวอย่างเขียนซ้ำได้ | `save_bytes` key เดิมสองครั้ง | ได้ค่าล่าสุด และทุกครั้งส่ง `overwrite=True` |
| VC-05 | อัปโหลด → ดาวน์โหลด → ภาพตัวอย่าง → ลบด้วยรหัส ผ่าน API เมื่อใช้ Blob | PNG ผ่าน `POST /notes` | ดาวน์โหลดได้ไบต์เดิม, ภาพตัวอย่างเป็น PNG, มี 2 blob · ลบแล้วไม่เหลือ blob |
| VC-06 | ดาวน์โหลดโน้ตที่ blob หายไปแล้ว | ลบ blob ทิ้งก่อนดาวน์โหลด | `404` ไม่ใช่ `500` |
| VC-07 | ค่าเริ่มต้นยังเก็บบนดิสก์ | ไม่ตั้ง `NOTES_STORAGE_BACKEND` | `LocalFileStorage` |
| VC-08 | `NOTES_STORAGE_BACKEND=blob` เลือก Blob | ตั้งเป็น `blob` | `BlobFileStorage` (ข้ามถ้าเครื่องไม่มี `vercel` SDK · CI ติดตั้งจาก requirements จึงรัน) |
| VC-09 | URL ของ Neon ใช้ psycopg 3 ทั้ง notes, auth และ stats | `postgres://…`, `postgresql://…`, `postgresql+psycopg://…`, `sqlite:///…` | สองตัวแรกกลายเป็น `postgresql+psycopg://…` · สองตัวหลังไม่เปลี่ยน |
| VC-10 | request ที่ใหญ่ที่สุดที่ notes-service รับต้องไม่เกินเพดาน body ของ Vercel | `MAX_CONTENT_LENGTH` เมื่อเก็บใน Blob · และเมื่อเก็บบนดิสก์ (compose) | Blob: น้อยกว่า 4,500,000 ไบต์ (ฟอร์ม 4 MB + 256 KB ไฟล์ใหญ่กว่านั้นอัปโหลดตรง ADR-012) · ดิสก์: มากกว่า 10 MB |
| VC-11 | `vercel.json` ส่ง path ไปที่ service เดียวกับ `web/nginx.conf` | `/notes/12/stats`, `/stats`, `/notes`, `/notes/12/download`, `/reports/3`, `/auth/login`, `/profile.html` ฯลฯ | stats, stats, notes, notes, notes, auth, web ตามลำดับ rewrite |
| VC-12 | ทุก service ใน `vercel.json` มีอยู่จริง และ notes/stats เรียก auth ผ่าน binding | `vercel.json` | ทุก rewrite ชี้ service ที่มี, catch-all อยู่ท้ายสุด, binding ใส่ `AUTH_SERVICE_URL`, `root` มีโฟลเดอร์จริง |

mutation 11 แบบถูกจับครบ: เก็บแบบ public, ไม่แปลง error เป็น `FileNotFoundError`, เขียนทับไฟล์ที่อัปโหลด, `delete` โยน error, รูปตัวอย่างไม่ยอมเขียนทับ,
อ่าน `NOTES_STORAGE_BACKEND` ผิด, ไม่แปลง `postgres://` (stats), แปลงผิด driver (auth), เผื่อ request 1 MB จนเกิน 4.5 MB, ลบ rewrite ของ `/notes/<id>/stats`
และตั้งชื่อ binding ผิด

ตรวจด้วยมือบน `docker compose` (nginx + Postgres จริง, 2026-10-06): ไฟล์ 3.9 MB และ 4 MB พอดีอัปโหลดได้ (`201`) · 4 MB + 1 byte ได้ `400`
"ไฟล์ใหญ่เกิน 4 MB" · 6 MB โดน nginx ตัดที่ `5m` ได้ `413` ซึ่งหน้าเว็บแปลงเป็นข้อความเดียวกัน

deploy preview บน Vercel จริง (2026-10-06, Neon + Blob แบบ private, ทดสอบผ่าน `vercel curl`): `/`, `/notes`, `/stats` ได้ `200` · `/auth/me` และ `/notes/1/stats`
ไม่มี token ได้ `401` (แปลว่าไปถึง auth และ stats ถูกตัว) · `Dockerfile`, `nginx.conf` และไฟล์เทสต์ใน `web/` ได้ `404` · สมัคร `201` → login → `auth/me` `200`
→ อัปโหลด PNG `201` (Blob + เรียก auth ผ่าน binding) → ดาวน์โหลดได้ไบต์เดิม → ภาพตัวอย่าง `200 image/png` → สถิติรายโน้ตและภาพรวมนับดาวน์โหลด 1 → ค้นหาเจอ
→ ลบด้วยรหัส `204` แล้ว `GET` ได้ `404` · ลบบัญชีทดสอบออกจาก Neon และ Blob ไม่เหลือไฟล์ค้าง

### 2.21 E2E ผ่าน browser — เส้นทางหลักของผู้ใช้ (`pytest` + Playwright)

ไฟล์ [`src/e2e/test_web_flows.py`](../../src/e2e/test_web_flows.py) · รันกับ stack ที่ยกไว้แล้ว (`docker compose up`) ผ่าน gateway `:8080`
ทุกเทสต์สมัครบัญชีใหม่และใช้รหัสวิชาสุ่ม จึงรันซ้ำบน DB เดิมได้ · ขั้นที่ไม่ใช่สิ่งที่เทสต์นั้นตรวจ (เช่นอัปโหลดโน้ตให้อีกบัญชีมาเปิด) ทำผ่าน API ตรง ๆ

| # | Test case | ขั้นตอน | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| E2E-01 | สมัครแล้วเข้าสู่ระบบให้เอง (US-05, US-06) | กรอกแท็บสมัครสมาชิกใน `login.html#register` | กลับหน้าแรก · หน้าอัปโหลดเปิดฟอร์มและขึ้นชื่อที่สมัคร |
| E2E-02 | อัปโหลดผ่านฟอร์ม แล้วค้นหาเจอ (US-07, US-08, US-09, US-31) | login → เลือกไฟล์ PDF + กรอก metadata → อัปโหลด → กดลิงก์ไปหน้าค้นหา | ขึ้นกล่องสำเร็จที่บอกให้แก้/ลบจากหน้าโปรไฟล์ · ผลค้นหา `แสดง 1 รายการ` มีชื่อโน้ตและชื่อผู้อัปโหลด |
| E2E-03 | อีกบัญชีใช้ทุกปุ่มบนหน้าโน้ต (US-12, US-13, US-14, US-15, US-28) | ดาวน์โหลด → ให้ 4 ดาว → ขอบคุณ → บันทึกรายการโปรด → แสดงความคิดเห็น → reload | ได้ไฟล์ `note.pdf` · `บันทึกคะแนนแล้ว` เฉลี่ย 4.0 · ปุ่มขอบคุณขึ้นหลังดาวน์โหลด · หลัง reload คะแนน รายการโปรด ความคิดเห็น และ `ดาวน์โหลด 1` ยังอยู่ (ไปถึง API จริง) |
| E2E-04 | เจ้าของแก้และลบจากหน้าโปรไฟล์ (US-19, US-20, ADR-013) | อีกบัญชีลบผ่าน API ก่อน → เจ้าของ login → โปรไฟล์ → แก้ชื่อ → หน้าโน้ต → โปรไฟล์ → ลบผ่านกล่องยืนยัน | อีกบัญชีได้ `403` · `บันทึกการแก้ไขแล้ว` และหน้าโน้ตขึ้นชื่อใหม่ · ปุ่มลบของโน้ตนั้นหายจากรายการ · `GET /notes/<id>` ได้ `404` |
| E2E-05 | ผลค้นหาเกินหน้าแรกบอกยอดรวม (NA-137, WEB-95, WEB-96) | 21 โน้ตรหัสวิชาเดียวกัน แล้วค้นด้วยรหัสนั้น → โหลดเพิ่ม | `แสดง 20 จาก 21 รายการ` และมีปุ่มโหลดเพิ่ม → `แสดง 21 รายการ` และปุ่มหาย |
| E2E-06 | หน้าจอมือถือกว้าง 375 px (NFR-008, NFR-009) | เปิด `/`, `login.html`, `upload.html`, `stats.html` | ไม่มี scroll แนวนอนทุกหน้า · ช่องค้นหาและปุ่มค้นหาอยู่ในจอแรกโดยไม่ต้อง scroll |
| E2E-07 | ไฟล์ 6 MB อัปโหลดผ่านหน้าเว็บ (NFR-006, ADR-012) | เลือก PDF 6 MB แล้วอัปโหลด → ค้นด้วยรหัสวิชา → ดาวน์โหลดผ่าน API | ขึ้นกล่องสำเร็จ · `size_bytes` ตรง · ดาวน์โหลดได้ไบต์เดิมครบ · บน compose ไปทางฟอร์ม (nginx `11m`) กับ stack ที่เก็บใน Blob ไปทางอัปโหลดตรง |

รันบนเครื่อง local (2026-10-08, compose stack ใหม่, Edge ผ่าน `--browser-channel msedge`): ผ่าน 6/6 สองรอบติดกันบน DB เดิม ~15 วินาที
mutation 5 แบบถูกจับครบ (แก้ไฟล์ใน container `web` ตรง ๆ แล้วคืนค่า): หน้าค้นหาไม่ใช้ `total`, ปุ่มขอบคุณไม่ขึ้นเลย, รหัสผิดไม่ถูกปฏิเสธ,
`body` กว้างเกินจอมือถือ, ลิงก์หลังอัปโหลดไม่พาไปผลค้นหา · รอบแรกเจอว่าลิงก์หลังอัปโหลดค้นด้วยชื่อโน้ต ชื่อซ้ำจากรอบก่อนทำให้นับผิด จึงใส่รหัสสุ่มในชื่อ

### 2.22 Migration ด้วย Alembic — notes-service และ auth-service (`pytest`, ADR-010)

ไฟล์ [`src/tests/test_migrations.py`](../../src/tests/test_migrations.py) · รันได้ทั้ง SQLite และ Postgres (`TEST_DATABASE_URL`) · ข้อที่มี 2 แบบ (notes, auth) รันแยกต่อ service

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| MG-01 | upgrade จาก DB ว่างได้ schema ตรงกับ models | สตาร์ตทั้งสอง service บน DB เดียวกัน แล้วรัน `alembic check` ผ่าน `env.py` ตัวจริง | ไม่มีความต่างทั้งคอลัมน์ index และ constraint · ตาราง version อยู่ที่ head · ไม่เสนอให้ลบตารางของอีก service |
| MG-02 | DB เดิมที่สร้างด้วย `create_all` ถูก stamp แล้วข้อมูลไม่หาย | `create_all` + ใส่ 1 แถว (`notes` / `users`) แล้วสตาร์ต service | ตาราง version อยู่ที่ head · แถวเดิมยังอยู่ 1 แถว |
| MG-03 | สตาร์ตซ้ำไม่เปลี่ยนอะไร | สตาร์ต service สองครั้ง | ไม่ error · ตาราง version มีแถวเดียวที่ head |
| MG-04 | สอง service ใช้ DB เดียวกันโดยนับเวอร์ชันแยกกัน | สตาร์ต notes และ auth บน DB เดียวกัน | มี `alembic_version_notes` และ `alembic_version_auth` · ไม่มี `alembic_version` · ทั้งคู่อยู่ที่ head ของตัวเอง |
| MG-05 | downgrade ของ baseline ลบเฉพาะตารางของ service นั้น | `alembic downgrade base` ของ service หนึ่ง แล้วสตาร์ตใหม่ | ตารางของ service นั้นหายหมด ของอีก service ยังอยู่ครบ · สตาร์ตใหม่แล้วตารางกลับมา |
| MG-06 | 4 instance สตาร์ตพร้อมกันบน DB ว่าง | 4 thread รอที่ `Barrier` แล้วสตาร์ตพร้อมกัน (ข้ามบน SQLite) | ไม่มี thread ไหน error หรือค้างเกิน 30 วินาที · ตาราง version มีแถวเดียวที่ head |
| MG-07 | revision ต่อกันเป็นเส้นเดียวจาก baseline | `ScriptDirectory` ของแต่ละ service | มี head เดียว · base คือ `0001` ตัวเดียวกับที่ `upgrade_to_head()` ใช้ stamp |

mutation ที่ลองแล้ว (2026-10-09, เครื่อง local + Postgres 16 ใน Docker) ถูกจับครบ: เพิ่มคอลัมน์ใน `models.py` โดยไม่เขียน revision (MG-01 เจอ `add_column`)
· ให้ `env.py` เทียบทุกตารางใน DB (MG-01 เจอ `remove_table` ของ `users`/`auth_sessions`) · เอา advisory lock ออกทีละ service (MG-06 ล้ม 12/12 รอบ
บางรอบเป็น `DuplicateTable`/`UndefinedTable` บางรอบ thread ค้างอยู่ใน `CREATE TABLE` จนครบ 30 วินาที) · รอบแรกที่ยังไม่มีเส้นตาย เทสต์ค้างไม่จบเอง
จึงให้ thread เป็น daemon และรอรวมกันแค่ 30 วินาที

### 2.25 อัปโหลดตรงเข้า Vercel Blob — ไฟล์ถึง 10 MB บน Vercel (`pytest` + `node --test`, ADR-012)

ไฟล์ [`src/tests/test_notes_direct_upload.py`](../../src/tests/test_notes_direct_upload.py) ใช้ Blob client ปลอมจาก `test_vercel_deploy.py`
ไฟล์ที่ "browser อัปโหลด" จำลองด้วยการ `put` ลง client ปลอมตรง ๆ · WEB-97 ถึง WEB-100 อยู่ใน [`web/upload-utils.test.js`](../../web/upload-utils.test.js)

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| BU-01 | client token รูปแบบเดียวกับ `@vercel/blob` | read-write token ปลอม, pathname, 10 MB, PDF, `validUntil` | `vercel_blob_client_<storeId>_…` · ลายเซ็น = HMAC-SHA256 ของ payload · payload ครบ 6 ช่อง ห้ามเขียนทับ · ไม่มีส่วนลับของ read-write token |
| BU-02 | read-write token ผิดรูปแบบ | `""`, `vercel_blob_rw`, `vercel_blob_rw__x`, `abc` | `ValueError` |
| BU-03 | ขอ token ต้อง login | ไม่มี `Authorization` | `401` |
| BU-04 | token ใช้ได้ไฟล์เดียวของผู้ใช้คนนี้ 10 นาที | PDF 9 MB | `mode = direct` · pathname `uploads/7/<32 hex>.pdf` · `upload_url` = `https://vercel.com/api/blob/?pathname=…` · payload ผูก pathname, PDF, 10 MB, หมดอายุ +600 วินาที |
| BU-05 | ขอสองครั้งได้คนละไฟล์ | ขอ token ซ้ำ | pathname ไม่ซ้ำกัน |
| BU-06 | ไฟล์ที่ประกาศมาไม่ผ่าน → ไม่ออก token | 10 MB + 1, 0 byte, ขนาดเป็นข้อความ, GIF | `400 validation_failed` พร้อมเหตุผลของ `file` |
| BU-07 | compose ไม่มี Blob | `LocalFileStorage` | `{"mode": "form", "max_file_bytes": 10485760}` |
| BU-08 | สร้างโน้ตจากไฟล์ที่อัปโหลดตรง | PUT 5,009 byte แล้ว `POST /notes` JSON ที่อ้าง `size_bytes = 1` และ `year_level` เป็นตัวเลข | `201` · ขนาดจาก Blob (5,009) · ดาวน์โหลดได้ไบต์เดิม |
| BU-09 | metadata ผิดใน JSON | `title` ว่าง, `year_level = true` | `400` ระบุทั้งสองช่อง · ไฟล์ใน Blob ยังอยู่ |
| BU-10 | อ้างไฟล์ที่ไม่ได้ออกให้ผู้เรียก | ของผู้ใช้ 8, key ของโน้ตแบบฟอร์ม, key ของรูปตัวอย่าง, `..`, ค่าว่าง | `400 ไม่พบไฟล์ที่อัปโหลด` · ไม่มีไฟล์ไหนถูกลบ |
| BU-11 | ได้ token แต่ PUT ไม่สำเร็จ | ไม่มีไฟล์ใน Blob | `400 ไม่พบไฟล์ที่อัปโหลด` |
| BU-12 | ไฟล์ใน Blob ผิดกติกา (token ควรกันไว้แล้ว) | 10 MB + 1, GIF, PNG ใต้ชื่อ `.pdf` | `400` เหตุผลตามกรณี · ไฟล์ถูกลบ |
| BU-13 | ส่ง JSON เดิมซ้ำ | `POST /notes` สองครั้ง | ครั้งแรก `201` ครั้งที่สอง `409 upload_already_used` · ไฟล์ของโน้ตแรกยังอยู่ · `total = 1` |
| BU-14 | compose รับ JSON ที่อ้าง pathname ไม่ได้ | `LocalFileStorage` | `400` |
| BU-15 | ขอ token ใหม่ลบไฟล์ที่ค้าง | ไฟล์ไม่มีโน้ตอายุ 11 นาที, ไฟล์ใหม่, ไฟล์ของโน้ตจริง, ไฟล์ของผู้ใช้อื่น | ลบเฉพาะไฟล์ค้างของผู้ใช้คนนี้ ที่เหลืออยู่ครบ |
| BU-16 | list ของ Blob ล่ม | `iter_objects` โยน error | ยังได้ token `200` |
| WEB-97 | `uploadTicketRequest` | PDF 9 MB ชนิดตัวใหญ่ | `{file_name, content_type: "application/pdf", size_bytes}` |
| WEB-98 | `blobUploadHeaders` เหมือน `put` ของ `@vercel/blob/client` | ticket + ไฟล์ | 6 header: `authorization`, `x-api-version`, `x-vercel-blob-access: private`, store id, content type, content length |
| WEB-99 | `directNoteBody` | ฟอร์ม + ticket + ไฟล์ | ฟิลด์ฟอร์ม + `file_name` + `upload_pathname` · ไม่มี client token |
| WEB-100 | `blobUploadErrorMessage` | `0`, `403`, `500` | ข้อความเรื่องเน็ต, สิทธิ์หมดอายุ, HTTP 500 |

VC-10 เปลี่ยนเป็นตรวจเพดานเมื่อเก็บใน Blob (ยังต่ำกว่า 4.5 MB) และเพิ่มข้อที่ compose รับฟอร์มได้เกิน 10 MB · NV-13 และ WEB-35 เปลี่ยนเป็น 10 MB

ตรวจว่า token ตรงกับของจริง (2026-10-09): สร้าง token ด้วย `generateClientTokenFromReadWriteToken` ของ `@vercel/blob` 2.8.0 ใน Node
และด้วย `generate_client_token` ด้วยค่าเดียวกัน ได้สตริงเดียวกันทุกไบต์

ทดสอบกับ Blob และ browser จริง (2026-10-09, เครื่อง local): ยก compose โดยให้ notes-service ใช้ `NOTES_STORAGE_BACKEND=blob` กับ Blob store จริงของ project
(ฐานข้อมูลยังเป็น Postgres ในเครื่อง ไม่แตะ Neon) แล้วรัน E2E ทั้งชุดด้วย Edge: ผ่าน 7/7 · โน้ตของ E2E-02 และไฟล์ 6 MB ของ E2E-07 อยู่ใต้ `uploads/<id>/`
แปลว่าไปทางอัปโหลดตรงจริง และ browser ส่ง PUT ข้าม origin ไป `vercel.com/api/blob` ได้ (CORS ผ่าน) · หลังทดสอบลบไฟล์ทั้ง 24 ไฟล์ที่เทสต์สร้างออกจาก Blob
mutation 7 แบบถูกจับครบ: ยอมรับ pathname ของผู้ใช้อื่น, เชื่อขนาดจาก client, เก็บไฟล์ผิดกติกาไว้, ลบไฟล์ของโน้ตเดิมตอนส่งซ้ำ, ล้างไฟล์โดยไม่ดูว่ามีโน้ต,
token ยอมให้เขียนทับ, เซ็นด้วยกุญแจผิด

### 2.26 Gateway ตรวจ token ก่อนส่งต่อ (`node --test` + `pytest`, ADR-014)

ตารางตั้งต้นคือ [`gateway/cases.json`](../../gateway/cases.json): ทุก route สาธารณะพร้อมผลที่คาด (`login` / `edit` / `open` และถาม auth-service หรือไม่)
GW-01 ถึง GW-06 อยู่ใน [`gateway/rules.test.js`](../../gateway/rules.test.js) ตรวจฝั่ง Vercel (`gateway/rules.js` ที่ `gateway/proxy.ts` เรียก) ด้วย fetch ปลอม
GW-07 ถึง GW-10 อยู่ใน [`src/tests/test_gateway_rules.py`](../../src/tests/test_gateway_rules.py) ตรวจ `web/nginx.conf`, `vercel.json` และ route ของ Flask · บน stack จริงดู DK-10

| # | Test case | Input | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| GW-01 | `rules.js` ให้ rule และผลการตรวจตรงกับ cases.json ทุกแถว | 31 แถว รวมแก้/ลบโน้ตทั้งแบบมีและไม่มี `X-Note-Token` และ path ที่หน้าตาคล้าย (`/notes/`, `/notes/abc/stats`, `/notes/favorites/extra`) | ตรงทุกแถว · method ตัวเล็กก็ได้ผลเดียวกัน · `X-Note-Token` ว่างไม่นับเป็นรหัส |
| GW-02 | route ที่เปิดและการแก้ด้วยรหัสไม่ถาม auth-service | ทุกแถวที่ `check = skip` | ผ่านไปที่ service (`undefined`) และ fetch ไม่ถูกเรียกเลย |
| GW-03 | route ที่ต้อง login แต่ไม่มี `Authorization` | `GET /notes/mine` | `401 {"error": "unauthorized"}` + `WWW-Authenticate: Bearer` โดยไม่ถาม auth-service |
| GW-04 | token ใช้ได้ | `POST /notes/12/comments?x=1` พร้อม `Authorization`, cookie, `x-vercel-protection-bypass`, `X-Note-Token` | ผ่าน · ถาม `/auth/me` ของ origin เดียวกันครั้งเดียว ส่งต่อสาม header แรก ไม่ส่ง `X-Note-Token` |
| GW-05 | token ใช้ไม่ได้หรือ logout แล้ว | auth-service ตอบ `401` | `401 {"error": "unauthorized"}` |
| GW-06 | auth-service ล่มหรือตอบแปลก | fetch โยน error, `500`, `502`, `403` | `503 {"error": "auth_unavailable"}` ทุกแบบ ไม่มีแบบไหนปล่อยผ่าน |
| GW-07 | `map` สองชั้นใน `web/nginx.conf` ให้ผลตรงกับ cases.json | ทุกแถว (จำลองการเลือก regex ตามลำดับแบบ nginx) | rule และ `login`/`skip` ตรงทุกแถว |
| GW-08 | ทุก location ของ API ตรวจจริง | location ที่ `proxy_pass` ไป notes/stats-service | 5 location มี `auth_request` และ `set $gateway_check_main` · `= /stats` (เปิด) ไม่มี · location ของ subrequest เป็น `internal`, ตอบ `204` เมื่อ `skip` และไม่ส่ง body ไป auth-service |
| GW-09 | ทุก route ของทุก service อยู่ในตาราง | `url_map` ของ notes, stats, auth-service (ยกเว้น `/health`) | ทุก method + route มีแถวใน cases.json · route ใหม่ที่ลืมตัดสินว่าต้อง login ไหมทำให้ล้ม |
| GW-10 | `proxy.matcher` ใน `vercel.json` ครอบพอดี | ทุกแถวที่ไม่ใช่ `open` · `/`, `/index.html`, `/upload.html`, `/app.js`, `/auth/login`, `/auth/me`, `/stats` | middleware รันกับทุก path ที่ต้องตรวจ และไม่รันกับหน้าเว็บ, `/auth` และ `/stats` · ไฟล์ entrypoint มีอยู่จริง |

mutation 12 แบบถูกจับครบ (2026-10-09): nginx ลืม route ขอบคุณ, ไม่มีข้อยกเว้นของรหัส, ข้อยกเว้นรับรหัสว่าง, subrequest อ่าน map เอง,
`/reports/` ลืม `auth_request` · cases.json ขาด route ขอบคุณ · matcher ขาด `/reports` · `rules.js` ลืม route ให้คะแนน, ไม่มีข้อยกเว้นของรหัส,
auth-service ตอบ 5xx แล้วปล่อยผ่าน, ไม่ส่ง cookie ต่อ, ไม่มี `Authorization` ก็ยังถาม auth-service

ตรวจบน stack จริง (2026-10-09):
- **docker compose (nginx):** เส้นทางเดียวกับ DK-10 ผ่านครบ · อัปโหลด PDF 4 MB ผ่าน `auth_request` ได้ `201` · ลองลบ `set` ออกแล้วให้ subrequest อ่าน map เอง
  `GET /notes/1/stats` ไม่มี token หลุดไปถึง stats-service (`Authentication required`) ตรงกับที่ comment ใน `nginx.conf` บอก · E2E-01 ถึง E2E-06 ผ่าน 6/6 บน stack นี้
- **Vercel preview** (Neon ตัวเดียวกับ production ใช้บัญชีทดสอบบัญชีเดียวแล้วลบทิ้ง): `middleware.ts` ที่ root ถูกเมินเมื่อใช้ `services` ต้องประกาศผ่าน `"proxy"` ·
  `.mjs` ล้มด้วย `ERR_REQUIRE_ESM` จึงเขียน `rules.js` เป็น CommonJS · หลังแก้: `/notes/1/stats`, `/reports`, `/notes/mine` ไม่มี token หรือ token มั่วได้
  `401 {"error":"unauthorized"}` จาก middleware · `PATCH /notes/999999` ไม่มีอะไรได้ `401` ส่วนที่มี `X-Note-Token` ผ่านไปถึง service (`404`) · `GET /notes` เปิดได้ `200` ·
  token จริง: `/notes/mine` `200`, อัปโหลด 2 KB / 3 MB / 3.9 MB / 4 MB ได้ `201` ทุกขนาด, สถิติของเจ้าของ `200`, ลบในฐานะเจ้าของ `204` · logout แล้ว token เดิมได้ `401` ·
  หลังทดสอบไม่เหลือ user, โน้ต หรือไฟล์ใน Blob

## 3. Test Report

**รันล่าสุด:** 2026-10-06 (เครื่อง local, Windows 11, `main` ที่ `65bd2bc` หลัง merge #90 #94 #95 #96) · ผล Python เท่ากับรอบ `3cbc4f2` เพราะรอบนี้ไม่ได้แก้โค้ดของ service · แถว smoke แบบไม่ใช้ Docker ยังเป็นผลวันที่ 2026-09-27

| ชุด | คำสั่ง | ผล |
| --- | --- | --- |
| JS unit | `cd prototypes/sprint1 && node --test` | ✅ 7 passed / 0 failed |
| Python unit + integration | `pytest src/tests -v --cov=services/notes-service --cov=services/auth-service --cov=src` (คำสั่งเดียวกับ CI) | ✅ 376 passed / 0 failed / 1 xfailed — notes API 59, notes reports 34, notes favorites 32, auth API 30, auth credentials 29, notes preview 27, notes ratings 21, notes thanks 20, notes validation 18 + boundary 19, notes owner 18, auth tokens 14, notes identity 13, stats 11, notes comments 9, auth email_error 9 (AE-09 เป็น xfail), notes sort rating 7, fizzbuzz 5, edit-token property 2 · coverage รวม 98% (`notes-service/app.py` 91%, `identity.py`/`models.py`/`validation.py`/`credentials.py` 100%) · stats-service ไม่อยู่ใน `--cov` ของ CI |
| Smoke DK-03 ถึง DK-06 แบบไม่ใช้ Docker | รัน `auth-service` กับ `notes-service` ตัวจริงบน SQLite (notes ชี้ `AUTH_SERVICE_URL` ไปที่ auth) แล้วรันสคริปต์ `run:` ของแต่ละ step ที่ดึงออกมาจาก `ci.yml` ตรง ๆ | ✅ ผ่านครบ 6 step (`upload auth OK`, `end-to-end OK`, `edit/delete OK`, `auth OK`, validation `400`) · บน Postgres + compose จริงรอผลจาก CI เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน · ตอนรันบน Windows ต้องแทน `/tmp/` เป็น path ของ Windows เพราะ curl ของ Windows อ่าน `/tmp` ของ Git Bash ไม่ได้ (ไม่ได้แก้ใน `ci.yml` เพราะ CI รันบน Linux) |
| Container smoke (compose e2e) | `docker compose up` + `curl` | ✅ ผ่านบน CI ([run #33351842320](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/33351842320), 1m6s) — log ยืนยัน `created note #1` และ `end-to-end OK` · ไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน · ล่าสุดผ่านบน CI ของ `main` ที่ `3cbc4f2` ([run #37326768845](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/37326768845), 2026-10-05) · ล่าสุดผ่านบน CI ของ `main` ที่ `65bd2bc` ([run #37457730164](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/37457730164), 2026-10-06) · 2026-10-06 รันบนเครื่อง local ได้แล้ว (ดูแถว "ทดสอบด้วยมือบน compose จริง") |
| JS unit (web) | `cd web && node --test` | ✅ 89 passed / 0 failed — search-utils 19, note-utils 14, session-utils 13, upload-utils 12, profile-utils 9, stats-utils 9, admin-utils 8, edit-utils 5 |
| ทดสอบด้วยมือบน compose จริง (Postgres 16 + nginx) | `ADMIN_USER_IDS=1 docker compose -p noteshare-e2e up -d --build` (ชื่อ project แยกเพื่อให้ได้ฐานข้อมูลว่าง) แล้วกดผ่าน Chrome ที่ `http://localhost:8080` ด้วยบัญชีทดสอบ 2 บัญชี | ✅ 2026-10-06 บน `65bd2bc`: สมัคร + login อัตโนมัติ · อัปโหลด PDF ได้รหัสแก้ไข · ค้นหาเจอ · หน้าโน้ต: รายการโปรด, ความคิดเห็น (เวลาตรงกับเวลาเครื่อง), เจ้าของขอบคุณ/รายงานโน้ตตัวเองไม่ได้ · บัญชีที่สอง: ดาวน์โหลด (ยอดเพิ่ม, ปุ่มขอบคุณขึ้นหลังดาวน์โหลด) → ให้ 4 ดาว (เฉลี่ย 4.0) → ขอบคุณ → รายงาน · โปรไฟล์ขึ้นปุ่มผู้ดูแลเฉพาะบัญชีเลข 1 · หน้าผู้ดูแลกันสมาชิกทั่วไป ผู้ดูแลเห็นรายงานพร้อมเหตุผลและยกเลิกได้ · สถิติตรงกับที่ทำ (เปิดดู 3, ดาวน์โหลด 1, ขอบคุณ 1) · หน้าแก้ด้วยรหัส: รหัสผิดถูกปฏิเสธ, บัญชีที่ไม่ใช่เจ้าของแก้ชื่อได้ด้วยรหัส, ลบผ่านกล่องยืนยันแล้ว `GET /notes/1` ได้ `404` · `?next=` พากลับหน้าผู้ดูแล · Postgres: มี 9 ตาราง, การลบโน้ตลบ ratings/thanks/comments/reports/favorites ของโน้ตนั้นครบ, ข้อมูลอยู่ครบหลัง `docker compose restart`, `?topic=%` และ `?topic=_` เจอเฉพาะโน้ตที่มีตัวอักษรนั้นจริง (มีโน้ตที่ไม่มีไว้เทียบ) · log ไม่มี `5xx` มีแค่ `/favicon.ico` `404` · ข้อจำกัด: ตอนดาวน์โหลดปิดการบันทึกไฟล์ลงดิสก์ไว้ในหน้า (request และการนับยังจริง), ไฟล์ทดสอบเป็น PDF เปล่าจึงไม่มีภาพตัวอย่าง, ไม่ได้ตรวจความกว้างมือถือรอบนี้ |

**ผลรันบน CI (PR #56):** ทั้ง 3 job ผ่านหมด — `js-tests` 13s, `python-tests` 13s, `docker-build` 1m6s

CI จับของจริงไปแล้ว 2 ครั้งตั้งแต่ตั้งขึ้นมา ทั้งที่เทสต์ในเครื่องเขียวหมด:
1. PR ที่ base เป็น feature branch อื่นไม่ถูกทดสอบเลย เพราะ trigger กรองไว้แค่ `branches: [main]` → เอาตัวกรองออกจาก `pull_request`
2. `printf '%PDF-1.4 ...'` ใน smoke test ล้มเพราะ `%P` ถูกตีความเป็น format specifier → เปลี่ยนเป็น `printf '%s'`

> DK-01 เคยผ่านมาแล้วตอน Lab 6 (build + push ขึ้น Docker Hub สำเร็จ ดู [`docker/README.md`](../../docker/README.md))
> รอบนี้เพิ่ม DK-02/DK-03 เข้ามาเป็น smoke test อัตโนมัติใน CI ซึ่ง Lab 6 ยังทำด้วยมือ

## 4. CI

[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) รันทุก push เข้า `main` และทุก PR ที่ยิงเข้า `main`
โดยแบ่ง job เพื่อให้อ่านผลได้ว่าอะไรพัง (`lint` รันแยกอิสระ ไม่มี job ไหนรอ)

```
js-tests ──────────────┐    ┌──> docker-build (build image + smoke ด้วย curl)
python-tests ──────────┼────┤
python-tests-postgres ─┘    └──> e2e-tests (build image + E2E ผ่าน Chromium)
```

`docker-build` ตั้ง `needs: [js-tests, python-tests, python-tests-postgres]` ไว้ เพราะไม่มีประโยชน์ที่จะเสียเวลา build image
ถ้าเทสต์ยังแดงอยู่ · `e2e-tests` (ชื่อใน GitHub: **E2E tests (browser)**) รอสามอันแรกเหมือนกัน แล้วยก stack ของตัวเองแยกจาก `docker-build`
เทสต์ที่ล้มจะเก็บ trace ของ Playwright เป็น artifact `e2e-traces` (7 วัน) เปิดดูทีละขั้นได้ด้วย `playwright show-trace`

`js-tests` รัน `node --test` ใน `gateway/` ด้วย (GW-01 ถึง GW-06, ADR-014) · step สุดท้ายของ `docker-build` (DK-10) หยุด auth-service
เพื่อดูคำตอบ `503` ของ gateway จึงต้องอยู่ท้ายสุดเสมอ step ที่เพิ่มทีหลังให้วางไว้ก่อนหน้า

`python-tests-postgres` (ชื่อใน GitHub: **Unit tests (PostgreSQL)**) รันเทสต์ Python ชุดเดียวกับ `python-tests`
แต่ต่อ `postgres:16-alpine` (image เดียวกับ compose) ที่ GitHub Actions ยกขึ้นเป็น service container
`conftest.py` เห็น `TEST_DATABASE_URL` แล้วล้าง schema และสร้างตารางของทุก service ใหม่ก่อนทุกเทสต์ ให้แต่ละเทสต์เริ่มจาก DB ว่างเหมือนไฟล์ SQLite ใหม่
เทสต์ที่ต้องใช้ DB ขอ URL จาก fixture `make_db_url()` จึงรันได้ทั้งสองแบบโดยไม่ต้องแก้ตัวเทสต์
ตั้งแต่ ADR-010 ตารางเหล่านี้สร้างผ่าน migration ของ Alembic ตัวเดียวกับที่ service ใช้ตอนสตาร์ต ไม่ใช่ `create_all`
job นี้ตั้ง `timeout-minutes: 15` ไว้ (ปกติจบใน ~4 นาที) ถ้าเทสต์ค้างจะได้ล้มแทนที่จะรอ 6 ชั่วโมงตามค่าเริ่มต้นของ GitHub Actions

ตรวจว่า job นี้จับของที่ SQLite ปล่อยผ่านได้จริง (2026-10-08, เครื่อง local + Postgres 16 ใน Docker): เปลี่ยน `ilike` เป็น `like` ทีละฟิลด์ใน `GET /notes?q=`
ครบ 5 ฟิลด์ (title, subject_name, subject_code, lesson, topic) — NA-135 ผ่านบน SQLite ทั้ง 5 แบบ และล้มบน Postgres ทั้ง 5 แบบ · ก่อนเพิ่ม NA-135
ทั้งชุดผ่านทั้งสองฐานข้อมูลแม้มี mutation นี้ แปลว่าการค้นแบบไม่สนตัวพิมพ์ไม่เคยถูกทดสอบเลย

## 5. งานที่ยังค้าง

- [x] **วชิรวิทย์** — เขียน unit test ของตัวเอง (เสนอ: logic filter คณะ/ปี/ประเภทไฟล์ และประวัติการค้นหาใน `wachirawit_search_note_prototype.html` ต้องแยก pure function ออกมาก่อนแบบเดียวกับ Lab 7) · ทำแล้วเป็นเทสต์ของ Notes Service แทน prototype: `test_notes_preview.py`, `test_notes_favorites.py`, `test_notes_thanks.py` และเทสต์ download/topic/date ใน `test_notes_api.py`
- [x] **กฤตเมธ** — เขียน unit test ของตัวเอง (เสนอ: การคำนวณคะแนนเฉลี่ยหลังส่ง rating ใน `kittamet_note_rating_prototype.html`) · ทำแล้วเป็นเทสต์ของ service แทน prototype: `test_notes_comments.py`, `test_notes_reports.py`, `test_notes_ratings.py` (รวมค่าเฉลี่ย rating) และเทสต์ stats ใน `test_stats_service.py`
- [x] เขียนเทสต์ของ `POST /notes` ที่ commit ไม่ผ่าน แล้วต้องไม่ทิ้งไฟล์กำพร้าไว้ใน storage — NA-12
- [x] เทสต์ที่รันกับ PostgreSQL จริง — ตอนนี้เทสต์ Python ใช้ SQLite ส่วน compose ใช้ Postgres จึงมีช่องว่างเรื่องความต่างของ dialect (`ilike`, การเทียบวันที่) ที่จับได้แค่ตอน smoke test · 2026-10-06 ตรวจด้วยมือบน Postgres 16 ของ compose แล้ว (`?topic=` กับ `%`/`_`, การลบแถวลูก, ข้อมูลหลัง restart — ดูหัวข้อ 3) แต่ยังไม่มีเทสต์อัตโนมัติ · **2026-10-08 ทำแล้ว:** job `Unit tests (PostgreSQL)` ใน CI รันเทสต์ Python ทั้งชุดบน Postgres 16 (หัวข้อ 4) และเพิ่ม NA-135 ที่จับได้เฉพาะบน Postgres
- [ ] เพิ่ม branch protection ให้ `main` ต้องผ่าน CI ก่อน merge (ตั้งใน GitHub Settings ไม่ใช่ในโค้ด)
- [x] E2E test อัตโนมัติผ่าน browser — มีหน้าเว็บจริงแล้ว (`web/`) แต่ยังตรวจด้วยมือ (ดูท้าย 2.13) ยังไม่มีเครื่องมืออย่าง Playwright ใน CI · 2026-10-06 กดครบทุกหน้าบน compose จริงแล้ว (ดูหัวข้อ 3) แต่ยังเป็นการตรวจด้วยมือ · **2026-10-08 ทำแล้ว:** job `E2E tests (browser)` ใน CI รัน Playwright 6 เส้นทาง (หัวข้อ 2.21)
