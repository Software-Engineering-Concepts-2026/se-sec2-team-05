# NoteShare — สถาปัตยกรรม

🌐 [English](./README.md) · **ภาษาไทย**

พิมพ์เขียวทางสถาปัตยกรรมของ **NoteShare** เว็บแพลตฟอร์มให้นักศึกษาอัปโหลด ค้นหา และแบ่งปันสรุปเลกเชอร์
เราอธิบายระบบด้วย [C4 model](https://c4model.com/) (Level 1 และ 2) และบันทึกเหตุผลของการตัดสินใจสำคัญไว้เป็น [ADR](./adr/)

## C4 Level 1 — บริบทของระบบ (System Context)

ภาพรวมว่าใครใช้ NoteShare และระบบไปพึ่งพาบริการภายนอกอะไรบ้าง

![C4 Level 1 – แผนภาพบริบทของระบบ NoteShare](diagrams/c4-level-1-context.th.png)

| ความสัมพันธ์ | คำอธิบาย |
| --- | --- |
| เจมส์ (ผู้ค้นหาโน้ต) → NoteShare | ค้นหา ดูตัวอย่าง และดาวน์โหลดโน้ต แล้วให้เครดิตเจ้าของโน้ต |
| พิม (ผู้แบ่งปันโน้ต) → NoteShare | อัปโหลดและจัดระเบียบโน้ต ดูการยอมรับ/สถิติการใช้งานโน้ตของตัวเอง |
| NoteShare → บริการอีเมล | ส่งอีเมลยืนยันบัญชีและอีเมลแจ้งเตือน |

```mermaid
C4Context
    title System Context diagram for NoteShare

    Person(james, "James", "Note Seeker")
    Person(pim, "Pim", "Note Contributor")

    System(noteshare, "NoteShare", "Web platform where university students upload, search, and share lecture notes")

    System_Ext(email, "Email Service", "External email provider")

    Rel(james, noteshare, "Searches, previews & downloads notes; gives credit to authors")
    Rel(pim, noteshare, "Uploads & organizes notes; views recognition/usage of her notes")
    Rel(noteshare, email, "Sends account-verification and notification emails")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

ต้นฉบับ Mermaid แก้ไขได้ที่ [c4-context.md](./c4-context.md) (มีเวอร์ชันเดียว ใช้ร่วมกับหน้าอังกฤษ)

## C4 Level 2 — Container

ซูมเข้าไปในระบบ NoteShare เพื่อดูส่วนประกอบที่ deploy แยกกันได้ และการสื่อสารระหว่างกัน

![C4 Level 2 – แผนภาพ Container ของ NoteShare](diagrams/c4-level-2-container.th.png)

| Container | เทคโนโลยี | หน้าที่ |
| --- | --- | --- |
| Single-Page App | React + Vite | UI ทั้งหมดในเบราว์เซอร์: ค้นหา กรอง ดูตัวอย่าง อัปโหลด และให้เครดิต |
| API Gateway | Python + Flask | ทางเข้าเดียวของระบบ กระจาย request ไปยัง service และตรวจสอบ token (JWT) |
| User & Auth Service | Python + Flask | สมัครสมาชิก เข้าสู่ระบบ (เก็บรหัสผ่านแบบ hash) ออก JWT และจัดการโปรไฟล์ |
| Notes Service | Python + Flask | ข้อมูลโน้ต ค้นหา/กรอง จัดการอัปโหลด–ดาวน์โหลด และเครดิต |
| Stats Service | Python + Flask | รวมสถิติยอดดาวน์โหลดและการใช้งานโน้ต เพื่อการยอมรับของผู้แบ่งปัน |
| PostgreSQL Database | PostgreSQL | เก็บข้อมูลผู้ใช้ metadata ของโน้ต รายวิชา และเครดิต |
| Object Storage | S3-compatible | เก็บไฟล์โน้ตที่อัปโหลด (PDF/รูปภาพ) |

```mermaid
C4Container
    title Container diagram for NoteShare

    Person(james, "James", "Note Seeker")
    Person(pim, "Pim", "Note Contributor")

    System_Boundary(noteshare, "NoteShare") {
        Container(spa, "Single-Page App", "React + Vite", "All user-facing UI in the browser: search, filter, preview, upload, credit")
        Container(gateway, "API Gateway", "Python + Flask", "Single entry point; routes requests to services and verifies tokens (JWT)")
        Container(auth, "User & Auth Service", "Python + Flask", "Registration, login (hashed passwords), JWT issuance, profiles")
        Container(notes, "Notes Service", "Python + Flask", "Note metadata, search/filter, upload/download, credits")
        Container(stats, "Stats Service", "Python + Flask", "Aggregates download and usage stats for contributor recognition")
        ContainerDb(db, "PostgreSQL Database", "PostgreSQL", "Users, note metadata, courses, and credit records")
        ContainerDb(storage, "Object Storage", "S3-compatible", "Uploaded note files (PDF/images)")
    }

    Rel(james, spa, "Uses", "HTTPS")
    Rel(pim, spa, "Uses", "HTTPS")

    Rel(spa, gateway, "Makes calls to", "REST/JSON over HTTPS")

    Rel(gateway, auth, "Routes requests to", "REST/JSON")
    Rel(gateway, notes, "Routes requests to", "REST/JSON")
    Rel(gateway, stats, "Routes requests to", "REST/JSON")

    Rel(auth, db, "Reads/writes", "SQL")
    Rel(notes, db, "Reads/writes", "SQL")
    Rel(stats, db, "Reads/writes", "SQL")

    Rel(notes, storage, "Stores/retrieves note files", "S3 API")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

ต้นฉบับ Mermaid แก้ไขได้ที่ [c4-container.md](./c4-container.md) (มีเวอร์ชันเดียว ใช้ร่วมกับหน้าอังกฤษ)

## Technology Stack

| ส่วน | ที่เลือกใช้ |
| --- | --- |
| Frontend | React (SPA) + Vite |
| Backend | Python + Flask (microservices) |
| Inter-service communication | REST / JSON over HTTP |
| Database | PostgreSQL |
| File storage | S3-compatible object storage |
| Packaging | Docker + Docker Compose |
| Deployment | backend รันเป็น container บน cloud host, frontend บน Vercel |

เหตุผลและ trade-off ทั้งหมดอยู่ใน [ADR-001: Core Technology Stack](./adr/0001-tech-stack-selection.th.md)

## Architecture Decision Records

- [ADR-001 — การเลือก Core Technology Stack](./adr/0001-tech-stack-selection.th.md)
- [ADR-002 — ใช้ RESTful API สำหรับการสื่อสารระหว่าง Service](./adr/0002-use-restful-api-internal-communication.th.md)

## แก้ไขแผนภาพ

แผนภาพเขียนเป็นไฟล์ SVG (`diagrams/*.svg`) เป็นต้นฉบับ และ export เป็น `.png` สำหรับแสดงผล
แต่ละแผนภาพมีเวอร์ชันอังกฤษและไทย (`*.th.svg` / `*.th.png`) แก้ที่ไฟล์ `.svg` แล้ว export เป็น PNG ชื่อเดิมทับ
