"""Unit tests ของ JWT access token — US-06 (#6)

ตรวจเฉพาะชั้นลายเซ็นกับเวลาหมดอายุ ส่วนการเพิกถอนผ่าน session ตรวจใน test_auth_api.py
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from auth_tokens import (
    ALGORITHM,
    DEFAULT_TTL,
    ISSUER,
    check_secret,
    decode_access_token,
    encode_access_token,
    new_session_id,
)

SECRET = "unit-test-secret-that-is-at-least-32-bytes"


def now():
    return datetime.now(timezone.utc)


def test_default_ttl_is_eight_hours():
    assert DEFAULT_TTL == timedelta(hours=8)


def test_round_trip_keeps_user_and_session_claims():
    session_id = new_session_id()

    token, expires_at = encode_access_token(SECRET, 42, session_id, now(), DEFAULT_TTL)
    claims = decode_access_token(SECRET, token)

    assert claims["sub"] == "42"
    assert claims["jti"] == session_id
    assert claims["iss"] == ISSUER
    assert claims["exp"] == int(expires_at.timestamp())


def test_expired_token_is_rejected():
    issued_at = now() - timedelta(hours=9)

    token, _ = encode_access_token(SECRET, 1, new_session_id(), issued_at, DEFAULT_TTL)

    assert decode_access_token(SECRET, token) is None


def test_token_signed_with_another_secret_is_rejected():
    token, _ = encode_access_token(
        "another-secret-that-is-also-32-bytes-long", 1, new_session_id(), now(), DEFAULT_TTL
    )

    assert decode_access_token(SECRET, token) is None


def test_tampered_payload_is_rejected():
    token, _ = encode_access_token(SECRET, 1, new_session_id(), now(), DEFAULT_TTL)
    header, payload, signature = token.split(".")
    # เปลี่ยน payload เป็นของ user อื่นแต่ใช้ลายเซ็นเดิม
    forged_payload = jwt.encode({"sub": "2"}, SECRET, algorithm=ALGORITHM).split(".")[1]

    assert decode_access_token(SECRET, f"{header}.{forged_payload}.{signature}") is None


def test_unsigned_alg_none_token_is_rejected():
    claims = {
        "sub": "1",
        "jti": new_session_id(),
        "iat": now(),
        "exp": now() + DEFAULT_TTL,
        "iss": ISSUER,
    }
    unsigned = jwt.encode(claims, key=None, algorithm="none")

    assert decode_access_token(SECRET, unsigned) is None


def test_token_missing_session_id_is_rejected():
    # ไม่มี jti = ผูกกับ session ไม่ได้ = เพิกถอนไม่ได้ ต้องไม่ผ่าน
    token = jwt.encode(
        {"sub": "1", "iat": now(), "exp": now() + DEFAULT_TTL, "iss": ISSUER},
        SECRET,
        algorithm=ALGORITHM,
    )

    assert decode_access_token(SECRET, token) is None


@pytest.mark.parametrize("token", [None, "", "not-a-jwt"])
def test_garbage_is_rejected_without_raising(token):
    assert decode_access_token(SECRET, token) is None


@pytest.mark.parametrize("secret", [None, "", "x" * 31])
def test_missing_or_short_secret_refuses_to_start(secret):
    with pytest.raises(RuntimeError):
        check_secret(secret)


def test_session_ids_are_unique():
    assert len({new_session_id() for _ in range(1000)}) == 1000
