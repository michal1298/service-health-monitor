# 🏥 Service Health Monitor

[![CI](https://github.com/michal1298/service-health-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/michal1298/service-health-monitor/actions/workflows/ci.yml)
[![Release](https://github.com/michal1298/service-health-monitor/actions/workflows/release.yml/badge.svg)](https://github.com/michal1298/service-health-monitor/actions/workflows/release.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/michal1298/service-health-monitor)](https://github.com/michal1298/service-health-monitor/releases/latest)

Simple, lightweight service health monitoring tool built with Python and FastAPI.

## ✨ Features

- ⚡ **Async health checks** - Concurrent monitoring using aiohttp
- 📊 **Prometheus metrics** - Ready for Grafana dashboards
- 🐳 **Docker ready** - Multi-stage Alpine image (~90MB)
- 🔄 **CI/CD** - GitHub Actions for testing and releases

## 🚀 Quick Start
### Option 1: `UV`

[UV](https://github.com/astral-sh/uv) is a ultra-fast Python package manager written in Rust (faster than pip).

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone git@github.com:michal1298/service-health-monitor.git
cd service-health-monitor

# Create venv and install dependencies in one command
uv sync

# Activate virtual environment
source .venv/bin/activate

# Run application
uvicorn app.main:app --reload
```

### Option 2: Traditional `pip`
```bash
# Clone repository
git clone git@github.com:michal1298/service-health-monitor.git
cd service-health-monitor

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload
```

### Access API

- **Root:** http://localhost:8000/
- **Health:** http://localhost:8000/health
- **Docs:** http://localhost:8000/docs

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Application health check |
| `/api/services` | GET | List all monitored services with real status |
| `/api/check` | POST | Manually trigger health check |
| `/metrics` | GET | Prometheus-compatible metrics |
| `/docs` | GET | Swagger documentation |

## 📁 Project Structure

```
service-health-monitor/
├── app/
│   ├── __init__.py      # Package with version
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic schemas
│   ├── config.py        # Application settings
│   └── checker.py       # Health check logic
├── .github/
│   └── workflows/
│       ├── ci.yml       # Lint, security & build dev image
│       └── release.yml  # Build prod image (master + tags)
├── Dockerfile           # Multi-stage Docker build
├── docker-compose.yml   # Docker Compose configuration
├── pyproject.toml       # Project metadata & dependencies (UV/pip)
├── requirements.txt     # Locked dependencies (pip fallback)
├── uv.lock              # UV lock file (deterministic builds)
├── .dockerignore
├── .env.example         # Example environment variables
├── .gitignore
├── README.md
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICES_CONFIG` | `github=https://api.github.com` | Services to monitor |
| `CHECK_INTERVAL_SECONDS` | `60` | Health check interval |
| `REQUEST_TIMEOUT_SECONDS` | `10` | HTTP request timeout |

## 🛠️ Tech Stack

- **Python 3.13**
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation and settings
- **aiohttp** - Async HTTP client
- **Docker** - Multi-stage Alpine build
- **Uvicorn** - ASGI server
- **UV** (optional) - Ultra-fast package manager

## 🐳 Docker

### Build and run with Docker Compose

```bash
# Start application
docker-compose up -d

# Check logs
docker-compose logs -f monitor

# Stop
docker-compose down
```

### Build image only

```bash
docker build -t service-health-monitor .
docker run -p 8000:8000 service-health-monitor
```

## 📦 Releases

Docker images are automatically built and pushed to GitHub Container Registry:

| Tag | Description |
|-----|-------------|
| `ghcr.io/michal1298/service-health-monitor:dev` | Latest develop branch |
| `ghcr.io/michal1298/service-health-monitor:latest` | Latest release |
| `ghcr.io/michal1298/service-health-monitor:X.Y.Z` | Specific version |

```bash
# Pull and run latest release
docker pull ghcr.io/michal1298/service-health-monitor:latest
docker run -p 8000:8000 ghcr.io/michal1298/service-health-monitor:latest
```

## 🔧 Development
### Adding dependencies

**With `UV`:**
```bash
uv add fastapi  # Adds to pyproject.toml and updates uv.lock
uv sync         # Installs all dependencies
```

**With `pip`:**
```bash
pip install fastapi
pip freeze > requirements.txt  # Update requirements.txt manually
```

### Linting and formatting

```bash
# With `UV`
uv run ruff check app/
uv run ruff format app/

# With `pip` (after `pip` install `ruff`)
ruff check app/
ruff format app/
```
