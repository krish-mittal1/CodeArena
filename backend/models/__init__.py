"""Models package — import all models for Alembic discovery."""

from backend.models.user import User
from backend.models.problem import Problem
from backend.models.test_case import TestCase
from backend.models.match import Match
from backend.models.match_problem import MatchProblem
from backend.models.submission import Submission
from backend.models.submission_result import SubmissionResult
from backend.models.ai_analysis import AIAnalysis
from backend.models.review_queue import ReviewQueueItem

__all__ = [
    "User",
    "Problem",
    "TestCase",
    "Match",
    "MatchProblem",
    "Submission",
    "SubmissionResult",
    "AIAnalysis",
    "ReviewQueueItem",
]
