"""
Environment enumeration for NiralayOS.

Defines the valid deployment environments and provides helpers
for environment-aware behaviour throughout the application.
"""

from enum import Enum


class Environment(str, Enum):
    """Valid deployment environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

    @property
    def is_development(self) -> bool:
        return self is Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self is Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self is Environment.TESTING

    @property
    def allows_debug(self) -> bool:
        """Only non-production environments may enable debug mode."""
        return self is not Environment.PRODUCTION
