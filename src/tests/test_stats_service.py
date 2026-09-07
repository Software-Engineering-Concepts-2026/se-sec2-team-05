"""Unit tests สำหรับ Stats Service (ผู้เขียน: อติชาติ)

ครอบคลุม contract ของ endpoint ที่ประกาศไว้ใน docs/architecture/c4-container.md
คือ /health และ /stats — ยังไม่แตะฐานข้อมูลเพราะ service ยังใช้ mock data อยู่
"""

from datetime import datetime

import pytest


@pytest.fixture
def client(stats_client):
    # ตัว app ถูกโหลดใน conftest.py เพราะทุก service มี app.py ชื่อซ้ำกัน
    return stats_client


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["service"] == "stats-service"


def test_health_time_is_valid_iso_timestamp(client):
    body = client.get("/health").get_json()

    # ต้อง parse กลับเป็น datetime ได้ และต้องมี timezone ติดมาด้วย (UTC)
    parsed = datetime.fromisoformat(body["time"])
    assert parsed.tzinfo is not None


def test_stats_returns_expected_shape(client):
    response = client.get("/stats")

    assert response.status_code == 200
    body = response.get_json()
    assert set(body) == {"total_downloads", "total_notes", "top_contributors"}
    assert isinstance(body["total_downloads"], int)
    assert isinstance(body["total_notes"], int)
    assert isinstance(body["top_contributors"], list)


def test_unknown_route_returns_404(client):
    assert client.get("/does-not-exist").status_code == 404
