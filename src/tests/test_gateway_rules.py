"""เทสต์ตาราง route ที่ gateway ต้องตรวจ login ก่อนส่งต่อ (ADR-014) — GW-07 ถึง GW-10

ตารางเดียวกันอยู่ 3 ที่: `gateway/cases.json` (ตัวตั้ง), `gateway/rules.js` (Vercel, เทสต์ด้วย node --test)
และ map ใน `web/nginx.conf` (docker compose) · ไฟล์นี้ตรวจฝั่ง nginx กับ vercel.json และตรวจว่าทุก route
ของ notes/stats/auth-service อยู่ใน cases.json เพิ่ม route ใหม่แล้วลืมตัดสินว่าต้อง login ไหมจะล้มที่นี่
"""

import json
import re
from pathlib import Path

import pytest

# app.py ของทั้งสาม service ชื่อซ้ำกัน conftest.py จึงโหลดไว้ใน sys.modules ด้วยชื่อเหล่านี้
import auth_service_app
import notes_service_app
import stats_service_app

REPO_ROOT = Path(__file__).resolve().parents[2]
NGINX_CONF = (REPO_ROOT / "web" / "nginx.conf").read_text(encoding="utf-8")
CASES = json.loads((REPO_ROOT / "gateway" / "cases.json").read_text(encoding="utf-8"))["cases"]
# route ที่ไม่ได้เปิดผ่าน gateway (nginx ไม่มี location ให้, vercel.json ไม่มี rewrite)
NOT_PUBLIC = {"/health"}


# note_token = แถวที่ส่ง header X-Note-Token เดิมมาด้วย ต้องได้ผลเหมือนไม่ส่ง (ADR-013) nginx ไม่อ่าน header นี้เลย
def _case_id(case):
    return f"{case['method']} {case['path']}" + (" +token" if case.get("note_token") else "")


def _nginx_map(variable):
    """คืน (default, [(regex, value), ...]) ของ map ที่ตั้งค่าตัวแปร `variable` ตามลำดับในไฟล์"""
    block = re.search(r"map\s+\"[^\"]+\"\s+\$" + variable + r"\s*\{(.*?)\n\}", NGINX_CONF, re.S)
    assert block, f"ไม่เจอ map ของ ${variable} ใน web/nginx.conf"
    default, rules = None, []
    for line in block.group(1).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        key, value = re.fullmatch(r"(\"[^\"]*\"|\S+)\s+(\S+);", line).groups()
        if key == "default":
            default = value
        else:
            assert key.startswith('"~'), f"map ใช้ได้แค่ regex: {key}"
            rules.append((re.compile(key[2:-1]), value))
    return default, rules


def _nginx_lookup(variable, key):
    # nginx เช็ค regex ใน map ตามลำดับที่เขียน ตัวแรกที่ match ชนะ
    default, rules = _nginx_map(variable)
    for pattern, value in rules:
        if pattern.search(key):
            return value
    return default


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_nginx_map_gives_the_same_answer_as_the_cases(case):
    """GW-07: map ทั้งสองชั้นใน nginx.conf ให้ rule และผลการตรวจตรงกับ cases.json ทุกแถว"""
    rule = _nginx_lookup("gateway_rule", f"{case['method']} {case['path']}")
    check = _nginx_lookup("gateway_check", rule)

    assert rule == case["rule"]
    assert check == ("login" if case["check"] == "login" else "skip")


def _location_blocks():
    return re.findall(r"\n    location\s+([^{]+?)\s*\{(.*?)\n    \}", NGINX_CONF, re.S)


def test_every_nginx_location_of_the_api_runs_the_check():
    """GW-08: ทุก location ที่ส่งต่อไป notes/stats-service ตรวจผ่าน auth_request และคำนวณ rule จาก request หลัก

    ถ้าลืม `set` ใน location ไหน subrequest จะไม่รู้ rule แล้วทุก route ใน location นั้นต้องถาม auth-service
    ถ้าลืม auth_request ทั้ง location ไม่ถูกตรวจเลย
    """
    api = [(where, body) for where, body in _location_blocks()
           if re.search(r"proxy_pass http://(notes|stats)-service", body)]
    assert len(api) == 6
    for where, body in api:
        if where.strip() == "= /stats":
            # ภาพรวมสถิติเปิดให้ทุกคน (open) ไม่ต้องเสีย subrequest
            assert "auth_request" not in body
            continue
        assert "auth_request /_gateway/auth;" in body, where
        assert "set $gateway_check_main $gateway_check;" in body, where

    auth_location = dict(_location_blocks())["= /_gateway/auth"]
    assert "internal;" in auth_location
    assert "if ($gateway_check_main = skip)" in auth_location
    assert "proxy_pass http://auth-service:5002/auth/me;" in auth_location
    assert "proxy_pass_request_body off;" in auth_location
    # ADR-013: header X-Note-Token เดิมต้องไม่มีผลกับการตรวจ
    assert "$http_x_note_token" not in NGINX_CONF


def _flask_routes():
    for name, module in (("notes", notes_service_app), ("stats", stats_service_app), ("auth", auth_service_app)):
        for rule in module.app.url_map.iter_rules():
            if rule.endpoint == "static" or rule.rule in NOT_PUBLIC:
                continue
            for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
                yield name, method, rule.rule


@pytest.mark.parametrize(("service", "method", "route"), list(_flask_routes()))
def test_every_service_route_is_in_the_gateway_table(service, method, route):
    """GW-09: ทุก route ของทุก service มีแถวใน cases.json — route ใหม่ต้องตัดสินก่อนว่าต้อง login ไหม"""
    pattern = re.sub(r"<int:\w+>", r"\\d+", route)
    pattern = re.sub(r"<\w+>", r"[^/]+", pattern)
    matching = [c for c in CASES if c["method"] == method and re.fullmatch(pattern, c["path"])]

    assert matching, f"{service}: {method} {route} ไม่มีใน gateway/cases.json"


def _vercel_matcher():
    config = json.loads((REPO_ROOT / "vercel.json").read_text(encoding="utf-8"))
    proxy = config["proxy"]
    assert (REPO_ROOT / proxy["entrypoint"]).is_file()
    # รองรับเฉพาะรูปแบบ "/x" และ "/x/:path*" ที่ไฟล์นี้ใช้
    return [re.compile(re.sub(r"/:\w+\*$", "/.*", m) + "$") for m in proxy["matcher"]]


def test_vercel_middleware_runs_on_every_protected_path_and_not_on_the_rest():
    """GW-10: proxy.matcher ใน vercel.json ครอบทุก path ที่ต้องตรวจ และไม่ไปเปลือง function กับหน้าเว็บ/auth"""
    matcher = _vercel_matcher()

    def runs_on(path):
        return any(m.match(path) for m in matcher)

    for case in CASES:
        if case["rule"] != "open":
            assert runs_on(case["path"]), _case_id(case)
    for path in ("/", "/index.html", "/upload.html", "/app.js", "/auth/login", "/auth/me", "/stats"):
        assert not runs_on(path), path
