# Final Reflection — วชิรวิทย์ ศรีทอง (67021219)

สมาชิกทีม The Builders · GitHub `@Washi-cloud` · โปรเจกต์ NoteShare · เว็บจริง https://noteshare-sooty.vercel.app

คำถาม 8 ข้อจากบทที่ 14 §14.6.3 (Grand Finale Session) · ลิงก์ PR และ commit ทั้งหมดชี้ไปที่ repo
[`Software-Engineering-Concepts-2026/se-sec2-team-05`](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05)

## 1. What did you build?

> "What did you build?"

NoteShare เป็นเว็บให้นักศึกษาแบ่งปันโน้ตเลกเชอร์ (ภาพรวมของทั้งระบบอยู่ใน [README](../README.md) และ [USER_GUIDE.md](../USER_GUIDE.md))
ส่วนที่ผมรับผิดชอบคือ **ฝั่ง "หาและเก็บโน้ต" ของ Notes Service** รวม 6 user story ผ่าน 6 PR ที่ merge เข้า `main` แล้ว:

| User story | สิ่งที่ผมทำ | PR | วันที่ merge |
| --- | --- | --- | --- |
| US-10 (#10) | กรองโน้ตตามชนิดไฟล์ (`file_type`) ใน `GET /notes` | [#60](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/60) | 2026-09-08 |
| US-12 (#12) | นับจำนวนดาวน์โหลด (`download_count`) ตอน `GET /notes/<id>/download` | [#62](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/62) | 2026-09-27 |
| US-11 (#11) | `GET /notes/<id>/preview` ดูตัวอย่างรูป/หน้าแรกของ PDF ก่อนดาวน์โหลด | [#67](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/67) | 2026-09-29 |
| US-26 (#26) | กรองตามหัวข้อเลกเชอร์ (`topic`) และช่วงวันที่ (`date_from`/`date_to`) | [#70](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/70) | 2026-09-30 |
| US-15 (#15) | รายการโปรด: model, endpoint และ `is_favorited` ใน `GET /notes` | [#71](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/71) | 2026-10-01 |
| US-28 (#28) | ตาราง `thanks`, `POST /notes/<id>/thanks` และ `thank_status` | [#76](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/76) | 2026-10-04 |

หลักฐานเชิงปริมาณจาก git ของ `origin/main`:

- commit ของผมที่ไม่ใช่ merge 38 รายการ · เป็น Conventional Commits 33 รายการ (87%) ส่วนอีก 5 รายการที่ไม่เป็นรูปแบบนี้ทั้งหมดเป็นงานเอกสารและ mockup ช่วงสิงหาคม–กันยายน
  (เช่น `อัปเดตไฟล์ AI_USAGE`, `Edit TODO`) ซึ่งเป็นจุดที่ผมไม่ทำตาม [Pragmatic Promise](../team/Wachirawit.md) ของตัวเองเต็มที่
- เทสต์ที่ผมเขียนในไฟล์ของตัวเอง: `test_notes_preview.py` 27 ฟังก์ชัน, `test_notes_favorites.py` 32 ฟังก์ชัน, `test_notes_thanks.py` 20 ฟังก์ชัน
  และเคสกรองใน `test_notes_api.py` เทสต์ทั้งหมดอยู่ใน [test plan](./testing/readme.md) ตามรหัส: NP-01 ถึง NP-27 (preview), NA-15 ถึง NA-18 (download count),
  NA-27 ถึง NA-36 (กรอง), NA-37 ถึง NA-52 (รายการโปรด), NA-97 ถึง NA-109 (ขอบคุณ)
- ช่วงต้นเทอมสร้าง prototype หน้าค้นหาโน้ต (`prototypes/sprint1/wachirawit_search_note_prototype.html`) และ wireframe ใน PR #37
  (ต่อมาอติชาติ refactor ใน Lab 7 โดยแยก `esc()`/`stars()` ออกไปเป็นไฟล์ที่ทดสอบได้)
- รีวิวและ approve PR ของเพื่อน: [#120](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/120) (2026-10-10),
  [#124](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/124) (2026-10-12) และ
  [#126](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/126) (2026-10-13)

งานที่ **ไม่ใช่ของผม** และผมไม่ขอนับเป็นผลงาน: การ deploy บน Vercel, Auth Service, หน้าเว็บตัวจริงใน `web/` (รวมการ redesign Issue #84), Alembic และ gateway
ซึ่งเป็นงานของอติชาติ ส่วนผมเป็นคนทำ API ที่หน้าเหล่านั้นเรียกใช้

## 2. What problem did you solve?

> "What problem did you solve?"

จาก [Project Proposal](./project-proposal.md) โน้ตเลกเชอร์ทุกวันนี้กระจายอยู่ในแชทกับลิงก์ Drive คนหา (persona James) เสียเวลาไล่ถามและเปิดไฟล์ทีละอัน
ส่วนคนเขียน (persona Pim) ไม่เห็นว่าโน้ตของตัวเองมีคนใช้หรือไม่ ผมแก้เป็น 3 ปัญหาย่อย:

- **หาไม่เจอ:** กรองด้วยชนิดไฟล์ หัวข้อ และช่วงวันที่ใช้ร่วมกันได้ (US-10 + US-26, เทสต์ NA-36 ยิงทุกตัวกรองพร้อมกัน) และ `date_from` ที่เลยหลัง `date_to` ตอบ `400`
  แทนที่จะคืนรายการว่างเงียบ ๆ ([6beb8eb](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/6beb8eb))
- **ไม่รู้ว่าไฟล์ใช่หรือเปล่าก่อนโหลด:** preview เห็นหน้าแรกของ PDF หรือรูปที่ย่อเหลือกว้างไม่เกิน 800 px (US-11) ผู้ใช้ไม่ต้องโหลดไฟล์เต็มเพื่อเดาเนื้อหา
- **คนเขียนไม่เห็นผลตอบแทน:** `download_count` (US-12) และคำขอบคุณ (US-28) ทำให้คนแชร์เห็นว่ามีคนใช้โน้ตของตน
  ส่วนรายการโปรด (US-15) ให้คนหาเก็บโน้ตที่จะกลับมาอ่านไว้ในที่เดียว ไม่ต้องหาใหม่ทุกรอบ

## 3. What technical decision are you proudest of?

> "What technical decision are you proudest of?"

ที่ภูมิใจที่สุดคือ **ทำให้ฐานข้อมูล SQLite ที่ใช้ในเทสต์ "บังคับ foreign key" เหมือน PostgreSQL ที่ใช้จริง และลบแถวลูกก่อนลบแถวแม่** ([7856df4](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/7856df4), PR #71)

**ปัญหา:** ตาราง `favorites` มี FK ไป `notes` และ Postgres ไม่มี `ON DELETE CASCADE` การลบโน้ต (US-20) ที่มีคนกดโปรดไว้จึงจะ `500` บน Postgres
แต่เทสต์ทั้งหมดรันบน SQLite ซึ่ง **ไม่บังคับ FK ถ้าไม่เปิดเอง** จึงเขียวหมดและไม่มีทางจับได้

**ทางที่เลือก:**

- `delete_note` ลบแถว `favorites` ของโน้ตนั้นก่อนในทรานแซกชันเดียวกัน แล้วค่อยลบโน้ต
- เปิด `PRAGMA foreign_keys=ON` ผ่าน SQLAlchemy `event "connect"` เมื่อ dialect เป็น SQLite ให้ฐานข้อมูลเทสต์มีพฤติกรรมตรงกับ production
- เพิ่มเทสต์ลบโน้ตที่ถูกกดโปรดแล้วใน `test_notes_favorites.py` (12 บรรทัดใน commit เดียวกัน) เพื่อล็อกพฤติกรรมนี้ไว้

ผลที่ตามมาที่ทำให้ภูมิใจ: ตอนทำ US-28 ผมใช้รูปแบบเดียวกันกับตาราง `thanks` และจับได้ใน PR เดียวกันก่อน merge
([00fcb75](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/00fcb75) ลบ `Thank` ก่อนลบโน้ต) ไม่ต้องรอให้พังบน production อีกรอบ
และต่อมาทีมเพิ่ม job เทสต์บน PostgreSQL ([PR #103](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/103)) ซึ่งยืนยันว่าความเสี่ยงที่ผมกันไว้เป็นความเสี่ยงจริง

การตัดสินใจเล็กอีกข้อที่คล้ายกัน: นับดาวน์โหลดด้วย `UPDATE … SET download_count = download_count + 1` ใน SQL แทนอ่านแล้วบวกใน Python
เพื่อไม่ให้นับตกหล่นเมื่อมีหลายคนโหลดพร้อมกัน และนับเฉพาะเมื่อเปิดไฟล์สำเร็จ ([bd95cc1](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/bd95cc1))

## 4. What failure taught you the most?

> "What failure taught you the most?"

**เทสต์เขียวหมด แต่ container ของ preview พังตั้งแต่ start** ([8f25b9b](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/8f25b9b))

ตอนทำ US-11 ผมเขียนเทสต์ 25 เคสผ่านหมดในเครื่อง แต่ `Dockerfile` ของ notes-service ลิสต์ไฟล์ที่ copy ทีละไฟล์และผมลืมเพิ่ม `preview.py`
container จึงขึ้น `ModuleNotFoundError: No module named 'preview'` เทสต์ระดับ unit จับไม่ได้เพราะ import จาก source tree ตรง ๆ ไม่ได้รันผ่าน image
ผมเจอก็ต่อเมื่อรัน `docker compose` จริง (ดูแถวของผมใน [AI_USAGE.md](../AI_USAGE.md))

ความผิดพลาดชุดเดียวกันซ้ำอีก 3 จุดใน PR #62 และ #67 ซึ่งอติชาติเจอตอนรีวิว (ผมไม่ได้จับเอง):

- **#62:** `download_count` เพิ่มขึ้นแม้ดาวน์โหลดตอบ `500` เพราะนับก่อนเปิดไฟล์ → แก้ให้นับหลังเปิดไฟล์สำเร็จ ไฟล์หายตอบ `404 file_not_found` และไม่นับ (เทสต์ NA-18)
- **#67:** รูปจากมือถือที่มี EXIF orientation แสดงกลับด้าน และ PDF ขนาด A4 ได้ preview กว้าง 801 px เกินที่เขียนไว้ว่า "ไม่เกิน 800" เพราะ pdfium ปัดขึ้นหนึ่งพิกเซล
  ([b3236ef](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/b3236ef), เทสต์ NP-26/NP-27)
- **หลัง merge `main`:** เทสต์ preview ทั้งไฟล์พังเป็น `401` เพราะเขียนไว้ก่อนที่ `POST /notes` จะบังคับ login ([c6595d7](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/commit/c6595d7))

อีกข้อที่ผมไม่ภูมิใจ: เอกสาร preview (หัวข้อ 2.12 ของ test plan, README ของ service, แถวใน `AI_USAGE.md`) ผมทำ **ย้อนหลัง** วันที่ 2026-09-28
หลังโค้ดถูก commit ไปแล้ว และแถวใน `AI_USAGE.md` ของผมถูกทีมติด TODO ว่ายังไม่ละเอียด

บทเรียนที่ใช้ต่อจริง: **"เทสต์ผ่าน" กับ "ของที่ส่งมอบใช้ได้" เป็นคนละเรื่อง** ผมแก้ด้วย 2 อย่างที่อยู่ใน repo แล้ว:

- เพิ่ม step `DK-07` ใน [`ci.yml`](../.github/workflows/ci.yml) ที่อัปโหลด PNG จริงผ่าน container แล้วเรียก `/preview` พร้อมเคส `422` ของไฟล์ปลอม
  ให้บั๊กแบบ Dockerfile ถูกจับโดย CI ไม่ใช่ด้วยความจำของผม
- ใน PR ถัดมา (#71, #76) ผมเขียนเทสต์ทางล้มเหลวไว้ในรอบเดียวกับ happy path (ลบโน้ตที่มีลูกโยง, และ NA-51/NA-108: auth-service ล่มระหว่างค้นหา
  ค้นหายังใช้ได้และสถานะเป็น `null`) แต่ **ยังไม่เป็นนิสัยสม่ำเสมอ** ข้อ 1–2 ในหัวข้อถัดไปคือสิ่งที่ผมจะทำให้เป็นกฎ

## 5. What would you do differently?

> "What would you do differently?"

ถ้าเริ่ม Sprint 2 ใหม่ ผมจะทำ 4 อย่างนี้ พร้อมเกณฑ์ว่าทำแล้วหรือยัง:

1. **รันบน container และ Postgres ก่อนเปิด PR ทุกครั้ง** ไม่รอให้ CI หรือรีวิวบอก
   - ที่ผ่านมา SQLite อย่างเดียวทำให้พลาด FK (#71) และ Dockerfile (#67)
   - เกณฑ์: ทุก PR ที่แตะ `services/` มีบรรทัดในรายละเอียด PR ว่ารัน `docker compose up --build` กับ Postgres แล้วเห็นผลอะไร
   - ลงมือ: เพิ่ม checkbox นี้ใน [`pull_request_template.md`](../.github/pull_request_template.md) ของทีม (ผมเสนอผ่าน PR ของผมเองรอบถัดไป)
2. **เขียนเทสต์ทางล้มเหลวพร้อม happy path ในคอมมิตเดียวกัน**
   - ที่ผ่านมาบั๊กของ #62 (นับตอน 500) และ #67 (EXIF, 801 px) ถูกจับตอนรีวิวทั้งที่เป็น edge case ที่คิดได้เอง
   - เกณฑ์: ทุก endpoint ใหม่มีเทสต์อย่างน้อย 1 เคสสำหรับ "ไฟล์/ข้อมูลหาย", "input ผิดรูป" และ "service ปลายทางล่ม" ก่อนขอรีวิว
3. **เขียนเอกสารและแถว `AI_USAGE.md` ในวันเดียวกับโค้ด**
   - กฎส่วนตัว: ห้ามเปิด PR ถ้า test plan กับ `AI_USAGE.md` ยังไม่มีแถวของงานนั้น เหมือนที่ [Definition of Done](./definition-of-done.md) ของทีมระบุ
   - เกณฑ์: ไม่มีข้อความ "ทำย้อนหลัง" ในแถวของผมอีก
4. **ทำตาม Pragmatic Promise ให้ครบทุก commit** เพราะ 5 จาก 38 commit ไม่เป็น Conventional Commits
   - ลงมือ: ตั้ง `commit-msg` hook ในเครื่อง หรือใช้ commitlint เพื่อให้ความผิดพลาดนี้เกิดไม่ได้ ไม่ต้องพึ่งความจำ
   - เกณฑ์: โปรเจกต์ถัดไป commit ที่ผิดรูปแบบเป็น 0

## 6. How did you embody Tip 52 (Delight Users)?

> "How did you embody Tip 52 (Delight Users)?"

Tip 52 คือไม่ใช่แค่ทำตาม requirement แต่ทำให้ผู้ใช้ได้สิ่งที่เขาต้องการจริง ๆ สิ่งที่ผมทำให้ผู้ใช้ (ส่วนที่เป็น API ที่หน้าเว็บเรียกใช้):

- **ดูก่อนโหลด** preview ของ PDF แสดงเฉพาะหน้าแรก ของรูปย่อเหลือ 800 px และแคชไว้ (`Cache-Control: public, max-age=86400`) ผู้ใช้เห็นเร็ว ไม่เปลืองดาต้า
  และแก้ EXIF ให้รูปถ่ายแนวตั้งจากมือถือไม่ขึ้นกลับด้าน (โน้ตที่ถ่ายด้วยมือถือเป็นกรณีที่คาดว่าเกิดบ่อย แต่ยังไม่ได้วัดจากข้อมูลจริง)
- **ไฟล์เสียไม่ทำให้หน้าพัง** ไฟล์ preview ที่เสีย ผิดชนิด หรือใหญ่ผิดปกติ ตอบ `422 preview_unavailable` (ตรวจจากเนื้อไฟล์จริงด้วย Pillow/pypdfium2
  ไม่เชื่อ mimetype ที่ส่งมา) หน้าเว็บจึงแสดงข้อความแทนที่จะเจอ `500`
- **ค้นหาไม่พังเพราะ service อื่น** ถ้า auth-service ล่ม `GET /notes` ยังตอบได้ โดย `is_favorited` และ `thank_status` เป็น `null` (NA-51, NA-108)
  คนที่แค่ค้นหายังใช้งานได้ตามปกติ
- **ตัวกรองบอกความผิดพลาดตรง ๆ** `date_from` เลยหลัง `date_to` ตอบ `400` แทนผลลัพธ์ว่างที่ทำให้ผู้ใช้คิดว่าไม่มีโน้ต
- **ให้เครดิตคนเขียน** `download_count` ที่แม่นยำ (ไม่นับตอนล้มเหลว ไม่ตกหล่นตอนโหลดพร้อมกัน) และ `thank_status` ที่บอกว่าเราขอบคุณโน้ตนี้แล้วหรือยัง

ข้อจำกัดที่ต้องยอมรับ: ผมไม่ได้เก็บ feedback จากผู้ใช้จริงนอกทีม ข้อกล่าวอ้างข้างบนจึงมาจากการวิเคราะห์พฤติกรรมและเทสต์ ไม่ใช่การวัดความพอใจ
ถ้ามีรอบถัดไป ผมจะให้เพื่อนในห้อง 3–5 คนลองหาโน้ตจริงและจับเวลาว่าหาไฟล์ที่ต้องการเจอภายในกี่วินาที

## 7. How did you embody Tip 53 (Sign Your Work)?

> "How did you embody Tip 53 (Sign Your Work)?"

Tip 53 คือภูมิใจและรับผิดชอบกับงานของตนจนกล้าใส่ชื่อ สิ่งที่ผมทำ:

- **ทุกการเปลี่ยนแปลงผูกกับ user story และอ่านย้อนได้** commit เป็น Conventional Commits ที่ระบุ `(US-xx)` เช่น
  `feat(notes): add favorites model and endpoints (US-15)` และแยกเป็น `feat` / `fix` / `test` / `docs` ตามลำดับ ทำให้ PR #71 อ่านเป็นเรื่องเล่าได้
  ว่าเพิ่มอะไร ทดสอบอะไร เอกสารอะไร และแก้บั๊กอะไรตามมา
- **ทุก endpoint ที่ผมทำมีเทสต์ที่มีรหัส** NP-, NA- ผูกกับ story ใน [test plan](./testing/readme.md) และมีหัวข้อ API ใน
  [README ของ notes-service](../services/notes-service/README.md) ทำให้คนอื่นตรวจงานผมได้โดยไม่ต้องถามผม
- **ยอมรับข้อผิดพลาดใน commit และเอกสาร** แก้ตามรีวิวใน commit ที่ชื่อบอกตรง ๆ ว่า `(PR #67 review)` และเขียน "ทำย้อนหลัง" ในแถวของตัวเองตามจริง
  แทนการเขียนให้ดูเหมือนทำตามขั้นตอนตั้งแต่แรก
- **รับผิดชอบงานที่ตรวจต่อ** เมื่อเพื่อนส่ง PR มาให้ ผมอ่านและ approve ตามจริง ([#120](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/120),
  [#124](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/124), [#126](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/126))
  และเพื่อนก็ตรวจงานผมเช่นกัน (อติชาติ request-changes แล้ว approve #67 เมื่อ 2026-09-29)
- **เปิดเผยการใช้ AI ตามจริง** commit ของผมมี `Co-Authored-By: Claude` และใน [AI_USAGE.md](../AI_USAGE.md) ระบุว่า `preview.py` และ `test_notes_preview.py`
  ถูก generate โดย Claude Code โดยไม่มีคนแก้บรรทัดใดก่อน commit และยังไม่ผ่านรีวิวตอนนั้น การใส่ชื่อในงานของผมจึงหมายถึงผมตรวจ รันจริง
  (ผ่าน `docker compose`) และรับผิดชอบผลลัพธ์ ไม่ได้แปลว่าพิมพ์เองทุกตัวอักษร
  - ตอนทำ prototype ผมยังใช้ Gemini ตรวจช่องโหว่ XSS แล้วเพิ่ม `esc()` กับ clamp ค่าใน `stars()` เองก่อน commit `0ea55bd`

## 8. What value did this experience add to your SE journey?

> "What value did this experience add to your SE journey?"

**ที่ได้มา:**

- เคยทำโปรเจกต์กลุ่มที่ปัญหาใหญ่คือรวมโค้ด (ตามที่ผมเขียนไว้ใน [reflection ตอนต้นเทอม](./reflections/wachirawit_1.md) และ [intro](../team/Wachirawit.md))
  รอบนี้ได้เห็นว่าเครื่องมือช่วยจริง ๆ ได้แก่ branch ต่อ story, PR ที่มีรีวิว, CI ที่รันบนทุก PR และ ADR/เอกสารที่ตรงกับโค้ด
- เรียนรู้ว่า "เสร็จ" คือโค้ด + เทสต์ + รันบนของจริง + เอกสาร + บันทึก AI ไม่ใช่แค่ PR เปิดได้
- เรียนรู้การทำงานกับ AI อย่างมีวินัย: ให้ AI ร่างและเสนอ แต่ผมต้องรันของจริงและอ่านผลเอง (จุดที่เจอบั๊ก Dockerfile ได้จาก `docker compose` ไม่ใช่จากเทสต์ที่ AI เขียน)

**แผนต่อจากนี้** (ปรับตามที่ทำได้จริงได้ แต่ทุกข้อตรวจผลได้):

1. **ภายใน 2026-10-31** สร้าง repo template ส่วนตัวที่มี CI, `pull_request_template.md` (มี checkbox รัน container/Postgres), `commit-msg` hook และโฟลเดอร์ `docs/adr/`
   โดยใช้ [`ci.yml`](../.github/workflows/ci.yml) ของ NoteShare เป็นต้นแบบ โปรเจกต์ใหม่ทุกอันเริ่มจาก template นี้
2. **ภายใน 2026-11-15** เขียน README ใน GitHub profile ให้ลิงก์เว็บจริงกับ PR #71 (FK + SQLite/Postgres) และ #67 (preview + บทเรียน Dockerfile) เป็นตัวอย่างผลงาน
   พร้อมสรุปว่าส่วนไหนใช้ AI ช่วยและผมตรวจอย่างไร
3. **ทุก feature ใหม่** ใช้ checklist "ทางล้มเหลว 3 ข้อ" (ข้อมูลหาย, input ผิด, service ล่ม) ก่อนขอรีวิว และนับจำนวนบั๊กที่รีวิวเจอเทียบกับ Sprint 2
   เป้าหมายคือเหลือ 0 บั๊กประเภท edge case ที่ผมคิดได้เองใน PR ถัดไป (Sprint 2 ผมมี 3 จุดจาก 2 PR)
4. **ฝึก Postgres/Alembic เองจริง** ผมใช้ Postgres ผ่าน compose แต่การตั้ง migration ([PR #107](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/107))
   เป็นงานของอติชาติ ผมจะลองเขียน migration ของตารางใหม่เองใน repo ส่วนตัว 1 ตารางแล้วเทียบกับของทีม เพื่อปิดช่องว่างที่ผมรู้ตัวว่ามี
