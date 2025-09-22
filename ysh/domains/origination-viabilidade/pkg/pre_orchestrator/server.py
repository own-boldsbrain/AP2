"""FastAPI surface exposing PRE orchestrator skills over MCP."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pkg.pre_orchestrator.agent import PREOrchestratorAgent, TIER_FACTORS

logger = logging.getLogger("pre_orchestrator.server")

app = FastAPI(title="PRE Orchestrator Agent Server", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

agent = PREOrchestratorAgent()


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/mcp/pre_orchestrator")
async def handle_mcp_request(request: Request) -> JSONResponse:
    try:
        body = await request.json()
        logger.info("Received MCP request", extra={"body": body})
        skill_id = body.get("skill", {}).get("id")
        parameters = body.get("skill", {}).get("parameters", {})
        result = await _execute_skill(skill_id, parameters)
        return JSONResponse({"status": "success", "skill": {"id": skill_id, "result": result}})
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Error processing MCP request")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": {"id": str(uuid4()), "message": str(exc)},
            },
        )


async def _execute_skill(skill_id: str | None, parameters: Dict[str, Any]) -> Dict[str, Any]:
    if not skill_id:
        raise HTTPException(status_code=400, detail="Skill ID ausente")

    if skill_id == "create_update_lead":
        return await agent.create_update_lead(parameters)
    if skill_id == "classify_consumer":
        lead_id = parameters.get("lead_id")
        if not lead_id:
            raise HTTPException(status_code=400, detail="lead_id obrigatório")
        payload = {k: v for k, v in parameters.items() if k != "lead_id"}
        return await agent.classify_consumer(lead_id, payload)
    if skill_id == "select_modality":
        lead_id = parameters.get("lead_id")
        if not lead_id:
            raise HTTPException(status_code=400, detail="lead_id obrigatório")
        payload = {k: v for k, v in parameters.items() if k != "lead_id"}
        return await agent.select_modality(lead_id, payload)
    if skill_id == "calculate_viability":
        return await agent.calculate_viability(parameters)
    if skill_id == "evaluate_economics":
        return await agent.evaluate_economics(parameters)
    if skill_id == "size_system":
        tier_factor = parameters.get("tier_factor")
        if tier_factor is None:
            tier_code = parameters.get("tier_code", "T115")
            tier_factor = TIER_FACTORS.get(tier_code, TIER_FACTORS["T115"])
        return agent.size_system(
            annual_consumption_kwh=parameters.get("annual_consumption_kwh", 6000.0),
            kwh_per_kwp_year=parameters.get("kwh_per_kwp_year", 1200.0),
            tier_factor=tier_factor,
        )
    if skill_id == "generate_recommendations":
        lead_id = parameters.get("lead_id")
        if not lead_id:
            raise HTTPException(status_code=400, detail="lead_id obrigatório")
        payload = {k: v for k, v in parameters.items() if k != "lead_id"}
        return await agent.generate_recommendations(lead_id, payload)
    if skill_id == "emit_event":
        suffix = parameters.get("event_type")
        payload = parameters.get("payload", {})
        if not suffix:
            raise HTTPException(status_code=400, detail="event_type obrigatório")
        await agent.emit_event(suffix, payload)
        return {"event_emitted": True}
    if skill_id == "orchestrate_pre_process":
        return await agent.orchestrate_pre_process(parameters)

    raise HTTPException(status_code=400, detail=f"Skill não reconhecida: {skill_id}")


@app.on_event("startup")
async def on_startup() -> None:
    try:
        await agent.connect_nats()
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("NATS connection failed during startup: %s", exc)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await agent.close()


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "pkg.pre_orchestrator.server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
