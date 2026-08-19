# Definition of Done — NoteShare

นิยาม "เสร็จ" ของทีม The Builders มีสองระดับ: ระดับ User Story/PR เดียว และระดับ Sprint ทั้งก้อน อ้างอิงตาม Git Workflow ที่ตกลงกันไว้ใน [README.md](../README.md#3-git-workflow)

## Definition of Done — User Story / PR

User Story หนึ่งเรื่องถือว่า "done" เมื่อ:

- Acceptance criteria ที่เขียนไว้ใน issue ผ่านครบทุกข้อ
- แตก branch จาก `main` ตามรูปแบบ `type/short-description` (เช่น `feature/upload-note`) และ commit message เป็นแบบ Conventional Commits (เช่น `feat: add note upload`)
- โค้ดผ่าน PR เท่านั้น — ไม่มีการ push ตรงเข้า `main`
- มีสมาชิกในทีมอย่างน้อย **1 คน** review และ approve PR ก่อน merge
- Build ไม่พัง (ไม่มี error ที่ทำให้รันแอปไม่ได้)
- ถ้าการเปลี่ยนแปลงกระทบพฤติกรรมของระบบ (เช่น API, schema, flow การใช้งาน) ต้องอัปเดตเอกสารที่เกี่ยวข้องด้วย (เช่น `docs/architecture`, `docs/requirements`)
- Merge แล้วลบ branch ทิ้งตามข้อตกลงในทีม

## Definition of Done — Sprint

Sprint หนึ่งถือว่า "done" เมื่อ:

- User Story ระดับ **Must have** ทั้งหมดใน milestone ของ sprint นั้นถูกปิด (closed) แล้ว
- ระบบ demo ได้จริงแบบ end-to-end อย่างน้อยในเส้นทางหลัก (happy path) ของ sprint นั้น ไม่ใช่แค่ทีละหน้าจอแยกกัน
- จัดประชุม Sprint Review / Retrospective ตามที่ตกลงไว้ใน Project Charter และมีการบันทึกสิ่งที่จะปรับปรุงในรอบถัดไป
