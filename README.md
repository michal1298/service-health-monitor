# 🏥 Service Health Monitor

Simple, lightweight service health monitoring tool built with Python and FastAPI.

## ✨ Features

- ⚡ **Async health checks** - Concurrent monitoring using aiohttp
- 🐘 **PostgreSQL storage** - Reliable data persistence
- 📊 **Prometheus metrics** - Ready for Grafana dashboards
- 🐳 **Docker ready** - Multi-stage Alpine image
- 🔄 **CI/CD** - GitHub Actions for testing and releases

## 🚀 Quick Start

### Local Development

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
| `/api/services` | GET | List all monitored services (demo data) |
| `/docs` | GET | Swagger documentation |

## 📁 Project Structure

```
hardware_test_runner/
├── app/
│   ├── __init__.py      # Package with version
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic schemas
│   ├── config.py        # Application settings
│   └── api/
│       └── __init__.py
├── .env.example         # Example environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `monitor` | Database user |
| `POSTGRES_PASSWORD` | `monitor` | Database password |
| `POSTGRES_DB` | `health_monitor` | Database name |
| `SERVICES_CONFIG` | `github=https://api.github.com` | Services to monitor |
| `CHECK_INTERVAL_SECONDS` | `60` | Health check interval |

## 🛠️ Tech Stack

- **Python 3.13**
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation and settings
- **Uvicorn** - ASGI server

