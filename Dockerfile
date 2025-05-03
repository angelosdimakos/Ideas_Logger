# ─────────────────────────────
# Stage 1: Build dependencies
# ─────────────────────────────
FROM python:3.11-slim-bookworm AS builder

# Install build tools and system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages globally (no venv)
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=faiss-cpu -r requirements.txt && \
    rm -rf /root/.cache/pip


# ─────────────────────────────
# Stage 2: Runtime environment
# ─────────────────────────────
FROM python:3.11-slim-bookworm AS runtime

# Install runtime system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    tk tcl \
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
USER myuser
WORKDIR /app

# Environment
ENV PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Copy only necessary files
COPY --chown=myuser:myuser . .

# Default test entrypoint
ENTRYPOINT ["xvfb-run", "-a", "pytest"]
