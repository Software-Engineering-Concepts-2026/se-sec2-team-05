# Project: NoteShare
_สร้างพื้นที่ให้นักศึกษาแบ่งปันสรุปเลกเชอร์และโน้ตซึ่งกันและกัน เพื่อให้ทุกคนเข้าถึงความรู้ได้ง่ายและเรียนรู้ร่วมกันเป็นชุมชน_

## Team: The Builders
- นายอติชาติ ผาแสนเถิน (67026168) — หัวหน้ากลุ่ม, GitHub: `@Felsau`
- วชิรวิทย์ ศรีทอง (67021219), GitHub: `@Washi-cloud`
- กฤตเมธ ป้องตัน (67020746), GitHub: `@KITTAMETPONGTAN`

📖 **วิธีใช้งานเว็บ:** ดู [คู่มือการใช้งาน (USER_GUIDE.md)](./USER_GUIDE.md) · เว็บจริง https://noteshare-sooty.vercel.app

---

## 🚀 Getting Started

This section explains how to get a local copy of the project up and running for development and testing purposes.

### Prerequisites

- Git
- Python 3.10+
- Docker & Docker Compose

### Running the Application (with Docker)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05.git
    cd se-sec2-team-05
    ```

2.  **Run the services:**
    ```bash
    docker compose up --build
    ```
    ยกขึ้นมาห้าตัว: PostgreSQL, [Notes Service](./services/notes-service/README.md) ที่ `localhost:5001`,
    [User & Auth Service](./services/auth-service/README.md) ที่ `localhost:5002`,
    Stats Service ที่ `localhost:5000` และหน้าเว็บพร้อม gateway (nginx) ที่ **http://localhost:8080**
    — ตรวจว่าขึ้นแล้วด้วย `curl localhost:5001/health` แล้วเปิดเว็บที่ `localhost:8080`

    ```bash
    docker compose down -v   # ลบ volume ด้วย = ล้างข้อมูลทั้งหมด (schema อัปเกรดเองด้วย Alembic ตอน service เริ่ม, ADR-010)
    ```

    > ℹ️ gateway (nginx ใน `web/`) ตรวจ login กับ `GET /auth/me` ของ User & Auth Service ก่อนส่งต่อ
    > route ที่ต้อง login เช่น อัปโหลด ให้คะแนน ความคิดเห็น รายการโปรด และรายงาน ส่วนการอ่าน (ค้นหา หน้าโน้ต
    > ดาวน์โหลด ภาพรวมสถิติ) เปิดให้ทุกคน และการแก้/ลบต้อง login เป็นเจ้าของโน้ต เหตุผลอยู่ใน
    > [ADR-005](./docs/architecture/adr/0005-auth-jwt-with-server-side-sessions.th.md),
    > [ADR-006](./docs/architecture/adr/0006-nginx-web-gateway.th.md),
    > [ADR-013](./docs/architecture/adr/0013-retire-per-note-edit-token.th.md)
    > และ [ADR-014](./docs/architecture/adr/0014-gateway-checks-login.th.md)

3.  **Deploy บน Vercel:** merge เข้า `main` แล้ว Vercel deploy เว็บจริงให้อัตโนมัติ (branch อื่นไม่ deploy) · ถ้าจะตั้ง project เองทำตาม [docs/deploy/vercel.md](./docs/deploy/vercel.md) — หน้าเว็บและ 3 service เป็น Vercel Services, ฐานข้อมูล Neon, ไฟล์ใน Vercel Blob ([ADR-009](./docs/architecture/adr/0009-deploy-on-vercel-services.th.md)) · ไฟล์อัปโหลดได้ถึง 10 MB เพราะหน้าเว็บส่งไฟล์ตรงเข้า Blob ([ADR-012](./docs/architecture/adr/0012-direct-upload-to-vercel-blob.th.md))

---

## 🤝 Ways of Working (Project Charter)

ข้อตกลงร่วมกันของทีมเพื่อให้การทำงานราบรื่นและลดปัญหาที่พบบ่อย

### 1. Meeting Cadence
| Meeting | ความถี่ | ระยะเวลา | จุดประสงค์ |
| --- | --- | --- | --- |
| Sprint Planning | ต้นสัปดาห์ (สัปดาห์ละครั้ง) | 45–60 นาที | วางแผนงานและเป้าหมายของ Sprint |
| Daily Stand-up | ทุกวันทำงาน / 2–3 ครั้งต่อสัปดาห์ | 10–15 นาที | อัปเดตความคืบหน้า, สิ่งที่ติดขัด |
| Sprint Review / Retrospective | ปลายสัปดาห์ (สัปดาห์ละครั้ง) | 30–45 นาที | ทบทวนผลงานและปรับปรุงวิธีการทำงาน |

### 2. Communication Rules
- **ช่องทางหลัก:** กลุ่ม Instagram (IG)
- **เวลาตอบกลับ (Response time):** ตอบกลับภายใน 24 ชั่วโมงในวันทำงาน
- **การใช้ Thread:** ใช้ thread แยกตามหัวข้อ เพื่อให้สนทนาเป็นระเบียบ
- **DM vs. Public:** เรื่องที่เกี่ยวข้องกับทีมให้คุยในช่องสาธารณะ (public channel) เพื่อความโปร่งใส; ใช้ DM เฉพาะเรื่องส่วนตัว
- **การแจ้งลา/ติดปัญหา:** แจ้งทีมล่วงหน้าหากไม่สามารถเข้าร่วมประชุมหรือทำงานตามกำหนด

### 3. Git Workflow
- **Branching:** แตก branch จาก `main` เสมอ ตั้งชื่อตามรูปแบบ `type/short-description` เช่น `feature/upload-note`, `fix/login-bug`, `docs/initial-charter` — **ถ้าใบงานของ Lab ระบุชื่อ branch มาให้ ใช้ชื่อของใบงานก่อนรูปแบบของทีม** เพราะเกณฑ์ให้คะแนนบางข้อดูชื่อ branch
- **Commit Messages:** ใช้รูปแบบ [Conventional Commits] เช่น `feat: add note upload`, `fix: correct search query`
- **Pull Request:** ทุกการเปลี่ยนแปลงเข้าผ่าน PR เท่านั้น ห้าม push ตรงเข้า `main` · PR ใหม่จะขึ้น template จาก `.github/pull_request_template.md` มาให้ กรอกให้ครบทุกหัวข้อ **โดยเฉพาะช่อง Screenshots ถ้า PR แตะ UI** เพราะแนบย้อนหลังใน PR ที่ merge ไปแล้วไม่ได้
- **Code Review:** ต้องมีสมาชิกอย่างน้อย **1 คน** review และ approve ก่อน merge (GitHub ไม่ให้เจ้าของ PR approve ตัวเอง) และ CI ต้องเขียวครบตาม [Testing & CI](#-testing--ci) — branch protection ของ `main` บังคับทั้งสองข้อ
- **ปิด PR ให้จบในคาบ:** ไม่ปล่อย PR ค้างข้าม Lab เพราะหลายใบงานให้คะแนนตอน merge ไม่ใช่ตอนเปิด PR — ถ้ายังไม่พร้อมให้เปิดเป็น draft ไว้
- **หลัง Merge:** ลบ branch ที่ merge แล้วเพื่อความเป็นระเบียบ

### 4. Decision Making
- พยายามหา **ฉันทามติ (consensus)** เป็นอันดับแรก
- หากเห็นต่างกัน ใช้การ **โหวต (majority vote)** โดยทุกคนมีหนึ่งเสียง
- หากเสียงเท่ากันหรือยังตัดสินใจไม่ได้ ให้ **หัวหน้าทีม (Team Lead)** เป็นผู้ตัดสินใจขั้นสุดท้าย
- บันทึกการตัดสินใจสำคัญไว้ใน `/docs/architecture/adr/`

---

## 🏛️ Architecture & Design

Key architectural decisions and diagrams are documented in the `/docs/architecture` directory.

- **[C4 Models & Tech Stack](./docs/architecture/README.md)**
- **[Architectural Decision Records (ADRs)](./docs/architecture/adr/)**

## 🧩 Services

| Service | Port | สถานะ |
| --- | --- | --- |
| **[Notes Service](./services/notes-service/README.md)** | 5001 | อัปโหลด/ค้นหา/ตัวอย่าง/ดาวน์โหลด/แก้ไข/ลบโน้ตพร้อม metadata (US-07–12, US-19, US-20, US-26) · ให้คะแนน ความคิดเห็น รายการโปรด ขอบคุณ รายงาน และหน้าผู้ดูแล (US-13–15, US-17, US-18, US-28) — อัปโหลดต้อง login และแนบชื่อจากบัญชี (US-31) |
| **[User & Auth Service](./services/auth-service/README.md)** | 5002 | สมัครสมาชิกด้วยอีเมลมหาวิทยาลัย, login/logout ด้วย JWT ที่เพิกถอนได้ทันที (US-05, US-06) และจำกัดจำนวนครั้งที่ login/สมัครได้ ([ADR-011](./docs/architecture/adr/0011-rate-limit-login-and-register.th.md)) — gateway และ notes-service ใช้ `GET /auth/me` ตรวจ login |
| **Stats Service** | 5000 | อ่านจากฐานข้อมูลเดียวกับ Notes Service: ภาพรวม ยอดดาวน์โหลด และอันดับเจ้าของโน้ต (`GET /stats`) กับสถิติรายโน้ต (`GET /notes/<id>/stats`) (US-16, US-28) |
| **API Gateway** | 8080 | nginx ใน `web/` บนเครื่อง และ [`gateway/proxy.ts`](./gateway/proxy.ts) บน Vercel — ตรวจ login ก่อนส่งต่อ route ที่ต้อง login ([ADR-006](./docs/architecture/adr/0006-nginx-web-gateway.th.md), [ADR-014](./docs/architecture/adr/0014-gateway-checks-login.th.md)) |

## 👥 Requirements

User personas and key scenarios that drive our development are located in the `/docs/requirements` directory.

- **[User Personas](./docs/requirements/personas/)**
- **[User Scenarios](./docs/requirements/main_scenario.md)**
- **[User Stories](./docs/requirements/user-stories.md)**
- **[Non-functional Requirements](./docs/requirements/nfr.md)**

## 🧪 Testing & CI

ทุก PR และทุก push เข้า `main` จะถูกรันอัตโนมัติด้วย [GitHub Actions](./.github/workflows/ci.yml) 7 job:

| Job | ตรวจอะไร | ต้องผ่านก่อน merge |
| --- | --- | --- |
| `lint` | ruff ตามกฎใน `ruff.toml` | ✅ |
| `Unit tests (JS prototypes)` | `node --test` ของ `prototypes/sprint1`, `web/` และ `gateway/` | ✅ |
| `Unit tests (Stats Service)` | `pytest src/tests` บน SQLite ทุก service พร้อม coverage | ✅ |
| `Unit tests (PostgreSQL)` | `pytest src/tests` ชุดเดียวกันบน PostgreSQL 16 | ✅ |
| `Build & smoke-test stack` | `docker compose up --build` แล้วยิง API จริงผ่าน gateway | ✅ |
| `E2E tests (browser)` | Playwright เปิดเว็บบน stack จริง (`src/e2e`) | ✅ |
| `Security scan` | pip-audit + bandit | — (แดงเองได้เมื่อมี CVE ใหม่ แม้โค้ดไม่เปลี่ยน) |

branch protection ของ `main` บังคับให้ 6 job แรกผ่าน และ branch ต้องตามทัน `main` ก่อน merge
ถ้ามี PR อื่น merge ไปก่อน ให้กด **Update branch** แล้วรอ CI รันใหม่

```bash
cd prototypes/sprint1 && node --test   # unit test ฝั่ง prototype (web/ และ gateway/ รันแบบเดียวกัน)
pytest src/tests -v                    # unit test ของทุก service (ดูวิธีติดตั้งใน src/tests/README.md)
```

- **[Test Plan & Report](./docs/testing/readme.md)**
- **[วิธีรันเทสต์ในเครื่อง](./src/tests/README.md)**
