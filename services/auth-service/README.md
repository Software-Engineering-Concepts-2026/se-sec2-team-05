# User & Auth Service

Service สมัครสมาชิกและเข้า/ออกจากระบบ — ทำตาม [US-05 (#5)](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/issues/5)
และ [US-06 (#6)](https://github.com/Software-Engineering-Concepts-2026/se-sec2-team-05/issues/6)
การออกแบบ token/session และเหตุผลที่เลือก scrypt อยู่ใน [ADR-005](../../docs/architecture/adr/0005-auth-jwt-with-server-side-sessions.th.md)

> ⚠️ **notes-service ยังไม่ได้เรียกใช้ service นี้** — การอัปโหลดยังรับ `uploader_name` จากฟอร์ม
> จนกว่างานบังคับ login ตอนอัปโหลด (refs #31) จะเสร็จ · ยังไม่มีการยืนยันอีเมลทางเมล
> ใครก็สมัครด้วยอีเมล `@up.ac.th` ของคนอื่นได้ จึงห้าม deploy ออกสู่สาธารณะ

## รันในเครื่อง

```bash
docker compose up --build        # ยก Postgres + auth-service (:5002) + notes-service (:5001) + stats-service (:5000)
```

รันแบบไม่ใช้ Docker (ใช้ SQLite แทน Postgres):

```bash
pip install -r services/auth-service/requirements.txt
cd services/auth-service
AUTH_JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(48))") python app.py
```

| Environment variable | ค่า default | ใช้ทำอะไร |
| --- | --- | --- |
| `AUTH_JWT_SECRET` | — (**บังคับ**) | secret สำหรับเซ็น JWT ยาวอย่างน้อย 32 ไบต์ ไม่ตั้งแล้ว service จะไม่สตาร์ต |
| `DATABASE_URL` | `sqlite:///auth.db` | SQLAlchemy URL — compose ตั้งเป็น Postgres ก้อนเดียวกับ notes-service |
| `ALLOWED_EMAIL_DOMAINS` | `up.ac.th` | โดเมนอีเมลที่สมัครได้ คั่นหลายโดเมนด้วย comma · ต้องตรงตัว ไม่นับ subdomain |
| `AUTH_TOKEN_TTL_HOURS` | `8` | อายุของ access token (ชั่วโมง) ไม่มี refresh token |

## API

| Method | Path | คำอธิบาย |
| --- | --- | --- |
| `GET` | `/health` | health check |
| `POST` | `/auth/register` | สมัครสมาชิก → `201` + ข้อมูลบัญชี (ยังไม่ได้ token ต้อง login ต่อ) |
| `POST` | `/auth/login` | login → `200` + `access_token` |
| `POST` | `/auth/logout` | เพิกถอน token ที่ส่งมาทันที → `204` |
| `GET` | `/auth/me` | ข้อมูลบัญชีของ token ที่ส่งมา — service อื่นใช้ตัวนี้ตรวจ token |

body รับได้ทั้ง JSON และ form (`curl -d`) · endpoint ที่ต้องมี token ให้ส่ง header
`Authorization: Bearer <access_token>` · response ไม่มี `password` หรือ `password_hash` ไม่ว่ากรณีใด

### `POST /auth/register`

| ฟิลด์ | เงื่อนไข |
| --- | --- |
| `email` | โดเมนต้องอยู่ใน `ALLOWED_EMAIL_DOMAINS` · ไม่สนตัวพิมพ์เล็ก/ใหญ่ · ยาวไม่เกิน 254 |
| `password` | 8–128 ตัวอักษร · ไม่ตัดช่องว่างหัวท้าย |
| `display_name` | 1–120 ตัวอักษร · ชื่อที่ผู้ใช้ตั้งเอง ใช้แสดงเป็นเครดิตบนโน้ต |

| กรณี | Response |
| --- | --- |
| สำเร็จ | `201` `{id, email, display_name, created_at}` |
| ข้อมูลผิด (รายงานครบทุกช่องในครั้งเดียว) | `400` `{"error": "validation_failed", "fields": {...}}` |
| อีเมลนี้สมัครไว้แล้ว | `409` `{"error": "email_taken", "fields": {"email": ...}}` |
| body ใหญ่เกิน 16 KB | `413` `{"error": "request_too_large"}` |

### `POST /auth/login`

| กรณี | Response |
| --- | --- |
| สำเร็จ | `200` `{access_token, token_type: "Bearer", expires_at, user}` |
| ไม่ได้กรอกอีเมลหรือรหัสผ่าน | `400` `validation_failed` บอกว่าช่องไหนว่าง |
| อีเมลไม่มีในระบบ **หรือ** รหัสผ่านผิด | `401` `{"error": "invalid_credentials", "message": "อีเมลหรือรหัสผ่านไม่ถูกต้อง"}` — เหมือนกันทุกไบต์ ไม่บอกว่าผิดช่องไหน |

### `POST /auth/logout` และ `GET /auth/me`

| กรณี | Response |
| --- | --- |
| token ใช้ได้ | logout `204` · me `200` + ข้อมูลบัญชี |
| ไม่มี token, token ผิดรูป/ลายเซ็นผิด, หมดอายุ หรือ logout ไปแล้ว | `401` `{"error": "unauthorized"}` + header `WWW-Authenticate: Bearer` |

logout เพิกถอนเฉพาะ session ของ token นั้น — ถ้า login ไว้หลายเครื่อง เครื่องอื่นยังใช้ได้

## ตัวอย่างการเรียกใช้

```bash
curl -X POST localhost:5002/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"67026168@up.ac.th","password":"correct horse","display_name":"อติชาติ"}'

TOKEN=$(curl -s -X POST localhost:5002/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"67026168@up.ac.th","password":"correct horse"}' | jq -r .access_token)

curl localhost:5002/auth/me -H "Authorization: Bearer $TOKEN"
curl -X POST localhost:5002/auth/logout -H "Authorization: Bearer $TOKEN"
curl -i localhost:5002/auth/me -H "Authorization: Bearer $TOKEN"   # 401 ทันที
```

## โครงไฟล์

| ไฟล์ | หน้าที่ |
| --- | --- |
| `app.py` | route ทั้งหมด + app factory (`create_app`) + การตรวจ Bearer token |
| `auth_models.py` | ตาราง `users`, `auth_sessions` และ session factory |
| `credentials.py` | ตรวจข้อมูลสมัคร + hash รหัสผ่าน (scrypt) — pure function ทดสอบแยกได้ |
| `auth_tokens.py` | ออก/ตรวจ JWT (ลายเซ็นกับเวลาหมดอายุ) |

ชื่อโมดูลขึ้นต้นด้วย `auth_` เพราะเทสต์เติมทุก service เข้า `sys.path` พร้อมกัน ถ้าใช้ชื่อ
`models.py`/`tokens.py` จะชนกับของ notes-service (ดู `src/tests/conftest.py`)

เทสต์อยู่ที่ [`src/tests/test_auth_credentials.py`](../../src/tests/test_auth_credentials.py),
[`src/tests/test_auth_tokens.py`](../../src/tests/test_auth_tokens.py) และ
[`src/tests/test_auth_api.py`](../../src/tests/test_auth_api.py)
