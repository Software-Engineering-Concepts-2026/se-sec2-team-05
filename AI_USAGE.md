# AI Usage Log

บันทึกการใช้เครื่องมือ AI (GitHub Copilot, ChatGPT, Claude, Gemini ฯลฯ) ในการทำโปรเจกต์ NoteShare ของทีม The Builders

**นโยบายของทีม:** เราใช้ AI เป็นผู้ช่วยร่าง (drafting) และ pair-programming เท่านั้น ไม่ใช่ผู้ตัดสินใจแทนคน — งานทุกชิ้นที่ AI ช่วยสร้างจะถูกสมาชิกในทีมอ่าน ตรวจ และแก้ไขก่อน commit เสมอ และต้องผ่าน PR review ตาม Git Workflow ที่ตกลงกันไว้ใน README (อย่างน้อย 1 คน approve ก่อน merge เข้า `main`) ความรับผิดชอบต่อความถูกต้องของโค้ด/เอกสารสุดท้ายเป็นของผู้เขียนที่เป็นมนุษย์ ไม่ใช่ของเครื่องมือ AI

ไฟล์นี้เป็น log ที่เปิดเผยตามจริง ไม่ปิดบังหรือลดทอนการใช้ AI — จุดประสงค์คือความโปร่งใส ไม่ใช่การทำให้ดูเหมือนเขียนเองทั้งหมด

## Log

| Date/PR | Contributor | Tool(s) | What it was used for | How output was reviewed/edited |
| --- | --- | --- | --- | --- |
| 2026-07-10, PR #35 | อติชาติ ผาแสนเถิน | GitHub Copilot, ChatGPT | สร้าง interactive prototype หน้าอัปโหลดโน้ต (commit `cca0aa0` — "implement interactive upload-note mockup using copilot/chatgpt") | อติชาติตรวจและแก้ HTML/CSS ที่ generate มาก่อน commit |
| 2026-07-10, ส่วนหนึ่งของ PR #37 | วชิรวิทย์ ศรีทอง | GitHub Copilot, Claude, Gemini | สร้าง prototype หน้าค้นหาโน้ต (`wachirawit_search_note_prototype.html`/`.css`) พร้อม wireframe ของหน้าค้นหา และแก้ชื่อไฟล์ wireframe (commits `e75dba8`, `7a455c6`, `0ea55bd`) · หมายเหตุ: ข้อความ commit `e75dba8` และ `7a455c6` เขียนว่า "registration mockup" แต่เนื้อหาจริงคือหน้าค้นหา (`e75dba8` เพิ่มแค่ไฟล์ wireframe, `7a455c6` เพิ่ม html/css ของหน้าค้นหา) ไม่เคยมีหน้าลงทะเบียนใน repo · ใช้ Gemini ตรวจหาช่องโหว่ XSS และเสนอวิธีแก้ (ดู Prompt 5) | วชิรวิทย์ตรวจและแก้ HTML/JavaScript หลัง generate ก่อน commit `0ea55bd`: เพิ่ม `<label>` ให้ช่องกรอง, เพิ่ม `esc()` กัน XSS, clamp ค่าใน `stars()`, ปรับ logic ประวัติการค้นหา (ไม่บันทึกคำสั้นกว่า 2 ตัวอักษร, พิมพ์ต่อจากคำล่าสุดให้ทับ) · ไม่ได้แก้ CSS และข้อมูลจำลองหลัง commit แรก (ดูตาราง "ส่วนที่รับจาก AI ตรงๆ") |
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
| 2026-09-06, PR #57 + hardening + US-19/US-20 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจสถานะโปรเจกต์ทั้งรีโปแล้วพบว่า PR #56 ถูก merge เข้า `feature/lab8-ci-tests` แทน `main` ทำให้ Notes Service ไม่เคยขึ้น `main` เลย จึงเปิด PR #57 แก้ · งาน hardening: ตั้ง `MAX_CONTENT_LENGTH` + errorhandler 413, clamp `limit`/`offset` ที่ขอบล่าง, เพิ่ม `.venv/` ใน `.gitignore`, เขียนเทสต์ commit ล้มแล้วไม่เหลือไฟล์กำพร้าที่ค้างไว้ใน test plan · งาน US-19/US-20: `PATCH`/`DELETE /notes/<id>`, `tokens.py` (edit token ต่อโน้ต), คอลัมน์ `edit_token_hash`/`updated_at`, โหมด partial ของ `validate_metadata`, ADR-004 ทั้ง EN/TH, เทสต์ 13 เคส และ smoke test ของ edit/delete ใน CI | อติชาติสั่งให้รันเทสต์จริงทุกครั้งก่อนยอมรับ — `pytest src/tests` ผ่าน 48/48 และ `node --test` ผ่าน 7/7 บนเครื่อง · อติชาติเป็นคนเลือกแนวทางตรวจสอบเจ้าของเองจากสามตัวเลือกที่เสนอมา (uploader_name / edit token / รอ Auth Service) โดยเลือก edit token เพราะเป็นทางเดียวที่บังคับ AC "เจ้าของเท่านั้น" ได้จริงและทดสอบได้ · ระหว่างทางอติชาติสั่งแก้ข้อเสนอเดิมเรื่อง `MAX_CONTENT_LENGTH` ที่ตั้งเท่าขนาดไฟล์สูงสุดพอดี ซึ่งจะทำให้ไฟล์ 20 MB ถูกปฏิเสธเพราะ multipart overhead จึงเผื่อไว้ 1 MB · job `docker-build` ยังไม่ได้รัน local เพราะ Docker daemon ไม่ได้เปิด จึงรอผลจาก CI ไม่ได้เขียนใน test report ว่าผ่านแล้ว · **อัปเดต 2026-10-01:** job `docker-build` (Build & smoke-test stack) ผ่านบน CI แล้วทั้ง 3 PR — #57 ([run 34027097667](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/34027097667)), #58 ([run 34128717022](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/34128717022)), #59 ([run 34130902414](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/actions/runs/34130902414)) |
| 2026-09-18, feature/lab9-testing | อติชาติ ผาแสนเถิน | ChatGPT, Claude Code (Anthropic) | Lab 9 (Unit Test/TDD/Property-Based Test/CI/Saboteur): Claude Code อ่านโค้ดจริงในรีโปแล้วร่าง prompt ให้อติชาติเอาไปสั่ง ChatGPT ทำทีละขั้น ได้ผลลัพธ์คือ `src/tests/test_notes_validation_boundary.py` (19 boundary/equivalence test ของ `validate_metadata`/`validate_file`), `src/fizzbuzz.py` + `src/tests/test_fizzbuzz.py` (TDD kata ครบ Red-Green-Refactor 4 รอบ + helper `is_multiple`), `src/tests/test_tokens_property.py` (2 property ด้วย Hypothesis บน `tokens.py`), แก้ `src/tests/requirements-dev.txt` (เพิ่ม `hypothesis`, `pytest-cov`) และ `.github/workflows/ci.yml` (เพิ่ม `--cov` ใน job `python-tests`), `docs/saboteur-journal.md` (เจาะ boundary บนของ `year_level` แบบ off-by-one แล้ว revert) | อติชาติรัน ChatGPT เองทีละขั้นแล้วรายงานผลกลับมาให้ Claude Code ตรวจ — Claude Code เปิด/รันไฟล์จริงในเครื่องเพื่อยืนยันทุกรอบ (diff, `pytest -v`, coverage report) ก่อนให้ prompt ขั้นถัดไป ไม่เชื่อรายงานเปล่า ๆ · commit history ถูกแยกย่อยตามลำดับ Red-Green-Refactor จริงที่เกิดขึ้น ไม่ใช่ squash เป็นก้อนเดียว |
| 2026-09-25, feature/auth-service | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจสถานะงานทั้งหมด → merge PR #63 ตามคำสั่ง → วิเคราะห์ #5/#6 เทียบ NFR-004/005/007, C4, ADR-003/004 แล้วเสนอแผนให้เลือก → เขียน User & Auth Service ใหม่ทั้งตัว (US-05/US-06): `services/auth-service/` (`app.py`, `auth_models.py`, `credentials.py`, `auth_tokens.py`, `Dockerfile`, `requirements.txt`, `README.md`), เทสต์ 73 เคสใน `test_auth_credentials.py`/`test_auth_tokens.py`/`test_auth_api.py`, แก้ `conftest.py`, เพิ่ม service ใน `docker-compose.yml`, เพิ่ม install/coverage/health/smoke step ใน `ci.yml`, ADR-005 ทั้ง EN/TH, อัปเดต README ราก + architecture README ทั้งสองภาษา + test plan | อติชาติเป็นคนตัดสินใจเองทั้ง 6 ข้อที่ AI เสนอมา (แยกเป็น 2 PR, ให้ PR ถัดไปใช้ `Refs #31` โดยไม่เปลี่ยนผู้รับผิดชอบ, ผู้ใช้ตั้ง `display_name` เอง 1–120 ตัวอักษร, อ่านโดเมนจาก `ALLOWED_EMAIL_DOMAINS` ค่าเริ่มต้น `up.ac.th`, JWT อายุ 8 ชั่วโมงไม่มี refresh token แต่มี session ฝั่งเซิร์ฟเวอร์ให้ logout มีผลทันที, ตรวจใบงานก่อนตั้งชื่อ branch) และสั่งให้บันทึกเหตุผลที่ scrypt เทียบเท่า bcrypt ไว้ใน ADR · `pytest src/tests` ผ่าน 153/153 และ `node --test` ผ่าน 7/7 บนเครื่อง · ลองทำโค้ด auth พังชั่วคราว 4 จุดแล้วทุกจุดมีเทสต์ fail จริงก่อน revert · ระหว่างทาง Claude ตรวจ source ของ Werkzeug แล้วพบว่าค่า default ของ scrypt (N=2^15) ต่ำกว่าขั้นต่ำของ OWASP จึงตั้งค่า N=2^17 เองและเขียนเทสต์กันค่าเปลี่ยน · step DK-05 ใน CI รันเทียบกับ service จริงบน SQLite ได้ `auth OK` แต่บน Postgres ยังรอผลจาก CI เพราะ Docker daemon ไม่ได้เปิด · รอบแรกสั่งห้าม commit/push ไว้ แล้วสั่งให้รีวิว diff เทียบ #5/#6, NFR-004/005/007 และขอบเขต PR A ก่อนจึงค่อย commit แยกตามเรื่องและ push โดยยังไม่เปิด PR |
| 2026-09-27, feature/notes-require-login | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจสถานะ PR #62 และ branch ใหม่ `feature/preview-note` บน GitHub จริง → approve และ merge PR #62 ตามคำสั่งทีละขั้น (ตรวจเงื่อนไขซ้ำก่อนทุกครั้ง) → เสนอแผน PR B (US-31, Refs #31) ให้เลือก 4 ข้อ → ทำ PR B: `services/notes-service/identity.py` (ตรวจ Bearer token ผ่าน `GET /auth/me` ด้วย urllib), `POST /notes` ต้อง login และเอาชื่อผู้อัปโหลดจากบัญชี, คอลัมน์ `uploader_id`, เลิกรับ `uploader_name` จากฟอร์ม, `Dockerfile`/`docker-compose.yml`, smoke step DK-06 ใน `ci.yml` และแนบ token ให้ step เดิม, เทสต์ใหม่ใน `test_notes_api.py` + `test_notes_identity.py` (ยก auth-service ตัวจริงเป็น HTTP server ในเทสต์), README ของ notes-service/ราก/architecture ทั้งสองภาษา, test plan | อติชาติตัดสินใจเอง 4 ข้อจากทางเลือกที่เสนอ (เพิ่ม `uploader_id`, เมิน `uploader_name` ในฟอร์มแทนการตอบ 400, ใช้ urllib ไม่เพิ่ม dependency, ไม่เขียน ADR ใหม่) และล็อกกรอบไว้ก่อนเริ่ม (ตรวจผ่าน `/auth/me`, inject identity แบบเดียวกับ storage, คง edit token ของ ADR-004, `Refs #31` เท่านั้น) · `pytest src/tests` ผ่าน 181/181 coverage 99% และ `node --test` ผ่าน 7/7 · ลองให้ `POST /notes` ปล่อยผ่านเมื่อ token ใช้ไม่ได้ มีเทสต์ fail 5 ตัวก่อน revert · smoke step ทั้ง 6 ใน `ci.yml` ผ่านเมื่อรันกับ service จริงบน SQLite แต่บน compose + Postgres ยังรอผล CI เพราะ Docker daemon ไม่ได้เปิด · สั่งห้าม commit/push/เปิด PR ไว้ตลอดรอบนี้ |
| 2026-09-27, PR #66 (feature/safety-net, Lab 12B) | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | Lab 12B Safety Net Sprint: merge PR #65 ตามคำสั่ง → วัด coverage ของ `validation.py` กับ `credentials.py` แล้วเสนอฟังก์ชัน `email_error()` พร้อมรายการ test case (happy/edge/error) → เขียน `src/tests/test_email_error.py` 9 ตัว (AE-09 `"a@"` เป็น `xfail(strict=True)`), เพิ่ม AE-01..09 ใน `docs/testing/readme.md` → เพิ่ม `ruff.toml` + job `lint` ใน `ci.yml` และลบ import ที่ไม่ได้ใช้ใน `test_notes_api.py` → push + เปิด PR #66 → ร่าง `docs/safety-net.md` ทั้ง 5 หัวข้อ → แกล้งทำเทสต์พังเพื่อเก็บหลักฐาน แล้วแก้กลับ | อติชาติเลือกเองว่า `"a@"` ควรได้ error รูปแบบ (ไม่ใช่ error โดเมนแบบที่โค้ดตอบอยู่) และสั่งห้ามแก้ `credentials.py` จึงเก็บเป็น xfail · สั่งทีละเฟส แต่ละเฟสมีเงื่อนไขหยุด (เทสต์เดิมแดง / conflict / CI แดง) · `pytest src/tests` ผ่าน 189 + xfail 1 coverage 99% (`credentials.py` 100%) · `ruff check .` ผ่าน · CI บน PR #66 ผ่านครบ 4 job และเปิด log ยืนยันว่ารัน ruff กับ pytest จริง ไม่ใช่เขียวหลอก · โค้ดเทสต์และ CI ในรอบนี้ AI เขียนทั้งหมด (ดูตาราง "ส่วนที่รับจาก AI ตรงๆ") |
| 2026-09-26 ~ 2026-09-28, branch `feature/preview-note` | วชิรวิทย์ ศรีทอง | Claude Code (Anthropic) | US-11 (#11) — Preview Note Before Download: เพิ่ม `GET /notes/<id>/preview` ให้ผู้ค้นหาดูตัวอย่างโน้ตได้โดยไม่ต้องดาวน์โหลดไฟล์เต็ม (`services/notes-service/preview.py` เป็น pure function แนวเดียวกับ `validation.py`) — รูปภาพ (PNG/JPEG) ย่อขนาดเหลือกว้างไม่เกิน 800px, PDF render เฉพาะหน้าแรกด้วย `pypdfium2` แล้วย่อขนาดเดียวกัน ตัวอย่างถูกแคชไว้ใต้ `previews/` ในรอบแรกที่มีคนขอ และลบตามเมื่อโน้ตต้นฉบับถูกลบ เนื้อไฟล์ตรวจด้วย Pillow/pypdfium2 จริง ไม่เชื่อ mimetype ที่ผู้ใช้ส่งมา ไฟล์เสีย/ผิดชนิด/ใหญ่ผิดปกติตอบ `422 preview_unavailable` แทนที่จะหลุดเป็น `500` · เขียนเทสต์ 25 เคสใน `src/tests/test_notes_preview.py` (ครอบทั้ง endpoint และ `render_preview()` ตรง ๆ) · แก้บั๊ก 2 จุดที่พบหลังจากนั้น: (1) `Dockerfile` ลืม copy `preview.py` เข้า image ทำให้ container พังตอน start ซึ่งเทสต์ระดับ unit จับไม่ได้เพราะ import จาก source tree ตรง ๆ ไม่ได้รันผ่าน image จริง ต้อง verify ผ่าน `docker compose` ถึงจะเจอ (2) route preview ส่ง open file handle ให้ `send_file` ตรง ๆ ทำให้ handle ค้างจน server ปิด response เอง แก้เป็นอ่านไบต์แล้วปิดไฟล์เองทันที ตัดปัญหา `ResourceWarning` ที่ขึ้นทุกเทสต์ · หลัง merge `origin/main` เข้ามา (ซึ่งมี `feature/notes-require-login` ที่บังคับ login ก่อนอัปโหลด) helper `upload()` ของไฟล์เทสต์นี้เขียนไว้ก่อนหน้านั้นจึงไม่ได้แนบ auth header ทำให้เทสต์ทั้งไฟล์พังเป็น `401` แทน `201` ต้องแก้ให้ reuse `FakeIdentity`/`AUTH_HEADER` จาก `test_notes_api.py` แบบเดียวกับไฟล์เทสต์อื่นของ notes-service | ยืนยันด้วยการรันจริงสองระดับ: unit test ผ่าน `pytest` และ manual verify ผ่าน `docker compose` จริง (เห็น PNG/PDF preview render ได้, PDF ปลอมตอบ 422, ไฟล์ตัวอย่างถูกเก็บใต้ `/data/notes/previews`) — จุดที่พบบั๊ก Dockerfile คือได้มาจากขั้นตอน verify ผ่าน container จริงนี้เอง ไม่ใช่จาก unit test ที่เขียวอยู่แล้ว · การแก้ resource-leak (ปิดไฟล์เอง) มาจากอ่าน `ResourceWarning` ที่ pytest แสดงออกมาจริงตอนรันเทสต์ ไม่ได้เดา · การแก้ auth header ในเทสต์เพื่อให้สอดคล้องกับ pattern เดิมของ notes-service (ดู `test_notes_api.py`/`test_notes_identity.py`) แทนที่จะเขียน helper แยกใหม่ · **เอกสารของรอบนี้ทำย้อนหลัง (2026-09-28)** หลังโค้ดถูก commit ไปแล้ว: เพิ่มหัวข้อ 2.12 ใน `docs/testing/readme.md` (NP-01..25 ตรงกับชื่อ test function จริงในไฟล์), เพิ่ม endpoint และหัวข้อ `GET /notes/<id>/preview` ใน `services/notes-service/README.md`, และแถวนี้ใน `AI_USAGE.md` — รันแยกยืนยันอีกครั้งว่า `test_notes_preview.py` ผ่านครบ 25/25 ก่อนเขียนตัวเลขลงเอกสาร (เครื่องที่ใช้เขียนมี Python 3.14 เป็นค่าเริ่มต้นซึ่ง SQLAlchemy ที่ pin ไว้ยังใช้ไม่ได้ จึงรันด้วย Python 3.13 แทน ไม่เกี่ยวกับโค้ดของ #11 และ CI ใช้ 3.12 อยู่แล้ว) · **รอบตรวจโค้ดเพิ่มเติม (2026-09-28):** อ่าน `preview.py`/route/`storage.py`/`Dockerfile` เทียบหา bug จริง (path traversal, decompression bomb, race condition, thread-safety ของ pdfium lock) ไม่พบจุดที่ทำงานผิด แต่พบ test-coverage gap 2 จุดแล้วแก้: (1) `test_read_endpoints_stay_open_without_login` (NA-25) ไม่ได้รวม `/preview` เข้าไปด้วย ทั้งที่ endpoint นี้ตั้งใจให้เปิดแบบเดียวกับ `/download` (2) ไม่มี smoke test บน container จริงที่ยิง `/preview` เลย ทั้งที่บั๊ก Dockerfile ที่เจอไปแล้ว (ลืม copy `preview.py`) เป็นบั๊กที่ unit test จับไม่ได้เพราะ import จาก source tree ตรง ๆ — เพิ่ม step ใหม่ใน `ci.yml` (`DK-07`) ที่อัปโหลด PNG จริงผ่าน container แล้วตรวจ `Content-Type`/PNG signature ของ `/preview` และเคส 422 ของไฟล์ปลอม · รอบตรวจโค้ดเพิ่มเติมนี้ verify ด้วยของจริงทั้งสองชั้น ไม่ใช่แค่อ่านโค้ดเดา: รัน `pytest src/tests/test_notes_api.py src/tests/test_notes_preview.py -v` ผ่านครบ 72/72 (รวมเคสที่แก้), รัน `ruff check .` ผ่าน และที่สำคัญคือรอบนี้ Docker Desktop เปิดอยู่จริง (ต่างจากรอบก่อนหน้าที่ไม่มี daemon) จึงรัน `docker compose up -d --build` ขึ้นทั้ง stack จริงแล้วจำลอง step `DK-07` ทีละคำสั่งด้วยมือผ่าน `curl` เพื่อยืนยันว่า script ที่เขียนลง `ci.yml` ใช้ได้จริงก่อนจะเชื่อว่า CI จะเขียว (ระหว่างทางเจอว่า volume Postgres เก่าจากรอบทดสอบก่อนหน้ายังไม่มีคอลัมน์ `uploader_id`/`download_count` ทำให้ upload แรก 500 — เป็นปัญหาของ local volume ที่ไม่มี migration ตามที่เอกสารเดิมเตือนไว้อยู่แล้ว ไม่ใช่บั๊กของ #11 แก้ด้วย `docker compose down -v` แล้วขึ้นใหม่) |
| 2026-09-21 ~ 2026-10-01, review PR #62 #67 #68 #69 #70 #71 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ช่วยรีวิว PR ของเพื่อนในทีม: ดึงสถานะ PR/CI จาก GitHub, รันเทสต์ทั้งชุดแบบเดียวกับ CI (`pytest src/tests`) ใน worktree แยกที่ merge กับ `main` ล่าสุด, ไล่หาบั๊กด้วย input แบบที่ผู้ใช้จริงส่ง, ลองแก้เองใน worktree ก่อนเสนอวิธีแก้ และร่างข้อความ review/comment · สิ่งที่พบ: #62 (US-12) `download_count` เพิ่มทั้งที่ดาวน์โหลดตอบ 500 · #67 (US-11) รูปจากมือถือที่มี EXIF orientation กลับด้าน และ PDF ขนาด A4 ได้ preview กว้าง 801px เกินขีด 800 · #68 (US-14) รอบแรก comment-service แยกตัว start ไม่ขึ้นและ token ปลอมที่เซ็นด้วย secret ค่าเริ่มต้นได้ 201, รอบสองเทสต์อยู่นอก `src/tests` จึงไม่ถูก CI รัน และลบโน้ตแล้ว comment ค้าง · #69 (US-16) ชื่อโมดูล `models`/`storage` ชนกับ notes-service จนเทสต์ทั้งชุด collect ไม่ได้, รอบสอง `identity.py` ชนกับ notes-service จนเทสต์ไม่เคยโหลดไฟล์ของ stats เลย · #70 (US-26) จับคู่แถว test plan กับ test function จริงทีละแถว · #71 (US-15) ลบโน้ตที่มีคนกด favorite บน Postgres จะชน foreign key ได้ 500 | ทุก finding ที่ให้แก้มีผลรันจริงประกอบ ไม่ได้อ่าน diff แล้วเดา เช่น เอาบรรทัดที่แก้ออกแล้วเทสต์แดงจริง, เปิด `PRAGMA foreign_keys=ON` บน SQLite เพื่อจำลองพฤติกรรมของ Postgres (#71), เช็ค `sys.modules` ว่าโหลดไฟล์ไหน (#69) · อติชาติอ่านผลวิเคราะห์แล้วตัดสินใจเองทีละขั้น ทั้งเรื่องโพสต์หรือไม่, เป็น comment หรือ request-changes, approve และ merge แต่ละขั้นต้องมีคำสั่งแยกกัน (approve/merge #67 และ #70 ทำหลังตรวจ head SHA ซ้ำ ส่วน approve/merge #62 อยู่ในแถว 2026-09-27) · อติชาติกำหนดให้ตัวเองเป็นผู้รีวิวเท่านั้น ไม่ push แก้โค้ดใน branch ของเพื่อน ให้เจ้าของ PR แก้เอง · ข้อจำกัด: Docker daemon ไม่ได้เปิดตลอดช่วงนี้ บั๊กที่เกิดเฉพาะบน Postgres (#71) จึงยืนยันผ่าน SQLite ที่เปิด foreign key แทน และ `?topic=` ของ #70 ยังไม่ได้ทดสอบบน Postgres จริง |
| 2026-10-01, branch `feature/web-search-preview` | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจสถานะ PR ที่เปิดอยู่ → merge PR #72 ตามที่เลือก → เสนอทางเลือกการต่อ frontend ให้เลือก 3 เรื่อง → ทำหน้าค้นหา + preview ตัวจริงใน `web/` (`index.html`, `app.js`, `search-utils.js` + เทสต์ 15 ตัว, `style.css`), nginx gateway (`web/nginx.conf`, `web/Dockerfile`, service `web` ใน `docker-compose.yml`), step `node --test` ของ `web/` และ smoke step DK-08 ใน `ci.yml`, ADR-006 ทั้งสองภาษา, README ของ `web/` และ architecture, test plan หัวข้อ 2.13 | อติชาติเลือกเองทุกทางแยกจากเมนูที่เสนอ: nginx gateway แทน CORS หรือให้ Flask เสิร์ฟหน้าเว็บ (เพื่อไม่แตะ `services/notes-service/app.py` ที่ #68/#69 conflict อยู่), slice แรกเป็นค้นหา + preview (ปิด AC3 ของ #11 และ #31), โฟลเดอร์ใหม่ `web/` โดยไม่แก้ `prototypes/sprint1/`, และอนุมัติแผนทั้งชุดก่อนลงมือ · `node --test` ใน `web/` ผ่าน 15/15 · ตรวจบน Chrome กับ notes-service และ auth-service ตัวจริงบน SQLite ผ่านสคริปต์ที่ทำตัวแทน nginx: ปิด preview ด้วย Esc/ฉากหลัง/ปุ่ม ✕ แล้ว scroll เท่าเดิมและ focus กลับปุ่มเดิม · ตัว nginx จริงยังรอผล DK-08 บน CI เพราะ Docker daemon ไม่ได้เปิด · ตรวจด้วย `git merge-tree` แล้วว่า branch นี้ไม่เพิ่มไฟล์ conflict ให้ #68/#69 · ยังไม่ได้ commit/push/เปิด PR |
| 2026-10-02, merge PR #73 และแก้ conflict/approve/merge PR #68 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจสถานะ PR → เปิด #31 ที่ถูกปิดด้วยมือก่อน merge กลับมา แล้ว merge #73 (`main` = `d857bab`, #11 และ #31 ปิดโดย PR) → รวมการแก้ conflict ที่เตรียมไว้ใน branch local `prep-68-merge` เข้ากับ `1f0eb2c` ของกฤตเมธ แล้ว merge `main` ใหม่ตามเข้าไป push ขึ้น `feature/issue-14-comment` (`c784a8c`, `adcb7ed`) → comment อธิบายว่าแก้อะไร → approve → merge #68 (`main` = `65caf42`, #14 ปิดโดย PR) | อติชาติเลือกทุกขั้นจากเมนูที่เสนอ · ก่อน push รัน `pytest src/tests` ได้ 268 passed + 1 xfailed, `ruff check .` ผ่าน, `node --test` ของ `web/` 15/15 · CI 4/4 ผ่านที่ `adcb7ed` · approve โดยอติชาติซึ่งเป็นคนแก้ conflict เอง (ทางที่เสนอเป็นตัวแนะนำคือ dismiss review ของตัวเองแล้วให้วชิรวิทย์ approve) จึงเขียนไว้ใน review ว่าคนแก้กับคน approve เป็นคนเดียวกันและส่วนที่แก้มีแค่การรวมโค้ด · ระหว่างทำ `git merge -F -` ใน Git Bash ไม่อ่านข้อความจาก stdin ทำให้ merge ผิดลำดับและเกิด conflict ใน branch local จึง `git merge --abort` แล้วทำใหม่ด้วยไฟล์ข้อความ tree สุดท้ายตรงกับชุดที่รันเทสต์ ไม่มีอะไรหลุดขึ้น remote |
| 2026-10-02, branch `feature/web-login-upload` | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ทำหน้าเข้าสู่ระบบ/สมัครสมาชิก (`web/login.html`, `login.js`), หน้าอัปโหลด (`upload.html`, `upload.js`), แถบเมนูบนทุกหน้า (`site.js`), pure function `session-utils.js` + `upload-utils.js` พร้อมเทสต์ 23 ตัว, แก้ `index.html`/`style.css`/`Dockerfile` ของ `web/`, step DK-08 ใน `ci.yml`, README ของ `web/` และ test plan หัวข้อ 2.14 | อติชาติเลือก 4 เรื่องจากเมนู: เก็บ token ใน `sessionStorage`, แยกหน้า + แถบเมนูบน, ขอบเขต login + สมัคร + logout + upload (แก้/ลบโน้ต, favorites, comments ไว้รอบหน้า) และหยุดก่อน commit · `node --test` ใน `web/` ผ่าน 38/38 · DK-08 ตัวใหม่ผ่านกับสคริปต์ที่ทำตัวแทน nginx · ตรวจบน Chrome กับ notes-service และ auth-service ตัวจริงบน SQLite (รายละเอียดท้ายหัวข้อ 2.14 ของ test plan) · ไม่แตะโค้ดของ service ใด · ยังไม่ได้ commit/push/เปิด PR |
| 2026-10-04, ตรวจ/approve/แก้ conflict/merge PR #78 และแก้ conflict PR #79 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจ commit ใหม่ของ #78 (`5b0206c`, แก้แค่ docs) เทียบกับรอบก่อน, ร่างข้อความ approve, รวม `main` เข้า #78 แล้วแก้ conflict กับ #77 (ย้าย `delete(NoteAccess)` เข้า `delete_note_record()`, เก็บแถวทั้งสองใน `src/tests/README.md`, ลบบรรทัดว่างที่ทำให้ตาราง NA-75..88 ขาด) เป็น `ac98b5d`, merge #78 (`37ac3aa`), รวม `main` เข้า #79 แล้วเลื่อนแถว NA ของ Issue #18 เป็น NA-89..96 (`3c955cc`) และแก้ body ของ #79 | อติชาติเลือกจากเมนูทุกขั้น: approve #78 (เห็นข้อความเต็มในเมนูก่อนโพสต์) → push การแก้ conflict ของ #78 แล้วรอ CI → merge → push การแก้ conflict ของ #79 + แก้ body · ก่อนโพสต์/push/merge ตรวจว่า head SHA ยังตรงกับที่ตรวจไว้ทุกครั้ง · ผลรันหลังแก้ conflict: pytest 329 passed + 1 xfailed (ทั้งปิดและเปิด PRAGMA foreign_keys), ruff ผ่าน, `node --test` ใน `web/` 39/39 · CI ของ PR ผ่านครบ 4 job ทั้ง #78 และ #79 · หลัง merge ตรวจว่า #13 ปิดจาก `Closes #13` และ CI ของ `main` ผ่าน |
| 2026-10-04, branch `feature/issue-28-thanks-stats` | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | US-28 AC3: เพิ่ม `thanks` ใน `GET /notes/<id>/stats` ของ stats-service (นับจากตาราง `thanks` ของ notes-service), mapping `Thank` ใน `stats_db.py`, เทสต์ใน `src/tests/test_stats_service.py` และแถว PY-08/PY-10/PY-11 ใน test plan | อติชาติเลือกจากเมนู: ทำ AC3 เอง แตก branch จาก `main` (ไม่ซ้อนบน #76) และทำแค่ API ส่วนหน้าเว็บไว้รอบ web ส่วนที่ 3 · pytest 331 passed + 1 xfailed, ruff ผ่าน · รันซ้ำโดยใช้ `models.py` ของ #76 (ที่สร้างตาราง `thanks` ตัวจริง) ก็ผ่าน · mutation 2 แบบ (ตัดเงื่อนไข `note_id` และตัดคีย์ `thanks`) ทำให้เทสต์ fail ทั้งคู่ · ต้อง merge หลัง #76 |
| 2026-10-04, branch `feature/issue-82-my-notes-owner-auth` | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | อ่าน wireframe/mockup ที่อติชาติออกแบบเอง แล้วเทียบกับ API ที่มีอยู่ทีละหน้าจอ เสนอสิ่งที่ต้องเพิ่มและสิ่งที่ควรตัด · ร่างและโพสต์ issue #82–#85 · ทำ Issue #82 + #83 ใน notes-service: `GET /notes/mine` พร้อม `summary`, ให้เจ้าของที่ login อยู่ `PATCH`/`DELETE` ได้โดยไม่ต้องมี edit token (ตรวจ token ก่อน), `sort=rating` · เทสต์ `src/tests/test_notes_owner.py` + `test_notes_sort_rating.py` (25 ตัว), แก้เทสต์เดิมใน `test_notes_api.py` 1 ตัวที่ยืนยันพฤติกรรมเก่า, smoke step DK-09 ใน `.github/workflows/ci.yml`, ADR-008 (EN/TH) + หมายเหตุใน ADR-004, เอกสาร API ใน `services/notes-service/README.md`, แถว NA-26 และ NA-111..134 + DK-09 ใน `docs/testing/readme.md` | อติชาติเลือกจากเมนู: เอาแค่ดีไซน์ ไม่เอารายการ requirement ในเอกสาร, เจ้าของยืนยันตัวด้วยการ login, หน้าตาตาม mockup แต่ข้อความภาษาไทย, หน้ารายละเอียดเป็นหน้าแยก, แบ่งเป็น PR 0 → 1 + 2 → 3 และเปิด issue ใหม่ (เห็นร่างทั้ง 4 issue ในเมนูก่อนโพสต์) · pytest 376 passed + 1 xfailed, ruff ผ่าน · mutation 7 แบบถูกจับครบ (ให้ใครก็แก้ได้, ไม่ตรวจ token ก่อน, ตัด tie-break, ตัดการเรียงค่าเฉลี่ย, summary ไม่กรองเจ้าของ, ค่าเฉลี่ยไม่ถ่วงน้ำหนัก, `thank_count` ไม่แยกโน้ต) · DK-09 รันผ่านกับ service จริงบน SQLite ในเครื่อง เรื่อง NULL อยู่ท้ายบน Postgres ทดสอบในเครื่องไม่ได้ (Docker ไม่ได้เปิด) จึงรอผล DK-09 บน CI · ระหว่างทดสอบพบว่า ` #82` ในชื่อ step ของ YAML ถูกอ่านเป็นคอมเมนต์ จึงใส่ชื่อในเครื่องหมายคำพูด |
| 2026-10-04, branch `feature/issue-84-web-redesign` | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ปรับหน้าตา `web/` ตาม mockup ที่อติชาติออกแบบเอง (Issue #84, ต่อจากรอบเดียวกับ Prompt 21 ใน PR #86): เขียน `web/style.css` ใหม่ทั้งไฟล์ (สีเป็นตัวแปรใน `:root`, ฟอนต์ที่มีชุดภาษาไทย), hero + แถบค้นหา + แผงตัวกรองแบบพับได้ใน `index.html`, การ์ดสองคอลัมน์ใน `login.html`, drop zone ใน `upload.html`, การ์ดโน้ตแบบใหม่และ `starBar` ใน `search-utils.js` + เทสต์ 2 ตัว, กางแผงตัวกรองเองใน `app.js`, คัด mockup เข้า `docs/design/mockup/` และเขียน `docs/design/README.md`, หัวข้อ "หน้าตา" ใน `web/README.md`, แถว WEB-39/40 ใน test plan | อติชาติเลือกจากเมนู: หน้าตาตาม mockup แต่ข้อความภาษาไทย, ใส่ใน repo เฉพาะ mockup `website/` (ไม่เอาไฟล์ `.dc.html`, `support.js` และเอกสาร requirement) · ตอนตรวจไฟล์ก่อนใส่ repo พบว่า `.dc.html`/`support.js` export มาจากเครื่องมือออกแบบ จึงถามที่มา อติชาติยืนยันว่าวาดเองในเครื่องมือโดยไม่มี AI ไฟล์ mockup จึงไม่อยู่ในตาราง "ส่วนที่รับจาก AI ตรงๆ" · `node --test` ใน `web/` 41/41, ruff ผ่าน · ตรวจบน Chrome กับ service จริงบน SQLite + ตัวแทน nginx: ค้นหา, preview, ตัวกรองจากลิงก์, หน้าเข้าสู่ระบบ, อัปโหลดจนเห็นกล่องรหัสแก้ไข และทั้งสามหน้ากว้าง 375 px ไม่มี scroll แนวนอน |
| 2026-10-05, ตรวจสถานะ/ตอบคำถามรีวิว #86, merge #86 #87 และแก้ conflict #87 #81 | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | ตรวจ PR ที่เปิดอยู่ (#81 #86 #87 ไม่มี commit ใหม่ ชนกันแค่ `AI_USAGE.md`) → เทียบคำถาม 4 ข้อที่กฤตเมธทิ้งไว้ตอน approve #86 กับโค้ดและเทสต์ แล้วโพสต์คำตอบเป็น comment → merge #86 (`main` = `5e1f4da`, #82 #83 ปิดโดย PR) → รวม `main` เข้า #87 แก้ `AI_USAGE.md` เก็บแถวของทั้งสอง PR (`90dc532`) → merge #87 (`1d492f7`, #84 ปิดโดย PR) → รวม `main` เข้า #81 แก้ `AI_USAGE.md` 3 จุด (`54ebb7c`) | อติชาติเลือกทุกขั้นจากเมนู (ข้อความ comment เห็นเต็มในเมนูก่อนโพสต์) · ก่อนโพสต์/push/merge ตรวจว่า head SHA ยังตรงกับที่ตรวจไว้ทุกครั้ง · ก่อน push การแก้ conflict ทั้งสองรอบรัน pytest ได้ 376 passed + 1 xfailed, ruff ผ่าน, `node --test` ใน `web/` 41/41 และตรวจว่าทุกบรรทัดที่แต่ละ PR เพิ่มยังอยู่ครบ · CI ผ่านครบ 4 job ทั้ง #87, #81 และ `main` หลัง merge ทั้งสองครั้ง · tree ของ merge commit #87 ตรงกับ `90dc532` ที่รันเทสต์ไว้ · push แล้ว approve เดิมยังอยู่ เพราะ repo ไม่ได้ตั้งให้ approve หายเมื่อมี commit ใหม่ |
| 2026-10-05, branch `feature/issue-85-note-detail` | อติชาติ ผาแสนเถิน | Claude Code (Anthropic) | Issue #85 ส่วนแรก: หน้ารายละเอียดโน้ต `web/note.html` + `note.js` (ดาวน์โหลด, รายการโปรด, รายงาน, ให้คะแนน, ขอบคุณ, ความคิดเห็น) และ pure function `note-utils.js` พร้อมเทสต์ 14 ตัวใน `note-utils.test.js` · ลิงก์จากชื่อโน้ตบนการ์ด (`search-utils.js`) และปุ่ม "เปิดหน้าโน้ต" ใน preview (`index.html`, `app.js`) · `/note.html` ใน `NEXT_PAGES` ของ `session-utils.js` · สไตล์ของหน้าใหม่และกฎ `[hidden]` ใน `style.css` · `web/Dockerfile`, step DK-08 ใน `ci.yml`, `web/README.md` และหัวข้อ 2.15 + แถว DK-08 ใน test plan | อติชาติเลือกจากเมนู: แบ่ง #85 เป็น 2 PR (หน้านี้ก่อน หน้าโปรไฟล์ + แถบอัปโหลดทีหลัง), ไม่แก้ backend ให้ความคิดเห็นมีชื่อผู้เขียน, หน้าโปรไฟล์แก้โน้ตในฟอร์ม `<dialog>` (ทำใน PR ถัดไป) · `node --test` ใน `web/` 55/55 (เทสต์ส่วนเวลาตั้ง TZ เองจึงผลเหมือนกันทุกเครื่อง) · mutation 11 แบบถูกจับครบ · ตรวจบน Chrome กับ service จริงบน SQLite + ตัวแทน nginx (รายละเอียดท้ายหัวข้อ 2.15 ของ test plan) และเจอบั๊กเวลาความคิดเห็นช้าไป 7 ชั่วโมงจากรอบนั้น · ไม่แตะโค้ดของ service ใด |

> **TODO:** วชิรวิทย์และกฤตเมธ — ช่วยกรอกแถวของตัวเองให้ละเอียดขึ้น (prompt ที่ใช้จริง, ช่วง session, และรายละเอียดของสิ่งที่ตรวจ/แก้) เพราะมีแค่เจ้าของงานที่รู้ข้อมูลนี้แน่ชัด — แถวของวชิรวิทย์ที่ยังค้างคือ "สร้าง prototype หน้าค้นหาโน้ต" (2026-07-10); แถว preview-note (2026-09-26 ~ 2026-09-28) ด้านบนเติมรายละเอียดแล้ว

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

### งาน Sprint 2 — User & Auth Service (ไม่ผูกกับ Lab)

ไม่พบใบงาน Lab ที่กำหนดงานนี้หรือกำหนดชื่อ branch ไว้ (ค้นในรีโป และค้นชื่อไฟล์ใน Desktop, Downloads, Documents ของเครื่องแล้ว) จึงแยกหัวข้อไว้ต่างหากต่อจาก Lab 9

#### Prompt 14 — ตรวจสถานะงาน, merge PR #63 และทำ User & Auth Service (อติชาติ, Claude Code, 2026-09-25)

**prompt จริงที่พิมพ์ (คำต่อคำ ส่วนการตัดบรรทัดของข้อ 2–4 เป็นไปตามที่ terminal ห่อบรรทัดไว้):**

```
1) เช็คงานทั้งหมดให้หน่อย ว่าตอนนี้ยังเหลืออะไรอีกมั้ย ในส่วนของฉันนะ

2) ทำงานต่อจากสรุปสถานะนี้ เริ่มด้วย merge PR #63 โดยเลือก Create a merge commit แล้ว pull main ตามขั้นตอนเดิม จากนั้นตรวจข้อกำหนดของ
   Issue #5 และ #6 กับโครงสร้างและรูปแบบเดิมในโปรเจกต์ แล้วเสนอแผนทำระบบสมัครสมาชิกและ login/logout ที่ป้องกันการปลอม uploader_name
   ด้วย สรุปแผนและไฟล์ที่จะเกี่ยวข้องก่อนเริ่มแก้โค้ด ยังไม่ต้องจัดการ PR #62 หรืองานที่รอคนอื่น

3) 1. แยกเป็นสอง PR โดยทำ auth-service ใน PR A ก่อน แล้วค่อยทำการบังคับ login ตอนอัปโหลดใน PR B หลัง PR A merge
   2. ให้ PR B อ้างอิง #31 ด้วย Refs #31 และจำกัดส่วนของรอบนั้นไว้ที่การยืนยันตัวตนกับการกำหนด uploader จากบัญชีผู้ใช้ อย่าเปลี่ยนผู้รับผิดชอบ #31
   3. ให้ผู้ใช้ตั้ง display_name เอง ความยาว 1–120 ตัวอักษร
   4. อ่านโดเมนที่อนุญาตจาก ALLOWED_EMAIL_DOMAINS โดยค่าเริ่มต้นเป็น up.ac.th
   5. ใช้ JWT อายุ 8 ชั่วโมง ไม่มี refresh token และเก็บ session ฝั่งเซิร์ฟเวอร์เพื่อเพิกถอน token ตอน logout ได้ทันที
   6. ตรวจใบงานก่อนตั้งชื่อ branch ถ้าไม่ได้ระบุชื่อไว้ ให้ใช้ feature/auth-service

   เริ่มจาก main ที่อัปเดตหลัง merge PR #63 แล้วตรวจคำแนะนำใน repo ก่อนแก้ไฟล์ ทำเฉพาะ PR A รวม auth-service, tests, เอกสาร, Docker
   และ CI ตามแผน ปรับรายละเอียดให้ตรงกับโครงสร้างจริงและข้อกำหนด NFR โดยบันทึกเหตุผลการเลือก Werkzeug scrypt ว่าเทียบเท่ากับ bcrypt ตาม
   NFR-004 ใน ADR หากยังใช้วิธีนี้อยู่

   ยังไม่ต้องแก้ notes-service เพื่อบังคับ login ตอนอัปโหลด และยังไม่ต้อง commit, push, เปิด PR หรือ merge เมื่อเสร็จให้สรุปไฟล์ที่เปลี่ยน
   ผลทดสอบ และสิ่งที่ยังค้าง

4) ตรวจ diff ของ branch feature/auth-service เทียบกับ main และรีวิวให้ครบตามข้อกำหนด #5/#6, NFR-004/005/007 และขอบเขต PR A ตรวจ
   AI_USAGE.md ด้วย เติมส่วน “รับจาก AI ตรงๆ” เฉพาะรายการที่ยืนยันได้จากประวัติหรือ diff อย่าเดา

   ถ้าไม่พบปัญหาที่ต้องแก้และ AI_USAGE.md ถูกต้องแล้ว ให้ stage เฉพาะไฟล์ของ PR A แบ่ง commit ตามเรื่อง service/tests, Docker/CI, เอกสาร
   และ AI_USAGE ตามความเหมาะสม ตรวจ staged diff ก่อนแต่ละ commit แล้ว push branch feature/auth-service ขึ้น origin

   ถ้าพบปัญหาหรือยืนยันรายการใน AI_USAGE.md ไม่ได้ ให้สรุปสิ่งที่ติดและหยุดก่อน commit/push อย่าเปิด PR หรือ merge และอย่าแตะ PR B หรือ notes-
   service ใช้ผลทดสอบที่รายงานไว้แล้ว เว้นแต่มีการแก้โค้ดระหว่างรีวิวหรือต้องทดสอบเพื่อยืนยันข้อค้นพบ รายงานผลรีวิว commit hash และผล push
   กลับมา.
```

เทียบกับ Five S's:

- **Single task** ผ่าน ข้อ 2 แยก "เสนอแผน" ออกจาก "ลงมือทำ" ชัดเจน ส่วนข้อ 3 จำกัดไว้ที่ PR A และห้ามแตะ notes-service ตรง ๆ ต่างจาก Prompt 11 ที่ hardening กับสอง story ปนกันจนต้องมาแยก PR ทีหลัง
- **Specific** ผ่านเต็ม ทางเลือกสถาปัตยกรรมที่ AI เสนอ (แยก PR, ความยาวชื่อ, โดเมน, อายุ token, การเพิกถอน, ชื่อ branch) ถูกล็อกด้วยคำตอบของคนทั้ง 6 ข้อก่อนเริ่มเขียนโค้ด AI จึงไม่ต้องเดาเอง
- **Structured** ผ่าน ข้อ 3 มีครบทั้งการตัดสินใจเป็นข้อ ๆ, ขอบเขต, ข้อห้าม (ไม่ commit/push/PR/merge) และสิ่งที่ต้องรายงานกลับ ส่วนข้อ 4 แยกเป็นสองทางชัดเจน คือถ้ารีวิวผ่านให้ commit/push ถ้าติดให้หยุดก่อน commit
- **Surrounding** ผ่าน สั่งให้ "ตรวจคำแนะนำใน repo ก่อนแก้ไฟล์" และ "ปรับให้ตรงกับโครงสร้างจริง" แทนการแปะโค้ดมาเอง เพราะ AI อ่านรีโปได้เอง
- **Short** ข้อ 1 สั้นมากและใช้ได้ผลเพราะเป็นงานสำรวจ ส่วนข้อ 3 ยาวแต่ส่วนใหญ่คือคำตอบของการตัดสินใจ ซึ่งตัดทิ้งไม่ได้

**บทเรียนจริงจากรอบนี้:** คำว่า "หากยังใช้วิธีนี้อยู่" ในข้อ 3 เปิดช่องให้ทบทวนแทนที่จะรับข้อเสนอเดิมไปเลย และช่องนี้ได้ใช้จริง พอตรวจ source ของ Werkzeug กับ OWASP Password Storage Cheat Sheet ก็พบว่า "ใช้ scrypt ของ Werkzeug" ตามที่เสนอไว้ในแผนยังไม่พอ เพราะค่า default ของ Werkzeug (N=2^15) ต่ำกว่าขั้นต่ำของ OWASP (N=2^17) ถ้าเขียนใน ADR ว่า "เทียบเท่า bcrypt" โดยใช้ค่า default จะเป็นการเคลมที่ไม่จริง จึงต้องตั้งค่าเองและเขียนเทสต์กันไว้ · อีกข้อคือสถานะที่สรุปไว้จากรอบก่อนคลาดเคลื่อน (เข้าใจว่า issue #8 ยังเปิด ทั้งที่ปิดไปตั้งแต่ 2026-09-07) จับได้เพราะข้อ 1 ถูกตอบด้วยการเช็ค GitHub จริง ไม่ใช่ตอบจากบันทึกเดิม

#### Prompt 15 — merge PR #62 และทำ PR B บังคับ login ตอนอัปโหลด (อติชาติ, Claude Code, 2026-09-27)

รอบนี้เริ่มจากถามสถานะ ("ตอนนี้งานถึงไหนอะไรยังไงแล้ว รบกวนเช็คให้ที") แล้วสั่ง approve กับ merge PR #62 ทีละคำสั่ง
แต่ละคำสั่งให้ตรวจเงื่อนไขซ้ำก่อนลงมือ และให้หยุดถ้าข้อใดไม่ตรง ซึ่งได้ใช้จริงครั้งหนึ่ง: คำสั่ง merge รอบแรกหยุดเพราะ PR ยังเป็น
`CHANGES_REQUESTED` จึงต้อง approve ก่อน · จากนั้นถามว่า "แล้วงานของฉันควรทำอะไรต่อ" และได้ PR B เป็นงานถัดไป

**prompt จริงที่ใช้กับ PR B (คำต่อคำ):** ข้อ 1 เป็นพรอมต์ที่ Claude Code ร่างไว้ในคำตอบก่อนหน้า แล้วอติชาติส่งกลับมาใช้ทั้งก้อน ส่วนข้อ 2 เป็นคำตอบของการตัดสินใจ

```
1) งาน: เริ่ม PR B — notes-service บังคับ login ตอนอัปโหลด (Refs #31)

   ขั้นตอน
   1. git fetch แล้วยืนยันว่า main = origin/main = 28b12be และ working tree สะอาด
   2. อ่าน issue #31, ADR-004, ADR-005, services/auth-service/README.md และ services/notes-service/app.py
      แล้วเสนอแผนก่อนลงมือ: ไฟล์ที่จะแก้, สัญญา API ที่เปลี่ยน, ผลต่อเทสต์และ CI smoke test, เอกสารที่ต้องอัปเดต
   3. หยุดรอให้ฉันอนุมัติแผนก่อน ห้ามสร้าง branch หรือแก้ไฟล์

   กรอบที่ตัดสินใจไว้แล้ว (ห้ามเปลี่ยน)
   - POST /notes ต้องมี Bearer token ตรวจผ่าน auth-service GET /auth/me
     ใช้ identity ที่ inject ได้ใน create_app แบบเดียวกับ storage
   - uploader มาจากบัญชีที่ login ไม่รับจาก form
   - คง edit token ของ ADR-004 ไว้ (เทสต์ property ของ Lab 9 ใช้ tokens.py)
   - branch ใหม่แยกจาก main 28b12be, PR ใช้ Refs #31 เท่านั้น ห้าม Closes และห้ามเปลี่ยน assignee ของ #31

   ข้อห้าม
   - ห้ามแตะ feature/preview-note
   - ห้าม push, เปิด PR หรือ commit จนกว่าฉันจะสั่ง
   - ถ้าเจอจุดที่ขัดกับกรอบข้างบน ให้หยุดและรายงาน ห้ามตัดสินใจเอง

2) เดินหน้าทำ PR B: บังคับ login ตอนอัปโหลด (Refs #31) ตามแผนก่อนหน้า โดยใช้คำตอบเหล่านี้:

   - D1: เลือก (ข) เพิ่ม uploader_id เพื่อเก็บ id ของบัญชีผู้ส่ง
   - D2: เลือก (ก) ถ้ามี uploader_name ในฟอร์ม ให้ละเลยและใช้ชื่อจากบัญชี
   - D3: เลือก (ก) ใช้ urllib ไม่เพิ่ม dependency
   - D4: เลือก (ก) ไม่สร้าง ADR ใหม่

   ก่อนเริ่ม ตรวจว่า main และ origin/main ยังอยู่ที่ 28b12be และ working tree สะอาด จากนั้นสร้าง branch feature/notes-require-login
   จาก commit นี้ แล้วลงมือทำตามแผน รวมถึงปรับหรือเพิ่ม tests, CI smoke test และเอกสารที่ระบุไว้

   อย่าแก้ tokens.py, auth-service หรือ feature/preview-note และอย่า commit, push หรือเปิด PR

   เมื่อเสร็จ ให้รัน tests และ smoke checks ที่เกี่ยวข้อง แล้วสรุปไฟล์ที่เปลี่ยน ผลตรวจ และข้อจำกัดที่ยังเหลือ
```

เทียบกับ Five S's:

- **Single task** ผ่าน แยก "เสนอแผน" (ข้อ 1) ออกจาก "ลงมือทำ" (ข้อ 2) และตัด preview-note ของวชิรวิทย์ออกจากขอบเขตชัดเจน
- **Specific** ผ่าน ข้อ 1 ล็อกสิ่งที่ตัดสินไปแล้วตั้งแต่ Prompt 14 ไว้เป็น "กรอบ" ส่วนเรื่องที่ยังเปิดอยู่ 4 ข้อ (D1–D4) ถูกถามกลับมาเป็นทางเลือกพร้อมคำแนะนำ แล้วตอบด้วยคำตอบสั้น ๆ ในข้อ 2 AI จึงไม่ต้องเลือกแทน
- **Structured** ผ่าน มีขั้นตอน, กรอบ, ข้อห้าม และเงื่อนไขหยุด ("ถ้าเจอจุดที่ขัดกับกรอบ ให้หยุดและรายงาน") แยกหัวข้อกันชัด
- **Surrounding** ผ่าน ระบุไฟล์ที่ต้องอ่านก่อน (issue #31, ADR-004/005, README ของ auth-service, `app.py`) แทนการอธิบายโค้ดเอง และระบุ commit ฐาน `28b12be` ให้ตรวจก่อนเริ่ม
- **Short** ข้อ 2 สั้นเพราะอ้างถึงแผนก่อนหน้า ไม่ต้องเขียนรายละเอียดซ้ำ

**บทเรียนจริงจากรอบนี้:** คำว่า "อย่าแก้ auth-service" ในข้อ 2 ครอบถึงไฟล์ `services/auth-service/README.md` ด้วยหรือไม่ ตีความได้สองแบบ รอบแรกจึงไม่ได้แก้ แต่รายงานไว้ว่าข้อความเตือนในไฟล์นั้น ("notes-service ยังไม่ได้เรียกใช้ service นี้") ล้าสมัยแล้ว จากนั้นอติชาติสั่งแก้เฉพาะข้อความนั้นก่อน commit · อีกข้อคือเทสต์ที่ใช้ตัวปลอมแทน auth-service พิสูจน์ได้แค่ว่า notes-service ใช้ผลการตรวจถูก แต่พิสูจน์ไม่ได้ว่าคุยกับ auth-service ตัวจริงถูก จึงเพิ่ม `test_notes_identity.py` ที่ยก auth-service ขึ้นเป็น HTTP server ในเทสต์ แทนที่จะรอให้ smoke test บน CI เป็นที่แรกที่จับสัญญาระหว่างสอง service ได้

### Lab 12B

#### Prompt 16 — Lab 12B Safety Net Sprint: เทสต์ + CI (อติชาติ, Claude Code, 2026-09-27)

- **เครื่องมือที่ใช้:** Claude Code
- **ที่มาของ prompt:** เริ่มจากส่งภาพหน้าจอใบงาน Lab 12B ทั้งชุดแล้วสั่ง "ช่วยสรุปมาให้ทั้งหมดก่อนว่าควรจะทำอะไรบ้าง"
  จากนั้นทุกเฟสใช้พรอมต์ที่ Claude Code ร่างไว้ท้ายคำตอบก่อนหน้า แล้วอติชาติส่งกลับมาใช้ทั้งก้อน (คำต่อคำด้านล่าง)

**Prompt 1 — ใช้เป็นไอเดีย test case (brainstorm):** ผลที่ได้คือฟังก์ชันที่แนะนำ (`email_error()`) กับตาราง test case 8 เคส
และข้อสังเกตว่า `"a@"` ได้ error โดเมนแทน error รูปแบบ ทีมเลือกใช้ทั้ง 8 เคส และตัดสินเองว่า `"a@"` ควรเป็น error รูปแบบ

```
1. merge PR #65 แบบ "Create a merge commit" โดยล็อก head ไว้ที่ b21f77b (--match-head-commit ใช้ SHA เต็ม) — ถ้า head เปลี่ยนหรือ CI ไม่เขียว ให้หยุดและรายงาน
2. pull main ล่าสุดแบบ ff-only แล้วยืนยันว่า issue ที่ PR #65 ปิดถูกปิดจริง
3. สร้าง branch feature/safety-net จาก main ใหม่
4. รัน coverage ของ validation.py และ credentials.py แล้วเสนอว่าฟังก์ชันไหนเหมาะที่สุด พร้อมรายการ test case (happy/edge/error) ยังไม่ต้องเขียนโค้ดเทสต์
ขอบเขต/ข้อห้าม:
- ห้ามลบ branch feature/notes-require-login
- ห้าม push / เปิด PR จนกว่าจะสั่ง
- ห้ามแก้ ci.yml, AI_USAGE.md, reflect.md ในรอบนี้
- ห้าม force-push และห้าม commit ตรงเข้า main
เงื่อนไขหยุด: ถ้าเจอ conflict หรือเทสต์เดิมแดง ให้หยุดทันทีแล้วรายงาน ห้ามแก้เอง
```

**Prompt 2 — เขียนเทสต์:**

```
เขียนเทสต์ Lab 12B สำหรับ email_error() ตามลำดับนี้:
1. สร้างไฟล์ src/tests/test_email_error.py เขียนเทสต์เคส #1–#8 ตามตารางที่เสนอ (โครง AAA + docstring 1 บรรทัด)
2. เคส "a@": ให้คาดหวังว่า <ได้ error รูปแบบ / ได้ error โดเมน> ← ฉันจะเลือกเอง
3. รันเทสต์แบบเดียวกับ CI (.venv pytest src/tests + --cov) แล้วรายงานผลและตัวเลข coverage
4. commit บน feature/safety-net ข้อความ "test(auth): add unit tests for email_error (Lab12B phase B)"
ขอบเขต/ข้อห้าม:
- ห้ามแก้ credentials.py แม้เทสต์ "a@" จะแดง
- ห้าม push / เปิด PR จนกว่าจะสั่ง
- ห้ามแก้ ci.yml, AI_USAGE.md, reflect.md ในรอบนี้
- ห้าม force-push และห้าม commit ตรงเข้า main
เงื่อนไขหยุด: ถ้าเทสต์เดิมตัวอื่นแดง ให้หยุดทันทีแล้วรายงาน ห้ามแก้เอง
```

**Prompt 3 — ใช้แก้/ตั้ง CI (`ci.yml` + ruff):**

```
Lab 12B เฟส C ตามลำดับนี้:
1. เพิ่ม ruff.toml ที่ root: select = ["E4","E7","E9","F"] แล้วลบ import FileStorage ที่ไม่ได้ใช้ใน src/tests/test_notes_api.py
2. เพิ่ม job "lint" ใน .github/workflows/ci.yml (ของเดิมห้ามแตะ): ruff ล็อกเวอร์ชันให้ตรงกับเครื่อง แล้วรัน ruff check .
3. รัน ruff check . และ pytest แบบเดียวกับ CI บนเครื่องให้เขียวก่อน แล้ว commit "ci: add ruff lint job (Lab12B phase C)"
4. push -u origin feature/safety-net แล้วเปิด PR ไป main ชื่อ "Lab12B: Safety Net Sprint — tests + CI" ใช้ template PR ของทีม
5. รอ CI แล้วรายงานผลทุก job
ขอบเขต/ข้อห้าม:
- ห้าม merge / approve
- ห้ามแก้ AI_USAGE.md, reflect.md และห้ามแก้ credentials.py
- ห้าม force-push
เงื่อนไขหยุด: ถ้า lint หรือเทสต์แดงบนเครื่อง หรือ CI แดง ให้หยุดทันทีแล้วรายงาน ห้ามแก้เอง
```

- **ส่วนที่รับจาก AI ตรง ๆ (ไม่แก้):** `src/tests/test_email_error.py`, `ruff.toml`, job `lint` ใน `ci.yml`, หัวข้อ 2.11 ใน `docs/testing/readme.md`
  และ `docs/safety-net.md` ทั้ง 5 หัวข้อ (ดูตารางท้ายไฟล์)
- **ตรวจสอบแล้วว่าเข้าใจทุกบรรทัดที่ส่ง:** [ ] ← ทีมติ๊กเองหลังอ่านครบ

**บทเรียนจริงจากรอบนี้:**
- Prompt 2 ถูกส่งไปทั้งที่ช่อง `<ได้ error รูปแบบ / ได้ error โดเมน>` ยังไม่ได้เลือก (เกิดสองรอบ) AI ไม่เดาแทน รอบแรกเขียนเฉพาะ 8 เคสที่ไม่ขึ้นกับการตัดสินใจนี้
  แล้ว commit ไปก่อน รอบที่สองหยุดถามก่อน · พรอมต์ที่มีช่องให้เลือกต้องเติมให้ครบก่อนส่ง ไม่อย่างนั้นงานส่วนนั้นจะค้าง
- ใบงานให้ `pip install ruff` แล้ว `ruff check .` แต่ ruff 0.16 เปิดกฎจัดลำดับ import (I001) กับกลุ่ม RUF เป็นค่า default ด้วย ถ้าทำตามใบงานตรง ๆ
  CI จะแดง 14 จุดทั้ง repo ตั้งแต่วันแรก จึงระบุกฎเองใน `ruff.toml` และล็อกเวอร์ชันใน CI
- `credentials.py` เป็น coverage 100% อยู่แล้ว แต่ยังเจอบั๊กได้ (AE-09) — coverage บอกว่าบรรทัดไหนถูกรัน ไม่ได้บอกว่าผลที่ได้ถูกหรือไม่

### งาน Sprint 2 — Web app (ไม่ผูกกับ Lab)

#### Prompt 17 — ตรวจสถานะ, merge PR #72 และต่อหน้าค้นหา + preview เข้ากับ API จริง (อติชาติ, Claude Code, 2026-10-01)

- **เครื่องมือที่ใช้:** Claude Code
- **ที่มาของ prompt:** รอบนี้แทบไม่มีพรอมต์ยาว เริ่มจากคำถามสั้น ๆ แล้วตัดสินใจทุกขั้นด้วยการเลือกจากเมนูทางเลือกที่ Claude Code เสนอ
  (มีตัวเลือกแนะนำพร้อมเหตุผลกำกับ) ข้อความที่พิมพ์เองมีสองข้อความ (คำต่อคำ):

```
เช็คงานต่ให้ที แล้วต้องทำอะไรต่ออีกดี
```

```
ถามมาให้ฉันเลือกได้มั้ย
```

- **การตัดสินใจที่เลือกจากเมนู (ตามลำดับ):** merge PR #72 (approve แล้ว, CI ผ่าน) → งานถัดไปคือต่อ frontend กับ API → browser เรียก API ผ่าน
  **nginx gateway** (ไม่เลือกการเพิ่ม CORS ใน service หรือให้ Flask เสิร์ฟหน้าเว็บ) → slice แรกเป็น **ค้นหา + preview** → เก็บโค้ดใน **โฟลเดอร์ใหม่ `web/`**
  → อนุมัติแผน 5 ข้อทั้งชุด (gateway, หน้าค้นหา, preview, เทสต์, เอกสารรวม ADR-006)
- **ผลลัพธ์:** ดูแถว `2026-10-01, branch feature/web-search-preview` ในตาราง Log และแถวในตาราง "ส่วนที่รับจาก AI ตรงๆ"
- **ตรวจสอบแล้วว่าเข้าใจทุกบรรทัดที่ส่ง:** [ ] ← ทีมติ๊กเองหลังอ่านครบ

เทียบกับ Five S's:

- **Single task / Specific** ข้อความที่พิมพ์เองกว้างมาก ("ต้องทำอะไรต่อ") ความเจาะจงทั้งหมดมาจากการเลือกในเมนูทีละเรื่อง ได้ผลดีกับงานที่มีทางแยกชัด
  แต่ข้อเสียคือเหตุผลของการตัดสินใจอยู่ในเมนูที่ AI เขียน ไม่ได้อยู่ในคำพูดของคนตัดสินใจ จึงต้องบันทึกไว้ในหัวข้อนี้และใน ADR-006 แทน
- **Structured** แผนถูกเสนอเป็นข้อ ๆ พร้อมขอบเขตและสิ่งที่ไม่ทำ ("ไม่แตะ `app.py`", "ไม่แก้ `prototypes/sprint1/`", "ยังไม่ push") ก่อนลงมือ
- **Surrounding** ไม่ได้ส่งบริบทเอง แต่ AI อ่านจาก repo (โค้ด endpoint, CI, ADR) และจากสถานะ PR บน GitHub เอง ซึ่งทำให้เจอข้อจำกัดสำคัญคือ service ไม่มี CORS
  และ `app.py` เป็นไฟล์ที่ #68/#69 conflict อยู่ ก่อนจะเสนอทางเลือก
- **Short** ผ่าน

**บทเรียนจริงจากรอบนี้:**
- Docker ไม่ได้เปิด จึงตรวจหน้าเว็บบน Chrome กับ service ตัวจริงที่รันบน SQLite และสคริปต์ Python ที่ทำตัวแทน `web/nginx.conf` · วิธีนี้พิสูจน์หน้าเว็บกับ API ได้
  แต่พิสูจน์ config ของ nginx ไม่ได้ จึงเพิ่ม smoke step DK-08 ใน CI ไว้เป็นที่ตรวจ nginx ตัวจริง
- ข้อมูลทดสอบที่อัปโหลดด้วย `curl -F` ใน Git Bash บน Windows ได้ชื่อภาษาไทยเป็น `?` ตั้งแต่ฝั่ง client ตอนแรกดูเหมือนบั๊กของหน้าเว็บ
  ตรวจที่ API แล้วพบว่าเก็บเป็น `?` มาตั้งแต่ตอนอัปโหลด อัปโหลดใหม่จาก Python ด้วย UTF-8 แล้วแสดงถูก (บันทึกไว้ใน `web/README.md`)
- คำสั่งตรวจรอบหนึ่งมี `git stash` ติดมาโดยไม่ตั้งใจ ทำให้ไฟล์ที่แก้ไว้ 5 ไฟล์ถูกเก็บเข้า stash เครื่องมือแจ้งว่า `docker-compose.yml` เปลี่ยนบนดิสก์
  จึงตรวจ `git stash list` (มี stash เดียว เป็นของ branch นี้) แล้ว `git stash pop` คืนครบ ไม่มีอะไรหาย · คำสั่งที่แตะ working tree ต้องอ่านซ้ำก่อนรัน
- ตอนแรกแถวผลเทสต์ที่เพิ่มใน `docs/testing/readme.md` อยู่ติดกับบรรทัดที่ #69 แก้ จึงกลายเป็นไฟล์ conflict ใหม่ ตรวจเจอด้วย `git merge-tree` กับ commit ชั่วคราว
  แล้วย้ายแถวไปท้ายตาราง ผลคือ conflict ของ #68/#69 กับ branch นี้เหลือชุดเดียวกับที่มีกับ `main` อยู่แล้ว

#### Prompt 18 — merge PR #73/#68 และทำหน้าเข้าสู่ระบบ + อัปโหลด (อติชาติ, Claude Code, 2026-10-02)

- **เครื่องมือที่ใช้:** Claude Code
- **ที่มาของ prompt:** แบบเดียวกับ Prompt 17 คือพิมพ์คำถามสั้น ๆ แล้วตัดสินใจทุกขั้นด้วยการเลือกจากเมนูทางเลือกที่ Claude Code เสนอ
  ข้อความที่พิมพ์เอง (คำต่อคำ):

```
เช็คงานล่าสุดให้หน่อย
```

```
มีอะไรที่ฉันต้องทำอีกมั้ย
```

```
ถามมาใหม่ที
```

```
ละมีงานส่วนไหนของฉันที่ต้องทำอีกมั้ย ช่วยลิสมาให้ที
```

- **การตัดสินใจที่เลือกจากเมนู (ตามลำดับ):** เปิด #31 กลับมาแล้ว merge #73 → push การแก้ conflict ของ #68 → approve #68 เอง
  (เลือกสองครั้ง ครั้งที่สองหลังขอให้ถามใหม่) → merge #68 → งานถัดไปคือ web ส่วนที่ 2 → เก็บ token ใน `sessionStorage` → แยกหน้า + แถบเมนูบน
  → ขอบเขต login + สมัคร + logout + upload → หยุดก่อน commit
- **ผลลัพธ์:** ดูแถว `2026-10-02, …` สองแถวในตาราง Log และแถวในตาราง "ส่วนที่รับจาก AI ตรงๆ"
- **ตรวจสอบแล้วว่าเข้าใจทุกบรรทัดที่ส่ง:** [ ] ← ทีมติ๊กเองหลังอ่านครบ

เทียบกับ Five S's: เหมือน Prompt 17 คือ **Specific** มาจากการเลือกในเมนูทีละเรื่อง ไม่ได้มาจากข้อความที่พิมพ์ · **Structured** แผนถูกเสนอพร้อมสิ่งที่ไม่ทำ
(ไม่แตะ service, แก้/ลบโน้ตไว้รอบหน้า) ก่อนลงมือ · **Surrounding** AI อ่านเองจากโค้ด endpoint, `validation.py`, `nginx.conf` และสถานะ PR บน GitHub
· **Single task** ไม่ผ่านเต็ม เพราะรอบเดียวมีทั้งงานคุม PR ของทีมและงานเขียนหน้าเว็บ จึงแยกบันทึกเป็นสองแถวใน Log

**บทเรียนจริงจากรอบนี้:**
- #31 ถูกปิดด้วยมือ 42 วินาทีหลังมีคน approve #73 (ก่อน merge) แบบเดียวกับ #7, #9, #14 และ #26 · เปิดกลับก่อน merge แล้วตรวจด้วย GraphQL
  (`ClosedEvent.closer`) ว่า #11 และ #31 ถูกปิดโดย PR #73 จริง ผู้ตรวจจึงตามจาก issue ไปที่โค้ดได้
- `git merge -F -` ใน Git Bash ไม่อ่านข้อความ commit จาก stdin ทำให้ merge ตัวแรกไม่เกิด แล้ว merge ตัวที่สองไปชน conflict แทน · ยกเลิกด้วย
  `git merge --abort` (ยังไม่ได้ push) แล้วเขียนข้อความลงไฟล์ก่อน · ก่อน push เทียบ tree hash กับชุดที่รันเทสต์แล้ว (`097d653`) ว่าตรงกัน
- ตอนตรวจบน Chrome คลิกแท็บ "สมัครสมาชิก" ผ่านเครื่องมือแล้วหน้าไม่เปลี่ยน ดูเหมือนบั๊ก แต่เรียก `click()` ผ่าน JavaScript แล้วสลับได้ปกติ
  และคลิกตามพิกัดจริงก็ได้ · ปุ่มออกจากระบบที่กดไม่ติดรอบแรกเพราะคลิกก่อนหน้าโหลดเสร็จ · ก่อนสรุปว่าเป็นบั๊กของหน้าเว็บต้องแยกให้ได้ว่าเป็นที่เครื่องมือหรือที่โค้ด
- กฎตรวจฟอร์มอัปโหลดใน `web/upload-utils.js` ซ้ำกับ `services/notes-service/validation.py` · ถ้าแก้ฝั่ง service ต้องแก้ฝั่งเว็บด้วย
  (มี comment กำกับไว้ทั้งสองจุดในไฟล์เว็บ) · ถ้าลืม ผลที่เกิดคือหน้าเว็บกันค่าที่ service รับได้ หรือปล่อยค่าที่ service ไม่รับไปให้ service ตอบ `400` เอง

### งาน Sprint 2 — สถิติคำขอบคุณ (ไม่ผูกกับ Lab)

#### Prompt 19 — merge PR #78, แก้ conflict PR #79 และทำ US-28 AC3 (อติชาติ, Claude Code, 2026-10-04)

- **เครื่องมือที่ใช้:** Claude Code
- **ที่มาของ prompt:** แบบเดียวกับ Prompt 17–18 คือพิมพ์คำสั้น ๆ แล้วตัดสินใจทุกขั้นด้วยการเลือกจากเมนูทางเลือกที่ Claude Code เสนอ
  ข้อความที่พิมพ์เอง (คำต่อคำ):

```
เช็คงานล่าสุดให้ที
```

```
จัดการต่อให้ที
```

```
จัดการต่อให้เลยที
```

```
งานของฉันมีอะไรอีกมั้ย
```

```
AC3 ฉันทำเอง
```

  ("จัดการต่อให้ที" พิมพ์สองครั้ง ครั้งแรกหลังเสนอแก้ conflict ของ #78 ครั้งที่สองหลังเสนอ merge #78)
- **การตัดสินใจที่เลือกจากเมนู (ตามลำดับ):** approve #78 → push การแก้ conflict ของ #78 แล้วรอ CI → (merge #78 จากข้อความที่พิมพ์)
  → push การแก้ conflict ของ #79 + แก้ body → AC3 แตก branch จาก `main` → ทำแค่ API → commit + push + เปิด PR พร้อมบันทึกไฟล์นี้
- **ผลลัพธ์:** ดูแถว `2026-10-04, …` สองแถวในตาราง Log และแถวในตาราง "ส่วนที่รับจาก AI ตรงๆ"
- **ตรวจสอบแล้วว่าเข้าใจทุกบรรทัดที่ส่ง:** [ ] ← ทีมติ๊กเองหลังอ่านครบ

เทียบกับ Five S's: **Specific** มาจากการเลือกในเมนู ไม่ได้มาจากข้อความที่พิมพ์ ข้อความ "AC3 ฉันทำเอง" สั้นมาก ขอบเขตจริง (ฐาน branch, API อย่างเดียว)
ถูกกำหนดตอนเลือกเมนู · **Surrounding** AI อ่านเองจาก issue #28, โค้ดของ #76 และ stats-service · **Single task** ไม่ผ่านเต็ม
เพราะรอบเดียวมีทั้งงานคุม PR ของทีมและงานเขียนโค้ด จึงแยกบันทึกเป็นสองแถวใน Log

**บทเรียนจริงจากรอบนี้:**
- บรรทัดว่างหนึ่งบรรทัดก่อน NA-75 ทำให้แถว NA-75..88 ของ #78 หลุดออกจากตาราง GitHub แสดงเป็นข้อความธรรมดา (ปัญหาเดียวกับที่เคยเกิดในตาราง Log ของไฟล์นี้)
- PR ที่ conflict กับ `main` ไม่มี CI รันเลย เพราะ GitHub สร้าง merge commit ให้ workflow `pull_request` ไม่ได้ ผล CI ของ #78 จึงมาหลังแก้ conflict แล้วเท่านั้น
- เลข NA ชนกันระหว่าง PR ที่เปิดพร้อมกันได้ง่าย (#76, #78, #79 ใช้ NA-75 เป็นเลขแรกทั้งสามตัว) · PR ที่เข้าทีหลังเลื่อนเลขตอนแก้ conflict
- stats-service อ่านตาราง `thanks` ที่ notes-service เป็นเจ้าของ จึงต้องมี mapping ซ้ำใน `stats_db.py` ที่คอลัมน์ตรงกัน
  เทสต์ถูกรันทั้งกับ `models.py` ของ `main` และของ #76 เพื่อยืนยันว่าตารางที่สร้างจากสองฝั่งใช้แทนกันได้

### งาน Sprint 2 — หน้าเว็บตาม wireframe (ไม่ผูกกับ Lab)

#### Prompt 21 — เทียบ wireframe กับระบบจริง และทำ backend ของหน้าโปรไฟล์ (อติชาติ, Claude Code, 2026-10-04)

- **เครื่องมือที่ใช้:** Claude Code
- **ที่มาของ prompt:** ส่งไฟล์ zip ของ wireframe + เอกสาร requirement ที่ทำเอง แล้วถามความเห็น ตัดสินใจต่อด้วยเมนูทางเลือกเหมือน Prompt 17–20
  ข้อความที่พิมพ์เอง (คำต่อคำ ตัด path ในเครื่องที่อยู่หน้าชื่อไฟล์ออก):

```
Wireframe and requirements document.zip แล้วตัวชิ้นงานฉันอยากได้ประมาณนี้น่ะ นายโอเคมั้ย ต้องเพิ่มฟังก์ชันอะไรมั้ย
```

- **การตัดสินใจที่เลือกจากเมนู (ตามลำดับ):** เจ้าของแก้/ลบด้วยการ login (ต้องมี ADR-008) · ตอบเองว่า "ฉันแค่อยากได้ดีไซน์เท่านั้นน่ะ"
  (ไม่เอารายการ requirement ในเอกสาร) · หน้าตาตาม mockup แต่ข้อความภาษาไทย · หน้ารายละเอียดโน้ตเป็นหน้าแยก
  → แผน PR 0 (เอกสาร) → PR 1 (backend) + PR 2 (หน้าตา) → PR 3 (หน้าใหม่) → เปิด issue ใหม่ #82–#85 ตามร่าง
- **ผลลัพธ์:** ดูแถว `2026-10-04, branch feature/issue-82-my-notes-owner-auth` ในตาราง Log
- **ตรวจสอบแล้วว่าเข้าใจทุกบรรทัดที่ส่ง:** [ ] ← ทีมติ๊กเองหลังอ่านครบ

เทียบกับ Five S's: **Surrounding** ดีที่สุดในชุดนี้ เพราะส่งดีไซน์จริงมาให้ดู · **Specific** ไม่ผ่านในข้อความแรก ("ประมาณนี้")
จนตอบในเมนูว่าเอาแค่ดีไซน์ ก่อนหน้านั้นการวิเคราะห์ครอบคลุม requirement ทั้งชุดซึ่งเกินที่ต้องการ

**บทเรียนจริงจากรอบนี้:**
- เอกสาร requirement ที่มากับดีไซน์มีของที่เกินขอบเขต (SSO, ส่งเมลยืนยัน, DOCX, ระบบ tag) การถามว่าต้องการ "ดีไซน์" หรือ "ทุก requirement" ทำให้งานเล็กลงมาก
- ดีไซน์ที่ดูเหมือนงานหน้าเว็บล้วน (หน้าโปรไฟล์) ต้องมี backend ใหม่ และต้องเปลี่ยนการตัดสินใจเดิม (ADR-004) จึงต้องมี ADR ใหม่ ไม่ใช่แค่แก้ CSS
- `#` หลังช่องว่างใน YAML คือคอมเมนต์ ชื่อ step ที่มีเลข issue ต้องใส่เครื่องหมายคำพูด ไม่งั้นชื่อถูกตัดเงียบ ๆ
- SQLite กับ Postgres วาง NULL ต่างกันเมื่อเรียง DESC เทสต์บน SQLite จึงพิสูจน์ "ไม่มีคะแนนอยู่ท้าย" ได้ไม่ครบ ต้องมี smoke test บน Postgres

#### Prompt 22 — ตรวจสถานะ, merge PR #86/#87, แก้ conflict #81 และทำหน้ารายละเอียดโน้ต (อติชาติ, Claude Code, 2026-10-05)

- **เครื่องมือที่ใช้:** Claude Code
- **ที่มาของ prompt:** แบบเดียวกับ Prompt 17–21 คือพิมพ์คำสั้น ๆ แล้วเลือกขั้นถัดไปจากเมนูทางเลือกที่ AI เสนอ
  ข้อความที่พิมพ์เอง (คำต่อคำ):

```
เช็คงานล่าสุดให้หน่อย
```

```
จัดการต่อให้ที
```

```
จัดการต่อให้ที
```

```
มีอะไรสามารถทำต่ออีกได้มั้ย
```

- **การตัดสินใจที่เลือกจากเมนู (ตามลำดับ):** ตอบคำถามในรีวิว #86 → (หลัง "จัดการต่อให้ที" ครั้งแรก) merge #86 → push การแก้ conflict ของ #87
  แล้วรอ CI → merge #87 → (หลัง "จัดการต่อให้ที" ครั้งที่สอง) แก้ conflict #81 ก่อนเริ่ม #85 → push #81 แล้วรอ CI → (หลังคำถามสุดท้าย)
  เริ่ม #85 → แบ่งเป็น 2 PR, ไม่แก้ backend เรื่องชื่อผู้เขียนความคิดเห็น, แก้โน้ตในหน้าโปรไฟล์ด้วยฟอร์ม `<dialog>`
- **ผลลัพธ์:** ดูแถว `2026-10-05, ตรวจสถานะ/ตอบคำถามรีวิว #86 …` และ `2026-10-05, branch feature/issue-85-note-detail` ในตาราง Log
- **ตรวจสอบแล้วว่าเข้าใจทุกบรรทัดที่ส่ง:** [ ] ← ทีมติ๊กเองหลังอ่านครบ

เทียบกับ Five S's: ข้อความที่พิมพ์สั้นมากเหมือน Prompt 19–20 **Specific** มาจากเมนูทั้งหมด · "จัดการต่อให้ที" ครั้งที่สองมีทางเลือกค้างอยู่สองทาง
(แก้ #81 หรือเริ่ม #85) จึงต้องถามซ้ำในเมนูก่อนลงมือ

**บทเรียนจริงจากรอบนี้:**
- เวลาจาก SQLite ไม่มี timezone ติดมา `Date.parse` ของ browser อ่านเป็นเวลาเครื่อง ความคิดเห็นจึงแสดงเวลาช้าไป 7 ชั่วโมง เทสต์ที่รันบน CI (เวลา UTC)
  จะผ่านแม้ไม่ได้แก้ จึงต้องตั้ง TZ ในเทสต์เอง และบั๊กนี้เจอได้จากการเปิดหน้าจริงกับ service จริงเท่านั้น
- ลิงก์ดาวน์โหลดแบบ `<a href>` ไม่ส่ง token ไปด้วย การดาวน์โหลดจึงไม่ถูกนับเป็นของผู้ใช้ หน้ารายละเอียดใช้ `fetch` พร้อม token แทน
- ทุก PR ที่เพิ่มแถวท้ายตาราง Log และท้ายหัวข้อ Prompt ชนกันที่ `AI_USAGE.md` เสมอ PR ที่ merge ทีหลังต้องรวม `main` แล้วเก็บแถวของทุก PR
- push commit ใหม่หลัง approve แล้ว approve เดิมไม่หาย (repo ไม่ได้ตั้ง dismiss stale reviews) คนรีวิวจึงควรดูว่ามี commit ใหม่หลังที่ตัวเอง approve หรือไม่

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
| `prototypes/sprint1/wachirawit_search_note_prototype.css` ทั้งไฟล์ | Claude/Gemini (Prompt 4, commit `7a455c6`, 2026-07-10) | generate ทั้งไฟล์ ประวัติ git แสดงว่าไม่ถูกแก้อีกเลยหลัง commit แรก (วชิรวิทย์ตรวจหน้าตาในเบราว์เซอร์) |
| ข้อมูลจำลอง `notes` (5 รายการ) ใน `wachirawit_search_note_prototype.html` | Claude/Gemini (Prompt 4, commit `7a455c6`) | generate มาตรงๆ เนื้อหาเหมือนเดิมทุกตัวอักษรตั้งแต่ commit แรกจนถึงปัจจุบัน |
| logic กรอง (คณะ/ปี/ประเภทไฟล์/คำค้น) และเรียงผลลัพธ์ใน `render()` ของหน้าค้นหา | Claude/Gemini (Prompt 4, commit `7a455c6`) | เงื่อนไขกรองและการเรียงเหมือนเดิมตั้งแต่ commit แรก วชิรวิทย์แค่เปลี่ยนชื่อตัวแปร (ใน `0ea55bd`) ต่อมาถูกแยกไป `note-utils.js` ใน Lab 7 (ดูแถวของ Lab 7 ด้านบน) |
| `services/auth-service/*` ทั้งโฟลเดอร์, `src/tests/test_auth_*.py`, ส่วนที่เพิ่มใน `src/tests/conftest.py`/`docker-compose.yml`/`.github/workflows/ci.yml`, ADR-005 ทั้ง EN/TH และส่วนที่แก้ในเอกสาร README/test plan (US-05/US-06, branch `feature/auth-service`) | Claude Code (2026-09-25) | generate ทั้งหมดใน session เดียว และไม่มีคนแก้บรรทัดใดก่อน commit (ยืนยันจากประวัติ session ว่าทุกบรรทัดใน diff เทียบกับ `main` ถูกเขียนโดยเครื่องมือ และ branch นี้ไม่มี commit ใดก่อนหน้านี้ที่คนจะแก้ไว้) · สิ่งที่มาจากคน: การตัดสินใจทั้ง 6 ข้อของอติชาติที่ล็อกการออกแบบไว้ (ดู Prompt 14) · **ยังไม่ผ่านการรีวิวโค้ดโดยคนในทีม** ที่ทำไปแล้วคือเทสต์อัตโนมัติกับการรีวิว diff ด้วยเครื่องมือ จึงยังต้องรอ review ใน PR |
| `services/notes-service/identity.py` และ `src/tests/test_notes_identity.py` ทั้งไฟล์, ส่วนที่แก้ใน `services/notes-service/app.py`/`models.py`/`validation.py`/`Dockerfile`/`README.md`, `src/tests/test_notes_api.py`/`test_notes_validation.py`, `docker-compose.yml`, `.github/workflows/ci.yml` และเอกสาร README/test plan (US-31, branch `feature/notes-require-login`) | Claude Code (2026-09-27) | generate ทั้งหมดใน session เดียว ยังไม่มีคนแก้บรรทัดใดก่อน commit · สิ่งที่มาจากคน: กรอบ 4 ข้อจาก Prompt 14 และคำตอบ D1–D4 ใน Prompt 15 · **ยังไม่ผ่านการรีวิวโค้ดโดยคนในทีม** ที่ทำไปแล้วคือเทสต์อัตโนมัติ, saboteur test และ smoke บน SQLite |
| `src/tests/test_email_error.py` ทั้งไฟล์, `ruff.toml`, job `lint` ใน `.github/workflows/ci.yml`, การลบ import ที่ไม่ได้ใช้ใน `src/tests/test_notes_api.py`, หัวข้อ 2.11 ใน `docs/testing/readme.md`, `docs/safety-net.md` ทั้ง 5 หัวข้อ และภาพหลักฐาน `docs/images/lab12b-merging-blocked.png` (Lab 12B) | Claude Code (Prompt 16, 2026-09-27) | generate ทั้งหมด ฟังก์ชัน `email_error()` เป็นข้อเสนอของ AI ที่อติชาติรับไป ส่วนความคาดหวังของเคส `"a@"` อติชาติเลือกเอง · ตรวจว่าเทสต์และ lint ผ่านทั้งบนเครื่องและบน CI ของ PR #66 · ใบงานกำหนดให้ทีมเขียนเองอย่างน้อยครึ่งหนึ่ง ส่วนนี้ยังไม่ถึง จึงเปิดเผยไว้ตามจริง · ข้อความเรื่องขอบ 254 ในหัวข้อ 5 ของ `docs/safety-net.md` ตรวจแล้วด้วยการลองเปลี่ยน `>` เป็น `>=` ในสำเนาชั่วคราว เทสต์เดิม 59 ตัวผ่านหมด มีแค่ AE-03 ที่แดง |
| `services/notes-service/preview.py` ทั้งไฟล์, `src/tests/test_notes_preview.py` ทั้งไฟล์, endpoint `GET /notes/<id>/preview` + ฟิลด์ `preview_url` ใน `services/notes-service/app.py`/`models.py`/`storage.py`, ส่วนที่เพิ่มใน `services/notes-service/requirements.txt`/`Dockerfile`, หัวข้อ 2.12 ใน `docs/testing/readme.md` และหัวข้อ `GET /notes/<id>/preview` ใน `services/notes-service/README.md` (US-11, branch `feature/preview-note`) | Claude Code (2026-09-26 ~ 2026-09-28) | generate ทั้งหมด ไม่มีคนแก้บรรทัดใดก่อน commit (ประวัติ git ของ `preview.py`/`test_notes_preview.py` มีแค่ 3 commit ทั้งหมดเป็นของ Claude Code) · verify ผ่าน `docker compose` จริงแล้วพบบั๊ก Dockerfile ที่ไม่ได้ copy `preview.py` เข้า image (แก้ใน commit ถัดมา) และ `ResourceWarning` จากไฟล์ที่ไม่ถูกปิด (แก้แยกอีก commit) · **ยังไม่ผ่านการรีวิวโค้ดโดยคนในทีม** ที่ทำไปแล้วคือเทสต์อัตโนมัติ (25/25) กับ manual verify ผ่าน container จริง จึงยังต้องรอ review ใน PR |
| ข้อความ review/comment ที่โพสต์ใน PR #67 #68 #69 #70 #71 ผ่าน `gh` | Claude Code (2026-09-28 ~ 2026-10-01) | AI ร่างทั้งข้อความ อติชาติอ่านผลวิเคราะห์และเลือกประเภทของการโพสต์ (comment / request-changes / approve) ก่อนทุกครั้ง แล้วโพสต์จากบัญชีของอติชาติตามที่ร่าง ไม่ได้แก้ถ้อยคำ |
| `web/` ทั้งโฟลเดอร์ (`index.html`, `app.js`, `search-utils.js`, `search-utils.test.js`, `style.css`, `nginx.conf`, `Dockerfile`, `README.md`), `docs/architecture/adr/0006-nginx-web-gateway.md`/`.th.md`, service `web` ใน `docker-compose.yml`, step `Run web search-utils tests` และ smoke step DK-08 ใน `.github/workflows/ci.yml`, ส่วนที่เพิ่มใน `docs/architecture/README.md`/`README.th.md` และ `docs/testing/readme.md` (DK-08, หัวข้อ 2.13) (branch `feature/web-search-preview`) | Claude Code (2026-10-01) | generate ทั้งหมด ไม่มีคนแก้บรรทัดใด · ทางเลือกสถาปัตยกรรม (nginx gateway, ขอบเขต slice, ที่เก็บโค้ด) อติชาติเป็นคนเลือก · verify ด้วย `node --test` 15/15 และตรวจบน Chrome กับ service ตัวจริง (SQLite) · nginx ตัวจริงยังไม่ได้รันบนเครื่อง รอผล DK-08 บน CI · **ยังไม่ผ่านการรีวิวโค้ดโดยคนในทีม** |
| การแก้ conflict ของ PR #68 กับ `main` (branch local `prep-68-merge`, 2026-10-01) ที่ push เป็น `c784a8c`/`adcb7ed`, ข้อความ merge commit ทั้งสอง และข้อความ comment กับ approve ที่โพสต์ใน PR #68 ผ่าน `gh` | Claude Code (2026-10-01 ~ 2026-10-02) | AI ทำการแก้ conflict และร่างข้อความทั้งหมด อติชาติเลือกให้ push, approve และ merge จากเมนูทีละขั้น ไม่ได้แก้ถ้อยคำหรือโค้ด · verify ด้วย `pytest src/tests` (268 passed + 1 xfailed) และ CI 4/4 ก่อน approve |
| `web/login.html`, `login.js`, `upload.html`, `upload.js`, `site.js`, `session-utils.js`, `upload-utils.js`, `session-utils.test.js`, `upload-utils.test.js` ทั้งไฟล์, ส่วนที่แก้ใน `web/index.html`/`style.css`/`Dockerfile`/`README.md`, ส่วนที่แก้ใน step DK-08 และชื่อ step `Run web unit tests` ใน `.github/workflows/ci.yml`, หัวข้อ 2.14 และแถว DK-08/Test Report ใน `docs/testing/readme.md` (branch `feature/web-login-upload`) | Claude Code (2026-10-02) | generate ทั้งหมด ไม่มีคนแก้บรรทัดใด · ทางเลือก (ที่เก็บ token, การแยกหน้า, ขอบเขต) อติชาติเป็นคนเลือก · verify ด้วย `node --test` 38/38, DK-08 กับตัวแทน nginx และตรวจบน Chrome กับ service ตัวจริง (SQLite) · nginx ตัวจริงรอผล DK-08 บน CI · **ยังไม่ผ่านการรีวิวโค้ดโดยคนในทีม** |
| ข้อความ approve ที่โพสต์ใน PR #78 ผ่าน `gh`, การแก้ conflict ของ PR #78 (`ac98b5d`) และ PR #79 (`3c955cc`) พร้อมข้อความ merge commit, และ body ใหม่ของ PR #79 | Claude Code (2026-10-04) | AI ร่างข้อความและทำการแก้ conflict ทั้งหมด อติชาติอ่านข้อความ approve และ body ฉบับเต็มในเมนูก่อนเลือก และเลือกให้ push/merge ทีละขั้น ไม่ได้แก้ถ้อยคำ · ผลการแก้ conflict ตรวจด้วยเทสต์และ CI (ดูแถว Log `2026-10-04, ตรวจ/approve/…`) |
| ส่วนที่แก้ใน `services/stats-service/app.py`/`stats_db.py`, เทสต์ที่เพิ่มใน `src/tests/test_stats_service.py` และแถว PY-08/PY-10/PY-11 ใน `docs/testing/readme.md` (US-28 AC3, branch `feature/issue-28-thanks-stats`) | Claude Code (2026-10-04) | generate ทั้งหมด อติชาติเลือกขอบเขตและฐาน branch จากเมนู · ตรวจด้วยเทสต์ การรันกับ `models.py` ของ #76 และ mutation 2 แบบ (ดูแถว Log `2026-10-04, branch feature/issue-28-thanks-stats`) · ยังไม่ผ่านการรีวิวโค้ดจากเพื่อนในทีม |
| ส่วนที่แก้ใน `services/notes-service/app.py`/`README.md`, `src/tests/test_notes_owner.py` และ `test_notes_sort_rating.py` ทั้งไฟล์, เทสต์ที่แก้ใน `src/tests/test_notes_api.py`, step DK-09 ใน `.github/workflows/ci.yml`, ADR-008 ทั้ง EN/TH, หมายเหตุใน ADR-004 และ index ใน `docs/architecture/README.md`/`README.th.md`, แถวที่เพิ่ม/แก้ใน `docs/testing/readme.md` และข้อความ issue #82–#85 (Issues #82, #83, branch `feature/issue-82-my-notes-owner-auth`) | Claude Code (2026-10-04) | generate ทั้งหมด ไม่มีคนแก้บรรทัดใด · ทางเลือกที่ล็อกการออกแบบ (login แทน token ได้, เก็บ token ไว้ด้วย, แบ่ง PR) อติชาติเป็นคนเลือก และอ่านร่าง issue ฉบับเต็มในเมนูก่อนโพสต์ · ตรวจด้วยเทสต์, mutation และ DK-09 กับ service จริง (ดูแถว Log `2026-10-04, branch feature/issue-82-my-notes-owner-auth`) · ยังไม่ผ่านการรีวิวโค้ดจากเพื่อนในทีม · ไฟล์ wireframe/mockup ไม่อยู่ในแถวนี้ เพราะอติชาติทำเอง |
| `web/style.css` ทั้งไฟล์, ส่วนที่แก้ใน `web/index.html`/`login.html`/`upload.html`/`app.js`/`search-utils.js`/`search-utils.test.js`/`README.md`, `docs/design/README.md` และแถว WEB-39/40 ใน `docs/testing/readme.md` (Issue #84, branch `feature/issue-84-web-redesign`) | Claude Code (2026-10-04) | generate ทั้งหมดโดยยึดสีและ layout จาก mockup ของอติชาติ ไม่มีคนแก้บรรทัดใด · ไฟล์ใน `docs/design/mockup/` เป็นงานของอติชาติเอง ไม่อยู่ในแถวนี้ · ตรวจด้วยเทสต์และบน Chrome (ดูแถว Log `2026-10-04, branch feature/issue-84-web-redesign`) · ยังไม่ผ่านการรีวิวโค้ดจากเพื่อนในทีม |
| ข้อความ comment ตอบคำถามรีวิวที่โพสต์ใน PR #86 ผ่าน `gh`, การแก้ conflict ของ PR #87 (`90dc532`) และ PR #81 (`54ebb7c`) พร้อมข้อความ merge commit | Claude Code (2026-10-05) | AI ร่างข้อความและทำการแก้ conflict ทั้งหมด อติชาติอ่านข้อความ comment ฉบับเต็มในเมนูก่อนเลือก และเลือกให้ push/merge ทีละขั้น ไม่ได้แก้ถ้อยคำ · ผลการแก้ conflict ตรวจด้วยเทสต์และ CI (ดูแถว Log `2026-10-05, ตรวจสถานะ/ตอบคำถามรีวิว #86 …`) |
| `web/note.html`, `note.js`, `note-utils.js`, `note-utils.test.js` ทั้งไฟล์, ส่วนที่แก้ใน `web/index.html`/`app.js`/`search-utils.js`/`search-utils.test.js`/`session-utils.js`/`session-utils.test.js`/`style.css`/`Dockerfile`/`README.md`, step DK-08 ใน `.github/workflows/ci.yml`, หัวข้อ 2.15 และแถว DK-08 ใน `docs/testing/readme.md` (Issue #85, branch `feature/issue-85-note-detail`) | Claude Code (2026-10-05) | generate ทั้งหมดโดยยึด layout หน้า 1d จาก mockup ของอติชาติ ไม่มีคนแก้บรรทัดใด · ทางเลือก (แบ่ง PR, ไม่แก้ backend) อติชาติเป็นคนเลือก · ตรวจด้วยเทสต์, mutation และบน Chrome (ดูแถว Log `2026-10-05, branch feature/issue-85-note-detail`) · ยังไม่ผ่านการรีวิวโค้ดจากเพื่อนในทีม |

ส่วนที่เป็นงานที่คนแก้เองบางส่วน ไม่ใช่รับจาก AI ตรง ๆ: ฟังก์ชัน `esc()` กัน XSS และการ clamp ค่าใน `stars()` ของหน้าค้นหา ก่อน Lab 7 (เข้ามาในรอบที่ PR #37 ถูก CHANGES_REQUESTED โดยทีมรีวิวพบช่องโหว่ XSS แล้ววชิรวิทย์ใช้ Gemini ช่วยหาจุดและเสนอวิธีแก้ตาม Prompt 5 ก่อนนำไปแก้ใน commit `0ea55bd` จึงเป็นงานที่ AI ช่วย ไม่ใช่เขียนเองล้วน) แต่ใน Lab 7 ฟังก์ชันสองตัวนี้ถูกย้าย/เขียนใหม่เป็น `escapeHtml`/`formatStars` ใน `note-utils.js` โดย Claude Code แล้ว (แถวด้านบน) จึงไม่ใช่ "ไม่แก้จาก AI" อีกต่อไปสำหรับตำแหน่งใหม่นี้ ส่วนที่ยังเป็นของคนเขียนเองเหมือนเดิม: การตัดสินใจเรื่อง Tracer vs Prototype และเนื้อหา reflection รายบุคคลทั้งสามไฟล์
