"""ทำให้ pytest มองเห็นโค้ดของแต่ละ service โดยไม่ต้องติดตั้งเป็น package

ตอนนี้ service ยังเป็น script ธรรมดา ยังไม่มี setup.py/pyproject ให้ pip install -e ได้
จึงเติม path เข้า sys.path ตรง ๆ ไปก่อน เมื่อ service ถูกยกระดับเป็น package จริงให้ลบไฟล์นี้ได้

หมายเหตุสำคัญ: ทุก service มีไฟล์ entrypoint ชื่อ `app.py` เหมือนกันหมด ถ้าปล่อยให้
เทสต์ `import app` ตรง ๆ ตัวไหนอยู่ต้น sys.path ก็จะชนะแล้วอีก service ถูกเทสต์ผิดตัว
(เจอจริงตอนเพิ่ม notes-service — เทสต์ของ stats-service กลายเป็นไปเรียก notes-service)
จึงโหลด `app.py` ของแต่ละ service ด้วย importlib ภายใต้ชื่อโมดูลที่ไม่ซ้ำกัน แล้วส่งต่อ
ให้เทสต์ผ่าน fixture แทน ส่วนโมดูลอื่น (models/storage/validation) ชื่อไม่ชนกันจึง import ปกติได้
"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES = REPO_ROOT / "services"

for service in ("stats-service", "notes-service"):
    path = str(SERVICES / service)
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest  # noqa: E402  (ต้องเติม sys.path ให้เสร็จก่อน)

# `app.py` ของ Notes Service สร้าง app ตอน import (gunicorn ต้องการ `app:app`) ซึ่งแปลว่า
# แค่โหลดโมดูลก็จะสร้างไฟล์ DB และโฟลเดอร์ storage ตามค่า default ทันที ชี้ทั้งสองอย่าง
# ไปที่ temp dir ก่อนโหลด เทสต์จะได้ไม่ทิ้งขยะไว้ในรีโปหรือที่ /data บนเครื่องคนรัน
_SANDBOX = Path(tempfile.mkdtemp(prefix="noteshare-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_SANDBOX / 'import-time.db'}"
os.environ["NOTES_STORAGE_DIR"] = str(_SANDBOX / "storage")


def _load_entrypoint(service: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SERVICES / service / "app.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


stats_app_module = _load_entrypoint("stats-service", "stats_service_app")
notes_app_module = _load_entrypoint("notes-service", "notes_service_app")


@pytest.fixture
def stats_client():
    stats_app_module.app.config.update(TESTING=True)
    return stats_app_module.app.test_client()


@pytest.fixture
def notes_create_app():
    """คืนฟังก์ชัน create_app ของ Notes Service ให้เทสต์ประกอบ app เองตามต้องการ"""
    return notes_app_module.create_app
