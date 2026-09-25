"""User & Auth Service — US-05 (#5) สมัครสมาชิก และ US-06 (#6) เข้า/ออกจากระบบ

Endpoint:
    GET  /health          health check (รูปแบบเดียวกับ service อื่น)
    POST /auth/register   สมัครด้วยอีเมลมหาวิทยาลัย
    POST /auth/login      รับ JWT อายุ 8 ชั่วโมง (ไม่มี refresh token)
    POST /auth/logout     เพิกถอน session ของ token ที่ส่งมาทันที
    GET  /auth/me         ข้อมูลบัญชีของ token ที่ส่งมา — service อื่นใช้ตรวจ token ผ่านตัวนี้

การออกแบบ token + session และเหตุผลที่เลือก scrypt อยู่ใน ADR-005
service นี้ยังไม่ได้ถูกเรียกจาก notes-service — การบังคับ login ตอนอัปโหลดเป็นงานรอบถัดไป
"""

import os
from datetime import timedelta

from flask import Flask, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from auth_models import AuthSession, User, build_session_factory, utcnow
from auth_tokens import (
    DEFAULT_TTL,
    check_secret,
    decode_access_token,
    encode_access_token,
    new_session_id,
)
from credentials import (
    MAX_PASSWORD_LENGTH,
    PASSWORD_HASH_METHOD,
    hash_password,
    normalize_email,
    parse_allowed_domains,
    validate_registration,
    verify_password,
)

DEFAULT_DATABASE_URL = "sqlite:///auth.db"

# body ของ endpoint ใน service นี้มีแค่อีเมล รหัสผ่าน และชื่อ — 16 KB เหลือเฟือ
# ตัดคำขอที่ใหญ่กว่านี้ทิ้งตั้งแต่ชั้น Werkzeug
MAX_REQUEST_BYTES = 16 * 1024

# ข้อความเดียวกันทุกกรณีที่ login ไม่ผ่าน ไม่บอกว่าผิดที่อีเมลหรือรหัสผ่าน (AC ข้อ 3 ของ #6)
INVALID_CREDENTIALS_MESSAGE = "อีเมลหรือรหัสผ่านไม่ถูกต้อง"


def _ttl_from_env() -> timedelta:
    raw = os.environ.get("AUTH_TOKEN_TTL_HOURS")
    if not raw:
        return DEFAULT_TTL
    try:
        hours = int(raw)
    except ValueError:
        raise RuntimeError("AUTH_TOKEN_TTL_HOURS ต้องเป็นจำนวนเต็ม") from None
    if hours < 1:
        raise RuntimeError("AUTH_TOKEN_TTL_HOURS ต้องมีค่าอย่างน้อย 1")
    return timedelta(hours=hours)


def create_app(
    database_url: str | None = None,
    secret: str | None = None,
    allowed_domains: str | None = None,
    token_ttl: timedelta | None = None,
    password_hash_method: str = PASSWORD_HASH_METHOD,
) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES

    session_factory = build_session_factory(
        database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    )
    jwt_secret = check_secret(secret or os.environ.get("AUTH_JWT_SECRET"))
    domains = parse_allowed_domains(
        allowed_domains if allowed_domains is not None else os.environ.get("ALLOWED_EMAIL_DOMAINS")
    )
    ttl = token_ttl if token_ttl is not None else _ttl_from_env()

    # login ด้วยอีเมลที่ไม่มีในระบบก็ต้องเสียเวลา hash เท่ากับอีเมลที่มีอยู่จริง
    # ไม่งั้นแค่จับเวลาตอบก็รู้แล้วว่าอีเมลไหนสมัครไว้ ซึ่งเท่ากับทำ AC ข้อ 3 ของ #6 หลุด
    dummy_hash = hash_password(os.urandom(16).hex(), method=password_hash_method)

    def payload():
        """รับได้ทั้ง JSON และ form — frontend ใช้ JSON ส่วน `curl -d` ส่ง form"""
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else request.form

    def unauthorized():
        return jsonify(error="unauthorized"), 401, {"WWW-Authenticate": "Bearer"}

    def authenticate(session):
        """คืน (auth_session, user) ของ Bearer token ใน request หรือ None ถ้าใช้ไม่ได้

        token ต้องผ่านทั้งสองชั้น: ลายเซ็น/เวลาหมดอายุของ JWT และ session ในฐานข้อมูล
        ที่ยังไม่ถูกเพิกถอน ชั้นที่สองคือสิ่งที่ทำให้ logout มีผลทันที
        """
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "bearer":
            return None
        claims = decode_access_token(jwt_secret, token.strip())
        if claims is None:
            return None
        auth_session = session.get(AuthSession, claims["jti"])
        if auth_session is None or auth_session.revoked_at is not None:
            return None
        if str(auth_session.user_id) != claims["sub"]:
            return None
        user = session.get(User, auth_session.user_id)
        if user is None:
            return None
        return auth_session, user

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="auth-service", time=utcnow().isoformat())

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify(error="request_too_large"), 413

    @app.post("/auth/register")
    def register():
        cleaned, errors = validate_registration(payload(), domains)
        if errors:
            return jsonify(error="validation_failed", fields=errors), 400

        # AC ข้อ 2 ของ #5 บังคับให้บอกว่าอีเมลซ้ำ จึงเลี่ยงไม่ได้ที่หน้าสมัครจะเผยว่าอีเมลนี้มีบัญชีแล้ว
        # (ข้อจำกัดนี้บันทึกไว้ใน ADR-005) ส่วน login ยังกันไว้ตาม AC ข้อ 3 ของ #6
        email_taken = (
            jsonify(error="email_taken", fields={"email": "อีเมลนี้สมัครสมาชิกไว้แล้ว"}),
            409,
        )
        with session_factory() as session:
            if session.scalar(select(User.id).where(User.email == cleaned["email"])):
                return email_taken

            user = User(
                email=cleaned["email"],
                display_name=cleaned["display_name"],
                password_hash=hash_password(cleaned["password"], method=password_hash_method),
            )
            session.add(user)
            try:
                session.commit()
            except IntegrityError:
                # สมัครพร้อมกันสองคำขอด้วยอีเมลเดียวกัน — ตัวที่สองชน unique constraint
                session.rollback()
                return email_taken
            return jsonify(user.to_dict()), 201

    @app.post("/auth/login")
    def login():
        data = payload()
        email = normalize_email(data.get("email"))
        password = data.get("password")

        # ช่องที่ว่างบอกได้ว่าว่างตรงไหน เพราะไม่ได้เผยอะไรเกี่ยวกับบัญชีเลย
        missing = {}
        if not email:
            missing["email"] = "จำเป็นต้องกรอก"
        if not isinstance(password, str) or password == "":
            missing["password"] = "จำเป็นต้องกรอก"
        if missing:
            return jsonify(error="validation_failed", fields=missing), 400

        invalid = jsonify(error="invalid_credentials", message=INVALID_CREDENTIALS_MESSAGE), 401
        # รหัสผ่านที่ยาวกว่าเพดานไม่มีทางถูกอยู่แล้ว เพราะตอนสมัครไม่ยอมรับ
        if len(password) > MAX_PASSWORD_LENGTH:
            return invalid

        with session_factory() as session:
            user = session.scalar(select(User).where(User.email == email))
            password_ok = verify_password(user.password_hash if user else dummy_hash, password)
            if user is None or not password_ok:
                return invalid

            issued_at = utcnow()
            session_id = new_session_id()
            token, expires_at = encode_access_token(jwt_secret, user.id, session_id, issued_at, ttl)
            session.add(
                AuthSession(
                    id=session_id, user_id=user.id, created_at=issued_at, expires_at=expires_at
                )
            )
            session.commit()
            return jsonify(
                access_token=token,
                token_type="Bearer",
                expires_at=expires_at.isoformat(),
                user=user.to_dict(),
            )

    @app.post("/auth/logout")
    def logout():
        with session_factory() as session:
            found = authenticate(session)
            if found is None:
                return unauthorized()
            auth_session, _user = found
            auth_session.revoked_at = utcnow()
            session.commit()
        return "", 204

    @app.get("/auth/me")
    def me():
        with session_factory() as session:
            found = authenticate(session)
            if found is None:
                return unauthorized()
            _auth_session, user = found
            return jsonify(user.to_dict())

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
