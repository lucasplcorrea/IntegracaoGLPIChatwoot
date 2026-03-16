import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

# Import models so SQLAlchemy registers them before create_all
import app.models.models  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("chatwoot_history")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Middleware para agrupamento e histórico de conversas por contato no Chatwoot.",
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Auto-create tables on startup (idempotent via CREATE TABLE IF NOT EXISTS logic in ORM)
    Base.metadata.create_all(bind=engine)

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} → {response.status_code}")
        return response

    @app.get("/healthz", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
