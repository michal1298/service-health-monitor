"""Service Health Monitor - FastAPI microservice for monitoring external HTTP services."""

import os

__version__ = os.getenv("APP_VERSION", "dev")
