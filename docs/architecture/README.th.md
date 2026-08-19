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
    title แผนภาพบริบทของระบบ NoteShare

    Person(james, "เจมส์", "ผู้ค้นหาโน้ต")
    Person(pim, "พิม", "ผู้แบ่งปันโน้ต")

    System(noteshare, "NoteShare", "เว็บแพลตฟอร์มให้นักศึกษาอัปโหลด ค้นหา และแบ่งปันสรุปเลกเชอร์")

    System_Ext(email, "บริการอีเมล", "ผู้ให้บริการอีเมลภายนอก")

    Rel(james, noteshare, "ค้นหาและดาวน์โหลดโน้ต")
    Rel(pim, noteshare, "อัปโหลดโน้ต ดูเครดิต")
    Rel(noteshare, email, "ส่งอีเมลยืนยันบัญชี")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

ต้นฉบับ Mermaid: [`diagrams/c4-level-1-context.th.mmd`](diagrams/c4-level-1-context.th.mmd) · ดูคำอธิบายเพิ่มเติมที่ [c4-context.md](./c4-context.md)

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
flowchart TB
    james["<b>เจมส์</b><br/>ผู้ค้นหาโน้ต"]
    pim["<b>พิม</b><br/>ผู้แบ่งปันโน้ต"]

    subgraph noteshare["NoteShare"]
        spa["<b>Single-Page App</b><br/><i>React + Vite</i><br/>UI ค้นหา กรอง ดูตัวอย่าง<br/>อัปโหลด และให้เครดิต"]
        gateway["<b>API Gateway</b><br/><i>Python + Flask</i><br/>ทางเข้าเดียวของระบบ<br/>ตรวจสอบ JWT"]

        auth["<b>User &amp; Auth Service</b><br/><i>Python + Flask</i><br/>สมัครสมาชิก เข้าสู่ระบบ<br/>ออก JWT จัดการโปรไฟล์"]
        notes["<b>Notes Service</b><br/><i>Python + Flask</i><br/>ข้อมูลโน้ต ค้นหา/กรอง<br/>อัปโหลด–ดาวน์โหลด เครดิต"]
        stats["<b>Stats Service</b><br/><i>Python + Flask</i><br/>สถิติยอดดาวน์โหลด<br/>และการใช้งาน"]

        db[("<b>PostgreSQL Database</b><br/><i>PostgreSQL</i><br/>ผู้ใช้ metadata ของโน้ต<br/>รายวิชา และเครดิต")]
        storage[("<b>Object Storage</b><br/><i>S3-compatible</i><br/>ไฟล์โน้ตที่อัปโหลด")]
    end

    james -->|"ใช้งาน<br/><i>HTTPS</i>"| spa
    pim -->|"ใช้งาน<br/><i>HTTPS</i>"| spa
    spa -->|"เรียกผ่าน<br/><i>REST/JSON over HTTPS</i>"| gateway

    gateway -->|"<i>REST/JSON</i>"| auth
    gateway -->|"<i>REST/JSON</i>"| notes
    gateway -->|"<i>REST/JSON</i>"| stats

    auth -->|"<i>SQL</i>"| db
    notes -->|"<i>SQL</i>"| db
    stats -->|"<i>SQL</i>"| db
    notes -->|"ไฟล์โน้ต<br/><i>S3 API</i>"| storage
```

ต้นฉบับ Mermaid: [`diagrams/c4-level-2-container.th.mmd`](diagrams/c4-level-2-container.th.mmd) · ดูคำอธิบายเพิ่มเติมที่ [c4-container.md](./c4-container.md)

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

แผนภาพใช้ Mermaid (`diagrams/*.mmd`) เป็นต้นฉบับ แล้ว render ออกเป็น SVG และ PNG
แต่ละแผนภาพมีเวอร์ชันอังกฤษและไทย (`*.th.mmd`) แก้ที่ไฟล์ `.mmd` แล้ว render ใหม่ทั้งสองฟอร์แมตโดยใช้ชื่อไฟล์เดิม:

```bash
npx @mermaid-js/mermaid-cli -i diagrams/c4-level-1-context.th.mmd -o diagrams/c4-level-1-context.th.svg -b white
npx @mermaid-js/mermaid-cli -i diagrams/c4-level-1-context.th.mmd -o diagrams/c4-level-1-context.th.png -w 1600 -b white
```

บล็อก Mermaid ที่ฝังอยู่ในหน้านี้คือแผนภาพเดียวกัน ต้องแก้ให้ตรงกับไฟล์ `.mmd` ด้วย เพื่อให้ GitHub render ให้เห็นในหน้าได้เลยโดยไม่ต้องพึ่งไฟล์รูป
