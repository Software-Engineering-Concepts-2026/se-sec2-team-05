"""Property-based test ด้วย Hypothesis (Lab 9)

เดิมทดสอบ edit token ต่อโน้ต (`tokens.py`) ซึ่งเลิกใช้แล้ว (ADR-013) จึงเปลี่ยนมาทดสอบ token ตัวที่ยังใช้อยู่
คือ client token ของการอัปโหลดตรงเข้า Vercel Blob (`storage.generate_client_token`, ADR-012) แบบ AAA เหมือนเดิม
"""

import base64
import hashlib
import hmac
import json

from hypothesis import assume, given, settings, strategies as st

from storage import generate_client_token

store_ids = st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1, max_size=20)
secrets = st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=1, max_size=40)
pathnames = st.text(alphabet="abcdef0123456789/._", min_size=1, max_size=80)
sizes = st.integers(min_value=1, max_value=10 * 1024 * 1024)
moments = st.integers(min_value=0, max_value=2**45)


def read_token(token):
    store_id, secured = token[len("vercel_blob_client_"):].split("_", 1)
    signature, payload = base64.b64decode(secured).decode().split(".", 1)
    return store_id, signature, payload, json.loads(base64.b64decode(payload))


@settings(max_examples=100)
@given(store_id=store_ids, secret=secrets, pathname=pathnames, size=sizes, valid_until=moments)
def test_client_token_carries_its_limits_and_a_valid_signature(store_id, secret, pathname, size, valid_until):
    # Arrange
    read_write_token = f"vercel_blob_rw_{store_id}_{secret}"

    # If this fails, Hypothesis shrinks to the shortest store id, path and size that break it.

    # Act
    token = generate_client_token(
        read_write_token, pathname=pathname, maximum_size_in_bytes=size,
        allowed_content_types=["application/pdf"], valid_until_ms=valid_until,
    )

    # Assert
    got_store, signature, payload, decoded = read_token(token)
    assert got_store == store_id
    assert hmac.compare_digest(
        signature, hmac.new(read_write_token.encode(), payload.encode(), hashlib.sha256).hexdigest()
    )
    assert decoded["pathname"] == pathname
    assert decoded["maximumSizeInBytes"] == size
    assert decoded["validUntil"] == valid_until
    assert decoded["allowOverwrite"] is False


@settings(max_examples=100)
@given(store_id=store_ids, secret=secrets, other_secret=secrets, pathname=pathnames)
def test_client_token_signed_with_another_key_does_not_verify(store_id, secret, other_secret, pathname):
    # Arrange
    assume(secret != other_secret)
    real_key = f"vercel_blob_rw_{store_id}_{secret}"
    other_key = f"vercel_blob_rw_{store_id}_{other_secret}"

    # Hypothesis shrinks a failing pair to the shortest distinct pair of secrets it can find.

    # Act
    token = generate_client_token(
        other_key, pathname=pathname, maximum_size_in_bytes=1,
        allowed_content_types=["image/png"], valid_until_ms=0,
    )

    # Assert
    _, signature, payload, _ = read_token(token)
    assert signature != hmac.new(real_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
