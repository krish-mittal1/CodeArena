# CodeArena

CodeArena is a real-time competitive coding platform where users can practice problems, join live 1v1 coding battles, submit code to an online judge, and track their performance over time.

The goal of the project is simple: make coding practice feel more like a live match than a static problem list. A user can sign in, find an opponent, solve the same problem under time pressure, and get instant feedback from the judge.

Live site: https://codexarena.app

## What CodeArena Does

CodeArena has two main modes:

1. Practice mode
   Users can solve coding problems individually, submit code, view verdicts, and improve their solutions.

2. Battle mode
   Two users are matched together in real time. Both receive the same problem, write code in the browser, submit solutions, and the first accepted solution wins the match.

The platform also includes authentication, OTP login, match history, rating/stat tracking, company-wise practice sets, competitive programming style problems, and AI-assisted code feedback.

## Main Features

- User registration and login
- Password-based authentication
- Email OTP authentication
- JWT access and refresh token flow
- Live WebSocket connection after login
- Real-time matchmaking queue
- Private room matchmaking with room codes
- 1v1 coding battle screen
- Online code editor
- Multi-language code execution
- Test-case based judging
- Verdicts such as accepted, wrong answer, runtime error, compilation error, and time limit exceeded
- Practice problem catalog
- Company-wise problem pages
- Competitive programming practice section
- Match history
- User profile, rating, wins, and statistics
- AI-based code analysis and feedback
- Frontend deployment on Vercel
- Backend deployment on Microsoft Azure VM with Docker

## Tech Stack

### Frontend

- Next.js
- React
- Tailwind CSS
- Zustand
- Axios
- Monaco Editor
- WebSockets
- Recharts
- Framer Motion
- Lucide icons

The frontend is responsible for the user interface: landing page, login/register screens, dashboard, practice pages, battle screen, profile, settings, and history.

### Backend

- FastAPI
- Python 3.12
- PostgreSQL
- SQLAlchemy Async ORM
- Alembic migrations
- Redis
- WebSockets
- JWT authentication
- Resend email API for OTP
- Docker
- Uvicorn

The backend handles authentication, user data, matchmaking, match state, submissions, judging, WebSocket events, OTP verification, rating updates, and API responses.

### Database

- PostgreSQL stores users, problems, matches, submissions, test cases, and submission results.
- Alembic manages database migrations.

### Redis

Redis is used for fast real-time state:

- Matchmaking queue
- Active match tracking
- Match timers
- WebSocket pub/sub
- OTP storage and rate-limiting support
- Submission queue in production mode

### AI

The project includes AI-powered code feedback using external LLM APIs. This is used to help users understand mistakes, improve their approach, and learn from failed submissions.

## How The App Works Internally

Here is the normal user flow:

1. A user opens the frontend at `codexarena.app`.
2. The frontend talks to the backend API.
3. The user logs in using username/password or email OTP.
4. The backend returns an access token and refresh token.
5. The frontend stores the refresh token and keeps the access token in memory.
6. After login, the frontend opens a WebSocket connection to the backend.
7. When the user clicks "Find Match", the backend adds the user to the matchmaking queue.
8. Redis stores queue data and active match state.
9. A matchmaking worker checks the queue and pairs compatible users.
10. When two users are matched, the backend creates a match in PostgreSQL.
11. The backend sends a `match_found` event to both users through WebSocket.
12. Both users enter the battle screen and receive the same problem.
13. When a user submits code, the backend creates a submission record.
14. The submission is sent to the judge worker.
15. The judge runs the code against hidden and sample test cases.
16. The backend saves the verdict and test results.
17. If the solution is accepted, the match is completed.
18. Ratings, win/loss stats, and match history are updated.
19. Both users receive live result updates through WebSocket.

## High-Level Architecture

```text
User Browser
    |
    | HTTPS
    v
Next.js Frontend on Vercel
    |
    | REST API + WebSocket
    v
FastAPI Backend on Azure VM
    |
    |----------------------|
    |                      |
    v                      v
PostgreSQL              Redis
Users                   Queue
Problems                Match state
Matches                 Timers
Submissions             Pub/Sub
Results                 OTP state
    |
    v
Judge Worker
    |
    v
Code Execution + Verdicts
```

## Backend Architecture

The backend is organized by responsibility:

```text
backend/
  api/          HTTP route handlers
  core/         constants, security, rate limits, exceptions
  db/           database session and Alembic migrations
  execution/    code execution and language drivers
  models/       SQLAlchemy database models
  schemas/      Pydantic request/response schemas
  services/     business logic
  websocket/    WebSocket manager and handlers
  workers/      judge and matchmaking background workers
```

Important backend modules:

- `backend/main.py` starts the FastAPI app, health checks, CORS, WebSockets, Redis workers, and migrations.
- `backend/api/auth.py` handles password login, registration, and token refresh.
- `backend/api/otp_auth.py` handles OTP login and verification.
- `backend/api/matchmaking.py` handles public queue and private room matchmaking.
- `backend/api/submissions.py` handles code submissions.
- `backend/services/matchmaking_service.py` contains Redis-based matchmaking logic.
- `backend/services/match_service.py` handles match completion and result calculation.
- `backend/workers/judge_worker.py` processes queued submissions.
- `backend/execution/` contains the code execution layer.

## Frontend Architecture

The frontend is organized around pages, reusable components, API clients, state, and WebSocket logic.

```text
frontend/
  pages/        Next.js route wrappers
  src/
    api/        Axios clients and API functions
    components/ Reusable UI and battle components
    hooks/      React hooks
    pages/      Main application pages
    stores/     Zustand auth state
    utils/      constants and helpers
    ws/         WebSocket manager
```

Important frontend areas:

- `src/pages/Landing.jsx` is the public landing page.
- `src/pages/Login.jsx` and `src/pages/Register.jsx` handle authentication.
- `src/pages/Dashboard.jsx` shows stats and match entry points.
- `src/pages/Battle.jsx` is the live battle screen.
- `src/pages/Practice.jsx` is the practice coding interface.
- `src/ws/WebSocketManager.js` maintains the live server connection.
- `src/api/client.js` handles API requests and silent token refresh.
- `src/stores/authStore.js` keeps authentication state.

## Authentication

CodeArena supports two login flows:

1. Username and password
2. Email OTP

After successful authentication, the backend returns:

- Access token
- Refresh token

The access token is used for API requests and WebSocket authentication. The refresh token is used by the frontend to silently refresh the session when the access token expires.

## Matchmaking

Matchmaking is built around Redis.

When a user joins the queue:

1. The backend checks whether the user is already in an active match.
2. The user is added to the Redis matchmaking queue.
3. A matchmaking worker scans the queue.
4. Players are paired based on rating window rules.
5. A match is created in PostgreSQL.
6. Redis stores active match state and timer state.
7. Both users receive a WebSocket event and are moved into the battle screen.

Private matchmaking is also supported through room codes.

## Online Judge

The judge is responsible for checking whether a submitted solution is correct.

The judge flow is:

1. User submits code.
2. Backend stores the submission as queued.
3. Judge worker picks the submission.
4. Code is executed against test cases.
5. Output is compared with expected output.
6. The final verdict is saved.
7. The frontend receives the result.

Supported languages include:

- C++
- Python
- Java
- JavaScript

## Environment Variables

The backend uses environment variables for database, Redis, JWT, OTP, AI keys, and sandbox settings.

Example file:

```text
backend/.env.example
```

Important variables:

```env
DATABASE_URL=
REDIS_ENABLED=
REDIS_URL=
JWT_SECRET_KEY=
JWT_ALGORITHM=
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=
RESEND_API_KEY=
OTP_FROM_EMAIL=
GROQ_API_KEY=
GEMINI_API_KEY=
```

Never commit real `.env` secrets to GitHub.

## Local Development

### Backend

From the project root:

```bash
docker compose -f docker-compose.backend.yml up -d --build
```

Useful backend checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
docker logs api --tail 100
```

API docs are available locally at:

```text
http://localhost:8000/docs
```

### Frontend

From the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## Deployment

The project is deployed as two parts:

### Frontend

The frontend is deployed on Vercel.

The production frontend talks to:

```text
https://api.codexarena.app
```

and uses secure WebSockets through:

```text
wss://api.codexarena.app
```

### Backend

The backend runs on a Microsoft Azure VM using Docker Compose.

The backend stack includes:

- FastAPI API container
- PostgreSQL container
- Redis container

Common server deployment flow:

```bash
git pull origin main
docker compose -f docker-compose.backend.yml up -d --build
docker compose -f docker-compose.backend.yml ps
docker logs api --tail 100
```

## Health Checks

The backend exposes:

```text
/health
/ready
```

`/health` confirms the app process is alive.

`/ready` checks whether required services like database and Redis are reachable.

## Security Notes

This app handles authentication, code execution, and user submissions, so security matters a lot.

Important production rules:

- Keep `.env` private.
- Rotate secrets if they are ever exposed.
- Use strong JWT secrets.
- Keep Redis and PostgreSQL private to the backend network.
- Do not expose database ports publicly.
- Use HTTPS and WSS in production.
- Keep code execution isolated.
- Review sandbox changes carefully before deploying.
- Do not log full JWT tokens.
- Keep API keys out of frontend code.

## Current Production Considerations

For production, Redis should be enabled because matchmaking, WebSocket pub/sub, OTP state, and worker queues depend on it.

If Redis is disabled, the app may still run in local development mode, but production matchmaking and multi-user behavior can become unreliable.

## Why This Project Is Useful

CodeArena is more than a CRUD app. It combines:

- Real-time systems
- Authentication
- WebSockets
- Queue-based workers
- Code execution
- Database design
- Deployment
- AI integration
- Competitive programming logic

That makes it a strong full-stack project because it has both product features and real backend engineering challenges.

## Project Status

The app is live and actively evolving. Core features such as authentication, practice, matchmaking, battles, submissions, and user stats are implemented. The main areas to keep improving are production hardening, judge isolation, monitoring, and deeper automated testing.

