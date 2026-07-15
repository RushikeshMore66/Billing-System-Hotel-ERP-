"""
NiralayOS FastAPI application entry point.

This module creates and configures the FastAPI application instance.
It is the ONLY place where middleware is registered and routers are mounted.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.core.settings import get_settings
from app.core.lifespan import lifespan
from app.api.router import api_router
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.cors import build_cors_kwargs
from app.schemas.base import ErrorResponse, ErrorDetail

_cfg = get_settings()

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title=_cfg.APP_NAME,
    description="Production-grade Hospitality ERP Platform",
    version=_cfg.APP_VERSION,
    docs_url="/docs" if not _cfg.is_production else None,
    redoc_url="/redoc" if not _cfg.is_production else None,
    openapi_url="/openapi.json" if not _cfg.is_production else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware (order matters — outermost first)
# ---------------------------------------------------------------------------
# 1. CORS — must be first so preflight requests are handled correctly
app.add_middleware(CORSMiddleware, **build_cors_kwargs())

# 2. Request ID — must run before logging so log lines carry the ID
app.add_middleware(RequestIDMiddleware)

# 3. Access logging
app.add_middleware(LoggingMiddleware)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic validation errors into the standard error envelope."""
    details = [
        ErrorDetail(
            field=" → ".join(str(loc) for loc in err["loc"]),
            message=err["msg"],
            code=err["type"],
        )
        for err in exc.errors()
    ]
    error = ErrorResponse.of(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details=details,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error.model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler — prevents stack traces leaking to clients in production."""
    import logging
    logging.getLogger(__name__).exception(
        "Unhandled exception",
        extra={"request_id": getattr(request.state, "request_id", None)},
    )
    if _cfg.is_production:
        message = "An unexpected error occurred. Please contact support."
    else:
        message = str(exc)

    error = ErrorResponse.of(
        error_code="INTERNAL_SERVER_ERROR",
        message=message,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump(mode="json"),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get(
    "/",
    include_in_schema=False,
)
async def root():
    return {"app": _cfg.APP_NAME, "version": _cfg.APP_VERSION, "docs": "/docs"}


@app.get(
    "/ping",
    include_in_schema=False,
)
async def ping():
    """Minimal liveness endpoint for load balancers."""
    return {"pong": True}


# Mount all API routers
app.include_router(api_router)
