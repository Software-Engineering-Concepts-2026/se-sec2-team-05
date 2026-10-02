# ADR-007: กำหนด admin ของ Notes Service ด้วย user ID

[🌐 English](./0007-notes-service-admin-user-ids.md) · **ภาษาไทย**

**สถานะ:** Accepted

**บริบท:**
Issue #17 ต้องการความสามารถ admin สำหรับตรวจและลบรายงานเนื้อหาที่ไม่เหมาะสม แต่ scope ปัจจุบันไม่ควรขยายไปแก้โมเดล authentication และ authorization ที่ `auth-service` เป็นเจ้าของ

**การตัดสินใจ:**
กำหนด admin ของ Notes Service ผ่าน environment variable `ADMIN_USER_IDS` ซึ่งรับ user ID คั่นด้วย comma และยังไม่เพิ่ม field สำหรับ admin หรือ role ใน `auth-service`

**ผลที่ตามมา:**
*   Notes Service ตรวจสิทธิ์ endpoint จัดการรายงานได้โดยไม่ต้องแก้ `auth-service`
*   allowlist ที่อยู่ใน service นี้เป็นแนวทางชั่วคราว และสามารถเปลี่ยนเป็น role-based authorization ในอนาคตได้ โดยเฉพาะเมื่อต่อยอด Issue #18
