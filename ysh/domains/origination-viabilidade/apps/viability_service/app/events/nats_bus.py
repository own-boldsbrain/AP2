"""Small helper module managing the NATS connection lifecycle."""

from __future__ import annotations

import contextlib
import json
import os
from typing import AsyncIterator

import nats

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SUBJECT_REQUESTED = "ysh.origination.viability.requested.v1"
SUBJECT_COMPLETED = "ysh.origination.viability.completed.v1"

nc: nats.NATS | None = None


@contextlib.asynccontextmanager
async def nats_lifespan(app) -> AsyncIterator[None]:
    """Connect to NATS on startup and drain the connection on shutdown."""

    global nc
    nc = await nats.connect(NATS_URL)

    async def _log_request(msg):
        try:
            payload = json.loads(msg.data.decode())
            app.logger.info("viability.requested", extra={"payload": payload}) if hasattr(app, "logger") else None
        except Exception:  # pragma: no cover - defensive logging only
            pass

    try:
        await nc.subscribe(SUBJECT_REQUESTED, cb=_log_request)
        yield
    finally:
        if nc and not nc.is_closed:
            await nc.drain()
            nc = None


async def publish_completed(payload: dict) -> bool:
    """Publish ``viability.completed`` events when the service finishes a job."""

    if not nc or nc.is_closed:
        return False

    try:
        await nc.publish(SUBJECT_COMPLETED, json.dumps(payload).encode("utf-8"))
        return True
    except Exception:  # pragma: no cover - network errors are logged by nats-py
        return False
