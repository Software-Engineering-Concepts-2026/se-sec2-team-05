# AI Usage Log

บันทึกการใช้เครื่องมือ AI (GitHub Copilot, ChatGPT, Claude, Gemini ฯลฯ) ในการทำโปรเจกต์ NoteShare ของทีม The Builders

**นโยบายของทีม:** เราใช้ AI เป็นผู้ช่วยร่าง (drafting) และ pair-programming เท่านั้น ไม่ใช่ผู้ตัดสินใจแทนคน — งานทุกชิ้นที่ AI ช่วยสร้างจะถูกสมาชิกในทีมอ่าน ตรวจ และแก้ไขก่อน commit เสมอ และต้องผ่าน PR review ตาม Git Workflow ที่ตกลงกันไว้ใน README (อย่างน้อย 1 คน approve ก่อน merge เข้า `main`) ความรับผิดชอบต่อความถูกต้องของโค้ด/เอกสารสุดท้ายเป็นของผู้เขียนที่เป็นมนุษย์ ไม่ใช่ของเครื่องมือ AI

ไฟล์นี้เป็น log ที่เปิดเผยตามจริง ไม่ปิดบังหรือลดทอนการใช้ AI — จุดประสงค์คือความโปร่งใส ไม่ใช่การทำให้ดูเหมือนเขียนเองทั้งหมด

## Log

| Date/PR | Contributor | Tool(s) | What it was used for | How output was reviewed/edited |
| --- | --- | --- | --- | --- |
| 2026-07-10, PR #35 | อติชาติ ผาแสนเถิน | GitHub Copilot, ChatGPT | สร้าง interactive prototype หน้าอัปโหลดโน้ต (commit `cca0aa0` — "implement interactive upload-note mockup using copilot/chatgpt") | อติชาติตรวจและแก้ HTML/CSS ที่ generate มาก่อน commit |
| 2026-07-10, ส่วนหนึ่งของ PR #37 | วชิรวิทย์ ศรีทอง | GitHub Copilot, Claude | สร้าง interactive mockup หน้าลงทะเบียน + prototype หน้าค้นหาโน้ต และแก้ชื่อไฟล์ wireframe (commits `e75dba8`, `7a455c6`, `0ea55bd`) | วชิรวิทย์ตรวจและแก้ไข HTML/CSS/XSS หลังจากที่ genereate มาก่อน comit  |
| 2026-07-10, PR #36 | กฤตเมธ ป้องตัน | GitHub Copilot, Gemini | สร้าง interactive prototype หน้า note-rating และแก้ brand/wireframe (commits `856e6ee`, `35aca15`, `a7321ba`) | กฤตเมธนำ Prompt ให้ Gemini ช่วยร่าง HTML/CSS และส่วนระบบให้คะแนนดาว/ความคิดเห็น (JavaScript) จากนั้นตรวจเช็กโครงสร้าง ปรับแต่ง UI ให้เข้ากับแบบร่าง และแก้ไขการเชื่อมโยงระบบ UI ดาว |
| 2026-07 ~ 2026-08 (ongoing sessions) | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ใช้หลายรอบ session สำหรับ: เอกสาร architecture (เขียน C4 diagrams, ร่าง ADR-001/002 รวม Alternatives section), จัด GitHub issue labels/milestones/acceptance criteria ให้ 19 user stories, `docs/requirements/user-stories.md`, `nfr.md`, เพิ่ม Frequency-of-Use ใน persona, ขยาย `main_scenario.md`, `prototypes/sprint1/README.md`, `tech_stack.md`, `docs/project-proposal.md`, `docs/definition-of-done.md` | อติชาติอ่าน ตรวจ และแก้เนื้อหาทั้งหมดก่อน commit ทุกครั้ง |
| 2026-08-19, PR #41 + #43 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจงาน Lab 4 เทียบ rubric ทั้งใบแล้วแก้ส่วนที่ตก: เขียน `prototypes/sprint1/index.html` + `style.css` (หน้า hub), ถ่าย screenshot prototype ทั้งสี่หน้าด้วย headless browser, เพิ่มหัวข้อ Next step ใน `prototypes/sprint1/README.md`, เพิ่มหัวข้อ Prompts + "ส่วนที่รับจาก AI ตรงๆ" ในไฟล์นี้, กรอก Sprint 1 retro ใน `reflect.md`, เขียน PR description ของ #41/#43 ใหม่ | อติชาติอ่านทุกไฟล์และเปิด prototype ทดสอบในเบราว์เซอร์ก่อน commit · ส่วนที่ไม่ได้แก้บรรทัดใดเลยระบุไว้ในตาราง "ส่วนที่รับจาก AI ตรงๆ" ด้านล่าง |
| 2026-08-19, PR #40 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | เติมประโยครองรับ US-14 (คอมเมนต์) และ US-15 (รายการโปรด) ใน Scenario 2 กับ 3 ของ `main_scenario.md` (commit `7afcb72`) เพราะสอง story นี้เดิมอ้าง scenario แบบใกล้เคียง ไม่มีประโยคใน scenario รองรับตรง ๆ | อติชาติตรวจว่าเนื้อเรื่องที่เติมยังเข้ากับ persona เจมส์และไม่ขัดกับ scenario เดิม |
| 2026-08-19, PR #45 (แทน #42) | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจงาน Lab 5 เทียบ deliverable ในสไลด์บทที่ 5 แล้วแก้ส่วนที่ตก: กู้ Mermaid `C4Context` กลับมาและเขียน `C4Container` ใหม่ทั้ง EN/TH, ฝังบล็อก Mermaid ใน `c4-context.md`/`c4-container.md`, แก้ย่อหน้า "ไม่ใช้ Mermaid" ใน README ทั้งสองภาษา, ลบ `uml_models.md` ที่เป็น template เปล่า, ร่างหัวข้อ Exit Ticket บทที่ 5 (B1/B2/B3) ใน `reflect.md`, แนบรูป C4 ใน PR description | ตรวจว่าไฟล์ `.mmd` ทั้ง 4 parse ผ่านด้วย `mermaid-cli` จริงก่อน commit · อติชาติอ่านและตรวจว่าเนื้อหา B1/B2/B3 ตรงกับ artifact ที่มีในรีโป และกำกับไว้ในไฟล์ว่าเขียนย้อนหลัง ไม่ใช่เขียนสดท้ายคาบ |
| 2026-08-19, PR #44 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | เขียน `.github/pull_request_template.md` และแก้หัวข้อ Git Workflow ใน `README.md` ตาม action item จาก Sprint 1 retro · พ่วงจัดคอลัมน์ project board #28 ผ่าน GitHub API (ย้าย Sprint 1 Must เข้า Sprint Backlog, เอา item ของ duplicate ที่ปิดแล้วออก) | อติชาติตรวจเนื้อหา template และไล่ดูสถานะบอร์ดหลังแก้ทุกครั้ง · ก่อนลบ item ตรวจแล้วว่า issue ทั้งสามถูกปิดเป็น duplicate จริง |
| 2026-08-23, feature/lab6-dockerfile | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | เขียน root `Dockerfile` แบบ multi-stage สำหรับ Stats Service, เติม `services/stats-service/app.py` (Flask, `/health` + `/stats`) และ `requirements.txt`, เพิ่ม `.env`/`.env.*`/`tests/`/`coverage/`/`*.log` เข้า `.dockerignore`, เขียน `docker/README.md`, และร่างหัวข้อ Post-quiz 6 ใน `reflect.md` | อติชาติตรวจ Dockerfile ทีละบรรทัดเทียบ checklist ใบงาน Lab 6 (multi-stage, base image ที่ pin เวอร์ชัน, `USER` non-root, `EXPOSE`) ก่อน commit |
| 2026-08-23, feature/lab6-dockerfile (ต่อ) | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | หลังติดตั้ง Docker Desktop สำเร็จ Claude รันคำสั่งเองใน session: `docker build`, `docker run` + `curl /health` และ `/stats` (ยืนยัน 200 ทั้งคู่), `docker tag` และ `docker push` ขึ้น `ghcr.io/software-engineering-concepts-2026/stats-service:v0.1.0`, แก้ `docker/README.md` ให้บันทึกขนาด image จริง (187MB) และผลทดสอบจริงแทนบรรทัด TBD, ตั้งค่า git identity ในเรโปนี้, commit และ push branch ขึ้น origin | อติชาติเป็นคนรัน `docker login` เอง แต่ GitHub PAT หลุดเข้ามาในบทสนทนากับ Claude 2 ครั้ง (ครั้งแรกพิมพ์วางในแชทตรง ๆ, ครั้งที่สองหลุดผ่าน terminal echo ของคำสั่ง `!`) — Claude เตือนให้ revoke ทั้งสองตัวทันทีที่เห็น และอติชาติ revoke ทั้งสองตัวใน GitHub settings แล้ว ไม่มี token ใดที่ยังใช้งานได้อยู่ในเวลาที่เขียน log นี้ · อติชาติตรวจ output ของทุกคำสั่งที่ Claude รัน (build log, curl response, push digest) ก่อนยืนยันให้ push branch ขึ้น origin |
| 2026-08-23, PR #46 (รอบตรวจใบงานจริง) | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจ PR #46 เทียบใบงาน Lab 6 ตัวจริง (ตาราง L6.1) พบว่าเกณฑ์ "Image บน Registry" ต้องการ public ไม่ใช่แค่ push — ใช้ browser automation เข้า Package settings ของ ghcr.io จริงแล้วพบว่า org `Software-Engineering-Concepts-2026` ปิด Public/Internal ไว้ระดับ org (เหลือ Private เท่านั้น) จึงเสนอ push เพิ่มขึ้น Docker Hub (public โดย default) แทน — Claude เปิด Docker Desktop ให้ (ค้างไม่ได้รันอยู่), รัน `docker build`/`run`/`curl` ทดสอบซ้ำ, และ `docker push felsau/stats-service:v0.1.0` เอง หลังจากยืนยันว่า repo เป็น public จริงผ่าน Docker Hub public API (`is_private:false`), แก้ `docker/README.md` ให้ระบุทั้งสอง registry และเหตุผลที่ ghcr.io ยังเป็น private, ถ่าย screenshot หน้า ghcr.io package แล้วฝังเข้า PR #46 description พร้อมหมายเหตุ org policy | รอบนี้อติชาติเป็นคนรัน `docker login` เองในเทอร์มินัลของตัวเองทั้งหมด (เรียนรู้จาก incident token หลุดในรอบก่อน) ไม่ได้พิมพ์ username/password ให้ Claude เห็นเลย — บอก Claude แค่ว่า "login แล้ว" จาก Docker Hub username `Felsau` เท่านั้น อติชาติตรวจ output `docker build`/`push`/curl ทุกคำสั่งก่อนอนุมัติให้แก้ README และ PR description |
| 2026-08-26, Lab 7 refactor | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | หา code smell ในหน้า search prototype แล้ว refactor: แยก `esc()`/`stars()`/ตัวเรียงผลลัพธ์ ออกจาก `wachirawit_search_note_prototype.html` ไปเป็นไฟล์ `prototypes/sprint1/note-utils.js` ที่ทดสอบได้ + เขียน unit test 7 เคสด้วย `node --test`, เขียน `docs/refactoring-journal.md` | อติชาติอ่านโค้ดที่แยกออกมาทั้งหมด รันเทสต์เองผ่านทุกเคส และเปิดหน้าเว็บจริงเทียบก่อน/หลังด้วย headless browser ก่อนจะยอมรับว่าใช้ได้ (ระหว่างทาง Claude ทำโค้ดพังเองครั้งหนึ่งเพราะลืม IIFE ทำให้ตัวแปรชนกันตอนโหลดในเบราว์เซอร์ แล้วแก้เองก่อนจะรายงานว่าเสร็จ ไม่ได้ปล่อยผ่านไปโดยไม่ตรวจ) |
| 2026-08-31, feature/lab8-ci-tests | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตั้ง CI ตัวแรกของโปรเจกต์: เขียน `.github/workflows/ci.yml` (3 job — เทสต์ JS, เทสต์ Python, build + smoke-test Docker image), เขียน `src/tests/test_stats_service.py` + `conftest.py` + `requirements-dev.txt` สำหรับ Stats Service, เขียน `docs/testing/readme.md` (test plan + test case + report) และ `src/tests/README.md`, ล้าง branch local ที่ merge แล้ว 14 อัน | อติชาติสั่งให้รันเทสต์จริงก่อนยืนยัน — `pytest src/tests` ผ่าน 4/4 และ `node --test` ผ่าน 7/7 บนเครื่อง (Claude รันให้เห็น output จริง ไม่ได้เคลม) · ส่วน job `docker-build` ยังไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิด จึงระบุไว้ใน test report ว่ารอผลจาก CI ไม่ได้เขียนว่าผ่านแล้ว · ระหว่างทางเจอว่า `pip install` พังบน Windows เพราะคอมเมนต์ภาษาไทยใน `requirements-dev.txt` (pip อ่านไฟล์ด้วย locale encoding cp1252) จึงเปลี่ยนคอมเมนต์เป็น ASCII |
| 2026-08-31, feature/us08-note-metadata-service | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | เขียน Notes Service ทั้งตัวสำหรับ US-08 (#8): `app.py` (5 endpoint), `models.py`, `validation.py`, `storage.py`, `Dockerfile`, `README.md` ของ service + `docker-compose.yml` (Postgres + 2 service) + เทสต์ 28 เคสใน `src/tests/` + ADR-003 ทั้ง EN/TH + อัปเดต CI ให้ทดสอบ end-to-end ผ่าน compose | อติชาติสั่งให้รันเทสต์จริงทุกครั้งก่อนยอมรับ (`pytest` 32/32, `node --test` 7/7) · ระหว่างทาง Claude ทำเทสต์ของ stats-service พังเองเพราะทุก service มีไฟล์ `app.py` ชื่อซ้ำกัน แล้ว `import app` ไปเจอ notes-service แทน — Claude เจอเองตอนรันเทสต์ แก้ด้วยการโหลดผ่าน importlib ในชื่อโมดูลที่ไม่ซ้ำ และเขียนเหตุผลไว้ใน `conftest.py` แล้ว · Claude ยังเจอว่า `import app.py` สร้าง `notes.db` และโฟลเดอร์ `C:\data\notes` ทิ้งไว้บนเครื่อง จึงชี้ไป temp dir ใน conftest และลบของที่ค้างทิ้ง |
| 2026-09-06, PR #57 + hardening + US-19/US-20 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจสถานะโปรเจกต์ทั้งรีโปแล้วพบว่า PR #56 ถูก merge เข้า `feature/lab8-ci-tests` แทน `main` ทำให้ Notes Service ไม่เคยขึ้น `main` เลย จึงเปิด PR #57 แก้ · งาน hardening: ตั้ง `MAX_CONTENT_LENGTH` + errorhandler 413, clamp `limit`/`offset` ที่ขอบล่าง, เพิ่ม `.venv/` ใน `.gitignore`, เขียนเทสต์ commit ล้มแล้วไม่เหลือไฟล์กำพร้าที่ค้างไว้ใน test plan · งาน US-19/US-20: `PATCH`/`DELETE /notes/<id>`, `tokens.py` (edit token ต่อโน้ต), คอลัมน์ `edit_token_hash`/`updated_at`, โหมด partial ของ `validate_metadata`, ADR-004 ทั้ง EN/TH, เทสต์ 13 เคส และ smoke test ของ edit/delete ใน CI | อติชาติสั่งให้รันเทสต์จริงทุกครั้งก่อนยอมรับ — `pytest src/tests` ผ่าน 48/48 และ `node --test` ผ่าน 7/7 บนเครื่อง · อติชาติเป็นคนเลือกแนวทางตรวจสอบเจ้าของเองจากสามตัวเลือกที่เสนอมา (uploader_name / edit token / รอ Auth Service) โดยเลือก edit token เพราะเป็นทางเดียวที่บังคับ AC "เจ้าของเท่านั้น" ได้จริงและทดสอบได้ · ระหว่างทางอติชาติสั่งแก้ข้อเสนอเดิมเรื่อง `MAX_CONTENT_LENGTH` ที่ตั้งเท่าขนาดไฟล์สูงสุดพอดี ซึ่งจะทำให้ไฟล์ 20 MB ถูกปฏิเสธเพราะ multipart overhead จึงเผื่อไว้ 1 MB · job `docker-build` ยังไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิด จึงรอผลจาก CI ไม่ได้เขียนใน test report ว่าผ่านแล้ว |
| 2026-09-18, feature/lab9-testing | อติชาติ ผาแสนเถิน | ChatGPT, Claude Code (Anthropic) | Lab 9 (Unit Test/TDD/Property-Based Test/CI/Saboteur): Claude Code อ่านโค้ดจริงในรีโปแล้วร่าง prompt ให้อติชาติเอาไปสั่ง ChatGPT ทำทีละขั้น ได้ผลลัพธ์คือ `src/tests/test_notes_validation_boundary.py` (19 boundary/equivalence test ของ `validate_metadata`/`validate_file`), `src/fizzbuzz.py` + `src/tests/test_fizzbuzz.py` (TDD kata ครบ Red-Green-Refactor 4 รอบ + helper `is_multiple`), `src/tests/test_tokens_property.py` (2 property ด้วย Hypothesis บน `tokens.py`), แก้ `src/tests/requirements-dev.txt` (เพิ่ม `hypothesis`, `pytest-cov`) และ `.github/workflows/ci.yml` (เพิ่ม `--cov` ใน job `python-tests`), `docs/saboteur-journal.md` (เจาะ boundary บนของ `year_level` แบบ off-by-one แล้ว revert) | อติชาติรัน ChatGPT เองทีละขั้นแล้วรายงานผลกลับมาให้ Claude Code ตรวจ — Claude Code เปิด/รันไฟล์จริงในเครื่องเพื่อยืนยันทุกรอบ (diff, `pytest -v`, coverage report) ก่อนให้ prompt ขั้นถัดไป ไม่เชื่อรายงานเปล่า ๆ · commit history ถูกแยกย่อยตามลำดับ Red-Green-Refactor จริงที่เกิดขึ้น ไม่ใช่ squash เป็นก้อนเดียว |

> **TODO:** วชิรวิทย์และกฤตเมธ — ช่วยกรอกแถวของตัวเองให้ละเอียดขึ้น (prompt ที่ใช้จริง, ช่วง session, และรายละเอียดของสิ่งที่ตรวจ/แก้) เพราะมีแค่เจ้าของงานที่รู้ข้อมูลนี้แน่ชัด

## Prompts ที่ใช้

prompt ที่เก็บได้แบบคำต่อคำมีดังนี้ อันไหนที่กู้ข้อความจริงไม่ได้จะระบุไว้ว่าเป็นการเรียบเรียงย้อนหลัง ไม่เอามาปนกับของจริง

### Lab 4

#### Prompt 2 — ตรวจงาน Lab 4 (อติชาติ, Claude Code, 2026-08-19)



prompt จริงที่พิมพ์ในรอบ session นี้ วางใบงาน Lab 4 ทั้งใบเป็น context แล้วปิดท้ายด้วยประโยคเดียว:

```
[วางเนื้อหาใบงาน Lab 4 ทั้งใบ] อันนี้ทำครบแล้วหรือยัง ตรวจเช็คให้ที
```

และรอบถัดมาเมื่อเห็นรายการที่ยังขาด:

```
จัดการต่อเลยให้ที
```

เทียบกับ Five S's: **Surrounding** แข็งที่สุด (ให้เกณฑ์การให้คะแนนทั้งใบไปเลย AI จึงเทียบกับ rubric ได้ตรงข้อ) และ **Single task** ชัด (ตรวจ ไม่ใช่ทำ) แต่ **Specific** อ่อน — ไม่ได้บอกว่าให้ตรวจ branch ไหนหรือรวม PR ที่ยังไม่ merge ด้วยไหม ผลคือ AI ต้องไปไล่ `git branch -a` และ `gh pr list` เอง ซึ่งรอบนี้ออกมาถูก แต่ถ้าอยากได้ผลแน่นอนควรระบุขอบเขตให้ตั้งแต่แรก

### Lab 5

#### Prompt 7 — ตรวจ + กู้ C4 diagrams สำหรับ Lab 5 (อติชาติ, Claude Code, 2026-08-19)



prompt จริงที่พิมพ์ (รูปแบบเดียวกับ Prompt 2 — วางใบงานทั้งใบก่อนถามให้ตรวจ):

```
[วางเนื้อหาใบงาน Lab 5 ทั้งใบ] ตรวจให้หน่อยว่า deliverable ครบไหม เทียบกับสไลด์บทที่ 5
```

แล้วรอบถัดมาเมื่อเห็นว่า Mermaid หายไปและ `c4-container.md` ไม่ครบ:

```
กู้ Mermaid กลับมาแล้วเขียน C4Container ให้ครบทั้ง EN/TH ให้เลย
```

เทียบกับ Five S's: **Surrounding** แข็ง (วางใบงานทั้งใบ) เหมือน Prompt 2 แต่รอบนี้ **Specific** ดีขึ้นเพราะระบุตรง ๆ ว่าให้กู้ Mermaid ที่หายไป ไม่ปล่อยให้ AI เดาว่าจะแก้อะไร ผลคือ AI อ่าน commit history ของ `c4-container.md` แล้วพบว่าเคยมี Mermaid source อยู่ก่อนถูกแทนที่ด้วย SVG ล้วน (ดู commit `36e0080` "redraw C4 diagrams as hand-authored SVG") จึงกู้ `.mmd` กลับมาไว้คู่กับ SVG แทนที่จะเขียน diagram ใหม่ทั้งหมด

### Lab 6

#### Prompt 5 — เริ่มงาน Lab 6 (อติชาติ, Claude Code, 2026-08-23)



prompt จริงที่พิมพ์ วางใบงาน Lab 6 ทั้งใบเป็น context ก่อน แล้วถามเป็นสองรอบ:

```
[วางเนื้อหาใบงาน Lab 6 ทั้งใบ] ช่วยเช็คให้หน่อยว่างานนี้ทำแล้วหรือยัง
```

แล้วรอบถัดมา:

```
จัดการเริ่มงานให้เลยทีได้ไหม
```

เทียบกับ Five S's: **Surrounding** แข็ง (วางใบงานทั้งใบเป็น context) แต่ **Specific** อ่อนกว่ารอบตรวจงาน Lab 4/5 เพราะไม่ได้ระบุว่าจะ containerize service ไหน AI จึงต้องไปอ่าน `docs/architecture/c4-container.md` เองเพื่อเลือก Stats Service (Python + Flask) ตาม ADR ที่มีอยู่แล้วแทนที่จะเดาสุ่ม

#### Prompt 6 — ขอบเขตของสิ่งที่ AI ทำได้จริงในรอบนี้



เครื่องที่ใช้คุยกับ Claude ตอนแรกไม่มี Docker ติดตั้ง จึง Claude เขียนไฟล์ `Dockerfile` / `.dockerignore` / `docker/README.md` / โค้ด Flask ให้ก่อน โดยระบุขอบเขตไว้ตรง ๆ ใน `docker/README.md` ว่ายัง build/run/push จริงไม่ได้

ภายหลังอติชาติติดตั้ง Docker Desktop สำเร็จในวันเดียวกัน (2026-08-23) แล้วกลับมาต่อ session เดิม รอบนี้ Claude เป็นคนรันคำสั่ง `docker build`/`run`/`tag`/`push` เองทั้งหมด (ยกเว้น `docker login` ที่อติชาติรันเองผ่าน token ส่วนตัว) และแก้ `docker/README.md` ให้ตรงกับผลจริง — จุดที่ควรระบุตรงๆ คือ token ของอติชาติหลุดเข้ามาในบทสนทนา 2 ครั้งระหว่างขั้นตอนนี้ (ดูรายละเอียดในตาราง Log ด้านบน) ทั้งสองตัวถูก revoke แล้ว

### Lab 7

#### Prompt 8 (Lab 7 refactor หน้า search, อติชาติ, Claude Code, 2026-08-26)



prompt จริงที่พิมพ์ในรอบ session นี้ แบ่งเป็น 3 รอบ (workflow explain to propose to apply to test ตามที่ใบงาน Lab 7 กำหนด):

```
1) อ่าน repo นี้ ช่วยหา code smell ที่เห็นชัดและแก้ได้ใน 30 นาที สำหรับ Lab 7
2) เลือก smell ในหน้า search prototype ที่อธิบายได้และมี test คลุมได้จริง
3) ทำเลย แล้วรันเทสต์/เปิดหน้าเว็บจริงยืนยันว่ายังทำงานเหมือนเดิม
```

เทียบกับ Five S's: **Surrounding** ดี (บอกว่าเป็นงาน Lab 7 และมีข้อจำกัดเวลา 30 นาที) **Single task** ชัด (หา smell ก่อน แล้วค่อยสั่งแก้แยกรอบ ไม่ได้สั่งรวดเดียว) แต่ **Specific** อ่อนเหมือน Prompt 2 คือปล่อยให้ AI เลือกไฟล์/ฟังก์ชันเอง ผลคือรอบแรก AI ต้องสำรวจทั้ง repo ก่อนเจอว่าโค้ดจริงมีน้อย (ส่วนใหญ่เป็นเอกสาร) กว่าจะเจอ candidate ที่ใช้ได้

### Lab 8

#### Prompt 9 (Lab 8 CI + testing, อติชาติ, Claude Code, 2026-08-31)



```
1) งานตอนนี้ถึงไหนแล้ว แล้วต้องทำอะไรต่ออีก หรือว่าควรจะเริ่มทำชิ้นงานได้เลย
2) จัดการต่อให้ที
```

รอบนี้จงใจไม่บอกว่าต้องทำอะไร ให้ AI อ่านสถานะรีโปเองแล้วเสนอว่าอะไรค้าง เทียบกับ Five S's: **Surrounding** ดี (AI เห็นทั้งรีโปและ git history) แต่ **Specific** และ **Single task** อ่อนมากทั้งคู่ — prompt ที่สองสั้นแค่สามคำและไม่ได้กำหนดขอบเขต ผลคือ AI เลือกขอบเขตเองว่าจะทำ CI + เทสต์ + เอกสารทดสอบ ซึ่งบังเอิญตรงกับที่ต้องการ แต่ถ้าเลือกผิดก็จะเสียเวลาทั้งรอบ บทเรียนเดิมกับ Prompt 2 และ 8 คือ prompt แบบ "ดูให้หน่อย" ใช้ได้ผลตอน **สำรวจ** แต่ตอน **ลงมือ** ควรระบุขอบเขตให้ชัดก่อน

### งาน Sprint 2 (ไม่ผูกกับ Lab)

งานสองรอบนี้เป็นการทำ user story ของ Sprint 2 กับการคุมคิว PR ไม่ได้ผูกกับใบงาน Lab ใด จึงแยกหัวข้อไว้ต่างหาก

#### Prompt 11 — งาน hardening + US-19/US-20 (อติชาติ, Claude Code, 2026-09-06 ~ 2026-09-07)

**ไม่มี prompt คำต่อคำของรอบนี้** — ไม่มีข้อความของ prompt รอบนี้เก็บไว้ในรีโปหรือใน PR description ที่จะยกมาอ้างได้ (งานรอบนี้ทำวันที่ 2026-09-06 แล้ว merge เข้า `main` เป็น PR #57/#58 ในวันถัดมา) จึงบันทึกเป็นลักษณะคำสั่งที่ใช้จริงเท่าที่ตามย้อนหลังได้จาก git history กับ PR description ไม่เอามาปนกับ prompt คำต่อคำของรอบอื่น และไม่ใส่ไว้ในบล็อกโค้ดเพื่อไม่ให้เข้าใจผิดว่าเป็นข้อความจริง

ลักษณะคำสั่งที่ใช้จริงในรอบนี้ ตามหลักฐานที่ตามได้:

- เริ่มจากคำสั่งกว้างให้ตรวจสถานะทั้งรีโปว่างานถึงไหน — ผลคือพบว่า PR #56 ถูก merge เข้า `feature/lab8-ci-tests` แทน `main` ทำให้ Notes Service ไม่เคยขึ้น `main` เลย
- ตอนเลือกวิธีตรวจสอบความเป็นเจ้าของโน้ต **อติชาติเป็นคนตัดสินใจเอง** จากสามตัวเลือกที่ AI เสนอมา (เชื่อ `uploader_name` / edit token ต่อโน้ต / รอ Auth Service #5/#6) โดยเลือก edit token แล้วสั่งให้บันทึกเหตุผลเป็น ADR-004 — ไม่ได้ปล่อยให้ AI เลือกเอง
- สั่งแก้ข้อเสนอเดิมเรื่อง `MAX_CONTENT_LENGTH` ที่ตั้งเท่าขนาดไฟล์สูงสุดพอดี เพราะไฟล์ 20 MB จะถูกปฏิเสธจาก multipart overhead จึงให้เผื่อไว้ 1 MB
- ตลอดรอบมีเงื่อนไขกำกับว่า **ห้ามรายงานว่าเสร็จถ้ายังไม่ได้รันเทสต์ให้เห็น output จริง** และ **ห้าม push/เปิด PR/merge เองโดยไม่ได้สั่ง**

เทียบกับ Five S's: **Surrounding** ได้มาฟรีเหมือน Prompt 9 และ 10 (AI อ่านรีโปกับ git history เองได้) **Specific** ดีขึ้นชัดในจุดที่สำคัญ คือการล็อกทางเลือกทางสถาปัตยกรรมด้วยตัวเองแทนที่จะให้ AI เดา แต่ยัง**ไม่ได้เขียนเป็น prompt เดียวที่มีขอบเขตครบตั้งแต่ต้น** ยังเป็นการแก้ทิศทางเป็นช่วง ๆ ระหว่างทาง **Single task** อ่อนที่สุดในรอบนี้ — งาน hardening กับ US-19/US-20 ถูกทำในรอบเดียวกันแล้วค่อยแยกเป็นสอง PR ทีหลัง ทำให้ต้องมาเรียงคิว #57 → #58 → #59 ตอนท้าย

**บทเรียนจริงจากรอบนี้ — แยกสาเหตุของคิว PR ให้ชัดสองชั้น:** **สาเหตุหลัก**คือ PR #56 ถูก merge เข้า `feature/lab8-ci-tests` แทน `main` ทำให้ Notes Service ไม่เคยขึ้น `main` เลย งานที่ต่อยอดจากมันจึงติดค้างอยู่บน branch ซ้อน branch ต้องเปิด PR #57 มาแก้ฐานก่อน · **ปัจจัยเสริม**คือการไม่แยก task ตั้งแต่ต้น ทำให้งาน hardening กับ US-19/US-20 อยู่ในรอบเดียวกันแล้วต้องมาแยกเป็นสอง PR ทีหลัง คิวจึงยาวเป็น #57 → #58 → #59 แทนที่จะเป็น PR เดียวจบ — ปัจจัยนี้ทำให้คิวยาวขึ้น แต่ไม่ใช่ต้นเหตุที่ทำให้เกิดคิว · ส่วนสิ่งที่ทำถูกคือการที่คนเป็นผู้เลือกทางสถาปัตยกรรมเองแล้วบังคับให้บันทึกเป็น ADR ทำให้ทีมรีวิวและค้านได้ ไม่ใช่ AI ตัดสินใจเงียบ ๆ

#### Prompt 12 — คุมคิว merge, รีวิว และ approve PR #59/#60 และเปิด PR เอกสาร #61 (อติชาติ, Claude Code, 2026-09-08)

**prompt จริงที่พิมพ์ (ข้อความในบล็อกเป็นคำต่อคำ ไม่ได้ขัดเกลา — ส่วนที่เป็นรายการยาวถูกย่อไว้ในวงเล็บเหลี่ยม `[...]` และระบุจำนวนข้อจริงกำกับไว้ ไม่ใช่ข้อความที่พิมพ์เอง):**

```
1) ตอนนี้งานที่คุยกันถึงไหนแล้ว

2) merge PR #59 ให้เลย ใช้ "Create a merge commit" เท่านั้น ห้าม Squash และห้าม Rebase
   ขั้นตอน:
   1. ตรวจซ้ำว่า PR #59 ยัง APPROVED, CI ผ่านครบ, และสถานะ MERGEABLE
   2. หากเงื่อนไขครบ ให้ merge ด้วย merge commit
   3. ห้ามลบ branch และห้ามแตะต้อง PR #60
   4. หลัง merge ให้ checkout main และ pull จาก remote
   5. รายงาน: SHA ของ merge commit / สถานะ local main เทียบกับ remote /
      ยืนยันว่า issue #19 และ #20 ปิดอัตโนมัติหรือไม่
   ข้อห้าม: ห้าม Squash/Rebase, ห้าม push commit เพิ่ม, ห้ามแก้ conflict เอง,
   ห้าม merge PR #60
   ถ้า PR ไม่ผ่านเงื่อนไข, merge ไม่สำเร็จ หรือเกิด conflict ให้หยุดทันทีและรายงาน
   โดยไม่แก้ไขอะไรเอง

3) รีวิว PR #60 ให้ผม แต่ยังห้าม merge และห้าม comment ลง GitHub
   [ระบุไฟล์ที่ต้องอ่าน 3 ไฟล์ + สิ่งที่ต้องตรวจ 5 ข้อ: file_type validate,
   SQL injection, ไม่ทับ query param เดิม, paging clamp, ความครอบคลุมของ test
   + ให้เทียบกับ main หลัง merge #59 และระบุจุดที่อาจ conflict
   + ให้สรุปเป็น 3 กลุ่ม: ต้องแก้ก่อน merge / ควรแก้ / ผ่าน]
   ข้อห้าม: ห้ามแก้ไฟล์ใน branch ของ PR #60, ห้าม push, ห้าม approve หรือ
   request changes, ห้าม merge PR #60, ห้ามแตะ fix/notes-service-hardening
   หากพบปัญหา ให้รายงานอย่างเดียวและหยุดหลังสรุปผล

4) จากผลรีวิว PR #60 กรุณาแก้ไขก่อนขอ review ใหม่:
   [รายการ 8 ข้อ: อัปเดต branch จาก main + แก้ conflict, แก้ helper upload()
   ให้รองรับ file override, ทำให้เทสต์ OR ทดสอบ PNG/PDF จริง, ลบ test-note.pdf,
   เพิ่ม file_type ในเอกสาร, แก้ trailing whitespace, เพิ่ม newline ท้ายไฟล์,
   รัน test suite และรายงานผล]
   ห้ามเปลี่ยนขอบเขตฟีเจอร์นอกเหนือจากรายการนี้ เมื่อเสร็จแล้ว push การแก้ไข
   ขึ้น PR #60 และแจ้งเพื่อ review ใหม่

5) รีวิว PR #60 รอบสองจาก head ล่าสุด f84f192 โดยยังห้าม merge
   [ระบุสิ่งที่ต้องตรวจยืนยัน 9 ข้อ รวมถึง "ไม่มี regression ต่อ faculty,
   year_level, paging และ token/auth จาก PR #59" และ "merge commit aeab7b2
   ไม่ทำให้ประวัติหรือโค้ดผิดปกติ"]
   ห้าม: merge, comment ลง GitHub, approve หรือ request changes, push หรือ
   แก้ไฟล์ใด ๆ
   ถ้าทุกอย่างผ่าน ให้ระบุชัดเจนว่า "พร้อม approve" แต่ยังไม่ต้อง approve เอง

6) ส่งข้อความใน PR #60 เพื่อขอให้ reviewer คนอื่นตรวจและ approve โดยระบุว่า:
   [8 ข้อที่ต้องระบุ] แจ้งเพิ่มเติมอย่างโปร่งใสว่า commit f84f192 ถูกสร้าง
   ระหว่างการช่วยแก้ตามรีวิว จึงขอให้ผู้ร่วมทีมคนอื่นเป็นผู้ approve แทน
   ห้าม merge PR #60 และห้าม approve แทน reviewer คนอื่น

7) ตรวจสอบ PR #60 ล่าสุด แล้ว approve ได้เลยในฐานะ reviewer
   [เงื่อนไขก่อน approve 7 ข้อ] หากเงื่อนไขใดไม่ครบ ให้หยุดและรายงานก่อน
   โดยไม่ approve

8) merge PR #60 ให้เลย โดยใช้ "Create a merge commit" เท่านั้น
   [เงื่อนไขตรวจซ้ำ 5 ข้อ + ขั้นตอนหลัง merge + ข้อห้าม 4 ข้อ]

9) ตรวจสอบ AI_USAGE.md เทียบกับประวัติการทำงานและรายงานล่าสุด แล้วสร้าง PR
   เอกสารแยกสำหรับเติม prompt ที่ยังค้างเท่านั้น
   [ข้อกำหนด 8 ข้อ: ห้ามแก้โค้ด production, ห้ามแตะ
   fix/notes-service-hardening, จัดกลุ่มตาม lab, ตรวจข้อมูลซ้ำ/อ้างผิด,
   รันตรวจรูปแบบ, สร้าง branch ใหม่, เปิด PR และรายงาน diff/SHA/PR number,
   ยังห้าม merge]
```

เทียบกับ Five S's — รอบนี้กลับด้านกับ Prompt 9 และ 10 อย่างชัดเจน:

- **Specific** ผ่านเต็ม เป็นครั้งแรกในกลุ่ม prompt ที่สั่งงานระดับ PR/รีโป (prompt ที่สั่งสร้าง UI อย่าง Prompt 1 ผ่านข้อนี้มาตั้งแต่ Lab 4 แล้ว) ทุก prompt ระบุขั้นตอนเป็นข้อ ๆ ระบุไฟล์ที่ต้องอ่าน ระบุสิ่งที่ต้องตรวจทีละข้อ และระบุกลยุทธ์ merge (`Create a merge commit`) แทนที่จะปล่อยให้เลือกเอง
- **Structured** ผ่านเต็ม ทุก prompt มีบล็อกเดียวกัน: ขั้นตอน → ข้อห้าม → เงื่อนไขหยุด ("ถ้าเกิด conflict ให้หยุดทันที ห้ามแก้เอง")
- **Single task** ผ่าน แต่ละ prompt จับ PR เดียวและงานเดียว ไม่พ่วง — ตรงข้ามกับ Prompt 11 ที่เอา hardening กับสอง story มารวมรอบเดียว
- **Surrounding** ผ่าน เพราะระบุ SHA (`f84f192`, `aeab7b2`) และเลข PR ตรง ๆ ไม่ปล่อยให้เดาว่าหมายถึง head ไหน
- **Short** ไม่ผ่าน — prompt ยาวขึ้นมากจนแทบเป็น checklist ทั้งใบ แต่ความยาวเกือบทั้งหมดคือ**ข้อห้าม**กับ**เงื่อนไขหยุด** ซึ่งเป็นส่วนที่ถ้าไม่เขียนก็ต้องมาตามแก้ทีหลังอยู่ดี

**บทเรียนจริงจากรอบนี้ — สองข้อที่ตรงกันข้ามกัน:**

ข้อแรก ข้อห้ามที่เขียนไว้ล่วงหน้าได้ผลจริง จุดที่ชัดที่สุดคือรีวิวรอบแรกจับได้ว่าเทสต์ `test_filter_multiple_file_types_combine_with_or` ของ PR #60 **เขียวแบบหลอก** เพราะ helper `upload()` เขียน `form["file"] = ...` ทับค่าที่ส่งเข้ามาทุกครั้ง ทำให้โน้ตที่ตั้งใจอัปเป็น PNG ถูกบันทึกเป็น `application/pdf` เทสต์จึงผ่านเพราะเป็น pdf สองไฟล์ ไม่ได้พิสูจน์ `in_()` เลย — และรอบสองก็พิสูจน์กลับด้วยการย้อนโค้ดที่แก้แล้วดูว่าเทสต์ FAIL จริง แทนที่จะเชื่อว่า "เทสต์ผ่านแล้วแปลว่าถูก"

ข้อสอง prompt ชุดนี้ทำให้เกิดปัญหาเชิงกระบวนการที่ prompt เองไม่ได้กันไว้ คือ prompt ข้อ 4 สั่งให้ผู้รีวิวเป็นคนแก้และ push ขึ้น branch ของเจ้าของ PR แล้ว prompt ข้อ 7 ก็สั่งให้ approve งานเดียวกันนั้น ผลคือ commit `f84f192` ในสายงานของวชิรวิทย์มีชื่ออติชาติเป็นผู้เขียน และคนที่ approve ก็คือคนที่แก้เอง ซึ่งขัดกับเจตนาของกฎ "1 approve ก่อน merge" ที่ต้องการให้มีคนที่สองมองงาน · ได้บันทึกไว้ใน comment ของ PR #60 อย่างโปร่งใสแล้วและเปิดช่องให้เพิ่ม approve ซ้อนจากคนที่ไม่ได้แก้ · **รอบหน้าถ้าเจอ PR ของคนอื่นที่ต้องแก้ ควรส่งรายการที่ต้องแก้ให้เจ้าของ PR ทำเอง ไม่ push ทับ** แล้วผู้รีวิวจึงจะ approve ได้โดยไม่มีข้อกังขา

### Lab 9

#### Prompt 13 — Unit Test/TDD/Property-Based Test/CI/Saboteur (อติชาติ, ChatGPT + Claude Code, 2026-09-18)

**บริบท:** อติชาติทำงานผ่าน ChatGPT โดยให้ Claude Code ช่วยร่าง prompt ให้ทีละขั้น (อ้างโค้ดจริงในไฟล์ของโปรเจกต์ ไม่ใช่ตัวอย่างลอย ๆ จากใบงาน) แล้วเอาไปพิมพ์ใน ChatGPT เอง จากนั้นรายงานผลกลับมาให้ Claude Code ตรวจก่อนได้ prompt ขั้นถัดไป ทำสลับกันแบบนี้ตลอดทั้ง 4 ส่วนของ Lab 9

**prompt ที่ Claude Code ร่างให้ (คำต่อคำ ทยอยให้ทีละขั้นตามที่อติชาติรายงานผลกลับมา):**

```
1) Unit Test (Equivalence + Boundary) จาก validation.py
   ให้วิเคราะห์ Equivalence Partition/Boundary ของ validate_metadata และ
   validate_file แล้วเขียน pytest อย่างน้อย 5 เคสใน
   src/tests/test_notes_validation_boundary.py แบบ Arrange-Act-Assert
   ห้ามเขียนเทสต์ที่ตรวจแค่ว่าฟังก์ชันถูกเรียก ต้องตรวจ return value จริง

2) TDD FizzBuzz แบบ Red-Green-Refactor ทีละสเตปเดียว ห้ามข้ามไปเขียนโค้ด
   สมบูรณ์ทีเดียว — ให้เขียนเทสต์ 1 เคสก่อนแล้วรอผล Red, บอกโค้ดขั้นต่ำสุด
   ให้ผ่านเฉพาะเคสนั้นแล้วรอผล Green, ทำซ้ำไปทีละเคส (1, 3, 5, 15, และเคส
   non-multiple เช่น 7) แล้วค่อย Refactor แยก helper is_multiple(n, factor)
   ท้ายสุด — ทุกสเตปห้าม commit เอง ต้องรายงานผลรันจริงกลับมาก่อนไปสเตปต่อไป

3) Property-Based Test ด้วย Hypothesis บน tokens.py (hash_token,
   token_matches) ใน src/tests/test_tokens_property.py อย่างน้อย 2 property
   ที่พิสูจน์ behavior จริง (token match กับ hash ของตัวเอง, token ที่ต่าง
   กันต้องไม่ match) ห้ามเขียน property ที่เช็คแค่ isinstance

4) เพิ่ม hypothesis/pytest-cov ลง src/tests/requirements-dev.txt (คงคอมเมนต์
   เดิม) และแก้ .github/workflows/ci.yml เฉพาะ step "Run pytest" ของ job
   python-tests ให้มี --cov ห้ามแก้ job อื่น

5) Saboteur Testing: แก้เงื่อนไข boundary บนของ year_level ใน validation.py
   ให้ผิดแบบ off-by-one ชั่วคราว, รัน pytest ยืนยันว่า boundary test ที่เขียน
   ไว้ในข้อ 1 จับได้จริง, revert กลับทันทีแล้วยืนยันว่ากลับมา all passed,
   สรุปเป็น docs/saboteur-journal.md (โค้ดที่ทำผิด/เทสต์ที่ควร fail/ผลก่อน/
   test ใหม่ถ้ามี/ผลหลัง revert) ห้าม commit ทั้งโค้ดที่ทำพังและ journal
```

ทุก prompt ในชุดนี้มีเงื่อนไขหยุดร่วมกัน (ถ้าเทสต์ที่ควรผ่านกลับ fail หรือ revert แล้วยังไม่ all passed ให้หยุดรายงานก่อน ห้ามแก้ไปเรื่อย ๆ เอง) และขอบเขตที่ตัดกันทุกครั้ง (ห้ามแก้ไฟล์อื่นนอกจากที่ระบุ ห้าม commit เอง)

เทียบกับ Five S's: **Single task** ผ่านเต็ม แยกเป็น prompt ย่อยทีละสเตปของ TDD โดยเฉพาะ ไม่ยอมให้ ChatGPT ข้ามจาก Red ไป Green หลายเคสพร้อมกัน ตรงข้ามกับ prompt กว้าง ๆ ในรอบก่อน ๆ ของไฟล์นี้ **Specific** ผ่าน (ระบุไฟล์ปลายทาง, ชื่อฟังก์ชัน, จำนวน property ขั้นต่ำ, ห้ามเขียนแบบ isinstance) **Structured** ผ่าน (ขอบเขต + เงื่อนไขหยุดแยกจากงานหลักทุกรอบ) **Surrounding** ผ่าน (แปะโค้ดจริงของ `tokens.py`/`validation.py` ไปด้วยเสมอ ไม่ให้ ChatGPT เดาโครงสร้างเอง) **Short** ผ่านสำหรับ prompt เดี่ยว ๆ แต่รวมทั้งชุดยาวเพราะมีหลายสเตปจริง ๆ

**บทเรียนจริงจากรอบนี้:** การแยกงานเป็น "prompt คนสั่ง ChatGPT" กับ "Claude Code ตรวจผลจริงในเครื่องทุกรอบ" ทำให้จับข้อผิดพลาดเชิงกระบวนการได้ก่อนที่จะสะสม เช่น ตรวจพบว่าถ้าไม่เพิ่ม `hypothesis` ลง `requirements-dev.txt` ทัน CI จะพังทันทีที่ push เพราะ `pytest src/tests -v` ใน `ci.yml` ยัง import `test_tokens_property.py` ไม่ได้ — จับได้ก่อนสั่งขั้นถัดไปเพราะ Claude Code รันคำสั่งเดียวกับที่ CI จะรันจริงในเครื่องก่อนเสมอ ไม่ใช่เชื่อคำรายงานว่า "ผ่านแล้ว" เพียว ๆ

### รายการที่ยังไม่ระบุ Lab

รายการต่อไปนี้ไม่ได้ระบุ Lab ไว้ในข้อมูลเดิม จึงแยกมาไว้ท้ายหัวข้อนี้

#### Prompt 1 — Copilot inline, หน้าอัปโหลดโน้ต (อติชาติ)



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

#### Prompt 3 — หน้า note-rating (กฤตเมธ)



เครื่องมือที่ใช้จริงคือ **Gemini** (กฤตเมธยืนยันเมื่อ 2026-08-19) ส่วน comment ในไฟล์ `kittamet_note_rating_prototype.html` ที่เคยเขียนว่า "JavaScript จาก ChatGPT" เป็นข้อความที่ระบุที่มาผิด และแก้ให้ตรงแล้วใน PR #41

Prompt ที่ใช้สร้างระบบดาวและความคิดเห็น (เรียบเรียงย้อนหลังตามโครงสร้างที่ส่งให้ Gemini):

```text
ช่วยเขียน HTML, CSS และ JavaScript สำหรับ UI หน้าประเมินให้คะแนนโน้ต (Note Rating) ของเว็บ NoteShare 
โดยต้องการส่วนประกอบดังนี้:
1. การ์ดแสดงข้อมูลโน้ตที่จะให้คะแนน (ชื่อโน้ต, วิชา, ผู้ดูแล/อัปโหลด)
2. ระบบให้คะแนนเป็นดาว 5 ดวง ที่สามารถเอาเมาส์วาง (Hover) แล้วแสดงสีไฮไลท์ และเมื่อกดคลิกจะบันทึกคะแนนดาวนั้น
3. กล่อง Textarea สำหรับพิมพ์ข้อความรีวิว/ความคิดเห็นเพิ่มเติม
4. ปุ่มกด "ส่งคะแนนประเมิน" (Submit Rating)
5. สไตล์ CSS ให้เน้นความคลีน อ่านง่าย รองรับ Responsive UI
```

#### Prompt 4 — หน้าค้นหาโน้ต (วชิรวิทย์)



เครื่องมือที่ใช้คือ claude/gemini ในไฟล์ `wachirawit_search_note_prototype.html`:
```
เขียน HTML, CSS และ JavaScript สำหรับ UI หน้า ค้นหาข้อมูล ของเว็บ NoteShare เป็นโปรแกรมสำหรับการแชร์โน้ต
โดยต้องการส่วนประกอบดังนี้:
1. ช่องค้นหา พร้อมปุ่มค้นหา รองรับพิมพ์ชื่อวิชา/รหัสวิชา
2. แถบตัวกรอง (คณะ, ปีการศึกษา, ประเภทไฟล์, เรียงตาม)
3. รายการผลลัพธ์ แบบการ์ด แสดงจำนวนที่พบและตัวอย่างเอกสาร
4. ต้องบันทึกคำต้นหาโดยอัตโนมัติ
5. สไตล์ CSS ให้เน้นความคลีน อ่านง่าย
6. สร้างข้อมูลจำลองสำหรับหน้าค้นหา
```

#### Prompt 5 — ตรวจสอบและแก้หน้าค้นหาโน้ต(วชิรวิทย์)



หลังจาก push ไฟล์ `wachirawit_search_note_prototype.html ให้ทีมตรวจสอบพบว่ามีปัญหาหาด้าน XSS จึงใช้ Gemini ในการตรวจสอบหาจุดของปัญหาและแก้ไข
```
ตรวจสอบช่องโหว่ของโปรแกรมบอกจุดของปัญหาและบรรทัดที่เกิดปัญหาและเสนอแนวทางการแก้ไขที่ทำได้
```

#### Prompt 10 (US-08 Notes Service, อติชาติ, Claude Code, 2026-08-31)



**prompt จริงที่พิมพ์ (คำต่อคำ ไม่ได้ขัดเกลา):**

```
1) แล้วชิ้นงานล่ะ ควรจะเริ่มได้เลยมั้ย
2) งั้นช่วยจัดการงานของฉันในส่วนของ Project ให้หน่อยได้มั้ย เอาสักงานนึงก่อนก็ได้
```

เทียบกับ Five S's: **Single task** ชัดเจนที่สุดในบรรดา prompt ทั้งหมดที่ผ่านมา (บอกตรง ๆ ว่า "เอาสักงานนึงก่อน" คือไม่ให้ทำหลายอย่างพร้อมกัน) **Surrounding** ดีมากแต่ได้มาฟรี ๆ ไม่ใช่เพราะเขียน prompt ดี — AI อ่าน issue/milestone/assignee บน GitHub เองได้ จึงเลือก #8 ที่เป็นของอติชาติและเป็น Must ของ Sprint 1 ได้เอง ส่วน **Specific** ยังอ่อนเหมือน Prompt 2 และ 8 คือไม่ได้บอกขอบเขตทางเทคนิคเลยสักข้อ ว่าจะเอา service เดียวหรือครบสี่ตัวตาม ADR-001, จะใช้ Postgres เลยไหม, จะทำ auth ด้วยหรือเปล่า AI จึงต้องตัดสินใจเองทั้งหมด

**เขียนใหม่ให้ผ่าน Five S's — แบบที่ควรพิมพ์ตั้งแต่แรกในรอบหน้า:**

```
บริบท: รีโปนี้มี prototype กับ CI แล้ว แต่ยังไม่มีโค้ดระบบจริงใน src/
user story ระดับ Must ของ Sprint 1 ที่ปิดไปแล้วปิดด้วย prototype ที่ข้อมูล hardcoded
จึงยังไม่ผ่าน Definition of Done ระดับ Sprint ที่กำหนดว่าต้อง demo end-to-end ได้

งาน: implement issue #8 (US-08 — note metadata) ให้จบเป็น PR เดียว
ทำเฉพาะ story นี้ อย่าพ่วง story อื่นเข้ามา

ขอบเขตทางเทคนิคที่กำหนดให้ (อย่าขยายเอง):
- Flask service ตัวเดียวชื่อ notes-service ยังไม่ต้องแตกตาม ADR-001 และยังไม่ต้องมี API Gateway
- PostgreSQL ผ่าน docker-compose ไม่ต้องใช้ SQLite ใน compose
- เก็บไฟล์บนดิสก์ที่ mount เป็น volume แต่ต้องอยู่หลัง interface ที่สลับไป S3 ได้ภายหลัง
- ยังไม่ต้องทำ auth (#5/#6 ยังไม่เริ่ม) แต่เขียนเตือนความเสี่ยงไว้ในเอกสาร

ต้องส่งมอบ:
- endpoint ที่ครอบ AC ทั้ง 4 ข้อของ #8 โดยเฉพาะข้อที่ว่า metadata ต้องใช้กรอง/ค้นหาได้จริง
- unit test ของ validation (pure function) + integration test ของ API
- อัปเดต CI ให้ทดสอบเส้น upload -> filter -> download บน stack ที่รันจริง
- ADR บันทึกส่วนที่จงใจทำน้อยกว่า ADR-001 เพื่อให้ทีมรีวิวและค้านได้

เงื่อนไข: ห้ามรายงานว่าเสร็จถ้ายังไม่ได้รันเทสต์ให้เห็น output จริง
ถ้าต้องออกนอกขอบเขตข้างบน ให้หยุดถามก่อน อย่าตัดสินใจเอง
```

เทียบทีละ S: **Surrounding** ผ่าน (บอกสถานะรีโปและเหตุผลว่าทำไมต้องเป็น story นี้ ไม่ปล่อยให้เดา) **Specific** ผ่าน (ล็อกทั้ง framework, ฐานข้อมูล, วิธีเก็บไฟล์ และสิ่งที่ห้ามทำ — จุดที่ prompt จริงไม่มีเลย) **Single task** ผ่าน (หนึ่ง issue หนึ่ง PR กันการพ่วง story อื่น) **Structured** ผ่าน (แยกบริบท/ขอบเขต/สิ่งที่ต้องส่งมอบ/เงื่อนไขออกจากกัน) **Short** พอใช้ — ยาวกว่าที่ควรอยู่บ้าง แต่ความยาวเกือบทั้งหมดคือข้อจำกัดที่ถ้าไม่เขียนก็ต้องมาแก้ทีหลังอยู่ดี

**บทเรียนจริงจากรอบนี้:** prompt ที่กว้างไม่ได้ทำให้งานพัง เพราะ AI เลือกขอบเขตแล้วบันทึกเป็น ADR-003 ให้ทีมค้านได้แทนที่จะเงียบ ๆ แต่นั่นคือการแก้ปัญหาที่ปลายทาง ถ้าเขียนขอบเขตให้ชัดตั้งแต่ต้นก็ไม่ต้องมาลุ้นว่า AI จะเดาตรงหรือเปล่า — บทเรียนเดียวกับ Prompt 2 และ 8 ที่ยังไม่ได้แก้สักที คือ prompt แบบ "ดูให้หน่อย" เหมาะกับตอน**สำรวจ** แต่ตอน**ลงมือ**ต้องล็อกขอบเขตก่อนเสมอ

## ส่วนที่รับจาก AI ตรงๆ (ไม่แก้)

ส่วนที่ยังเป็นของ AI แบบไม่ได้แก้เลย เท่าที่ตามย้อนหลังได้:

| ส่วน | ที่มา | สถานะ |
| --- | --- | --- |
| `prototypes/sprint1/index.html` และ `prototypes/sprint1/style.css` | Claude Code (2026-08-19) | generate ทั้งไฟล์ อติชาติอ่านและรันทดสอบใน browser ก่อน commit แต่ไม่ได้แก้บรรทัดใด |
| หัวข้อ "Next step (Sprint 2)" ใน `prototypes/sprint1/README.md` | Claude Code (2026-08-19) | AI ร่างโดยอ้างเนื้อหา ADR-001 อติชาติตรวจว่าลำดับงานตรงกับที่ทีมคุยกันไว้ ไม่ได้แก้เนื้อหา |
| script เซ็ต state ก่อนถ่าย screenshot (อยู่ใน scratchpad ไม่ commit) | Claude Code (2026-08-19) | รับมาทั้งก้อน ใช้ครั้งเดียวเพื่อถ่ายภาพ ไม่ได้เข้า repo |
| C4 diagram (SVG) และเนื้อหา ADR-001/ADR-002 | Claude Code | AI ร่าง อติชาติแก้ถ้อยคำและตัวเลือกใน Alternatives บางส่วน จึงไม่ใช่ "ไม่แก้" ทั้งก้อน |
| ฟังก์ชันการคำนวณและ Event Listener ของดาวใน `kittamet_note_rating_prototype.html` | Gemini (กฤตเมธ) | รับ Logic การคำนวณ Hover/Click เปลี่ยนสีดาวจาก Gemini มาตรงๆ แล้วนำมาครอบสไตล์ CSS ของการ์ดเอง |
| `services/stats-service/app.py`, root `Dockerfile`, ส่วนที่เพิ่มใน `.dockerignore` | Claude Code (2026-08-23) | generate ทั้งไฟล์/ส่วน อติชาติตรวจ syntax และเทียบ checklist Lab 6 (USER non-root, EXPOSE, pinned base image version) ก่อน commit และภายหลังตรวจผลจริงจากการ build/run/push (ดูแถวถัดไป) แล้ว |
| คำสั่ง `docker build`/`run`/`tag`/`push` และการแก้ `docker/README.md` ให้ตรงกับผลจริง | Claude Code (2026-08-23) | Claude รันคำสั่งเองทั้งหมด (ยกเว้น `docker login` ที่อติชาติรันเองเพื่อไม่ให้ token หลุด) อติชาติตรวจ output ทุกคำสั่งก่อนอนุมัติให้ push branch |
| `prototypes/sprint1/note-utils.js` และ `note-utils.test.js` ทั้งไฟล์ (Lab 7) | Claude Code (2026-08-26) | generate ทั้งสองไฟล์ อติชาติอ่านทุกบรรทัด รันเทสต์เองด้วย `node --test` และเปิดหน้าเว็บจริงเทียบก่อน/หลัง แต่ไม่ได้แก้โค้ดในไฟล์เพิ่มเติม รายละเอียดดู [docs/refactoring-journal.md](docs/refactoring-journal.md) |
| `.github/workflows/ci.yml`, `src/tests/*` และ `docs/testing/readme.md` (Lab 8) | Claude Code (2026-08-31) | generate ทั้งหมด อติชาติตรวจว่าเทสต์รันผ่านจริงทั้งสองชุดและตรวจว่าตาราง test report ตรงกับ output ที่เห็น (รวมถึงแถวที่ยังไม่ได้รัน ซึ่งถูกกำกับว่า "รอ CI" ไม่ใช่ "ผ่าน") แต่ไม่ได้แก้โค้ดในไฟล์เพิ่มเติม |
| `services/notes-service/*` ทั้งโฟลเดอร์, `docker-compose.yml`, `src/tests/test_notes_*.py`, ADR-003 (US-08) | Claude Code (2026-08-31) | generate ทั้งหมด อติชาติตรวจ endpoint เทียบ AC ของ #8 ทีละข้อ และตรวจว่าเทสต์ที่อ้างว่าผ่านนั้นรันจริง แต่ไม่ได้แก้โค้ดเพิ่ม · ขอบเขตที่ AI เลือกเอง (service เดียว, เก็บไฟล์บนดิสก์, ยังไม่มี auth) ถูกบันทึกไว้ใน [ADR-003](docs/architecture/adr/0003-tracer-bullet-scope.th.md) เพื่อให้ทีมรีวิว/ค้านได้ ไม่ใช่ตัดสินใจเงียบ ๆ |

ส่วนที่ตามหลักฐานแล้วน่าจะเป็นงานที่คนเขียน/แก้เอง ไม่ใช่รับจาก AI ตรง ๆ: ฟังก์ชัน `esc()` กัน XSS และการ clamp ค่าใน `stars()` ของหน้าค้นหา ก่อน Lab 7 (เข้ามาในรอบที่ PR #37 ถูก CHANGES_REQUESTED จึงเป็นผลจากรีวิวของคนในทีม) แต่ใน Lab 7 ฟังก์ชันสองตัวนี้ถูกย้าย/เขียนใหม่เป็น `escapeHtml`/`formatStars` ใน `note-utils.js` โดย Claude Code แล้ว (แถวด้านบน) จึงไม่ใช่ "ไม่แก้จาก AI" อีกต่อไปสำหรับตำแหน่งใหม่นี้ ส่วนที่ยังเป็นของคนเขียนเองเหมือนเดิม: การตัดสินใจเรื่อง Tracer vs Prototype และเนื้อหา reflection รายบุคคลทั้งสามไฟล์

>  **TODO:** วชิรวิทย์ — ตารางนี้ยังไม่ครบงานของตัวเอง ช่วยเติมส่วนที่รับจาก AI แบบไม่แก้ของตัวเอง และแก้แถวที่ระบุผิดด้วย
