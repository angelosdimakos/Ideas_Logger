FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including tkinter and xvfb
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tk \
        tcl \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxtst6 \
        xvfb \
        xauth \
        git \
        build-essential \
        curl \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Set Python path so imports like `from tests...` work
ENV PYTHONPATH=/app

# Pre-set non-interactive for potential future prompts (e.g. git)
ENV DEBIAN_FRONTEND=noninteractive

# Install Python dependencies, including pytest explicitly
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest

COPY . .

# Create a non-root user
RUN adduser --system --group myuser
USER myuser

# Default: run tests with xvfb
ENTRYPOINT ["xvfb-run", "-a", "pytest"]