"""Pydantic models for API request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ServiceConfig(BaseModel):
    """Configuration for a service to monitor."""

    name: str
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {
                "name": "github",
                "url": "https://api.github.com",
            }
        }


class HealthResult(BaseModel):
    """Result of a single health check."""

    service_name: str
    url: str
    is_healthy: bool
    status_code: int | None = None
    response_time_ms: float
    error_message: str | None = None
    checked_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "service_name": "github",
                "url": "https://api.github.com",
                "is_healthy": True,
                "status_code": 200,
                "response_time_ms": 145.32,
                "error_message": None,
                "checked_at": "2026-01-31T18:30:00",
            }
        }


class ServicesResponse(BaseModel):
    """Response with all monitored services status."""

    services: list[HealthResult]
    total: int
    healthy: int
    unhealthy: int


class AppHealth(BaseModel):
    """Application health check response."""

    status: str
    version: str
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2026-01-31T22:30:00.123456",
            }
        }


class AppInfo(BaseModel):
    """Basic application information."""

    name: str
    version: str
    docs: str
