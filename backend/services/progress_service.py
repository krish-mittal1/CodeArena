"""User interview prep progress — topics, companies, weak areas."""

from __future__ import annotations

import uuid
from collections import defaultdict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.constants import SubmissionStatus
from backend.models.problem import Problem
from backend.models.submission import Submission
from backend.services.interview_metadata_service import get_problem_meta


async def get_user_progress(db: AsyncSession, user_id: uuid.UUID) -> dict:
    problems_result = await db.execute(
        select(Problem).where(Problem.is_active.is_(True), Problem.problem_type == "dsa")
    )
    problems = list(problems_result.scalars().all())

    attempts_result = await db.execute(
        select(
            Submission.problem_id,
            func.count().label("attempts"),
        )
        .where(Submission.user_id == user_id, Submission.match_id.is_(None))
        .group_by(Submission.problem_id)
    )
    attempts_map = {row.problem_id: int(row.attempts) for row in attempts_result.all()}

    fails_result = await db.execute(
        select(Submission.problem_id, func.count().label("fails"))
        .where(
            Submission.user_id == user_id,
            Submission.match_id.is_(None),
            Submission.status != SubmissionStatus.ACCEPTED,
        )
        .group_by(Submission.problem_id)
    )
    fails_map = {row.problem_id: int(row.fails) for row in fails_result.all()}

    solved_result = await db.execute(
        select(Submission.problem_id)
        .where(
            Submission.user_id == user_id,
            Submission.status == SubmissionStatus.ACCEPTED,
        )
        .distinct()
    )
    solved_ids = set(solved_result.scalars().all())

    topic_stats: dict[str, dict] = defaultdict(lambda: {"total": 0, "solved": 0, "attempts": 0, "fails": 0})
    company_stats: dict[str, dict] = defaultdict(lambda: {"total": 0, "solved": 0})
    weak_topics: list[dict] = []

    for p in problems:
        meta = get_problem_meta(p.title)
        topic = meta["topic"]
        topic_stats[topic]["total"] += 1
        if p.id in solved_ids:
            topic_stats[topic]["solved"] += 1
        topic_stats[topic]["attempts"] += attempts_map.get(p.id, 0)
        topic_stats[topic]["fails"] += fails_map.get(p.id, 0)

        for company in meta.get("companies", []):
            company_stats[company]["total"] += 1
            if p.id in solved_ids:
                company_stats[company]["solved"] += 1

    topics = []
    for topic, s in sorted(topic_stats.items()):
        readiness = round(100 * s["solved"] / s["total"]) if s["total"] else 0
        fail_rate = round(100 * s["fails"] / s["attempts"]) if s["attempts"] else 0
        topics.append({
            "topic": topic,
            "total": s["total"],
            "solved": s["solved"],
            "readiness_pct": readiness,
            "attempts": s["attempts"],
            "fails": s["fails"],
            "fail_rate_pct": fail_rate,
        })
        if s["attempts"] >= 2 and fail_rate >= 40 and s["solved"] < s["total"]:
            weak_topics.append({"topic": topic, "fail_rate_pct": fail_rate, "solved": s["solved"], "total": s["total"]})

    weak_topics.sort(key=lambda x: x["fail_rate_pct"], reverse=True)

    companies = []
    for name, s in sorted(company_stats.items(), key=lambda x: x[1]["solved"], reverse=True)[:20]:
        companies.append({
            "company": name,
            "total": s["total"],
            "solved": s["solved"],
            "readiness_pct": round(100 * s["solved"] / s["total"]) if s["total"] else 0,
        })

    return {
        "total_problems": len(problems),
        "total_solved": len(solved_ids & {p.id for p in problems}),
        "topics": topics,
        "weak_topics": weak_topics[:5],
        "companies": companies,
        "solved_problem_ids": [str(pid) for pid in solved_ids],
    }
