# Team Reflection

เอกสารนี้เป็นการสรุปภาพรวมระดับทีม แยกจาก reflection รายบุคคลแบบ essay ที่ตอบคำถามเรื่อง Software Entropy / Broken Window Theory และ Take Responsibility / Provide Options, Don't Make Lame Excuses ซึ่งอยู่ที่ [`docs/reflections/atichat.md`](docs/reflections/atichat.md), [`docs/reflections/kittamet.md`](docs/reflections/kittamet.md) และ [`docs/reflections/wachirawit_1.md`](docs/reflections/wachirawit_1.md) — ใครอยากอ่านคำตอบเต็ม ๆ ของแต่ละคนให้ไปดูที่ไฟล์เหล่านั้น

## Common Themes

เรื่อง Software Entropy ทั้งสามคนพูดถึงประเด็นใกล้เคียงกันโดยไม่ได้นัดกัน คือความลวกในการตั้งชื่อ (อติชาติ — ตั้งชื่อตัวแปร/ฟังก์ชันแบบ `data1`, `temp`; กฤตเมธและวชิรวิทย์ — ตั้งชื่อไฟล์และจัดระเบียบโค้ดไม่ดี ปล่อยโค้ดที่ไม่ได้ใช้ค้างไว้ หรือไม่วางโครงสร้าง Logic/UI แยกกันตั้งแต่แรก) ซึ่งดูเหมือนเรื่องเล็กในตอนแรก แต่พอโปรเจกต์ใหญ่ขึ้นก็กลายเป็นตัวถ่วงที่ทำให้แก้บั๊ก/เพิ่มฟีเจอร์ยากขึ้นเรื่อย ๆ ตรงกับแนวคิด Broken Window Theory ที่ทั้งสามคนอ้างถึง

เรื่อง Take Responsibility ทั้งสามคนเห็นตรงกันว่าคือการยอมรับผิดเมื่อมีปัญหาแล้วลงมือแก้ ไม่ใช่โยนความผิด ส่วนวิธีสื่อสารเมื่อทำงานไม่ทัน อติชาติกับกฤตเมธ เขียนตรงตามหลัก Provide Options ชัดเจน คือเสนอทางเลือกเป็นข้อ ๆ ให้ทีมเลือก (เช่น จำกัด scope ก่อน / ใช้ทางเลือกอื่น / เลื่อนไป sprint หน้า สำหรับอติชาติ, และขอขยายเวลา/แบ่งงาน/ส่งส่วนที่เสร็จก่อน สำหรับกฤตเมธ) ส่วนวชิรวิทย์เน้นไปที่การแจ้งทีมล่วงหน้าเพื่อช่วยกันหาทางแก้และพยายามส่งงานส่วนที่จำเป็นที่สุดให้ได้ก่อน แล้วค่อยขอขยายเวลาส่วนที่เหลือ ซึ่งเป็นแนวทางเดียวกันแต่ยังไม่ได้ระบุเป็นตัวเลือกที่จับต้องได้ชัดเท่าอีกสองคน

## Post-quiz 3 — Requirements Documents

หมายเหตุ: เขียนย้อนหลัง เพราะไม่มี branch `feature/exit-ticket-3` แยกไว้ก่อนหน้าตามที่ใบงาน Lab 3 ระบุ จึงรวบรวมจากหลักฐานจริงที่มีอยู่แล้วในรีโป ([`docs/requirements/personas/`](docs/requirements/personas/), [`main_scenario.md`](docs/requirements/main_scenario.md), [`user-stories.md`](docs/requirements/user-stories.md), [`nfr.md`](docs/requirements/nfr.md)) ไม่ใช่การเดาย้อนหลัง

### B1 — Apply: Magic Shipping

ลูกค้าบอก "อยากให้แอปส่ง notification โปรโมชันใหม่" — โจทย์นี้กำกวมเพราะไม่รู้ว่า "ส่ง" หมายถึงอะไร ถึงใคร บ่อยแค่ไหน คำถาม 3 ข้อที่จะถามเพิ่มเพื่อให้ชัดพอจะเขียนเป็น user story ได้:

1. **ส่งถึงใคร** — ผู้ใช้ทุกคน หรือกรองเฉพาะกลุ่ม (เช่น เฉพาะคนที่เคยดาวน์โหลดโน้ตวิชานั้น)? ถ้าไม่ถามข้อนี้ก่อน อาจ implement เป็น broadcast ทั้งระบบทั้งที่ลูกค้าต้องการแค่ segment เดียว
2. **ผ่านช่องทางไหน** — in-app notification, อีเมล, หรือ push notification ของเบราว์เซอร์? แต่ละช่องทางใช้ infrastructure คนละแบบ (ใน scope ของ NoteShare ตอนนี้ยังไม่มี push notification service เลย ถ้าลูกค้าหมายถึง push ต้องเพิ่ม NFR/container ใหม่)
3. **"โปรโมชัน" คืออะไรในบริบทแอปแบ่งปันโน้ตที่ไม่มีการขายของ** — หมายถึงประกาศฟีเจอร์ใหม่ ประกาศกิจกรรมของทีม หรือจริง ๆ แล้วเป็น requirement ที่หลุดมาจากโปรเจกต์อื่น? ถ้าไม่เช็คคำนี้อาจไปสร้างฟีเจอร์ที่ไม่ตรงกับ scope ของ NoteShare เลย (ตรงกับ [PP] Tip 45 — "No one knows exactly what they want" ต้องถามให้ชัดก่อนลงมือ)

### B2 — Connect: NFR

แอปที่ใช้ทุกวัน: **LINE** (คุยงานกับทีมและติดต่ออาจารย์)

- **NFR ที่เลือก:** ข้อความที่ส่งต้องถึงผู้รับภายใน 2 วินาที เมื่อทั้งสองฝั่งมีสัญญาณอินเทอร์เน็ตปกติ (performance/reliability)
- **วิธีวัด:** จับเวลาตั้งแต่กดส่งบนเครื่องต้นทาง ถึงข้อความขึ้น "อ่านแล้ว/ส่งถึงแล้ว" บนเครื่องปลายทาง (อุปกรณ์คนละเครื่อง ซิงก์เวลาไว้ก่อน) ทำซ้ำหลายสิบครั้งแล้ววัด p95 แทนค่าเฉลี่ยเดียว เพราะ error กระจายไม่สม่ำเสมอ
- **ผลกระทบถ้าไม่มี NFR นี้:** ถ้าไม่กำหนดตัวเลขไว้ ทีมพัฒนาอาจปล่อยดีเลย์เป็นสิบวินาทีได้โดยยังถือว่า "ใช้งานได้" — ผลคือข้อความเรื่องด่วน (เช่นนัดประชุมกะทันหัน) มาช้าจนพลาดจังหวะ ผู้ใช้เสียความเชื่อมั่นและเปลี่ยนไปใช้แอปอื่นแทน ตรงกับเหตุผลที่ [`nfr.md`](docs/requirements/nfr.md) ของ NoteShare เองก็ผูกทุกข้อกับตัวเลขวัดผลได้ (เช่น NFR-002 คืนผลค้นหาภายใน 3 วินาที) แทนคำคุณศัพท์อย่าง "เร็ว"

### B3 — Reflect: User Story

**User Story ที่เลือกสำหรับ Sprint 1:** ในฐานะผู้แบ่งปันโน้ต (Note Contributor) ฉันต้องการอัปโหลดไฟล์โน้ต (PDF/รูปภาพ) เพื่อแบ่งปันสรุปให้เพื่อนในชุมชน

**เหตุผลที่เลือกเรื่องนี้:** อัปโหลดโน้ตเป็น core value proposition ของ NoteShare โดยตรง — ถ้าไม่มีโน้ตให้อัปโหลด ฟีเจอร์อื่นทั้งหมด (ค้นหา ดาวน์โหลด ให้เครดิต ให้คะแนน) ก็ไม่มีข้อมูลให้ทำงานด้วย จึงเป็น Must-have ตัวแรกที่ต้องมีก่อนอย่างอื่น เรื่องนี้ต่อมาถูกขยายเป็น GitHub Issue #7 (`US-07`) ใน Lab 3 จริง ผูกกับ [Scenario 4 — อัปโหลดโน้ตพร้อมข้อมูลครบ ตัดปัญหาถูกทักซ้ำ](docs/requirements/main_scenario.md) และตั้ง priority เป็น Must (Sprint 1) พร้อม Acceptance Criteria ครบ 4 ข้อใน [`user-stories.md`](docs/requirements/user-stories.md)

## Post-quiz 4 — AI Prompting Strategy

หมายเหตุ: เขียนย้อนหลัง เพราะไม่มี branch `feature/exit-ticket-4` แยกไว้ก่อนหน้าตามที่ใบงาน Lab 4 ระบุ เขียนหลัง Lab 4 (prototype ทั้งสามหน้า) เสร็จไปแล้ว จึงอ้างอิงกับสิ่งที่เกิดขึ้นจริงใน [`AI_USAGE.md`](AI_USAGE.md) แทนการเดาแผนล่วงหน้า

### B1 — Apply: Prompt Critique

Prompt เดิม "ช่วยเขียน code Python ที่ดีๆ หน่อย" ไม่ผ่านสัก S เดียวใน Five S's เพราะไม่บอกด้วยซ้ำว่าจะเขียนฟังก์ชันอะไร Prompt ที่เขียนใหม่สำหรับ `calculate_discount`:

```
คุณเป็น senior Python developer

เขียนฟังก์ชัน calculate_discount(price: float, discount_percent: float) -> float
ที่คำนวณราคาสินค้าหลังหักส่วนลด สำหรับใช้ใน production code

ข้อกำหนด:
- price ต้องมากกว่า 0, discount_percent ต้องอยู่ในช่วง 0-100 — ถ้าไม่เข้าเงื่อนไข raise ValueError พร้อมข้อความบอกสาเหตุ
- คืนค่าราคาหลังหักส่วนลด ปัดทศนิยม 2 ตำแหน่ง
- ใส่ type hint และ docstring สั้นๆ 1-2 บรรทัด

ขอแค่ตัวฟังก์ชันนี้ฟังก์ชันเดียว ไม่ต้องมี main() หรือ unit test
```

เทียบกับ Five S's ทีละข้อ: **Structured** ผ่าน (แยกข้อกำหนดเป็น bullet), **Specific** ผ่าน (ชื่อฟังก์ชัน, signature, ช่วงค่าที่รับได้, จำนวนทศนิยม, error handling ระบุชัดหมด — จุดที่ prompt เดิมไม่มีเลยสักอย่าง), **Single task** ผ่าน (ปิดท้ายกันไม่ให้ AI พ่วง test/main มาด้วย), **Short** ผ่าน (กระชับ ไม่มีคำฟุ่มเฟือย), **Surrounding** ผ่าน (บอก role "senior Python developer" และบริบทว่าเป็น production code ไม่ใช่ script ทดลอง ทำให้ได้ error handling ที่รัดกุมกว่าถ้าไม่บอก)

### B2 — Connect: AI ในงานที่ใช้

- **Task ที่ AI ช่วยได้จริง:** สร้าง interactive prototype (HTML/CSS/JS) จาก spec ที่ให้ชัดเจน — เกิดขึ้นจริงใน Lab 4: Copilot/ChatGPT สร้างหน้าอัปโหลดโน้ต (PR #35), Gemini สร้างหน้า note-rating พร้อมระบบดาว (PR #36) ทั้งสองกรณีนี้เป็นงาน boilerplate ที่ pattern ชัดเจนอยู่แล้ว (persona + scenario บอกไว้ครบใน Lab 3) AI จึงร่างโครงได้เร็วและถูกต้องพอสมควรตั้งแต่รอบแรก
- **Task ที่ AI ใช้ไม่ได้/ไม่ควรใช้ตรงๆ:** ตัดสินใจเรื่อง security ของ input ที่ผู้ใช้พิมพ์เอง — เกิดขึ้นจริงเช่นกัน: โค้ดหน้าค้นหาที่ AI ช่วยร่างใน PR #37 ถูก reviewer สั่ง CHANGES_REQUESTED เพราะไม่ได้ escape ข้อความก่อนแสดงผล (XSS) ต้องเพิ่มฟังก์ชัน `esc()` เองถึงจะผ่าน เหตุผลคือ AI generate โค้ดที่ "ทำงานได้" แต่ไม่รู้ context ว่าข้อมูลไหนมาจากผู้ใช้และต้อง sanitize จุดไหนบ้าง เรื่องแบบนี้ต้องให้คนตรวจ ไม่ใช่เชื่อว่า AI คิดเรื่อง security ให้ครบเอง

### B3 — Reflect: AI Strategy

Sprint หน้า (ตอนทำ Lab 4 จริง) วางแผนจะใช้ AI ในขั้นตอน **สร้าง starter prototype (markup/style เริ่มต้น) จาก scenario ที่มีอยู่แล้วใน Lab 3** เพราะเป็นงานที่มี input ชัด (persona, scenario, action sequence) แปลงเป็น UI ได้ตรงไปตรงมา และ AI ทำได้เร็วกว่าพิมพ์ HTML/CSS เองทีละบรรทัดมาก แต่จะ**ไม่**ให้ AI เป็นคนตัดสินใจสุดท้ายในสองเรื่อง: (1) จุดที่รับ input จากผู้ใช้ต้อง escape/validate เอง ตรวจทุกครั้งก่อน commit ไม่ปล่อยผ่านตามที่ AI เขียนมา — บทเรียนตรงจาก B2 ข้างบน (2) priority/scope ของ prototype ยังเป็นการตัดสินใจของทีมเหมือนเดิมตาม policy AI usage ของ Lab 3 ผลจริงคือแผนนี้ตรงกับที่เกิดขึ้นใน Lab 4 พอดี — ได้ prototype เร็วจาก AI แต่ต้องแก้ XSS เองหลัง review อยู่ดี

## Sprint Retro

ตารางข้างล่างร่างจากหลักฐานที่ตามได้จริงใน repo (commit history, PR review, สถานะ PR) ไม่ใช่จากความรู้สึกย้อนหลัง ทีมยืนยันและเพิ่มเติมกันในคาบ retro ได้

| Sprint | What went well | What didn't go well | Action items |
| --- | --- | --- | --- |
| Sprint 0 | Charter + README เริ่มต้น (Lab 1) ทำเร็วมาก — commit แรกของ repo วันที่ 17 มิ.ย. และ PR #1 (`docs/initial-charter`) merge ในวันที่ 27 มิ.ย. วันเดียวกับที่ตั้งชื่อทีม "The Builders" ไม่มีการดองงานตั้งแต่ต้น | Project Proposal + Definition of Done (Lab 2 deliverable) ไม่ได้ทำจนถึง **19 ส.ค.** — ห่างจาก Lab 1 เกือบ 2 เดือน ทั้งที่ตามกำหนดควรห่างกันแค่ 1 สัปดาห์ และ merge วันเดียวกับ PR #39 (`docs/lab2-proposal-dod`) พร้อมกับ PR #40-45 ที่เป็นการไล่แก้ Lab 3-5 ย้อนหลังทั้งชุด — แปลว่าทีมทิ้งงานตั้งแต่ Lab 2 เป็นต้นมาแล้วมาอัดทำทีเดียวช่วงกลางเดือนสิงหาคม | 1. ถ้าจะดองงาน ให้บอกทีมล่วงหน้าว่าจะไล่ตามให้ทันตอนไหน แทนที่จะปล่อยเงียบจนของค้างเป็นเดือน<br>2. Sprint 0 ควรมี checkpoint สั้น ๆ ทุกสัปดาห์ (แม้ไม่ใช่ Lab ที่มีคาบ) เพื่อไม่ให้ momentum จาก Lab 1 หายไป |
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

**Status code:** ตอนนี้ [`app.py`](services/stats-service/app.py) คืน `200 OK` เสมอผ่าน `jsonify()` ยังไม่มี branch สำหรับกรณี error (เช่น service ล่ม/DB ต่อไม่ได้) เพราะยังเป็น mock data ไม่มีจุดที่ fail ได้จริง — เมื่อต่อ PostgreSQL จริงใน Sprint 2 ต้องเพิ่ม `503` เมื่อ DB unreachable ตาม NFR-011 ที่เขียนไว้แล้วใน [`nfr.md`](docs/requirements/nfr.md)

**Versioning:** endpoint ปัจจุบันคือ `/stats` ไม่มี prefix เวอร์ชัน (เช่น `/v1/stats`) — เป็นช่องว่างที่ยังไม่ได้ตัดสินใจจริง ๆ ไม่ใช่ว่าตั้งใจไม่ใส่ ถ้า API เปลี่ยน breaking change ในอนาคต (เช่น เปลี่ยน shape ของ `top_contributors`) ตอนนี้ยังไม่มีทาง version ให้ client เก่ากับใหม่อยู่ร่วมกันได้ ควรตัดสินใจเรื่องนี้ก่อนเริ่ม Sprint 2 ไม่ใช่ปล่อยผ่าน

## Post-quiz 7 - Refactoring

หมายเหตุ: ทำก่อนเริ่ม Lab 7 ตามที่ใบงานสั่ง (ถ้ายังไม่ได้ทำในคาบบรรยาย) เนื้อหาอ้างจากการอ่านโค้ดจริงในรีโป ไม่ใช่การเดา

### DRY Hunt

โค้ดจริงในโปรเจกต์ยังมีน้อย (ส่วนใหญ่เป็นเอกสาร/mockup) แต่จุดที่เห็น DRY violation ชัดคือแนวคิด "แปลงคะแนนเป็นดาว" ถูกทำซ้ำคนละแบบใน 2 ไฟล์:

- `wachirawit_search_note_prototype.html` เดิมมีฟังก์ชัน `stars()` แปลงตัวเลขเป็นข้อความดาว (`★★★★☆`)
- `kittamet_note_rating_prototype.html` มี logic คนละแบบ (toggle class + textContent ของ `<span>` 5 ตัว) แต่ทำเรื่องเดียวกันคือ "แสดงดาวตามคะแนน 0-5"

ทั้งสองที่ hardcode เลข 5 (จำนวนดาวเต็ม) ไว้ในโค้ดของตัวเอง ถ้าจะเปลี่ยนสเกลคะแนน (เช่นเป็น 10) ต้องไปแก้หลายที่ Lab 7 นี้แก้เฉพาะฝั่ง `wachirawit_search_note_prototype.html` (ย้าย `stars()` ไป `note-utils.js`) ส่วนฝั่ง `kittamet_note_rating_prototype.html` ยังไม่แตะ เพราะเป็นคนละรูปแบบ implementation (interactive DOM ไม่ใช่ text) ควรคุยกับกฤตเมธก่อนว่าจะรวมเป็นฟังก์ชันเดียวกันไหมในรอบถัดไป

### Orthogonality Check

จุดที่ผิด orthogonality ชัดที่สุดคือหน้า prototype ทั้งสามหน้า (upload/rating/search) ผูก business logic (คำนวณ, กรอง, escape ข้อความ) เข้ากับ DOM/UI ไว้ในบล็อก `<script>` เดียวกัน ทำให้:

- เปลี่ยน logic การเรียง/กรอง ต้องเสี่ยงไปแตะโค้ดที่จัดการ DOM ด้วย ทั้งที่สองเรื่องนี้ไม่เกี่ยวกัน
- ทดสอบ logic อย่างเดียวไม่ได้เลยถ้าไม่เปิดเบราว์เซอร์

Lab 7 แก้จุดนี้ในหน้า search โดยแยก pure function ออกเป็น `note-utils.js` ทำให้ logic เปลี่ยนได้โดยไม่กระทบโค้ด DOM และกลับกัน (เปลี่ยนหน้าตาการ์ดไม่กระทบการคำนวณดาว)

### Refactoring Plan

**สรุป Smell + Before/After + Tests + AI workflow ของรอบนี้:** สรุปละเอียดทั้งหมดอยู่ใน [`docs/refactoring-journal.md`](docs/refactoring-journal.md) โดยย่อ — smell ที่เลือกแก้คือ ternary ซ้อน 3 ชั้นในตัวเรียงผลลัพธ์ และ `esc()`/`stars()` ที่ผูกกับ DOM จนทดสอบไม่ได้ (ดู DRY Hunt/Orthogonality ด้านบน) ก่อนแก้ logic ทั้งหมดอยู่ปนกับ DOM ~90 บรรทัดและมี unit test ได้ 0 เคส หลังแก้แยกออกมาเป็น `note-utils.js` 33 บรรทัดที่ทดสอบได้ตรง ๆ พร้อม `node --test` 7 เคสผ่านทั้งหมด และเปิดหน้าเว็บจริงเทียบก่อน/หลังด้วย headless Edge ยืนยันว่าผลค้นหา/กรอง/เรียงไม่เปลี่ยน ส่วน AI workflow ใช้ explain to propose to apply to test ตามที่ใบงานกำหนด — ขั้น "test" นี่เองที่จับได้ว่า Claude ลืมห่อไฟล์ด้วย IIFE จนตัวแปรชนกันตอนโหลดในเบราว์เซอร์ ถ้าข้ามขั้นทดสอบจริงไปเชื่อโค้ดที่ AI เขียนเลยจะไม่มีทางรู้

ลำดับที่วางไว้ถ้ามีเวลาต่อจาก Lab 7:
1. ทำแบบเดียวกันกับหน้า upload และ rating คือแยก pure function ออกจาก DOM code
2. รวม logic "แสดงดาว" ของหน้า search กับหน้า rating เป็นฟังก์ชันเดียวกันใน `note-utils.js` ถ้าทีมตกลงรูปแบบการแสดงผลร่วมกันได้
3. ตั้ง test runner ให้ backend (`services/stats-service`) ด้วย pytest เมื่อมี endpoint ที่ทำงานจริงมากกว่านี้ (ตอนนี้ยังเป็น mock data ล้วน)
