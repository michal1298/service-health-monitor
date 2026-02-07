"""FastAPI application entry point."""

from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from app import __version__
from app.checker import checker
from app.config import settings
from app.models import AppHealth, AppInfo, ServicesResponse


# Background task dla cyklicznych checków
async def periodic_health_check():
    """Automatyczne sprawdzanie serwisów co X sekund."""
    while True:
        await asyncio.sleep(settings.check_interval_seconds)
        await checker.check_all()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager - uruchamia background task."""
    task = asyncio.create_task(periodic_health_check())
    yield
    task.cancel()


app = FastAPI(
    title=settings.app_name,
    description="Simple service health monitoring tool for DevOps",
    version=__version__,
    lifespan=lifespan,
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

    Performs real HTTP requests to all configured services
    and returns their current status.
    """
    # Real service checking!
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

    Use this endpoint when you want to force a check "now"
    instead of waiting for the automatic cycle.
    """
    return await get_services()


@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics() -> str:
    """Prometheus-compatible metrics endpoint.

    Returns metrics in Prometheus text format:
    - `service_up{service="name"} 1|0` - whether the service is running
    - `service_response_time_ms{service="name"} X.XX` - response time

    Example usage in prometheus.yml:
    ```yaml
    scrape_configs:
      - job_name: 'health-monitor'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/metrics'
    ```
    """
    # Get current check results
    results = await checker.check_all()

    # Build response in Prometheus format
    lines = [
        "# HELP service_up Service health status (1=healthy, 0=unhealthy)",
        "# TYPE service_up gauge",
    ]

    for r in results:
        status = 1 if r.is_healthy else 0
        lines.append(f'service_up{{service="{r.service_name}"}} {status}')

    lines.extend(
        [
            "",
            "# HELP service_response_time_ms Service response time in milliseconds",
            "# TYPE service_response_time_ms gauge",
        ]
    )

    for r in results:
        lines.append(
            f'service_response_time_ms{{service="{r.service_name}"}} {r.response_time_ms}'
        )

    return "\n".join(lines)
