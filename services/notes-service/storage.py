"""ที่เก็บไฟล์โน้ต

ADR-001 เลือก S3-compatible object storage เป็นปลายทาง แต่รอบ tracer bullet นี้ใช้
โฟลเดอร์บนดิสก์ที่ mount เป็น volume ไปก่อน เพื่อไม่ให้ต้องยก MinIO ขึ้นมาพร้อมกัน
ตั้งแต่ commit แรก — โค้ดส่วนที่เหลือคุยกับ storage ผ่าน interface นี้เท่านั้น
(`save`, `open`, `delete`) การสลับไป boto3/MinIO จึงแตะแค่ไฟล์นี้ไฟล์เดียว

บน Vercel ดิสก์ของ function หายทุกครั้งที่ instance ถูกปิด จึงมี `BlobFileStorage` ที่เก็บใน
Vercel Blob แบบ private แทน (ADR-009) เลือกด้วย `NOTES_STORAGE_BACKEND=blob`
"""

import io
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

    def save_bytes(self, key: str, data: bytes) -> None:
        """เขียนไบต์ลง key (ใช้กับรูปตัวอย่างที่ระบบสร้างเอง ไม่ใช่ไฟล์ที่ผู้ใช้อัปโหลด)

        เขียนลงไฟล์ชั่วคราวแล้วค่อยเปลี่ยนชื่อ กันสอง request ที่สร้างรูปเดียวกันพร้อมกัน
        จนอีกฝั่งอ่านเจอไฟล์ที่เขียนไม่เสร็จ
        """
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            tmp.write_bytes(data)
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

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


class BlobFileStorage:
    """เก็บไฟล์ใน Vercel Blob แบบ private (ADR-009) — method ชุดเดียวกับ LocalFileStorage

    `client` คือ `vercel.blob.BlobClient` หรือของปลอมในเทสต์ที่มี `put`/`get`/`head`/`delete`
    `not_found` คือ exception ที่ client โยนเมื่อไม่มีไฟล์ (`BlobNotFoundError`) ซึ่งแปลงเป็น
    `FileNotFoundError` ให้ app.py จัดการแบบเดียวกับไฟล์บนดิสก์
    """

    def __init__(self, client, not_found: type[Exception]):
        self.client = client
        self.not_found = not_found

    def build_key(self, content_type: str) -> str:
        return f"{uuid.uuid4().hex}{ALLOWED_CONTENT_TYPES[content_type]}"

    def save(self, key: str, file_storage) -> None:
        # ไฟล์ไม่เกิน MAX_FILE_BYTES (4 MB) อ่านเข้าหน่วยความจำทั้งก้อนได้
        self.client.put(
            key,
            file_storage.stream.read(),
            access="private",
            content_type=file_storage.mimetype or None,
            overwrite=False,
        )

    def save_bytes(self, key: str, data: bytes) -> None:
        # รูปตัวอย่างอาจถูกสร้างซ้ำพร้อมกันจากสอง request ผลเหมือนกัน จึงยอมให้เขียนทับ
        self.client.put(key, data, access="private", content_type="image/png", overwrite=True)

    def exists(self, key: str) -> bool:
        try:
            self.client.head(key)
        except self.not_found:
            return False
        return True

    def open(self, key: str):
        try:
            result = self.client.get(key, access="private")
        except self.not_found as error:
            raise FileNotFoundError(key) from error
        return io.BytesIO(result.content)

    def delete(self, key: str) -> None:
        try:
            self.client.delete(key)
        except self.not_found:
            pass


def storage_from_env():
    if os.environ.get("NOTES_STORAGE_BACKEND", "local") == "blob":
        # import เฉพาะตอนใช้ Blob เครื่องที่รันแบบ local ไม่ต้องมี token ของ Vercel
        from vercel.blob import BlobClient, BlobNotFoundError

        return BlobFileStorage(BlobClient(), BlobNotFoundError)
    return LocalFileStorage(os.environ.get("NOTES_STORAGE_DIR", "/data/notes"))
