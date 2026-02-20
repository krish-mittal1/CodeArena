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

### 5. Start Services

```bash
# Terminal 1 — API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Matchmaking worker
python -m workers.matchmaking_worker

# Terminal 3 — Submission worker (run multiple for scaling)
python -m workers.submission_worker
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
