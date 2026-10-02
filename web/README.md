# Web app — หน้าค้นหาโน้ต + gateway

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

ยังไม่มีในรอบนี้: login/สมัคร และอัปโหลดผ่านหน้าเว็บ (slice ถัดไป), favorites, แก้/ลบโน้ต

## ไฟล์

| ไฟล์ | หน้าที่ |
| --- | --- |
| `index.html` | โครงหน้า ฟอร์มค้นหา และ `<dialog>` ตัวอย่าง |
| `app.js` | ผูก DOM กับ `fetch` — อ่านฟอร์ม, เรียก API, เปิด/ปิด preview |
| `search-utils.js` | pure function (สร้าง/อ่าน query string, การ์ดโน้ตพร้อม escape HTML, ข้อความ error) แยกไว้ให้เทสต์ได้ |
| `search-utils.test.js` | unit test ของ `search-utils.js` ด้วย `node --test` |
| `style.css` | หน้าตายืมจาก prototype ค้นหาของ Sprint 1 |
| `nginx.conf` | เสิร์ฟไฟล์ static + proxy `/notes` → notes-service, `/auth/` → auth-service |
| `Dockerfile` | image `nginx-unprivileged` ที่ copy เฉพาะไฟล์ที่ต้องเสิร์ฟ (ไม่มีไฟล์เทสต์/README) |

## วิธีรัน

```bash
docker compose up -d --build
# เปิด http://localhost:8080
```

ทุก request ของหน้าเว็บเป็น URL แบบ relative ไปที่ origin เดียวกัน (`/notes?…`) จึง**ต้องเปิดผ่าน gateway**
ถ้าเปิด `index.html` จากดิสก์ตรง ๆ browser จะบล็อกการเรียก API เพราะ service ไม่ได้เปิด CORS

ถ้ายังไม่มีโน้ตให้ค้น ให้สมัคร + login แล้วอัปโหลดผ่าน API ก่อน (ยิงผ่าน gateway ได้เลย):

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
