# ADR-014: Gateway ตรวจ login ก่อนส่งต่อ request

[🌐 English](./0014-gateway-checks-login.md) · **ภาษาไทย**

**สถานะ:** Accepted

**บริบท:**
C4 Container diagram วาง API Gateway ไว้หน้า service และ ADR-006 จดไว้ว่า gateway nginx "ยังไม่ได้ตรวจ JWT" · ตั้งแต่นั้นระบบโตขึ้นเป็นราว 30 route ใน 3 service และแต่ละ service ตรวจ login เอง: notes-service กับ stats-service ถาม auth-service ที่ `GET /auth/me` (ADR-005) ส่วน route ที่เปิดให้ทุกคน (ค้นหา, หน้าโน้ต, ภาพตัวอย่าง, ดาวน์โหลด, รายการความคิดเห็น, ภาพรวมสถิติ) ตอบใครก็ได้ · บน Vercel (ADR-009) rewrite ระดับบนของ `vercel.json` แทน nginx และส่งต่อทุกอย่างเหมือนกัน request ที่ไม่มี token ใช้ได้ของ route ที่ต้อง login จึงวิ่งไปถึง function ของ Flask ก่อนถึงถูกปฏิเสธ

บน Vercel โค้ดที่รันก่อน rewrite ได้มีแค่ Routing Middleware และต้องลองบน preview จริงสองเรื่อง เพราะเอกสารไม่ได้พูดถึงกรณี project ที่ใช้ `services`:
*   ไฟล์ `middleware.ts` ที่ root ของ repo **ถูกเมิน** เมื่อใช้ services (build มีแค่ function ของ Flask สามตัว) ต้องประกาศผ่าน `"proxy": { "entrypoint": … }` ใน `vercel.json` ถึงจะทำงาน
*   middleware ถูก build เป็น CommonJS จึง import ไฟล์ `.mjs` ไม่ได้ (ล้มตอนรันด้วย `ERR_REQUIRE_ESM`)

Routing Middleware ใช้ service binding ไม่ได้ จึงเรียก auth-service ทางภายในไม่ได้

**การตัดสินใจ:**
*   มีตารางเดียวบอกว่า method + path ไหนต้อง login ไหนเปิด · ต้อง login: อัปโหลดและขอสิทธิ์อัปโหลดตรง (`POST /notes/uploads`, ADR-012), แก้และลบโน้ต (`PATCH`/`DELETE /notes/<id>` เจ้าของเท่านั้นตั้งแต่ ADR-013), รายการโปรดทั้งดูและกด, โน้ตของฉัน, ขอบคุณ, ให้คะแนน, รายงาน, เขียน/ลบความคิดเห็น, สถิติรายโน้ต และ route รายงานของผู้ดูแล · ที่เหลือรวม `/auth/*` และ `GET /stats` เปิดหมด · header `X-Note-Token` แบบเดิมไม่มีผลอะไร
*   **docker compose:** `web/nginx.conf` เก็บตารางเป็น `map` สองชั้น และทุก location ของ API เรียก `auth_request` ไปที่ `auth-service /auth/me` · แต่ละ location ใช้ `set` คำนวณ rule จาก request หลักไว้ก่อน เพราะใน subrequest `$uri` คือ path ของ subrequest เอง · route ที่เปิดตอบ subrequest ด้วย `204` โดยไม่ถาม auth-service
*   **Vercel:** `gateway/proxy.ts` เป็น Routing Middleware ที่ประกาศใน `"proxy"` ของ `vercel.json` โดย matcher จับแค่ `/notes` และ `/reports` · logic อยู่ใน `gateway/rules.js` (CommonJS) ซึ่งเรียก `/auth/me` ผ่าน URL สาธารณะของ deployment เดียวกัน ส่ง `Authorization` ต่อ พร้อม cookie และ `x-vercel-protection-bypass` ให้ผ่าน Deployment Protection บน preview ได้ด้วย
*   gateway ทั้งสองตอบเหมือน service: `401 {"error": "unauthorized"}` พร้อม `WWW-Authenticate: Bearer` และ `503 {"error": "auth_unavailable"}` เมื่อ auth-service ล่มหรือตอบอย่างอื่นที่ไม่ใช่ 2xx/401 หน้าเว็บจึงขึ้นข้อความเดิม
*   gateway ตรวจแค่ว่า login ใช้ได้ สิทธิ์ผู้ดูแล, ความเป็นเจ้าของโน้ต และ "ให้คะแนนได้หลังเปิดดู" ยังตัดสินที่ service ซึ่งตรวจเองครบเหมือนเดิม (ป้องกันสองชั้น)
*   `gateway/cases.json` เก็บทุก route สาธารณะพร้อมผลที่คาด · `node --test` เทียบ `rules.js` กับไฟล์นี้ และ `src/tests/test_gateway_rules.py` เทียบ map ของ nginx, matcher ใน `vercel.json` และตรวจว่าทุก route ของ Flask ทั้งสาม service มีอยู่ใน cases

**ทางเลือกที่พิจารณา:**
*   **ตรวจลายเซ็น JWT ที่ gateway ด้วย `AUTH_JWT_SECRET`:** ไม่ต้องเรียกผ่าน network แต่มองไม่เห็น session ที่ถูก logout ไปแล้ว (ADR-005) token ที่ logout แล้วจะผ่าน gateway และ gateway จะขัดกับ auth-service อีกทั้งต้องเอา secret ไปไว้อีกที่ ไม่เลือก
*   **เขียน gateway เป็น service แยกด้วย Flask:** ตรงกับกล่องใน C4 ที่สุด แต่บน Vercel ต้องเพิ่ม function ตัวที่สี่และทุก request ต้องผ่านอีกทอด ซ้ำกับสิ่งที่ nginx และ Routing Middleware ทำได้อยู่แล้ว ไม่เลือก
*   **ตรวจทุก request รวม route ที่เปิด:** token หมดอายุบนหน้าค้นหาจะกลายเป็น error ทั้งที่ service ตั้งใจถือว่า "ยังไม่ login" ไม่เลือก

**ผลที่ตามมา:**
*   request ที่ไม่มี login ใช้ได้ของ route ที่ต้อง login หยุดที่ gateway และ gateway ทั้งสองตอบเหมือนกัน · smoke test ใน CI ตรวจบน compose รวมกรณี `503` ตอนหยุด auth-service
*   route ที่ต้อง login ถาม auth-service เพิ่มอีกครั้ง (subrequest ของ nginx หรืออีกหนึ่ง request ผ่าน routing สาธารณะของ Vercel) · route ที่เปิดไม่เปลี่ยน และบน Vercel หน้าเว็บ static ไม่ผ่าน middleware เลย
*   route ใหม่ต้องเพิ่ม 3 ที่: `gateway/cases.json`, `gateway/rules.js` และ map ใน `web/nginx.conf` ขาดที่ไหนเทสต์ล้ม
*   ใน compose ยังเรียก service ตรง ๆ ที่ 5000–5002 ได้ service จึงต้องตรวจเองต่อไป · บน Vercel service ถูกเรียกได้ทาง rewrite เท่านั้นซึ่งอยู่หลัง middleware
*   การอัปโหลดยังผ่าน middleware ได้: ไฟล์ 4 MB (เพดานของ notes-service) อัปโหลดผ่าน gateway ทั้งสองแบบได้ตอนทดสอบ
*   ร่างแรกของ ADR นี้ปล่อย `PATCH`/`DELETE /notes/<id>` ที่มี `X-Note-Token` ผ่านโดยไม่ต้อง login (ADR-004) · ADR-013 เลิกใช้ edit token ก่อน ADR นี้ merge ข้อยกเว้นจึงถูกลบ และ cases เก็บสองแถวที่ส่ง header เดิมไว้ให้เห็นว่าไม่ข้ามการตรวจแล้ว
