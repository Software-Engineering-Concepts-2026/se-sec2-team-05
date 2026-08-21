# Project: NoteShare
_สร้างพื้นที่ให้นักศึกษาแบ่งปันสรุปเลกเชอร์และโน้ตซึ่งกันและกัน เพื่อให้ทุกคนเข้าถึงความรู้ได้ง่ายและเรียนรู้ร่วมกันเป็นชุมชน_

## Team: The Builders
- นายอติชาติ ผาแสนเถิน (67026168) — หัวหน้ากลุ่ม, GitHub: `@Felsau`
- วชิรวิทย์ ศรีทอง (67021219), GitHub: `@Washi-cloud`
- กฤตเมธ ป้องตัน (67020746), GitHub: `@KITTAMETPONGTAN`

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
    *(This section will be updated in later weeks when using Docker Compose)*
    ```bash
    # Example for a single service
    cd services/stats-service
    docker build -t your-team/stats-service .
    docker run -p 5001:5000 your-team/stats-service
    ```

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
- **Code Review:** ต้องมีสมาชิกอย่างน้อย **1 คน** review และ approve ก่อน merge (GitHub ไม่ให้เจ้าของ PR approve ตัวเอง)
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

## 👥 Requirements

User personas and key scenarios that drive our development are located in the `/docs/requirements` directory.

- **[User Personas](./docs/requirements/personas/)**
- **[User Scenarios](./docs/requirements/main_scenario.md)**
- **[User Stories](./docs/requirements/user-stories.md)**
- **[Non-functional Requirements](./docs/requirements/nfr.md)**
