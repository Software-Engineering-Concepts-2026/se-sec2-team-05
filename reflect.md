# Team Reflection

เอกสารนี้เป็นการสรุปภาพรวมระดับทีม แยกจาก reflection รายบุคคลแบบ essay ที่ตอบคำถามเรื่อง Software Entropy / Broken Window Theory และ Take Responsibility / Provide Options, Don't Make Lame Excuses ซึ่งอยู่ที่ [`docs/reflections/atichat.md`](docs/reflections/atichat.md), [`docs/reflections/kittamet.md`](docs/reflections/kittamet.md) และ [`docs/reflections/wachirawit_1.md`](docs/reflections/wachirawit_1.md) — ใครอยากอ่านคำตอบเต็ม ๆ ของแต่ละคนให้ไปดูที่ไฟล์เหล่านั้น

## Common Themes

เรื่อง Software Entropy ทั้งสามคนพูดถึงประเด็นใกล้เคียงกันโดยไม่ได้นัดกัน คือความลวกในการตั้งชื่อ (อติชาติ — ตั้งชื่อตัวแปร/ฟังก์ชันแบบ `data1`, `temp`; กฤตเมธและวชิรวิทย์ — ตั้งชื่อไฟล์และจัดระเบียบโค้ดไม่ดี ปล่อยโค้ดที่ไม่ได้ใช้ค้างไว้ หรือไม่วางโครงสร้าง Logic/UI แยกกันตั้งแต่แรก) ซึ่งดูเหมือนเรื่องเล็กในตอนแรก แต่พอโปรเจกต์ใหญ่ขึ้นก็กลายเป็นตัวถ่วงที่ทำให้แก้บั๊ก/เพิ่มฟีเจอร์ยากขึ้นเรื่อย ๆ ตรงกับแนวคิด Broken Window Theory ที่ทั้งสามคนอ้างถึง

เรื่อง Take Responsibility ทั้งสามคนเห็นตรงกันว่าคือการยอมรับผิดเมื่อมีปัญหาแล้วลงมือแก้ ไม่ใช่โยนความผิด ส่วนวิธีสื่อสารเมื่อทำงานไม่ทัน อติชาติกับกฤตเมธ เขียนตรงตามหลัก Provide Options ชัดเจน คือเสนอทางเลือกเป็นข้อ ๆ ให้ทีมเลือก (เช่น จำกัด scope ก่อน / ใช้ทางเลือกอื่น / เลื่อนไป sprint หน้า สำหรับอติชาติ, และขอขยายเวลา/แบ่งงาน/ส่งส่วนที่เสร็จก่อน สำหรับกฤตเมธ) ส่วนวชิรวิทย์เน้นไปที่การแจ้งทีมล่วงหน้าเพื่อช่วยกันหาทางแก้และพยายามส่งงานส่วนที่จำเป็นที่สุดให้ได้ก่อน แล้วค่อยขอขยายเวลาส่วนที่เหลือ ซึ่งเป็นแนวทางเดียวกันแต่ยังไม่ได้ระบุเป็นตัวเลือกที่จับต้องได้ชัดเท่าอีกสองคน

## Sprint Retro

ตารางข้างล่างร่างจากหลักฐานที่ตามได้จริงใน repo (commit history, PR review, สถานะ PR) ไม่ใช่จากความรู้สึกย้อนหลัง ทีมยืนยันและเพิ่มเติมกันในคาบ retro ได้

| Sprint | What went well | What didn't go well | Action items |
| --- | --- | --- | --- |
| Sprint 1 | ทั้งสามคนส่ง prototype ของตัวเองครบ (PR #35 #36 #37 merge แล้วทั้งหมด) และแบ่งงานได้ไม่ทับกัน คนละ flow<br><br>รีวิวทำงานจริง — PR #37 ถูก CHANGES_REQUESTED เรื่อง XSS แล้วแก้ก่อน merge (เพิ่มฟังก์ชัน `esc()` และ clamp ค่าดาว) ไม่ใช่ approve ผ่าน ๆ<br><br>ไม่มีใคร push ตรงเข้า `main` เลย ทุกอย่างผ่าน branch + PR | PR ค้างไม่ merge เป็นเดือน — #39 #40 #41 #42 #43 เปิดค้างพร้อมกัน ทำให้งานที่ทำเสร็จแล้วไม่นับเป็นของที่ส่ง<br><br>PR description บางอันแทบว่าง (#36 มีแค่ commit message ที่ถูกตัด) และไม่มีใครแนบ screenshot ใน PR รอบ prototype เลย ทั้งที่เป็นเกณฑ์ให้คะแนน<br><br>ชื่อ branch ไม่ตรงแพตเทิร์นที่ใบงานกำหนด (`feature/atichat-upload-note-prototype` แทน `feature/lab4-prototype-<feature>`)<br><br>PR #34 ต้องปิดแล้วเปิดใหม่เป็น #36 เพราะเปิดจาก branch ผิด<br><br>`AI_USAGE.md` เขียนย้อนหลังหลังงานเสร็จไปนาน ทำให้กู้ prompt ที่ใช้จริงไม่ได้ครบ เหลือแต่ที่เผอิญค้างเป็น comment ในโค้ด | 1. ปิด PR ให้จบภายในคาบที่ทำ ไม่ปล่อยค้างข้าม lab — ถ้ายังไม่พร้อม merge ให้เปิดเป็น draft<br>2. เพิ่ม PR template ที่บังคับช่อง screenshot + วิธีทดสอบ เพื่อไม่ให้ลืมอีก<br>3. ตกลงแพตเทิร์นชื่อ branch ไว้ใน README แล้วอ้างตอนเปิด PR<br>4. บันทึก prompt ลง `AI_USAGE.md` ทันทีในรอบที่ใช้ AI ไม่รอมาเขียนย้อนหลัง<br>5. Sprint 2 ยกหน้าอัปโหลดขึ้นเป็น Tracer Bullet ตัวแรกตามที่ระบุใน [`prototypes/sprint1/README.md`](prototypes/sprint1/README.md) |

## Exit Ticket บทที่ 5 — Architecture

หมายเหตุ: ส่วนนี้เขียนย้อนหลังหลังทำ artifact ของ Lab 5 เสร็จแล้ว ไม่ได้เขียนสด ๆ ท้ายคาบบรรยาย เนื้อหาทั้งสามข้อจึงสรุปจากของที่มีอยู่จริงในรีโป ไม่ใช่การเดาล่วงหน้า

### B1 — Apply: ADR ฉบับแรก

ADR ฉบับแรกของทีมคือ [ADR-001: Selection of Core Technology Stack](docs/architecture/adr/0001-tech-stack-selection.md) เขียนตาม Nygard format ครบทั้งห้าส่วน

- **Context** — ทีม 3 คน มีทักษะ Python / HTML-CSS-JS / Git / Docker อยู่แล้ว มีเวลาหนึ่งภาคเรียน และตัดสินใจไว้ก่อนแล้วว่าจะทำเป็น microservices หลายตัว จึงต้องเลือก stack ที่รองรับ service ที่ deploy แยกกันได้และมีที่เก็บไฟล์แยกจากฐานข้อมูล
- **Decision** — React + Vite ฝั่งหน้าเว็บ, Python + Flask แบ่งเป็น 4 service (API Gateway, User & Auth, Notes, Stats), PostgreSQL คู่กับ S3-compatible object storage, แพ็กด้วย Docker + Docker Compose
- **Consequences ฝั่งดี** — Flask ตรงกับทักษะเดิมของทั้งทีม learning curve จึงต่ำ และการเก็บไฟล์ไว้ใน object storage แทนฐานข้อมูลทำให้ฐานข้อมูลเล็กและดาวน์โหลดเร็ว
- **Consequences ฝั่งเสีย** — microservices เพิ่ม operational overhead ที่หนักเกินตัวสำหรับทีม 3 คนในหนึ่งภาคเรียน เรายอมรับข้อนี้เพื่อได้ฝึกแบ่ง service จริง และคุมความเสียหายด้วยการจำกัดจำนวน service ให้น้อย · อีกข้อคือเริ่มจาก PostgreSQL instance เดียว (แยก schema ต่อ service) ไม่ใช่ database-per-service เต็มรูปแบบ แลก isolation กับความง่าย

สิ่งที่ได้จากการเขียนจริงคือช่อง Consequences ฝั่งเสียเป็นช่องที่เขียนยากที่สุด เพราะต้องยอมเขียนออกมาว่าทางที่เลือกแพ้ทางอื่นเรื่องอะไร ตอนแรก ADR-001 ไม่มีหัวข้อ Alternatives ด้วย ต้องกลับมาเติมทีหลังว่าเคยชั่งใจ monolith ไว้และเลือกไม่เอาเพราะอะไร ซึ่งพอเติมแล้วเอกสารอ่านรู้เรื่องขึ้นชัดเจน

### B2 — Connect: C4 Context + Container

- **Level 1 (Context)** — [c4-context.md](docs/architecture/c4-context.md) · มี 2 persona (เจมส์ ผู้ค้นหาโน้ต, พิม ผู้แบ่งปันโน้ต), ระบบ NoteShare และระบบภายนอกหนึ่งตัวคือบริการอีเมล
- **Level 2 (Container)** — [c4-container.md](docs/architecture/c4-container.md) · 7 container พร้อมป้ายเทคโนโลยีและโพรโทคอลทุกเส้น: SPA → API Gateway → สาม service → PostgreSQL และ Notes Service → Object Storage

บทเรียนจริงจากข้อนี้เป็นเรื่องเครื่องมือ ไม่ใช่เรื่องสถาปัตยกรรม — เราทำเป็น Mermaid ก่อน แล้วพบว่า renderer ของ `C4Container` วางป้ายชื่อขอบเขตระบบทับกับป้ายกำกับเส้น และไม่สนใจค่าจำนวนกล่องต่อแถว ทำให้ Level 2 อ่านไม่ออก จึงวาด SVG เองเพื่อคุมตำแหน่ง สุดท้ายเก็บไว้ทั้งสองแบบ: Mermaid เป็นต้นฉบับแบบข้อความที่ diff ได้ใน PR ส่วน SVG เป็นรูปที่เอาไปแสดงจริง ต้องแก้ให้ตรงกันทั้งคู่เวลาแผนภาพเปลี่ยน

ที่น่าจดไว้คือรอบแรกเราเผลอตัดสินใจแบบดู artifact เป็นหลักจนลบ Mermaid ออกทั้งหมด แล้วมารู้ทีหลังว่าใบงานระบุ Mermaid ไว้ตรง ๆ — บทเรียนคืออ่าน deliverable ให้ครบก่อนตัดสินใจทางเทคนิคที่ลบของทิ้ง

### B3 — Reflect: Tech Stack

| ส่วน | ที่เลือก | เหตุผลเชิงบริบท |
| --- | --- | --- |
| Frontend | React (SPA) + Vite | หน้าจอหลักของ NoteShare เป็นการค้นหา–กรอง–ดูตัวอย่างที่ state เปลี่ยนถี่ในหน้าเดียว component model จึงคุ้มกว่าการ render หน้าใหม่ทุกครั้ง |
| Backend | Python + Flask | ทั้งทีมเขียน Python ได้อยู่แล้วและตรงกับเนื้อหาวิชา ในเวลาหนึ่งภาคเรียนเราเลือกลดเวลาเรียนภาษาใหม่ ไปลงกับการแบ่ง service แทน |
| Database | PostgreSQL + object storage | ความสัมพันธ์ระหว่างผู้ใช้ โน้ต รายวิชา และเครดิตเป็น relational ชัดเจนและต้อง join จริง ส่วนไฟล์ PDF/รูปแยกไปไว้ object storage เพื่อไม่ให้ฐานข้อมูลบวมตามขนาดไฟล์ |

เหตุผลที่ระวังไม่เขียนคือคำว่า "ถนัด" ลอย ๆ — ข้อ Backend เป็นข้อที่ใกล้เคียงที่สุด แต่เขียนให้ผูกกับ constraint จริงคือเวลาหนึ่งภาคเรียนและสิ่งที่เราเลือกเอาเวลาไปลงแทน รายละเอียดเต็มพร้อมทางเลือกที่ตัดออกอยู่ใน [tech_stack.md](docs/architecture/tech_stack.md)

## Post-quiz 6 — Containerization

หมายเหตุ: เขียนพร้อมกับตอนทำ Lab 6 จริง ไม่ใช่ post-quiz แยกจากคาบบรรยาย เพราะไม่มี branch reflect ของ post-quiz แยกไว้ก่อนหน้า จึงรวมสามข้อ (B1–B3) ไว้ในหัวข้อนี้เลย

### B1 — Dockerfile Draft → Production Dockerfile

Draft แรก (ก่อนเห็นใบงานเต็ม) คือ copy ทั้งโปรเจกต์เข้า image เดียวแล้ว `pip install -r requirements.txt` ตรง ๆ ใน stage เดียว ไม่มี multi-stage เพราะคิดว่า Flask app เล็กไม่คุ้มจะซับซ้อน

Production Dockerfile ที่ได้ต่างจาก draft ตรงที่ (1) แยกเป็น 2 stage — stage `deps` ติดตั้ง pip package ด้วย `--user` แล้ว stage สุดท้าย copy เฉพาะ `/root/.local` ที่ build เสร็จเข้ามา ไม่พ่วง build cache/metadata (2) เพิ่ม `USER appuser` ที่สร้างเองแทนรันเป็น root (3) pin `python:3.12-slim` แทน `python:latest` (4) `.dockerignore` กัน `.env`/`.git`/`tests/` ไม่ให้หลุดเข้า image บทเรียนคือ multi-stage ไม่ได้ซับซ้อนอย่างที่คิดไว้ตอนแรก แต่ตัด layer ที่ไม่จำเป็นออกได้จริง

### B2 — Service Decomposition ตรวจด้วย Rule of Twos

Stats Service เป็น 1 ใน 4 service ตาม [C4 Container diagram](docs/architecture/c4-container.md) (Gateway, Auth, Notes, Stats) เช็คกับ Microservices Rule of Twos:

- ทีมขนาดพอดูแลได้ (3 คน ดูแล 4 service ยังไม่เกิน "two-pizza team" แต่เริ่มตึงถ้าเพิ่ม service อีก)
- Stats Service มี responsibility เดียวชัดเจน (aggregate download/usage stats) ไม่ปนกับ Auth หรือ Notes — อ่านจาก DB โดยตรง ไม่ต้องเรียกข้าม service อื่นบ่อย
- ความเสี่ยงที่เห็นจาก Rule of Twos คือถ้าเพิ่ม service ที่ 5 (เช่น Notification service) ทีม 3 คนอาจดูแล operational overhead ไม่ไหว — ตรงกับ Consequences ฝั่งเสียที่เขียนไว้ใน ADR-001 อยู่แล้ว จึงตัดสินใจคงที่ 4 service ต่อไปในเทอมนี้

### B3 — REST Endpoint

เลือก `GET /stats` ของ Stats Service เป็นตัวอย่าง เพราะเป็น read-only, stateless, และไม่ต้อง auth ในเวอร์ชันนี้ (auth มาจาก API Gateway ที่ route เข้ามาตาม [ADR-002](docs/architecture/adr/0002-use-restful-api-internal-communication.md)) ตอนนี้ response ยังเป็น mock data คงที่เพราะยังไม่ได้ต่อ PostgreSQL จริง (Sprint 2) แต่ shape ของ JSON (`total_downloads`, `total_notes`, `top_contributors`) ออกแบบให้ตรงกับสิ่งที่ Notes/Auth service ต้องส่งมาให้ query ได้จริงในอนาคต ไม่ใช่เดาขึ้นมาลอย ๆ
