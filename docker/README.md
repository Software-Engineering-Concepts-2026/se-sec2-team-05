# Stats Service — Docker

## Image

- **Public image (Docker Hub):** `docker.io/felsau/stats-service:v0.1.0` — this is the one to pull; the repo is public
- Also pushed to `ghcr.io/software-engineering-concepts-2026/stats-service:v0.1.0`, but that package stays **private** — the org's package visibility policy has both Public and Internal disabled (Package settings → Danger Zone → Change visibility shows "Setting is disabled by organization administrators"), so only Docker Hub satisfies the "public" requirement
- Base image: `python:3.12-slim` (multi-stage build — the `deps` stage that runs `pip install` is discarded; only the final slim runtime stage ships)
- Built size: 187MB (measured via `docker images` after a local build, 2026-08-23)

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

Docker Hub (public — use this one):

```bash
docker login
docker build -t felsau/stats-service:v0.1.0 .
docker push felsau/stats-service:v0.1.0
```

ghcr.io (private, kept for the org-linked package trail):

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

## Verified locally (2026-08-23)

- `docker build -t stats-service:v0.1.0 .` — succeeded
- `docker run -p 5000:5000 stats-service:v0.1.0` then:
  - `curl http://localhost:5000/health` → `200`, `{"service":"stats-service","status":"ok",...}`
  - `curl http://localhost:5000/stats` → `200`, `{"top_contributors":[],"total_downloads":0,"total_notes":0}`
- Image size: 187MB (see above)
- Pushed to `ghcr.io/software-engineering-concepts-2026/stats-service:v0.1.0` (private — see the visibility note above)
- Pushed to `docker.io/felsau/stats-service:v0.1.0`, digest `sha256:0abff5bb6bbc007cf81dea82fcede9eb107c532dd18db73ba0090b65ffba0025` — confirmed public via `curl https://hub.docker.com/v2/repositories/felsau/stats-service/` returning `"is_private":false`; screenshot in the PR description
