# Final Reflection — อติชาติ ผาแสนเถิน (67026168)

หัวหน้าทีม The Builders · GitHub `@Felsau` · โปรเจกต์ NoteShare · เว็บจริง https://noteshare-sooty.vercel.app

คำถาม 8 ข้อจากบทที่ 14 §14.6.3 (Grand Finale Session) · ลิงก์ PR ทั้งหมดชี้ไปที่ repo
[`Software-Engineering-Concepts-2026/se-sec2-team-05`](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05)

## 1. What did you build?

> "What did you build?"

NoteShare เว็บสำหรับนักศึกษาแบ่งปันโน้ตเลกเชอร์ อัปโหลดไฟล์ PDF/PNG/JPG ได้ถึง 10 MB ค้นหาและกรองตามคณะ ชั้นปี
และชนิดไฟล์ ดูตัวอย่างหน้าแรก ดาวน์โหลด ให้คะแนน กดขอบคุณ แสดงความคิดเห็น เก็บรายการโปรด และรายงานโน้ตที่ไม่เหมาะสม
ให้ผู้ดูแลตรวจ วิธีใช้แต่ละหน้าอยู่ใน [USER_GUIDE.md](../USER_GUIDE.md)

ตัวระบบแบ่งเป็น 3 service ภาษา Flask (Notes, User & Auth, Stats) กับหน้าเว็บ static ที่มี gateway คั่นหน้า:

- บนเครื่องใช้ `docker compose` ยก PostgreSQL 16, 3 service และ nginx ขึ้นมาพร้อมกัน
- บน production ใช้ Vercel Services ฐานข้อมูล Neon Postgres และเก็บไฟล์ใน Vercel Blob ([ADR-009](./architecture/adr/0009-deploy-on-vercel-services.th.md))

การตัดสินใจทางสถาปัตยกรรมทั้งหมดบันทึกเป็น ADR 14 ฉบับ ทั้งภาษาไทยและอังกฤษ ใน [`docs/architecture/adr/`](./architecture/adr/)

ตัวเลขของงาน ณ วันที่ 2026-10-13:

- PR ที่ merge แล้ว 79 PR · issue ทั้งหมด 45 ใบ (ณ 2026-10-13)
- เทสต์ Python 532 ข้อผ่านบน SQLite และ 534 ข้อบน PostgreSQL · coverage รวม 97% ตาม [Test Report](./testing/readme.md#3-test-report)
- เทสต์ JavaScript ของหน้าเว็บ 94 ข้อ · E2E ผ่าน browser จริงด้วย Playwright 7 เส้นทาง
- CI บน GitHub Actions มี 7 job · ตั้งแต่ 2026-10-13 `main` บังคับให้ผ่าน 6 job ก่อน merge

ส่วนที่ผมรับผิดชอบเอง:

- Notes Service ตั้งแต่ตัวแรก ([PR #57](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/57))
- User & Auth Service ([PR #64](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/64), [PR #65](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/65))
- หน้าเว็บส่วนใหญ่ และการ deploy บน Vercel
- งานคุณภาพรอบสุดท้าย: Alembic ([PR #107](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/107)), gateway ตรวจ login ([PR #115](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/115)), อัปโหลดตรงเข้า Blob ([PR #117](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/117)) และเลิกใช้ edit token ([PR #119](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/119))
- รีวิวและ merge PR ของเพื่อนในทีมในฐานะหัวหน้าทีม

## 2. What problem did you solve?

> "What problem did you solve?"

ตาม [Project Proposal](./project-proposal.md) โน้ตเลกเชอร์ทุกวันนี้ส่งต่อกันในกลุ่มแชทกับลิงก์ Google Drive ปัญหาจึงมีสองฝั่ง:

- **ฝั่งคนหา** (persona James) แชทเลื่อนผ่านไปไม่กี่วันก็หาไฟล์เดิมไม่เจอ ต้องไล่ถามเพื่อนซ้ำ
- **ฝั่งคนเขียน** (persona Pim) คนที่จดโน้ตดีไม่ได้เครดิตอะไรกลับมา นอกจากต้องส่งไฟล์เดิมซ้ำไปเรื่อย ๆ

NoteShare แก้ทั้งสองฝั่ง:

- **ฝั่งคนหา** ค้นจากชื่อวิชา รหัสวิชา บทเรียน และหัวข้อได้ (US-09) กรองตามคณะ ชั้นปี ชนิดไฟล์ และวันที่ (US-10, US-26) ดูตัวอย่างก่อนดาวน์โหลด (US-11) และเรียงตามคะแนนได้ จึงเห็นโน้ตที่คนอื่นว่าดีก่อน
- **ฝั่งคนเขียน** ชื่อผู้อัปโหลดมาจากบัญชีที่ login อยู่ (US-31) แก้แทนกันไม่ได้ เครดิตจึงติดไปกับไฟล์เสมอ และมีจำนวนดาวน์โหลด คะแนน คำขอบคุณ กับอันดับผู้แบ่งปันในหน้าสถิติให้เห็นผลกลับมา
- สมัครได้เฉพาะอีเมล `@up.ac.th` ระบบจึงเป็นของนักศึกษามหาวิทยาลัยจริง ไม่ใช่ที่ฝากไฟล์สาธารณะ

## 3. What technical decision are you proudest of?

> "What technical decision are you proudest of?"

ที่ภูมิใจที่สุดคือ [ADR-012](./architecture/adr/0012-direct-upload-to-vercel-blob.th.md) ให้ browser อัปโหลดไฟล์**ตรงเข้า Vercel Blob**
([PR #117](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/117))

**ปัญหา:** NFR-003/006 ให้ไฟล์ใหญ่ได้ 10 MB แต่ Vercel Function รับ body ได้ไม่เกิน 4.5 MB ตอน deploy ครั้งแรก
([ADR-009](./architecture/adr/0009-deploy-on-vercel-services.th.md)) จึงต้องลดเพดานเหลือ 4 MB ทุกจุด ซึ่งผิดจาก requirement

**ทางที่เลือก:**

- notes-service ออก client token ที่ใช้ได้กับ pathname เดียว ชนิดไฟล์เดียว และขนาดไม่เกิน 10 MB
- browser ส่งไฟล์ไปที่ Blob เองพร้อมแถบความคืบหน้า แล้วค่อยเรียก `POST /notes` ด้วย pathname
- notes-service อ่านขนาดและชนิดไฟล์จาก Blob เองโดยไม่เชื่อค่าที่ client ส่งมา และรับเฉพาะ pathname ใต้ `uploads/<user id>/` ของผู้เรียก

ที่ภูมิใจคือไม่ได้แก้ด้วยการเพิ่ม dependency แต่เข้าใจรูปแบบ token ของ `@vercel/blob` 2.8.0 แล้วเซ็นเองใน Python
ให้ได้ผลตรงกับแพ็กเกจจริงทีละไบต์ (เทสต์ BU-01) หน้าเว็บจึงยังเป็นไฟล์ static ล้วน และ compose บนเครื่องยังใช้ฟอร์มแบบเดิมได้
มีเทสต์ BU-01 ถึง BU-16 ใน หัวข้อ 2.25 ของ [test plan](./testing/readme.md)
และผลที่ตามมา (ถ้า Vercel เปลี่ยนรูปแบบ token ต้องแก้ตาม) เขียนไว้ใน ADR ตรง ๆ

เรื่องนี้ตรงกับที่ผมเขียนไว้ใน [reflection ตอนต้นเทอม](./reflections/atichat.md) ว่าถ้าติดปัญหาไฟล์ใหญ่จะเสนอทางเลือกให้ทีม
คือจำกัด 10 MB หรือใช้ cloud storage ภายนอก สุดท้ายได้ทั้งสองอย่าง และเลือกทางนี้ได้เพราะมีข้อมูลจริงจากการ deploy แล้ว

## 4. What failure taught you the most?

> "What failure taught you the most?"

**Notes Service ไม่เคยขึ้น `main` ทั้งที่ทุกคนคิดว่า merge แล้ว** PR #56 ถูก merge เข้า `feature/lab8-ci-tests` แทน `main`
งานที่ต่อยอดจากมันจึงค้างอยู่บน branch ซ้อน branch จนต้องเปิด
[PR #57](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/57) มาแก้ฐานใหม่ (บันทึกไว้ใน Prompt 11 ของ [AI_USAGE.md](../AI_USAGE.md))
ตอนนั้น CI ยังกรองให้รันเฉพาะ PR ที่ base เป็น `main` ด้วย PR ที่ซ้อนกันจึงไม่ถูกทดสอบเลย

บทเรียนคือ **"merge แล้ว" ต้องตรวจจากสถานะจริง ไม่ใช่จากความจำ** หลังจากนั้นผมทำเป็นขั้นตอนประจำ:

- ทุกครั้งที่ merge ใช้ merge commit แล้ว pull `main` มาดู
- ตรวจว่า issue ที่ควรปิดถูกปิดจริง เพราะ PR ที่เขียน "ปิด #116" GitHub ไม่ผูกกับ issue ต้องใช้ `Closes #116`
- เอาตัวกรอง branch ออกจาก trigger `pull_request` ของ CI ให้ทุก PR ถูกทดสอบ

ความผิดพลาดแบบเดียวกันเกิดอีกในตอนท้ายเทอมคนละรูปแบบ:

- required status checks ของ `main` ปิดอยู่ตั้งแต่ Lab 12B เพราะทีมมีแค่สิทธิ์ Maintain ทำให้ PR ที่ CI แดงยัง merge ได้ถ้ามีคน approve
- เมื่อ GitHub Actions ของ organization หยุดรันเพราะเรื่อง billing ทีมก็ไม่มีสิทธิ์แก้เอง

ผมแก้ด้วยการเปิด issue ขออาจารย์ใน repo `Discussions` (#12) ระบุสาเหตุ สิ่งที่ขอ และสิ่งที่ห้ามเปิด (`Security scan`) ให้ชัด
จนได้สิทธิ์ Admin แล้วตั้ง 6 check บังคับบน `main` ได้ในวันที่ 2026-10-13

## 5. What would you do differently?

> "What would you do differently?"

ถ้าเริ่มใหม่ จะทำ 4 อย่างนี้ตั้งแต่ Sprint 1:

1. **ล็อก `main` ด้วย required checks ตั้งแต่วันแรก**
   - ขอสิทธิ์ Admin หรือให้ owner ตั้งให้ก่อนเขียนโค้ดบรรทัดแรก
   - เกณฑ์ว่าทำแล้ว: PR ที่ CI แดง merge ไม่ได้
2. **เลือกที่ deploy ก่อนออกแบบ storage**
   - [ADR-001](./architecture/adr/0001-tech-stack-selection.th.md) วางไว้ว่าจะใช้ Render/Railway แต่สุดท้ายใช้ Vercel
   - เพดาน 4.5 MB ของ Vercel เลยโผล่มาหลัง deploy และต้องแก้ 2 รอบ (ADR-009 แล้วค่อย ADR-012)
   - ครั้งหน้าจะ deploy "hello world" บนที่ deploy จริงภายในสัปดาห์แรก แล้วจดข้อจำกัดของแพลตฟอร์ม (ขนาด body, ระบบไฟล์, เวลา cold start) ลง NFR ก่อนเขียน feature
3. **ไม่สร้างของชั่วคราวที่ต้องรื้อ ถ้ารู้อยู่แล้วว่าของจริงมาแน่**
   - edit token ต่อโน้ต ([ADR-004](./architecture/adr/0004-per-note-edit-token.th.md)) ทำเพราะตอนนั้นยังไม่มีระบบ login
   - พอมี Auth Service ต้องรื้อออกใน [PR #119](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/119) ลบไป 887 บรรทัด ([ADR-013](./architecture/adr/0013-retire-per-note-edit-token.th.md))
   - ครั้งหน้าจะเรียงให้ Auth มาก่อน feature ที่ต้องรู้ว่าใครเป็นเจ้าของ
4. **รันเทสต์บนฐานข้อมูลตัวเดียวกับ production ตั้งแต่ต้น**
   - เทสต์รันบน SQLite อย่างเดียวจนถึง 2026-10-08
   - พอเพิ่ม job บน PostgreSQL ถึงรู้ว่าถ้ามีคนเปลี่ยน `ilike` เป็น `like` เทสต์บน SQLite ไม่มีทางจับได้ ([หัวข้อ 4 ของ test plan](./testing/readme.md#4-ci))

## 6. How did you embody Tip 52 (Delight Users)?

> "How did you embody Tip 52 (Delight Users)?"

Tip 52 บอกว่าเป้าหมายไม่ใช่แค่ส่งโค้ดที่ทำตาม requirement แต่ทำให้ผู้ใช้ได้สิ่งที่เขาต้องการจริง ๆ สิ่งที่ผมทำ:

- **ชื่อคนแทนคำว่า "สมาชิก"**
  - ตอนกดใช้เว็บจริงพบว่าความคิดเห็นและอันดับผู้แบ่งปันขึ้นเป็น "สมาชิก" ทุกแถว ซึ่งขัดกับเป้าหมาย "ให้เครดิตคนเขียน" โดยตรง
  - เปิด issue #121 แล้วแก้ใน [PR #122](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/pull/122) ทั้ง migration, API และหน้าเว็บ
  - แก้แถบเมนูบนมือถือที่ล้นจอใน PR เดียวกันด้วย
- **อัปโหลดไฟล์ใหญ่ได้จริงพร้อมแถบความคืบหน้า** (ADR-012) แทนที่จะปล่อยให้ผู้ใช้เจอ error ตอนไฟล์เกิน 4 MB
- **ข้อความเมื่อเกิดปัญหาบอกวิธีแก้**
  - login ผิด 5 ครั้งจะได้ `429` พร้อมบอกว่ารอกี่นาที ([ADR-011](./architecture/adr/0011-rate-limit-login-and-register.th.md))
  - [USER_GUIDE.md](../USER_GUIDE.md) มีตารางข้อความแจ้งเตือนพร้อมวิธีแก้ คัดลอกจากหน้าจอจริง และภาพหน้าจอทุกหน้า
- **ข้อมูลตัวอย่างที่ดูเป็นของจริง** บนเว็บ production มีโน้ตตัวอย่าง 40 ใบพร้อมคะแนนและความคิดเห็น
  ให้คนที่เข้ามาครั้งแรกเห็นว่าเว็บใช้ทำอะไร และทุกใบมีข้อความกำกับว่าเป็นข้อมูลจำลอง

## 7. How did you embody Tip 53 (Sign Your Work)?

> "How did you embody Tip 53 (Sign Your Work)?"

Tip 53 คือการภูมิใจและรับผิดชอบกับงานของตัวเองจนกล้าใส่ชื่อ สิ่งที่ผมทำ:

- **ทุกการตัดสินใจมีเหตุผลเป็นลายลักษณ์อักษร** ADR 14 ฉบับ ทั้งไทยและอังกฤษ
  - ฉบับที่เปลี่ยนใจภายหลังไม่ได้ลบทิ้ง แต่เขียนฉบับใหม่ที่อ้างถึงฉบับเดิม เช่น ADR-013 แทน ADR-004 และ ADR-012 แทนเพดาน 4 MB ของ ADR-009
  - คนที่มาอ่านทีหลังจึงเห็นว่าทำไมระบบเป็นแบบนี้
- **ทุกเทสต์มีรหัส** (NA-, BU-, GW-, NM- ฯลฯ) ผูกกับ user story หรือ ADR ใน [test plan](./testing/readme.md)
  - [Test Report](./testing/readme.md#3-test-report) ระบุว่ารันที่ commit ไหน เครื่องไหน และส่วนไหน "ไม่ได้รัน" ตรง ๆ
  - ทุกครั้งที่เขียนเทสต์สำคัญ จะลองแก้โค้ดให้ผิดโดยตั้งใจ (mutation check) เพื่อยืนยันว่าเทสต์ล้มจริง ไม่ใช่เขียวทุกกรณี
- **ทุก PR ใช้ Conventional Commits ผูกกับ issue และผ่านการรีวิว**
  - ผมไม่ merge PR ของตัวเองถ้าเพื่อนยังไม่ approve
  - ตอนนี้มี required checks คอยกันอีกชั้น
- **เปิดเผยการใช้ AI ตามจริง**
  - ผมใช้ Claude Code ช่วยเขียนโค้ดและเอกสารจำนวนมาก
  - ทุกรอบบันทึกไว้ใน [AI_USAGE.md](../AI_USAGE.md) พร้อม prompt คำต่อคำและตารางส่วนที่รับจาก AI ตรง ๆ
  - การใส่ชื่อในงานจึงหมายถึงผมอ่าน ตรวจ รันเทสต์ และรับผิดชอบทุกบรรทัดที่ merge ไม่ใช่ว่าพิมพ์เองทุกตัวอักษร

## 8. What value did this experience add to your SE journey?

> "What value did this experience add to your SE journey?"

**ที่ได้มา:** ประสบการณ์ครั้งแรกที่ดูแลระบบตั้งแต่ proposal จนขึ้น production ที่คนอื่นเปิดใช้ได้จริง
สิ่งที่เปลี่ยนวิธีคิดของผมมากที่สุดคือ:

- "เสร็จ" ไม่ได้แปลว่าเขียนโค้ดเสร็จ แต่หมายถึงผ่านเทสต์บนฐานข้อมูลจริง ผ่าน CI ผ่านการรีวิว merge แล้ว deploy แล้ว และเอกสารตรงกับของจริง
  (ตรงกับ [Definition of Done](./definition-of-done.md) ของทีม)
- ในฐานะหัวหน้าทีม งานที่กินเวลาจริงคือการจัดลำดับ merge แก้ conflict และตามสิทธิ์ที่ทีมไม่มี มากกว่าการเขียน feature

**แผนต่อจากนี้** เป็นรูปธรรม:

1. ทุกโปรเจกต์ใหม่เริ่มจาก template ที่มี CI + required checks + PR template + โฟลเดอร์ ADR ตั้งแต่ commit แรก
   (ใช้ [`ci.yml`](../.github/workflows/ci.yml) และ [`pull_request_template.md`](../.github/pull_request_template.md) ของ NoteShare เป็นต้นแบบ)
2. deploy ขึ้นที่จริงภายในสัปดาห์แรกของทุกโปรเจกต์ แล้วจดข้อจำกัดของแพลตฟอร์มลง NFR
3. ทำ NoteShare ให้เป็นผลงานใน GitHub profile: ปักหมุด repo เขียนสรุปใน README ส่วนตัว และลิงก์เว็บจริงกับ ADR-012 เป็นตัวอย่างการตัดสินใจทางเทคนิค
4. ใช้ AI ต่อแบบที่ทำมาในเทอมนี้: ให้ AI เสนอทางเลือก แต่คนเลือกและรับผิดชอบเอง บังคับให้มีหลักฐานเทสต์ก่อนรายงานว่าเสร็จ และบันทึกการใช้ไว้ทุกครั้ง
