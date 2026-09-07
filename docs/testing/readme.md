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

### 2.5 Container smoke test (CI เท่านั้น)

| # | Test case | ขั้นตอน | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| DK-01 | ทั้ง stack build และสตาร์ตได้ | `docker compose up -d --build` | exit code 0 |
| DK-02 | ทุก service ตอบ health | `curl :5000/health`, `:5001/health` (retry 20 ครั้ง ห่างละ 3 วิ) | `200` ทั้งคู่ |
| DK-03 | end-to-end ของ US-08 | อัปโหลดพร้อม metadata → กรองด้วย `faculty`+`year_level`+`q` → ดาวน์โหลด | `count = 1` และไฟล์ที่ดาวน์โหลดตรงกับต้นฉบับ (`cmp`) |
| DK-04 | validation ทำงานจริงบน stack ที่รัน | `POST /notes` ส่งแค่ `title` | `400` |

## 3. Test Report

**รันล่าสุด:** 2026-08-31 (เครื่อง local, Windows 11)

| ชุด | คำสั่ง | ผล |
| --- | --- | --- |
| JS unit | `cd prototypes/sprint1 && node --test` | ✅ 7 passed / 0 failed (119 ms) |
| Python unit + integration | `pytest src/tests -v` | ✅ 35 passed / 0 failed (0.45 s) — stats 4, notes validation 17, notes API 14 |
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
