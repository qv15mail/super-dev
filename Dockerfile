# Super Dev — Python CLI tool
# Multi-stage build for production deployment

# ========== Build stage ==========
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
COPY pyproject.toml requirements.lock ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.lock

# Copy source and install
COPY super_dev/ super_dev/
RUN pip install --no-cache-dir --no-deps .

# ========== Production stage ==========
FROM python:3.12-slim AS production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends dumb-init && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g 1001 superdev && \
    useradd -u 1001 -g superdev -s /bin/bash -m superdev

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/super-dev /usr/local/bin/super-dev

# Copy project files needed at runtime
COPY super_dev/ /app/super_dev/
COPY super-dev.yaml /app/super-dev.yaml
COPY knowledge/ /app/knowledge/

# Switch to non-root user
USER superdev

EXPOSE 8000

ENTRYPOINT ["dumb-init", "--"]
CMD ["super-dev", "web", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1
