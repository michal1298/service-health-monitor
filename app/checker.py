"""Service health checker with async HTTP requests.

This module handles actual HTTP service availability checking.
Uses aiohttp to perform asynchronous requests, which allows
parallel checking of multiple services without blocking.

Main functions:
- check_service() - checks a single service
- check_all() - checks all configured services in parallel
"""

import asyncio
from datetime import datetime, timedelta

import aiohttp

from app.config import settings
from app.models import HealthResult


class HealthChecker:
    """Async health checker for multiple services.

    Example usage:
        checker = HealthChecker()
        results = await checker.check_all()
        for result in results:
            print(f"{result.service_name}: {'OK' if result.is_healthy else 'FAIL'}")
    """

    def __init__(self) -> None:
        """Initialize checker with settings from config."""
        self.services = settings.services
        self.timeout = aiohttp.ClientTimeout(total=settings.request_timeout_seconds)
        self._cache: list[HealthResult] = []
        self._cache_time: datetime | None = None
        self._cache_ttl = timedelta(seconds=5)  # Cache for 5 seconds

    async def check_service(self, name: str, url: str) -> HealthResult:
        """Check health of a single service.

        Args:
            name: Service name (e.g., "github")
            url: URL to check (e.g., "https://api.github.com")

        Returns:
            HealthResult with service status information
        """
        start_time = datetime.now()

        try:
            # Create HTTP session and execute request
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    # Calculate response time in milliseconds
                    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

                    return HealthResult(
                        service_name=name,
                        url=url,
                        is_healthy=response.status < 400,  # 2xx and 3xx = OK
                        status_code=response.status,
                        response_time_ms=round(elapsed_ms, 2),
                        error_message=None,
                        checked_at=datetime.now(),
                    )

        except TimeoutError:
            # Service did not respond in time
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthResult(
                service_name=name,
                url=url,
                is_healthy=False,
                status_code=None,
                response_time_ms=round(elapsed_ms, 2),
                error_message="Connection timeout",
                checked_at=datetime.now(),
            )

        except aiohttp.ClientError as e:
            # Connection error (DNS, refused, etc.)
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return HealthResult(
                service_name=name,
                url=url,
                is_healthy=False,
                status_code=None,
                response_time_ms=round(elapsed_ms, 2),
                error_message=str(e),
                checked_at=datetime.now(),
            )

    async def check_all(self, force: bool = False) -> list[HealthResult]:
        """Check all configured services with optional caching.

        Args:
            force: Forces check, ignoring cache
        """
        # If cache exists and is not expired, return from cache
        if not force and self._cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_ttl:
                return self._cache

        if not self.services:
            return []

        # Create list of tasks - each checks one service
        tasks = [self.check_service(name, url) for name, url in self.services.items()]

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)

        # Update cache
        self._cache = list(results)
        self._cache_time = datetime.now()

        return self._cache


# Global checker instance - used by endpoints
checker = HealthChecker()
