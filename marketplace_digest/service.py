"""Application entry point for scheduling and delivering the weekly digest."""

from __future__ import annotations

import hashlib
import os

from fastapi import FastAPI, HTTPException

from . import infrai
from .infrai import InfraiError
from .models import DigestRequest, DigestResult, ScheduleRequest, ScheduleResult
from .receipt_sender import build_digest, send_digest

app = FastAPI(title="Marketplace weekly digest")


@app.post("/schedule", response_model=ScheduleResult)
def schedule(request: ScheduleRequest) -> ScheduleResult:
    task = f"{request.public_base_url.rstrip('/')}/digest/run"
    key_source = f"marketplace-weekly-digest:{request.cron_expr}:{task}"
    idempotency_key = hashlib.sha256(key_source.encode()).hexdigest()
    try:
        data = infrai.cron.create(
            cron_expr=request.cron_expr,
            task=task,
            idempotency_key=idempotency_key,
        )
    except InfraiError as error:
        caller_status = error.status_code if 400 <= error.status_code < 500 else 502
        raise HTTPException(status_code=caller_status, detail=error.details) from error
    return ScheduleResult(job_id=str(data["job_id"]))


@app.post("/digest/run", response_model=DigestResult)
def run_digest(request: DigestRequest) -> DigestResult:
    result = build_digest(request)
    if result.sections and os.environ.get("DIGEST_SEND_EMAIL", "1") == "1":
        send_digest(result)
    return result
