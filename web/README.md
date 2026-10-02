# Web app — ค้นหา, เข้าสู่ระบบ, อัปโหลดโน้ต + gateway

หน้าเว็บตัวจริงตัวแรกของ NoteShare ที่ต่อกับ API จริง (ต่างจาก `prototypes/sprint1/` ที่เป็น mockup ข้อมูล hardcode
และเก็บไว้เป็นหลักฐาน Lab 4 ไม่ได้แก้) เสิร์ฟผ่าน nginx ที่ทำหน้าที่ gateway ด้วย ดูเหตุผลใน
[ADR-006](../docs/architecture/adr/0006-nginx-web-gateway.th.md)

## ทำอะไรได้

- **ค้นหา/กรองโน้ต** ผ่าน `GET /notes` จริง: คำค้น (`q`), คณะ, ชั้นปี 1–8, หัวข้อ (`topic`), ช่วงวันที่เรียน,
  ประเภทไฟล์ (PDF/PNG/JPG เลือกได้หลายแบบ) และการเรียง (`new`, `old`, `class_date`, `title`)
  - ตัวกรองถูกเก็บใน URL — reload หรือกด back แล้วได้ผลค้นหาเดิม แชร์ลิงก์ผลค้นหาได้
  - API ส่ง `count` เป็นจำนวนในหน้านั้น ไม่ใช่ยอดรวม หน้าเว็บจึงใช้ปุ่ม "โหลดเพิ่ม" ทีละ 20 รายการ
    แทนเลขหน้า และซ่อนปุ่มเมื่อได้หน้าที่ไม่เต็ม
  - ค่าที่ API ไม่รับ (`400 invalid_filter`) แสดงเป็นข้อความในหน้าพร้อมชื่อช่องที่ผิด ไม่ใช้ `alert()`
- **ชื่อผู้อัปโหลดอยู่บนการ์ดทุกใบและในหน้าตัวอย่าง** — US-31 AC3 (#31)
- **ดูตัวอย่างก่อนดาวน์โหลด** — กด "ดูตัวอย่าง" แล้วเปิด `<dialog>` ทับผลค้นหา แสดงภาพจาก
  `/notes/<id>/preview` พร้อมปุ่มดาวน์โหลดไฟล์เต็ม ปิดได้ทั้งปุ่ม ✕, Esc และคลิกฉากหลัง ผลค้นหาและตำแหน่ง
  scroll ไม่ถูกแตะ และ focus กลับไปที่ปุ่มที่กดเปิด — US-11 AC3 (#11)
  - preview ที่สร้างไม่ได้ (`422 preview_unavailable`) หรือโน้ตถูกลบ (`404`) แสดงเหตุผลแทนรูปแตก
- **สมัครสมาชิกและเข้าสู่ระบบ** ที่ `/login.html` (แท็บ "เข้าสู่ระบบ" / "สมัครสมาชิก", เปิดแท็บสมัครตรง ๆ ด้วย `#register`)
  ผ่าน `POST /auth/register` และ `POST /auth/login` — US-05 (#5), US-06 (#6)
  - เหตุผลที่ผิดแสดงใต้ช่องนั้นจาก `fields` ที่ auth-service ส่งมา (เช่น ต้องเป็นอีเมล `@up.ac.th`, รหัสผ่านอย่างน้อย 8 ตัว)
  - สมัครสำเร็จแล้วเข้าสู่ระบบต่อให้ทันทีด้วยข้อมูลชุดเดิม ไม่ต้องกรอกซ้ำ
  - login ผิดได้ข้อความกลาง ๆ จาก service ("อีเมลหรือรหัสผ่านไม่ถูกต้อง") ไม่บอกว่าผิดช่องไหน (AC3 ของ #6)
  - เข้าสู่ระบบแล้วกลับไปหน้าเดิมตาม `?next=` ซึ่งรับแค่ `/`, `/index.html`, `/upload.html` ของเว็บนี้เท่านั้น
    ลิงก์ที่ชี้ไปเว็บอื่นจะพากลับหน้าค้นหาแทน (กัน open redirect)
- **แถบเมนูบนทุกหน้า** แสดงชื่อผู้ใช้กับปุ่ม "ออกจากระบบ" หรือปุ่ม "เข้าสู่ระบบ" ถ้ายังไม่ได้เข้า · ออกจากระบบเรียก
  `POST /auth/logout` ให้ token ใช้ไม่ได้ทันทีที่ฝั่ง server (ADR-005) แล้วล้างใน browser
- **อัปโหลดโน้ต** ที่ `/upload.html` ผ่าน `POST /notes` แบบ multipart — US-08 (#8), US-31 (#31)
  - ยังไม่ได้เข้าสู่ระบบจะถูกพาไปหน้าเข้าสู่ระบบก่อน แล้วกลับมาหน้านี้
  - ฟอร์มตรวจทุกช่องก่อนส่งตามกฎเดียวกับ `services/notes-service/validation.py` (ช่องบังคับ, ความยาว, ชั้นปี 1–8,
    วันที่, PDF/PNG/JPG ไม่เกิน 20 MB) จะได้ไม่ต้องส่งไฟล์ใหญ่ไปแล้วค่อยรู้ว่าผิด · service ยังตรวจซ้ำทุกครั้ง
    และถ้าผลไม่ตรงกัน หน้าเว็บจะแสดงคำตอบของ service
  - หน้าบอกล่วงหน้าว่าโน้ตจะแสดงชื่อผู้อัปโหลดอะไร (ชื่อจากบัญชี ไม่มีช่องให้กรอกชื่อเอง)
  - อัปโหลดเสร็จแล้วแสดง **รหัสแก้ไขโน้ต** (`edit_token`) พร้อมปุ่มคัดลอกและคำเตือนว่าเห็นได้ครั้งเดียว เพราะ service เก็บไว้แค่ hash
    (ADR-004) · กด "อัปโหลดอีกไฟล์" แล้วรหัสหายจากหน้าจอ
  - ถ้า session ถูกเพิกถอนระหว่างกรอก (เช่น ออกจากระบบจากอีกแท็บ) จะได้ `401` แล้วแสดงลิงก์เข้าสู่ระบบใหม่ โดยข้อมูลที่กรอกยังอยู่

ยังไม่มีในรอบนี้: แก้/ลบโน้ตด้วยรหัสแก้ไข (US-19/US-20), favorites (US-15), ความคิดเห็น (US-14)

## เก็บ token ไว้ที่ไหน

หลังเข้าสู่ระบบ หน้าเว็บเก็บ `access_token`, `expires_at` และชื่อผู้ใช้ไว้ใน **`sessionStorage`** (key `noteshare.session`)

- **ไม่ใช้ `localStorage`** เพราะ token อยู่ได้ถึง 8 ชั่วโมง (`AUTH_TOKEN_TTL_HOURS`) ถ้าเก็บแบบข้ามการปิด browser
  เครื่องที่ใช้ร่วมกัน (เช่นห้องคอมพิวเตอร์ของมหาวิทยาลัย) จะยัง login ค้างอยู่หลังผู้ใช้ปิดหน้าต่างไป · `sessionStorage` หายเมื่อปิดแท็บ
  แต่ยังอยู่เมื่อเปลี่ยนหน้าในแท็บเดิม ซึ่งพอสำหรับเว็บหลายหน้าแบบนี้
- **ไม่เก็บไว้ในหน่วยความจำอย่างเดียว** เพราะเว็บนี้แยกเป็นหลายหน้า เปลี่ยนหน้าแล้ว token จะหาย
- **ข้อจำกัดที่ยอมรับ:** script ที่รันบนหน้าเดียวกันอ่าน `sessionStorage` ได้ ถ้ามีช่องโหว่ XSS token จะรั่วได้ จึงต้อง escape ทุกค่าที่มาจากผู้ใช้
  (`escapeHtml` ใน `search-utils.js` และ `textContent` ในแถบเมนู/หน้าอัปโหลด) · ทางที่ปลอดภัยกว่าคือ cookie แบบ `HttpOnly`
  แต่ต้องแก้ auth-service และเพิ่มการกัน CSRF จึงยังไม่ทำในรอบนี้
- session ที่หมดอายุตาม `expires_at` หรืออ่านไม่ออกจะถูกลบทิ้งตอนโหลดหน้า และ API ที่ตอบ `401` ทำให้หน้าเว็บล้าง session ด้วย

## ไฟล์

| ไฟล์ | หน้าที่ |
| --- | --- |
| `index.html` | โครงหน้า ฟอร์มค้นหา และ `<dialog>` ตัวอย่าง |
| `app.js` | ผูก DOM กับ `fetch` — อ่านฟอร์ม, เรียก API, เปิด/ปิด preview |
| `search-utils.js` | pure function (สร้าง/อ่าน query string, การ์ดโน้ตพร้อม escape HTML, ข้อความ error) แยกไว้ให้เทสต์ได้ |
| `search-utils.test.js` | unit test ของ `search-utils.js` ด้วย `node --test` |
| `login.html`, `login.js` | หน้าเข้าสู่ระบบ/สมัครสมาชิก |
| `upload.html`, `upload.js` | หน้าอัปโหลดโน้ตและกล่องรหัสแก้ไข |
| `site.js` | โค้ด DOM ที่ทุกหน้าใช้ร่วมกัน: แถบเมนูบน, การเข้าถึง `sessionStorage`, `fetchJson`, การแสดง error ใต้ช่อง |
| `session-utils.js` | pure function ของสถานะ login (อ่าน/บันทึก/ล้าง session, ตรวจวันหมดอายุ, ตรวจ `?next=`, ข้อความ error ของ auth) |
| `upload-utils.js` | pure function ของหน้าอัปโหลด (ตรวจฟอร์มตามกฎของ notes-service, เลือกฟิลด์ที่ส่ง, ข้อความ error) |
| `session-utils.test.js`, `upload-utils.test.js` | unit test ของสองไฟล์ข้างบนด้วย `node --test` |
| `style.css` | หน้าตายืมจาก prototype ค้นหาของ Sprint 1 ใช้ร่วมทุกหน้า |
| `nginx.conf` | เสิร์ฟไฟล์ static + proxy `/notes` → notes-service, `/auth/` → auth-service |
| `Dockerfile` | image `nginx-unprivileged` ที่ copy เฉพาะไฟล์ที่ต้องเสิร์ฟ (ไม่มีไฟล์เทสต์/README) |

## วิธีรัน

```bash
docker compose up -d --build
# เปิด http://localhost:8080
```

ทุก request ของหน้าเว็บเป็น URL แบบ relative ไปที่ origin เดียวกัน (`/notes?…`) จึง**ต้องเปิดผ่าน gateway**
ถ้าเปิด `index.html` จากดิสก์ตรง ๆ browser จะบล็อกการเรียก API เพราะ service ไม่ได้เปิด CORS

ถ้ายังไม่มีโน้ตให้ค้น ให้สมัครที่ http://localhost:8080/login.html#register แล้วอัปโหลดที่ `/upload.html`
หรือยิง API ผ่าน gateway ตรง ๆ ก็ได้ (เช่นตอนเตรียมข้อมูลทีละหลายโน้ต):

```bash
curl -X POST http://localhost:8080/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"me@up.ac.th","password":"choose a password","display_name":"My Name"}'
token=$(curl -s -X POST http://localhost:8080/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"me@up.ac.th","password":"choose a password"}' | jq -r .access_token)
curl -X POST http://localhost:8080/notes -H "Authorization: Bearer $token" \
  -F title='Linked List' -F subject_name='Data Structures' -F subject_code=CS201 \
  -F faculty=ICT -F year_level=2 -F lesson='Linked List' -F 'file=@note.pdf;type=application/pdf'
```

> บน Windows ถ้าส่งชื่อภาษาไทยผ่าน `curl -F` ใน Git Bash ตัวอักษรอาจกลายเป็น `?` ตั้งแต่ฝั่ง client
> (เจอตอนทดสอบ) — ไม่ใช่บั๊กของ service · ส่งจาก Python/Postman หรือ terminal ที่เป็น UTF-8 แทน

## เทสต์

```bash
cd web && node --test
```

ไม่มี dependency และไม่มี `package.json` เหมือน `prototypes/sprint1/` · CI รันทั้งชุดนี้ใน job `js-tests`
และเช็ค gateway บน stack จริงใน step `Web gateway serves the page and proxies the APIs` (DK-08 ใน
[test plan](../docs/testing/readme.md))
