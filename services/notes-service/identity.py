"""ตรวจตัวตนผู้ใช้ผ่าน User & Auth Service — US-31 (#31)

notes-service ไม่ถือ secret ที่ใช้เซ็น JWT เอง ตาม ADR-005 service อื่นต้องถาม
auth-service ผ่าน `GET /auth/me` ซึ่งตรวจทั้งลายเซ็น เวลาหมดอายุ และ session ที่ถูก
logout ไปแล้ว ถ้าตรวจเองในนี้จะรู้ไม่ได้ว่า token ถูกเพิกถอนหรือยัง

app.py คุยกับไฟล์นี้ผ่าน interface เดียว คือเรียก object เป็นฟังก์ชันด้วยค่า header
`Authorization` แบบเดียวกับที่ storage ถูก inject — เทสต์จึงส่งตัวปลอมเข้าไปแทนได้
โดยไม่ต้องยก auth-service ขึ้นมาจริง
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_AUTH_SERVICE_URL = "http://localhost:5002"
DEFAULT_TIMEOUT_SECONDS = 3


class IdentityUnavailable(Exception):
    """เรียก auth-service ไม่สำเร็จ — แยกจาก "token ใช้ไม่ได้" ที่คืนเป็น None"""


class HttpIdentity:
    def __init__(self, base_url: str, timeout: float = DEFAULT_TIMEOUT_SECONDS):
        # urlopen เปิดได้ทุก scheme รวม file:// — ถ้า AUTH_SERVICE_URL ตั้งผิดจะไปอ่านไฟล์บนเครื่องแทน
        # จึงยอมรับแค่ http/https ตั้งแต่ตอนสร้าง (bandit B310)
        if urllib.parse.urlsplit(base_url).scheme not in ("http", "https"):
            raise ValueError(f"AUTH_SERVICE_URL ต้องเป็น http:// หรือ https:// ไม่ใช่ {base_url!r}")
        self.me_url = base_url.rstrip("/") + "/auth/me"
        self.timeout = timeout

    def __call__(self, authorization: str | None) -> dict | None:
        """คืน `{"id": int, "display_name": str}` ของเจ้าของ token หรือ None ถ้าใช้ไม่ได้

        ไม่ได้ส่ง header มาเลยก็ตอบ None ทันที ไม่ต้องเสีย request ไปถาม auth-service
        """
        if not authorization:
            return None
        request = urllib.request.Request(self.me_url, headers={"Authorization": authorization})
        try:
            # scheme ถูกจำกัดเป็น http/https ใน __init__ แล้ว
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec B310
                body = json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 401:
                return None
            raise IdentityUnavailable(f"auth-service ตอบ {error.code}") from error
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            # URLError = ต่อไม่ติด, TimeoutError = ช้าเกิน, ValueError = body ไม่ใช่ JSON
            raise IdentityUnavailable(str(error)) from error

        try:
            return {"id": int(body["id"]), "display_name": str(body["display_name"])}
        except (KeyError, TypeError, ValueError) as error:
            raise IdentityUnavailable("response ของ /auth/me ผิดรูป") from error


def identity_from_env():
    # สร้างแค่ object ยังไม่ต่อเครือข่าย — app.py ถูกโหลดตอน import (gunicorn `app:app`
    # และ conftest) ถ้าต่อ auth-service ตั้งแต่ตอนนี้ แค่ import ก็จะพังเมื่อ auth-service ยังไม่ขึ้น
    return HttpIdentity(os.environ.get("AUTH_SERVICE_URL", DEFAULT_AUTH_SERVICE_URL))
