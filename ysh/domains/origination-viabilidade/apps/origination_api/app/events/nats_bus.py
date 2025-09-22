import contextlib
import json
from typing import AsyncIterator

import nats

from app.core.config import settings

SUBJECTS = {
    "lead_captured": "ysh.origination.lead.captured.v1",
    "lead_scored": "ysh.origination.lead.scored.v1",
    "profile_detected": "ysh.origination.consumption.profile.detected.v1",
    "sized": "ysh.origination.system.sized.v1",
    "reco_bundle": "ysh.origination.recommendation.bundle.created.v1",
    "modality_selected": "ysh.origination.generation.modality.selected.v1",
}

nc: nats.NATS | None = None


@contextlib.asynccontextmanager
async def nats_lifespan(app) -> AsyncIterator[None]:  # type: ignore[override]
    global nc
    nc = await nats.connect(settings.nats_url)
    try:
        yield
    finally:
        if nc:
            await nc.drain()


async def publish(subject: str, payload: dict) -> None:
    if not nc:
        return
    await nc.publish(subject, json.dumps(payload).encode())
