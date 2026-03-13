from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.infrastructure.logging.setup import setup_logging
from src.presentation.api.error_handlers import register_error_handlers
from src.presentation.api.middleware import RequestLoggingMiddleware
from src.presentation.api.routes.datasets import router as datasets_router
from src.presentation.api.routes.documents import router as documents_router
from src.presentation.api.routes.health import router as health_router


def create_app() -> FastAPI:
    setup_logging()

    import logging

    from src.shared.config.settings import settings

    logger = logging.getLogger(__name__)
    logger.info("OPENAI_API_KEY configurada: %s", bool(settings.openai_api_key))
    logger.info("LLM_MODE activo: %s", settings.llm_mode)

    app = FastAPI(
        title="InsightCopilot AI",
        version="1.0.0",
        description="Plataforma analítica con IA para exploración de datos.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_error_handlers(app)

    app.include_router(health_router)
    app.include_router(datasets_router)
    app.include_router(documents_router)
    return app


app = create_app()
