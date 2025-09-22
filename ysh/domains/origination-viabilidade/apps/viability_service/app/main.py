from fastapi import FastAPI
from app.events.nats_bus import nats_lifespan, publish_completed
from app.services.viability import ViabilityIn, compute_viability
from app.services.economics import EconomicsIn, evaluate
from datetime import datetime, timezone

app = FastAPI(title="YSH Viability Service", version="0.1.0")
app.router.lifespan_context = nats_lifespan

@app.post("/tools/viability.compute")
async def viability_compute(inp: ViabilityIn):
    out = compute_viability(inp)
    return out.model_dump()

@app.post("/tools/economics.evaluate")
async def economics_evaluate(inp: EconomicsIn):
    out = evaluate(inp)
    return out.model_dump()

# Endpoint auxiliar: fecha o ciclo e publica viability.completed.v1
@app.post("/tools/viability.complete")
async def viability_complete(lead_id: str, kwh_year: float, pr: float):
    await publish_completed({
        "lead_id": lead_id, "ts": datetime.now(timezone.utc).isoformat(),
        "kwh_year": kwh_year, "pr": pr, "economics": {}
    })
    return {"ok": True}
