"""
Submission worker — consumes from Redis queue, executes code in Docker
via subprocess sandbox, judges output, and publishes verdict.

Run separately:  python -m workers.submission_worker

Architecture:
  Redis BRPOP (blocking) → load submission from DB → execute per test case
  → judge output → persist results → PUBLISH verdict via Redis pub/sub
"""

import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.config import settings
from backend.db.session import AsyncSessionLocal
from backend.core.constants import SubmissionStatus, RedisKey, WSEvent, Verdict
from backend.execution.sandbox import sandbox
from backend.services.judge_service import judge
from backend.services import match_service
from backend.models.submission import Submission
from backend.models.submission_result import SubmissionResult
from backend.models.test_case import TestCase

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Worker loop
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def run_worker():
    """
    Main worker loop.
    BRPOP blocks until a submission is available, then processes it.
    Runs indefinitely with error backoff.
    """
    redis = aioredis.from_url(settings.redis_url, decode_responses=False)

    logger.info("Submission worker started — waiting for jobs...")

    while True:
        try:
            # BRPOP: atomic blocking pop (timeout=0 → wait forever)
            result = await redis.brpop(RedisKey.SUBMISSION_QUEUE, timeout=0)
            if not result:
                continue

            _, raw = result
            data = json.loads(raw)
            submission_id = uuid.UUID(data["submission_id"])

            logger.info(f"[WORKER] Dequeued submission {submission_id}")
            await process_submission(redis, submission_id)

        except Exception as e:
            logger.error(f"[WORKER] Loop error: {e}", exc_info=True)
            await asyncio.sleep(1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Submission processing pipeline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def process_submission(redis: aioredis.Redis, submission_id: uuid.UUID):
    """
    Full submission pipeline:

      1. Load submission + problem + test cases from DB
      2. Mark status = RUNNING, publish event
      3. For each test case:
         a. Execute code in Docker sandbox (timeout, memory/CPU capped)
         b. Judge output against expected
         c. Record per-case result
         d. Stop on first failure (fail-fast)
      4. Persist all results to DB
      5. Publish verdict via Redis pub/sub
      6. If ACCEPTED → trigger match completion check
    """
    async with AsyncSessionLocal() as db:
        # ── 1. Load submission ────────────────────────────
        stmt = (
            select(Submission)
            .where(Submission.id == submission_id)
            .options(selectinload(Submission.problem))
        )
        row = await db.execute(stmt)
        submission = row.scalar_one_or_none()

        if not submission:
            logger.error(f"[WORKER] Submission {submission_id} not found in DB")
            return

        # ── Load test cases ───────────────────────────────
        tc_stmt = (
            select(TestCase)
            .where(TestCase.problem_id == submission.problem_id)
            .order_by(TestCase.order_index)
        )
        tc_rows = await db.execute(tc_stmt)
        test_cases = tc_rows.scalars().all()

        if not test_cases:
            logger.error(f"[WORKER] No test cases for problem {submission.problem_id}")
            return

        # ── 2. Mark as running ────────────────────────────
        submission.status = SubmissionStatus.RUNNING
        await db.commit()

        match_channel = RedisKey.ws_channel(str(submission.match_id))
        await _publish_event(redis, match_channel, WSEvent.SUBMISSION_RUNNING, {
            "submission_id": str(submission_id),
            "user_id": str(submission.user_id),
        })

        logger.info(
            f"[WORKER] ═══ Processing submission {submission_id} ═══ "
            f"problem={submission.problem_id}, "
            f"language={submission.language}, "
            f"test_cases={len(list(test_cases))}"
        )

        # ── 3. Execute per test case (fail-fast) ─────────
        results: list[SubmissionResult] = []
        overall_verdict = Verdict.ACCEPTED
        max_time_ms = 0
        max_memory_kb = 0

        for tc_idx, tc in enumerate(test_cases):
            # Execute in Docker sandbox
            exec_result = await sandbox.execute(
                language=submission.language,
                code=submission.code,
                stdin_data=tc.input,
                time_limit_ms=submission.problem.time_limit_ms,
                memory_limit_mb=submission.problem.memory_limit_mb,
            )

            # ── Detect compilation error (separate from runtime) ──
            if exec_result.stage == "compile" and exec_result.exit_code != 0:
                is_infra_compile_failure = (
                    exec_result.timed_out
                    or "Execution engine error" in exec_result.stderr
                    or "sandbox container did not respond" in exec_result.stderr
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
                logger.info(
                    f"[WORKER] {submission_id} TC#{tc_idx}: "
                    f"verdict={failure_status}, "
                    f"stderr={repr(exec_result.stderr[:300])}"
                )

                case_result = SubmissionResult(
                    submission_id=submission.id,
                    test_case_id=tc.id,
                    verdict=failure_status,
                    execution_time_ms=0,
                    memory_used_kb=0,
                    actual_output="",
                    error_output=exec_result.stderr[:5000] if exec_result.stderr else None,
                )
                results.append(case_result)

                # Compilation error → stop, don't run other test cases
                submission.status = failure_status
                submission.passed_test_cases = 0
                submission.execution_time_ms = 0
                submission.memory_used_kb = 0
                submission.judged_at = datetime.now(timezone.utc)

                db.add_all(results)
                await db.commit()

                await _publish_event(redis, match_channel, WSEvent.SUBMISSION_RESULT, {
                    "submission_id": str(submission.id),
                    "user_id": str(submission.user_id),
                    "verdict": failure_event,
                    "passed": 0,
                    "total": len(list(test_cases)),
                    "runtime_ms": 0,
                    "memory_kb": 0,
                })
                logger.info(
                    f"[WORKER] {submission_id}: FINAL=compilation_error"
                )
                return

            # Judge the output
            verdict = judge(
                actual_output=exec_result.stdout,
                expected_output=tc.expected_output,
                exit_code=exec_result.exit_code,
                timed_out=exec_result.timed_out,
                oom_killed=exec_result.oom_killed,
            )

            # ── Log per-test-case details ─────────────────
            logger.info(
                f"[WORKER] {submission_id} TC#{tc_idx}: "
                f"verdict={verdict.value}, "
                f"exit_code={exec_result.exit_code}, "
                f"time_ms={exec_result.time_ms}, "
                f"timed_out={exec_result.timed_out}, "
                f"oom_killed={exec_result.oom_killed}, "
                f"stdout_len={len(exec_result.stdout)}, "
                f"stderr_preview={repr(exec_result.stderr[:200])}"
            )

            # Track peak resources
            max_time_ms = max(max_time_ms, exec_result.time_ms)
            max_memory_kb = max(max_memory_kb, exec_result.memory_kb)

            # Record per-case result
            case_result = SubmissionResult(
                submission_id=submission.id,
                test_case_id=tc.id,
                verdict=verdict.value,
                execution_time_ms=exec_result.time_ms,
                memory_used_kb=exec_result.memory_kb,
                actual_output=(
                    exec_result.stdout[:5000]
                    if verdict != Verdict.ACCEPTED else None
                ),
                error_output=(
                    exec_result.stderr[:5000]
                    if exec_result.stderr else None
                ),
            )
            results.append(case_result)

            # Fail-fast: stop on first non-AC verdict
            if verdict != Verdict.ACCEPTED:
                overall_verdict = verdict
                logger.info(
                    f"[WORKER] Submission {submission_id} failed on "
                    f"test case #{tc_idx}: {verdict.value}"
                )
                break

        # ── 4. Persist results ────────────────────────────
        passed_count = sum(1 for r in results if r.verdict == Verdict.ACCEPTED.value)

        submission.status = overall_verdict.value
        submission.passed_test_cases = passed_count
        submission.execution_time_ms = max_time_ms
        submission.memory_used_kb = max_memory_kb
        submission.judged_at = datetime.now(timezone.utc)

        db.add_all(results)
        await db.commit()

        # ── 5. Publish verdict ────────────────────────────
        await _publish_event(redis, match_channel, WSEvent.SUBMISSION_RESULT, {
            "submission_id": str(submission.id),
            "user_id": str(submission.user_id),
            "verdict": overall_verdict.value,
            "passed": passed_count,
            "total": len(list(test_cases)),
            "runtime_ms": max_time_ms,
            "memory_kb": max_memory_kb,
        })

        logger.info(
            f"[WORKER] ═══ {submission_id}: FINAL={overall_verdict.value} ═══ "
            f"({passed_count}/{len(list(test_cases))} passed, "
            f"{max_time_ms}ms, {max_memory_kb}KB)"
        )

        # ── 6. Check for match completion ─────────────────
        if overall_verdict == Verdict.ACCEPTED:
            try:
                result_data = await match_service.complete_match(
                    db, redis, submission.match_id, reason="solved"
                )
                if result_data:
                    await _publish_event(
                        redis, match_channel,
                        WSEvent.MATCH_ENDED, result_data,
                    )
                    logger.info(
                        f"[WORKER] Match {submission.match_id} completed (solved)"
                    )
            except Exception as e:
                logger.error(f"[WORKER] Error completing match: {e}", exc_info=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def _publish_event(
    redis: aioredis.Redis,
    channel: str,
    event: str,
    data: dict,
):
    """Publish a WebSocket event through Redis pub/sub."""
    payload = json.dumps({"event": event, "data": data})
    await redis.publish(channel, payload)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Entry point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(run_worker())
