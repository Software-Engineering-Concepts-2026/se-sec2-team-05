# Test Plan & Report — NoteShare

เอกสารนี้สรุปว่าทีมทดสอบอะไร ด้วยเครื่องมืออะไร และผลล่าสุดเป็นอย่างไร
ตัวไฟล์เทสต์อยู่ที่ [`src/tests/`](../../src/tests/) และ [`prototypes/sprint1/`](../../prototypes/sprint1/)

## 1. กลยุทธ์การทดสอบ

ตอนนี้ระบบยังไม่มี backend จริง (ดู [ADR-001](../architecture/adr/0001-tech-stack-selection.th.md)) มีแค่
Stats Service ที่คืน mock data กับ prototype ฝั่ง front-end ทีมจึงโฟกัสสองระดับนี้ก่อน

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

### 2.4 Notes Service — API (`pytest`, US-08 AC ข้อ 4)

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

| # | Test case | ขั้นตอน | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| DK-01 | ทั้ง stack build และสตาร์ตได้ | `docker compose up -d --build` | exit code 0 |
| DK-02 | ทุก service ตอบ health | `curl :5000/health`, `:5001/health`, `:5002/health` (retry 20 ครั้ง ห่างละ 3 วิ) | `200` ทั้งหมด |
| DK-03 | end-to-end ของ US-08 | อัปโหลดพร้อม metadata → กรองด้วย `faculty`+`year_level`+`q` → ดาวน์โหลด | `count = 1` และไฟล์ที่ดาวน์โหลดตรงกับต้นฉบับ (`cmp`) |
| DK-04 | validation ทำงานจริงบน stack ที่รัน | `POST /notes` ส่งแค่ `title` | `400` |
| DK-05 | สมัคร → login → ใช้ token → logout บน Postgres จริง (US-05/US-06) | `curl` ไปที่ `:5002/auth/*` | สมัคร `201` · สมัครซ้ำ `409` · โดเมนอื่น `400` · รหัสผิดกับอีเมลที่ไม่มีได้ body เดียวกัน · `me` ได้ชื่อถูก · logout `204` แล้ว `me` ด้วย token เดิมได้ `401` |

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

## 3. Test Report

**รันล่าสุด:** 2026-09-25 (เครื่อง local, Windows 11)

| ชุด | คำสั่ง | ผล |
| --- | --- | --- |
| JS unit | `cd prototypes/sprint1 && node --test` | ✅ 7 passed / 0 failed (88 ms) |
| Python unit + integration | `pytest src/tests -v` | ✅ 153 passed / 0 failed (~4 s) — stats 4, notes validation 17 + boundary 19, notes API 33, edit-token property 2, fizzbuzz 5, auth credentials 29, auth tokens 14, auth API 30 |
| Auth smoke (DK-05) แบบไม่ใช้ Docker | รัน `services/auth-service/app.py` บน SQLite แล้วรันสคริปต์ของ step DK-05 ที่ดึงออกมาจาก `ci.yml` ตรง ๆ | ✅ `auth OK` · บน Postgres จริงยังรอผลจาก CI เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน |
| Container smoke (compose e2e) | `docker compose up` + `curl` | ✅ ผ่านบน CI ([run #33351842320](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/33351842320), 1m6s) — log ยืนยัน `created note #1` และ `end-to-end OK` · ไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน |

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
- [ ] E2E test — รอ backend จริง
