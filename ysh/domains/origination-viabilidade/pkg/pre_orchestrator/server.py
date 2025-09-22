"""Servidor MCP para o PREOrchestratorAgent.

Este módulo implementa um servidor FastAPI que expõe as skills do
PREOrchestratorAgent através do protocolo MCP.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

from pre_orchestrator.agent import PREOrchestratorAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pre_orchestrator_server")

# Inicializar FastAPI
app = FastAPI(
    title="PRE Orchestrator Agent Server",
    description="Servidor MCP para o agente orquestrador de PRE",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar agente
agent = PREOrchestratorAgent()


@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde do servidor."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/mcp/pre_orchestrator")
async def handle_mcp_request(request: Request):
    """Endpoint principal para receber requisições MCP."""
    try:
        body = await request.json()
        logger.info(f"Recebida requisição MCP: {body}")
        
        # Extrair informações da requisição
        skill_id = body.get("skill", {}).get("id", "")
        parameters = body.get("skill", {}).get("parameters", {})
        
        # Executar skill correspondente
        result = await execute_skill(skill_id, parameters)
        
        # Montar resposta MCP
        response = {
            "status": "success",
            "skill": {
                "id": skill_id,
                "result": result
            }
        }
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Erro ao processar requisição MCP: {str(e)}")
        error_id = str(uuid4())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": {
                    "id": error_id,
                    "message": str(e)
                }
            }
        )


async def execute_skill(skill_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa a skill do agente com base no ID e parâmetros.
    
    Args:
        skill_id: ID da skill a ser executada.
        parameters: Parâmetros para a skill.
        
    Returns:
        Resultado da execução da skill.
    """
    if skill_id == "create_update_lead":
        return await agent.create_update_lead(parameters)
    
    elif skill_id == "classify_consumer":
        lead_id = parameters.get("lead_id")
        classification_data = {
            k: v for k, v in parameters.items() if k != "lead_id"
        }
        return await agent.classify_consumer(lead_id, classification_data)
    
    elif skill_id == "select_modality":
        lead_id = parameters.get("lead_id")
        modality_data = {
            k: v for k, v in parameters.items() if k != "lead_id"
        }
        return await agent.select_modality(lead_id, modality_data)
    
    elif skill_id == "calculate_viability":
        return await agent.calculate_viability(parameters)
    
    elif skill_id == "evaluate_economics":
        return await agent.evaluate_economics(parameters)
    
    elif skill_id == "size_system":
        return agent.size_system(parameters)
    
    elif skill_id == "generate_recommendations":
        lead_id = parameters.get("lead_id")
        reco_data = {
            k: v for k, v in parameters.items() if k != "lead_id"
        }
        return await agent.generate_recommendations(lead_id, reco_data)
    
    elif skill_id == "emit_event":
        event_type = parameters.get("event_type")
        payload = parameters.get("payload", {})
        await agent.emit_event(event_type, payload)
        return {"event_emitted": True, "event_type": event_type}
    
    elif skill_id == "orchestrate_pre_process":
        return await agent.orchestrate_pre_process(parameters)
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Skill não reconhecida: {skill_id}"
        )


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização do servidor."""
    # Conectar ao servidor NATS
    try:
        await agent.connect_nats()
    except Exception as e:
        logger.warning(f"Não foi possível conectar ao servidor NATS: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento do servidor."""
    # Fechar conexões
    await agent.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)