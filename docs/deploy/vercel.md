# Deploy NoteShare บน Vercel

ขั้นตอนนี้ยก NoteShare ขึ้น Vercel ตาม [ADR-009](../architecture/adr/0009-deploy-on-vercel-services.th.md):
หน้าเว็บ `web/` + Flask 3 service เป็น **Vercel Services** ใน project เดียว (ตั้งไว้ใน [`vercel.json`](../../vercel.json)),
ฐานข้อมูลเป็น **Neon Postgres** และไฟล์โน้ตอยู่ใน **Vercel Blob แบบ private**
ส่วน `docker compose up` บนเครื่องยังใช้ได้เหมือนเดิม

> ⚠️ เมื่อ deploy production แล้วเว็บจะเปิดสู่สาธารณะ ใครมีอีเมล `@up.ac.th` ก็สมัครได้

## สิ่งที่ต้องมี

- บัญชี Vercel (แพ็กเกจ Hobby ใช้ได้ Services เปิดให้ทุกแพ็กเกจในช่วง beta)
- Node.js สำหรับติดตั้ง Vercel CLI (`npm i -g vercel`) แล้ว `vercel login`
- clone repo นี้ไว้ในเครื่อง · deploy จากเครื่องด้วย CLI ไม่ต้องให้สิทธิ์ Vercel กับ GitHub organization
  (ถ้าจะให้ deploy อัตโนมัติทุกครั้งที่ push ต้องให้เจ้าของ organization ติดตั้ง Vercel GitHub App ก่อน)

## 1. สร้างและเชื่อม project

ที่ root ของ repo:

```bash
vercel link
```

ตอบให้สร้าง project ใหม่ · คำสั่งนี้สร้างโฟลเดอร์ `.vercel/` และไฟล์ `.env.local` ในเครื่อง (อยู่ใน `.gitignore` แล้ว ห้าม commit)

> ⚠️ `vercel link` และข้อ 2–3 ชอบเพิ่มบรรทัดใน `.gitignore` เอง และ `vercel integration add neon` วางไฟล์ skill ของ Neon
> ลงใน repo (`.agents/`, `.claude/skills/`, `skills-lock.json`) ทั้งหมดไม่ใช่ส่วนของโปรเจกต์ ให้ `git checkout -- .gitignore`
> แล้วลบไฟล์เหล่านั้นทิ้งก่อน commit

## 2. ฐานข้อมูล Neon

```bash
vercel integration add neon --plan free_v3 -m region=iad1
```

หรือในหน้า project → **Storage** → **Create Database** → Neon แล้วเชื่อมกับ project นี้
Vercel จะใส่ `DATABASE_URL` ให้เอง ไม่ต้องแก้รูปแบบ URL เพราะ service แปลง `postgres://` เป็น psycopg 3 ให้
ตารางถูกสร้างและอัปเกรดด้วย migration ของ Alembic ตอน service ทำงานครั้งแรกของแต่ละ deploy (ADR-010)

## 3. ที่เก็บไฟล์ Vercel Blob (private)

```bash
vercel blob create-store noteshare-files --access private --region iad1
```

หรือหน้า project → **Storage** → **Create Storage** → **Blob** → ตั้ง access เป็น **Private** แล้วเชื่อมกับ project
การเชื่อม store กับ project จะเพิ่ม **`BLOB_READ_WRITE_TOKEN`** ให้ทุก environment เอง (ตรวจแล้วตอน deploy จริง 2026-10-06)
ซึ่งเป็นตัวแปรเดียวที่ `vercel` Python SDK ของ notes-service (0.11.4) อ่าน · ถ้าไม่มี ให้สร้าง read-write token ในหน้าตั้งค่าของ store
แล้วเพิ่มเองด้วย `vercel env add BLOB_READ_WRITE_TOKEN`

## 4. Environment variables

ตั้งทั้ง **Production** และ **Preview** (`vercel env add <ชื่อ>` หรือหน้า **Settings → Environment Variables**):

| ชื่อ | ค่า | ใช้ที่ |
| --- | --- | --- |
| `AUTH_JWT_SECRET` | สุ่มใหม่ ยาวอย่างน้อย 32 ไบต์ เช่นผลของ `python -c "import secrets; print(secrets.token_urlsafe(48))"` · **ห้ามใช้ค่าใน `docker-compose.yml`** | auth |
| `ALLOWED_EMAIL_DOMAINS` | `up.ac.th` | auth |
| `AUTH_TOKEN_TTL_HOURS` | `8` | auth |
| `NOTES_STORAGE_BACKEND` | `blob` | notes |
| `ADMIN_USER_IDS` | ว่างไว้ก่อน (ดูข้อ 6) | notes |
| `DATABASE_URL` | Neon ใส่ให้ (ข้อ 2) | notes, auth, stats |
| `BLOB_READ_WRITE_TOKEN` | Blob ใส่ให้ (ข้อ 3) | notes |

`AUTH_SERVICE_URL` **ไม่ต้องตั้ง** · Vercel ใส่ให้ notes และ stats ผ่าน service binding ใน `vercel.json`

เพดานของ rate limit ที่ login และสมัครสมาชิก (`AUTH_LOGIN_MAX_FAILS_PER_EMAIL`, `AUTH_LOGIN_MAX_FAILS_PER_IP`,
`AUTH_REGISTER_MAX_PER_IP` และหน้าต่างเวลา, ADR-011) ไม่ต้องตั้ง ใช้ค่า default ได้เลย · ตัวนับอยู่ในตาราง `auth_attempts`
ของ Neon จึงใช้ร่วมกันทุก instance · ดูค่า default ใน [`services/auth-service/README.md`](../../services/auth-service/README.md)

## 5. Deploy

```bash
vercel deploy --target preview   # preview — ได้ URL ทดสอบ (ปกติต้อง login Vercel ก่อนเปิด)
vercel deploy --prod             # production — URL สาธารณะ
```

## 6. ตั้งผู้ดูแล

สมัครบัญชีของผู้ดูแลผ่านหน้าเว็บ แล้วดู id ของบัญชีนั้น (เช่นใน Neon console: `select id, email from users;`)
จากนั้นตั้ง `ADMIN_USER_IDS` เป็น id นั้น (คั่นด้วย comma ถ้ามีหลายคน) แล้ว deploy ใหม่

## 7. ตรวจหลัง deploy

- [ ] เปิด URL แล้วเห็นหน้าค้นหา · `/notes` ตอบ JSON
- [ ] สมัคร + login ได้ (ทดสอบ auth และ `DATABASE_URL`)
- [ ] อัปโหลด PDF ขนาด 5–10 MB ได้ แล้วแก้ชื่อและลบได้จากหน้าโปรไฟล์ (ทดสอบการอัปโหลดตรงเข้า Blob ตาม ADR-012 และ binding ไป auth)
- [ ] เปิดหน้าโน้ต เห็นภาพตัวอย่าง ดาวน์โหลดได้
- [ ] หน้าสถิติแสดงตัวเลข (ทดสอบ route `/stats` และ `/notes/<id>/stats`)
- [ ] บัญชีผู้ดูแลเห็นปุ่ม "ตรวจรายงานโน้ต" ในโปรไฟล์
- [ ] gateway ตรวจ login (ADR-014): `/notes/1/stats` ไม่มี token ได้ `{"error": "unauthorized"}` (ถ้าได้ `Authentication required`
  แปลว่า middleware `gateway/proxy.ts` ไม่ได้ทำงาน และ request หลุดไปถึง stats-service)

ถ้า preview เปิดไม่ได้เพราะ Deployment Protection ให้ทดสอบด้วย `vercel curl <url>/notes` ซึ่งผ่าน protection ให้เอง
ถ้ามี error ดูที่หน้า deployment → **Logs** แยกตาม service

## ข้อจำกัดที่ควรรู้

- ไฟล์อัปโหลดได้ถึง **10 MB** เพราะหน้าเว็บส่งไฟล์ตรงเข้า Blob ไม่ผ่าน function (ADR-012) · ถ้าเรียก `POST /notes` แบบฟอร์มเองยังได้แค่ 4 MB
  เพราะ Vercel รับ body ได้ไม่เกิน 4.5 MB
- ไฟล์ที่อัปโหลดตรงแล้วไม่ได้สร้างโน้ต (ปิดแท็บกลางทาง) ค้างใน `uploads/<user id>/` จนผู้ใช้คนนั้นขออัปโหลดครั้งถัดไป ระบบจึงลบให้
- request แรกหลังไม่มีคนใช้สักพักจะช้า (cold start)
- route ที่ต้อง login ผ่าน Routing Middleware (`gateway/proxy.ts`, ADR-014) ซึ่งถาม `/auth/me` ของ deployment เดียวกันอีกรอบ
  จึงช้ากว่า route ที่เปิดให้ทุกคนหนึ่ง request · ต้องตั้งผ่าน `"proxy"` ใน `vercel.json` เพราะไฟล์ `middleware.ts` ที่ root
  ถูกเมินเมื่อ project ใช้ `services`
- schema อัปเกรดเองตอน deploy (ADR-010) · preview กับ production ใช้ Neon ก้อนเดียวกัน ห้าม deploy preview ของ branch ที่มี migration ใหม่
  เพราะ migration จะไปแก้ฐานข้อมูลของ production ทันที
- ข้อมูลเดิมในเครื่อง (`docker compose`) ไม่ได้ย้ายขึ้นไปด้วย
