# 🎯 Project Proposal — NoteShare

**NoteShare** เว็บแอปสำหรับนักศึกษามหาวิทยาลัยในการอัปโหลด ค้นหา และแชร์โน้ตเลกเชอร์ระหว่างกัน
(ธีม: *Tools for Modern Learners*)

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
