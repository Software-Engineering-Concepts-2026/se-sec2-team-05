"""สร้างรูปตัวอย่างของโน้ต — US-11 (#11)

เป็น pure function ล้วน ไม่รู้จัก Flask/DB/storage (แนวเดียวกับ validation.py) จึงทดสอบได้
โดยส่งไฟล์เข้ามาตรงๆ ผลลัพธ์เป็น PNG เสมอ ไม่ว่าไฟล์ต้นฉบับจะเป็นชนิดไหน

ไฟล์ที่เข้ามาที่นี่มาจากผู้ใช้ และ validate_file เชื่อ mimetype ที่ client ส่งมาโดยไม่ตรวจ
เนื้อไฟล์ ดังนั้นทุกความล้มเหลวของการอ่าน/แปลงไฟล์ต้องกลายเป็น PreviewUnavailable
(ให้ชั้น API ตอบ 422) ห้ามหลุดออกไปเป็น 500
"""

import io

from PIL import Image, UnidentifiedImageError

PREVIEW_MAX_WIDTH = 800

# กันรูปที่ประกาศขนาดใหญ่ผิดปกติ (decompression bomb) — เช็คจาก header ก่อนถอดรหัสเนื้อภาพ
# 50 ล้านพิกเซลเกินรูปถ่ายจากกล้องมือถือทั่วไป แต่ยังไม่กินหน่วยความจำจนเกินรับได้
MAX_SOURCE_PIXELS = 50_000_000

# ชนิดที่ Pillow ต้องอ่านได้จริง จำกัดชื่อ format ไว้ ไม่ให้ Pillow ไล่ลอง decoder อื่นทั้งหมด
_IMAGE_FORMATS = {
    "image/png": ["PNG"],
    "image/jpeg": ["JPEG"],
}

# โหมดสีที่ PNG เก็บได้ตรงๆ ที่เหลือ (เช่น CMYK จาก JPEG) แปลงเป็น RGB ก่อน
_PNG_SAFE_MODES = {"1", "L", "LA", "P", "RGB", "RGBA"}


class PreviewUnavailable(Exception):
    """สร้างตัวอย่างจากไฟล์นี้ไม่ได้ (ชนิดยังไม่รองรับ ไฟล์เสีย หรือใหญ่เกินไป)"""


def render_preview(fileobj, content_type: str) -> bytes:
    """คืนไบต์ PNG ของตัวอย่าง กว้างไม่เกิน PREVIEW_MAX_WIDTH (ไม่ขยายรูปที่เล็กอยู่แล้ว)"""
    formats = _IMAGE_FORMATS.get(content_type)
    if formats is None:
        raise PreviewUnavailable(f"ยังไม่รองรับตัวอย่างของ {content_type}")

    try:
        with Image.open(fileobj, formats=formats) as image:
            width, height = image.size
            if width * height > MAX_SOURCE_PIXELS:
                raise PreviewUnavailable("รูปใหญ่เกินกว่าจะสร้างตัวอย่างได้")

            image.load()
            if image.mode not in _PNG_SAFE_MODES:
                image = image.convert("RGB")
            if width > PREVIEW_MAX_WIDTH:
                new_height = max(1, round(height * PREVIEW_MAX_WIDTH / width))
                image = image.resize((PREVIEW_MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

            out = io.BytesIO()
            image.save(out, format="PNG")
            return out.getvalue()
    except PreviewUnavailable:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise PreviewUnavailable("อ่านไฟล์เป็นรูปภาพไม่ได้") from exc
