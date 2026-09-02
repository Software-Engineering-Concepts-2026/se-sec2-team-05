"""ทำให้ pytest มองเห็นโค้ดของ Stats Service โดยไม่ต้องติดตั้งเป็น package

ตอนนี้ service ยังเป็น script เดี่ยว ๆ (services/stats-service/app.py) ยังไม่มี
setup.py/pyproject ให้ pip install -e ได้ จึงเติม path เข้า sys.path ตรง ๆ ไปก่อน
เมื่อ service ถูกยกระดับเป็น package จริงให้ลบไฟล์นี้ทิ้งได้เลย
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATS_SERVICE = REPO_ROOT / "services" / "stats-service"

if str(STATS_SERVICE) not in sys.path:
    sys.path.insert(0, str(STATS_SERVICE))
