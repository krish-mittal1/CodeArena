# CodeArena — Real-time Competitive Coding Platform

## Infrastructure Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (for code execution sandbox)

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
copy .env.example .env
# Edit .env with your database and Redis credentials
```

### 3. Database Setup

```bash
# Create the PostgreSQL database
createdb codearena

# Run migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head

# Sync problem packages into Postgres (required for practice + matchmaking)
# New DSA packs under problems/ will not appear in battles until this runs:
python -m backend.tools.sync_problems --all
```

### 4. Build Docker Runner Images

```bash
# Python runner
docker build -t codearena-runner-python:latest -f runners/python.Dockerfile .

# C++ runner
docker build -t codearena-runner-cpp:latest -f runners/cpp.Dockerfile .

# Java runner
docker build -t codearena-runner-java:latest -f runners/java.Dockerfile .

# Node.js runner
docker build -t codearena-runner-node:latest -f runners/node.Dockerfile .
```

### Docker Compose / Docker socket risk

`docker-compose.backend.yml` mounts the **host Docker socket** so the API can
spawn judge runner containers. Anyone who can execute code inside the API
container effectively has root on the host. Mitigations in the default compose:

- Full repo is **not** bind-mounted RW (image copy + `./problems:ro`)
- Sandbox I/O is confined to `./.sandbox_tmp` only
- Set `POSTGRES_PASSWORD` via env (no plaintext password in compose)

For hardened deploys prefer a rootless socket or a scoped Docker socket proxy.

### 5. Start Services

```bash
# Terminal 1 — API server (also starts in-process judge + matchmaking when Redis is on)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 (optional scale-out) — standalone judge worker
# Prefer this when you want judge off the API process:
python -m backend.workers.judge_worker

# Terminal 3 — Matchmaking worker (optional if API lifespan already polls)
python -m workers.matchmaking_worker

# Legacy alternate submission worker (same Redis queue as judge_worker):
# python -m workers.submission_worker
```

## Architecture

```
backend/
├── main.py                 # FastAPI app factory
├── config.py               # Pydantic Settings
├── dependencies.py         # DI (DB, Redis, auth)
├── alembic.ini
├── db/                     # Database layer
├── models/                 # SQLAlchemy ORM models
├── schemas/                # Pydantic schemas
├── api/                    # Route handlers
├── services/               # Business logic
├── workers/                # Background workers
├── execution/              # Docker sandbox
├── websocket/              # WS manager + handlers
├── core/                   # Security, constants, exceptions
└── tests/
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register |
| POST | `/api/v1/auth/login` | — | Login |
| POST | `/api/v1/auth/refresh` | — | Refresh token |
| GET | `/api/v1/users/me` | ✓ | Profile |
| GET | `/api/v1/users/me/stats` | ✓ | Stats |
| POST | `/api/v1/matchmaking/join` | ✓ | Join queue |
| DELETE | `/api/v1/matchmaking/leave` | ✓ | Leave queue |
| GET | `/api/v1/matches/{id}` | — | Match details |
| GET | `/api/v1/matches/history/me` | ✓ | Match history |
| POST | `/api/v1/submissions/` | ✓ | Submit code |
| POST | `/api/v1/problems/` | ✓ | Create problem |
| GET | `/api/v1/problems/` | — | List problems |
| GET | `/api/v1/problems/{id}` | — | Get problem |
| WS | `/ws?token=JWT` | ✓ | Player WebSocket |
| WS | `/ws/spectate/{match_id}` | — | Spectator WS |
| GET | `/health` | — | Health check |
