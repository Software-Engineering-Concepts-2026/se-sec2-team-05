# ⏱️ Load test

[`load_test.py`](./load_test.py) วัดเวลาตอบสนองของ API เทียบ NFR-001 และ NFR-002 ([nfr.md](../../docs/requirements/nfr.md))
ผลล่าสุดและรายละเอียดแต่ละ scenario อยู่ใน test plan หัวข้อ 2.24 ([docs/testing/readme.md](../../docs/testing/readme.md))

## วิธีรัน

```bash
docker compose up -d --build
pip install -r src/perf/requirements.txt
python src/perf/load_test.py --base-url http://localhost:8080
# ปรับได้: --notes 300 --uploaders 10 --concurrency 1,10,25 --requests 200 --only PF-02,PF-09 --json result.json
```

สคริปต์ทำ 2 ขั้น:

1. **seed** ผ่าน API จริง: สมัครบัญชี `perf-<รหัสรอบ>-<n>@up.ac.th` → อัปโหลดโน้ต (PDF ทุก 3 ใน 4 ไฟล์ ที่เหลือเป็น PNG
   ให้ preview มีงานย่อรูปจริง) → แต่ละบัญชีดาวน์โหลดแล้วให้คะแนน 10 โน้ต ให้ `sort=rating` และสถิติมีข้อมูล
2. **วัด** ทีละ scenario (PF-01 ถึง PF-09) ทีละระดับ concurrency: อุ่นเครื่อง 20 request ก่อน (NFR-001 ไม่นับ cold start)
   แล้วยิงตามจำนวนที่กำหนดพร้อมกันหลาย thread · สรุป p50/p95/p99, req/s และ error % เป็นตาราง Markdown
   · ผ่าน = p95 ไม่เกินงบเวลาของ NFR และไม่มี error · exit code เป็น 1 ถ้ามีข้อไหนไม่ผ่าน

## ข้อควรรู้

- **ยอมรันกับ `localhost` เท่านั้น** สคริปต์เขียนบัญชีและโน้ตทดสอบลง DB ที่ชี้ไป ล้างด้วย `docker compose down -v`
  ห้ามรันกับเว็บจริงบน Vercel: Neon ใช้ร่วมกันระหว่าง preview กับ production และแพ็กเกจ Hobby มีโควตา
- ถ้ามี compose stack อื่นใช้ port อยู่ ให้ยก stack แยกด้วย `-p <ชื่อ>` และไฟล์ override ที่ map แค่ `web` ไป port อื่น
  (`ports: !override ["8282:8080"]` และ `ports: !reset []` ให้ service ที่เหลือ)
- เวลาที่วัดคือฝั่ง server + network ในเครื่อง ไม่รวมเวลาวาดหน้าจอของ browser · NFR-001/002 นับถึงตอนเห็นผลบนจอ
  จึงถือว่างบเต็มของ NFR เป็นเพดานบนสุด
- NFR-014 ไม่ตั้งเป้ารองรับผู้ใช้พร้อมกันจำนวนมาก ระดับ 10 และ 25 thread ใช้ดูว่าระบบเริ่มช้าตรงไหน ไม่ใช่เกณฑ์ผ่าน

## ทำไมไม่อยู่ใน CI

- ตัวเลขขึ้นกับเครื่อง runner ของ GitHub ที่ใช้ร่วมกับคนอื่น ผลแกว่งจนตั้งเกณฑ์ผ่าน/ไม่ผ่านที่ไม่หลอกไม่ได้
- ต้อง build image และ seed หลายร้อยโน้ตทุกรอบ เพิ่มเวลา CI อีกหลายนาทีโดยแทบไม่จับบั๊กที่เทสต์อื่นไม่จับ
- job `E2E tests (browser)` และ `Build & smoke-test stack` ยืนยันอยู่แล้วว่า stack เดียวกันนี้ทำงานได้
  ให้รันสคริปต์นี้เองก่อนส่งงานที่แตะ query ค้นหา, `sort=rating`, preview หรือการ hash รหัสผ่าน
