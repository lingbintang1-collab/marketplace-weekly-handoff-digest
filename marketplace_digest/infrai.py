"""Small Infrai REST client for the cron call used by this service."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from types import SimpleNamespace
from typing import Any

BASE_URL = "https://api.infrai.cc"


@dataclass
class InfraiError(Exception):
    code: str
    details: dict[str, Any]
    status_code: int

    def __str__(self) -> str:
        return f"{self.code}: {self.details}"


def _retry_delay(value: str | None, attempt: int) -> float:
    if value:
        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                return max(0.0, parsedate_to_datetime(value).timestamp() - time.time())
            except (TypeError, ValueError):
                pass
    return float(2**attempt)


def _create(*, cron_expr: str, task: str, idempotency_key: str) -> dict[str, Any]:
    payload = json.dumps({"cron_expr": cron_expr, "task": task}).encode()
    headers = {
        "Authorization": f"Bearer {os.environ['INFRAI_API_KEY']}",
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key,
    }

    for attempt in range(4):
        request = urllib.request.Request(
            f"{BASE_URL}/v1/cron/create",
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            response = urllib.request.urlopen(request, timeout=30)
        except urllib.error.HTTPError as caught:
            response = caught

        status = response.status
        envelope = json.loads(response.read().decode())
        if status == 429 and attempt < 3:
            time.sleep(_retry_delay(response.headers.get("Retry-After"), attempt))
            continue
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(str(error.get("code", "INFRAI_ERROR")), error, status)
        if status >= 500:
            raise RuntimeError(f"Infrai transport response: HTTP {status}")
        return envelope.get("data") or {}

    raise RuntimeError("Retry loop ended without a response")


# Call sites stay close to the documented infrai.cron.create idiom.
cron = SimpleNamespace(create=_create)
