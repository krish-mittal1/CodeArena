"""
Judge worker — process submissions from queue, execute in sandbox, save results.

Usage:
    # With Redis (production):
    python -m backend.workers.judge_worker

    # Without Redis (dev mode): started automatically by FastAPI lifespan
    # as an in-process background task.

Architecture:
    1. Pop submission_id from queue (Redis BRPOP or asyncio.Queue)
    2. Load submission + test cases from PostgreSQL
    3. For each test case:
       a. Call sandbox.run_code() in a thread (blocking Docker call)
       b. Call judge_service.judge() to get verdict
       c. Save SubmissionResult to DB
    4. Update Submission.status based on results
    5. Broadcast SUBMISSION_RESULT via WebSocket
    6. If ACCEPTED → trigger match completion + ELO update
    7. Broadcast MATCH_ENDED via WebSocket
"""

import asyncio
import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.core.constants import SubmissionStatus, Verdict
from backend.models.submission import Submission
from backend.models.submission_result import SubmissionResult
from backend.models.test_case import TestCase
from backend.services.judge_service import judge
from backend.execution.sandbox import sandbox, ExecutionResult

logger = logging.getLogger(__name__)

# In-memory queue for dev mode (no Redis)
dev_queue: asyncio.Queue[str] = asyncio.Queue()


async def _emit_submission_result(
    submission: Submission,
    verdict: str,
    passed: int,
    total: int,
    runtime_ms: int,
    memory_kb: int,
) -> None:
    """Emit SUBMISSION_RESULT WebSocket event to the submitter (dev-mode, no Redis)."""
    try:
        from backend.websocket.manager import manager

        room_id = str(submission.match_id)
        submitter_id = str(submission.user_id)
        submission_id = str(submission.id)

        await manager.broadcast_submission_result(
            room_id=room_id,
            submitter_id=submitter_id,
            verdict=verdict,
            passed=passed,
            total=total,
            runtime_ms=runtime_ms,
            memory_kb=memory_kb,
            submission_id=submission_id,
        )
        logger.info(
            f"[WS] Sent submission_result to {submitter_id} "
            f"(verdict={verdict}, submission={submission_id})"
        )
    except Exception as e:
        logger.error(f"[WS] Failed to emit submission_result: {e}", exc_info=True)


async def _emit_match_ended(match_result: dict) -> None:
    """Emit MATCH_ENDED WebSocket event to both players (dev-mode, no Redis)."""
    try:
        from backend.websocket.manager import manager

        room_id = match_result["match_id"]
        await manager.broadcast_match_ended(room_id, match_result)
        logger.info(
            f"[WS] Sent match_ended to {match_result.get('player1_id')} "
            f"and {match_result.get('player2_id')} "
            f"(winner={match_result.get('winner_id')}, reason={match_result.get('reason')})"
        )
    except Exception as e:
        logger.error(f"[WS] Failed to emit match_ended: {e}", exc_info=True)


async def process_submission(
    session_factory: async_sessionmaker,
    submission_id: uuid.UUID,
) -> None:
    """
    Fail-safe wrapper around the judge pipeline.
    Guarantees a SUBMISSION_RESULT WebSocket event is ALWAYS sent,
    even if the sandbox, DB, or any other component crashes.
    """
    try:
        await _process_submission_inner(session_factory, submission_id)
    except Exception as e:
        logger.error(
            f"[JUDGE] Unhandled error processing submission {submission_id}: {e}",
            exc_info=True,
        )
        # Emergency fallback: mark as RUNTIME_ERROR and notify frontend
        # Log the EXACT cause so we never have mystery runtime_errors
        try:
            async with session_factory() as db:
                result = await db.execute(
                    select(Submission)
                    .where(Submission.id == submission_id)
                )
                submission = result.scalar_one_or_none()
                if submission and submission.status in (
                    SubmissionStatus.QUEUED, SubmissionStatus.RUNNING
                ):
                    submission.status = SubmissionStatus.RUNTIME_ERROR
                    submission.judged_at = datetime.now(timezone.utc)
                    await db.commit()

                    logger.error(
                        f"[JUDGE] EMERGENCY FALLBACK for {submission_id}: "
                        f"Marking as runtime_error due to infrastructure failure. "
                        f"Root cause: {type(e).__name__}: {e}"
                    )

                    await _emit_submission_result(
                        submission, "runtime_error", 0, 0, 0, 0
                    )
        except Exception as fallback_err:
            logger.error(
                f"[JUDGE] Emergency fallback also failed for {submission_id}: {fallback_err}",
                exc_info=True,
            )


async def _process_submission_inner(
    session_factory: async_sessionmaker,
    submission_id: uuid.UUID,
) -> None:
    """
    Full judge pipeline for a single submission.

    PRODUCTION: Idempotent - can be safely retried.
    If submission is already processed, skips execution.

    1. Load submission + test cases
    2. Execute code against each test case in Docker sandbox
    3. Save per-test-case results
    4. Update overall submission status
    5. Emit SUBMISSION_RESULT via WebSocket
    6. If ACCEPTED → complete match, emit MATCH_ENDED
    """
    async with session_factory() as db:
        # ── Load submission with problem ──────────────────
        result = await db.execute(
            select(Submission)
            .where(Submission.id == submission_id)
            .options(selectinload(Submission.problem))
        )
        submission = result.scalar_one_or_none()
        if not submission:
            logger.error(f"[JUDGE] Submission {submission_id} not found in DB")
            return

        # ── Idempotency check: skip if already processed ───
        if submission.status not in (SubmissionStatus.QUEUED, SubmissionStatus.RUNNING):
            logger.info(
                f"[JUDGE] Submission {submission_id} already processed "
                f"(status={submission.status}), skipping"
            )
            return

        # If stuck in RUNNING for > 60s, another worker likely crashed — re-process
        if submission.status == SubmissionStatus.RUNNING:
            if submission.judged_at is None:
                updated_at = submission.submitted_at
            else:
                updated_at = submission.judged_at
            if updated_at and (datetime.now(timezone.utc) - updated_at.replace(tzinfo=timezone.utc if updated_at.tzinfo is None else updated_at.tzinfo)).total_seconds() < 60:
                logger.info(f"[JUDGE] Submission {submission_id} already RUNNING (recent), skipping")
                return
            logger.warning(f"[JUDGE] Submission {submission_id} stuck in RUNNING > 60s, re-processing")

        # ── Load test cases ───────────────────────────────
        tc_result = await db.execute(
            select(TestCase)
            .where(TestCase.problem_id == submission.problem_id)
            .order_by(TestCase.order_index)
        )
        test_cases = list(tc_result.scalars().all())

        if not test_cases:
            logger.error(
                f"[JUDGE] No test cases for problem {submission.problem_id} "
                f"(submission {submission_id})"
            )
            submission.status = SubmissionStatus.RUNTIME_ERROR
            submission.judged_at = datetime.now(timezone.utc)
            await db.commit()
            await _emit_submission_result(submission, "runtime_error", 0, 0, 0, 0)
            return

        # ── Mark as running (atomic update) ───────────────
        result = await db.execute(
            select(Submission)
            .where(
                Submission.id == submission_id,
                Submission.status.in_([SubmissionStatus.QUEUED, SubmissionStatus.RUNNING])
            )
            .options(selectinload(Submission.problem))
        )
        submission = result.scalar_one_or_none()
        if not submission:
            logger.warning(
                f"[JUDGE] Submission {submission_id} status changed, skipping"
            )
            return

        submission.status = SubmissionStatus.RUNNING
        await db.commit()
        await db.refresh(submission)

        logger.info(
            f"[JUDGE] ═══ Processing submission {submission_id} ═══ "
            f"problem={submission.problem_id}, "
            f"language={submission.language}, "
            f"test_cases={len(test_cases)}"
        )

        # ── Execute ALL test cases in ONE container ─────────
        passed = 0
        overall_verdict = Verdict.ACCEPTED
        max_time_ms = 0
        max_memory_kb = 0

        time_limit_ms = submission.problem.time_limit_ms if submission.problem else 2000
        memory_limit_mb = submission.problem.memory_limit_mb if submission.problem else 256

        # Batch execute: compile once, run all tests in a single container
        # Build problem_meta for LeetCode-style driver injection
        problem_meta = None
        if submission.problem and submission.problem.method_name:
            problem_meta = {
                "method_name": submission.problem.method_name,
                "parameters": submission.problem.parameters,
                "return_type": submission.problem.return_type,
            }
        
        try:
            batch_results = await sandbox.execute_batch(
                language=submission.language,
                code=submission.code,
                test_inputs=[tc.input for tc in test_cases],
                time_limit_ms=time_limit_ms,
                memory_limit_mb=memory_limit_mb,
                problem_meta=problem_meta,
            )
        except Exception as batch_err:
            logger.error(
                f"[JUDGE] Batch execution crashed for submission "
                f"{submission_id}: {batch_err}",
                exc_info=True,
            )
            # Fallback: mark all as runtime error
            batch_results = [
                ExecutionResult(
                    stdout="",
                    stderr=f"Execution engine error: {batch_err}",
                    exit_code=1, timed_out=False, oom_killed=False,
                    time_ms=0, memory_kb=0, stage="infrastructure",
                )
            ] * len(test_cases)

        # ── Judge each result (fail-fast on first failure) ──
        for tc_idx, (tc, sandbox_result) in enumerate(zip(test_cases, batch_results)):

            # ── COMPILATION ERROR check ───────────────────
            if sandbox_result.stage == "compile" and sandbox_result.exit_code != 0:
                is_infra_compile_failure = (
                    sandbox_result.timed_out
                    or "Execution engine error" in sandbox_result.stderr
                    or "sandbox container did not respond" in sandbox_result.stderr
                )
                failure_status = (
                    SubmissionStatus.RUNTIME_ERROR
                    if is_infra_compile_failure
                    else SubmissionStatus.COMPILATION_ERROR
                )
                failure_event = (
                    "runtime_error"
                    if is_infra_compile_failure
                    else "compilation_error"
                )
                tc_result_obj = SubmissionResult(
                    submission_id=submission.id,
                    test_case_id=tc.id,
                    verdict=failure_status,
                    execution_time_ms=0,
                    memory_used_kb=0,
                    actual_output="",
                    error_output=sandbox_result.stderr[:2000],
                )
                db.add(tc_result_obj)

                submission.status = failure_status
                submission.passed_test_cases = passed
                submission.judged_at = datetime.now(timezone.utc)
                await db.commit()

                logger.info(
                    f"[JUDGE] {submission_id} TC#{tc_idx}: "
                    f"verdict={submission.status}, "
                    f"stderr={repr(sandbox_result.stderr[:300])}"
                )
                await _emit_submission_result(
                    submission, failure_event, passed, len(test_cases), 0, 0
                )
                return
            else:
                problem_title = submission.problem.title if submission.problem else None
                is_leetcode = problem_meta is not None
                verdict = judge(
                    actual_output=sandbox_result.stdout,
                    expected_output=tc.expected_output,
                    exit_code=sandbox_result.exit_code,
                    timed_out=sandbox_result.timed_out,
                    oom_killed=sandbox_result.oom_killed,
                    problem_title=problem_title,
                    is_leetcode_mode=is_leetcode,
                )

            # ── Log per-test-case details ─────────────────
            logger.info(
                f"[JUDGE] {submission_id} TC#{tc_idx}: "
                f"verdict={verdict.value}, "
                f"exit_code={sandbox_result.exit_code}, "
                f"time_ms={sandbox_result.time_ms}, "
                f"timed_out={sandbox_result.timed_out}, "
                f"oom_killed={sandbox_result.oom_killed}, "
                f"stdout_len={len(sandbox_result.stdout)}, "
                f"stderr_preview={repr(sandbox_result.stderr[:200])}"
            )

            # Track max resource usage
            max_time_ms = max(max_time_ms, sandbox_result.time_ms)
            max_memory_kb = max(max_memory_kb, sandbox_result.memory_kb)

            # ── Save per-test-case result ─────────────────
            tc_result_obj = SubmissionResult(
                submission_id=submission.id,
                test_case_id=tc.id,
                verdict=verdict.value,
                execution_time_ms=sandbox_result.time_ms,
                memory_used_kb=sandbox_result.memory_kb,
                actual_output=sandbox_result.stdout[:2000],
                error_output=sandbox_result.stderr[:2000] if sandbox_result.stderr else None,
            )
            db.add(tc_result_obj)

            if verdict == Verdict.ACCEPTED:
                passed += 1
            else:
                overall_verdict = verdict
                # Stop judging on first failure (competitive style)
                break

        # ── Update submission status ──────────────────────
        try:
            if overall_verdict == Verdict.ACCEPTED:
                submission.status = SubmissionStatus.ACCEPTED
            elif overall_verdict == Verdict.WRONG_ANSWER:
                submission.status = SubmissionStatus.WRONG_ANSWER
            elif overall_verdict == Verdict.TLE:
                submission.status = SubmissionStatus.TLE
            elif overall_verdict == Verdict.MLE:
                submission.status = SubmissionStatus.MLE
            elif overall_verdict == Verdict.RUNTIME_ERROR:
                submission.status = SubmissionStatus.RUNTIME_ERROR
            else:
                # Should never happen, but log if it does
                logger.warning(
                    f"[JUDGE] Unknown verdict {overall_verdict} for {submission_id}, "
                    f"defaulting to RUNTIME_ERROR"
                )
                submission.status = SubmissionStatus.RUNTIME_ERROR

            submission.passed_test_cases = passed
            submission.total_test_cases = len(test_cases)
            submission.execution_time_ms = max_time_ms
            submission.memory_used_kb = max_memory_kb
            submission.judged_at = datetime.now(timezone.utc)

            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.error(f"[JUDGE] Failed to update submission {submission_id}: {e}")
            raise

        logger.info(
            f"[JUDGE] ═══ {submission_id}: FINAL={submission.status} ═══ "
            f"({passed}/{len(test_cases)} passed, "
            f"time={max_time_ms}ms, mem={max_memory_kb}KB)"
        )

        # ── Emit SUBMISSION_RESULT via WebSocket ──────────
        await _emit_submission_result(
            submission,
            submission.status,
            passed,
            len(test_cases),
            max_time_ms,
            max_memory_kb,
        )

        # ── If ACCEPTED, trigger match completion ─────────
        if submission.status == SubmissionStatus.ACCEPTED and submission.match_id is not None:
            try:
                from backend.services import match_service

                async with session_factory() as match_db:
                    match_result = await match_service.complete_match_with_winner(
                        db=match_db,
                        redis=None,
                        match_id=submission.match_id,
                        winner_id=submission.user_id,
                        reason="accepted",
                    )
                    if match_result:
                        logger.info(
                            f"[JUDGE] Match {submission.match_id} completed. "
                            f"Winner: {match_result.get('winner_id')}"
                        )
                        await _emit_match_ended(match_result)

                        try:
                            from backend.services.matchmaking_memory import memory_queue
                            memory_queue.clear_match_for_both(
                                match_result["player1_id"],
                                match_result["player2_id"],
                            )
                        except Exception as e:
                            logger.warning(
                                f"[JUDGE] Failed to clear dev active_matches: {e}",
                                exc_info=True,
                            )
                    else:
                        logger.info(
                            f"[JUDGE] Match {submission.match_id} already completed, "
                            f"skipping duplicate completion"
                        )
            except Exception as e:
                logger.warning(f"[JUDGE] Match completion failed: {e}", exc_info=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Worker loops
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def run_dev_worker(session_factory: async_sessionmaker) -> None:
    """Dev-mode worker: polls asyncio.Queue (no Redis required)."""
    logger.info("[JUDGE] Dev-mode worker started (asyncio.Queue)")

    while True:
        try:
            submission_id_str = await dev_queue.get()
            submission_id = uuid.UUID(submission_id_str)
            logger.info(f"[JUDGE] Dequeued submission {submission_id} from dev queue")
            await process_submission(session_factory, submission_id)
            dev_queue.task_done()
        except asyncio.CancelledError:
            logger.info("[JUDGE] Dev worker shutting down")
            break
        except Exception as e:
            logger.error(f"[JUDGE] Dev worker error: {e}", exc_info=True)


async def run_redis_worker() -> None:
    """Production worker: polls Redis BRPOP (standalone process)."""
    import redis.asyncio as aioredis
    from backend.core.constants import RedisKey

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    logger.info("[JUDGE] Redis worker started")
    logger.info(f"[JUDGE] Polling queue: {RedisKey.SUBMISSION_QUEUE}")

    while True:
        try:
            result = await redis.brpop(RedisKey.SUBMISSION_QUEUE, timeout=5)
            if result is None:
                continue

            _, payload = result
            data = json.loads(payload)
            submission_id = uuid.UUID(data["submission_id"])

            logger.info(f"[JUDGE] Dequeued submission {submission_id} from Redis")
            await process_submission(session_factory, submission_id)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[JUDGE] Redis worker error: {e}", exc_info=True)
            await asyncio.sleep(1)

    await redis.close()
    await engine.dispose()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Standalone entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if settings.redis_enabled:
        logger.info("Starting judge worker with Redis queue...")
        asyncio.run(run_redis_worker())
    else:
        logger.info("Redis disabled. Use dev-mode worker via FastAPI lifespan.")
        sys.exit(0)
