"""
Custom exception classes for structured error handling.
"""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


# ── Auth ──────────────────────────────────────────────────────

class InvalidCredentials(AppException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")


class TokenExpired(AppException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Token has expired")


class UserAlreadyExists(AppException):
    def __init__(self):
        super().__init__(status.HTTP_409_CONFLICT, "Username or email already registered")


class LoginRateLimited(AppException):
    def __init__(self):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, "Too many failed login attempts. Try again later.")


class AdminAccessRequired(AppException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, "Admin access required")


class SpectatorAuthRequired(AppException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Authentication required")


class RoomCodeRateLimited(AppException):
    def __init__(self):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, "Too many room code attempts. Try again later.")


# ── Matchmaking ──────────────────────────────────────────────

class AlreadyInQueue(AppException):
    def __init__(self):
        super().__init__(status.HTTP_409_CONFLICT, "Already in matchmaking queue")


class NotInQueue(AppException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "Not in matchmaking queue")


class AlreadyInMatch(AppException):
    def __init__(self):
        super().__init__(status.HTTP_409_CONFLICT, "Already in an active match")


# ── Match ─────────────────────────────────────────────────────

class MatchNotFound(AppException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "Match not found")


class MatchNotActive(AppException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, "Match is not active")


class MatchExpired(AppException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, "Match time has expired")


class NotMatchParticipant(AppException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, "You are not a participant in this match")


# ── Submission ────────────────────────────────────────────────

class UnsupportedLanguage(AppException):
    def __init__(self, lang: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"Unsupported language: {lang}")


class SubmissionRateLimited(AppException):
    def __init__(self):
        super().__init__(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many submissions in a short time. Please wait a moment and try again.",
        )


# ── Problem ───────────────────────────────────────────────────

class ProblemNotFound(AppException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, "Problem not found")


# ── OTP ──────────────────────────────────────────────────────

class OTPRateLimited(AppException):
    def __init__(self):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, "Too many OTP requests. Try again later.")


class OTPInvalid(AppException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "Invalid or expired OTP")


class OTPMaxAttemptsExceeded(AppException):
    def __init__(self):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, "Too many failed attempts. Request a new OTP.")


class DisposableEmailBlocked(AppException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, "Disposable email addresses are not allowed")
