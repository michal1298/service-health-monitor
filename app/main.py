"""FastAPI application entry point."""

from datetime import datetime

from fastapi import FastAPI

from app import __version__
from app.config import settings
from app.models import AppHealth, AppInfo, HealthResult, ServicesResponse

app = FastAPI(
    title=settings.app_name,
    description="Simple service health monitoring tool for DevOps",
    version=__version__,
)


@app.get("/", response_model=AppInfo)
async def root() -> AppInfo:
    """Root endpoint with basic API information."""
    return AppInfo(
        name=settings.app_name,
        version=__version__,
        docs="/docs",
    )


@app.get("/health", response_model=AppHealth)
async def health_check() -> AppHealth:
    """Health check endpoint - returns service status."""
    return AppHealth(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(),
    )


@app.get("/api/services", response_model=ServicesResponse)
async def get_services() -> ServicesResponse:
    """Get status of all monitored services (demo with fake data)."""
    # Tymczasowe dane demonstracyjne - będą zastąpione prawdziwymi danymi
    demo_results = [
        HealthResult(
            service_name=name,
            url=url,
            is_healthy=True,
            status_code=200,
            response_time_ms=100.0,
            error_message=None,
            checked_at=datetime.now(),
        )
        for name, url in settings.services.items()
    ]

    healthy_count = sum(1 for r in demo_results if r.is_healthy)

    return ServicesResponse(
        services=demo_results,
        total=len(demo_results),
        healthy=healthy_count,
        unhealthy=len(demo_results) - healthy_count,
    )
