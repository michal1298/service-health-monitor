# Build stage - install dependencies
FROM python:3.13-alpine AS builder

# Install build dependencies for aiohttp (needs gcc)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

WORKDIR /app

RUN pip install --no-cache-dir --upgrade "pip>=26.0"

# Copy requirements and install to user directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Runtime stage - minimal image
FROM python:3.13-alpine AS runtime

# Security: Create non-root user
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -D appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Build argument for version (passed from CI)
ARG APP_VERSION=dev

# Copy application code
COPY --chown=appuser:appgroup app/ ./app/

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_VERSION=${APP_VERSION}

EXPOSE 8000

# Health check - sprawdza czy aplikacja odpowiada
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
