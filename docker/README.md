# Stats Service — Docker

## Image

- Name: `ghcr.io/software-engineering-concepts-2026/stats-service`
- Tag: `v0.1.0`
- Base image: `python:3.12-slim` (multi-stage build — the `deps` stage that runs `pip install` is discarded; only the final slim runtime stage ships)
- Built size: *TBD* — record the actual value from `docker images` after building locally and update this line before opening the PR

## Build

```bash
docker build -t ghcr.io/software-engineering-concepts-2026/stats-service:v0.1.0 .
```

Build context is the **repo root** (the Dockerfile `COPY`s from `services/stats-service/`), so run this command from the repository root, not from inside `services/stats-service/`.

## Run

```bash
docker run -p 5000:5000 ghcr.io/software-engineering-concepts-2026/stats-service:v0.1.0
```

No environment variables are required yet — the service currently returns mock/in-memory stats (see `services/stats-service/app.py`). Once it is wired to PostgreSQL (per [`docs/architecture/c4-container.md`](../docs/architecture/c4-container.md)) it will need a `DATABASE_URL`, passed at run time with `-e DATABASE_URL=...` — never baked into the image or copied in via `.env`.

Test it responds 2xx:

```bash
curl -i http://localhost:5000/health
curl -i http://localhost:5000/stats
```

## Push

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u <github-username> --password-stdin
docker push ghcr.io/software-engineering-concepts-2026/stats-service:v0.1.0
```

## Why Container, not VM (ESP §5.4)

ตาม Sommerville, *Engineering Software Products* §5.4 (Container vs VM), Container เหมาะกับ Stats Service เพราะ:

- Stats Service เป็น stateless HTTP service (อ่านจาก DB ภายนอก ไม่เก็บ state ในตัวเอง) — ไม่ต้องการ isolation ระดับ OS เต็มรูปแบบที่ VM ให้
- Container share host OS kernel ทำให้ startup เร็วระดับวินาทีและ overhead ต่ำกว่า VM มาก ซึ่งสำคัญเมื่อต้องรัน 4 microservices (Gateway, Auth, Notes, Stats) พร้อมกันบนเครื่องเดียวหรือ free-tier host ที่ทีมใช้ (Render/Railway ตาม [tech_stack.md](../docs/architecture/tech_stack.md))
- Image ที่ build ได้ portable ข้าม environment (dev ในเครื่องนักศึกษา ↔ CI ↔ production host) — ปัญหาเดียวกับที่ VM แก้ได้ แต่ VM ต้องแบก full guest OS ต่อ instance ซึ่งแพงและช้ากว่าโดยไม่จำเป็นสำหรับ service เล็กและ stateless แบบนี้

VM ยังจำเป็นถ้าต้องการ kernel/OS ต่างจาก host จริง ๆ หรือต้องการ isolation ระดับ hypervisor สำหรับ workload ที่ไม่ไว้ใจกัน (multi-tenant untrusted code) ซึ่งไม่ใช่กรณีของ Stats Service

## Notes

ไฟล์นี้เขียนขึ้นก่อน build/run/push จริง เพราะเครื่องที่ใช้ตอนเขียนไม่มี Docker ติดตั้ง — ก่อนเปิด PR ต้อง: build image, รัน + curl ทั้งสอง endpoint ให้เห็น 2xx จริง, บันทึก image size จริงแทนบรรทัด TBD ด้านบน, push ขึ้น ghcr.io (หรือ Docker Hub ถ้าทีมเลือกใช้แทน) แล้วแนบ screenshot หน้า registry ใน PR description
