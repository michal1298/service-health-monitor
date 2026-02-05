# Service Health Monitor - AI Agent Instructions
## Architecture Overview

**FastAPI async microservice** that monitors external HTTP services and exposes Prometheus metrics. Core pattern: single `HealthChecker` class performing concurrent HTTP checks using `aiohttp`.

- **[app/main.py](../app/main.py)** - FastAPI routes, entrypoint
- **[app/checker.py](../app/checker.py)** - Async health checking logic (`check_service()`, `check_all()`)
- **[app/config.py](../app/config.py)** - Pydantic Settings with CSV-style `SERVICES_CONFIG` parsing
- **[app/models.py](../app/models.py)** - Pydantic schemas for API responses

**Data flow:** Config → HealthChecker → aiohttp concurrent requests → HealthResult → FastAPI JSON/Prometheus text

## Development Workflow
### Local Development
```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000/docs
```

### Docker Testing
```bash
docker-compose up -d  # Uses .env file, exposes port 8000
docker-compose logs -f monitor
```

### Lint & Format (STRICT)
```bash
ruff check app/      # Linting - blocks CI
ruff format app/     # Formatting - must pass before commit
```

## Project-Specific Conventions
### Code Style
- **Python 3.13** - Use modern type hints (`dict[str, str]`, `int | None`)
- **Polish comments** in code, **English** in docstrings and public-facing text
- Polish explanations like `"Ten moduł odpowiada za..."` in implementation files are intentional
- Use `ruff` for linting/formatting (no black, no flake8)

### Configuration Pattern
Services configured via **CSV-style env var**: `name=url,name2=url2`
```python
# app/config.py
services_config: str = "github=https://api.github.com,google=https://www.google.com"

@property
def services(self) -> dict[str, str]:
    # Parses CSV into dict
```

### Async HTTP Checks
- Use `aiohttp.ClientSession` with timeout from settings
- `asyncio.gather()` for concurrent checks in `check_all()`
- Status codes < 400 considered healthy
- Always catch `asyncio.TimeoutError` and `aiohttp.ClientError` separately

### Documentation
- **README.md must be updated** whenever code changes affect:
  - API endpoints, configuration options, or deployment methods
  - Docker image structure or environment variables
  - CI/CD pipeline behavior or release process
- Keep README.md synchronized with actual implementation, not aspirational features

## Docker & CI/CD
### Multi-Platform Support (CRITICAL)
**Both `linux/amd64` and `linux/arm64`** - supports Raspberry Pi, Apple Silicon, x86 servers.

In CI workflow:
- Build AMD64 → load → Trivy scan (only AMD64 scannable on GitHub Actions)
- Build ARM64 → test compile only (can't execute on x86 runners)
- Production release builds both platforms simultaneously

### Security Practices
1. **pip upgrade** - Always pin `pip>=26.0` in Dockerfile to avoid CVEs
2. **pip-audit** - Runs in CI, blocks on vulnerabilities with `--strict`
3. **Trivy** - Scans Docker images for CRITICAL/HIGH vulnerabilities
4. **Multi-stage Dockerfile** - Alpine builder → minimal runtime (~90MB)
5. **Non-root user** - Runs as `appuser:appgroup` (UID/GID 1000)

### CI Pipeline (.github/workflows/ci.yml)
```
develop branch → lint → security → build-test (AMD64+ARM64) → push dev image
master branch → (via release.yml) → multi-platform prod image → GitHub Release
```

**Important:** Security audit failure requires fixing dependencies in `requirements.txt` or upgrading pip in Dockerfile.

## Version Management
Version set via **build arg** in Dockerfile:
```dockerfile
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
```

Read at runtime from `os.getenv("APP_VERSION", "dev")` in `app/__init__.py`.

## Common Issues
### Multi-platform build fails
- Check `docker/setup-buildx-action@v3` is present
- Can't use `load: true` with multiple platforms - use `push: true` or save to tar

### Security audit failures
- Update pip: `RUN pip install --no-cache-dir --upgrade pip>=X.Y` in Dockerfile
- Check pip-audit output for CVE numbers
- Create GitHub Issue with template: `[Security] package X.Y vulnerability CVE-YYYY-NNNN`

### Service checks timing out
- Default timeout: 10s (`REQUEST_TIMEOUT_SECONDS`)
- Increase in `.env` if monitoring slow endpoints
- Check `aiohttp.ClientTimeout(total=...)` in `checker.py`

## Key Files Reference
- **Dockerfile** - Multi-stage Alpine, security hardened, pin pip version at top of builder stage
- **.env.example** - All environment variables with defaults
- **docker-compose.yml** - Local dev setup, pass-through env vars
- **.github/workflows/ci.yml** - 4 jobs: lint, security, build-test (both platforms), build-dev
- **.github/workflows/release.yml** - Production multi-platform build on tags

## Testing Strategy
**No unit tests yet** - rely on:
1. Ruff linting for code quality
2. Docker build success as integration test
3. Trivy + pip-audit for security
4. FastAPI `/docs` for manual API testing

When adding tests, use `pytest` with `pytest-asyncio` for async test support.

