"""FastAPI application entry point."""

from datetime import datetime

from fastapi import FastAPI

from app import __version__
from app.checker import checker
from app.config import settings
from app.models import AppHealth, AppInfo, ServicesResponse

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
    """Get status of all monitored services.

    Wykonuje prawdziwe requesty HTTP do wszystkich skonfigurowanych serwisów
    i zwraca ich aktualny status.
    """
    # Prawdziwe sprawdzanie serwisów!
    results = await checker.check_all()

    healthy_count = sum(1 for r in results if r.is_healthy)

    return ServicesResponse(
        services=results,
        total=len(results),
        healthy=healthy_count,
        unhealthy=len(results) - healthy_count,
    )


@app.post("/api/check", response_model=ServicesResponse)
async def trigger_check() -> ServicesResponse:
    """Manually trigger health check for all services.

    Używaj tego endpointu gdy chcesz wymusić sprawdzenie "teraz"
    zamiast czekać na automatyczny cykl.
    """
    return await get_services()
