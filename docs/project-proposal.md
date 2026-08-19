# Project Proposal — NoteShare

**NoteShare** เว็บแอปสำหรับนักศึกษามหาวิทยาลัยในการอัปโหลด ค้นหา และแชร์โน้ตเลกเชอร์ระหว่างกัน

## Theme

ทีมเลือกธีม **Tools for Modern Learners** เพราะเป็นปัญหาที่พวกเราเจอเองทุกเทอมในฐานะนักศึกษา ไม่ต้องไปสัมภาษณ์หา pain point ที่ไม่คุ้นเคย และหา user จริงมาทดสอบได้ทันทีจากเพื่อนในคณะ

อีกสองธีมถูกตัดออกด้วยเหตุผลเรื่องขอบเขต — Community Connector ต้องพึ่งข้อมูล/ผู้ใช้จากภายนอกมหาวิทยาลัยซึ่งทีมควบคุมไม่ได้ ส่วน Quantified Self Dashboard ต้องมีข้อมูลที่เก็บต่อเนื่องเป็นเวลานานหรืออุปกรณ์เซนเซอร์ ซึ่งไม่พอดีกับเวลาหนึ่งเทอม

## Problem Statement

ทุกวันนี้โน้ตเลกเชอร์ถูกส่งต่อกันผ่านกลุ่มแชท (LINE, Google Drive ที่แชร์ลิงก์ทิ้งไว้) ซึ่งมีปัญหาสองด้าน:

- **ฝั่งคนหา** — พอแชทเก่าเลื่อนผ่านไปหลายวัน แทบเป็นไปไม่ได้ที่จะค้นย้อนกลับไปหาไฟล์ที่ต้องการ ต้องไล่ถามเพื่อนซ้ำๆ
- **ฝั่งคนเขียน** — คนที่จดโน้ตดีและถูกขอไฟล์บ่อยๆ ไม่ได้รับเครดิตหรือการยอมรับใดๆ กลับมา นอกจากต้องคอยส่งไฟล์เดิมซ้ำไปเรื่อยๆ

NoteShare แก้ปัญหานี้ด้วยการทำให้โน้ตค้นหาได้จริง (searchable) และให้เครดิตกับผู้ที่อัปโหลดติดไปกับไฟล์เสมอ

## Target Users

ระบบมีสอง persona หลัก (รายละเอียดเต็มอยู่ที่ [`docs/requirements/personas/`](./requirements/personas/)):

- **James (Note Seeker)** — นักศึกษาปี 1 คณะบริหารธุรกิจ ทำงานพาร์ทไทม์ควบคู่กับเรียน บางครั้งขาดเรียนและต้องตามเนื้อหาให้ทันอย่างเร็วที่สุด
- **Pim (Note Contributor)** — นักศึกษาปี 3 คณะวิศวกรรมคอมพิวเตอร์ ขึ้นชื่อเรื่องจดโน้ตดีในกลุ่มเพื่อน อยากได้รับการยอมรับ (recognition) จากสิ่งที่ทำ และเบื่อที่ต้องส่งไฟล์เดิมซ้ำๆ ให้คนที่มาขอทีหลัง

## Objectives / Success Criteria

เป้าหมายของเทอมนี้คือทำ prototype ที่ใช้งานได้จริงตาม flow หลัก ไม่ใช่แค่ mockup:

- สมัครสมาชิก/login ได้จริง
- อัปโหลดโน้ตพร้อม metadata ได้จริง
- ค้นหา/filter/preview/download โน้ตได้จริง
- ผู้อัปโหลดเห็นเครดิตและสถิติของโน้ตตัวเองได้จริง

ข้อสุดท้ายไม่ใช่ nice-to-have — NoteShare เป็น two-sided marketplace (คนหากับคนให้) ถ้าฝั่งผู้ให้ไม่เห็นผลตอบแทนอะไรเลย ก็ไม่มีเหตุผลให้อัปโหลดต่อ ระบบเครดิตจึงต้องอยู่ใน prototype ตั้งแต่ต้น ไม่ใช่ฟีเจอร์ที่ค่อยเพิ่มทีหลัง

## Scope (MoSCoW)

รายการนี้ต้องตรงกับ backlog จริงบน GitHub Issues และ [`docs/requirements/user-stories.md`](./requirements/user-stories.md)

**Must have**
- Register with university email
- Login / logout
- Upload note file (PDF/image)
- Note metadata (subject/code, faculty, year, lesson/topic, date)
- Search by keyword
- Download file
- Edit own note
- Delete own note
- Auto-attach contributor name to uploaded notes (for credit)

**Should have**
- Filter by faculty / year / file type
- Preview before download
- Filter by lecture date / topic
- View own note stats (views + downloads)
- Report inappropriate content
- Admin review / delete reported note
- Thank / credit note owner after download

**Could have**
- Rate a note
- Comment on a note
- Save note to favorites

**Won't have (this semester)**
- Full-text OCR search inside note images
- Mobile native app
- Payment / monetization

## Constraints

- ระยะเวลาทำงาน: หนึ่งเทอมการศึกษา
- ทีม: 3 คน ("The Builders")
- นี่เป็นครั้งแรกที่ทีมสร้าง backend แบบหลาย service พร้อมกัน (multi-service) — ดูเหตุผลและ trade-off ที่ [ADR-001](./architecture/adr/0001-tech-stack-selection.md)

## Risks & Assumptions

### สมมติฐานที่ต้อง validate

| สมมติฐาน | จะตรวจอย่างไร |
| --- | --- |
| นักศึกษายอมอัปโหลดโน้ตของตัวเองขึ้นระบบกลาง ถ้าได้เครดิตติดไปกับไฟล์ | ถาม Note Contributor จริง 3-5 คนตอน demo Sprint 1 ว่าเงื่อนไขไหนที่ทำให้เขายอมอัปโหลด |
| การค้นด้วย metadata (รหัสวิชา/คณะ/ปี/หัวข้อ) เพียงพอ ไม่ต้องค้นข้อความในรูป | ให้ผู้ใช้ลองหาโน้ตที่เจาะจงจากชุดทดลอง แล้วดูว่าหาเจอโดยไม่ต้องเปิดไฟล์ดูทีละอันหรือไม่ |
| ทีม 3 คนทำ backend หลาย service ให้ทันในหนึ่งเทอมได้ | วัดจาก velocity จริงของ Sprint 1 ถ้าปิด Must ไม่ทัน ให้รวม service เข้าด้วยกัน |

### ความเสี่ยง

| ความเสี่ยง | ผลกระทบ | แผนรับมือ |
| --- | --- | --- |
| **Cold start** — ระบบเป็น two-sided ช่วงแรกไม่มีโน้ตในระบบ คนหาก็ไม่มีเหตุผลเข้ามาใช้ | สูง | ทีมเตรียม seed โน้ตของตัวเองใส่ก่อน demo และดัน Must ฝั่ง upload ให้เสร็จก่อนฝั่ง social |
| **ลิขสิทธิ์/เนื้อหาไม่เหมาะสม** — มีคนอัปสไลด์ของอาจารย์หรือไฟล์ที่ไม่ใช่ของตัวเอง | สูง | มี story report + admin review อยู่ใน Should have และแจ้งเงื่อนไขตอนอัปโหลดว่าต้องเป็นโน้ตที่ผู้ใช้จดเอง |
| **ทีมยังไม่เคยทำ multi-service** — เสี่ยงเสียเวลาไปกับ setup/deploy มากกว่าฟีเจอร์ | กลาง | ตกลง contract ระหว่าง service เป็น REST ไว้ล่วงหน้า ([ADR-002](./architecture/adr/0002-use-restful-api-internal-communication.md)) และมี CI ตั้งแต่ Sprint 1 |
| **สมาชิกไม่ว่างตรงกัน** — ทั้งสามคนเรียนต่างเวลาและมีงานวิชาอื่น | กลาง | ทำงานแบบ async ผ่าน issue + PR ไม่รอประชุมพร้อมกัน (บังคับด้วย DoD ที่ห้าม push ตรง `main`) |

## Definition of Done

DoD ของทีมแยกไว้ที่ [`docs/definition-of-done.md`](./definition-of-done.md) — มีสองระดับคือระดับ User Story/PR และระดับ Sprint
