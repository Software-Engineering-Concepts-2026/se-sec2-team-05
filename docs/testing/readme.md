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
| Smoke (container) | image ที่ build ออกมารันได้จริงและตอบ `/health`, `/stats` | `docker build` + `curl` ใน CI | จับปัญหาที่ unit test มองไม่เห็น เช่น gunicorn/CMD พัง |

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

### 2.3 Container smoke test (CI เท่านั้น)

| # | Test case | ขั้นตอน | ผลที่คาดหวัง |
| --- | --- | --- | --- |
| DK-01 | image build ผ่าน | `docker build -t noteshare/stats-service:ci .` | exit code 0 |
| DK-02 | container ตอบ health | `curl /health` (retry สูงสุด 15 ครั้ง ห่างละ 2 วิ) | `200` ภายใน ~30 วินาที |
| DK-03 | container ตอบ stats | `curl /stats` | `200` |

## 3. Test Report

**รันล่าสุด:** 2026-08-31 (เครื่อง local, Windows 11)

| ชุด | คำสั่ง | ผล |
| --- | --- | --- |
| JS unit | `cd prototypes/sprint1 && node --test` | ✅ 7 passed / 0 failed (119 ms) |
| Python unit | `pytest src/tests -v` | ✅ 4 passed / 0 failed (0.16 s) |
| Container smoke | `docker build` + `curl` | ✅ ผ่านบน CI ([run #33350421986](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/33350421986)) — ไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิดบนเครื่องที่ใช้เขียน |

**ผลรันบน CI ครั้งแรก (PR #55):** ทั้ง 3 job ผ่านหมด — `js-tests` 14s, `python-tests` 14s, `docker-build` 17s

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
- [ ] เพิ่ม branch protection ให้ `main` ต้องผ่าน CI ก่อน merge (ตั้งใน GitHub Settings ไม่ใช่ในโค้ด)
- [ ] E2E test — รอ backend จริง
