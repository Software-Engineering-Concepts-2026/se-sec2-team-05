"""ที่เก็บไฟล์โน้ต

ADR-001 เลือก S3-compatible object storage เป็นปลายทาง แต่รอบ tracer bullet นี้ใช้
โฟลเดอร์บนดิสก์ที่ mount เป็น volume ไปก่อน เพื่อไม่ให้ต้องยก MinIO ขึ้นมาพร้อมกัน
ตั้งแต่ commit แรก — โค้ดส่วนที่เหลือคุยกับ storage ผ่าน interface นี้เท่านั้น
(`save`, `open`, `delete`) การสลับไป boto3/MinIO จึงแตะแค่ไฟล์นี้ไฟล์เดียว
"""

import os
import uuid
from pathlib import Path

from validation import ALLOWED_CONTENT_TYPES


class LocalFileStorage:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def build_key(self, content_type: str) -> str:
        """สร้างชื่อไฟล์ใหม่เอง ไม่ใช้ชื่อที่ผู้ใช้ส่งมา

        ชื่อไฟล์จากผู้ใช้เชื่อไม่ได้ (path traversal เช่น `../../etc/passwd` หรือชื่อชนกัน)
        ชื่อเดิมยังถูกเก็บไว้ในคอลัมน์ `file_name` เพื่อใช้ตอนดาวน์โหลด
        """
        return f"{uuid.uuid4().hex}{ALLOWED_CONTENT_TYPES[content_type]}"

    def save(self, key: str, file_storage) -> None:
        file_storage.save(self._path(key))

    def open(self, key: str):
        return open(self._path(key), "rb")

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def _path(self, key: str) -> Path:
        # กันไม่ให้ key ที่ผิดรูปพาออกนอกโฟลเดอร์ storage
        path = (self.root / key).resolve()
        if not str(path).startswith(str(self.root.resolve())):
            raise ValueError(f"invalid storage key: {key!r}")
        return path


def storage_from_env():
    return LocalFileStorage(os.environ.get("NOTES_STORAGE_DIR", "/data/notes"))
