"""Funções para comunicação via NATS."""

import contextlib
import json
import os
from typing import AsyncIterator

import nats

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SUBJECT_REQUESTED = "ysh.origination.viability.requested.v1"
SUBJECT_COMPLETED = "ysh.origination.viability.completed.v1"
nc = None


@contextlib.asynccontextmanager
async def nats_lifespan(app) -> AsyncIterator[None]:
    """Gerencia o ciclo de vida da conexão NATS."""
    global nc
    nc = await nats.connect(NATS_URL)
    try:
        # opcional: subscribe para processar pedidos via eventos
        async def handler(msg):
            try:
                payload = json.loads(msg.data.decode())
                print(f"Recebido evento {SUBJECT_REQUESTED}: {payload}")
                # aqui poderíamos acionar compute e publish completed
            except Exception as e:
                print(f"Erro no handler de viabilidade: {e}")

        await nc.subscribe(SUBJECT_REQUESTED, cb=handler)
        yield
    finally:
        if nc:
            await nc.drain()


async def publish_completed(payload: dict):
    """Publica um evento de viabilidade concluída."""
    if nc:
        try:
            await nc.publish(SUBJECT_COMPLETED, json.dumps(payload).encode())
            print(f"Publicado evento {SUBJECT_COMPLETED}: {payload}")
            return True
        except Exception as e:
            print(f"Erro ao publicar evento {SUBJECT_COMPLETED}: {e}")
            return False
    return False            print(f"Erro ao publicar evento {SUBJECT_COMPLETED}: {e}")
            return False
    return False
