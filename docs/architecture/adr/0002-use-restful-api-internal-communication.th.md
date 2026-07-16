# ADR-002: ใช้ RESTful API สำหรับการสื่อสารระหว่าง Service

🌐 [English](./0002-use-restful-api-internal-communication.md) · **ภาษาไทย**

**สถานะ (Status):** Accepted

**บริบท (Context):**
เราเลือกสถาปัตยกรรมแบบ microservices สำหรับ NoteShare ไว้ใน [ADR-001](./0001-tech-stack-selection.th.md) จึงต้องมีกลไกที่เป็นมาตรฐานและเข้าใจง่ายสำหรับการสื่อสารแบบ synchronous ระหว่าง service ทีมพัฒนามีประสบการณ์ทั้ง RESTful API (ผ่าน HTTP/JSON) และ gRPC

**การตัดสินใจ (Decision):**
เราจะใช้ RESTful API พร้อม payload แบบ JSON เป็นกลไกหลักสำหรับการสื่อสารแบบ request-response ระหว่าง microservices ภายในของเรา ทุก service ต้องเปิดเผยความสามารถของตัวเองผ่านสเปก OpenAPI (Swagger) ที่กำหนดไว้ชัดเจน

**ผลที่ตามมา (Consequences):**

*   **ข้อดี (Positive):**
    - ใช้ทักษะเดิมของทีมด้าน HTTP และ JSON ได้ ทำให้ learning curve ต่ำ
    - debug และทดสอบง่ายด้วยเครื่องมือทั่วไป เช่น Postman, Insomnia หรือแม้แต่เว็บเบราว์เซอร์
    - มีไลบรารีและเฟรมเวิร์กรองรับ REST จำนวนมาก ทำให้ implement ได้สะดวก
    - สเปก OpenAPI ทำหน้าที่เป็น "สัญญาที่บังคับใช้ได้" ระหว่าง service
*   **ข้อเสีย/ข้อแลกเปลี่ยน (Negative):**
    - REST บน HTTP/JSON มีความยืดยาวกว่าและอาจมี latency สูงกว่าเล็กน้อยเมื่อเทียบกับโปรโตคอลแบบ binary อย่าง gRPC
    - เราเสียประโยชน์ด้าน strong typing ข้ามขอบเขต service ที่ gRPC มีให้
    - เราต้อง implement กลไกเองสำหรับฟีเจอร์อย่าง service discovery และ client-side load balancing
