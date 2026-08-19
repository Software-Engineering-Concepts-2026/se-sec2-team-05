# C4 Level 1 — System Context (Diagram Source)

แผนภาพ C4 Level 1 (System Context) ของ NoteShare

ต้นฉบับอยู่ที่ [`diagrams/c4-level-1-context.svg`](diagrams/c4-level-1-context.svg) (ฉบับไทย: [`.th.svg`](diagrams/c4-level-1-context.th.svg)) — ถ้าจะแก้แผนภาพ ให้แก้ที่ไฟล์ `.svg` แล้ว export `.png` ใหม่ตามขั้นตอนใน [README.md](./README.md#editing-the-diagrams)

## Diagram

![C4 Level 1 – System Context diagram for NoteShare](diagrams/c4-level-1-context.png)

## Relationships

| Relationship | Description |
| --- | --- |
| James (Note Seeker) → NoteShare | Searches, previews & downloads notes; gives credit to authors |
| Pim (Note Contributor) → NoteShare | Uploads & organizes notes; views recognition/usage of her notes |
| NoteShare → Email Service | Sends account-verification and notification emails |

ตารางนี้ตรงกับป้ายกำกับเส้นในแผนภาพทุกคำ — ก่อนหน้านี้แผนภาพย่อข้อความให้สั้นลงเพราะ Mermaid วางป้ายของสองเส้นทับกัน ตอนนี้วาด SVG เองแล้วจึงใส่ข้อความเต็มลงในแผนภาพได้

## ทำไมไม่ได้ใช้ Mermaid

ทั้ง Level 1 และ Level 2 วาดเป็น SVG เอง เพื่อให้สองแผนภาพใช้สัญลักษณ์และรูปแบบชุดเดียวกัน — Level 2 จำเป็นต้องวาดเองเพราะ renderer ของ `C4Container` มีบั๊กเรื่องการจัดวาง (ดู [c4-container.md](./c4-container.md)) ถ้าปล่อยให้ Level 1 ยังเป็น Mermaid ต่อ สองระดับจะหน้าตาไม่เหมือนกัน และ Level 1 ก็ยังติดปัญหาป้ายกำกับเส้นทับกันอยู่

สัญลักษณ์ที่ใช้เป็นไปตามมาตรฐาน C4: กล่อง `«Person»` สำหรับผู้ใช้, `«Software System»` สีน้ำเงินสำหรับระบบที่พิจารณา, `«External System»` สีเทาสำหรับระบบภายนอก และเส้นความสัมพันธ์ที่มีคำอธิบายกำกับ ส่วนรายละเอียดเทคโนโลยีและโพรโทคอลอยู่ที่ Level 2 ตามที่ C4 model กำหนดว่าเป็นเรื่องของ container diagram
