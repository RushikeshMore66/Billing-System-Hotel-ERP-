"""
API v1 package.

Aggregates all v1 routers. New modules register here.
"""

from app.api.v1 import health

__all__ = ["health"]
