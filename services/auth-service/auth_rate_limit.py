"""Rate limit ของ login และสมัครสมาชิก (ADR-011)

นับจากแถวในตาราง `auth_attempts` ภายในหน้าต่างเวลาที่เลื่อนไปเรื่อย ๆ (sliding window)
- login ที่ไม่ผ่าน นับแยกทั้งต่ออีเมลและต่อ IP — ต่ออีเมลกันการเดารหัสของบัญชีเดียว ต่อ IP กันการไล่เดาหลายบัญชี
  login สำเร็จแล้วล้างตัวนับของอีเมลนั้น · ช่วงที่ถูกล็อกไม่ตรวจรหัสผ่านเลย แม้รหัสถูกก็ได้ 429
- สมัครสมาชิก นับต่อ IP ทุกคำขอที่ผ่าน validation (ทั้งที่สมัครได้และที่ชนอีเมลซ้ำ) เพราะคำตอบ "อีเมลซ้ำ"
  เผยได้ว่าอีเมลไหนมีบัญชี (ADR-005) จึงต้องจำกัดไม่ให้ไล่ถามได้เรื่อย ๆ

นับต่ออีเมลที่ส่งมาไม่ว่าบัญชีจะมีจริงหรือไม่ อีเมลที่ไม่มีบัญชีจึงถูกล็อกเหมือนกัน — ไม่เผยว่าอีเมลไหนสมัครไว้
"""

import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from auth_models import AuthAttempt

LOGIN_FAILED = "login_failed"
REGISTER = "register"


@dataclass(frozen=True)
class Limit:
    max_attempts: int
    window: timedelta


@dataclass(frozen=True)
class RateLimits:
    # 5 ครั้งต่อบัญชีพอสำหรับคนพิมพ์ผิด แต่น้อยพอให้เดารหัสแทบไม่ได้
    login_per_email: Limit = Limit(5, timedelta(minutes=15))
    # ต่อ IP สูงกว่าต่ออีเมลมาก เพราะนักศึกษาในมหาวิทยาลัยออกเน็ตผ่าน IP สาธารณะเดียวกันได้หลายคน
    login_per_ip: Limit = Limit(30, timedelta(minutes=15))
    # สมัครพร้อมกันทั้งห้องเรียนจากเน็ตมหาวิทยาลัยต้องยังผ่าน จึงเผื่อไว้ 20 ต่อชั่วโมง
    register_per_ip: Limit = Limit(20, timedelta(hours=1))

    def longest_window(self) -> timedelta:
        return max(self.login_per_email.window, self.login_per_ip.window, self.register_per_ip.window)


def _positive_int(env, name, default):
    raw = env.get(name)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise RuntimeError(f"{name} ต้องเป็นจำนวนเต็ม") from None
    if value < 1:
        raise RuntimeError(f"{name} ต้องมีค่าอย่างน้อย 1")
    return value


def limits_from_env(env=None) -> RateLimits:
    """อ่านเพดานจาก environment ทุกค่ามีค่า default ใน RateLimits ไม่ต้องตั้งก็ได้"""
    env = os.environ if env is None else env
    default = RateLimits()

    def minutes(name, window):
        return timedelta(minutes=_positive_int(env, name, int(window.total_seconds() // 60)))

    def count(name, limit):
        return _positive_int(env, name, limit.max_attempts)

    login_window = minutes("AUTH_LOGIN_WINDOW_MINUTES", default.login_per_email.window)
    register_window = minutes("AUTH_REGISTER_WINDOW_MINUTES", default.register_per_ip.window)
    return RateLimits(
        login_per_email=Limit(count("AUTH_LOGIN_MAX_FAILS_PER_EMAIL", default.login_per_email), login_window),
        login_per_ip=Limit(count("AUTH_LOGIN_MAX_FAILS_PER_IP", default.login_per_ip), login_window),
        register_per_ip=Limit(count("AUTH_REGISTER_MAX_PER_IP", default.register_per_ip), register_window),
    )


def email_key(email: str) -> str:
    return f"email:{email}"


def ip_key(ip: str) -> str:
    return f"ip:{ip}"


def client_ip(request) -> str:
    """ที่อยู่ของผู้ใช้จริงหลัง proxy ตัวเดียวที่อยู่หน้า service

    ใช้ค่าขวาสุดของ `X-Forwarded-For` คือค่าที่ proxy ตัวที่อยู่ติด service เติมเอง (nginx ใช้
    `$proxy_add_x_forwarded_for` ซึ่งต่อท้าย, Vercel เขียนทับทั้ง header) ไม่ใช้ค่าซ้ายสุด
    เพราะ client ใส่ค่านั้นมาเองได้ ถ้าเชื่อ ก็แค่เปลี่ยน header ทุกคำขอเพื่อหลบ limit ต่อ IP
    """
    forwarded = request.headers.get("X-Forwarded-For", "")
    hops = [hop.strip() for hop in forwarded.split(",") if hop.strip()]
    if hops:
        return hops[-1]
    return request.remote_addr or "unknown"


def _aware(value: datetime) -> datetime:
    # SQLite คืน datetime แบบไม่มี timezone แม้คอลัมน์จะประกาศ timezone=True — ทุกค่าที่เก็บเป็น UTC
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def retry_after(session, kind: str, key: str, limit: Limit, now: datetime) -> int | None:
    """จำนวนวินาทีที่ต้องรอ ถ้าครบเพดานแล้ว · None ถ้ายังทำได้"""
    since = now - limit.window
    in_window = (AuthAttempt.kind == kind, AuthAttempt.key == key, AuthAttempt.created_at > since)
    count = session.scalar(select(func.count()).select_from(AuthAttempt).where(*in_window))
    if count < limit.max_attempts:
        return None
    # ต้องรอจนแถวที่เก่าที่สุดที่ยังทำให้ครบเพดานหลุดออกจากหน้าต่าง
    oldest = session.scalars(
        select(AuthAttempt.created_at)
        .where(*in_window)
        .order_by(AuthAttempt.created_at.desc())
        .offset(limit.max_attempts - 1)
        .limit(1)
    ).one()
    wait = (_aware(oldest) + limit.window - now).total_seconds()
    return max(1, math.ceil(wait))


def record(session, kind: str, keys, now: datetime, prune_before: datetime):
    """บันทึก 1 แถวต่อ key และลบแถวที่เก่ากว่าหน้าต่างที่ยาวที่สุดทิ้ง (ไม่ commit — ผู้เรียก commit เอง)"""
    session.execute(delete(AuthAttempt).where(AuthAttempt.created_at <= prune_before))
    for key in keys:
        session.add(AuthAttempt(kind=kind, key=key, created_at=now))


def clear(session, kind: str, key: str):
    session.execute(delete(AuthAttempt).where(AuthAttempt.kind == kind, AuthAttempt.key == key))
