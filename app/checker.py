"""Service health checker with async HTTP requests.

Ten moduł odpowiada za rzeczywiste sprawdzanie dostępności serwisów HTTP.
Używa aiohttp do wykonywania asynchronicznych requestów, co pozwala
na równoległe sprawdzanie wielu serwisów bez blokowania.

Główne funkcje:
- check_service() - sprawdza pojedynczy serwis
- check_all() - sprawdza wszystkie serwisy z konfiguracji równolegle
"""

import asyncio
from datetime import datetime, timedelta

import aiohttp

from app.config import settings
from app.models import HealthResult


class HealthChecker:
    """Async health checker for multiple services.

    Przykład użycia:
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
        self._cache_ttl = timedelta(seconds=5)  # Cache na 5 sekund

    async def check_service(self, name: str, url: str) -> HealthResult:
        """Check health of a single service.

        Args:
            name: Nazwa serwisu (np. "github")
            url: URL do sprawdzenia (np. "https://api.github.com")

        Returns:
            HealthResult z informacjami o statusie serwisu
        """
        start_time = datetime.now()

        try:
            # Tworzymy sesję HTTP i wykonujemy request
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    # Obliczamy czas odpowiedzi w milisekundach
                    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

                    return HealthResult(
                        service_name=name,
                        url=url,
                        is_healthy=response.status < 400,  # 2xx i 3xx = OK
                        status_code=response.status,
                        response_time_ms=round(elapsed_ms, 2),
                        error_message=None,
                        checked_at=datetime.now(),
                    )

        except asyncio.TimeoutError:
            # Serwis nie odpowiedział w czasie
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
            # Błąd połączenia (DNS, refused, etc.)
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
            force: Wymusza sprawdzenie, ignorując cache
        """
        # Jeśli jest cache i nie jest przeterminowany, zwróć z cache
        if not force and self._cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_ttl:
                return self._cache

        if not self.services:
            return []

        # Tworzymy listę tasków - każdy sprawdza jeden serwis
        tasks = [self.check_service(name, url) for name, url in self.services.items()]

        # Wykonujemy wszystkie taski równolegle
        results = await asyncio.gather(*tasks)

        # Zaktualizuj cache
        self._cache = list(results)
        self._cache_time = datetime.now()

        return self._cache


# Global checker instance - używany przez endpointy
checker = HealthChecker()
