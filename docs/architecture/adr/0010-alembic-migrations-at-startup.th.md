# ADR-010: รัน migration ด้วย Alembic ตอน service สตาร์ต

[🌐 English](./0010-alembic-migrations-at-startup.md) · **ภาษาไทย**

**สถานะ:** Accepted

**บริบท:**
notes-service และ auth-service สร้างตารางด้วย `Base.metadata.create_all` (ADR-003) ซึ่งสร้างได้แค่ตารางที่ยังไม่มี เพิ่มคอลัมน์ให้ตารางที่มีอยู่แล้วไม่ได้ · บนเครื่องจึงต้อง `docker compose down -v` ทุกครั้งที่ schema เปลี่ยน และ ADR-009 ยังเหลือปัญหาเดียวกันบน Neon คือถ้าเพิ่มคอลัมน์ต้องสร้างเองหรือล้างฐานข้อมูล production · Vercel ไม่มีขั้นตอนให้รันคำสั่งก่อน service สตาร์ต และอาจมีหลาย instance (gunicorn worker, cold start พร้อมกัน) สตาร์ตบนฐานข้อมูลเดียวกันในเวลาเดียวกัน · ทั้งสอง service ใช้ฐานข้อมูล Postgres ก้อนเดียวกัน

**การตัดสินใจ:**
*   ใช้ **Alembic** ใน notes-service และ auth-service · แต่ละ service มีโฟลเดอร์ `migrations/` และตาราง version ของตัวเอง (`alembic_version_notes`, `alembic_version_auth`) จึงอยู่ฐานข้อมูลเดียวกันได้โดยไม่ยุ่งกับประวัติของอีกฝั่ง · `env.py` เทียบและสร้างเฉพาะตารางที่อยู่ใน metadata ของ service ตัวเอง
*   **migrate ตอนสตาร์ต**: `build_session_factory()` เรียก `upgrade_to_head()` (`migrate.py` ใน notes-service, `auth_migrate.py` ใน auth-service) แทน `create_all` · ทำงานเหมือนกันทั้งใน compose, บน Vercel และในเทสต์ ไม่ต้องมีขั้นตอน deploy แยก
*   บน Postgres ถือ **advisory lock ระดับ transaction** (`pg_advisory_xact_lock` คนละเลขต่อ service) ตลอดการ migrate ให้ instance ที่สตาร์ตพร้อมกันรอกันทีละตัว ไม่แย่งกัน `CREATE TABLE`
*   revision แรก `0001` เป็น **baseline** ของ schema ที่ `create_all` สร้างไว้ · ฐานข้อมูลที่มีตารางของ service อยู่แล้วแต่ไม่มีตาราง version (volume ของ compose เดิม, Neon) จะถูก **stamp** เป็น `0001` แล้วค่อย upgrade ต่อ ข้อมูลเดิมไม่หาย
*   schema ที่เปลี่ยนต่อจากนี้ให้เขียนเป็น revision ใหม่ด้วย `alembic revision --autogenerate` จากโฟลเดอร์ของ service (`alembic.ini` ในนั้นมีไว้ใช้กับ CLI เท่านั้น) · ห้ามแก้ `0001`

**ผลที่ตามมา:**
*   คอลัมน์ใหม่ขึ้นไปถึง Neon ใน deploy รอบถัดไปโดยไม่ต้องล้างฐานข้อมูล
*   ทุกครั้งที่สตาร์ตจะเช็คเวอร์ชันใน transaction เดียว ทำให้ cold start ช้าลงเล็กน้อย
*   ถ้าฐานข้อมูลจากก่อนมี Alembic มี schema ไม่ตรงกับ baseline ก็จะถูก stamp อยู่ดีแล้วไปล้มที่ revision ถัดไป · ฐานข้อมูลที่มีอยู่ทั้งหมดสร้างจาก models ชุดเดียวกัน จึงไม่น่าเกิด
*   เทสต์สร้างตารางผ่าน migration ชุดเดียวกัน และ MG-01 (`alembic check`) จะล้มถ้ามีคนแก้ models โดยไม่เพิ่ม revision · MG-06 (สตาร์ตพร้อมกัน) รันเฉพาะบน Postgres
*   Docker image ทั้งสองตัวต้อง copy ไฟล์ migration ไปด้วย และทั้งสอง service พึ่ง `alembic`
