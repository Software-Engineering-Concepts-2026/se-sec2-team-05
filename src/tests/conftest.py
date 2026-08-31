"""ทำให้ pytest มองเห็นโค้ดของแต่ละ service โดยไม่ต้องติดตั้งเป็น package

ตอนนี้ service ยังเป็น script ธรรมดา ยังไม่มี setup.py/pyproject ให้ pip install -e ได้
จึงเติม path เข้า sys.path ตรง ๆ ไปก่อน เมื่อ service ถูกยกระดับเป็น package จริงให้ลบไฟล์นี้ได้
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES = REPO_ROOT / "services"

for service in ("stats-service", "notes-service"):
    path = str(SERVICES / service)
    if path not in sys.path:
        sys.path.insert(0, path)
