"""FastAPI application entry point."""

from datetime import datetime

from fastapi import FastAPI

from app import __version__
from app.models import AppHealth, AppInfo, HealthResult, ServicesResponse

app = FastAPI(
    title="Service Health Monitor",
    description="Simple service health monitoring tool for DevOps",
    version=__version__,
)


@app.get("/", response_model=AppInfo)
async def root() -> AppInfo:
    """Root endpoint with basic API information."""
    return AppInfo(
        name="Service Health Monitor",
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
    # Tymczasowe dane demonstracyjne
    demo_results = [
        HealthResult(
            service_name="github",
            url="https://api.github.com",
            is_healthy=True,
            status_code=200,
            response_time_ms=145.32,
            error_message=None,
            checked_at=datetime.now(),
        ),
        HealthResult(
            service_name="google",
            url="https://www.google.com",
            is_healthy=True,
            status_code=200,
            response_time_ms=89.5,
            error_message=None,
            checked_at=datetime.now(),
        ),
    ]

    return ServicesResponse(
        services=demo_results,
        total=2,
        healthy=2,
        unhealthy=0,
    )
