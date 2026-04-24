#!/bin/sh
# entrypoint.sh
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}"
