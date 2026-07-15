"""
CORS configuration helper for NiralayOS.

Reads allowed origins from application settings and returns
a pre-configured CORSMiddleware instance ready to be added
to the FastAPI application.

Usage in main.py:
    from app.middleware.cors import build_cors_middleware
    app.add_middleware(*build_cors_middleware())
"""

from __future__ import annotations


from app.core.settings import get_settings


def build_cors_kwargs() -> dict:
    """
    Return keyword arguments for CORSMiddleware based on current settings.

    Separating the config from the middleware class makes unit testing
    the CORS settings trivial.
    """
    cfg = get_settings()
    return {
        "allow_origins": cfg.ALLOWED_ORIGINS,
        "allow_credentials": cfg.ALLOW_CREDENTIALS,
        "allow_methods": cfg.ALLOWED_METHODS,
        "allow_headers": cfg.ALLOWED_HEADERS,
    }
