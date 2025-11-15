# ============================================================================
# Stage 1: Base Python Image
# ============================================================================
# We use the official Python 3.12 slim image as our base
# "slim" = smaller image (doesn't include unnecessary tools)
# Alpine is even smaller but can have compatibility issues, so we use slim
FROM python:3.12-slim

# ============================================================================
# Stage 2: Set Working Directory
# ============================================================================
# All subsequent commands will run from /app inside the container
# This is like doing "cd /app" - it's where our code will live
WORKDIR /app

# ============================================================================
# Stage 3: Install System Dependencies
# ============================================================================
# We need PostgreSQL client libraries for psycopg2
# Note: We're installing to the container, not your Mac
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Why these packages?
# - libpq-dev: PostgreSQL development libraries (needed for psycopg2)
# - gcc: C compiler (needed to build psycopg2)
# - rm -rf /var/lib/apt/lists/*: Clean up to keep image small

# ============================================================================
# Stage 4: Copy Dependency Files FIRST
# ============================================================================
# We copy ONLY the dependency files first, not our code
# This creates a layer that only rebuilds when dependencies change
# If pyproject.toml doesn't change, Docker reuses this cached layer
COPY pyproject.toml ./

# ============================================================================
# Stage 5: Install Python Dependencies
# ============================================================================
# Install uv (fast Python package installer) and use it to install deps
# We use pip to install uv, then uv to install our packages
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -e .

# Why --system?
# - We're in a container (isolated environment already)
# - No need for a virtual environment inside a container
# - Install packages system-wide in the container

# Why --no-cache?
# - Don't save pip/uv cache
# - Keeps the Docker image smaller
# - We won't be installing more packages after build

# ============================================================================
# Stage 6: Capture Git Commit SHA for Release Tracking
# ============================================================================
# This build arg is passed during docker build and used for Sentry release tracking
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}

# ============================================================================
# Stage 7: Copy Application Code
# ============================================================================
# NOW we copy our application code
# This layer rebuilds every time you change code (which is frequent)
# But the dependency layers above are cached and fast
COPY src/ ./src/
COPY data/ ./data/

# We don't copy:
# - tests/ (not needed in production)
# - .env (secrets should come from environment variables)
# - .git/ (not needed at runtime)
# - __pycache__/ (will be regenerated)

# ============================================================================
# Stage 8: Set Environment Variables
# ============================================================================
# These are defaults that can be overridden when running the container
ENV PYTHONUNBUFFERED=1
# PYTHONUNBUFFERED=1 means Python outputs immediately (don't buffer)
# Important for seeing logs in real-time

ENV PORT=8000
# The port our app will listen on inside the container

# ============================================================================
# Stage 9: Expose Port
# ============================================================================
# This is documentation - tells users "this app listens on port 8000"
# Doesn't actually open the port (that happens when we run the container)
EXPOSE 8000

# ============================================================================
# Stage 10: Copy Entrypoint Script
# ============================================================================
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# ============================================================================
# Stage 11: Define Startup Command
# ============================================================================
# This command runs when the container starts
# We use the "exec form" (JSON array) for proper signal handling
CMD ["./docker-entrypoint.sh"]

# Why --host 0.0.0.0?
# - Makes the server accessible from outside the container
# - localhost would only work inside the container
# - 0.0.0.0 means "listen on all network interfaces"
