# MediGen Development Guide

## Official Development Environment

**Standard workflow:** Docker backend (PostgreSQL) + Native Vite frontend.

```
┌──────────────────────────────────────────────────────────┐
│  Browser ── http://localhost:3000                        │
│         │                                                │
│         ▼                                                │
│  Vite Dev Server (npm run dev, port 3000)                │
│  ┌──────────────────────────────────────────┐            │
│  │  React SPA (React Router, hot-reload)    │            │
│  │  API calls to http://127.0.0.1:8000/api/v1            │
│  └───────────────────┬──────────────────────┘            │
│                      │                                   │
│  ┌───────────────────▼──────────────────────┐            │
│  │  Docker Container: medigen_backend       │            │
│  │  FastAPI + Uvicorn (port 8000)           │            │
│  │  Hot-reload: ❌ (restart container)      │            │
│  └───────────────────┬──────────────────────┘            │
│                      │                                   │
│  ┌───────────────────▼──────────────────────┐            │
│  │  Docker Container: medigen_db            │            │
│  │  PostgreSQL 15 (port 5432)               │            │
│  └──────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────┘
```

**Why Docker + PostgreSQL is the standard:**

| Concern | Docker + PostgreSQL | Native Uvicorn + SQLite |
|---|---|---|
| **Production parity** | ✅ Same database engine | ❌ SQLite differences mask bugs |
| **Team consistency** | ✅ Identical environment | ❌ Depends on local Python setup |
| **Data integrity testing** | ✅ PostgreSQL constraints enforced | ❌ SQLite is more permissive |
| **JSONB / advanced types** | ✅ Full PostgreSQL feature set | ❌ Not available |
| **Startup speed** | ~15 seconds (cold) | ~1 second |
| **Hot-reload backend** | ❌ Requires restart | ✅ `--reload` flag |
| **Resource usage** | ~1.1 GB (Docker Desktop) | ~44 MB |

**When to use each workflow:**
- **Daily development** → Docker backend + PostgreSQL (standard)
- **Active backend debugging** → Native Uvicorn + `--reload` + Docker PostgreSQL (best of both)
- **Offline / no Docker** → Native Uvicorn + SQLite (fallback only)

---

## Prerequisites

- **Docker Desktop** — for PostgreSQL and standard backend
- **Node.js** v18+ — for the React frontend
- **Python** 3.12+ — for debugging with native Uvicorn
- **npm** (comes with Node.js)

---

## Standard Workflow: Docker Backend + Vite Frontend

### 1. Start the Database and Backend

```bash
# From the project root (./Medigen)

# Build and start all Docker services
docker compose up -d db backend

# Wait for services to become healthy (usually 10-15 seconds)
docker compose ps

# Check the backend is responding
curl http://127.0.0.1:8000/health
# Expected: {"status":"ok","app_name":"MediGen API","database":"connected"}
```

### 2. Start the Frontend

In a **separate terminal**:

```bash
cd frontend

# Install dependencies (one-time)
npm install

# Start the Vite dev server (hot-reload)
npm run dev
```

The frontend starts on `http://localhost:3000`.

> **Why not use the Docker frontend container?** The Docker frontend serves pre-built static files via nginx (no hot-reload, no HMR). For daily development, the Vite dev server gives instant feedback on code changes.

### 3. Verify Everything

```bash
# Backend is running
curl http://127.0.0.1:8000/health

# Frontend is serving
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
# Expected: 200

# API is reachable
curl http://127.0.0.1:8000/api/v1/
```

Open `http://localhost:3000` in your browser. You should see the MediGen login page.

---

## Debugging Workflow: Native Uvicorn + Docker PostgreSQL

When actively developing backend code, run native Uvicorn with hot-reload while keeping the Docker PostgreSQL database.

### 1. Stop the Docker Backend (keep the database)

```bash
docker compose stop backend
```

### 2. Install Backend Dependencies (one-time)

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start Native Uvicorn with PostgreSQL

```bash
MEDIGEN_DATABASE_URL="postgresql://medigen:medigenpass@localhost:5432/medigen" \
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend now has hot-reload (`--reload`) and uses the **same PostgreSQL database** as the Docker backend. Data is preserved when switching between workflows.

### 5. Return to Docker Backend

```bash
# Stop native Uvicorn (Ctrl+C)

# Restart the Docker backend
docker compose start backend
```

---

## Offline / Fallback Workflow: Native Uvicorn + SQLite

When Docker is unavailable, use SQLite as a lightweight fallback. Note that data in the SQLite database is **separate** from the Docker PostgreSQL database.

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations (creates/updates medigen.db)
alembic upgrade head

# Start native Uvicorn with SQLite (reads from .env)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Stopping Services

```bash
# Stop all Docker services
docker compose down

# Stop only backend (keep database running)
docker compose stop backend

# Stop native Uvicorn — press Ctrl+C in its terminal

# Stop Vite dev server — press Ctrl+C in its terminal
```

---

## Database

### Primary: PostgreSQL (Docker, standard)

- Runs in the `medigen_db` Docker container
- Persisted in a Docker volume (`postgres_data`)
- Connection string: `postgresql://medigen:medigenpass@localhost:5432/medigen`
- Data survives container restarts

### Fallback: SQLite (single file)

- File: `./medigen.db`
- Used only when running native Uvicorn without Docker PostgreSQL
- Configured via `.env`: `MEDIGEN_DATABASE_URL=sqlite:///./medigen.db`

> **Important:** Data in PostgreSQL and SQLite are independent. Users created in one are not visible in the other.

### Reset the PostgreSQL Database

```bash
# Destroy and recreate the volume
docker compose down -v
docker compose up -d db backend

# Re-run migrations
docker exec medigen_backend alembic upgrade head
```

---

## Running Tests

```bash
# Backend tests (SQLite, independent of Docker)
pytest

# Run a specific test file
pytest tests/api/test_auth.py -v
```

Tests use a separate SQLite database (not PostgreSQL) for speed and isolation.

---

## Common Troubleshooting

### "Port 8000 is already in use"

Multiple backends (Docker + native Python) are competing for port 8000. On this machine, `127.0.0.1:8000` routes to Docker and `localhost:8000` (IPv6 `::1`) routes to a native Python process.

```bash
# Find what's on port 8000
netstat -ano | findstr ":8000"

# Kill unwanted process (replace PID)
taskkill /PID <PID> /F

# Or stop the Docker backend
docker compose stop backend
```

### Frontend shows blank page or 404

1. Verify `frontend/index.html` exists
2. Reinstall: `cd frontend && npm install`
3. Restart Vite: `npm run dev`

### API calls return 401 (Unauthorized)

The user database depends on which backend you're hitting:

- **Docker backend** (127.0.0.1:8000) → PostgreSQL → register/login here
- **Native backend** (localhost:8000) → SQLite → different users

Register a new user in whichever backend the frontend is configured to use:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Dev User","email":"dev@example.com","password":"DevPass123!"}'
```

### Changed Python code but backend still uses old version

**Docker backend:** Requires a restart:
```bash
docker compose restart backend
```

**Native Uvicorn:** Verify it was started with `--reload`, then save any `.py` file to trigger reload.

### CORS errors in browser console

1. Verify the backend is running on port 8000
2. Ensure you're accessing the frontend at `http://localhost:3000` (not `127.0.0.1:3000`)
3. Check `MEDIGEN_CORS_ORIGINS` includes `http://localhost:3000`

### Docker containers are unhealthy

```bash
# Check logs
docker compose logs backend
docker compose logs db

# Rebuild and restart
docker compose down
docker compose up -d --build
```

### Alembic migration fails

```bash
# Reset and retry
alembic stamp head
alembic upgrade head

# If using SQLite, reset the database file
rm medigen.db
alembic upgrade head
```

### npm install fails

```bash
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## Quick Reference

| Action | Command |
|---|---|
| Start standard environment | `docker compose up -d db backend` |
| Start frontend | `cd frontend && npm run dev` |
| Start backend debugging | `MEDIGEN_DATABASE_URL="postgresql://medigen:medigenpass@localhost:5432/medigen" uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| Stop everything | `docker compose down` |
| Restart Docker backend | `docker compose restart backend` |
| Check status | `docker compose ps` |
| View backend logs | `docker compose logs -f backend` |
| Run tests | `pytest` |
| Reset PostgreSQL | `docker compose down -v && docker compose up -d db backend` |
| Health check | `curl http://127.0.0.1:8000/health` |
| Register a user | `curl -X POST http://127.0.0.1:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{"full_name":"Dev User","email":"dev@example.com","password":"DevPass123!"}'` |