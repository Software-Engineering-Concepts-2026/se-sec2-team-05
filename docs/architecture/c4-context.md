# C4 Level 1 — System Context (Mermaid Source)

แผนภาพ C4 Level 1 (System Context) ของ NoteShare ในรูปแบบ Mermaid

ต้นฉบับที่ใช้ render จริงอยู่ที่ [`diagrams/c4-level-1-context.mmd`](diagrams/c4-level-1-context.mmd) (ฉบับไทย: [`.th.mmd`](diagrams/c4-level-1-context.th.mmd)) — ถ้าจะแก้แผนภาพ ให้แก้ที่ไฟล์ `.mmd` แล้ว render รูปใหม่ตามขั้นตอนใน [README.md](./README.md#editing-the-diagrams) จากนั้นอัปเดตบล็อกด้านล่างนี้กับใน README ให้ตรงกัน

## Diagram

```mermaid
C4Context
    title System Context diagram for NoteShare

    Person(james, "James", "Note Seeker")
    Person(pim, "Pim", "Note Contributor")

    System(noteshare, "NoteShare", "Web platform where university students upload, search, and share lecture notes")

    System_Ext(email, "Email Service", "External email provider")

    Rel(james, noteshare, "Searches & downloads notes")
    Rel(pim, noteshare, "Uploads notes, views credit")
    Rel(noteshare, email, "Sends verification emails")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Relationships (อ้างอิงจาก README.md)

| Relationship | Description |
| --- | --- |
| James (Note Seeker) → NoteShare | Searches, previews & downloads notes; gives credit to authors |
| Pim (Note Contributor) → NoteShare | Uploads & organizes notes; views recognition/usage of her notes |
| NoteShare → Email Service | Sends account-verification and notification emails |

ตารางด้านบนคือคำอธิบายความสัมพันธ์ฉบับเต็ม เหมือนกับตารางในหัวข้อ "C4 Level 1 — System Context" ของ [README.md](./README.md) ทุกประการ ส่วนป้ายกำกับเส้นในแผนภาพย่อให้สั้นลง เพราะถ้าใส่ข้อความเต็มลงไป Mermaid จะวางป้ายของเส้นสองเส้นทับกันจนอ่านไม่ออก — ไม่ได้เพิ่มหรือลด entity/ความสัมพันธ์ใด ๆ
