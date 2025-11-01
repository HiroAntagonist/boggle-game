#!/bin/bash
set -e

echo "Initializing database..."
python -m src.init_db

echo "Starting uvicorn..."
exec uvicorn src.api_server:app --host 0.0.0.0 --port 8000
