"""
Authentication middleware for NiralayOS.

Note: In FastAPI, it is generally preferred to use Dependencies (e.g. `Depends(get_current_user)`)
for authentication at the route level, as dependencies integrate natively with OpenAPI/Swagger
and allow granular, per-route authorization.

This module is provided for global authentication checks if needed, but
Sprint 2 relies on dependencies (`app.api.dependencies`) to protect routes
and enforce RBAC.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.security import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optional global authentication middleware.
    Decodes the JWT token (if present) and attaches the payload to `request.state`.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                request.state.user_uuid = payload.sub
                request.state.roles = payload.role
                request.state.permissions = payload.permissions
            except Exception:
                # Let the route-level dependency handle invalid tokens
                # or block it here globally if all routes are protected.
                pass

        response = await call_next(request)
        return response
