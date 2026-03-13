from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.exceptions.ai import AiServiceError
from src.shared.exceptions.base import DomainError

logger = logging.getLogger("insightcopilot.errors")


def register_error_handlers(app: FastAPI) -> None:
    """Registra handlers globales para errores no capturados en los endpoints."""

    @app.exception_handler(AiServiceError)
    async def ai_service_error_handler(
        _request: Request, exc: AiServiceError
    ) -> JSONResponse:
        logger.warning("AiServiceError [%s/%s]: %s", exc.service, exc.code, exc.message)
        return JSONResponse(status_code=exc.status_code, content=exc.to_response())

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        logger.warning("DomainError: %s", exc.message)
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error no manejado: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor."},
        )
