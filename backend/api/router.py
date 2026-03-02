"""
Central router — aggregates all API routers.
"""

from fastapi import APIRouter

from backend.api.auth import router as auth_router
from backend.api.otp_auth import router as otp_auth_router
from backend.api.matchmaking import router as matchmaking_router
from backend.api.matches import router as matches_router
from backend.api.submissions import router as submissions_router
from backend.api.problems import router as problems_router
from backend.api.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(otp_auth_router)
api_router.include_router(users_router)
api_router.include_router(matchmaking_router)
api_router.include_router(matches_router)
api_router.include_router(submissions_router)
api_router.include_router(problems_router)
