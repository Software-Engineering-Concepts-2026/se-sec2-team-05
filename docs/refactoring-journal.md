# Refactoring Journal - Lab 7

## Smell ที่เจอ

**ที่ไหน:** `prototypes/sprint1/wachirawit_search_note_prototype.html` (ก่อนแก้ อยู่ในบล็อก `<script>` inline บรรทัดประมาณ 84-148)

**คืออะไร:**
1. **Long/nested conditional:** ตัวเรียงผลลัพธ์ (`sort`) เขียนเป็น ternary ซ้อนกัน 3 ชั้น (`sortFilter.value === 'rating' ? ... : sortFilter.value === 'download' ? ... : ...`) ถ้าจะเพิ่มโหมดเรียงใหม่ต้องซ้อน ternary เพิ่มไปเรื่อยๆ อ่านยากขึ้นทุกครั้ง
2. **โค้ดที่ทดสอบไม่ได้เลย (testability / Orthogonality):** ฟังก์ชัน `esc()` (escape HTML กัน XSS) และ `stars()` (แปลงคะแนนเป็นดาว) เป็น pure logic ที่ไม่ควรผูกกับ UI แต่ถูกเขียนไว้ inline ในหน้า HTML ทำให้ไม่มีทางเขียน unit test ได้เลยถ้าไม่เปิดเบราว์เซอร์จริง ทั้งที่โปรเจกต์นี้ยังไม่มี test runner ตั้งไว้เลยสักตัว (`src/tests/README.md` เป็น template เปล่า)
3. **Magic number ซ้ำ:** เลข `5` (จำนวนดาวเต็ม) ปรากฏ 2 ครั้งในฟังก์ชัน `stars()` โดยไม่มีชื่อกำกับความหมาย

**ทำไมถือว่า smell:** ข้อ 1 และ 2 ตรงกับสิ่งที่ใบงานให้สังเกต โค้ดจุดนี้แก้ยากขึ้นเรื่อยๆ ถ้าโปรเจกต์โต (ETC: เปลี่ยนยาก) และผิด Orthogonality เพราะ business logic (คำนวณ/กรอง/เรียง) ถูกมัดรวมกับ DOM จนแยกทดสอบไม่ได้

## AI usage

**เครื่องมือ:** Claude Code (Claude Sonnet 5)

**Prompt ที่ใช้ (สรุปจากบทสนทนาจริง):**
1. "อ่าน repo นี้ ช่วยหา code smell ที่เห็นชัดและแก้ได้ใน 30 นาที สำหรับ Lab 7" ผลคือ Claude สำรวจ repo แล้วรายงานว่าโค้ดจริงมีน้อยมาก (ส่วนใหญ่เป็นเอกสาร/mockup) ตัวเลือกที่เป็นไปได้มีแค่ `services/stats-service/app.py` (เล็กเกินไป ยังไม่ merge เข้า main) กับ prototype 3 หน้า
2. "เลือก smell ในหน้า search prototype ที่อธิบายได้และมี test คลุมได้จริง" ผลคือ Claude เสนอแยก `esc()`/`stars()`/ตัวเรียงผลลัพธ์ ออกเป็นไฟล์ `note-utils.js` แล้วเขียน unit test ด้วย `node --test` (มากับ Node.js อยู่แล้ว ไม่ต้องลง dependency เพิ่ม)
3. "ทำเลย แล้วรันเทสต์/เปิดหน้าเว็บจริงยืนยันว่ายังทำงานเหมือนเดิม" ผลคือ Claude สร้างไฟล์ เขียนเทสต์ 7 เคส รันผ่านทั้งหมด แล้วเปิดหน้าเว็บด้วย headless Edge ตรวจ console error และหน้าตาก่อน-หลัง (ระหว่างทางเจอบั๊กที่ Claude สร้างเอง คือลืมห่อไฟล์ `note-utils.js` ด้วย IIFE ทำให้ `escapeHtml` ชนกับตัวแปรชื่อเดียวกันในสโคปโกลบอลตอนโหลดในเบราว์เซอร์ แก้แล้วก่อนจะยืนยันว่าใช้ได้จริง)

**ส่วนที่รับจาก AI ตรงๆ (ไม่แก้เพิ่ม):** โค้ดทั้งหมดใน `note-utils.js`, `note-utils.test.js`, และการแก้ `wachirawit_search_note_prototype.html` มาจาก Claude Code ทั้งก้อน ทีมยังไม่ได้แก้ต่อเพิ่มเติม เพราะเนื้อหาเป็น utility function ล้วนๆ (ไม่ใช่ business logic ที่ต้องใช้ context เฉพาะของทีม) แต่สมาชิกในทีมอ่านโค้ดและรันเทสต์เองแล้วก่อนจะเชื่อว่าใช้ได้จริง

## Before/After

| | Before | After |
| --- | --- | --- |
| ความยาว logic ใน `<script>` ของหน้า search | ~90 บรรทัด รวม pure function กับ DOM code ปนกัน | ลดลงเหลือเฉพาะโค้ดที่ต้องคุย DOM จริงๆ ส่วน pure function ย้ายออกไป 33 บรรทัดใน `note-utils.js` |
| Testability | 0 ไม่มีทางรัน unit test ได้เลยถ้าไม่เปิดเบราว์เซอร์ | มี unit test 7 เคส รันผ่าน `node --test` ได้ทันที ไม่ต้องลง dependency |
| การเรียงผลลัพธ์ | ternary ซ้อน 3 ชั้น เพิ่มโหมดใหม่ต้องซ้อนต่อ | lookup table (`SORT_COMPARATORS`) เพิ่มโหมดใหม่แค่เพิ่ม entry เดียว |
| การ escape ข้อความกัน XSS | สร้าง DOM node จริงเพื่อ escape (ใช้ได้แค่ในเบราว์เซอร์) | string replace ล้วนๆ (`escapeHtml`) ใช้ได้ทั้งเบราว์เซอร์และ Node ทดสอบได้ตรงๆ |
| Coupling | UI กับ logic ผูกกันแน่นในไฟล์เดียว | แยกไฟล์ชัดเจน หน้า HTML เรียกใช้ฟังก์ชันจาก `NoteUtils` แทนที่จะนิยามเอง |

ยืนยันว่าพฤติกรรมเดิมไม่เปลี่ยน โดยรัน `node --test` ผ่านทั้ง 7 เคส และเปิดหน้าเว็บจริงด้วย headless Edge เทียบก่อน/หลัง ผลค้นหา/กรอง/เรียงทั้ง 5 รายการเหมือนเดิมทุกประการ ไม่มี console error

## Lesson

- โปรเจกต์นี้ยังไม่มี test runner ตั้งไว้เลยตั้งแต่ Lab 1-6 การจะ "เขียน test ก่อน refactor" ตามที่ Fowler แนะนำจึงทำไม่ได้ทันทีจนกว่าจะแยกโค้ดออกมาให้ testable ก่อน บทเรียนคือ pure logic ควรแยกออกจาก DOM ตั้งแต่แรกเขียน ไม่ใช่รอมาแยกทีหลังตอนจะ refactor
- AI workflow แบบ explain to propose to apply to test ช่วยจับบั๊กที่ AI สร้างขึ้นเองได้ (ปัญหา IIFE/global scope) เพราะขั้น "test" บังคับให้เปิดเบราว์เซอร์จริงตรวจ ไม่ใช่เชื่อว่าโค้ดถูกเพราะ AI เขียนให้
- `node --test` ที่มากับ Node.js ใช้แทน framework ทดสอบเต็มรูปแบบได้ในสถานการณ์ที่โปรเจกต์ยังไม่มี dependency ทดสอบเลย เหมาะกับ scope เล็กๆ แบบนี้ ไม่จำเป็นต้องลง Jest/Vitest ถ้ายังไม่มีเหตุผลอื่นที่ต้องใช้
