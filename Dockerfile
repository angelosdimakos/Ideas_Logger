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
        git \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set Python path so imports like `from tests...` work
ENV PYTHONPATH=/app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: run tests with xvfb
ENTRYPOINT ["xvfb-run", "-a", "pytest"]
