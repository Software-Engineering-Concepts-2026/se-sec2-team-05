# C4 Level 2 — Containers (Mermaid Source)

ไฟล์นี้คือต้นฉบับ Mermaid ของแผนภาพ C4 Level 2 (Container) สำหรับ NoteShare ใช้คู่กับรูป PNG ใน [README.md](./README.md#c4-level-2--containers) container, เทคโนโลยี, และ responsibility ทั้งหมดตรงกับตารางใน README ทุกประการ

## Diagram

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

## Containers (อ้างอิงจาก README.md)

| Container | Tech | Responsibility |
| --- | --- | --- |
| Single-Page App | React + Vite | All user-facing UI in the browser: search, filter, preview, upload, credit |
| API Gateway | Python + Flask | Single entry point; routes requests to services and verifies tokens (JWT) |
| User & Auth Service | Python + Flask | Registration, login (hashed passwords), JWT issuance, profiles |
| Notes Service | Python + Flask | Note metadata, search/filter, upload/download, credits |
| Stats Service | Python + Flask | Aggregates download and usage stats for contributor recognition |
| PostgreSQL Database | PostgreSQL | Users, note metadata, courses, and credit records |
| Object Storage | S3-compatible | Uploaded note files (PDF/images) |

การเรียกทั้งหมดระหว่าง SPA → API Gateway → services เป็น REST/JSON over HTTP (รายละเอียดใน [ADR-002](./adr/0002-use-restful-api-internal-communication.md)) ส่วน service แต่ละตัวคุยกับ PostgreSQL ด้วย SQL ตรง ๆ และ Notes Service เป็นตัวที่ต่อกับ Object Storage สำหรับไฟล์โน้ตที่อัปโหลด/ดาวน์โหลด
