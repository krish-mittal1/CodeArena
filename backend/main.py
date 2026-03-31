"""
FastAPI application factory with lifespan events.
Main entry point: uvicorn main:app
"""

import logging
import asyncio
import uuid
import os
import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.config import settings
from backend.core.logging_config import setup_logging, set_correlation_id, get_correlation_id
from backend.api.router import api_router
from backend.dependencies import get_redis, close_redis, set_redis_forced_disabled
from backend.websocket.manager import manager
from backend.websocket.handlers import (
    handle_player_connection,
    handle_spectator_connection,
)
from backend.db.session import AsyncSessionLocal, engine
from backend.workers.judge_worker import run_dev_worker, run_redis_worker
from backend.services.matchmaking_memory import run_matchmaking_poller
from backend.services import matchmaking_service, match_service, bot_submission_service
from backend.core.exceptions import AppException
from backend.websocket.manager import manager
from backend.core.constants import WSEvent, MatchStatus, RedisKey
from backend.models.match import Match
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# ── Initialize Logging FIRST (before any logs) ────────────────────
setup_logging()

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    """
    Apply all pending Alembic migrations (upgrade head) on startup.

    Uses the existing async engine to avoid creating a second connection pool.
    Runs the migration commands synchronously inside `run_sync` so Alembic's
    synchronous API works transparently on the async connection.
    """
    from alembic.config import Config
    from alembic import command

    logger.info("Running Alembic migrations …")

    # Resolve the project root (parent of the 'backend' package)
    project_root = Path(__file__).resolve().parent.parent
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "backend" / "db" / "migrations"))

    # Override the DB URL so Alembic uses the same URL as the app
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    def _run_upgrade(connection):
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    async with engine.begin() as conn:
        await conn.run_sync(_run_upgrade)

    logger.info("Alembic migrations applied successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    
    PRODUCTION: Ensures lifespan always yields, never deadlocks.
    All initialization failures are handled gracefully.
    Background tasks get correlation IDs for logging.
    """
    # Set correlation ID for startup logs
    set_correlation_id("startup")
    
    # ── Startup ───────────────────────────────────────────
    logger.info(f"Starting {settings.app_name}...")

    # ── Apply database migrations ─────────────────────────
    try:
        await run_migrations()
    except Exception as exc:
        logger.error(f"Alembic migration failed: {exc}", exc_info=True)
    
    # ── Seed bot users ────────────────────────────────────
    try:
        async with AsyncSessionLocal() as db:
            from backend.scripts.seed_bots import get_or_create_bots
            await get_or_create_bots(db, reset=False)
            logger.info("Bot users initialized")
    except Exception as exc:
        logger.error(f"Failed to seed bot users: {exc}", exc_info=True)
    
    redis = None
    judge_task = None
    matchmaking_task = None
    timer_sync_task = None
    match_recovery_task = None

    try:
        # Initialize Redis connection (with timeout)
        redis = await get_redis()

        if redis is not None:
            try:
                # Manager init must complete within timeout or we skip Redis
                await asyncio.wait_for(manager.init(redis), timeout=5)
                logger.info("Redis connected, WebSocket manager initialized")
            except asyncio.TimeoutError:
                logger.warning(
                    "Redis manager init timed out. "
                    "Running in local-only mode — WebSocket pub/sub disabled."
                )
                redis = None
            except Exception as exc:
                logger.warning(
                    f"Redis unavailable ({exc}). "
                    "Running in local-only mode — WebSocket pub/sub disabled."
                )
                redis = None
        else:
            logger.info(
                "Redis disabled or unavailable. "
                "Running in local-only mode."
            )
    except Exception as exc:
        # Fail-safe: log but continue startup
        logger.error(f"Startup error: {exc}", exc_info=True)
        redis = None

    if redis is None and settings.is_production:
        logger.critical("Redis is required in production startup")
        raise RuntimeError("Redis is required in production")

    # ── Start dev-mode background tasks ────────────────────
    if redis is not None:
        try:
            judge_task = asyncio.create_task(
                run_redis_worker(),
                name="redis-judge-worker",
            )
            matchmaking_task = asyncio.create_task(
                _run_redis_matchmaking_poller(redis),
                name="redis-matchmaking-poller",
            )
            logger.info("Production judge worker started")
            logger.info("Production matchmaking worker started")
        except Exception as exc:
            logger.error(
                f"Failed to start production workers: {exc}",
                exc_info=True,
            )
            if settings.is_production:
                raise

    if redis is None:
        try:
            # Keep runtime behavior consistent with startup decision.
            # If Redis failed at boot and we start dev workers, do not allow
            # request-time Redis reconnect to switch endpoints into Redis mode.
            set_redis_forced_disabled(True)

            # Background tasks inherit correlation ID from their creation context
            # Each task will use "-" for correlation ID unless set in their own context
            judge_task = asyncio.create_task(
                run_dev_worker(AsyncSessionLocal),
                name="dev-judge-worker",
            )
            matchmaking_task = asyncio.create_task(
                run_matchmaking_poller(AsyncSessionLocal),
                name="dev-matchmaking-poller",
            )
            timer_sync_task = asyncio.create_task(
                _run_timer_sync_poller(),
                name="dev-match-timer-sync",
            )
            match_recovery_task = asyncio.create_task(
                _run_match_recovery_poller(),
                name="dev-match-recovery",
            )
            logger.info("Dev-mode judge worker + matchmaking poller started")
        except Exception as exc:
            logger.error(f"Failed to start dev workers: {exc}", exc_info=True)
            # Cancel tasks if they were created
            if judge_task:
                judge_task.cancel()
            if matchmaking_task:
                matchmaking_task.cancel()
            if timer_sync_task:
                timer_sync_task.cancel()
            if match_recovery_task:
                match_recovery_task.cancel()

    # CRITICAL: Always yield, even if initialization failed
    yield

    # ── Shutdown ──────────────────────────────────────────
    set_correlation_id("shutdown")
    logger.info("Shutting down...")
    
    # Cancel background tasks with timeout
    if judge_task is not None:
        judge_task.cancel()
        try:
            await asyncio.wait_for(judge_task, timeout=5)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    
    if matchmaking_task is not None:
        matchmaking_task.cancel()
        try:
            await asyncio.wait_for(matchmaking_task, timeout=5)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

    if timer_sync_task is not None:
        timer_sync_task.cancel()
        try:
            await asyncio.wait_for(timer_sync_task, timeout=5)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass

    if match_recovery_task is not None:
        match_recovery_task.cancel()
        try:
            await asyncio.wait_for(match_recovery_task, timeout=5)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    
    # Shutdown Redis manager and connection
    if redis is not None:
        try:
            await asyncio.wait_for(manager.shutdown(), timeout=5)
        except asyncio.TimeoutError:
            logger.warning("Manager shutdown timed out")
        except Exception as exc:
            logger.error(f"Manager shutdown error: {exc}")
        
        try:
            await asyncio.wait_for(close_redis(), timeout=5)
        except asyncio.TimeoutError:
            logger.warning("Redis close timed out")
        except Exception as exc:
            logger.error(f"Redis close error: {exc}")
    
    logger.info("Shutdown complete")


async def _run_timer_sync_poller() -> None:
    """
    Dev-mode timer sync:
      - Every 5s, send match_timer_sync to active rooms using DB started_at.
      - Prevents drift and guarantees reconnects converge.
    """
    logger = logging.getLogger(__name__)
    logger.info("[MM-DEV] match_timer_sync poller started (every 5s)")

    while True:
        try:
            rooms = await manager.get_active_rooms()
            if rooms:
                async with AsyncSessionLocal() as db:
                    for info in rooms:
                        room_id = info.get("room_id")
                        if not room_id:
                            continue
                        result = await db.execute(
                            select(Match)
                            .where((Match.id == uuid.UUID(room_id)) & (Match.status == MatchStatus.ACTIVE))
                            .options(selectinload(Match.problem))
                        )
                        match = result.scalar_one_or_none()
                        if not match:
                            continue
                        started_at = match.started_at
                        if started_at.tzinfo is None:
                            started_at = started_at.replace(tzinfo=timezone.utc)
                        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
                        remaining = max(0, int(match.duration_seconds - elapsed))
                        await manager.broadcast_to_room(room_id, WSEvent.MATCH_TIMER_SYNC, {"remaining_seconds": remaining})
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[MM-DEV] match_timer_sync poller error: {e}", exc_info=True)

        await asyncio.sleep(5)


async def _run_redis_matchmaking_poller(redis) -> None:
    """
    Production Redis matchmaking loop:
      - Processes the queue so players/bots actually get paired.
      - Completes expired matches.
      - Triggers bot submissions for active matches.
    """
    logger = logging.getLogger(__name__)
    poll_interval = settings.matchmaking_poll_interval_ms / 1000.0
    logger.info("Redis matchmaking poller started")

    while True:
        try:
            async with AsyncSessionLocal() as db:
                new_matches = await matchmaking_service.process_queue(redis, db)

                for match_id in new_matches:
                    match = await match_service.get_match(db, match_id)
                    if not match:
                        continue

                    await redis.publish(
                        RedisKey.ws_channel(str(match_id)),
                        json.dumps({
                            "event": WSEvent.MATCH_FOUND,
                            "data": {
                                "match_id": str(match.id),
                                "problem_id": str(match.problem_id),
                                "problem_title": match.problem.title,
                                "duration_seconds": match.duration_seconds,
                                "player1": {
                                    "user_id": str(match.player1.id),
                                    "username": match.player1.username,
                                    "elo": match.player1.elo,
                                },
                                "player2": {
                                    "user_id": str(match.player2.id),
                                    "username": match.player2.username,
                                    "elo": match.player2.elo,
                                },
                            },
                        }),
                    )

                completed = await match_service.check_and_complete_expired_matches(db, redis)
                for match_id in completed:
                    logger.info(f"Match {match_id} expired and completed")

                bot_processed = await bot_submission_service.process_bot_submissions_for_active_matches(db, redis)
                if bot_processed > 0:
                    logger.debug(f"Processed bot submissions for {bot_processed} matches")

        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error(f"Redis matchmaking poller error: {exc}", exc_info=True)

        await asyncio.sleep(poll_interval)


async def _run_match_recovery_poller() -> None:
    """
    Dev-mode match_found recovery:
      - Some clients can miss match_found due to connect timing.
      - Every 2s, for each connected user, if they have an ACTIVE match in DB but are not in the room,
        resend match_found and join them to the room.
    """
    logger = logging.getLogger(__name__)
    logger.info("[MM-DEV] match_found recovery poller started (every 2s)")

    while True:
        try:
            user_ids = await manager.get_connected_user_ids()
            if user_ids:
                async with AsyncSessionLocal() as db:
                    for user_id in user_ids:
                        try:
                            uid = uuid.UUID(user_id)
                        except Exception:
                            continue

                        res = await db.execute(
                            select(Match)
                            .where(
                                (Match.status == MatchStatus.ACTIVE)
                                & ((Match.player1_id == uid) | (Match.player2_id == uid))
                            )
                            .order_by(Match.started_at.desc())
                            .options(
                                selectinload(Match.player1),
                                selectinload(Match.player2),
                                selectinload(Match.problem),
                            )
                            .limit(1)
                        )
                        match = res.scalar_one_or_none()
                        if not match:
                            continue

                        room_id = str(match.id)
                        if await manager.is_user_in_room(room_id, user_id):
                            continue

                        payload = {
                            "match_id": room_id,
                            "problem_id": str(match.problem_id),
                            "problem_title": match.problem.title if match.problem else "",
                            "player1": {
                                "user_id": str(match.player1.id),
                                "username": match.player1.username,
                                "elo": match.player1.elo,
                            },
                            "player2": {
                                "user_id": str(match.player2.id),
                                "username": match.player2.username,
                                "elo": match.player2.elo,
                            },
                            "duration_seconds": match.duration_seconds,
                        }

                        await manager.send_to_user(user_id, WSEvent.MATCH_FOUND, payload)
                        await manager.join_room(room_id, user_id)
                        logger.info(f"[MM-DEV] Recovered match_found for {user_id} → {room_id}")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[MM-DEV] match_found recovery poller error: {e}", exc_info=True)

        await asyncio.sleep(2)


app = FastAPI(
    title=settings.app_name,
    description="Real-time 1v1 competitive coding platform",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Middleware: Correlation IDs ──────────────────────────────────

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """
    Add correlation ID to HTTP requests for tracing.
    
    PRODUCTION: Uses contextvars for async-safe correlation ID storage.
    All logs within this request context automatically include the correlation ID.
    """
    # Get or generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    
    # Set in contextvar (async-safe, per-request)
    set_correlation_id(correlation_id)
    
    # Also store in request state for exception handlers
    request.state.correlation_id = correlation_id
    
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    finally:
        set_correlation_id("-")


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Add security headers to all HTTP responses.
    Protects against common web vulnerabilities.
    """
    response = await call_next(request)
    
    # Prevent CSRF via SameSite cookie attribute
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


# ── Global Exception Handlers ───────────────────────────────────

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions."""
    correlation_id = get_correlation_id()
    logger.warning(f"AppException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "correlation_id": correlation_id,
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    correlation_id = get_correlation_id()
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "correlation_id": correlation_id,
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle standard FastAPI/Starlette HTTP exceptions directly instead of defaulting to 500."""
    correlation_id = get_correlation_id()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "correlation_id": correlation_id,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler - never return raw 500."""
    correlation_id = get_correlation_id()
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal error details in production
    detail = "Internal server error" if not settings.debug else str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": detail,
            "correlation_id": correlation_id,
            "type": type(exc).__name__ if settings.debug else "internal_error",
        }
    )

# ── CORS ──────────────────────────────────────────────────────

# It is correct setup to add CORSMiddleware via add_middleware - this adds it to the TOP of the stack,
# meaning it is the FIRST middleware executed on incoming requests and LAST on outgoing responses.
# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://codexarena.app",
        "https://www.codexarena.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type"],
    max_age=3600,
)

# ── HTTP Routes ───────────────────────────────────────────────

app.include_router(api_router)


# ── WebSocket Endpoints ──────────────────────────────────────

@app.websocket("/ws")
async def websocket_player(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint for authenticated players.
    
    PRODUCTION: Sets correlation ID for WebSocket connection logging.
    """
    # Generate correlation ID for WebSocket connection
    correlation_id = str(uuid.uuid4())
    set_correlation_id(correlation_id)
    
    try:
        redis = await get_redis()
        await handle_player_connection(websocket, token, redis)
    finally:
        set_correlation_id("-")


@app.websocket("/ws/spectate/{match_id}")
async def websocket_spectator(
    websocket: WebSocket,
    match_id: str,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for match spectators (read-only).
    
    PRODUCTION: Sets correlation ID for WebSocket connection logging.
    """
    # Generate correlation ID for WebSocket connection
    correlation_id = str(uuid.uuid4())
    set_correlation_id(correlation_id)
    
    try:
        redis = await get_redis()
        await handle_spectator_connection(websocket, match_id, redis, token)
    finally:
        set_correlation_id("-")


# ── Health Check Endpoints ──────────────────────────────────────

@app.get("/health")
async def health():
    """
    Basic health check - returns 200 if server is running.
    Does not check dependencies.
    """
    return {"status": "ok", "app": settings.app_name}


@app.get("/ready")
async def ready():
    """
    Readiness check - verifies critical dependencies are available.
    Returns 503 if any dependency is unavailable.
    """
    checks = {
        "database": False,
        "redis": False,
    }
    
    # Check database
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            await asyncio.wait_for(db.execute(text("SELECT 1")), timeout=2)
        checks["database"] = True
    except Exception as e:
        logger.warning(f"Database readiness check failed: {e}")
    
    # Check Redis (if enabled)
    if settings.redis_enabled:
        redis = await get_redis()
        if redis:
            try:
                await asyncio.wait_for(redis.ping(), timeout=2)
                checks["redis"] = True
            except Exception as e:
                logger.warning(f"Redis readiness check failed: {e}")
        else:
            checks["redis"] = False
    else:
        checks["redis"] = True  # Redis disabled is OK
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "checks": checks}
        )
