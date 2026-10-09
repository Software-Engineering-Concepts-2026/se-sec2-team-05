"""ที่เก็บไฟล์โน้ต

ADR-001 เลือก S3-compatible object storage เป็นปลายทาง แต่รอบ tracer bullet นี้ใช้
โฟลเดอร์บนดิสก์ที่ mount เป็น volume ไปก่อน เพื่อไม่ให้ต้องยก MinIO ขึ้นมาพร้อมกัน
ตั้งแต่ commit แรก — โค้ดส่วนที่เหลือคุยกับ storage ผ่าน interface นี้เท่านั้น
(`save`, `open`, `delete`) การสลับไป boto3/MinIO จึงแตะแค่ไฟล์นี้ไฟล์เดียว

บน Vercel ดิสก์ของ function หายทุกครั้งที่ instance ถูกปิด จึงมี `BlobFileStorage` ที่เก็บใน
Vercel Blob แบบ private แทน (ADR-009) เลือกด้วย `NOTES_STORAGE_BACKEND=blob`

`BlobFileStorage` ยังออก client token ให้ browser อัปโหลดไฟล์ตรงเข้า Blob ได้ (ADR-012) ไฟล์
จึงไม่ต้องผ่าน function ที่รับ body ได้ไม่เกิน 4.5 MB · `LocalFileStorage` ไม่มีทางนี้
(`supports_direct_upload = False`) หน้าเว็บบน compose จึงส่งไฟล์มาในฟอร์มเหมือนเดิม
"""

import base64
import hashlib
import hmac
import io
import json
import os
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

from validation import ALLOWED_CONTENT_TYPES, MAX_FILE_BYTES, MAX_FORM_FILE_BYTES_ON_BLOB

# endpoint ที่ `put` ของ `@vercel/blob/client` ส่งไฟล์ไป และเวอร์ชันของ API ที่ library นั้นใช้
# (อ่านจาก @vercel/blob 2.8.0: defaultVercelBlobApiUrl, BLOB_API_VERSION)
BLOB_API_URL = "https://vercel.com/api/blob"
BLOB_API_VERSION = "12"
# client token ใช้ได้ไม่นาน แค่พอให้ browser เริ่มส่งไฟล์ 10 MB บนเน็ตช้า ๆ
CLIENT_TOKEN_TTL_SECONDS = 10 * 60


def store_id_from_token(read_write_token: str) -> str:
    """`vercel_blob_rw_<storeId>_<secret>` → `<storeId>` แบบเดียวกับ parseStoreIdFromReadWriteToken"""
    parts = read_write_token.split("_")
    if len(parts) < 4 or not parts[3]:
        raise ValueError("BLOB_READ_WRITE_TOKEN ไม่ใช่รูปแบบ vercel_blob_rw_<storeId>_<secret>")
    return parts[3]


def generate_client_token(read_write_token: str, *, pathname: str, maximum_size_in_bytes: int,
                          allowed_content_types: list[str], valid_until_ms: int) -> str:
    """client token ของ Vercel Blob แบบเดียวกับ generateClientTokenFromReadWriteToken ใน
    `@vercel/blob` (Python SDK ไม่มี) — Blob ตรวจลายเซ็นแล้วบังคับเงื่อนไขใน payload เอง:
    ใช้ได้กับ pathname นี้เท่านั้น ห้ามใหญ่เกิน ห้ามชนิดอื่น ห้ามเขียนทับ และหมดอายุตาม validUntil

    payload = base64(JSON) · ลายเซ็น = HMAC-SHA256 ของ payload ด้วย read-write token เป็น hex
    token = `vercel_blob_client_<storeId>_` + base64(`<ลายเซ็น>.<payload>`)
    """
    payload = base64.b64encode(json.dumps({
        "pathname": pathname,
        "maximumSizeInBytes": maximum_size_in_bytes,
        "allowedContentTypes": allowed_content_types,
        "addRandomSuffix": False,
        "allowOverwrite": False,
        "validUntil": valid_until_ms,
    }, separators=(",", ":")).encode()).decode()
    signature = hmac.new(read_write_token.encode(), payload.encode(), hashlib.sha256).hexdigest()
    secured = base64.b64encode(f"{signature}.{payload}".encode()).decode()
    return f"vercel_blob_client_{store_id_from_token(read_write_token)}_{secured}"


class LocalFileStorage:
    supports_direct_upload = False
    # ไม่มีเพดาน body ของ Vercel มาบังคับ ฟอร์มรับไฟล์ได้เต็ม 10 MB
    form_upload_limit = MAX_FILE_BYTES

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
    `read_write_token` ใช้เซ็น client token ให้ browser (ADR-012) — ไม่มีก็อัปโหลดตรงไม่ได้
    """

    # ใช้ Blob = รันบน Vercel ที่รับ body ได้ไม่เกิน 4.5 MB (ADR-009)
    form_upload_limit = MAX_FORM_FILE_BYTES_ON_BLOB

    def __init__(self, client, not_found: type[Exception], read_write_token: str | None = None,
                 clock=time.time):
        self.client = client
        self.not_found = not_found
        self.read_write_token = read_write_token
        self.clock = clock

    @property
    def supports_direct_upload(self) -> bool:
        return bool(self.read_write_token)

    def build_key(self, content_type: str) -> str:
        return f"{uuid.uuid4().hex}{ALLOWED_CONTENT_TYPES[content_type]}"

    def direct_upload(self, key: str, content_type: str, max_bytes: int) -> dict:
        """สิ่งที่ browser ต้องใช้ส่งไฟล์ตรงเข้า Blob ที่ `key` — ดู web/upload.js"""
        valid_until_ms = int((self.clock() + CLIENT_TOKEN_TTL_SECONDS) * 1000)
        return {
            "pathname": key,
            "upload_url": BLOB_API_URL + "/?" + urlencode({"pathname": key}),
            "client_token": generate_client_token(
                self.read_write_token,
                pathname=key,
                maximum_size_in_bytes=max_bytes,
                allowed_content_types=[content_type],
                valid_until_ms=valid_until_ms,
            ),
            "store_id": store_id_from_token(self.read_write_token),
            "api_version": BLOB_API_VERSION,
            "expires_at": valid_until_ms,
        }

    def list_uploads(self, prefix: str) -> list[tuple[str, object]]:
        """(pathname, เวลาอัปโหลด) ของทุกไฟล์ใต้ prefix — ใช้หาไฟล์ที่อัปโหลดตรงแล้วไม่มีโน้ตตามมา"""
        return [(item.pathname, item.uploaded_at) for item in self.client.iter_objects(prefix=prefix)]

    def stat(self, key: str) -> tuple[int, str]:
        """(ขนาดไบต์, content type) ของไฟล์ที่อยู่ใน Blob แล้ว — ไม่มีไฟล์โยน FileNotFoundError"""
        try:
            result = self.client.head(key)
        except self.not_found as error:
            raise FileNotFoundError(key) from error
        return int(result.size), (result.content_type or "").lower()

    def save(self, key: str, file_storage) -> None:
        # ไฟล์ไม่เกิน MAX_FILE_BYTES (10 MB) อ่านเข้าหน่วยความจำทั้งก้อนได้
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

        return BlobFileStorage(
            BlobClient(), BlobNotFoundError, os.environ.get("BLOB_READ_WRITE_TOKEN")
        )
    return LocalFileStorage(os.environ.get("NOTES_STORAGE_DIR", "/data/notes"))
