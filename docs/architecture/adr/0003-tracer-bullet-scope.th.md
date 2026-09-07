# ADR-003: จำกัดขอบเขตของ slice แรกที่รันได้ ให้เหลือ service เดียวและเก็บไฟล์บนดิสก์

[🌐 English](./0003-tracer-bullet-scope.md) · **ภาษาไทย**

**สถานะ:** Accepted

**บริบท:**
[ADR-001](./0001-tech-stack-selection.th.md) กำหนดให้ NoteShare เป็น microservices — API Gateway, User & Auth Service, Notes Service, Stats Service — ใช้ PostgreSQL และ object storage แบบ S3 แต่จนถึงตอนนี้รีโปยังไม่มีแอปที่รันได้จริงเลย user story ระดับ Must ของ Sprint 1 ถูกปิดด้วย prototype ที่ข้อมูล hardcoded ทั้งหมด ตามที่ `prototypes/sprint1/README.md` เขียนไว้เอง ขณะที่ Definition of Done ของทีมระบุว่า sprint จะ done ต่อเมื่อ demo ได้จริงแบบ end-to-end ซึ่งตอนนี้ยังทำไม่ได้

เราจึงต้องการ slice แรกที่วิ่งทะลุทุกชั้นจริง (tracer bullet) การสร้างสถาปัตยกรรมเป้าหมายให้ครบก่อนแล้วค่อยรัน จะทำให้ทีม 3 คนหมดเวลาที่เหลือไปกับงาน infrastructure แทนที่จะได้ user story ที่ใช้ให้คะแนน

**การตัดสินใจ:**
สำหรับ slice แรก (US-08, issue #8) เราจะสร้าง **น้อยกว่า** สถาปัตยกรรมเป้าหมายอย่างตั้งใจ:

*   **service เดียว ไม่ใช่สี่** — `notes-service` ดูแล metadata และไฟล์ของโน้ต ยังไม่สร้าง API Gateway และ User & Auth Service และเปิด `notes-service` ตรง ๆ โดยทุก endpoint ยังไม่มี auth
*   **เก็บไฟล์บนดิสก์ผ่าน interface ไม่ใช่ object storage** — เขียนไฟล์ลงโฟลเดอร์ที่ mount เป็น Docker volume การเข้าถึงทั้งหมดผ่าน interface `save`/`open`/`delete` ใน `storage.py` การเปลี่ยนไปใช้ MinIO/S3 จึงแตะไฟล์เดียว
*   **ใช้ PostgreSQL ตั้งแต่ต้น** — เป็นข้อเดียวที่เราไม่เลื่อน เพราะการเปลี่ยนฐานข้อมูลตอนปลายโปรเจกต์เจ็บกว่าการเปลี่ยน storage มาก และ `docker compose` ทำให้ต้นทุนตอนนี้ต่ำ
*   **ยังไม่ใช้ migration tool** — สร้าง schema ด้วย `SQLAlchemy.create_all()` ไปก่อน จะเพิ่ม Alembic เมื่อ schema นิ่งและมีข้อมูลที่ต้องรักษา

ADR-001 และ ADR-002 ยังเป็นเป้าหมายเหมือนเดิม ADR นี้บันทึก "ลำดับการเดิน" ไม่ใช่การเปลี่ยนปลายทาง

**ผลที่ตามมา:**
*   **ด้านบวก:**
    *   โปรเจกต์มีเส้นทาง end-to-end ที่ demo ได้จริง — อัปโหลดพร้อม metadata, กรอง, ดาวน์โหลด — ทำให้ผ่าน Definition of Done ระดับ Sprint เป็นครั้งแรก
    *   CI ได้ทดสอบโค้ดแอปจริงแบบ end-to-end (`docker compose up` + วนอัปโหลด → กรอง → ดาวน์โหลด) ไม่ใช่ทดสอบแค่ prototype
    *   interface ของ storage และการแยก container ทำให้เดินต่อไปหา ADR-001 ได้โดยไม่ต้องเขียน business logic ใหม่
*   **ด้านลบ:**
    *   ระบบที่รันจริงยังไม่ตรงกับ C4 Container diagram — `docs/architecture/c4-container.md` อธิบายเป้าหมาย ไม่ใช่สิ่งที่ `docker compose up` ยกขึ้นมา คนอ่านที่ไม่ได้อ่าน ADR นี้อาจเข้าใจผิด
    *   การเก็บไฟล์บนดิสก์ไม่ทนต่อการ redeploy บน host จริง และ scale เกินหนึ่ง instance ไม่ได้ ยอมรับได้เพราะยังไม่ได้ deploy ขึ้น production
    *   ทุก endpoint เปิดหมด — ห้ามเปิด `notes-service` ออกสู่สาธารณะก่อน #5/#6 (auth) จะเสร็จ เพราะชื่อผู้อัปโหลดรับมาจากฟอร์มตรง ๆ ปลอมได้ทันที
    *   เมื่อไม่มี migration การแก้ schema ระหว่างเฟสนี้ต้องลบ volume ทิ้ง (`docker compose down -v`)
