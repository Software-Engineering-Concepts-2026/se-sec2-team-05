# 🧪 Automated Testing

โฟลเดอร์นี้เก็บ **unit / integration test ของโค้ดฝั่ง service** ส่วนเทสต์ของ prototype ฝั่ง front-end
อยู่ติดกับโค้ดที่มันทดสอบ (`prototypes/sprint1/note-utils.test.js`) เพื่อให้ไฟล์เทสต์กับไฟล์ต้นทางอยู่ด้วยกัน

| ไฟล์ | ทดสอบอะไร | ผู้เขียน |
| --- | --- | --- |
| `conftest.py` | ทำให้ pytest มองเห็นโค้ดของทุก service (ยังไม่ได้ทำเป็น package) และเลือก DB ของเทสต์ (SQLite หรือ Postgres ผ่าน `TEST_DATABASE_URL`) | อติชาติ |
| `test_stats_service.py` | Stats Service: `/health`, `/stats` และสถิติต่อโน้ต `GET /notes/<id>/stats` (US-16, US-28 AC3) | อติชาติ, กฤตเมธ |
| `test_auth_credentials.py` | ตรวจข้อมูลสมัครสมาชิกและ hash รหัสผ่านของ User & Auth Service (US-05) | อติชาติ |
| `test_auth_tokens.py` | ออก/ตรวจ JWT ของ User & Auth Service (US-06) | อติชาติ |
| `test_auth_api.py` | endpoint `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me` (US-05, US-06) | อติชาติ |
| `test_auth_rate_limit.py` | rate limit ของ login และสมัครสมาชิก (ADR-011, test plan 2.23) | อติชาติ |
| `test_email_error.py` | `email_error()` ของ auth-service โดยตรง (Lab 12B) | อติชาติ |
| `test_notes_validation.py` | ตรวจ metadata และไฟล์ตอนอัปโหลด (US-08) | อติชาติ |
| `test_notes_validation_boundary.py` | boundary/equivalence ของการตรวจ metadata (Lab 9) | อติชาติ |
| `test_tokens_property.py` | property-based test ของ edit token ด้วย Hypothesis (Lab 9) | อติชาติ |
| `test_fizzbuzz.py` | TDD kata (Lab 9) | อติชาติ |
| `test_notes_api.py` | Notes Service: อัปโหลด ค้นหา/กรอง ดาวน์โหลด แก้ไข/ลบโน้ต และตัวนับ view/download (US-08, US-10, US-12, US-16, US-19, US-20, US-26) | อติชาติ, วชิรวิทย์, กฤตเมธ |
| `test_notes_identity.py` | Notes Service ตรวจ token ผ่าน auth-service ตัวจริงทาง HTTP (US-31) | อติชาติ |
| `test_notes_preview.py` | preview รูปและหน้าแรกของ PDF (US-11) | วชิรวิทย์ |
| `test_notes_favorites.py` | favorites และ `is_favorited` (US-15) | วชิรวิทย์ |
| `test_notes_thanks.py` | ขอบคุณเจ้าของโน้ตและ `thank_status` (US-28) | วชิรวิทย์ |
| `test_notes_comments.py` | ความคิดเห็นบนโน้ต (US-14) | กฤตเมธ |
| `test_notes_reports.py` | รายงานเนื้อหาและ workflow ตรวจ/ปฏิเสธ/ลบโน้ตของ admin (Issues #17, #18) | กฤตเมธ |
| `test_notes_ratings.py` | Notes Service rating: eligibility, การสร้าง/แก้ไข Rating, ค่าเฉลี่ย, authorization และ cleanup (Issue #13) | กฤตเมธ |
| `test_notes_owner.py` | โน้ตของฉัน `GET /notes/mine` และการแก้/ลบด้วยบัญชีเจ้าของ (Issue #82, ADR-008) | อติชาติ |
| `test_notes_sort_rating.py` | `GET /notes?sort=rating` เรียงตามคะแนนเฉลี่ย (Issue #83) | อติชาติ |
| `test_vercel_deploy.py` | deploy บน Vercel: `BlobFileStorage`, URL ของ Neon ทั้ง 3 service, เพดาน body 4.5 MB และ route ใน `vercel.json` (ADR-009) | อติชาติ |
| `../e2e/test_web_flows.py` | E2E ผ่าน browser: สมัคร อัปโหลด ค้นหา ใช้โน้ตจากอีกบัญชี แก้/ลบด้วยรหัส และความกว้างมือถือ (test plan 2.21) | อติชาติ |
| `../perf/load_test.py` | load test: เวลาตอบสนองของ API เทียบ NFR-001/002 ที่ 1, 10 และ 25 คนพร้อมกัน (test plan 2.24) — ไม่ใช่ pytest และไม่อยู่ใน CI | อติชาติ |
| `../../prototypes/sprint1/note-utils.test.js` | `escapeHtml`, `formatStars`, `compareNotes` | อติชาติ (Lab 7) |
| `../../web/*.test.js` | pure function ของหน้าเว็บ: `search-utils`, `session-utils`, `upload-utils`, `note-utils`, `profile-utils`, `admin-utils`, `stats-utils`, `edit-utils` | อติชาติ |

ผู้เขียนดูจาก `git blame` ของฟังก์ชันเทสต์ ไฟล์ที่มีหลายคนแปลว่าแต่ละคนเพิ่มเทสต์ของงานตัวเองเข้าไปในไฟล์เดียวกัน

## วิธีรันในเครื่อง

**เทสต์ Python (Stats Service)** — แนะนำให้ใช้ virtualenv แยก

```bash
python -m venv venv
# Windows: venv\Scripts\activate   |   macOS/Linux: source venv/bin/activate
pip install -r services/stats-service/requirements.txt
pip install -r services/notes-service/requirements.txt
pip install -r services/auth-service/requirements.txt
pip install -r src/tests/requirements-dev.txt
pytest src/tests -v
```

**รันชุดเดียวกันบน PostgreSQL** — ปกติเทสต์ใช้ SQLite ในไฟล์ชั่วคราว ถ้าตั้ง `TEST_DATABASE_URL`
`conftest.py` จะใช้ Postgres ตัวนั้นแทนและ **ล้าง schema ทิ้งทุกเทสต์** ห้ามชี้ไปที่ DB ที่มีข้อมูลจริง
(รวมถึง DB ของ compose ที่ใช้ทำงานอยู่) CI รันแบบนี้ใน job `Unit tests (PostgreSQL)`

```bash
docker run -d --name noteshare-pytest-pg -p 55432:5432 \
  -e POSTGRES_USER=noteshare -e POSTGRES_PASSWORD=noteshare_test -e POSTGRES_DB=noteshare_test \
  postgres:16-alpine
TEST_DATABASE_URL=postgresql+psycopg://noteshare:noteshare_test@localhost:55432/noteshare_test pytest src/tests -v
docker rm -f noteshare-pytest-pg
```

เทสต์ใหม่ที่ต้องใช้ฐานข้อมูลให้ขอ URL จาก fixture `make_db_url("ชื่อ.db")` อย่าเขียน `sqlite:///...` เอง
ไม่อย่างนั้นเทสต์นั้นจะไม่ถูกรันบน Postgres

**E2E ผ่าน browser** — อยู่ที่ [`src/e2e/`](../e2e/) แยกจากโฟลเดอร์นี้ เพราะต้องมี stack ที่รันอยู่และ browser
(`pytest src/tests` จึงไม่ต้องติดตั้ง Playwright) · ใช้ Playwright ของ Python กับ `pytest` · CI รันใน job `E2E tests (browser)`

```bash
docker compose up -d --build
pip install -r src/e2e/requirements.txt
python -m playwright install chromium        # หรือใช้ Edge/Chrome ที่มีอยู่: --browser-channel msedge
pytest src/e2e -v --base-url http://localhost:8080
# ดูหน้าจอระหว่างรัน: --headed --slowmo 300 · เก็บ trace ของเทสต์ที่ล้ม: --tracing retain-on-failure
```

ทุกเทสต์สมัครบัญชีใหม่และสุ่มรหัสวิชาเอง จึงรันซ้ำบน DB เดิมได้ แต่จะทิ้งบัญชีและโน้ตทดสอบไว้ใน DB นั้น
ใช้กับ stack ทดสอบเท่านั้น (ล้างด้วย `docker compose down -v`) ห้ามชี้ `--base-url` ไปที่เว็บจริงบน Vercel

**Load test** — สคริปต์ธรรมดาที่ [`src/perf/`](../perf/) (ไม่ใช่ pytest) seed โน้ตหลายร้อยไฟล์แล้ววัด p50/p95/p99
เทียบ NFR-001/002 กับ stack ที่ยกไว้ ยอมรันกับ `localhost` เท่านั้น วิธีรันและเหตุผลที่ไม่อยู่ใน CI ดู [`src/perf/README.md`](../perf/README.md)

```bash
docker compose up -d --build
pip install -r src/perf/requirements.txt
python src/perf/load_test.py --base-url http://localhost:8080
```

**เทสต์ JavaScript (prototypes และ web)** — ใช้ test runner ที่มากับ Node 18+ ไม่ต้อง npm install

```bash
cd prototypes/sprint1
node --test

# เทสต์ของหน้าเว็บ
cd ../../web
node --test
```

> ต้อง `cd` เข้าไปก่อน แล้วรัน `node --test` เปล่า ๆ — ถ้าส่ง path โฟลเดอร์เป็น argument
> ตรง ๆ (`node --test prototypes/sprint1/`) Node 24 จะตีความว่าเป็นชื่อ module แล้วพังด้วย
> `MODULE_NOT_FOUND`

ทุกชุดถูกรันอัตโนมัติทุก PR ผ่าน [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
