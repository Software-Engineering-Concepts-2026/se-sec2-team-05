from __future__ import annotations

import os

import requests


class IdentityUnavailable(Exception):
    pass


class HttpIdentity:
    def __init__(self, base_url: str, timeout: float = 3.0):
        self.me_url = base_url.rstrip("/") + "/auth/me"
        self.timeout = timeout

    def __call__(self, authorization: str | None):
        if not authorization:
            return None

        try:
            response = requests.get(
                self.me_url,
                headers={"Authorization": authorization},
                timeout=self.timeout,
            )
        except (requests.RequestException, ValueError) as exc:
            raise IdentityUnavailable from exc

        if response.status_code == 401:
            return None

        if response.status_code != 200:
            raise IdentityUnavailable

        try:
            body = response.json()
            return {
                "id": int(body["id"]),
                "display_name": str(body["display_name"]),
            }
        except (KeyError, TypeError, ValueError) as exc:
            raise IdentityUnavailable from exc


def identity_from_env() -> HttpIdentity:
    return HttpIdentity(
        os.getenv(
            "AUTH_SERVICE_URL",
            "http://localhost:5002",
        )
    )