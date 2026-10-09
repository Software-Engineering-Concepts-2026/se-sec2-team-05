"""E2E ผ่าน browser จริง — รันกับ stack ที่ยกขึ้นแล้ว (`docker compose up`) ไม่ได้สตาร์ต service เอง

รัน: `pytest src/e2e --base-url http://localhost:8080` (CI job "E2E tests (browser)")
ไม่ได้อยู่ใน `src/tests` ตั้งใจ — `pytest src/tests` ของ job อื่นจะได้ไม่ต้องมี browser และ stack

ทุกเทสต์สมัครบัญชีใหม่และใช้รหัสวิชาที่สุ่มขึ้นมาเอง จึงรันซ้ำบน DB เดิมได้
และไม่ชนกับข้อมูลที่ smoke test หรือคนอื่นทิ้งไว้ · ส่วนที่ไม่ใช่สิ่งที่เทสต์นั้นตรวจ (เช่นอัปโหลดโน้ต
ให้คนอื่นมาเปิด) ทำผ่าน API ตรง ๆ ให้เร็วและไม่เปราะ ส่วนที่ตรวจทำผ่านหน้าเว็บเหมือนผู้ใช้จริง
"""

import uuid
from dataclasses import dataclass

import pytest
import requests

PASSWORD = "e2e-password-123"
PDF_BYTES = b"%PDF-1.4\n% NoteShare E2E\n"


@dataclass
class User:
    name: str
    email: str
    password: str = PASSWORD
    token: str | None = None
    id: int | None = None


def unique(prefix):
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


class Api:
    """เรียก API ผ่าน gateway ตัวเดียวกับที่หน้าเว็บใช้ (same origin)"""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def url(self, path):
        return f"{self.base_url}{path}"

    def register(self, name="ผู้ทดสอบ E2E", login=True):
        user = User(name=name, email=f"{unique('e2e-').lower()}@up.ac.th")
        response = requests.post(
            self.url("/auth/register"),
            json={"display_name": user.name, "email": user.email, "password": user.password},
            timeout=10,
        )
        assert response.status_code == 201, response.text
        if login:
            body = requests.post(
                self.url("/auth/login"), json={"email": user.email, "password": user.password}, timeout=10
            ).json()
            user.token = body["access_token"]
            user.id = body["user"]["id"]
        return user

    def upload(self, user, **fields):
        form = {
            "title": "โน้ต E2E",
            "subject_code": unique("E2E"),
            "subject_name": "End-to-End Testing",
            "faculty": "ICT",
            "year_level": "2",
            "lesson": "บทที่ 1",
            **fields,
        }
        response = requests.post(
            self.url("/notes"),
            data=form,
            files={"file": ("note.pdf", PDF_BYTES, "application/pdf")},
            headers={"Authorization": f"Bearer {user.token}"},
            timeout=10,
        )
        assert response.status_code == 201, response.text
        return response.json()

    def note_status(self, note_id):
        return requests.get(self.url(f"/notes/{note_id}"), timeout=10).status_code


@pytest.fixture
def api(base_url):
    if not base_url:
        pytest.skip("ต้องส่ง --base-url ของ stack ที่ยกไว้แล้ว เช่น http://localhost:8080")
    return Api(base_url)


@pytest.fixture
def log_in(page):
    """เข้าสู่ระบบผ่านหน้า login จริง แล้วรอจนกลับมาหน้าแรก"""

    def run(user):
        page.goto("/login.html")
        form = page.locator("#loginForm")
        form.locator('[name="email"]').fill(user.email)
        form.locator('[name="password"]').fill(user.password)
        form.get_by_role("button", name="เข้าสู่ระบบ").click()
        page.wait_for_url("**/")

    return run
