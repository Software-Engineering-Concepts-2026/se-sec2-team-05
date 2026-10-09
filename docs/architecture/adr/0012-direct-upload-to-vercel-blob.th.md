# ADR-012: อัปโหลดไฟล์โน้ตตรงเข้า Vercel Blob

[🌐 English](./0012-direct-upload-to-vercel-blob.md) · **ภาษาไทย**

**สถานะ:** Accepted

**บริบท:**
NFR-003 และ NFR-006 ให้ไฟล์โน้ตใหญ่ได้ถึง 10 MB · ADR-009 ลดเพดานเหลือ 4 MB ทุกจุด เพราะ Vercel Function รับ body ของ request ได้ไม่เกิน 4.5 MB และฟอร์มอัปโหลดส่งไฟล์ผ่าน notes-service · ADR-009 พักเรื่องอัปโหลดตรงจาก browser ไป Blob ไว้ก่อน เพราะต้องมี endpoint ออก token และแก้ทั้งหน้าอัปโหลดและ API · Vercel Python SDK (`vercel` 0.11.4) อ่าน/เขียน Blob ได้แต่ออก client token สำหรับอัปโหลดไม่ได้ มีแค่แพ็กเกจ JavaScript `@vercel/blob` ที่ทำได้

**การตัดสินใจ:**
*   บน Vercel (`NOTES_STORAGE_BACKEND=blob`) browser ส่งไฟล์**ตรงเข้า Vercel Blob**:
    1.  `POST /notes/uploads` (ต้อง login) พร้อมชื่อ ชนิด และขนาดของไฟล์ · notes-service ตรวจแล้วตอบ **client token** ที่ใช้ได้กับ pathname เดียวใต้ `uploads/<user id>/` ชนิดนั้นเท่านั้น ไม่เกิน 10 MB ห้ามเขียนทับ อายุ 10 นาที
    2.  หน้าอัปโหลด PUT ไฟล์ไปที่ `https://vercel.com/api/blob/` ด้วย token นั้น ใช้ `XMLHttpRequest` เพื่อให้มีแถบความคืบหน้า
    3.  `POST /notes` แบบ JSON พร้อมฟิลด์ในฟอร์ม `file_name` และ `upload_pathname` · notes-service รับเฉพาะ pathname ใต้ `uploads/<id>/` ของผู้เรียกเอง อ่านขนาดและชนิดจาก Blob เอง (ไม่เชื่อค่าจาก client) ลบไฟล์ทิ้งถ้าผิดกติกา และตอบ `409` ถ้าไฟล์นั้นเป็นของโน้ตอื่นไปแล้ว
*   notes-service **เซ็น client token เอง** (`storage.generate_client_token`) รูปแบบเดียวกับ `generateClientTokenFromReadWriteToken` ใน `@vercel/blob` 2.8.0 คือ HMAC-SHA256 ของ payload JSON ที่เข้ารหัส base64 โดยใช้ `BLOB_READ_WRITE_TOKEN` เป็นกุญแจ · เทียบกับฟังก์ชัน JavaScript ตัวจริงแล้วได้ token เดียวกันทุกไบต์ · read-write token ไม่ออกจากเซิร์ฟเวอร์
*   หน้าเว็บส่ง PUT เองโดยไม่ใช้ library ของ JavaScript: header ชุดเดียวกับที่ `put` ของ `@vercel/blob/client` ส่ง หน้าเว็บจึงยังเป็นไฟล์ static ล้วนและไม่พึ่ง CDN
*   บน compose (`LocalFileStorage`) `POST /notes/uploads` ตอบ `mode: "form"` หน้าเว็บส่งฟอร์ม multipart เหมือนเดิม และเพดานกลับเป็น **10 MB** (nginx `client_max_body_size 11m`)
*   บน Vercel ทางฟอร์ม multipart ยังเหลือไว้ให้ client อื่นของ API แต่จำกัด 4 MB ให้ request ไม่ชนเพดาน 4.5 MB ของแพลตฟอร์ม

**ผลที่ตามมา:**
*   โน้ตไม่เกิน 10 MB อัปโหลดได้ทั้งบน Vercel และ compose ตาม NFR-003/006 และมีแถบความคืบหน้าจริง
*   รูปแบบ token ลอกมาจาก `@vercel/blob` ถ้า Vercel เปลี่ยน การอัปโหลดบน Vercel จะพังจนกว่าจะแก้ `generate_client_token` ตาม · BU-01 และการเทียบกับแพ็กเกจจริงบอกว่าต้องดูตรงไหน
*   ถ้า browser ได้ token และอัปโหลดไปแล้วแต่ไม่เรียก `POST /notes` (ปิดแท็บ) ไฟล์จะค้างใน Blob ใต้ `uploads/<id>/` โดยไม่มีโน้ต · จำนวนถูกจำกัดด้วยอายุและขนาดของ token และลบได้ด้วยการ list prefix นั้น · ตอนนี้ยังไม่มีอะไรลบให้อัตโนมัติ
*   ทดสอบการอัปโหลดตรงครบทั้งเส้นได้บน deployment จริงของ Vercel เท่านั้น ชุด pytest ใช้ Blob client ปลอม
