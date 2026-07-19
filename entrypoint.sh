#!/bin/sh
set -e

echo "Current working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "DATABASE_URL: ${DATABASE_URL:-unset}"
if [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL scheme: $(echo "$DATABASE_URL" | grep -o '^[^:]*')"
fi
echo "Alembic config: $(find . -name 'alembic.ini' -print -quit)"
echo "Running Alembic migrations..."
alembic upgrade head
echo "Migrations completed."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}