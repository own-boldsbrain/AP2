from fastapi import FastAPI

from app.core.config import settings
from app.core.db import init_db
from app.events.nats_bus import nats_lifespan
from app.routers import leads

app = FastAPI(title=settings.app_name, version="0.1.0", openapi_url="/openapi.json")
app.router.lifespan_context = nats_lifespan


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


app.include_router(leads.router, prefix=settings.api_prefix, tags=["leads"])


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
