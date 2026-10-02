# ADR-006: เสิร์ฟหน้าเว็บและส่งต่อ API ผ่าน nginx gateway ตัวเดียว

[🌐 English](./0006-nginx-web-gateway.md) · **ภาษาไทย**

**สถานะ:** Accepted

**บริบท:**
story ฝั่ง backend ที่ส่งมอบไปแล้วทั้งหมดมีแค่ API ส่วนหน้าใน `prototypes/sprint1/` เป็น mockup ที่ข้อมูล hardcode ไว้ จึงเหลือ acceptance criteria อีกข้อละหนึ่งของสอง story ที่ต้องมีหน้าเว็บจริงถึงจะผ่าน คือ US-11 (#11) "ปิดหน้าตัวอย่างแล้วกลับมาหน้าผลการค้นหาได้โดยไม่เสียตำแหน่ง" และ US-31 (#31) "แสดงชื่อเจ้าของโน้ตให้ผู้ค้นหาเห็นทุกครั้งที่แสดงผลโน้ตนั้น"

หน้าเว็บใน browser จะเรียก API ได้ก็ต่อเมื่ออยู่ origin เดียวกัน หรือ service ตอบ header CORS กลับมา ตอนนี้ `notes-service` (`:5001`) กับ `auth-service` (`:5002`) เป็นคนละ origin และไม่ส่ง header CORS เลย หน้าที่เปิดจากดิสก์ (`file://`) หรือจาก port อื่นจึงโดน browser บล็อกก่อน request จะถึง service

[C4 Container diagram](../c4-container.md) วาง API Gateway ไว้หน้า service สำหรับงานแบบนี้พอดี แต่ [ADR-003](./0003-tracer-bullet-scope.th.md) เลื่อนออกไป และ [ADR-005](./0005-auth-jwt-with-server-side-sessions.th.md) ให้ `notes-service` ตรวจ token ผ่าน `GET /auth/me` ไปก่อน อีกทั้งมี PR ที่เปิดอยู่สองตัว (#68, #69) ที่ conflict กับ `main` ใน `services/notes-service/app.py` การแก้ที่ต้องแตะไฟล์นี้จึงทำให้สอง PR นั้น merge ยากขึ้น

**การตัดสินใจ:**
เพิ่ม container `web` ที่ build จาก `web/Dockerfile` เป็น nginx (`nginxinc/nginx-unprivileged` รันแบบ non-root ที่ port 8080) ซึ่ง

*   เสิร์ฟไฟล์ static ของหน้าเว็บ (`web/index.html`, `app.js`, `search-utils.js`, `style.css`) ที่ `/`
*   ส่งต่อ `/notes` และ `/notes/…` ไปที่ `notes-service:5001` และ `/auth/…` ไปที่ `auth-service:5002` โดยส่ง path, query string และ header `Authorization` เดิมไปครบไม่แก้อะไร
*   รับ body ได้ถึง 22 MB สูงกว่าเพดาน 21 MB ของ `notes-service` เล็กน้อย ไฟล์ที่ใหญ่เกินจะได้ไปโดน `notes-service` ปฏิเสธด้วย `413` แบบ JSON ไม่ใช่หน้า error HTML ของ nginx

หน้าเว็บจึงเรียก URL แบบ relative (`/notes?…`, `/notes/7/preview`) บน origin ของตัวเองได้ และไม่มี service ไหนต้องเปิด CORS ส่วน port 5001 กับ 5002 ยังเปิดไว้เหมือนเดิม `curl` และ smoke test ใน CI ที่มีอยู่จึงใช้ต่อได้

**นี่ยังไม่ใช่ API Gateway ตาม C4 diagram** เพราะไม่ได้ตรวจ JWT ไม่ได้จำกัด rate และไม่ได้รวม response แต่ละ service ยังบังคับกฎของตัวเองอยู่ และ `notes-service` ยังถาม `auth-service` ทุกครั้งที่ต้องตรวจ token (ADR-005) เส้นทางทั้งหมดอยู่ในไฟล์เดียวคือ `web/nginx.conf` วันหลังจะเพิ่มการตรวจ token ที่นี่ หรือเปลี่ยนเป็น gateway ตัวจริงก็ทำได้โดยไม่ต้องแก้หน้าเว็บ

**ทางเลือกที่พิจารณา:**
*   **ใส่ header CORS ในแต่ละ Flask service** — หน้าเว็บจะอยู่ที่ไหนก็ได้ แต่ต้องแก้ `app.py` ของทั้งสอง service รวมถึงไฟล์ของ `notes-service` ที่ #68 กับ #69 conflict กันอยู่แล้ว และทุก service ต้องดูแลรายการ origin ที่อนุญาตให้ตรงกัน ไม่เลือกในตอนนี้
*   **ให้ `notes-service` เสิร์ฟหน้าเว็บเอง** — ชิ้นส่วนน้อยที่สุด แต่ frontend จะกลายเป็นส่วนหนึ่งของ backend service ตัวเดียว `/auth` ก็ยังเป็นคนละ origin และยังต้องแตะ `notes-service/app.py` อยู่ดี ไม่เลือก
*   **เขียน API Gateway เต็มตัวด้วย Flask ตาม C4 diagram เลย** — เป็นสถาปัตยกรรมเป้าหมาย แต่งานเยอะกว่าที่ slice นี้ต้องการมาก และจะซ้ำความผิดพลาดที่ ADR-003 วิจารณ์ไว้ คือสร้าง layer ก่อนมีเส้นทาง end-to-end บาง ๆ ที่วิ่งได้ เลื่อนออกไป และ gateway ตัวนี้คือที่ที่มันจะมาอยู่

**ผลที่ตามมา:**
*   **ด้านบวก:**
    *   browser วิ่ง flow ค้นหา → preview ได้ครบเส้นบน stack จริงที่ `http://localhost:8080` ซึ่งปิด acceptance criteria ข้อสุดท้ายของ #11 และ #31
    *   ไม่ต้องแก้โค้ด service เลย PR #68/#69 ที่เปิดอยู่จึงไม่โดนผลกระทบ
    *   ระบบมีทางเข้าสาธารณะทางเดียวแล้ว เป็นที่ที่จะเพิ่มงานของ gateway (ตรวจ JWT, จำกัด rate) ได้ในอนาคต
    *   smoke test ใน CI ครอบคลุม gateway ด้วย ทั้งไฟล์ static, query string, header `Authorization` และ multipart upload ที่ต้องผ่าน nginx (DK-08)
*   **ด้านลบ:**
    *   `docker compose up` มี container เพิ่มอีกตัว และมีไฟล์ config อีกไฟล์ที่อาจไม่ตรงกับเส้นทางของ service ถ้าเพิ่ม path ระดับบนใหม่อย่าง `/stats` ต้องเพิ่ม `location` ใน `web/nginx.conf` ด้วย
    *   ยังเรียก service ตรง ๆ ที่ 5001/5002 ได้ gateway จึงยังไม่ใช่ขอบเขตความปลอดภัย ตราบใดที่ยังไม่ตรวจ token เอง ทุก service ต้องบังคับ auth ของตัวเองต่อไป
    *   nginx resolve ชื่อ `notes-service` กับ `auth-service` ตอนสตาร์ต ถ้า container ใดไม่มีอยู่ `web` จะสตาร์ตไม่ขึ้นแทนที่จะตอบ `502`
