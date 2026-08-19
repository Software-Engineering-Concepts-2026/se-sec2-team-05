# AI Usage Log

บันทึกการใช้เครื่องมือ AI (GitHub Copilot, ChatGPT, Claude, Gemini ฯลฯ) ในการทำโปรเจกต์ NoteShare ของทีม The Builders

**นโยบายของทีม:** เราใช้ AI เป็นผู้ช่วยร่าง (drafting) และ pair-programming เท่านั้น ไม่ใช่ผู้ตัดสินใจแทนคน — งานทุกชิ้นที่ AI ช่วยสร้างจะถูกสมาชิกในทีมอ่าน ตรวจ และแก้ไขก่อน commit เสมอ และต้องผ่าน PR review ตาม Git Workflow ที่ตกลงกันไว้ใน README (อย่างน้อย 1 คน approve ก่อน merge เข้า `main`) ความรับผิดชอบต่อความถูกต้องของโค้ด/เอกสารสุดท้ายเป็นของผู้เขียนที่เป็นมนุษย์ ไม่ใช่ของเครื่องมือ AI

ไฟล์นี้เป็น log ที่เปิดเผยตามจริง ไม่ปิดบังหรือลดทอนการใช้ AI — จุดประสงค์คือความโปร่งใส ไม่ใช่การทำให้ดูเหมือนเขียนเองทั้งหมด

## Log

| Date/PR | Contributor | Tool(s) | What it was used for | How output was reviewed/edited |
| --- | --- | --- | --- | --- |
| 2026-07-10, PR #35 | อติชาติ ผาแสนเถิน | GitHub Copilot, ChatGPT | สร้าง interactive prototype หน้าอัปโหลดโน้ต (commit `cca0aa0` — "implement interactive upload-note mockup using copilot/chatgpt") | อติชาติตรวจและแก้ HTML/CSS ที่ generate มาก่อน commit |
| 2026-07-10, ส่วนหนึ่งของ PR #37 | วชิรวิทย์ ศรีทอง | GitHub Copilot, Claude | สร้าง interactive mockup หน้าลงทะเบียน + prototype หน้าค้นหาโน้ต และแก้ชื่อไฟล์ wireframe (commits `e75dba8`, `7a455c6`, `0ea55bd`) | วชิรวิทย์ตรวจและแก้ไข HTML/CSS/XSS หลังจากที่ genereate มาก่อน comit  |
| 2026-07-10, PR #36 | กฤตเมธ ป้องตัน | GitHub Copilot, Gemini | สร้าง interactive prototype หน้า note-rating และแก้ brand/wireframe (commits `856e6ee`, `35aca15`, `a7321ba`) | _(TODO — กฤตเมธ กรอกรายละเอียดว่า prompt/ผลลัพธ์จาก AI ตรวจและแก้ตรงไหนบ้าง)_ |
| 2026-07 ~ 2026-08 (ongoing sessions) | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ใช้หลายรอบ session สำหรับ: เอกสาร architecture (เขียน C4 diagrams, ร่าง ADR-001/002 รวม Alternatives section), จัด GitHub issue labels/milestones/acceptance criteria ให้ 19 user stories, `docs/requirements/user-stories.md`, `nfr.md`, เพิ่ม Frequency-of-Use ใน persona, ขยาย `main_scenario.md`, `prototypes/sprint1/README.md`, `tech_stack.md`, `docs/project-proposal.md`, `docs/definition-of-done.md` | อติชาติอ่าน ตรวจ และแก้เนื้อหาทั้งหมดก่อน commit ทุกครั้ง |

> **TODO:** วชิรวิทย์และกฤตเมธ — ช่วยกรอกแถวของตัวเองให้ละเอียดขึ้น (prompt ที่ใช้จริง, ช่วง session, และรายละเอียดของสิ่งที่ตรวจ/แก้) เพราะมีแค่เจ้าของงานที่รู้ข้อมูลนี้แน่ชัด

## Prompts ที่ใช้

prompt ที่เก็บได้แบบคำต่อคำมีดังนี้ อันไหนที่กู้ข้อความจริงไม่ได้จะระบุไว้ว่าเป็นการเรียบเรียงย้อนหลัง ไม่เอามาปนกับของจริง

### Prompt 1 — Copilot inline, หน้าอัปโหลดโน้ต (อติชาติ)

prompt นี้ยังค้างอยู่ในโค้ดจริง เป็น HTML comment ที่ `prototypes/sprint1/atichat_upload_note_prototype.html` บรรทัด 10–19 (ตอนใช้ Copilot แบบ comment-driven แล้วไม่ได้ลบทิ้ง) จึงยกมาได้ตรงตัว:

```
A centered card for an "upload note" form.
It should contain:
- A main title: "แบ่งปันโน้ต"
- An input field for the note title
- An input field for the subject / course code
- A file input that accepts a PDF or an image file
- A textarea for an optional description
- A primary submit button with the text "อัปโหลด"
```

เทียบกับ Five S's (SCG Ch.4): **Structured** ผ่าน (บอกเป็น bullet ทีละ element), **Specific** ผ่าน (ระบุชนิด input และข้อความบนปุ่มตรงตัว), **Single task** ผ่าน (ขอแค่ markup ของการ์ดเดียว ไม่พ่วง validation หรือ CSS), **Short** ผ่าน, แต่ **Surrounding** ยังขาด — ไม่ได้บอก AI ว่าเป็นโปรเจกต์ NoteShare, ไม่ได้บอกว่าห้ามใช้ framework, และไม่ได้บอกว่าจะมี `style.css` แยกอยู่แล้ว ผลคือรอบแรก Copilot เสนอ inline style มาด้วยซึ่งต้องรื้อออกเอง

### Prompt 2 — ตรวจงาน Lab 4 (อติชาติ, Claude Code, 2026-08-19)

prompt จริงที่พิมพ์ในรอบ session นี้ วางใบงาน Lab 4 ทั้งใบเป็น context แล้วปิดท้ายด้วยประโยคเดียว:

```
[วางเนื้อหาใบงาน Lab 4 ทั้งใบ] อันนี้ทำครบแล้วหรือยัง ตรวจเช็คให้ที
```

และรอบถัดมาเมื่อเห็นรายการที่ยังขาด:

```
จัดการต่อเลยให้ที
```

เทียบกับ Five S's: **Surrounding** แข็งที่สุด (ให้เกณฑ์การให้คะแนนทั้งใบไปเลย AI จึงเทียบกับ rubric ได้ตรงข้อ) และ **Single task** ชัด (ตรวจ ไม่ใช่ทำ) แต่ **Specific** อ่อน — ไม่ได้บอกว่าให้ตรวจ branch ไหนหรือรวม PR ที่ยังไม่ merge ด้วยไหม ผลคือ AI ต้องไปไล่ `git branch -a` และ `gh pr list` เอง ซึ่งรอบนี้ออกมาถูก แต่ถ้าอยากได้ผลแน่นอนควรระบุขอบเขตให้ตั้งแต่แรก

### Prompt 3 — หน้า note-rating (กฤตเมธ)

เครื่องมือที่ใช้จริงคือ **Gemini** (กฤตเมธยืนยันเมื่อ 2026-08-19) ส่วน comment ในไฟล์ `kittamet_note_rating_prototype.html` ที่เคยเขียนว่า "JavaScript จาก ChatGPT" เป็นข้อความที่ระบุที่มาผิด และแก้ให้ตรงแล้วใน PR #41

_TODO — กฤตเมธ: วาง prompt ที่ใช้ขอ JS ส่วนคลิกดาวจาก Gemini มาไว้ตรงนี้_

### Prompt 4 — หน้าค้นหาโน้ต (วชิรวิทย์)

_TODO — วชิรวิทย์: วาง prompt ที่ใช้ขอ search/filter/sort และ prompt รอบที่แก้เรื่อง XSS (ฟังก์ชัน `esc()` ในไฟล์) มาไว้ตรงนี้_

## ส่วนที่รับจาก AI ตรงๆ (ไม่แก้)

ส่วนที่ยังเป็นของ AI แบบไม่ได้แก้เลย เท่าที่ตามย้อนหลังได้:

| ส่วน | ที่มา | สถานะ |
| --- | --- | --- |
| `prototypes/sprint1/index.html` และ `prototypes/sprint1/style.css` | Claude Code (2026-08-19) | generate ทั้งไฟล์ อติชาติอ่านและรันทดสอบใน browser ก่อน commit แต่ไม่ได้แก้บรรทัดใด |
| หัวข้อ "Next step (Sprint 2)" ใน `prototypes/sprint1/README.md` | Claude Code (2026-08-19) | AI ร่างโดยอ้างเนื้อหา ADR-001 อติชาติตรวจว่าลำดับงานตรงกับที่ทีมคุยกันไว้ ไม่ได้แก้เนื้อหา |
| script เซ็ต state ก่อนถ่าย screenshot (อยู่ใน scratchpad ไม่ commit) | Claude Code (2026-08-19) | รับมาทั้งก้อน ใช้ครั้งเดียวเพื่อถ่ายภาพ ไม่ได้เข้า repo |
| C4 diagram (SVG) และเนื้อหา ADR-001/ADR-002 | Claude Code | AI ร่าง อติชาติแก้ถ้อยคำและตัวเลือกใน Alternatives บางส่วน จึงไม่ใช่ "ไม่แก้" ทั้งก้อน |
| ตัวจัดการคลิกดาวใน `kittamet_note_rating_prototype.html` | Gemini (กฤตเมธยืนยัน 2026-08-19) | _รอกฤตเมธยืนยันว่ารับมาตรง ๆ หรือแก้ไปแล้วบ้าง_ |

ส่วนที่ตามหลักฐานแล้วน่าจะเป็นงานที่คนเขียน/แก้เอง ไม่ใช่รับจาก AI ตรง ๆ: ฟังก์ชัน `esc()` กัน XSS และการ clamp ค่าใน `stars()` ของหน้าค้นหา (เข้ามาในรอบที่ PR #37 ถูก CHANGES_REQUESTED จึงเป็นผลจากรีวิวของคนในทีม), การตัดสินใจเรื่อง Tracer vs Prototype, และเนื้อหา reflection รายบุคคลทั้งสามไฟล์

> **TODO:** วชิรวิทย์และกฤตเมธ — ตารางนี้ยังไม่ครบงานของสองคน ที่กรอกไว้ประเมินจากการอ่านโค้ดกับ commit message ย้อนหลัง ไม่ใช่จากความจำของเจ้าของงาน ช่วยเติมส่วนที่รับจาก AI แบบไม่แก้ของตัวเอง และแก้แถวที่ระบุผิดด้วย
