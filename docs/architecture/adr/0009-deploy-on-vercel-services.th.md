# ADR-009: Deploy บน Vercel ด้วย Services, Neon Postgres และ Vercel Blob แบบ private

[🌐 English](./0009-deploy-on-vercel-services.md) · **ภาษาไทย**

**สถานะ:** Accepted · เพดานอัปโหลด 4 MB ถูกแทนด้วย ADR-012 (อัปโหลดตรงเข้า Blob ได้ 10 MB)

**บริบท:**
ทีมต้องการ URL สาธารณะของ NoteShare และเลือก Vercel · ADR-001 วางแผนไว้ว่า backend เป็น container บน Render/Railway และ frontend บน Vercel แต่สิ่งที่สร้างจริงเป็น `docker compose` ก้อนเดียว คือ Flask 3 service, PostgreSQL, ไฟล์บน volume ของดิสก์ (ADR-003) และ gateway nginx (ADR-006) · บน Vercel แต่ละ backend รันเป็น Vercel Function ซึ่งไม่เก็บ state และปิดตัวเองเมื่อไม่มีคนใช้ ของที่เขียนลงดิสก์จึงหาย และ body ของ request/response รับได้ไม่เกิน 4.5 MB

**การตัดสินใจ:**
*   deploy ทั้ง 4 ส่วนเป็น **Vercel Services** ใน project เดียว (`vercel.json` ที่ root ของ repo): `web` (ไฟล์ static ใน `web/`), `notes`, `auth` และ `stats` (Flask) · rewrite ระดับบนสุดแทน route ของ nginx แบบตัวต่อตัว และ `notes`/`stats` เรียก `auth` ผ่าน **service binding** ภายในที่ใส่ค่าให้ `AUTH_SERVICE_URL`
*   ใช้ **Neon Postgres** จาก Vercel Marketplace เป็น `DATABASE_URL` · service แปลง URL แบบ `postgres://`/`postgresql://` เป็น `postgresql+psycopg://` เพราะติดตั้งไว้แค่ psycopg 3 และเปิด `pool_pre_ping` เพราะ Neon ปิด connection ที่ว่างนาน
*   เก็บไฟล์โน้ตและรูปตัวอย่างใน **Vercel Blob แบบ private** ผ่าน `BlobFileStorage` ใหม่ (`NOTES_STORAGE_BACKEND=blob` + `BLOB_READ_WRITE_TOKEN`) · การดาวน์โหลดยังผ่าน notes-service การตรวจสิทธิ์และตัวนับจึงทำงานเหมือนเดิม
*   ลดเพดานอัปโหลดจาก 20 MB เหลือ **4 MB** ทุกจุด (service, ฟอร์มหน้าเว็บ, nginx) ให้ request อัปโหลดทั้งก้อนไม่เกิน 4.5 MB · ยังไม่ทำการอัปโหลดตรงจาก browser ไป Blob เพราะต้องมี endpoint ออก token และแก้ทั้งหน้าอัปโหลดและ API
*   `docker compose` ยังเป็นทางรันบนเครื่องและใน CI เหมือนเดิม ใช้ดิสก์และ nginx ต่อไป

**ผลที่ตามมา:**
*   ค่าลับ (`AUTH_JWT_SECRET`, รหัสผ่านฐานข้อมูล, token ของ Blob) อยู่ใน environment variable ของ Vercel แทนไฟล์ compose ที่ commit ไว้ และเว็บได้ HTTPS
*   อัปโหลดโน้ตที่ใหญ่กว่า 4 MB ไม่ได้อีก ทั้งบน Vercel และบนเครื่อง
*   notes-service ต้องพึ่ง `vercel` Python SDK ซึ่งติดเข้าไปใน Docker image ด้วยแม้ compose จะไม่ได้ใช้ Blob
*   ยังไม่มีเครื่องมือ migration: บน Neon ถ้าเพิ่มคอลัมน์ต้องสร้างเองหรือล้างฐานข้อมูล
*   หลังว่างนาน request แรกช้าลงเพราะต้องเปิด instance ใหม่ และอยู่ใต้ข้อจำกัดของแพ็กเกจ Hobby ที่ใช้ฟรี
