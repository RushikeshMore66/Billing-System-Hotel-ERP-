"""
Request-ID middleware.

Generates a unique X-Request-ID header for every incoming request.
If the client already provides one, it is forwarded as-is (useful for
distributed tracing).

The request ID is injected into logging context so every log line
from within a request handler automatically carries the request ID.
"""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request and response."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store on request state so route handlers can read it
        request.state.request_id = request_id

        response: Response = await call_next(request)

        # Echo it back in the response
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
