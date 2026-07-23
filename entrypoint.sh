#!/bin/sh
set -e

echo "=== STEP 1: Startup ==="

echo "=== STEP 2: pwd ==="
pwd

echo "=== STEP 3: python ==="
python --version

echo "=== STEP 4: env ==="
echo "DATABASE_URL=${DATABASE_URL:-unset}"
echo "MEDIGEN_ENVIRONMENT=${MEDIGEN_ENVIRONMENT:-unset}"

echo "=== STEP 5: alembic ==="
alembic upgrade head
echo "Alembic OK"

echo "=== STEP 6: uvicorn ==="
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
