# User Stories

แหล่งข้อมูลจริงของเอกสารนี้คือ GitHub Issues ของ repo (`Software-Engineering-Concepts-2026/se-sec2-team-05`) issue #5–#20, #26, #28, #31 ทีมนำมาจัดรูปแบบใหม่ให้อยู่ในรูป user story ที่มี Acceptance Criteria และ Priority ชัดเจน เพื่อใช้เป็น input ของ Lab 3 (Requirements) ส่วน issue #25, #27, #29, #30, #32 ถูกปิดไปแล้วเพราะเป็นเรื่องซ้ำกับ story ที่มีอยู่แล้ว (ดู footnote ท้ายไฟล์)

Priority ใช้หลัก MoSCoW ผูกกับ sprint ที่วางแผนไว้จริง: **Must → Sprint 1**, **Should → Sprint 2**, **Could → Sprint 3**

Estimate เป็นขนาดงานคร่าวๆ ที่ทีมประเมินร่วมกัน: **S** = ทำจบได้ในครั้งเดียว, **M** = ต้องแตะทั้ง frontend และ backend, **L** = มีหลายส่วนย่อยหรือเกี่ยวกับการจัดการไฟล์/storage ค่าเดียวกันนี้ติดเป็น label `size:S/M/L` บน issue ด้วย

ช่อง "ที่มา" ของแต่ละ story ชี้กลับไปยัง scenario ใน [main_scenario.md](./main_scenario.md) ที่เป็นต้นทางของ story นั้น

## สรุปรวม (Overview)

| ID | Persona | Priority | Estimate | Theme | Scenario |
| --- | --- | --- | --- | --- | --- |
| US-05 (#5) | Member | Must (Sprint 1) | M | Auth | Scenario 1 |
| US-06 (#6) | Member | Must (Sprint 1) | S | Auth | Scenario 5 |
| US-07 (#7) | Note Contributor | Must (Sprint 1) | L | Upload/Manage Note | Scenario 4 |
| US-08 (#8) | Note Contributor | Must (Sprint 1) | L | Upload/Manage Note | Scenario 4 |
| US-19 (#19) | Note Contributor | Must (Sprint 1) | M | Upload/Manage Note | Scenario 6 |
| US-20 (#20) | Note Contributor | Must (Sprint 1) | M | Upload/Manage Note | Scenario 6 |
| US-31 (#31) | Note Contributor | Must (Sprint 1) | S | Upload/Manage Note | Scenario 4 |
| US-09 (#9) | Note Seeker | Must (Sprint 1) | M | Search | Scenario 1 |
| US-12 (#12) | Note Seeker | Must (Sprint 1) | M | Download/Credit/Stats | Scenario 1 |
| US-10 (#10) | Note Seeker | Should (Sprint 2) | M | Search | Scenario 2 |
| US-11 (#11) | Note Seeker | Should (Sprint 2) | M | Search | Scenario 2 |
| US-26 (#26) | Note Seeker | Should (Sprint 2) | M | Search | Scenario 1 |
| US-16 (#16) | Note Contributor | Should (Sprint 2) | M | Download/Credit/Stats | Scenario 5 |
| US-28 (#28) | Note Seeker | Should (Sprint 2) | S | Download/Credit/Stats | Scenario 5 |
| US-17 (#17) | Member | Should (Sprint 2) | S | Moderation | Scenario 3 |
| US-18 (#18) | Admin | Should (Sprint 2) | M | Moderation | Scenario 3 |
| US-13 (#13) | Member | Could (Sprint 3) | S | Social | Scenario 2 |
| US-14 (#14) | Member | Could (Sprint 3) | S | Social | Scenario 3 |
| US-15 (#15) | Member | Could (Sprint 3) | S | Social | Scenario 2 |

---

## 1. Auth (สมัครสมาชิก / เข้า-ออกจากระบบ)

#### US-05 (issue #5) — สมัครสมาชิกด้วยอีเมลมหาวิทยาลัย
- **Persona:** Member (ผู้เยี่ยมชมที่กำลังสมัครเป็นสมาชิก)
- **Priority:** Must (Sprint 1)
- **Estimate:** M
- **ที่มา:** [Scenario 1 — การตามเนื้อหาให้ทันก่อนสอบกลางภาค](./main_scenario.md)
- **Story:** ในฐานะผู้เยี่ยมชม ฉันต้องการสมัครสมาชิกด้วยอีเมลมหาวิทยาลัย เพื่อเข้าใช้งานระบบในฐานะสมาชิก
- **Acceptance Criteria:**
  - ต้องใช้อีเมลโดเมนมหาวิทยาลัยเท่านั้น
  - ตรวจอีเมลซ้ำก่อนสร้างบัญชี
  - รหัสผ่านเข้ารหัสก่อนบันทึก
  - แจ้งเตือน error ที่เข้าใจง่าย

#### US-06 (issue #6) — เข้าสู่ระบบและออกจากระบบ
- **Persona:** Member
- **Priority:** Must (Sprint 1)
- **Estimate:** S
- **ที่มา:** [Scenario 5 — เห็นคำขอบคุณจากคนที่ไม่เคยรู้จัก](./main_scenario.md)
- **Story:** ในฐานะสมาชิก ฉันต้องการเข้าสู่ระบบและออกจากระบบ เพื่อเข้าถึงข้อมูลส่วนตัวของฉันอย่างปลอดภัย
- **Acceptance Criteria:**
  - login ด้วยอีเมล+รหัสผ่าน
  - logout invalidate session ทันที
  - error message ไม่ระบุว่าผิดช่องไหน (กัน enumeration)
  - คงสถานะ login จนกว่าจะ logout หรือ token หมดอายุ

---

## 2. Upload/Manage Note (อัปโหลดและจัดการโน้ต)

#### US-07 (issue #7) — อัปโหลดไฟล์โน้ต
- **Persona:** Note Contributor
- **Priority:** Must (Sprint 1)
- **Estimate:** L
- **ที่มา:** [Scenario 4 — อัปโหลดโน้ตพร้อมข้อมูลครบ ตัดปัญหาถูกทักซ้ำ](./main_scenario.md)
- **Story:** ในฐานะผู้แบ่งปัน ฉันต้องการอัปโหลดไฟล์โน้ต (PDF/รูปภาพ) เพื่อแบ่งปันสรุปให้เพื่อนในชุมชน
- **Acceptance Criteria:**
  - รับเฉพาะ PDF/JPG/PNG
  - จำกัดขนาดไฟล์ + แจ้งเตือนเมื่อเกิน
  - แสดงสถานะระหว่างอัปโหลด
  - ไฟล์ผูกกับ record ในฐานข้อมูลทันที

#### US-08 (issue #8) — ระบุข้อมูลของโน้ต (metadata)
- **Persona:** Note Contributor
- **Priority:** Must (Sprint 1)
- **Estimate:** L
- **ที่มา:** [Scenario 4 — อัปโหลดโน้ตพร้อมข้อมูลครบ ตัดปัญหาถูกทักซ้ำ](./main_scenario.md)
- **Story:** ในฐานะผู้แบ่งปัน ฉันต้องการระบุข้อมูลของโน้ต (ชื่อวิชา รหัสวิชา คณะ ชั้นปี และบทเรียน) เพื่อให้ระบบค้นหาและกรองโน้ตได้ถูกต้อง
- **Acceptance Criteria:**
  - กรอกชื่อวิชา/รหัส/คณะ/ชั้นปี/บทเรียนครบ
  - ระบุหัวข้อและวันที่คาบเรียนได้ (ใช้ร่วมกับ US-26)
  - validation ฟิลด์บังคับ
  - ข้อมูลใช้เป็นเงื่อนไขค้นหา/กรองได้จริง

#### US-19 (issue #19) — แก้ไขข้อมูลของโน้ต
- **Persona:** Note Contributor
- **Priority:** Must (Sprint 1)
- **Estimate:** M
- **ที่มา:** [Scenario 6 — แก้ไขโน้ตเก่าแทนการอัปโหลดใหม่](./main_scenario.md)
- **Story:** ในฐานะผู้แบ่งปัน ฉันต้องการแก้ไขข้อมูลของโน้ตที่อัปโหลดไปแล้ว เพื่อแก้ไขข้อมูลที่ผิดได้โดยไม่ต้องลบแล้วอัปใหม่
- **Acceptance Criteria:**
  - เจ้าของเท่านั้นแก้ไขได้
  - แก้ metadata ได้
  - บันทึกเวลาแก้ไขล่าสุด

#### US-20 (issue #20) — ลบโน้ตของตนเอง
- **Persona:** Note Contributor
- **Priority:** Must (Sprint 1)
- **Estimate:** M
- **ที่มา:** [Scenario 6 — แก้ไขโน้ตเก่าแทนการอัปโหลดใหม่](./main_scenario.md)
- **Story:** ในฐานะผู้แบ่งปัน ฉันต้องการลบโน้ตของตนเอง เพื่อนำเนื้อหาที่ไม่ต้องการออกจากระบบ
- **Acceptance Criteria:**
  - เจ้าของเท่านั้นลบได้
  - มีกล่องยืนยันก่อนลบ
  - ลบไฟล์จาก storage และ record ในฐานข้อมูล

#### US-31 (issue #31) — แนบชื่อผู้อัปโหลดอัตโนมัติ
- **Persona:** Note Contributor
- **Priority:** Must (Sprint 1)
- **Estimate:** S
- **ที่มา:** [Scenario 4 — อัปโหลดโน้ตพร้อมข้อมูลครบ ตัดปัญหาถูกทักซ้ำ](./main_scenario.md)
- **Story:** ในฐานะผู้แบ่งปันโน้ต ฉันต้องการให้ชื่อของฉันแนบไปกับโน้ตที่อัปโหลดโดยอัตโนมัติ เพื่อที่จะได้รับเครดิตและป้องกันไม่ให้ผลงานถูกอ้างอิงผิดคน
- **Acceptance Criteria:**
  - แนบชื่อผู้อัปโหลดอัตโนมัติ
  - แก้ไขไม่ได้โดยผู้ใช้อื่น
  - แสดงชื่อเจ้าของทุกครั้งที่แสดงผลโน้ต

---

## 3. Search (ค้นหาและกรองโน้ต)

#### US-09 (issue #9) — ค้นหาโน้ตด้วยคำค้น
- **Persona:** Note Seeker
- **Priority:** Must (Sprint 1)
- **Estimate:** M
- **ที่มา:** [Scenario 1 — การตามเนื้อหาให้ทันก่อนสอบกลางภาค](./main_scenario.md)
- **Story:** ในฐานะผู้ค้นหา ฉันต้องการค้นหาโน้ตด้วยคำค้น (ชื่อวิชา/รหัสวิชา) เพื่อหาเอกสารที่ต้องการได้เร็ว
- **Acceptance Criteria:**
  - ค้นด้วยชื่อวิชาหรือรหัสวิชา
  - partial match
  - แจ้งเมื่อไม่พบผล
  - ผลลัพธ์เร็ว

#### US-10 (issue #10) — กรองโน้ตตามคณะ/ชั้นปี/ประเภทไฟล์
- **Persona:** Note Seeker
- **Priority:** Should (Sprint 2)
- **Estimate:** M
- **ที่มา:** [Scenario 2 — กรองหาโน้ตแล็บที่พลาดให้ตรงจุดที่สุด](./main_scenario.md)
- **Story:** ในฐานะผู้ค้นหา ฉันต้องการกรองโน้ตตามคณะ/ชั้นปี/ประเภทไฟล์ เพื่อจำกัดผลลัพธ์ให้ตรงกับที่ฉันเรียน
- **Acceptance Criteria:**
  - กรองตามคณะ/ชั้นปี/ประเภทไฟล์
  - ใช้หลายตัวกรองพร้อมกันได้ ร่วมกับ US-26 ได้

#### US-11 (issue #11) — ดูตัวอย่างโน้ตก่อนดาวน์โหลด
- **Persona:** Note Seeker
- **Priority:** Should (Sprint 2)
- **Estimate:** M
- **ที่มา:** [Scenario 2 — กรองหาโน้ตแล็บที่พลาดให้ตรงจุดที่สุด](./main_scenario.md)
- **Story:** ในฐานะผู้ค้นหา ฉันต้องการดูตัวอย่าง (preview) โน้ตก่อนดาวน์โหลด เพื่อประเมินว่าตรงกับที่ต้องการไหม
- **Acceptance Criteria:**
  - preview โดยไม่ต้องโหลดไฟล์เต็ม
  - แสดงอย่างน้อยหน้าแรก
  - ปิด preview แล้วกลับผลค้นหาโดยไม่เสียตำแหน่ง

#### US-26 (issue #26) — กรองตามวันที่หรือหัวข้อเลกเชอร์
- **Persona:** Note Seeker
- **Priority:** Should (Sprint 2)
- **Estimate:** M
- **ที่มา:** [Scenario 1 — การตามเนื้อหาให้ทันก่อนสอบกลางภาค](./main_scenario.md)
- **Story:** ในฐานะผู้ค้นหาโน้ต ฉันต้องการกรองโน้ตตามวันที่หรือหัวข้อเลกเชอร์ เพื่อที่จะหาคาบเรียนที่ขาดไปได้ตรงจุด
- **Acceptance Criteria:**
  - กรองตามช่วงวันที่
  - กรองตามหัวข้อเลกเชอร์
  - ใช้ร่วมกับ US-10 พร้อมกันได้

---

## 4. Download / Credit / Stats (ดาวน์โหลด เครดิต และสถิติ)

#### US-12 (issue #12) — ดาวน์โหลดไฟล์โน้ต
- **Persona:** Note Seeker
- **Priority:** Must (Sprint 1)
- **Estimate:** M
- **ที่มา:** [Scenario 1 — การตามเนื้อหาให้ทันก่อนสอบกลางภาค](./main_scenario.md)
- **Story:** ในฐานะผู้ค้นหา ฉันต้องการดาวน์โหลดไฟล์โน้ต เพื่อนำไปอ่านทบทวนแบบออฟไลน์
- **Acceptance Criteria:**
  - ดาวน์โหลดไฟล์ได้
  - นับจำนวนดาวน์โหลดเพื่อสถิติ (เชื่อมกับ US-16)
  - แจ้งเตือนเมื่อดาวน์โหลดไม่สำเร็จ

#### US-16 (issue #16) — ดูสถิติยอดดาวน์โหลดของโน้ตตัวเอง
- **Persona:** Note Contributor
- **Priority:** Should (Sprint 2)
- **Estimate:** M
- **ที่มา:** [Scenario 5 — เห็นคำขอบคุณจากคนที่ไม่เคยรู้จัก](./main_scenario.md)
- **Story:** ในฐานะผู้แบ่งปัน ฉันต้องการดูสถิติยอดดาวน์โหลดของโน้ตตัวเอง เพื่อรู้ว่าเนื้อหาของฉันมีประโยชน์แค่ไหน
- **Acceptance Criteria:**
  - ดูจำนวนดาวน์โหลดต่อโน้ต
  - ดูจำนวนการเปิดดู (view) แยกจากดาวน์โหลด
  - สถิติแยกรายโน้ต

#### US-28 (issue #28) — ขอบคุณ/ให้เครดิตเจ้าของโน้ตหลังดาวน์โหลด
- **Persona:** Note Seeker
- **Priority:** Should (Sprint 2)
- **Estimate:** S
- **ที่มา:** [Scenario 5 — เห็นคำขอบคุณจากคนที่ไม่เคยรู้จัก](./main_scenario.md)
- **Story:** ในฐานะผู้ค้นหาโน้ต ฉันต้องการขอบคุณ/ให้เครดิตเจ้าของโน้ตหลังดาวน์โหลด เพื่อที่ผู้แบ่งปันจะรู้สึกว่าความตั้งใจได้รับการยอมรับ
- **Acceptance Criteria:**
  - กดขอบคุณได้หลังดาวน์โหลดสำเร็จ
  - กดได้ครั้งเดียวต่อโน้ตต่อผู้ใช้
  - เจ้าของเห็นจำนวนครั้งที่ถูกขอบคุณ (เชื่อมกับ US-16)

---

## 5. Social (ปฏิสัมพันธ์ทางสังคมระหว่างสมาชิก)

#### US-13 (issue #13) — ให้คะแนน (rating) โน้ต
- **Persona:** Member
- **Priority:** Could (Sprint 3)
- **Estimate:** S
- **ที่มา:** [Scenario 2 — กรองหาโน้ตแล็บที่พลาดให้ตรงจุดที่สุด](./main_scenario.md)
- **Story:** ในฐานะสมาชิก ฉันต้องการให้คะแนน (rating) โน้ตที่อ่านแล้ว เพื่อช่วยให้คนอื่นเลือกโน้ตคุณภาพดีได้
- **Acceptance Criteria:**
  - ให้คะแนนได้เฉพาะโน้ตที่เคยเปิด/ดาวน์โหลด
  - ให้คะแนนซ้ำได้แค่แก้ไข ไม่สร้างใหม่
  - แสดงคะแนนเฉลี่ย

#### US-14 (issue #14) — แสดงความคิดเห็นใต้โน้ต
- **Persona:** Member
- **Priority:** Could (Sprint 3)
- **Estimate:** S
- **ที่มา:** [Scenario 3 — รายงานโน้ตที่ติดป้ายผิดวิชา](./main_scenario.md)
- **Story:** ในฐานะสมาชิก ฉันต้องการแสดงความคิดเห็นใต้โน้ต เพื่อสอบถามหรือเสริมข้อมูลกับเจ้าของโน้ต
- **Acceptance Criteria:**
  - comment ได้เมื่อ login แล้ว
  - เรียงตามเวลาล่าสุด
  - ลบ comment ของตัวเองได้

#### US-15 (issue #15) — บันทึกโน้ตไว้ใน "รายการโปรด"
- **Persona:** Member
- **Priority:** Could (Sprint 3)
- **Estimate:** S
- **ที่มา:** [Scenario 2 — กรองหาโน้ตแล็บที่พลาดให้ตรงจุดที่สุด](./main_scenario.md)
- **Story:** ในฐานะสมาชิก ฉันต้องการกดบันทึกโน้ตที่ชอบไว้ใน "รายการโปรด" เพื่อกลับมาเปิดอ่านได้ภายหลัง
- **Acceptance Criteria:**
  - บันทึกเข้ารายการโปรดได้
  - ดูรายการโปรดแยกจากผลค้นหา
  - เอาออกจากรายการโปรดได้

---

## 6. Moderation (การกำกับดูแลเนื้อหา)

#### US-17 (issue #17) — รายงานเนื้อหาที่ไม่เหมาะสม/ละเมิดลิขสิทธิ์
- **Persona:** Member
- **Priority:** Should (Sprint 2)
- **Estimate:** S
- **ที่มา:** [Scenario 3 — รายงานโน้ตที่ติดป้ายผิดวิชา](./main_scenario.md)
- **Story:** ในฐานะสมาชิก ฉันต้องการรายงานเนื้อหาที่ไม่เหมาะสม/ละเมิดลิขสิทธิ์ เพื่อช่วยรักษาคุณภาพของชุมชน
- **Acceptance Criteria:**
  - รายงานพร้อมเหตุผล
  - รายงานซ้ำจากคนเดิมไม่นับซ้ำ
  - admin เห็นรายการที่ถูกรายงาน (เชื่อมกับ US-18)

#### US-18 (issue #18) — ตรวจสอบและลบโน้ตที่ถูกรายงาน
- **Persona:** Admin
- **Priority:** Should (Sprint 2)
- **Estimate:** M
- **ที่มา:** [Scenario 3 — รายงานโน้ตที่ติดป้ายผิดวิชา](./main_scenario.md)
- **Story:** ในฐานะผู้ดูแลระบบ ฉันต้องการตรวจสอบและลบโน้ตที่ถูกรายงาน เพื่อให้แพลตฟอร์มปลอดภัยและถูกกฎหมาย
- **Acceptance Criteria:**
  - เห็นรายการที่ถูกรายงานพร้อมเหตุผล
  - ลบโน้ตที่ถูกรายงานได้
  - ปฏิเสธรายงานที่ไม่มีมูลได้

---

### หมายเหตุ: issue ที่ถูกปิดเพราะซ้ำ

Issue ต่อไปนี้ถูกปิดบน GitHub แล้วเพราะเนื้อหาซ้ำกับ story ที่ระบุไว้ข้างต้น จึงไม่ถูกนับเป็น story แยกในเอกสารนี้:

- #25 — ซ้ำกับ US-09 (#9)
- #27 — ซ้ำกับ US-11 (#11)
- #29 — ซ้ำกับ US-08 (#8)
- #30 — ซ้ำกับ US-16 (#16)
- #32 — ซ้ำกับ US-05 + US-06 (#5, #6)
