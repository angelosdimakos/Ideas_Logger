# ─────────────────────────────
# Stage 1: Build dependencies
# ─────────────────────────────
FROM python:3.11-slim-bookworm AS builder

# Install build tools and system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install large, stable dependencies first (rarely change)
COPY base-requirements.txt .
RUN pip install --no-cache-dir -r base-requirements.txt && \
    rm -rf ~/.cache/pip

# Install app-specific dependencies (change more frequently)
COPY app-requirements.txt .
RUN pip install --no-cache-dir -r app-requirements.txt && \
    rm -rf ~/.cache/pip

# ─────────────────────────────
# Stage 2: Runtime environment
# ─────────────────────────────
FROM python:3.11-slim-bookworm AS runtime

# Install runtime system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl gpg \
    tk tcl \
    jq\
    libx11-6 libxext6 libxrender1 libxtst6 \
    xvfb xauth \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy installed site-packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create a non-root user
ARG USER_UID=1001
ARG USER_GID=1001
RUN groupadd -g $USER_GID myuser && \
    useradd -u $USER_UID -g myuser -m myuser

# Set up working directory
WORKDIR /app

# Environment
ENV PYTHONPATH=/app \
    PATH=$PATH:/home/myuser/.local/bin \
    DEBIAN_FRONTEND=noninteractive

# Copy application code (this happens last to maximize cache usage)
COPY --chown=myuser:myuser . .

# Ensure myuser owns the /app directory fully
RUN chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

# Default test entrypoint
ENTRYPOINT ["xvfb-run", "-a", "pytest"]