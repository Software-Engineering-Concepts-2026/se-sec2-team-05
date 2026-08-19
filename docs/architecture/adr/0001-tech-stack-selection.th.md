# ADR-001: การเลือก Core Technology Stack

🌐 [English](./0001-tech-stack-selection.md) · **ภาษาไทย**

**สถานะ (Status):** Accepted

**บริบท (Context):**
NoteShare เป็นเว็บแอปพลิเคชันที่ให้นักศึกษาอัปโหลด ค้นหา และแบ่งปันสรุปเลกเชอร์ ทีมของเราคือนักศึกษา 3 คน ("The Builders") ที่มีประสบการณ์ Python, HTML/CSS/JavaScript พื้นฐาน, Git และ Docker ข้อจำกัดหลักคือกรอบเวลาหนึ่งภาคการศึกษาและความจำเป็นในการทำ prototype และปรับปรุงอย่างรวดเร็ว เราตัดสินใจสร้างระบบเป็น microservices จำนวนน้อย (ดูแผนภาพ container ใน [../README.th.md](../README.th.md)) ดังนั้น stack ที่เลือกต้องรองรับหลาย service ที่ deploy แยกกันได้และสื่อสารกันผ่านเครือข่าย รวมถึงมีที่เก็บไฟล์ที่อัปโหลดแยกต่างหาก

**การตัดสินใจ (Decision):**
เราตัดสินใจใช้ core technology stack ดังนี้:

- **Frontend:** React (single-page application) ร่วมกับ Vite
- **Backend:** Python + Flask จัดเป็น microservices จำนวนน้อย (API Gateway, User & Auth, Notes, Stats)
- **Database:** PostgreSQL เป็นฐานข้อมูลเชิงสัมพันธ์หลัก และใช้ object storage แบบ S3-compatible สำหรับเก็บไฟล์โน้ตที่อัปโหลด
- **Packaging & Deployment:** ใช้ Docker และ Docker Compose ในการพัฒนาบนเครื่อง; backend รันเป็น container บน cloud host (เช่น Render/Railway) และ frontend deploy บน Vercel

**ผลที่ตามมา (Consequences):**

*   **ข้อดี (Positive):**
    - Python/Flask ตรงกับทักษะเดิมของทั้งทีมและเนื้อหาในวิชา ทำให้ learning curve ต่ำ
    - Component model ของ React เหมาะกับ UI แบบโต้ตอบและ mobile-first ของ NoteShare (ค้นหา กรอง ดูตัวอย่าง อัปโหลด) และเป็นทักษะที่ใช้งานในตลาดได้จริง
    - โมเดลเชิงสัมพันธ์ของ PostgreSQL เข้ากับความสัมพันธ์ที่ชัดเจนระหว่างผู้ใช้ โน้ต รายวิชา และเครดิตได้ดี
    - การเก็บไฟล์ขนาดใหญ่ไว้ใน object storage แทนฐานข้อมูล ทำให้ฐานข้อมูลเล็กและการดาวน์โหลดเร็วและประหยัด
    - Docker ทำให้ทุกคนในทีมมีสภาพแวดล้อมเหมือนกัน และแต่ละ service build/deploy แยกกันได้
*   **ข้อเสีย/ข้อแลกเปลี่ยน (Negative):**
    - โครงสร้างแบบ microservices เพิ่มภาระด้านการดูแล (หลาย service, การเรียกข้าม service, ชิ้นส่วนที่ต้องดูแลมากขึ้น) ซึ่งหนักสำหรับทีม 3 คนในหนึ่งภาคการศึกษา เรายอมรับเพื่อฝึกการแยก service และลดต้นทุนด้วยการจำกัดจำนวน service ให้น้อย
    - การแยก frontend (Vercel) กับ backend (container host) ทำให้มีปลายทาง deploy สองที่ ต้องตั้งค่า CORS และ environment variable อย่างระมัดระวัง
    - Free tier ของ host อย่าง Render และ Vercel อาจมี cold start และข้อจำกัดทรัพยากรที่ต้องวางแผนรับมือตอน demo
    - เราเริ่มด้วย PostgreSQL อินสแตนซ์เดียวที่ใช้ร่วมกัน (แยก schema ต่อ service) แทน database-per-service เต็มรูปแบบ เพื่อแลกความเรียบง่ายกับการแยกข้อมูลที่ไม่เข้มงวดนัก และสามารถแยกฐานข้อมูลภายหลังได้หาก service ใดต้องการ

**ทางเลือกอื่นที่พิจารณา (Alternatives):**

*   **Monolith vs. Microservices:**
    - เราพิจารณาสร้าง NoteShare เป็น monolithic Flask application เดียว ซึ่งจะง่ายกว่าสำหรับทีม 3 คนในการพัฒนา ทดสอบ และ deploy เป็นหน่วยเดียว
    - แต่เราเลือกแยกเป็น microservices อยู่ดี เพื่อฝึกการทำ service decomposition เป็นเป้าหมายการเรียนรู้ โดยยอมรับภาระด้านการดูแลที่ระบุไว้แล้วในข้อ "ข้อเสีย/ข้อแลกเปลี่ยน (Negative)" ข้างต้น (หลาย service, การเรียกข้าม service, และชิ้นส่วนที่ต้องดูแลมากขึ้นสำหรับทีม 3 คน)

**การตัดสินใจที่เกี่ยวข้อง (Related decisions):**

- [ADR-002: ใช้ RESTful API สำหรับการสื่อสารระหว่าง Service](./0002-use-restful-api-internal-communication.th.md)
