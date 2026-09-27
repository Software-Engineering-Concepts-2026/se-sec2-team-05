# Safety Net ของทีม The Builders

Lab 12B (W12) — Safety Net Sprint · PR #66

## 1. ฟังก์ชันที่เลือกทดสอบ

- **ฟังก์ชัน:** `email_error(email, allowed_domains)` — อยู่ไฟล์ `services/auth-service/credentials.py`
- **เหตุผลที่เลือก:** ตัดสินว่าใครสมัครสมาชิกได้ (AC ข้อแรกของ US-05 #5 — อีเมลมหาวิทยาลัยเท่านั้น) เป็น pure function ไม่พึ่ง DB/Flask/เวลา
  มีเงื่อนไข 4 จุด และก่อน Lab นี้ถูกทดสอบผ่าน `validate_registration()` เท่านั้น ซึ่ง normalize อีเมลให้ก่อนเสมอ
  จึงยังไม่มีเทสต์ที่ตรึงสัญญาของตัวฟังก์ชันเอง และไม่มีเทสต์ที่ขอบ 254 ตัวพอดี

## 2. เทสต์ที่เขียน (9 ตัว)

ไฟล์ `src/tests/test_email_error.py` · รายละเอียด input/ผลที่คาดหวังอยู่ใน `docs/testing/readme.md` หัวข้อ 2.11

| # | ชื่อเทสต์ | ประเภท | ยืนยันอะไร |
|---|---|---|---|
| AE-01 | `test_university_email_is_accepted` | happy | `67026168@up.ac.th` → `None` |
| AE-02 | `test_second_allowed_domain_is_accepted` | happy | ตั้ง 2 โดเมน โดเมนที่สองก็ผ่าน |
| AE-03 | `test_email_at_exact_max_length_is_accepted` | edge | ยาว 254 ตัวพอดี → ผ่าน |
| AE-04 | `test_email_one_over_max_length_is_rejected` | edge | ยาว 255 ตัว → `"ยาวเกิน 254 ตัวอักษร"` |
| AE-05 | `test_uppercase_domain_is_rejected_because_caller_must_normalize` | edge | ฟังก์ชันไม่ normalize เอง — `A@UP.AC.TH` ไม่ผ่าน |
| AE-06 | `test_empty_email_is_required` | error | `""` → `"จำเป็นต้องกรอก"` |
| AE-07 | `test_tab_inside_email_is_malformed` | error | มี tab → `"รูปแบบอีเมลไม่ถูกต้อง"` |
| AE-08 | `test_rejection_message_lists_every_allowed_domain` | error | ข้อความ error บอกครบทุกโดเมนที่อนุญาต |
| AE-09 | `test_email_without_domain_is_malformed` | error (xfail) | `a@` ควรได้ error รูปแบบ — โค้ดตอนนี้คืน error โดเมน ดูหัวข้อ 3 |

## 3. Coverage (ผลรันจริงจากเครื่อง, 2026-09-27)

```text
# pytest src/tests --cov=services/auth-service --cov-branch --cov-report=term-missing  (ทั้งชุด)
Name                                   Stmts   Miss Branch BrPart  Cover   Missing
services\auth-service\credentials.py      58      0     24      0   100%
189 passed, 1 xfailed

# pytest src/tests/test_email_error.py --cov=services/auth-service --cov-branch --cov-report=term-missing  (เฉพาะไฟล์นี้)
Name                                   Stmts   Miss Branch BrPart  Cover   Missing
services\auth-service\credentials.py      58     30     24      0   44%   40-42, 65-71, 79-104, 114
8 passed, 1 xfailed
```

- **ตีความ:** เทสต์ชุดนี้ครอบคลุม `email_error()` (บรรทัด 45–60) ครบทุกบรรทัดและทุกกิ่ง บรรทัดที่ขาดในผลแบบแยกไฟล์เป็นฟังก์ชันอื่นในไฟล์เดียวกัน
  (`normalize_email`, `password_error`, `validate_registration`, `verify_password`) ซึ่ง `test_auth_credentials.py` ครอบไว้แล้ว
  `credentials.py` เป็น 100% มาตั้งแต่ก่อน Lab นี้ ตัวเลขจึงไม่ขึ้น คุณค่าอยู่ที่ขอบความยาวทั้งสองฝั่งกับสัญญาที่ถูกตรึงไว้ ไม่ใช่ตัวเลข coverage
- **ส่วนที่ยังไม่ถูกต้อง + เหตุผลที่ยอมรับความเสี่ยง:** AE-09 เจอบั๊กจริง — `a@` หลุดไปตกเงื่อนไขโดเมนเพราะโค้ดเช็ค local ว่างแต่ไม่เช็ค domain ว่าง
  ผลคือแค่ข้อความ error ผิดประเภท อีเมลนี้ยังถูกปฏิเสธอยู่ ไม่มีใครสมัครผ่านได้ จึงยังไม่แก้ในรอบนี้
  ตั้ง `xfail(strict=True)` ไว้ วันที่แก้ `credentials.py` แล้วเทสต์ผ่าน CI จะแดงเตือนให้เอา xfail ออก

## 4. CI block อะไรบ้าง

`.github/workflows/ci.yml` รันทุก PR และทุก push เข้า `main` (run ล่าสุดบน PR #66: ผ่านครบ 4 job)

- `lint` (ruff 0.16.0 ตามกฎใน `ruff.toml`: `E4, E7, E9, F`): import ที่ไม่ได้ใช้, ชื่อที่ไม่ได้ประกาศ, syntax error = แดง
- `Unit tests (Stats Service)` (pytest): เทสต์ Python ทั้งหมด 190 ตัว + coverage
- `Unit tests (JS prototypes)` (`node --test`) และ `Build & smoke-test stack` (docker compose + curl end-to-end) — มีอยู่ก่อน Lab นี้
- **Branch Protection:** `main` มี protection อยู่แล้วและบังคับ review (PR #66 ขึ้น `REVIEW_REQUIRED`) แต่ยัง**ไม่ได้บังคับ status check**
  ทีมมีสิทธิ์แค่ Maintain ตั้งเองไม่ได้ ขอให้ org owner เพิ่ม `lint` + `Unit tests (Stats Service)` เป็น required checks แล้ว — รอผล
- **หลักฐาน:** ภาพหน้า PR ตอนขึ้น "Merging is blocked" — _รอหลังตั้ง required checks แล้วแกล้งทำเทสต์พัง_

## 5. บทเรียนที่ได้

> **TODO (ทีมเขียนเอง 2–3 บรรทัด):** เช่น เทสต์ช่วยเจอบั๊กอะไร / boundary ตรงไหนที่เกือบพลาด / CI จับอะไรได้บ้าง
