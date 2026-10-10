"""Load test ของ NoteShare — วัดเวลาตอบสนองของ API เทียบ NFR-001 / NFR-002 (test plan หัวข้อ 2.24)

รันกับ stack ที่ยกขึ้นแล้ว (`docker compose up`) ผ่าน gateway เหมือนที่ browser เรียก:

    python src/perf/load_test.py --base-url http://localhost:8080

ขั้นตอน: สมัครบัญชีผู้อัปโหลด → อัปโหลดโน้ต (PDF + PNG) หลายร้อยไฟล์ → ให้คะแนนและดาวน์โหลดบางโน้ต
ให้ `sort=rating` และสถิติมีข้อมูลจริง → ยิงแต่ละ scenario พร้อมกันหลาย thread แล้วสรุป p50/p95/p99,
throughput และ error rate พร้อมตัดสินผ่าน/ไม่ผ่านเทียบงบเวลาของ NFR

ข้อจำกัดที่ตั้งใจ:
- วัดเวลาฝั่ง server + network ในเครื่อง ไม่รวมเวลาวาดหน้าจอของ browser · NFR-001/002 นับถึงตอนเห็นผลบนจอ
  จึงใช้งบเต็มของ NFR เป็นเพดานบนสุด ไม่ใช่เป้าที่ "พอดี"
- NFR-014 ไม่ตั้งเป้ารองรับผู้ใช้พร้อมกันจำนวนมาก ค่าเริ่มต้น 10 thread = ห้องเรียนเล็ก ๆ เปิดเว็บพร้อมกัน
- seed ข้อมูลทิ้งไว้ใน DB ที่ชี้ไป จึงยอมรันกับ localhost เท่านั้น ห้ามรันกับเว็บจริงบน Vercel
  (Neon ใช้ร่วมกันระหว่าง preview กับ production และแพ็กเกจ Hobby มีโควตา)
"""

import argparse
import json
import math
import random
import statistics
import struct
import sys
import time
import uuid
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
PASSWORD = "perf-password-123"
PDF_BYTES = b"%PDF-1.4\n% NoteShare load test\n"
FACULTIES = ["ICT", "Engineering", "Science", "Medicine", "Business"]
SUBJECTS = [
    ("Data Structures", "CS201"),
    ("Algorithms", "CS301"),
    ("Database Systems", "CS241"),
    ("Software Engineering", "SE321"),
    ("Calculus I", "MA101"),
    ("Linear Algebra", "MA211"),
    ("Physics I", "PH101"),
    ("Organic Chemistry", "CH221"),
    ("Microeconomics", "EC101"),
    ("Anatomy", "MD111"),
]
LESSONS = ["บทที่ 1 บทนำ", "Linked List", "Big-O", "Normalization", "Integration", "Matrix", "Kinematics"]


def png_bytes(width=320, height=240, seed=0):
    """สร้าง PNG สีพื้นแบบไม่ต้องพึ่ง Pillow — ให้ preview ฝั่ง server มีงานย่อรูปจริง"""
    rng = random.Random(seed)
    pixel = bytes(rng.randrange(256) for _ in range(3))
    raw = b"".join(b"\x00" + pixel * width for _ in range(height))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


@dataclass
class Scenario:
    code: str
    name: str
    nfr: str
    budget_ms: float | None  # None = ไม่มี NFR กำหนดเวลา บันทึกไว้ดูเฉย ๆ
    request: object  # callable(session, rng) -> requests.Response
    expected: tuple = (200,)
    latencies: list = field(default_factory=list)
    errors: int = 0
    elapsed_s: float = 0.0


def percentile(values, pct):
    """nearest-rank: ค่าที่ pct% ของ request เร็วกว่าหรือเท่ากับ"""
    if not values:
        return float("nan")
    ordered = sorted(values)
    return ordered[max(0, math.ceil(pct / 100 * len(ordered)) - 1)]


class LoadTest:
    def __init__(self, base_url, timeout):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.run_id = uuid.uuid4().hex[:6].upper()
        self.users = []  # (email, token)
        self.note_ids = []
        self.png_note_ids = []

    def url(self, path):
        return f"{self.base_url}{path}"

    # ---------- seed ----------

    def register(self, index):
        email = f"perf-{self.run_id.lower()}-{index}@up.ac.th"
        response = requests.post(
            self.url("/auth/register"),
            json={"display_name": f"ผู้ทดสอบโหลด {index}", "email": email, "password": PASSWORD},
            timeout=self.timeout,
        )
        response.raise_for_status()
        login = requests.post(self.url("/auth/login"), json={"email": email, "password": PASSWORD}, timeout=self.timeout)
        login.raise_for_status()
        return email, login.json()["access_token"]

    def upload(self, index):
        _, token = self.users[index % len(self.users)]
        subject_name, subject_code = SUBJECTS[index % len(SUBJECTS)]
        is_png = index % 4 == 0
        files = (
            {"file": (f"note-{index}.png", png_bytes(seed=index), "image/png")}
            if is_png
            else {"file": (f"note-{index}.pdf", PDF_BYTES, "application/pdf")}
        )
        form = {
            "title": f"{subject_name} สรุป {LESSONS[index % len(LESSONS)]} #{index}",
            "subject_name": subject_name,
            "subject_code": subject_code,
            "faculty": FACULTIES[index % len(FACULTIES)],
            "year_level": str(1 + index % 4),
            "lesson": LESSONS[index % len(LESSONS)],
            "topic": f"perf {self.run_id}",
        }
        response = requests.post(
            self.url("/notes"), data=form, files=files,
            headers={"Authorization": f"Bearer {token}"}, timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["id"], is_png

    def seed(self, uploaders, notes, workers):
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=min(workers, uploaders)) as pool:
            self.users = list(pool.map(self.register, range(uploaders)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for note_id, is_png in pool.map(self.upload, range(notes)):
                self.note_ids.append(note_id)
                if is_png:
                    self.png_note_ids.append(note_id)

        # คะแนนต้องดาวน์โหลดก่อน (กติกาของ US-13) — ผู้อัปโหลดแต่ละคนให้คะแนนโน้ตของคนอื่นคนละไม่กี่โน้ต
        def rate(pair):
            (_, token), note_id = pair
            headers = {"Authorization": f"Bearer {token}"}
            requests.get(self.url(f"/notes/{note_id}/download"), headers=headers, timeout=self.timeout)
            requests.put(
                self.url(f"/notes/{note_id}/rating"), json={"rating": 1 + note_id % 5},
                headers=headers, timeout=self.timeout,
            )

        rng = random.Random(42)
        pairs = [(user, rng.choice(self.note_ids)) for user in self.users for _ in range(10)]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(rate, pairs))
        return time.perf_counter() - started

    # ---------- scenarios ----------

    def scenarios(self):
        notes, pngs = self.note_ids, self.png_note_ids or self.note_ids
        _, token = self.users[0]
        email = self.users[0][0]

        def get(path, **kw):
            return lambda s, rng: s.get(self.url(path(rng) if callable(path) else path), timeout=self.timeout, **kw)

        keywords = ["data", "cs201", "matrix", "บทนำ", "algorithms", "Big-O"]
        return [
            Scenario("PF-01", "หน้าเว็บ `/` (HTML)", "NFR-001", 2000, get("/")),
            Scenario("PF-02", "ค้นด้วยคำ `GET /notes?q=`", "NFR-002", 3000,
                     get(lambda rng: f"/notes?q={rng.choice(keywords)}")),
            Scenario("PF-03", "กรอง คณะ + ปี + ชนิดไฟล์", "NFR-002", 3000,
                     get(lambda rng: f"/notes?faculty={rng.choice(FACULTIES)}&year_level={rng.randint(1, 4)}"
                                     f"&file_type={rng.choice(['pdf', 'png'])}")),
            Scenario("PF-04", "เรียงตามคะแนน `sort=rating`", "NFR-002", 3000,
                     get(lambda rng: f"/notes?sort=rating&offset={rng.choice([0, 20, 40])}")),
            Scenario("PF-05", "รายละเอียดโน้ต `GET /notes/<id>`", "NFR-001", 2000,
                     get(lambda rng: f"/notes/{rng.choice(notes)}")),
            Scenario("PF-06", "รูปตัวอย่าง `/preview` (PNG)", "NFR-001", 2000,
                     get(lambda rng: f"/notes/{rng.choice(pngs)}/preview")),
            Scenario("PF-07", "ดาวน์โหลด `/download`", "—", None,
                     get(lambda rng: f"/notes/{rng.choice(notes)}/download",
                         headers={"Authorization": f"Bearer {token}"})),
            Scenario("PF-08", "สถิติภาพรวม `GET /stats`", "—", None, get("/stats")),
            Scenario("PF-09", "เข้าสู่ระบบ `POST /auth/login`", "—", None,
                     lambda s, rng: s.post(self.url("/auth/login"), json={"email": email, "password": PASSWORD},
                                           timeout=self.timeout)),
        ]

    def run(self, scenario, concurrency, total):
        def worker(count, seed):
            rng = random.Random(seed)
            session = requests.Session()
            latencies, errors = [], 0
            for _ in range(count):
                started = time.perf_counter()
                try:
                    response = scenario.request(session, rng)
                    response.content  # อ่าน body ให้ครบ — นับเวลาส่งไฟล์ด้วย
                    ok = response.status_code in scenario.expected
                except requests.RequestException:
                    ok = False
                latencies.append((time.perf_counter() - started) * 1000)
                errors += not ok
            return latencies, errors

        # อุ่นเครื่องก่อนวัด (connection pool, preview ที่ยังไม่ถูกสร้าง) — NFR-001 ไม่นับ cold start
        worker(min(20, total), seed=-1)
        per_thread = [total // concurrency + (i < total % concurrency) for i in range(concurrency)]
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            results = list(pool.map(worker, per_thread, range(concurrency)))
        scenario.elapsed_s = time.perf_counter() - started
        scenario.latencies = [ms for lat, _ in results for ms in lat]
        scenario.errors = sum(err for _, err in results)
        return scenario


def summarize(scenario):
    lat = scenario.latencies
    p95 = percentile(lat, 95)
    error_rate = scenario.errors / len(lat) if lat else 1.0
    if scenario.budget_ms is None:
        verdict = "ไม่มีเป้า" if error_rate == 0 else "error"
    else:
        verdict = "ผ่าน" if p95 <= scenario.budget_ms and error_rate == 0 else "ไม่ผ่าน"
    return {
        "code": scenario.code, "name": scenario.name, "nfr": scenario.nfr,
        "budget_ms": scenario.budget_ms, "requests": len(lat),
        "p50_ms": round(percentile(lat, 50), 1), "p95_ms": round(p95, 1), "p99_ms": round(percentile(lat, 99), 1),
        "mean_ms": round(statistics.fmean(lat), 1) if lat else None,
        "rps": round(len(lat) / scenario.elapsed_s, 1) if scenario.elapsed_s else None,
        "error_rate": round(error_rate * 100, 2), "verdict": verdict,
    }


def markdown_table(rows, concurrency):
    lines = [
        "| # | Scenario | NFR (งบ) | Threads | Requests | p50 ms | p95 ms | p99 ms | req/s | error % | ผล |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        budget = f"{r['nfr']} ({r['budget_ms'] / 1000:g} s)" if r["budget_ms"] else r["nfr"]
        lines.append(
            f"| {r['code']} | {r['name']} | {budget} | {concurrency} | {r['requests']} | {r['p50_ms']} | "
            f"{r['p95_ms']} | {r['p99_ms']} | {r['rps']} | {r['error_rate']} | {r['verdict']} |"
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--uploaders", type=int, default=10, help="จำนวนบัญชีที่ใช้อัปโหลดและให้คะแนน")
    parser.add_argument("--notes", type=int, default=300, help="จำนวนโน้ตที่ seed")
    parser.add_argument("--concurrency", default="1,10", help="จำนวน thread พร้อมกัน คั่นด้วยจุลภาค")
    parser.add_argument("--requests", type=int, default=200, help="จำนวน request ต่อ scenario ต่อระดับ concurrency")
    parser.add_argument("--only", default="", help="รันเฉพาะรหัส scenario เช่น PF-02,PF-09")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--json", help="บันทึกผลเป็นไฟล์ JSON")
    args = parser.parse_args(argv)

    host = urlparse(args.base_url).hostname
    if host not in LOCAL_HOSTS:
        parser.error(f"ยอมรันกับ localhost เท่านั้น (ได้ {host!r}) — สคริปต์นี้เขียนข้อมูลทดสอบลง DB")

    test = LoadTest(args.base_url, args.timeout)
    levels = [int(c) for c in args.concurrency.split(",")]
    seed_s = test.seed(args.uploaders, args.notes, workers=max(levels))
    print(f"seed: {args.uploaders} บัญชี, {len(test.note_ids)} โน้ต ({len(test.png_note_ids)} PNG) ใน {seed_s:.1f} s "
          f"· รหัสรอบ {test.run_id}", flush=True)

    wanted = {code.strip() for code in args.only.split(",") if code.strip()}
    report = {"base_url": args.base_url, "notes": len(test.note_ids), "seed_s": round(seed_s, 1), "levels": {}}
    failed = False
    for level in levels:
        rows = []
        for scenario in test.scenarios():
            if wanted and scenario.code not in wanted:
                continue
            rows.append(summarize(test.run(scenario, level, args.requests)))
            print(f"  {scenario.code} @{level}: p95 {rows[-1]['p95_ms']} ms, error {rows[-1]['error_rate']} %", flush=True)
        failed |= any(r["verdict"] in ("ไม่ผ่าน", "error") for r in rows)
        report["levels"][level] = rows
        print(f"\n{markdown_table(rows, level)}\n", flush=True)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as out:
            json.dump(report, out, ensure_ascii=False, indent=2)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
